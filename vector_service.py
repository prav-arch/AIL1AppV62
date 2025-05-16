"""
Vector service using FAISS for the GPU server environment
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaissVectorService:
    """Vector service for embedding storage and retrieval using FAISS"""
    
    def __init__(self, dimension=384, index_path=None):
        """Initialize the FAISS vector service"""
        try:
            import faiss
            self.faiss = faiss
            self.dimension = dimension
            self.index_path = index_path or 'data/faiss_index.bin'
            self.id_mapping_path = 'data/id_mapping.json'
            
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
        if not ids or not vectors or len(ids) != len(vectors):
            logger.warning("Invalid IDs or vectors")
            return
        
        # Convert vectors to numpy array
        vectors_array = np.array(vectors).astype('float32')
        
        # Add to index
        self.index.add(vectors_array)
        
        # Update ID mapping
        base_index = len(self.id_map)
        for i, id_val in enumerate(ids):
            self.id_map[str(base_index + i)] = str(id_val)
        
        # Save index
        self._save_index()
        
        logger.info(f"Added {len(ids)} vectors to FAISS index")
    
    def search(self, query_vector, top_k=5):
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector (numpy array)
            top_k: Number of results to return
            
        Returns:
            List of (ID, distance) tuples
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty, no results to return")
            return []
        
        # Convert query to numpy array
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector).astype('float32')
        
        # Reshape if needed
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search index
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        # Map indices to original IDs
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # -1 indicates no result
                results.append((self.id_map.get(str(idx)), float(distances[0][i])))
        
        return results
    
    def get_stats(self):
        """Get stats about the vector index"""
        return {
            'vector_count': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__,
            'id_mapping_count': len(self.id_map)
        }
    
    def generate_embedding(self, text):
        """
        Generate an embedding for the given text
        
        This is a simplified random embedding for demonstration purposes.
        In a real application, you would use a proper embedding model.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector (numpy array)
        """
        # Use the hash of the text to seed the random generator
        np.random.seed(hash(text) % 2**32)
        
        # Generate a random vector
        vector = np.random.rand(self.dimension).astype(np.float32)
        
        # Normalize to unit length (important for similarity search)
        vector = vector / np.linalg.norm(vector)
        
        return vector

# Example usage
if __name__ == "__main__":
    # Create the vector service
    vector_service = FaissVectorService()
    
    # Generate embeddings for a few texts
    texts = [
        "This is a sample text for embedding generation",
        "Another example of text that will be converted to a vector",
        "The quick brown fox jumps over the lazy dog"
    ]
    
    ids = [f"text_{i+1}" for i in range(len(texts))]
    embeddings = [vector_service.generate_embedding(text) for text in texts]
    
    # Add vectors to the index
    vector_service.add_vectors(ids, embeddings)
    
    # Search for similar vectors
    query = "Example text for searching"
    query_embedding = vector_service.generate_embedding(query)
    
    results = vector_service.search(query_embedding, top_k=2)
    
    print(f"Query: {query}")
    print(f"Results: {results}")
    
    # Get stats
    stats = vector_service.get_stats()
    print(f"Stats: {stats}")