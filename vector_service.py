"""
FAISS Vector Service
This module provides interfaces for the FAISS vector database
"""
import os
import json
import logging
import numpy as np
import faiss
from typing import List, Dict, Tuple, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
FAISS_DIMENSION = int(os.environ.get('FAISS_DIMENSION', 384))
FAISS_INDEX_PATH = os.environ.get('FAISS_INDEX_PATH', 'data/faiss_index.bin')
FAISS_MAPPING_PATH = os.environ.get('FAISS_MAPPING_PATH', 'data/faiss_id_mapping.json')

class VectorService:
    """Service for vector operations using FAISS"""
    
    def __init__(self, dimension=FAISS_DIMENSION, index_path=None, mapping_path=None):
        """Initialize the vector service"""
        self.dimension = dimension
        self.index_path = index_path or FAISS_INDEX_PATH
        self.mapping_path = mapping_path or FAISS_MAPPING_PATH
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Initialize index and ID mapping
        self.index = None
        self.id_mapping = {}
        self._load_or_create_index()
        
        logger.info(f"FAISS initialized with dimension {self.dimension}")
    
    def _load_or_create_index(self):
        """Load an existing index or create a new one"""
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index from {self.index_path}")
            else:
                self._create_new_index()
                logger.info("Creating new FAISS index")
            
            self._load_id_mapping()
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self._create_new_index()
            self.id_mapping = {}
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Using IndexFlatL2 for simplicity and accuracy
        # In production, you might want to use a more efficient index type
        self.index = faiss.IndexFlatL2(self.dimension)
        self._save_index()
    
    def _load_id_mapping(self):
        """Load ID mapping from disk"""
        try:
            if os.path.exists(self.mapping_path):
                with open(self.mapping_path, 'r') as f:
                    self.id_mapping = json.load(f)
        except Exception as e:
            logger.error(f"Error loading ID mapping: {e}")
            self.id_mapping = {}
    
    def _save_id_mapping(self):
        """Save ID mapping to disk"""
        try:
            with open(self.mapping_path, 'w') as f:
                json.dump(self.id_mapping, f)
        except Exception as e:
            logger.error(f"Error saving ID mapping: {e}")
    
    def _save_index(self):
        """Save index to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def add_vectors(self, ids: List[str], vectors: List[List[float]]) -> bool:
        """
        Add vectors to the index
        
        Args:
            ids: List of external IDs (strings)
            vectors: List of vectors (each a list of floats)
            
        Returns:
            bool: Success status
        """
        try:
            if not ids or not vectors or len(ids) != len(vectors):
                logger.error(f"Invalid inputs: ids={len(ids) if ids else 0}, vectors={len(vectors) if vectors else 0}")
                return False
            
            # Convert vectors to numpy array
            vectors_np = np.array(vectors).astype('float32')
            
            # Get current maximum internal ID
            next_id = max(self.id_mapping.values()) + 1 if self.id_mapping else 0
            
            # Add vectors to index
            internal_ids = list(range(next_id, next_id + len(vectors_np)))
            
            # Map external IDs to internal IDs
            for i, ext_id in enumerate(ids):
                self.id_mapping[ext_id] = internal_ids[i]
            
            # Add to FAISS index
            self.index.add(vectors_np)
            
            # Save changes
            self._save_index()
            self._save_id_mapping()
            
            logger.info(f"Added {len(vectors)} vectors to index")
            return True
        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            return False
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector (list of floats)
            top_k: Number of results to return
            
        Returns:
            List of (ID, distance) tuples
        """
        try:
            # Convert to numpy array
            query_np = np.array([query_vector]).astype('float32')
            
            # Search index
            D, I = self.index.search(query_np, top_k)
            
            # Map internal IDs back to external IDs
            reverse_mapping = {v: k for k, v in self.id_mapping.items()}
            
            results = []
            for i in range(len(I[0])):
                internal_id = int(I[0][i])
                if internal_id in reverse_mapping:
                    results.append((reverse_mapping[internal_id], float(D[0][i])))
            
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """
        Delete vectors from the index
        Note: FAISS doesn't natively support removal, so we rebuild the index
        
        Args:
            ids: List of external IDs to remove
            
        Returns:
            bool: Success status
        """
        try:
            # For simplicity in implementation, we'll rebuild the index without the deleted vectors
            # This is inefficient for large indices but works for small to medium sized ones
            
            # Get internal IDs to remove
            internal_ids_to_remove = set()
            for ext_id in ids:
                if ext_id in self.id_mapping:
                    internal_ids_to_remove.add(self.id_mapping[ext_id])
                    del self.id_mapping[ext_id]
            
            if not internal_ids_to_remove:
                logger.warning("No valid IDs to remove")
                return False
            
            # If we have vectors to keep, rebuild the index
            if self.id_mapping:
                # Create a new index
                new_index = faiss.IndexFlatL2(self.dimension)
                
                # Get all vectors we want to keep
                reverse_mapping = {v: k for k, v in self.id_mapping.items()}
                remaining_internal_ids = sorted(list(reverse_mapping.keys()))
                
                # This approach only works if we can reconstruct vectors
                if hasattr(self.index, 'reconstruct'):
                    # Reconstruct vectors for remaining IDs
                    vectors_to_keep = []
                    for idx in remaining_internal_ids:
                        vector = self.index.reconstruct(int(idx))
                        vectors_to_keep.append(vector)
                    
                    # Add vectors to the new index
                    vectors_np = np.array(vectors_to_keep).astype('float32')
                    new_index.add(vectors_np)
                    
                    # Update ID mapping to use consecutive indices
                    new_mapping = {}
                    for i, internal_id in enumerate(remaining_internal_ids):
                        ext_id = reverse_mapping[internal_id]
                        new_mapping[ext_id] = i
                    
                    self.id_mapping = new_mapping
                    self.index = new_index
                    
                    # Save changes
                    self._save_index()
                    self._save_id_mapping()
                    
                    logger.info(f"Removed {len(internal_ids_to_remove)} vectors from index")
                    return True
                else:
                    logger.error("Index doesn't support vector reconstruction, cannot remove vectors")
                    return False
            else:
                # If no vectors left, create a new empty index
                self._create_new_index()
                self._save_id_mapping()
                logger.info("Removed all vectors from index")
                return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get stats about the vector index
        
        Returns:
            Dict with vector database statistics
        """
        try:
            # Get index size
            index_size_bytes = os.path.getsize(self.index_path) if os.path.exists(self.index_path) else 0
            
            # Format size for display
            if index_size_bytes < 1024:
                index_size = f"{index_size_bytes} B"
            elif index_size_bytes < 1024 * 1024:
                index_size = f"{index_size_bytes / 1024:.1f} KB"
            elif index_size_bytes < 1024 * 1024 * 1024:
                index_size = f"{index_size_bytes / (1024 * 1024):.1f} MB"
            else:
                index_size = f"{index_size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
            # Get number of vectors
            total_vectors = len(self.id_mapping)
            
            # Get index type
            index_type = type(self.index).__name__ if self.index else "Unknown"
            
            return {
                "index_type": index_type,
                "vector_dimension": self.dimension,
                "total_vectors": total_vectors,
                "index_size": index_size,
                "index_size_bytes": index_size_bytes
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "error": str(e),
                "index_type": "Error",
                "vector_dimension": self.dimension,
                "total_vectors": 0,
                "index_size": "0 B",
                "index_size_bytes": 0
            }

# Singleton instance for the application
_vector_service = None

def get_vector_service() -> VectorService:
    """Get or create a vector service instance"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service

