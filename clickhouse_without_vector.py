"""
Basic ClickHouse 18.16.1 Integration (No Vector/Embedding Column)
This module provides basic database access and functions without vector operations
"""

import logging
import json
import time
import uuid
from typing import List, Dict, Any, Optional

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

# Import here to allow for clear error messages
try:
    from clickhouse_driver import Client
    logger.info("Successfully imported clickhouse_driver")
except ImportError as e:
    logger.error(f"Error importing clickhouse_driver: {e}")
    logger.error("Please install clickhouse-driver with: pip install clickhouse-driver")
    raise

class ClickHouseDB:
    """Basic ClickHouse database access class"""
    
    def __init__(self, config=None):
        """Initialize ClickHouse connection"""
        self.config = config or CLICKHOUSE_CONFIG
        self.client = self._connect()
    
    def _connect(self):
        """Connect to ClickHouse"""
        try:
            logger.info(f"Connecting to ClickHouse at {self.config['host']}:{self.config['port']}")
            client = Client(**self.config)
            
            # Test connection with a simple query
            result = client.execute("SELECT 1")
            logger.info(f"Connected to ClickHouse successfully. Test query result: {result}")
            
            return client
        except Exception as e:
            logger.error(f"Error connecting to ClickHouse: {e}")
            raise
    
    def execute(self, query, params=None):
        """Execute a query with parameters"""
        try:
            return self.client.execute(query, params or {})
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def initialize_schema(self):
        """Initialize database schema"""
        try:
            # Create database if it doesn't exist
            self.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            
            # Use the database
            self.execute(f"USE {self.config['database']}")
            
            # Create documents table
            self.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id String,
                name String,
                description String,
                metadata String,
                file_path String,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree() ORDER BY id
            """)
            
            # Create document_chunks table - NO embedding column
            self.execute("""
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
            self.execute("""
            CREATE TABLE IF NOT EXISTS vector_db_stats (
                id UInt8,
                documents_count UInt32 DEFAULT 0,
                chunks_count UInt32 DEFAULT 0,
                vector_dim UInt16,
                last_modified DateTime DEFAULT now()
            ) ENGINE = ReplacingMergeTree() ORDER BY id
            """)
            
            # Initialize stats if needed
            self.execute("""
            INSERT INTO vector_db_stats (id, documents_count, chunks_count, vector_dim)
            VALUES (1, 0, 0, 384)
            IF NOT EXISTS
            """)
            
            logger.info("Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            return False
    
    def add_document(self, name, description, metadata=None, file_path=None):
        """Add a document to the database"""
        try:
            document_id = str(uuid.uuid4())
            metadata_str = json.dumps(metadata) if metadata else '{}'
            file_path = file_path or ''
            
            logger.info(f"Adding document: {name}")
            self.execute("""
            INSERT INTO documents (id, name, description, metadata, file_path)
            VALUES (%s, %s, %s, %s, %s)
            """, (document_id, name, description, metadata_str, file_path))
            
            # Update document count
            self.execute("""
            UPDATE vector_db_stats
            SET documents_count = documents_count + 1, last_modified = now()
            WHERE id = 1
            """)
            
            logger.info(f"Document added with ID: {document_id}")
            return document_id
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return None
    
    def add_chunks(self, document_id, chunks):
        """Add document chunks to the database"""
        if not chunks:
            logger.warning("No chunks to add")
            return []
        
        try:
            logger.info(f"Adding {len(chunks)} chunks for document {document_id}")
            
            chunk_ids = []
            timestamp = int(time.time() * 1000)
            
            for i, chunk_text in enumerate(chunks):
                chunk_id = timestamp + i
                chunk_ids.append(chunk_id)
                
                metadata = json.dumps({'index': i})
                
                self.execute("""
                INSERT INTO document_chunks (id, document_id, chunk_index, chunk_text, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """, (chunk_id, document_id, i, chunk_text, metadata))
            
            # Update chunk count
            self.execute("""
            UPDATE vector_db_stats
            SET chunks_count = chunks_count + %s, last_modified = now()
            WHERE id = 1
            """, (len(chunks),))
            
            logger.info(f"Added {len(chunks)} chunks with IDs: {chunk_ids}")
            return chunk_ids
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            return []
    
    def get_document(self, document_id):
        """Get a document by ID"""
        try:
            logger.info(f"Getting document: {document_id}")
            result = self.execute("""
            SELECT id, name, description, metadata, file_path, created_at
            FROM documents
            WHERE id = %s
            """, (document_id,))
            
            if not result:
                logger.warning(f"Document not found: {document_id}")
                return None
            
            row = result[0]
            document = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'file_path': row[4],
                'created_at': row[5].isoformat() if row[5] else None
            }
            
            logger.info(f"Retrieved document: {document['name']}")
            return document
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    def get_chunks(self, document_id):
        """Get chunks for a document"""
        try:
            logger.info(f"Getting chunks for document: {document_id}")
            result = self.execute("""
            SELECT id, document_id, chunk_index, chunk_text, metadata, created_at
            FROM document_chunks
            WHERE document_id = %s
            ORDER BY chunk_index
            """, (document_id,))
            
            chunks = []
            for row in result:
                chunks.append({
                    'id': row[0],
                    'document_id': row[1],
                    'chunk_index': row[2],
                    'chunk_text': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {},
                    'created_at': row[5].isoformat() if row[5] else None
                })
            
            logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
            return chunks
        except Exception as e:
            logger.error(f"Error getting chunks: {e}")
            return []
    
    def get_all_documents(self, limit=100):
        """Get all documents"""
        try:
            logger.info("Getting all documents")
            result = self.execute(f"""
            SELECT id, name, description, metadata, file_path, created_at
            FROM documents
            ORDER BY created_at DESC
            LIMIT {limit}
            """)
            
            documents = []
            for row in result:
                documents.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'file_path': row[4],
                    'created_at': row[5].isoformat() if row[5] else None
                })
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        try:
            logger.info("Getting database statistics")
            result = self.execute("""
            SELECT documents_count, chunks_count, vector_dim, last_modified
            FROM vector_db_stats
            WHERE id = 1
            """)
            
            if not result:
                logger.warning("No stats found")
                return {
                    'documents_count': 0,
                    'chunks_count': 0,
                    'vector_dim': 384,
                    'last_modified': None
                }
            
            row = result[0]
            stats = {
                'documents_count': row[0],
                'chunks_count': row[1],
                'vector_dim': row[2],
                'last_modified': row[3].isoformat() if row[3] else None
            }
            
            logger.info(f"Stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'documents_count': 0,
                'chunks_count': 0,
                'vector_dim': 384,
                'last_modified': None
            }

