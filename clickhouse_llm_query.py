"""
ClickHouse implementation for LLM Queries
This module provides functions for storing and retrieving LLM queries using ClickHouse
"""

import logging
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check if we're in development or production environment
IS_DEVELOPMENT = os.environ.get('REPL_ID') is not None

# ClickHouse connection parameters (will be used in production environment)
CLICKHOUSE_CONFIG = {
    'host': os.environ.get('CLICKHOUSE_HOST', 'localhost'),
    'port': int(os.environ.get('CLICKHOUSE_PORT', 9000)),
    'user': os.environ.get('CLICKHOUSE_USER', 'default'),
    'password': os.environ.get('CLICKHOUSE_PASSWORD', ''),
    'database': os.environ.get('CLICKHOUSE_DB', 'l1_app_db'),
    'connect_timeout': 5  # Reduced timeout for faster fallback
}

# Track connection state to avoid repeated connection attempts
_connection_attempted = False
_clickhouse_available = False

def get_clickhouse_client():
    """Get a ClickHouse client connection"""
    global _connection_attempted, _clickhouse_available
    
    # If we've already tried to connect and failed, don't try again
    if _connection_attempted and not _clickhouse_available:
        return None
        
    _connection_attempted = True
    
    try:
        from clickhouse_driver import Client
        client = Client(**CLICKHOUSE_CONFIG)
        # Verify the connection with a simple query
        client.execute("SELECT 1")
        _clickhouse_available = True
        return client
    except Exception as e:
        logger.error(f"Error connecting to ClickHouse: {e}")
        _clickhouse_available = False
        return None

def is_clickhouse_available():
    """Check if ClickHouse is available"""
    global _connection_attempted, _clickhouse_available
    
    # If we've already determined availability, return cached result
    if _connection_attempted:
        return _clickhouse_available
        
    # Otherwise, attempt to connect
    client = get_clickhouse_client()
    return client is not None

def initialize_database():
    """Initialize the database schema"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot initialize database - no connection")
        return False
    
    try:
        # Create database if it doesn't exist
        client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_CONFIG['database']}")
        
        # Create LLM queries table
        client.execute("""
        CREATE TABLE IF NOT EXISTS llm_queries (
            id String,
            query_text String,
            response_text String,
            agent_type String,
            temperature Float64 DEFAULT 0.7,
            max_tokens UInt32 DEFAULT 1024,
            created_at DateTime DEFAULT now(),
            response_time_ms UInt32,
            prompt_tokens UInt32,
            completion_tokens UInt32,
            error String,
            used_rag UInt8 DEFAULT 0
        ) ENGINE = MergeTree() ORDER BY (created_at, id)
        """)
        
        logger.info("ClickHouse database schema initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        return False

def save_llm_query(query_text: str, agent_type: str = 'general', 
                  temperature: float = 0.7, max_tokens: int = 1024, 
                  used_rag: bool = False) -> str:
    """Save a new LLM query to ClickHouse"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot save LLM query - no connection")
        return None
    
    try:
        # Generate a query ID
        query_id = str(uuid.uuid4())
        
        # Insert the query
        client.execute("""
        INSERT INTO llm_queries 
        (id, query_text, agent_type, temperature, max_tokens, used_rag, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, now())
        """, (query_id, query_text, agent_type, temperature, max_tokens, 1 if used_rag else 0))
        
        logger.info(f"Saved LLM query to ClickHouse with ID: {query_id}")
        return query_id
    except Exception as e:
        logger.error(f"Error saving LLM query: {e}")
        return None

