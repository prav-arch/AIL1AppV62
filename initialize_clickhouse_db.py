#!/usr/bin/env python
"""
Initialize ClickHouse Database for RAG Application
Creates all necessary tables and initial data
"""
import os
import sys
import logging
from clickhouse_models import (
    Document, 
    DocumentChunk, 
    VectorDBStats, 
    LLMPrompt,
    initialize_database
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the ClickHouse database schema"""
    try:
        logger.info("Creating ClickHouse database tables...")
        
        # Initialize all tables
        initialize_database()
        
        # Initialize statistics
        VectorDBStats.initialize(vector_dim=384)
        
        logger.info("ClickHouse database schema initialized successfully")
        return 0
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())