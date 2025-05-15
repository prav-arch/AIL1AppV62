"""
Vector Database Service using PostgreSQL

This module provides functionality for working with vectors in PostgreSQL:
1. Converting documents to embeddings
2. Storing document content and metadata in PostgreSQL
3. Storing vector embeddings in PostgreSQL
4. Performing vector similarity search
"""

import os
import json
import time
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime
import pickle
import psycopg2
from psycopg2.extras import RealDictCursor

# Import database module
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import get_connection, execute_query

# Set up logger
logger = logging.getLogger(__name__)

class PostgresVectorDBService:
    """Service for managing vector database operations in PostgreSQL"""
    
    def __init__(self, vector_dim: int = 384):
        """
        Initialize the vector database service
        
        Args:
            vector_dim: Dimension of the vectors
        """
        self.vector_dim = vector_dim
        
        # Ensure the database tables are created
        self._init_tables()
    
    def _init_tables(self):
        """
        Initialize database tables for vector storage
        """
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # Check and create documents table if not exists
                cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    content TEXT,
                    file_path VARCHAR(255),
                    file_type VARCHAR(50),
                    file_size INTEGER,
                    source VARCHAR(255),
                    source_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                );
                """)
                
                # Check and create document_chunks table if not exists
                cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    embedding_data BYTEA,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                
                conn.commit()
            logger.info("Vector database tables initialized")
        except Exception as e:
            logger.error(f"Error initializing vector database tables: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
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
            
            # Extract metadata fields
            title = metadata.get('name', f"Document {doc_id}")
            description = metadata.get('description', '')
            file_path = metadata.get('file_path', '')
            file_type = metadata.get('file_type', '')
            file_size = metadata.get('file_size', 0)
            source = metadata.get('source', 'upload')
            source_url = metadata.get('source_url', '')
            
            # Insert document into the database
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO documents (title, description, content, file_path, file_type, 
                                     file_size, source, source_url, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """, (title, description, text, file_path, file_type, file_size, 
                     source, source_url, json.dumps(metadata)))
                
                db_doc_id = cur.fetchone()[0]
                
                # Process each chunk
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    vector = self._generate_embeddings(chunk)
                    
                    # Serialize the embedding
                    embedding_data = pickle.dumps(vector)
                    
                    # Insert chunk
                    cur.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding_data)
                    VALUES (%s, %s, %s, %s);
                    """, (db_doc_id, chunk, i, psycopg2.Binary(embedding_data)))
                
                conn.commit()
                
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks to the database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to database: {str(e)}")
            if 'conn' in locals() and conn:
                conn.rollback()
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
            
            # Get all chunks with their embeddings
            conn = get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                SELECT dc.id, dc.document_id, dc.chunk_text, dc.embedding_data,
                       d.title, d.description, d.file_path, d.metadata
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                """)
                
                chunks = cur.fetchall()
            
            # If no chunks, return empty results
            if not chunks:
                return []
            
            # Calculate similarity for each chunk
            results = []
            for chunk in chunks:
                # Deserialize the embedding
                chunk_vector = pickle.loads(chunk['embedding_data'])
                
                # Calculate cosine similarity
                similarity = np.dot(query_vector, chunk_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(chunk_vector))
                
                # Convert to a distance (lower is better)
                distance = 1.0 - similarity
                
                chunk_id = chunk['id']
                document_id = chunk['document_id']
                
                # Parse metadata
                metadata = chunk.get('metadata', {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Use the document's title or metadata name
                doc_id = metadata.get('id', f"doc_{document_id}")
                
                results.append({
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'score': float(distance),
                    'chunk_text': chunk['chunk_text'],
                    'document_title': chunk['title'],
                    'document_path': chunk['file_path']
                })
            
            # Sort by score (lower is better) and get top_k
            results.sort(key=lambda x: x['score'])
            results = results[:top_k]
            
            # Add rank
            for i, result in enumerate(results):
                result['rank'] = i + 1
            
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
            conn = get_connection()
            stats = {}
            
            with conn.cursor() as cur:
                # Get document count
                cur.execute("SELECT COUNT(*) FROM documents")
                stats['documents_count'] = cur.fetchone()[0]
                
                # Get chunks count
                cur.execute("SELECT COUNT(*) FROM document_chunks")
                stats['chunks_count'] = cur.fetchone()[0]
                
                # Get total document size
                cur.execute("SELECT SUM(file_size) FROM documents WHERE file_size IS NOT NULL")
                total_size = cur.fetchone()[0]
                stats['total_size'] = total_size if total_size else 0
                
                # Get vector dimension
                stats['vector_dim'] = self.vector_dim
                
                # Get newest document
                cur.execute("""
                SELECT title, created_at FROM documents 
                ORDER BY created_at DESC LIMIT 1
                """)
                newest = cur.fetchone()
                if newest:
                    stats['newest_document'] = {
                        'title': newest[0],
                        'created_at': newest[1].isoformat() if newest[1] else None
                    }
                
                # Get document types
                cur.execute("""
                SELECT file_type, COUNT(*) as count 
                FROM documents 
                WHERE file_type IS NOT NULL 
                GROUP BY file_type
                """)
                stats['document_types'] = {row[0]: row[1] for row in cur.fetchall()}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting vector database stats: {str(e)}")
            return {'error': str(e), 'documents_count': 0, 'chunks_count': 0, 'vector_dim': self.vector_dim}
    
    def get_documents(self) -> Dict[str, Any]:
        """
        Get all documents in the vector database
        
        Returns:
            Dictionary of document metadata
        """
        try:
            conn = get_connection()
            documents = {}
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                SELECT id, title, description, file_path, file_type, file_size, 
                       source, source_url, created_at, metadata
                FROM documents
                """)
                
                rows = cur.fetchall()
                
                for row in rows:
                    # Extract metadata
                    metadata = row['metadata']
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}
                    
                    # Get the document ID from metadata or use the database ID
                    doc_id = metadata.get('id', f"doc_{row['id']}")
                    
                    # Create document entry
                    documents[doc_id] = {
                        'id': doc_id,
                        'name': row['title'],
                        'description': row['description'],
                        'file_path': row['file_path'],
                        'file_type': row['file_type'],
                        'file_size': row['file_size'],
                        'source': row['source'],
                        'source_url': row['source_url'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None
                    }
                    
                    # Add other metadata fields
                    if metadata:
                        for key, value in metadata.items():
                            if key not in documents[doc_id]:
                                documents[doc_id][key] = value
            
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
            conn = get_connection()
            with conn.cursor() as cur:
                # Delete all document chunks (cascade will handle dependencies)
                cur.execute("DELETE FROM document_chunks")
                
                # Delete all documents
                cur.execute("DELETE FROM documents")
                
                conn.commit()
                
            logger.info("Vector database reset")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting vector database: {str(e)}")
            if 'conn' in locals() and conn:
                conn.rollback()
            return False

# Create a singleton instance
postgres_vector_db_service = PostgresVectorDBService()