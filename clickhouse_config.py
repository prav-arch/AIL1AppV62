"""
ClickHouse Configuration

This module centralizes ClickHouse configuration parameters and provides
utility functions to standardize connection handling.

In development environment (Replit), it will automatically use mock services.
On the GPU server, it will connect to the real ClickHouse database.
"""

import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ClickHouse connection parameters
CLICKHOUSE_HOST = os.environ.get('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.environ.get('CLICKHOUSE_PORT', 9000))
CLICKHOUSE_USER = os.environ.get('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.environ.get('CLICKHOUSE_PASSWORD', '')
CLICKHOUSE_DB = os.environ.get('CLICKHOUSE_DB', 'l1_app_db')

# Vector embedding dimension
VECTOR_DIMENSION = 384

# Check if we're in development mode or production
IS_DEVELOPMENT = os.environ.get('REPL_ID') is not None
USE_MOCK_DB = os.environ.get('USE_MOCK_DB', 'False') == 'True'

def get_connection_params():
    """Get ClickHouse connection parameters"""
    return {
        'host': CLICKHOUSE_HOST,
        'port': CLICKHOUSE_PORT,
        'user': CLICKHOUSE_USER,
        'password': CLICKHOUSE_PASSWORD,
        'database': CLICKHOUSE_DB
    }