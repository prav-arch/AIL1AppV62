#!/bin/bash

# Script to set up hybrid ClickHouse 18.16.1 + FAISS environment
# This script creates environment variables and directories for the hybrid setup

# Create directories for FAISS indices
mkdir -p $HOME/faiss_indices

# Create .env file with hybrid configuration
cat > $HOME/.env << EOL
# Hybrid ClickHouse 18.16.1 + FAISS Configuration

# ClickHouse Connection Details
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=l1_app_user
CLICKHOUSE_PASSWORD=test
CLICKHOUSE_DATABASE=l1_app_db

# Vector Storage Configuration
VECTOR_STORAGE=faiss
FAISS_INDEX_DIR=$HOME/faiss_indices
FAISS_INDEX_TYPE=L2
FAISS_DIMENSION=384
FAISS_USE_GPU=false

# Database Type
DATABASE_TYPE=hybrid
DATABASE_URL=clickhouse://l1_app_user:test@localhost:9000/l1_app_db
EOL

# Create the ClickHouse schema file
cat > clickhouse_schema.sql << EOL
-- ClickHouse 18.16.1 Database Schema
-- This schema is compatible with ClickHouse 18.16.1 and doesn't use any
-- vector-specific features (which will be handled by FAISS instead)

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS l1_app_db;

-- Use the database
USE l1_app_db;

-- Documents table to store document metadata
CREATE TABLE IF NOT EXISTS documents
(
    id String,
    name String,
    description String,
    metadata String,
    file_path String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- Document chunks table to store text chunks
-- Note: embeddings are NOT stored in ClickHouse, only the chunk text
-- The embeddings will be generated and stored in FAISS separately
CREATE TABLE IF NOT EXISTS document_chunks
(
    id UInt64,
    document_id String,
    chunk_index UInt32,
    chunk_text String,
    metadata String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (document_id, chunk_index);

-- Create an index to speed up lookups by document_id
ALTER TABLE document_chunks ADD INDEX idx_document_id document_id TYPE minmax GRANULARITY 8192;

-- Vector database stats for tracking
CREATE TABLE IF NOT EXISTS vector_db_stats
(
    id UInt8,
    documents_count UInt32 DEFAULT 0,
    chunks_count UInt32 DEFAULT 0,
    vector_dim UInt16,
    last_modified DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY id;

-- Insert initial stats
INSERT INTO vector_db_stats (id, vector_dim) VALUES (1, 384) ON DUPLICATE KEY UPDATE last_modified = now();
EOL

# Create initialization script
cat > initialize_hybrid_db.py << EOL
#!/usr/bin/env python3

"""
Initialization script for hybrid ClickHouse 18.16.1 + FAISS setup
"""

import os
import sys
import logging
from dotenv import load_dotenv
from clickhouse_driver import Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """Initialize the hybrid database"""
    logger.info("Initializing hybrid ClickHouse + FAISS setup")
    
    # Get ClickHouse connection parameters
    host = os.getenv('CLICKHOUSE_HOST', 'localhost')
    port = int(os.getenv('CLICKHOUSE_PORT', 9000))
    user = os.getenv('CLICKHOUSE_USER', 'l1_app_user')
    password = os.getenv('CLICKHOUSE_PASSWORD', 'test')
    database = os.getenv('CLICKHOUSE_DATABASE', 'l1_app_db')
    
    # Connect to ClickHouse
    try:
        logger.info(f"Connecting to ClickHouse at {host}:{port}")
        client = Client(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=10
        )
        logger.info("Connected to ClickHouse successfully")
    except Exception as e:
        logger.error(f"Error connecting to ClickHouse: {e}")
        sys.exit(1)
    
    # Create database
    try:
        logger.info(f"Creating database '{database}' if it doesn't exist")
        client.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        logger.info(f"Database '{database}' created or already exists")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        sys.exit(1)
    
    # Select database
    client.execute(f"USE {database}")
    
    # Read schema file
    try:
        with open('clickhouse_schema.sql', 'r') as f:
            schema = f.read()
        
        # Split the schema into individual queries
        queries = [q.strip() for q in schema.split(';') if q.strip()]
        
        # Execute each query
        for query in queries:
            try:
                logger.info(f"Executing query: {query[:50]}...")
                client.execute(query)
            except Exception as e:
                logger.error(f"Error executing schema query: {e}")
                logger.error(f"Query: {query}")
        
        logger.info("Database schema created successfully")
    except Exception as e:
        logger.error(f"Error reading or executing schema: {e}")
        sys.exit(1)
    
    # Create FAISS index directory
    faiss_index_dir = os.getenv('FAISS_INDEX_DIR', os.path.join(os.path.expanduser('~'), 'faiss_indices'))
    os.makedirs(faiss_index_dir, exist_ok=True)
    logger.info(f"FAISS index directory created at {faiss_index_dir}")
    
    logger.info("Hybrid database initialization complete!")
    logger.info(f"ClickHouse connection: clickhouse://{user}:{password}@{host}:{port}/{database}")
    logger.info(f"FAISS index directory: {faiss_index_dir}")

if __name__ == "__main__":
    main()
EOL

# Make the initialization script executable
chmod +x initialize_hybrid_db.py

echo "=== Hybrid ClickHouse 18.16.1 + FAISS Setup Complete ==="
echo ""
echo "Environment configuration created at $HOME/.env"
echo "ClickHouse schema created at $(pwd)/clickhouse_schema.sql"
echo "Initialization script created at $(pwd)/initialize_hybrid_db.py"
echo ""
echo "Next steps:"
echo "1. Install the required Python packages:"
echo "   ./install_requirements.sh"
echo ""
echo "2. Make sure ClickHouse 18.16.1 is running"
echo ""
echo "3. Initialize the hybrid database:"
echo "   python initialize_hybrid_db.py"
echo ""
echo "4. Use the hybrid database service in your application"
echo "   by importing hybrid_db_service.py"