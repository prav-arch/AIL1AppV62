"""
Vector Database Service for ClickHouse

This module provides a mock implementation that mimics the original vector database service,
but doesn't actually connect to PostgreSQL. This makes the application compatible with
ClickHouse-only environments.
"""

import os
import json
import time
import logging
import random
import uuid
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

class PgVectorDBService:
    """Mock service for vector database operations"""
    
    def __init__(self, vector_dim: int = 384):
        """
        Initialize the vector database service
        
        Args:
            vector_dim: Dimension of the vectors
        """
        self.vector_dim = vector_dim
        self.documents = {}
        self.chunks = {}
        self.stats = {
            'documents_count': 0,
            'chunks_count': 0,
            'vector_dim': vector_dim,
            'last_modified': datetime.now().isoformat()
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
        
        logger.info(f"Initialized mock vector database service with dimension {vector_dim}")
            
    def _initialize_sample_data(self):
        """Initialize with sample data for development"""
        # Sample document 1
        doc_id1 = str(uuid.uuid4())
        self.documents[doc_id1] = {
            'id': doc_id1,
            'name': 'Network Security Guide.pdf',
            'description': 'A comprehensive guide to network security best practices',
            'metadata': {'category': 'Security', 'format': 'PDF'},
            'file_path': '/data/documents/network_security_guide.pdf',
            'created_at': datetime.now().isoformat()
        }
        
        # Sample document 2
        doc_id2 = str(uuid.uuid4())
        self.documents[doc_id2] = {
            'id': doc_id2,
            'name': 'Machine Learning Tutorial.docx',
            'description': 'Introduction to machine learning concepts and techniques',
            'metadata': {'category': 'AI', 'format': 'DOCX'},
            'file_path': '/data/documents/ml_tutorial.docx',
            'created_at': datetime.now().isoformat()
        }
        
        # Add sample chunks for document 1
        for i in range(3):
            chunk_id = len(self.chunks) + 1
            self.chunks[chunk_id] = {
                'id': chunk_id,
                'document_id': doc_id1,
                'chunk_text': f'Sample network security content {i+1}. This section covers firewalls and VPNs.',
                'chunk_index': i,
                'metadata': {'page': i+1},
                'created_at': datetime.now().isoformat()
            }
        
        # Add sample chunks for document 2
        for i in range(5):
            chunk_id = len(self.chunks) + 1
            self.chunks[chunk_id] = {
                'id': chunk_id,
                'document_id': doc_id2,
                'chunk_text': f'Sample machine learning content {i+1}. This section covers neural networks.',
                'chunk_index': i,
                'metadata': {'page': i+1},
                'created_at': datetime.now().isoformat()
            }
        
        # Update stats
        self.stats['documents_count'] = len(self.documents)
        self.stats['chunks_count'] = len(self.chunks)
        self.stats['last_modified'] = datetime.now().isoformat()
        
        logger.info(f"Initialized with {len(self.documents)} sample documents and {len(self.chunks)} sample chunks")
    
    def add_document(self, name: str, description: str, metadata: Dict = None, file_path: str = None) -> str:
        """
        Add a document to the database
        
        Args:
            name: Document name
            description: Document description
            metadata: Additional metadata
            file_path: Path to the document file
            
        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())
        
        self.documents[doc_id] = {
            'id': doc_id,
            'name': name,
            'description': description,
            'metadata': metadata or {},
            'file_path': file_path,
            'created_at': datetime.now().isoformat()
        }
        
        # Update stats
        self.stats['documents_count'] += 1
        self.stats['last_modified'] = datetime.now().isoformat()
        
        logger.info(f"Added document with ID: {doc_id}")
        return doc_id
    
    def add_chunks(self, document_id: str, chunks: List[str], embeddings: List[List[float]] = None, 
                  metadata: List[Dict] = None) -> List[int]:
        """
        Add document chunks to the database
        
        Args:
            document_id: Document ID
            chunks: List of text chunks
            embeddings: List of embedding vectors (optional)
            metadata: List of metadata dictionaries (optional)
            
        Returns:
            List of chunk IDs
        """
        if document_id not in self.documents:
            logger.warning(f"Document {document_id} not found")
            return []
            
        if not chunks:
            logger.warning("No chunks provided to add_chunks")
            return []
        
        # Delete existing chunks for this document
        existing_chunks = [c_id for c_id, chunk in self.chunks.items() 
                           if chunk['document_id'] == document_id]
        for c_id in existing_chunks:
            del self.chunks[c_id]
        
        # Add new chunks
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = len(self.chunks) + 1
            
            # Use provided metadata if available, otherwise use empty dict
            chunk_metadata = metadata[i] if metadata and i < len(metadata) else {}
            
            self.chunks[chunk_id] = {
                'id': chunk_id,
                'document_id': document_id,
                'chunk_text': chunk,
                'chunk_index': i,
                'metadata': chunk_metadata,
                'created_at': datetime.now().isoformat()
            }
            
            chunk_ids.append(chunk_id)
        
        # Update stats
        self.stats['chunks_count'] = len(self.chunks)
        self.stats['last_modified'] = datetime.now().isoformat()
        
        logger.info(f"Added {len(chunks)} chunks for document {document_id}")
        return chunk_ids
    
    def search(self, query: str, query_embedding: List[float] = None, top_k: int = 5) -> List[Dict]:
        """
        Search for similar document chunks

        Args:
            query: Query text
            query_embedding: Query embedding vector (optional)
            top_k: Number of results to return
            
        Returns:
            List of search results containing document_id, chunk_id, score, and metadata
        """
        # For the mock implementation, just return random chunks
        if not self.chunks:
            logger.warning("No document chunks found")
            return []
        
        # Get all chunks as a list
        all_chunks = list(self.chunks.values())
        
        # Select random chunks (or all if fewer than top_k)
        selected_count = min(top_k, len(all_chunks))
        selected_chunks = random.sample(all_chunks, selected_count)
        
        results = []
        for chunk in selected_chunks:
            document = self.documents.get(chunk['document_id'], {})
            
            results.append({
                'chunk_id': chunk['id'],
                'document_id': chunk['document_id'],
                'chunk_text': chunk['chunk_text'],
                'score': random.uniform(0.1, 0.9),  # Random similarity score
                'metadata': chunk.get('metadata', {}),
                'document_name': document.get('name', ''),
                'document_metadata': document.get('metadata', {})
            })
        
        # Sort by score (ascending - lower is better in vector similarity)
        results.sort(key=lambda x: x['score'])
        
        return results
    
    def get_document(self, document_id: str) -> Dict:
        """
        Get a document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data
        """
        return self.documents.get(document_id)
    
    def get_documents(self) -> Dict[str, Dict]:
        """
        Get all documents
        
        Returns:
            Dictionary of document data keyed by document ID
        """
        return self.documents
    
    def get_chunks(self, document_id: str) -> List[Dict]:
        """
        Get chunks for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of chunks
        """
        return [chunk for chunk_id, chunk in self.chunks.items() 
                if chunk['document_id'] == document_id]
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and its chunks
        
        Args:
            document_id: Document ID
            
        Returns:
            Success flag
        """
        if document_id not in self.documents:
            logger.warning(f"Document {document_id} not found for deletion")
            return False
        
        # Delete document
        del self.documents[document_id]
        
        # Delete associated chunks
        chunk_ids = [c_id for c_id, chunk in self.chunks.items() 
                     if chunk['document_id'] == document_id]
        
        for c_id in chunk_ids:
            del self.chunks[c_id]
        
        # Update stats
        self.stats['documents_count'] = len(self.documents)
        self.stats['chunks_count'] = len(self.chunks)
        self.stats['last_modified'] = datetime.now().isoformat()
        
        logger.info(f"Deleted document {document_id} with {len(chunk_ids)} chunks")
        return True
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Statistics data
        """
        return self.stats

# Create a singleton instance
pg_vector_db_service = PgVectorDBService()