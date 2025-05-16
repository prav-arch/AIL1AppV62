"""
Simplified Application for ClickHouse 18.16.1 + FAISS
This is a slimmed-down version that avoids potential hanging issues
"""

import os
import logging
import json
import numpy as np
from typing import List, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ClickHouse connection parameters
CLICKHOUSE_CONFIG = {
    'host': 'localhost',
    'port': 9000,
    'user': 'default',
    'password': '',
    'database': 'l1_app_db',
    'connect_timeout': 10
}

# Try importing necessary libraries with clear error messages
try:
    from clickhouse_driver import Client
    logger.info("Successfully imported clickhouse_driver")
except ImportError:
    logger.error("Could not import clickhouse_driver. Please install with: pip install clickhouse-driver")
    exit(1)

try:
    import faiss
    logger.info("Successfully imported faiss")
except ImportError:
    logger.error("Could not import faiss. Please install with: pip install faiss-cpu")
    exit(1)

def get_clickhouse_client():
    """Get a ClickHouse client connection with error handling"""
    try:
        logger.info(f"Connecting to ClickHouse at {CLICKHOUSE_CONFIG['host']}:{CLICKHOUSE_CONFIG['port']}")
        client = Client(**CLICKHOUSE_CONFIG)
        
        # Run a simple query to test connection
        result = client.execute("SELECT 1")
        logger.info(f"Connected to ClickHouse successfully. Test query result: {result}")
        
        return client
    except Exception as e:
        logger.error(f"Error connecting to ClickHouse: {e}")
        logger.error("Please make sure ClickHouse is running and accessible")
        return None

def initialize_database():
    """Create necessary database schema"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot initialize database - no connection")
        return False
    
    try:
        # Create database
        logger.info(f"Creating database {CLICKHOUSE_CONFIG['database']} if it doesn't exist")
        client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_CONFIG['database']}")
        
        # Use database
        client.execute(f"USE {CLICKHOUSE_CONFIG['database']}")
        
        # Create documents table
        logger.info("Creating documents table")
        client.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id String,
            name String,
            description String,
            metadata String,
            file_path String,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree() ORDER BY id
        """)
        
        # Create document_chunks table
        logger.info("Creating document_chunks table")
        client.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id UInt64,
            document_id String,
            chunk_index UInt32,
            chunk_text String,
            metadata String,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree() ORDER BY (document_id, chunk_index)
        """)
        
        # Create vector_db_stats table
        logger.info("Creating vector_db_stats table")
        client.execute("""
        CREATE TABLE IF NOT EXISTS vector_db_stats (
            id UInt8,
            documents_count UInt32 DEFAULT 0,
            chunks_count UInt32 DEFAULT 0,
            vector_dim UInt16,
            last_modified DateTime DEFAULT now()
        ) ENGINE = ReplacingMergeTree() ORDER BY id
        """)
        
        # Initialize stats if needed
        client.execute("""
        INSERT INTO vector_db_stats (id, documents_count, chunks_count, vector_dim)
        VALUES (1, 0, 0, 384)
        IF NOT EXISTS
        """)
        
        logger.info("Database schema created successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def create_faiss_index(dimension=384):
    """Create a basic FAISS index for testing"""
    logger.info(f"Creating FAISS index with dimension {dimension}")
    try:
        index = faiss.IndexFlatL2(dimension)
        logger.info("FAISS index created successfully")
        return index
    except Exception as e:
        logger.error(f"Error creating FAISS index: {e}")
        return None

def test_faiss_operations():
    """Test basic FAISS operations to verify functionality"""
    logger.info("Testing FAISS operations...")
    try:
        # Create index
        dimension = 4  # Small dimension for quick testing
        index = create_faiss_index(dimension)
        if not index:
            return False
        
        # Create a simple vector
        vector = np.array([[1.0, 2.0, 3.0, 4.0]], dtype='float32')
        logger.info(f"Adding vector: {vector} to index")
        
        # Add vector to index
        index.add(vector)
        logger.info(f"Vector added. Index now contains {index.ntotal} vectors")
        
        # Search for a similar vector
        query = np.array([[1.1, 2.1, 3.1, 4.1]], dtype='float32')
        logger.info(f"Searching for vector: {query}")
        
        distances, indices = index.search(query, 1)
        logger.info(f"Search results - distances: {distances}, indices: {indices}")
        
        logger.info("FAISS operations completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in FAISS operations: {e}")
        return False

def add_test_document():
    """Add a test document to ClickHouse"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot add test document - no connection")
        return False
    
    try:
        # Generate a random document ID
        document_id = str(int(time.time()))
        logger.info(f"Adding test document with ID: {document_id}")
        
        # Insert document
        client.execute("""
        INSERT INTO documents (id, name, description, metadata)
        VALUES (%s, %s, %s, %s)
        """, (document_id, "Test Document", "This is a test document", "{}"))
        
        # Add a few chunks
        for i in range(3):
            chunk_id = int(time.time() * 1000) + i
            client.execute("""
            INSERT INTO document_chunks (id, document_id, chunk_index, chunk_text, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """, (chunk_id, document_id, i, f"This is test chunk {i}", "{}"))
        
        # Update stats
        client.execute("""
        UPDATE vector_db_stats
        SET documents_count = documents_count + 1, chunks_count = chunks_count + 3, last_modified = now()
        WHERE id = 1
        """)
        
        logger.info(f"Test document added successfully with ID: {document_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding test document: {e}")
        return False

def get_database_stats():
    """Get database statistics from ClickHouse"""
    client = get_clickhouse_client()
    if not client:
        logger.error("Cannot get stats - no connection")
        return None
    
    try:
        logger.info("Getting database statistics")
        result = client.execute("""
        SELECT documents_count, chunks_count, vector_dim, last_modified
        FROM vector_db_stats
        WHERE id = 1
        """)
        
        if not result:
            logger.warning("No stats found in database")
            return None
        
        row = result[0]
        stats = {
            'documents_count': row[0],
            'chunks_count': row[1],
            'vector_dim': row[2],
            'last_modified': row[3].isoformat() if row[3] else None
        }
        
        logger.info(f"Database stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return None

def main():
    """Main function to test core functionality"""
    logger.info("Starting simplified application")
    
    # Step 1: Check ClickHouse connection
    client = get_clickhouse_client()
    if not client:
        logger.error("Failed to connect to ClickHouse. Exiting.")
        return
    
    logger.info("Connection to ClickHouse established successfully")
    
    # Step 2: Initialize database schema
    if not initialize_database():
        logger.error("Failed to initialize database schema. Exiting.")
        return
    
    logger.info("Database schema initialized successfully")
    
    # Step 3: Test FAISS operations
    if not test_faiss_operations():
        logger.error("Failed to complete FAISS operations. Exiting.")
        return
    
    logger.info("FAISS operations completed successfully")
    
    # Step 4: Add a test document
    if not add_test_document():
        logger.error("Failed to add test document. Exiting.")
        return
    
    logger.info("Test document added successfully")
    
    # Step 5: Get database stats
    stats = get_database_stats()
    if not stats:
        logger.error("Failed to get database stats. Exiting.")
        return
    
    logger.info(f"Final database stats: {stats}")
    logger.info("All tests completed successfully!")

if __name__ == "__main__":
    main()