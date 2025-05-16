"""
PostgreSQL Vector Database Service using pgvector

This module provides functionality for working with PostgreSQL + pgvector as a vector database:
1. Creating and managing a vector index
2. Converting documents to embeddings
3. Adding documents to the vector database
4. Searching the vector database
"""

import os
import json
import time
import logging
import numpy as np
import psycopg2
from psycopg2.extras import Json, DictCursor, execute_values
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

class PgVectorDBService:
    """Service for managing PostgreSQL vector database operations"""
    
    def __init__(self, vector_dim: int = 384):
        """
        Initialize the PostgreSQL vector database service
        
        Args:
            vector_dim: Dimension of the vectors
        """
        self.vector_dim = vector_dim
        self.conn = None
        self.db_url = os.environ.get('DATABASE_URL')
        
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not found")
            
        # Initialize database
        self._initialize_db()
    
    def _get_connection(self):
        """
        Get a database connection
        
        Returns:
            psycopg2 connection object
        """
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(self.db_url)
        return self.conn
    
    def _initialize_db(self):
        """
        Initialize the database with the required tables and extension
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if pgvector extension already exists
            try:
                # Create pgvector extension if it doesn't exist
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                conn.commit()
                logger.info("pgvector extension created or already exists")
            except Exception as e:
                logger.error(f"Error creating pgvector extension: {str(e)}")
                logger.info("Continuing without pgvector - will use alternative approach")
                if conn:
                    conn.rollback()
                
                # Use a simpler approach without the vector extension
                # We'll store the vectors as TEXT instead and convert when needed
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        description TEXT,
                        metadata JSONB,
                        file_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id SERIAL PRIMARY KEY,
                        document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
                        chunk_index INTEGER,
                        chunk_text TEXT,
                        embedding_json TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(document_id, chunk_index)
                    );
                """)
                
                if conn:
                    conn.commit()
                
                # Create stats table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vector_db_stats (
                        id INTEGER PRIMARY KEY,
                        documents_count INTEGER DEFAULT 0,
                        chunks_count INTEGER DEFAULT 0,
                        vector_dim INTEGER,
                        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Insert initial stats if not exists
                cursor.execute("""
                    INSERT INTO vector_db_stats (id, vector_dim)
                    VALUES (1, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (self.vector_dim,))
                
                if conn:
                    conn.commit()
                logger.info("Database initialized with alternative schema")
                return
            
            # If we got here, pgvector is available, so create tables normally
            
            # Create documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    metadata JSONB,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create vector chunks table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER,
                    chunk_text TEXT,
                    embedding vector({self.vector_dim}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(document_id, chunk_index)
                );
            """)
            
            # Try to create index on the vector column
            # Skip vector index creation as we're using FAISS instead
            logger.info("Skipping PostgreSQL vector index creation since we're using FAISS")
            
            # Create stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_db_stats (
                    id INTEGER PRIMARY KEY,
                    documents_count INTEGER DEFAULT 0,
                    chunks_count INTEGER DEFAULT 0,
                    vector_dim INTEGER,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert initial stats if not exists
            cursor.execute("""
                INSERT INTO vector_db_stats (id, vector_dim)
                VALUES (1, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (self.vector_dim,))
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
    def _generate_embeddings(self, text: str) -> np.ndarray:
        """
        Generate embeddings for text using a simple method
        
        In production, this would use a proper embedding model like:
        - SentenceTransformers
        - OpenAI Embeddings API
        - Hugging Face models
        
        For this demo, we'll use a simple mock implementation
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            Embeddings vector
        """
        # In a real implementation, you would use a proper embedding model
        # Here we just use a simple method to generate random embeddings for demo purposes
        
        # For consistency, we use the hash of the text to seed the random generator
        np.random.seed(hash(text) % 2**32)
        
        # Generate a random vector of the right dimension
        vector = np.random.rand(self.vector_dim).astype(np.float32)
        
        # Normalize to unit length
        vector = vector / np.linalg.norm(vector)
        
        return vector
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split into chunks
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
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
    
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a document to the vector database
        
        Args:
            doc_id: Unique identifier for the document
            text: Document text
            metadata: Additional metadata about the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Chunk the document
            chunks = self._chunk_text(text)
            
            # Create document metadata if not provided
            if metadata is None:
                metadata = {}
            
            # Add basic metadata
            base_metadata = {
                'id': doc_id,
                'added': datetime.now().isoformat(),
                'chunks_count': len(chunks),
                'text_length': len(text)
            }
            metadata.update(base_metadata)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert document
            cursor.execute("""
                INSERT INTO documents (id, name, description, metadata, file_path)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    metadata = EXCLUDED.metadata,
                    file_path = EXCLUDED.file_path
            """, (
                doc_id,
                metadata.get('name', doc_id),
                metadata.get('description', ''),
                Json(metadata),
                metadata.get('file_path', '')
            ))
            
            # Check if we're using pgvector or the fallback approach
            has_vector_column = True
            try:
                cursor.execute("SELECT embedding FROM document_chunks LIMIT 1")
                cursor.fetchone()  # This will raise an exception if the column doesn't exist
            except Exception:
                logger.info("Using embedding_json fallback for document chunks")
                has_vector_column = False
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Generate embedding
                vector = self._generate_embeddings(chunk)
                
                # Insert based on available columns
                if has_vector_column:
                    # Using pgvector
                    cursor.execute("""
                        INSERT INTO document_chunks 
                            (document_id, chunk_index, chunk_text, embedding, metadata)
                        VALUES 
                            (%s, %s, %s, %s::vector, %s)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                            chunk_text = EXCLUDED.chunk_text,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                    """, (
                        doc_id,
                        i,
                        chunk,
                        str(vector.tolist()),
                        Json({'index': i, 'length': len(chunk)})
                    ))
                else:
                    # Using fallback
                    cursor.execute("""
                        INSERT INTO document_chunks 
                            (document_id, chunk_index, chunk_text, embedding_json, metadata)
                        VALUES 
                            (%s, %s, %s, %s, %s)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                            chunk_text = EXCLUDED.chunk_text,
                            embedding_json = EXCLUDED.embedding_json,
                            metadata = EXCLUDED.metadata
                    """, (
                        doc_id,
                        i,
                        chunk,
                        json.dumps(vector.tolist()),
                        Json({'index': i, 'length': len(chunk)})
                    ))
            
            # Update stats
            cursor.execute("""
                UPDATE vector_db_stats
                SET 
                    documents_count = (SELECT COUNT(*) FROM documents),
                    chunks_count = (SELECT COUNT(*) FROM document_chunks),
                    last_modified = CURRENT_TIMESTAMP
                WHERE id = 1
            """)
            
            conn.commit()
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks to the vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector database: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the vector database for documents similar to the query
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of search results with document IDs and scores
        """
        try:
            # Generate query embedding
            query_vector = self._generate_embeddings(query)
            
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            # Check if we're using pgvector or the fallback approach
            has_vector_column = True
            try:
                cursor.execute("SELECT embedding FROM document_chunks LIMIT 1")
                cursor.fetchone()  # This will raise an exception if the column doesn't exist
            except Exception:
                logger.info("Using embedding_json fallback for search")
                has_vector_column = False
            
            if has_vector_column:
                # Search using pgvector similarity
                try:
                    cursor.execute("""
                        SELECT 
                            dc.id as chunk_id,
                            dc.document_id,
                            d.name as document_name,
                            dc.chunk_text,
                            dc.embedding <-> %s::vector as distance,
                            d.metadata,
                            d.file_path
                        FROM 
                            document_chunks dc
                        JOIN 
                            documents d ON dc.document_id = d.id
                        ORDER BY 
                            distance ASC
                        LIMIT %s
                    """, (str(query_vector.tolist()), top_k))
                except Exception as e:
                    logger.error(f"Error with pgvector search: {str(e)}")
                    # Fallback to manual calculation
                    has_vector_column = False
            
            results = []
            
            if not has_vector_column:
                # Fallback approach with manual similarity calculation
                # Get all chunks
                cursor.execute("""
                    SELECT 
                        dc.id as chunk_id,
                        dc.document_id,
                        d.name as document_name,
                        dc.chunk_text,
                        dc.embedding_json,
                        d.metadata,
                        d.file_path
                    FROM 
                        document_chunks dc
                    JOIN 
                        documents d ON dc.document_id = d.id
                """)
                
                # Manually calculate distances
                all_results = []
                for row in cursor:
                    try:
                        # Parse the embedding JSON
                        embedding = None
                        if row['embedding_json']:
                            embedding = np.array(json.loads(row['embedding_json']))
                        
                        if embedding is None:
                            continue
                            
                        # Calculate distance (using Euclidean distance)
                        distance = np.linalg.norm(embedding - query_vector)
                        
                        all_results.append({
                            'row': row,
                            'distance': distance
                        })
                    except Exception as e:
                        logger.warning(f"Error processing row {row['chunk_id']}: {str(e)}")
                
                # Sort by distance and take top k
                all_results.sort(key=lambda x: x['distance'])
                top_results = all_results[:top_k]
                
                # Format results
                for result in top_results:
                    row = result['row']
                    distance = result['distance']
                    similarity = 1.0 / (1.0 + distance)
                    
                    results.append({
                        'document_id': row['document_id'],
                        'chunk_id': f"{row['document_id']}_chunk_{row['chunk_id']}",
                        'document_name': row['document_name'],
                        'text': row['chunk_text'],
                        'score': distance,
                        'similarity': similarity,
                        'metadata': row['metadata'],
                        'file_path': row['file_path']
                    })
            else:
                # Process results from pgvector query
                for row in cursor:
                    # Calculate a similarity score from the distance (lower distance = higher similarity)
                    distance = float(row['distance'])
                    similarity = 1.0 / (1.0 + distance)
                    
                    results.append({
                        'document_id': row['document_id'],
                        'chunk_id': f"{row['document_id']}_chunk_{row['chunk_id']}",
                        'document_name': row['document_name'],
                        'text': row['chunk_text'],
                        'score': distance,
                        'similarity': similarity,
                        'metadata': row['metadata'],
                        'file_path': row['file_path']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database
        
        Returns:
            Dictionary of statistics
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Initialize stats dictionary
            stats = {
                'documents_count': 0,
                'chunks_count': 0,
                'vector_dim': self.vector_dim,
                'last_modified': datetime.now().isoformat(),
                'documents_size': '0 bytes',
                'chunks_size': '0 bytes'
            }
            
            # Get stats from the database
            try:
                cursor.execute("SELECT * FROM vector_db_stats WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    # Access by index instead of by name for compatibility
                    stats['documents_count'] = row[1]  # documents_count is the 2nd column
                    stats['chunks_count'] = row[2]     # chunks_count is the 3rd column
                    stats['vector_dim'] = row[3]       # vector_dim is the 4th column
                    if row[4]:  # last_modified is the 5th column
                        stats['last_modified'] = row[4].isoformat()
            except Exception as e:
                logger.warning(f"Error getting stats from vector_db_stats: {str(e)}")
            
            # Add additional stats
            try:
                cursor.execute("SELECT COUNT(*) FROM documents")
                count = cursor.fetchone()
                if count and count[0]:
                    stats['documents_count'] = count[0]
            except Exception as e:
                logger.warning(f"Error counting documents: {str(e)}")
            
            try:
                cursor.execute("SELECT COUNT(*) FROM document_chunks")
                count = cursor.fetchone()
                if count and count[0]:
                    stats['chunks_count'] = count[0]
            except Exception as e:
                logger.warning(f"Error counting document chunks: {str(e)}")
            
            # Get size information
            try:
                cursor.execute("""
                    SELECT 
                        pg_size_pretty(pg_total_relation_size('documents')) as documents_size,
                        pg_size_pretty(pg_total_relation_size('document_chunks')) as chunks_size
                """)
                size_info = cursor.fetchone()
                if size_info:
                    stats['documents_size'] = size_info[0]  # documents_size
                    stats['chunks_size'] = size_info[1]     # chunks_size
            except Exception as e:
                logger.warning(f"Could not get size information: {str(e)}")
                stats['documents_size'] = 'Unknown'
                stats['chunks_size'] = 'Unknown'
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting vector database stats: {str(e)}")
            return {
                'documents_count': 0,
                'chunks_count': 0,
                'vector_dim': self.vector_dim,
                'error': str(e)
            }
    
    def get_documents(self) -> Dict[str, Any]:
        """
        Get all documents in the vector database
        
        Returns:
            Dictionary of document metadata
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            cursor.execute("SELECT id, name, description, metadata, file_path FROM documents")
            
            documents = {}
            for row in cursor:
                doc_id = row['id']
                documents[doc_id] = {
                    'id': doc_id,
                    'name': row['name'],
                    'description': row['description'],
                    'file_path': row['file_path'],
                    'metadata': row['metadata']
                }
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents from vector database: {str(e)}")
            return {}
    
    def reset(self) -> bool:
        """
        Reset the vector database, removing all documents
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete all documents (cascades to chunks)
            cursor.execute("DELETE FROM documents")
            
            # Reset stats
            cursor.execute("""
                UPDATE vector_db_stats
                SET 
                    documents_count = 0,
                    chunks_count = 0,
                    last_modified = CURRENT_TIMESTAMP
                WHERE id = 1
            """)
            
            conn.commit()
            
            logger.info("Reset vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting vector database: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

# Create a singleton instance
pg_vector_db_service = PgVectorDBService()