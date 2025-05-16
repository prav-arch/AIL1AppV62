#!/usr/bin/env python
"""
Check the status of ClickHouse service and initialize tables if needed
"""
import logging
import sys
import os
from clickhouse_driver import Client

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get ClickHouse connection details from environment or use defaults
CLICKHOUSE_HOST = os.environ.get('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.environ.get('CLICKHOUSE_PORT', 9000))
CLICKHOUSE_USER = os.environ.get('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.environ.get('CLICKHOUSE_PASSWORD', '')
CLICKHOUSE_DATABASE = os.environ.get('CLICKHOUSE_DATABASE', 'l1_app_db')

def get_client():
    """Get a ClickHouse client connection"""
    try:
        client = Client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DATABASE,
            connect_timeout=5
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create ClickHouse client: {e}")
        return None

def check_server_status():
    """Check if ClickHouse server is running"""
    try:
        client = get_client()
        if client:
            result = client.execute("SELECT version()")
            version = result[0][0] if result and len(result) > 0 else "Unknown"
            logger.info(f"ClickHouse server is running (version: {version})")
            return True
        return False
    except Exception as e:
        logger.error(f"ClickHouse server is not running or not accessible: {e}")
        return False

def check_database_exists():
    """Check if the l1_app_db database exists"""
    try:
        client = get_client()
        if client:
            result = client.execute("SHOW DATABASES")
            databases = [row[0] for row in result]
            if CLICKHOUSE_DATABASE in databases:
                logger.info(f"Database '{CLICKHOUSE_DATABASE}' exists")
                return True
            else:
                logger.warning(f"Database '{CLICKHOUSE_DATABASE}' does not exist")
                return False
        return False
    except Exception as e:
        logger.error(f"Failed to check database existence: {e}")
        return False

def create_database():
    """Create the l1_app_db database if it doesn't exist"""
    try:
        client = Client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD
        )
        client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DATABASE}")
        logger.info(f"Database '{CLICKHOUSE_DATABASE}' created")
        return True
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False

def list_tables():
    """List all tables in the database"""
    try:
        client = get_client()
        if client:
            result = client.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            if tables:
                logger.info(f"Tables in '{CLICKHOUSE_DATABASE}': {', '.join(tables)}")
            else:
                logger.info(f"No tables found in '{CLICKHOUSE_DATABASE}'")
            return tables
        return []
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        return []

def main():
    """Main function"""
    logger.info("Checking ClickHouse service status...")
    
    if not check_server_status():
        logger.error("ClickHouse server is not running or not accessible")
        return 1
    
    if not check_database_exists():
        logger.info(f"Creating database '{CLICKHOUSE_DATABASE}'...")
        if not create_database():
            return 1
    
    tables = list_tables()
    
    if not tables:
        logger.info("No tables found. You need to initialize the database schema.")
        logger.info("Run 'python initialize_clickhouse_db.py' to create the necessary tables.")
    elif 'documents' in tables and 'llm_prompts' in tables:
        logger.info("Required tables exist. The database is ready to use.")
    else:
        required_tables = ['documents', 'document_chunks', 'vector_db_stats', 'llm_prompts']
        missing_tables = [table for table in required_tables if table not in tables]
        if missing_tables:
            logger.warning(f"Missing tables: {', '.join(missing_tables)}")
            logger.info("Run 'python fix_clickhouse_tables.py' to recreate the missing tables.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())