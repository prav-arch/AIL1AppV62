"""
Vector Database Service using FAISS

This module provides functionality for working with FAISS vector database:
1. Creating and managing a FAISS index
2. Converting documents to embeddings
3. Adding documents to the vector database
4. Searching the vector database
"""

import os
import json
import time
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

# Try to import FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS is not available. Vector search functionality will be limited.")
    FAISS_AVAILABLE = False

class VectorDBService:
    """Service for managing vector database operations"""
    
    def __init__(self, vector_dim: int = 384, index_dir: str = 'data/vector_db'):
        """
        Initialize the vector database service
        
        Args:
            vector_dim: Dimension of the vectors
            index_dir: Directory to store the index and metadata
        """
        self.vector_dim = vector_dim
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, 'faiss_index.bin')
        self.metadata_path = os.path.join(index_dir, 'metadata.json')
        self.documents_path = os.path.join(index_dir, 'documents.json')
        
        # Create index directory if it doesn't exist
        os.makedirs(index_dir, exist_ok=True)
        
        # Initialize FAISS index
        if FAISS_AVAILABLE:
            if os.path.exists(self.index_path):
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
            else:
                logger.info(f"Creating new FAISS index with dimension {vector_dim}")
                self.index = faiss.IndexFlatL2(vector_dim)  # L2 distance
        else:
            self.index = None
            
        # Load or initialize metadata
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'documents_count': 0,
                'chunks_count': 0,
                'vector_dim': vector_dim,
                'index_type': 'FlatL2' if FAISS_AVAILABLE else 'None'
            }
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
                
        # Load or initialize documents
        if os.path.exists(self.documents_path):
            with open(self.documents_path, 'r') as f:
                self.documents = json.load(f)
        else:
            self.documents = {}
            with open(self.documents_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
    
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
    
    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a document to the vector database
        
        Args:
            doc_id: Unique identifier for the document
            text: Document text
            metadata: Additional metadata about the document
            
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS is not available. Cannot add document to vector database.")
            return False
        
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
            
            # Store document metadata
            self.documents[doc_id] = metadata
            
            # Process each chunk
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                vector = self._generate_embeddings(chunk)
                
                # Add to FAISS index
                self.index.add(np.array([vector]))
                
                # Add chunk ID to the list
                chunk_ids.append(chunk_id)
            
            # Update document metadata with chunk IDs
            self.documents[doc_id]['chunk_ids'] = chunk_ids
            
            # Update global metadata
            self.metadata['documents_count'] = len(self.documents)
            self.metadata['chunks_count'] += len(chunks)
            self.metadata['last_modified'] = datetime.now().isoformat()
            
            # Save metadata and documents
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            with open(self.documents_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
                
            # Save the FAISS index
            faiss.write_index(self.index, self.index_path)
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks to the vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector database: {str(e)}")
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
        if not FAISS_AVAILABLE:
            logger.error("FAISS is not available. Cannot search vector database.")
            return []
        
        try:
            # Generate query embedding
            query_vector = self._generate_embeddings(query)
            
            # Search the FAISS index
            scores, indices = self.index.search(np.array([query_vector]), top_k)
            
            # Format results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                # In a real implementation, you would convert the index to a document ID
                # Here we just use a mock implementation
                doc_id = list(self.documents.keys())[idx % len(self.documents)] if self.documents else f"doc_{idx}"
                
                results.append({
                    'score': float(score),
                    'document_id': doc_id,
                    'rank': i + 1
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
        return self.metadata
    
    def get_documents(self) -> Dict[str, Any]:
        """
        Get all documents in the vector database
        
        Returns:
            Dictionary of document metadata
        """
        return self.documents
    
    def reset(self) -> bool:
        """
        Reset the vector database, removing all documents
        
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS is not available. Cannot reset vector database.")
            return False
        
        try:
            # Create a new FAISS index
            self.index = faiss.IndexFlatL2(self.vector_dim)
            
            # Reset metadata
            self.metadata = {
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'documents_count': 0,
                'chunks_count': 0,
                'vector_dim': self.vector_dim,
                'index_type': 'FlatL2' if FAISS_AVAILABLE else 'None'
            }
            
            # Reset documents
            self.documents = {}
            
            # Save metadata and documents
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            with open(self.documents_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
                
            # Save the FAISS index
            faiss.write_index(self.index, self.index_path)
            
            logger.info("Reset vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting vector database: {str(e)}")
            return False

# Create a singleton instance
vector_db_service = VectorDBService()