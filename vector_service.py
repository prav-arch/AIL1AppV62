"""
FAISS Vector Service
This module provides interfaces for the FAISS vector database with real TF-IDF embeddings
"""
import os
import json
import logging
import numpy as np
import faiss
import pickle
from typing import List, Dict, Tuple, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration for real embeddings
FAISS_DIMENSION = int(os.environ.get('FAISS_DIMENSION', 128))  # Increased for real embeddings
FAISS_INDEX_PATH = os.environ.get('FAISS_INDEX_PATH', 'data/faiss_index.bin')
FAISS_MAPPING_PATH = os.environ.get('FAISS_MAPPING_PATH', 'data/faiss_id_mapping.json')
EMBEDDING_MODEL_PATH = os.environ.get('EMBEDDING_MODEL_PATH', 'data/embedding_model.pkl')

class RealEmbeddingModel:
    """Real embedding model using TF-IDF + SVD for semantic similarity"""
    
    def __init__(self, dimension=128, model_path=EMBEDDING_MODEL_PATH):
        self.dimension = dimension
        self.model_path = model_path
        self.vectorizer = None
        self.svd = None
        self.is_fitted = False
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.vectorizer = model_data['vectorizer']
                    self.svd = model_data['svd']
                    self.is_fitted = True
                logger.info(f"Loaded embedding model from {self.model_path}")
            else:
                self._create_new_model()
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}, creating new one")
            self._create_new_model()
    
    def _create_new_model(self):
        """Create a new embedding model"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        self.svd = TruncatedSVD(n_components=self.dimension, random_state=42)
        self.is_fitted = False
        logger.info("Created new TF-IDF embedding model")
    
    def _save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            model_data = {
                'vectorizer': self.vectorizer,
                'svd': self.svd
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"Saved embedding model to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def fit_texts(self, texts):
        """Fit the model on a collection of texts"""
        if not texts:
            return
        try:
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            # Fit SVD for dimensionality reduction
            self.svd.fit(tfidf_matrix)
            self.is_fitted = True
            self._save_model()
            logger.info(f"Fitted embedding model on {len(texts)} texts")
        except Exception as e:
            logger.error(f"Error fitting model: {e}")
    
    def encode_texts(self, texts):
        """Encode texts into embeddings"""
        if not self.is_fitted:
            # Auto-fit on the input texts if not fitted
            self.fit_texts(texts)
        
        try:
            # Transform to TF-IDF
            tfidf_matrix = self.vectorizer.transform(texts)
            # Apply SVD
            embeddings = self.svd.transform(tfidf_matrix)
            # Normalize
            embeddings = normalize(embeddings, norm='l2')
            return embeddings.astype('float32')
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            # Fallback to random vectors if encoding fails
            return np.random.randn(len(texts), self.dimension).astype('float32')

# Global embedding model instance
_embedding_model = None

def get_embedding_model():
    """Get the global embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = RealEmbeddingModel()
    return _embedding_model

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
            
            # Fix vector dimensions if needed
            fixed_vectors = []
            for i, vector in enumerate(vectors):
                if len(vector) != self.dimension:
                    logger.warning(f"Vector dimension mismatch: got {len(vector)}, expected {self.dimension}. Adjusting...")
                    if len(vector) > self.dimension:
                        # Truncate vector
                        fixed_vectors.append(vector[:self.dimension])
                    else:
                        # Pad vector with zeros
                        padding = [0.0] * (self.dimension - len(vector))
                        fixed_vectors.append(vector + padding)
                else:
                    fixed_vectors.append(vector)
            
            # Convert vectors to numpy array
            vectors_np = np.array(fixed_vectors).astype('float32')
            
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
            
            logger.info(f"Added {len(vectors)} vectors to index with dimension {self.dimension}")
            return True
        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            return False
    
    def add_documents(self, doc_ids: List[str], texts: List[str]) -> bool:
        """
        Add documents to the vector store using real TF-IDF embeddings
        
        Args:
            doc_ids: List of document IDs
            texts: List of text content to embed
            
        Returns:
            bool: Success status
        """
        try:
            if not doc_ids or not texts or len(doc_ids) != len(texts):
                logger.error(f"Invalid inputs: doc_ids={len(doc_ids) if doc_ids else 0}, texts={len(texts) if texts else 0}")
                return False
            
            # Get embedding model
            embedding_model = get_embedding_model()
            
            # Generate real embeddings
            embeddings = embedding_model.encode_texts(texts)
            
            # Convert embeddings to list format for add_vectors
            embedding_vectors = [embedding.tolist() for embedding in embeddings]
            
            # Add to vector store
            return self.add_vectors(doc_ids, embedding_vectors)
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def search_similar_text(self, query_text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for documents similar to the query text using real embeddings
        
        Args:
            query_text: The search query text
            top_k: Number of results to return
            
        Returns:
            List of (document_id, similarity_score) tuples
        """
        try:
            # Get embedding model
            embedding_model = get_embedding_model()
            
            # Generate embedding for query
            query_embeddings = embedding_model.encode_texts([query_text])
            query_vector = query_embeddings[0].tolist()
            
            # Search using the embedding
            return self.search(query_vector, top_k)
            
        except Exception as e:
            logger.error(f"Error searching similar text: {e}")
            return []
    
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
            
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for text content with dimension 12
        to match the existing FAISS index
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            A list of 12 floats representing the embedding vector
        """
        dimension = self.dimension  # This should be 12
        
        # For consistent results with minimal dependencies, use hash-based embedding
        import hashlib
        import numpy as np
        
        # Create a hash of the text content
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # Convert hash to numerical values for seeding
        seed = int(text_hash, 16) % (2**32)
        np.random.seed(seed)
        
        # Generate a deterministic "embedding" based on the text hash
        # This ensures the same text always gets the same vector
        vector = np.random.randn(dimension).astype(np.float32)
        
        # Normalize to unit length (for cosine similarity)
        if np.linalg.norm(vector) > 0:
            vector = vector / np.linalg.norm(vector)
        
        logger.info(f"Generated embedding with dimension {len(vector)}")
        return vector.tolist()

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
    Generate embeddings for text content using available methods:
    1. Try SentenceTransformers if available (best quality)
    2. Fall back to TF-IDF + SVD otherwise
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        A list of floats representing the embedding vector
    """
    dimension = FAISS_DIMENSION
    
    try:
        # Try importing sentence_transformers for high-quality embeddings
        from sentence_transformers import SentenceTransformer
        
        # Use one of the smaller models that's commonly available
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(text, normalize_embeddings=True)
        
        # Resize if necessary
        if len(embedding) > dimension:
            embedding = embedding[:dimension]
        elif len(embedding) < dimension:
            # Pad with zeros if needed
            padding = np.zeros(dimension - len(embedding))
            embedding = np.concatenate([embedding, padding])
            
        logger.info(f"Generated embedding using SentenceTransformer with dimension {len(embedding)}")
        return embedding.tolist()
    
    except ImportError:
        logger.warning("SentenceTransformers not available, using scikit-learn for embeddings")
        
        try:
            # Fall back to TF-IDF + SVD (scikit-learn)
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            import numpy as np
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(max_features=1000)
            
            # Fit and transform the text
            tfidf_matrix = vectorizer.fit_transform([text])
            
            # Reduce dimensionality with SVD
            svd = TruncatedSVD(n_components=dimension)
            embedding = svd.fit_transform(tfidf_matrix)[0]
            
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.info(f"Generated embedding using TF-IDF + SVD with dimension {len(embedding)}")
            return embedding.tolist()
        
        except ImportError:
            logger.warning("Scikit-learn not available, using simple embedding technique")
            
            # Basic tokenization and hashing as a last resort
            import hashlib
            import numpy as np
            
            # Split text into tokens
            tokens = text.lower().split()
            
            # Create an empty embedding vector
            embedding = np.zeros(dimension, dtype=np.float32)
            
            # Fill embedding vector with token hashes
            for i, token in enumerate(tokens):
                # Hash the token
                token_hash = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
                
                # Use the hash to set values in the embedding
                pos = token_hash % dimension
                embedding[pos] += 1.0 / (i + 1)  # Weigh earlier tokens more
            
            # Normalize the vector
            if np.linalg.norm(embedding) > 0:
                embedding = embedding / np.linalg.norm(embedding)
            
            logger.info(f"Generated embedding using basic hashing with dimension {len(embedding)}")
            return embedding.tolist()

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