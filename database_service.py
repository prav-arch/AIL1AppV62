"""
ClickHouse Database Service for L1 Application

This module provides database functionality using ClickHouse 18.16.1 for:
1. Document storage
2. Document chunk storage
3. Database statistics

The vector operations are handled separately by FAISS.
"""

import os
import json
import uuid
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ClickHouse connection parameters
CLICKHOUSE_CONFIG = {
    'host': 'localhost',
    'port': 9000,
    'user': 'default',  # PostgreSQL user is always default
    'password': '',     # Password is empty
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

class ClickHouseService:
    """Service for ClickHouse database operations"""
    
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
            logger.error("Please make sure ClickHouse is running and accessible")
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
            
            # Create web_pages table for web scraping
            self.execute("""
            CREATE TABLE IF NOT EXISTS web_pages (
                id String,
                url String,
                title String,
                content String,
                metadata String,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree() ORDER BY id
            """)
            
            # Create page_chunks table for web scraping
            self.execute("""
            CREATE TABLE IF NOT EXISTS page_chunks (
                id UInt64,
                page_id String,
                chunk_index UInt32,
                chunk_text String,
                metadata String,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree() ORDER BY (page_id, chunk_index)
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
    
    # Web scraping specific methods
    def add_webpage(self, url, title, content, metadata=None):
        """Add a webpage to the database"""
        try:
            page_id = str(uuid.uuid4())
            metadata_str = json.dumps(metadata) if metadata else '{}'
            
            logger.info(f"Adding webpage: {title}")
            self.execute("""
            INSERT INTO web_pages (id, url, title, content, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """, (page_id, url, title, content, metadata_str))
            
            logger.info(f"Webpage added with ID: {page_id}")
            return page_id
        except Exception as e:
            logger.error(f"Error adding webpage: {e}")
            return None
    
    def add_page_chunks(self, page_id, chunks):
        """Add webpage chunks to the database"""
        if not chunks:
            logger.warning("No chunks to add")
            return []
        
        try:
            logger.info(f"Adding {len(chunks)} chunks for webpage {page_id}")
            
            chunk_ids = []
            timestamp = int(time.time() * 1000)
            
            for i, chunk_text in enumerate(chunks):
                chunk_id = timestamp + i
                chunk_ids.append(chunk_id)
                
                metadata = json.dumps({'index': i})
                
                self.execute("""
                INSERT INTO page_chunks (id, page_id, chunk_index, chunk_text, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """, (chunk_id, page_id, i, chunk_text, metadata))
            
            logger.info(f"Added {len(chunks)} page chunks with IDs: {chunk_ids}")
            return chunk_ids
        except Exception as e:
            logger.error(f"Error adding page chunks: {e}")
            return []
    
    def get_webpage(self, page_id):
        """Get a webpage by ID"""
        try:
            logger.info(f"Getting webpage: {page_id}")
            result = self.execute("""
            SELECT id, url, title, content, metadata, created_at
            FROM web_pages
            WHERE id = %s
            """, (page_id,))
            
            if not result:
                logger.warning(f"Webpage not found: {page_id}")
                return None
            
            row = result[0]
            webpage = {
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'content': row[3],
                'metadata': json.loads(row[4]) if row[4] else {},
                'created_at': row[5].isoformat() if row[5] else None
            }
            
            logger.info(f"Retrieved webpage: {webpage['title']}")
            return webpage
        except Exception as e:
            logger.error(f"Error getting webpage: {e}")
            return None
    
    def get_page_chunks(self, page_id):
        """Get chunks for a webpage"""
        try:
            logger.info(f"Getting chunks for webpage: {page_id}")
            result = self.execute("""
            SELECT id, page_id, chunk_index, chunk_text, metadata, created_at
            FROM page_chunks
            WHERE page_id = %s
            ORDER BY chunk_index
            """, (page_id,))
            
            chunks = []
            for row in result:
                chunks.append({
                    'id': row[0],
                    'page_id': row[1],
                    'chunk_index': row[2],
                    'chunk_text': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {},
                    'created_at': row[5].isoformat() if row[5] else None
                })
            
            logger.info(f"Retrieved {len(chunks)} chunks for webpage {page_id}")
            return chunks
        except Exception as e:
            logger.error(f"Error getting page chunks: {e}")
            return []
    
    def get_all_webpages(self, limit=100):
        """Get all webpages"""
        try:
            logger.info("Getting all webpages")
            result = self.execute(f"""
            SELECT id, url, title, metadata, created_at
            FROM web_pages
            ORDER BY created_at DESC
            LIMIT {limit}
            """)
            
            webpages = []
            for row in result:
                webpages.append({
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'created_at': row[4].isoformat() if row[4] else None
                })
            
            logger.info(f"Retrieved {len(webpages)} webpages")
            return webpages
        except Exception as e:
            logger.error(f"Error getting all webpages: {e}")
            return []

# FAISS vector class for handling embeddings
class FaissVectorService:
    """FAISS vector service for vector similarity search"""
    
    def __init__(self, dimension=384, index_path=None):
        """Initialize the FAISS vector service"""
        try:
            import faiss
            import numpy as np
            
            self.faiss = faiss
            self.np = np
            self.dimension = dimension
            self.index_path = index_path or 'data/faiss_index.bin'
            self.id_mapping_path = os.path.join(os.path.dirname(self.index_path), 'id_mapping.json')
            
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Load or create index
            self.index, self.id_map = self._load_or_create_index()
            
            logger.info(f"FAISS initialized with dimension {dimension}")
        except ImportError as e:
            logger.error(f"Error importing FAISS: {e}")
            logger.error("Please install FAISS with: pip install faiss-cpu")
            raise
    
    def _load_or_create_index(self):
        """Load an existing index or create a new one"""
        try:
            # Try to load existing index
            if os.path.exists(self.index_path):
                logger.info(f"Loading FAISS index from {self.index_path}")
                index = self.faiss.read_index(self.index_path)
                id_map = self._load_id_mapping()
                logger.info(f"FAISS index loaded with {index.ntotal} vectors")
                return index, id_map
        except Exception as e:
            logger.warning(f"Error loading index, creating a new one: {e}")
        
        # Create a new index
        return self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        logger.info("Creating new FAISS index")
        index = self.faiss.IndexFlatL2(self.dimension)
        id_map = {}
        return index, id_map
    
    def _load_id_mapping(self):
        """Load ID mapping from disk"""
        if os.path.exists(self.id_mapping_path):
            try:
                with open(self.id_mapping_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading ID mapping: {e}")
        return {}
    
    def _save_id_mapping(self):
        """Save ID mapping to disk"""
        try:
            with open(self.id_mapping_path, 'w') as f:
                json.dump(self.id_map, f)
        except Exception as e:
            logger.error(f"Error saving ID mapping: {e}")
    
    def _save_index(self):
        """Save index to disk"""
        try:
            logger.info(f"Saving FAISS index to {self.index_path}")
            self.faiss.write_index(self.index, self.index_path)
            self._save_id_mapping()
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def add_vectors(self, ids, vectors):
        """
        Add vectors to the index
        
        Args:
            ids: List of IDs (strings or ints)
            vectors: List of vectors (numpy arrays)
        """
        try:
            if not ids or not vectors or len(ids) != len(vectors):
                logger.warning("Invalid IDs or vectors")
                return
            
            # Convert vectors to numpy array
            vectors_array = self.np.array(vectors).astype('float32')
            
            # Add to index
            self.index.add(vectors_array)
            
            # Update ID mapping
            base_index = len(self.id_map)
            for i, id_val in enumerate(ids):
                self.id_map[base_index + i] = str(id_val)
            
            # Save index
            self._save_index()
            
            logger.info(f"Added {len(ids)} vectors to FAISS index")
        except Exception as e:
            logger.error(f"Error adding vectors to FAISS: {e}")
    
    def search(self, query_vector, top_k=5):
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            
        Returns:
            List of (ID, distance) tuples
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Index is empty, no results to return")
                return []
            
            # Convert query to numpy array
            if not isinstance(query_vector, self.np.ndarray):
                query_vector = self.np.array(query_vector).astype('float32')
            
            # Reshape if needed
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Search index
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            # Map indices to original IDs
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and str(idx) in self.id_map:  # -1 indicates no result
                    results.append((self.id_map[str(idx)], float(distances[0][i])))
            
            return results
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []
    
    def delete_vectors(self, ids):
        """
        Delete vectors from the index
        Note: Not all FAISS indices support removal, so we might need to rebuild the index
        
        Args:
            ids: List of IDs to remove
        """
        logger.warning("FAISS vector deletion is not fully supported in this implementation")
        return False
    
    def get_stats(self):
        """Get stats about the vector index"""
        return {
            'vector_count': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__,
            'id_mapping_count': len(self.id_map)
        }

# Wrapper service that combines ClickHouse and FAISS
class DatabaseService:
    """Combined database service with ClickHouse and FAISS"""
    
    def __init__(self):
        """Initialize the database service"""
        self.db = ClickHouseService()
        self.vector_service = FaissVectorService()
        
        # Initialize schema
        self.db.initialize_schema()
    
    def add_document(self, name, description, text, metadata=None):
        """Add a document with text and generate embeddings"""
        try:
            # Add document to ClickHouse
            document_id = self.db.add_document(name, description, metadata)
            if not document_id:
                return None
            
            # Split text into chunks
            chunks = self._chunk_text(text)
            
            # Add chunks to ClickHouse
            chunk_ids = self.db.add_chunks(document_id, chunks)
            
            # Generate embeddings and add to FAISS
            vectors = [self._generate_embeddings(chunk) for chunk in chunks]
            self.vector_service.add_vectors(chunk_ids, vectors)
            
            return document_id
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return None
    
    def _chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
        """Split text into overlapping chunks"""
        chunks = []
        
        # If text is shorter than chunk_size, return it as a single chunk
        if len(text) <= chunk_size:
            return [text]
        
        # Split text into chunks
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to find a good boundary (newline or period)
            if end < len(text):
                # Look for a newline or period to end the chunk
                for i in range(min(50, chunk_overlap)):
                    if end - i > start and (text[end - i] == '\n' or text[end - i] == '.'):
                        end = end - i + 1  # Include the newline or period
                        break
            
            # Add the chunk
            chunks.append(text[start:end])
            
            # Move to the next chunk, with overlap
            start = end - chunk_overlap
            
            # Make sure we're making progress
            if start >= end:
                start = end
        
        return chunks
    
    def _generate_embeddings(self, text):
        """
        Generate embeddings for text
        
        This is a simplified random embedding generator for demonstration.
        In a real application, you would use a proper embedding model.
        """
        import numpy as np
        
        # For consistency, seed the random generator with the hash of the text
        np.random.seed(hash(text) % 2**32)
        
        # Generate a random vector
        vector = np.random.rand(self.vector_service.dimension).astype(np.float32)
        
        # Normalize to unit length
        vector = vector / np.linalg.norm(vector)
        
        return vector
    
    def search_similar(self, query, top_k=5):
        """Search for chunks similar to the query"""
        try:
            # Generate query embedding
            query_vector = self._generate_embeddings(query)
            
            # Search FAISS index
            results = self.vector_service.search(query_vector, top_k)
            
            # Get chunk details
            chunks = []
            for chunk_id, distance in results:
                # Get chunk from ClickHouse
                chunk_result = self.db.execute("""
                SELECT dc.id, dc.document_id, dc.chunk_index, dc.chunk_text, 
                       d.name, d.description, d.metadata
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE dc.id = %s
                """, (int(chunk_id),))
                
                if chunk_result:
                    row = chunk_result[0]
                    chunks.append({
                        'chunk_id': row[0],
                        'document_id': row[1],
                        'chunk_index': row[2],
                        'text': row[3],
                        'document_name': row[4],
                        'document_description': row[5],
                        'metadata': json.loads(row[6]) if row[6] else {},
                        'similarity': 1.0 / (1.0 + distance)  # Convert distance to similarity score
                    })
            
            return chunks
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def add_webpage(self, url, title, content, metadata=None):
        """Add a webpage with content and generate embeddings"""
        try:
            # Add webpage to ClickHouse
            page_id = self.db.add_webpage(url, title, content, metadata)
            if not page_id:
                return None
            
            # Split content into chunks
            chunks = self._chunk_text(content)
            
            # Add chunks to ClickHouse
            chunk_ids = self.db.add_page_chunks(page_id, chunks)
            
            # Generate embeddings and add to FAISS
            vectors = [self._generate_embeddings(chunk) for chunk in chunks]
            self.vector_service.add_vectors(chunk_ids, vectors)
            
            return page_id
        except Exception as e:
            logger.error(f"Error adding webpage: {e}")
            return None
    
    def get_stats(self):
        """Get combined stats about the database and vector index"""
        db_stats = self.db.get_stats()
        vector_stats = self.vector_service.get_stats()
        
        return {
            **db_stats,
            **vector_stats
        }

# Example usage for testing
def test_database_service():
    """Test the database service functionality"""
    try:
        # Initialize service
        db_service = DatabaseService()
        
        # Add a test document
        document_id = db_service.add_document(
            name="Test Document",
            description="This is a test document",
            text="This is a test document with some text for embedding and searching. " * 10,
            metadata={"test": True}
        )
        
        if not document_id:
            logger.error("Failed to add test document")
            return False
        
        logger.info(f"Added document with ID: {document_id}")
        
        # Search for similar chunks
        results = db_service.search_similar("test document", top_k=3)
        
        logger.info(f"Search results: {results}")
        
        # Get stats
        stats = db_service.get_stats()
        
        logger.info(f"Database stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing database service: {e}")
        return False

if __name__ == "__main__":
    # Run tests
    test_database_service()