def update_llm_query_response(query_id: str, response_text: str, 
                            response_time_ms: int = None,
                            prompt_tokens: int = None, 
                            completion_tokens: int = None,
                            error: str = None) -> bool:
    """Update an LLM query with the response"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot update LLM query - no connection")
        return False
    
    try:
        # Update the query with response information
        update_fields = []
        update_values = []
        
        if response_text:
            update_fields.append("response_text = %s")
            update_values.append(response_text)
        
        if response_time_ms is not None:
            update_fields.append("response_time_ms = %s")
            update_values.append(response_time_ms)
            
        if prompt_tokens is not None:
            update_fields.append("prompt_tokens = %s")
            update_values.append(prompt_tokens)
            
        if completion_tokens is not None:
            update_fields.append("completion_tokens = %s")
            update_values.append(completion_tokens)
            
        if error:
            update_fields.append("error = %s")
            update_values.append(error)
            
        if not update_fields:
            logger.warning("No fields to update for LLM query")
            return False
            
        # In ClickHouse, we need to create a new row with updated values since it's immutable
        # We'll do this by inserting the updated record and then running optimize
        # First, get the original record
        original = client.execute("""
        SELECT * FROM llm_queries WHERE id = %s
        """, (query_id,))
        
        if not original:
            logger.error(f"Cannot find LLM query with ID: {query_id}")
            return False
            
        # For a proper update in ClickHouse (which doesn't support UPDATE), 
        # we'd need to use a more complex approach like ReplacingMergeTree
        # But for simplicity in this example, we'll just insert a new record
        # with the same ID (which ClickHouse allows)
        
        # Create set clause for update
        set_clause = ", ".join(update_fields)
        
        # Execute the query with parameters
        client.execute(f"""
        INSERT INTO llm_queries 
        (id, query_text, response_text, agent_type, temperature, max_tokens, 
         created_at, response_time_ms, prompt_tokens, completion_tokens, error, used_rag)
        SELECT 
            id, 
            query_text, 
            {response_text if response_text else 'response_text'}, 
            agent_type, 
            temperature, 
            max_tokens, 
            created_at, 
            {response_time_ms if response_time_ms is not None else 'response_time_ms'}, 
            {prompt_tokens if prompt_tokens is not None else 'prompt_tokens'}, 
            {completion_tokens if completion_tokens is not None else 'completion_tokens'}, 
            {f"'{error}'" if error else 'error'}, 
            used_rag
        FROM llm_queries 
        WHERE id = '{query_id}'
        ORDER BY created_at DESC
        LIMIT 1
        """)
        
        # Optimize the table to merge the updated record
        client.execute(f"OPTIMIZE TABLE llm_queries FINAL")
        
        logger.info(f"Updated LLM query response for ID: {query_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating LLM query response: {e}")
        return False

def get_llm_query_count() -> int:
    """Get the total count of LLM queries"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot get LLM query count - no connection")
        return 0
    
    try:
        result = client.execute("SELECT count() FROM llm_queries")
        return result[0][0] if result else 0
    except Exception as e:
        logger.error(f"Error getting LLM query count: {e}")
        return 0

def get_today_llm_query_count() -> int:
    """Get the count of LLM queries from today"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot get today's LLM query count - no connection")
        return 0
    
    try:
        result = client.execute("""
        SELECT count() FROM llm_queries 
        WHERE created_at >= toDate(now())
        """)
        return result[0][0] if result else 0
    except Exception as e:
        logger.error(f"Error getting today's LLM query count: {e}")
        return 0

def get_llm_queries(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Get paginated LLM queries"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot get LLM queries - no connection")
        return {"queries": [], "total": 0, "pages": 0, "current_page": page}
    
    try:
        # Get total count
        total_count = get_llm_query_count()
        
        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
        offset = (page - 1) * per_page
        
        # Get the paginated queries
        queries = client.execute("""
        SELECT id, query_text, response_text, agent_type, temperature, max_tokens, 
               created_at, response_time_ms, prompt_tokens, completion_tokens, error, used_rag
        FROM llm_queries
        ORDER BY created_at DESC
        LIMIT %s, %s
        """, (offset, per_page))
        
        # Format the results
        formatted_queries = []
        for q in queries:
            formatted_queries.append({
                'id': q[0],
                'query_text': q[1],
                'response_text': q[2],
                'agent_type': q[3],
                'temperature': q[4],
                'max_tokens': q[5],
                'created_at': q[6].isoformat() if q[6] else None,
                'response_time_ms': q[7],
                'prompt_tokens': q[8],
                'completion_tokens': q[9],
                'error': q[10],
                'used_rag': bool(q[11])
            })
        
        return {
            'queries': formatted_queries,
            'total': total_count,
            'pages': total_pages,
            'current_page': page
        }
    except Exception as e:
        logger.error(f"Error getting LLM queries: {e}")
        return {"queries": [], "total": 0, "pages": 0, "current_page": page}

# Initialize the database when the module is imported
try:
    initialize_database()
except Exception as e:
    logger.error(f"Error initializing ClickHouse database: {e}")