def get_stats() -> Dict[str, Any]:
    """Get vector database statistics"""
    return get_vector_service().get_stats()

def generate_embedding(text: str) -> List[float]:
    """
    Generate a mock embedding for text content
    
    This is a temporary implementation that creates random embeddings of the correct 
    dimension. In a production environment, you would replace this with a proper 
    embedding model like SentenceTransformers, OpenAI embeddings, etc.
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        A list of floats representing the embedding vector
    """
    dimension = FAISS_DIMENSION
    
    # Create a deterministic embedding based on the text hash
    # This ensures the same text always gets the same embedding
    import hashlib
    import numpy as np
    
    # Create a hash of the text
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    
    # Use the hash to seed the random number generator
    hash_value = int(text_hash, 16) % (2**32)
    np.random.seed(hash_value)
    
    # Generate a random vector
    vector = np.random.randn(dimension).astype(np.float32)
    
    # Normalize to unit length (cosine similarity)
    vector = vector / np.linalg.norm(vector)
    
    return vector.tolist()

# For testing
if __name__ == "__main__":
    # Create vector service
    service = VectorService()
    
    # Generate some random vectors
    dimension = service.dimension
    num_vectors = 5
    
    vectors = []
    for _ in range(num_vectors):
        vector = np.random.rand(dimension).tolist()
        vectors.append(vector)
    
    # Add vectors
    ids = [f"test-{i}" for i in range(num_vectors)]
    service.add_vectors(ids, vectors)
    
    # Search similar vectors
    query = vectors[0]
    results = service.search(query, 3)
    
    print(f"\nSearch results for vector {ids[0]}:")
    for idx, (id_, distance) in enumerate(results):
        print(f"  {idx+1}. ID: {id_}, Distance: {distance:.4f}")
    
    # Get stats
    stats = service.get_stats()
    print("\nVector database stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")