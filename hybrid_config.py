"""
Configuration for hybrid ClickHouse 18.16.1 + FAISS setup
This file configures the application to use:
- ClickHouse 18.16.1 for regular database operations
- FAISS for vector search operations
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    # ClickHouse connection information
    'clickhouse': {
        'host': os.getenv('CLICKHOUSE_HOST', 'localhost'),
        'port': int(os.getenv('CLICKHOUSE_PORT', 9000)),
        'user': os.getenv('CLICKHOUSE_USER', 'l1_app_user'),
        'password': os.getenv('CLICKHOUSE_PASSWORD', 'test'),
        'database': os.getenv('CLICKHOUSE_DATABASE', 'l1_app_db'),
        'version': '18.16.1',  # Specific ClickHouse version
    },
    
    # Use FAISS for vector operations instead of ClickHouse
    'vector_db': 'faiss',
    
    # FAISS configuration
    'faiss': {
        'index_dir': os.getenv('FAISS_INDEX_DIR', os.path.join(os.path.expanduser('~'), 'faiss_indices')),
        'index_type': 'L2',  # Type of FAISS index (L2, IP, Cosine)
        'dimension': 384,    # Dimension of the vectors
        'use_gpu': False,    # Whether to use GPU acceleration
    }
}

# Create directories if they don't exist
os.makedirs(DB_CONFIG['faiss']['index_dir'], exist_ok=True)

# Set default connection string for the application
if os.environ.get('DATABASE_URL') is None:
    conn_string = f"clickhouse://{DB_CONFIG['clickhouse']['user']}:{DB_CONFIG['clickhouse']['password']}@{DB_CONFIG['clickhouse']['host']}:{DB_CONFIG['clickhouse']['port']}/{DB_CONFIG['clickhouse']['database']}"
    os.environ['DATABASE_URL'] = conn_string
    logger.info(f"Set DATABASE_URL to {conn_string}")

# Set vector storage type to FAISS explicitly
if os.environ.get('VECTOR_STORAGE') is None:
    os.environ['VECTOR_STORAGE'] = 'faiss'
    logger.info("Set VECTOR_STORAGE to faiss")