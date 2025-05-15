"""
PostgreSQL pgvector database service for vector embeddings storage and retrieval

This module replaces FAISS with pgvector for managing vector embeddings. 
It provides similar functionality but stores embeddings in PostgreSQL.
"""

import os
import json
import logging
import numpy as np
import psycopg2
from psycopg2.extras import execute_values, Json
from typing import List, Dict, Any, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    """
    Get a connection to the PostgreSQL database
    
    Returns:
        connection: psycopg2 connection object
    """
    db_params = {
        'dbname': os.environ.get('PGDATABASE', 'l1_app_db'),
        'user': os.environ.get('PGUSER', 'l1_app_user'),
        'password': os.environ.get('PGPASSWORD', 'l1'),
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5433'),
    }
    
    try:
        # Using keyword arguments explicitly to avoid type errors
        connection = psycopg2.connect(
            dbname=db_params['dbname'],
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port']
        )
        return connection
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None

def init_vector_db():
    """
    Initialize the pgvector database, creating extension and tables if needed
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database to initialize pgvector")
            return False
        
        cursor = conn.cursor()
        
        # Check if vector extension is installed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');")
        vector_exists = cursor.fetchone()[0]
        
        if not vector_exists:
            logger.info("Installing vector extension...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Check if embeddings table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'document_embeddings'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.info("Creating document_embeddings table...")
            cursor.execute("""
                CREATE TABLE document_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    embedding vector(1536) NOT NULL,
                    text TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS document_embeddings_idx 
                ON document_embeddings USING ivfflat (embedding vector_cosine_ops) 
                WITH (lists = 100);
            """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Vector database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}")
        if conn:
            conn.close()
        return False

def add_embedding(document_id: str, chunk_id: int, embedding_vector: np.ndarray, text: str, metadata: Dict = None) -> bool:
    """
    Add a document embedding to pgvector
    
    Args:
        document_id: ID of the document
        chunk_id: Chunk index within the document
        embedding_vector: Embedding vector as numpy array
        text: Text content of the chunk
        metadata: Additional metadata
        
    Returns:
        bool: True if successfully added, False otherwise
    """
    conn = None
    try:
        # Convert numpy array to list format for pgvector
        if isinstance(embedding_vector, np.ndarray):
            embedding_list = embedding_vector.tolist()
        else:
            embedding_list = embedding_vector
            
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database to add embedding")
            return False
            
        cursor = conn.cursor()
        
        # Insert embedding
        cursor.execute("""
            INSERT INTO document_embeddings(document_id, chunk_id, embedding, text, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (document_id, chunk_id, embedding_list, text, Json(metadata) if metadata else None))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Added embedding for document {document_id}, chunk {chunk_id}, with ID {new_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding embedding to database: {e}")
        if conn:
            conn.close()
        return False

def batch_add_embeddings(embeddings_data: List[Dict[str, Any]]) -> bool:
    """
    Add multiple embeddings at once for better performance
    
    Args:
        embeddings_data: List of dicts with keys: document_id, chunk_id, embedding, text, metadata
        
    Returns:
        bool: True if successfully added, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database for batch embedding insert")
            return False
            
        cursor = conn.cursor()
        
        # Prepare data for batch insert
        values = []
        for item in embeddings_data:
            # Convert numpy array to list format for pgvector
            if isinstance(item['embedding'], np.ndarray):
                embedding_list = item['embedding'].tolist()
            else:
                embedding_list = item['embedding']
                
            values.append((
                item['document_id'],
                item['chunk_id'],
                embedding_list,
                item['text'],
                Json(item['metadata']) if 'metadata' in item and item['metadata'] else None
            ))
        
        # Execute batch insert
        execute_values(
            cursor,
            """
            INSERT INTO document_embeddings(document_id, chunk_id, embedding, text, metadata)
            VALUES %s
            """,
            values
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Added {len(values)} embeddings in batch")
        return True
        
    except Exception as e:
        logger.error(f"Error batch adding embeddings to database: {e}")
        if conn:
            conn.close()
        return False

def search_embeddings(query_embedding: np.ndarray, limit: int = 5, filter_criteria: Dict = None) -> List[Dict]:
    """
    Search for similar embeddings using cosine similarity
    
    Args:
        query_embedding: Query embedding vector as numpy array
        limit: Maximum number of results to return
        filter_criteria: Optional filter criteria (e.g., document_id)
        
    Returns:
        List of dicts with search results, each containing:
            document_id, chunk_id, similarity, text, metadata
    """
    try:
        # Convert numpy array to list format for pgvector
        if isinstance(query_embedding, np.ndarray):
            query_vector = query_embedding.tolist()
        else:
            query_vector = query_embedding
            
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database for vector search")
            return []
            
        cursor = conn.cursor()
        
        # Build the query
        query = """
            SELECT 
                document_id, 
                chunk_id, 
                1 - (embedding <=> %s) as similarity, 
                text, 
                metadata 
            FROM document_embeddings
        """
        
        params = [query_vector]
        
        # Add filter criteria if provided
        if filter_criteria:
            conditions = []
            for key, value in filter_criteria.items():
                if key == 'document_id':
                    conditions.append("document_id = %s")
                    params.append(value)
                elif key == 'metadata' and isinstance(value, dict):
                    for meta_key, meta_value in value.items():
                        conditions.append(f"metadata->>'{meta_key}' = %s")
                        params.append(str(meta_value))
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # Add ordering and limit
        query += """
            ORDER BY similarity DESC
            LIMIT %s
        """
        params.append(limit)
        
        # Execute the query
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Format the results
        formatted_results = []
        for row in results:
            document_id, chunk_id, similarity, text, metadata = row
            formatted_results.append({
                'document_id': document_id,
                'chunk_id': chunk_id,
                'similarity': float(similarity),
                'text': text,
                'metadata': metadata
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Found {len(formatted_results)} similar embeddings")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching embeddings in database: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return []

def delete_embeddings(document_id: str = None, ids: List[int] = None) -> bool:
    """
    Delete embeddings from the database
    
    Args:
        document_id: Optional document ID to delete all chunks for a document
        ids: Optional list of specific embedding IDs to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not document_id and not ids:
        logger.error("Must provide either document_id or ids to delete embeddings")
        return False
        
    try:
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database to delete embeddings")
            return False
            
        cursor = conn.cursor()
        
        if document_id:
            cursor.execute("DELETE FROM document_embeddings WHERE document_id = %s", (document_id,))
            logger.info(f"Deleted all embeddings for document {document_id}")
        elif ids:
            cursor.execute("DELETE FROM document_embeddings WHERE id = ANY(%s)", (ids,))
            logger.info(f"Deleted embeddings with IDs: {ids}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error deleting embeddings from database: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return False

def get_document_embeddings(document_id: str) -> List[Dict]:
    """
    Get all embeddings for a specific document
    
    Args:
        document_id: Document ID to retrieve embeddings for
        
    Returns:
        List of embedding dictionaries
    """
    try:
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database to get embeddings")
            return []
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, document_id, chunk_id, text, metadata
            FROM document_embeddings
            WHERE document_id = %s
            ORDER BY chunk_id
        """, (document_id,))
        
        results = cursor.fetchall()
        
        formatted_results = []
        for row in results:
            id, doc_id, chunk_id, text, metadata = row
            formatted_results.append({
                'id': id,
                'document_id': doc_id,
                'chunk_id': chunk_id,
                'text': text,
                'metadata': metadata
            })
        
        cursor.close()
        conn.close()
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error retrieving embeddings from database: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return []

def count_embeddings() -> int:
    """
    Count total number of embeddings in the database
    
    Returns:
        int: Total count of embeddings
    """
    try:
        conn = get_connection()
        if not conn:
            logger.error("Failed to connect to database to count embeddings")
            return 0
            
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM document_embeddings")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count
        
    except Exception as e:
        logger.error(f"Error counting embeddings in database: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return 0

# Initialize the database when module is imported
if __name__ != "__main__":
    init_vector_db()