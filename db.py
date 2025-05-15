"""
Database utilities for the AI Assistant Platform using psycopg2 
for direct PostgreSQL connection without an ORM
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Database connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """
    Get a connection to the PostgreSQL database
    
    Returns:
        connection: psycopg2 connection object
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {str(e)}")
        raise

def execute_query(query, params=None, fetch=True):
    """
    Execute a SQL query and return the results
    
    Args:
        query: SQL query string
        params: Parameters for the query
        fetch: Whether to fetch results (for SELECT) or not (for INSERT/UPDATE/DELETE)
        
    Returns:
        results: Query results if fetch=True, otherwise None
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            else:
                conn.commit()
                return None
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error executing query: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """
    Initialize the database by creating all necessary tables
    """
    # Users and conversations
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(64) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    """
    
    create_conversations_table = """
    CREATE TABLE IF NOT EXISTS conversations (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        title VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_messages_table = """
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
        role VARCHAR(20) NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Documents and RAG
    create_documents_table = """
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        title VARCHAR(255) NOT NULL,
        description TEXT,
        content TEXT,
        file_path VARCHAR(255),
        file_type VARCHAR(50),
        file_size INTEGER,
        source VARCHAR(255),
        source_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_document_chunks_table = """
    CREATE TABLE IF NOT EXISTS document_chunks (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
        chunk_text TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        embedding_data BYTEA,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_rag_searches_table = """
    CREATE TABLE IF NOT EXISTS rag_searches (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        query TEXT NOT NULL,
        top_k INTEGER,
        search_time FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Time series and anomalies
    create_time_series_table = """
    CREATE TABLE IF NOT EXISTS time_series (
        id SERIAL PRIMARY KEY,
        source VARCHAR(100) NOT NULL,
        metric_name VARCHAR(100) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        value FLOAT NOT NULL,
        tags JSONB
    );
    """
    
    create_anomalies_table = """
    CREATE TABLE IF NOT EXISTS anomalies (
        id SERIAL PRIMARY KEY,
        time_series_id INTEGER REFERENCES time_series(id),
        algorithm VARCHAR(100) NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        severity FLOAT NOT NULL,
        score FLOAT NOT NULL,
        status VARCHAR(20) DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_anomaly_alerts_table = """
    CREATE TABLE IF NOT EXISTS anomaly_alerts (
        id SERIAL PRIMARY KEY,
        anomaly_id INTEGER REFERENCES anomalies(id) ON DELETE CASCADE,
        alert_type VARCHAR(50) NOT NULL,
        recipient VARCHAR(255) NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        acknowledged_at TIMESTAMP
    );
    """
    
    # Data pipelines
    create_pipeline_jobs_table = """
    CREATE TABLE IF NOT EXISTS pipeline_jobs (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        schedule VARCHAR(100),
        pipeline_type VARCHAR(50) NOT NULL,
        config JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_job_runs_table = """
    CREATE TABLE IF NOT EXISTS job_runs (
        id SERIAL PRIMARY KEY,
        job_id INTEGER REFERENCES pipeline_jobs(id) ON DELETE CASCADE,
        status VARCHAR(50) NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        logs TEXT,
        error_message TEXT
    );
    """
    
    # Kafka
    create_kafka_topics_table = """
    CREATE TABLE IF NOT EXISTS kafka_topics (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        description TEXT,
        partition_count INTEGER NOT NULL,
        replication_factor INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_kafka_consumer_groups_table = """
    CREATE TABLE IF NOT EXISTS kafka_consumer_groups (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_kafka_messages_table = """
    CREATE TABLE IF NOT EXISTS kafka_messages (
        id SERIAL PRIMARY KEY,
        topic_id INTEGER REFERENCES kafka_topics(id) ON DELETE CASCADE,
        partition INTEGER NOT NULL,
        offset BIGINT NOT NULL,
        key TEXT,
        value TEXT,
        headers JSONB,
        timestamp TIMESTAMP NOT NULL
    );
    """
    
    # System
    create_settings_table = """
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        category VARCHAR(100) NOT NULL,
        key VARCHAR(100) NOT NULL,
        value TEXT,
        description TEXT,
        UNIQUE(category, key)
    );
    """
    
    create_activity_logs_table = """
    CREATE TABLE IF NOT EXISTS activity_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        action VARCHAR(100) NOT NULL,
        entity_type VARCHAR(100),
        entity_id INTEGER,
        details JSONB,
        ip_address VARCHAR(45),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Tables creation sequence
    tables = [
        create_users_table,
        create_conversations_table,
        create_messages_table,
        create_documents_table,
        create_document_chunks_table,
        create_rag_searches_table,
        create_time_series_table,
        create_anomalies_table,
        create_anomaly_alerts_table,
        create_pipeline_jobs_table,
        create_job_runs_table,
        create_kafka_topics_table,
        create_kafka_consumer_groups_table,
        create_kafka_messages_table,
        create_settings_table,
        create_activity_logs_table
    ]
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            for table_query in tables:
                cur.execute(table_query)
            conn.commit()
            logger.info("All database tables created successfully")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


# Document operations
def add_document(user_id, title, description, content=None, file_path=None, 
                file_type=None, file_size=None, source=None, source_url=None):
    """
    Add a document to the database
    
    Args:
        user_id: User ID who owns the document
        title: Document title
        description: Document description
        content: Document text content
        file_path: Path to the document file
        file_type: MIME type of the document
        file_size: Size of the document in bytes
        source: Source of the document (upload, web_scrape, etc.)
        source_url: URL for scraped documents
        
    Returns:
        document_id: ID of the newly created document
    """
    query = """
    INSERT INTO documents (user_id, title, description, content, file_path, 
                          file_type, file_size, source, source_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    params = (user_id, title, description, content, file_path, file_type, 
              file_size, source, source_url)
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            document_id = result[0] if result else None
            conn.commit()
            return document_id
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def add_document_chunk(document_id, chunk_text, chunk_index, embedding_data=None):
    """
    Add a document chunk with embedding
    
    Args:
        document_id: ID of the parent document
        chunk_text: Text of the chunk
        chunk_index: Index of the chunk within the document
        embedding_data: Binary embedding data
        
    Returns:
        chunk_id: ID of the newly created chunk
    """
    query = """
    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding_data)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    params = (document_id, chunk_text, chunk_index, embedding_data)
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            chunk_id = result[0] if result else None
            conn.commit()
            return chunk_id
    except Exception as e:
        logger.error(f"Error adding document chunk: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_documents(user_id=None, limit=100, offset=0):
    """
    Get documents from the database
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of documents to return
        offset: Number of documents to skip
        
    Returns:
        documents: List of document records
    """
    if user_id:
        query = """
        SELECT * FROM documents 
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s;
        """
        params = (user_id, limit, offset)
    else:
        query = """
        SELECT * FROM documents 
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s;
        """
        params = (limit, offset)
    
    return execute_query(query, params)

def get_document_chunks(document_id):
    """
    Get chunks for a document
    
    Args:
        document_id: ID of the document
        
    Returns:
        chunks: List of chunk records
    """
    query = """
    SELECT * FROM document_chunks 
    WHERE document_id = %s
    ORDER BY chunk_index;
    """
    params = (document_id,)
    
    return execute_query(query, params)

# Conversation operations
def add_conversation(user_id, title=None):
    """
    Add a conversation to the database
    
    Args:
        user_id: User ID who owns the conversation
        title: Optional title for the conversation
        
    Returns:
        conversation_id: ID of the newly created conversation
    """
    query = """
    INSERT INTO conversations (user_id, title)
    VALUES (%s, %s)
    RETURNING id;
    """
    params = (user_id, title)
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            conversation_id = result[0] if result else None
            conn.commit()
            return conversation_id
    except Exception as e:
        logger.error(f"Error adding conversation: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def add_message(conversation_id, role, content):
    """
    Add a message to a conversation
    
    Args:
        conversation_id: ID of the conversation
        role: Message role (user, assistant, system)
        content: Message content
        
    Returns:
        message_id: ID of the newly created message
    """
    query = """
    INSERT INTO messages (conversation_id, role, content)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    params = (conversation_id, role, content)
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            message_id = result[0] if result else None
            # Also update the conversation's updated_at timestamp
            update_query = """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
            """
            cur.execute(update_query, (conversation_id,))
            conn.commit()
            return message_id
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_conversations(user_id, limit=20, offset=0):
    """
    Get conversations for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        
    Returns:
        conversations: List of conversation records
    """
    query = """
    SELECT * FROM conversations 
    WHERE user_id = %s
    ORDER BY updated_at DESC
    LIMIT %s OFFSET %s;
    """
    params = (user_id, limit, offset)
    
    return execute_query(query, params)

def get_messages(conversation_id):
    """
    Get messages for a conversation
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        messages: List of message records
    """
    query = """
    SELECT * FROM messages 
    WHERE conversation_id = %s
    ORDER BY timestamp;
    """
    params = (conversation_id,)
    
    return execute_query(query, params)

# Anomaly operations
def add_time_series_data(source, metric_name, timestamp, value, tags=None):
    """
    Add time series data point
    
    Args:
        source: Source of the data
        metric_name: Name of the metric
        timestamp: Timestamp of the data point
        value: Numeric value
        tags: JSON tags/metadata
        
    Returns:
        time_series_id: ID of the newly created time series data point
    """
    query = """
    INSERT INTO time_series (source, metric_name, timestamp, value, tags)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    params = (source, metric_name, timestamp, value, tags)
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            time_series_id = result[0] if result else None
            conn.commit()
            return time_series_id
    except Exception as e:
        logger.error(f"Error adding time series data: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def add_anomaly(time_series_id, algorithm, start_time, severity, score, 
               end_time=None, status='open'):
    """
    Add an anomaly
    
    Args:
        time_series_id: ID of the time series
        algorithm: Detection algorithm used
        start_time: Start time of the anomaly
        severity: Severity score (0-1)
        score: Anomaly score
        end_time: Optional end time
        status: Status (open, acknowledged, closed)
        
    Returns:
        anomaly_id: ID of the newly created anomaly
    """
    query = """
    INSERT INTO anomalies (time_series_id, algorithm, start_time, end_time, 
                          severity, score, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    params = (time_series_id, algorithm, start_time, end_time, severity, score, status)
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            anomaly_id = result[0] if result else None
            conn.commit()
            return anomaly_id
    except Exception as e:
        logger.error(f"Error adding anomaly: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_anomalies(status=None, limit=50, offset=0):
    """
    Get anomalies from the database
    
    Args:
        status: Optional status to filter by
        limit: Maximum number of anomalies to return
        offset: Number of anomalies to skip
        
    Returns:
        anomalies: List of anomaly records
    """
    if status:
        query = """
        SELECT a.*, t.source, t.metric_name, t.tags
        FROM anomalies a
        JOIN time_series t ON a.time_series_id = t.id
        WHERE a.status = %s
        ORDER BY a.created_at DESC
        LIMIT %s OFFSET %s;
        """
        params = (status, limit, offset)
    else:
        query = """
        SELECT a.*, t.source, t.metric_name, t.tags
        FROM anomalies a
        JOIN time_series t ON a.time_series_id = t.id
        ORDER BY a.created_at DESC
        LIMIT %s OFFSET %s;
        """
        params = (limit, offset)
    
    return execute_query(query, params)

# Log activity
def log_activity(user_id, action, entity_type=None, entity_id=None, 
                details=None, ip_address=None):
    """
    Log user activity
    
    Args:
        user_id: User ID
        action: Action performed
        entity_type: Type of entity acted upon
        entity_id: ID of entity
        details: JSON details
        ip_address: IP address of the user
    """
    query = """
    INSERT INTO activity_logs (user_id, action, entity_type, entity_id, details, ip_address)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    params = (user_id, action, entity_type, entity_id, details, ip_address)
    
    execute_query(query, params, fetch=False)