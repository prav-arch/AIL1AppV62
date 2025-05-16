#!/usr/bin/env python
"""
Fix ClickHouse table structures to match model definitions
"""
import logging
from clickhouse_driver import Client
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get ClickHouse connection details from environment or use defaults
CLICKHOUSE_HOST = os.environ.get('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.environ.get('CLICKHOUSE_PORT', 9000))
CLICKHOUSE_USER = os.environ.get('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.environ.get('CLICKHOUSE_PASSWORD', '')
CLICKHOUSE_DATABASE = os.environ.get('CLICKHOUSE_DATABASE', 'l1_app_db')

def get_client():
    """Get a ClickHouse client connection"""
    return Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DATABASE
    )

def fix_documents_table():
    """Drop and recreate documents table with correct structure"""
    client = get_client()
    
    # Create database if it doesn't exist
    client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DATABASE}")
    
    # Drop existing table if it exists
    client.execute("DROP TABLE IF EXISTS documents")
    
    # Create table with all required columns
    create_query = """
    CREATE TABLE documents (
        id String,
        name String,
        description String,
        metadata String,
        file_path String,
        created_at DateTime DEFAULT now(),
        minio_url String,
        bucket String,
        storage_type String,
        status String,
        indexed UInt8,
        filename String,
        file_size UInt64
    ) ENGINE = MergeTree() ORDER BY id
    """
    
    client.execute(create_query)
    logger.info("Documents table recreated successfully")

def fix_llm_prompts_table():
    """Drop and recreate llm_prompts table with correct structure"""
    client = get_client()
    
    # Drop existing table if it exists
    client.execute("DROP TABLE IF EXISTS llm_prompts")
    
    # Create table with all required columns
    create_query = """
    CREATE TABLE llm_prompts (
        id String,
        prompt String,
        response String,
        metadata String,
        user_id String,
        created_at DateTime DEFAULT now(),
        response_time Float64
    ) ENGINE = MergeTree() ORDER BY id
    """
    
    client.execute(create_query)
    logger.info("LLM prompts table recreated successfully")

if __name__ == "__main__":
    try:
        logger.info("Fixing ClickHouse tables...")
        fix_documents_table()
        fix_llm_prompts_table()
        logger.info("All tables fixed successfully")
    except Exception as e:
        logger.error(f"Error fixing tables: {e}")