def test_clickhouse():
    """Test basic ClickHouse functionality"""
    try:
        # Connect to ClickHouse
        db = ClickHouseDB()
        
        # Initialize schema
        db.initialize_schema()
        
        # Add a test document
        document_id = db.add_document(
            name="Test Document",
            description="This is a test document",
            metadata={"test": True}
        )
        
        if not document_id:
            logger.error("Failed to add test document")
            return False
        
        # Add chunks
        chunks = [
            "This is the first chunk of the test document.",
            "This is the second chunk of the test document.",
            "This is the third chunk of the test document."
        ]
        
        chunk_ids = db.add_chunks(document_id, chunks)
        
        if not chunk_ids:
            logger.error("Failed to add chunks")
            return False
        
        # Get document
        document = db.get_document(document_id)
        if not document:
            logger.error("Failed to get document")
            return False
        
        # Get chunks
        retrieved_chunks = db.get_chunks(document_id)
        if not retrieved_chunks:
            logger.error("Failed to get chunks")
            return False
        
        # Get stats
        stats = db.get_stats()
        
        logger.info("All tests passed successfully!")
        logger.info(f"Document ID: {document_id}")
        logger.info(f"Chunk IDs: {chunk_ids}")
        logger.info(f"Document: {document}")
        logger.info(f"Chunks: {len(retrieved_chunks)} chunks")
        logger.info(f"Stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests
    test_clickhouse()