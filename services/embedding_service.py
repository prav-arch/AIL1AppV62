"""
Real Embedding Service for RAG
This module provides a TF-IDF based embedding service that creates meaningful vector representations
of text for semantic similarity search.
"""
import numpy as np
import pickle
import os
import logging
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating real text embeddings using TF-IDF + SVD"""
    
    def __init__(self, dimension: int = 128, model_path: str = "data/embedding_model.pkl"):
        """Initialize the embedding service"""
        self.dimension = dimension
        self.model_path = model_path
        self.vectorizer = None
        self.svd = None
        self.is_fitted = False
        
        # Try to load existing model
        self._load_model()
        
        # If no model exists, initialize new one
        if not self.is_fitted:
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            self.svd = TruncatedSVD(n_components=self.dimension, random_state=42)
            logger.info("Initialized new embedding model")
    
    def _load_model(self):
        """Load pre-trained model if available"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.vectorizer = model_data['vectorizer']
                    self.svd = model_data['svd']
                    self.dimension = model_data['dimension']
                    self.is_fitted = True
                logger.info(f"Loaded embedding model from {self.model_path}")
            else:
                logger.info("No existing embedding model found")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.is_fitted = False
    
    def _save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            model_data = {
                'vectorizer': self.vectorizer,
                'svd': self.svd,
                'dimension': self.dimension
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"Saved embedding model to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving embedding model: {e}")
    
    def fit(self, texts: List[str]):
        """Fit the embedding model on a collection of texts"""
        if not texts:
            logger.warning("No texts provided for fitting")
            return
        
        try:
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            logger.info(f"Fitted TF-IDF vectorizer on {len(texts)} texts")
            
            # Fit SVD for dimensionality reduction
            self.svd.fit(tfidf_matrix)
            logger.info(f"Fitted SVD with {self.dimension} dimensions")
            
            self.is_fitted = True
            self._save_model()
            
        except Exception as e:
            logger.error(f"Error fitting embedding model: {e}")
            raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into embeddings"""
        if not self.is_fitted:
            # If not fitted, fit on the input texts
            logger.info("Model not fitted, fitting on input texts")
            self.fit(texts)
        
        try:
            # Transform texts to TF-IDF
            tfidf_matrix = self.vectorizer.transform(texts)
            
            # Apply SVD for dimensionality reduction
            embeddings = self.svd.transform(tfidf_matrix)
            
            # Normalize embeddings
            embeddings = normalize(embeddings, norm='l2')
            
            return embeddings.astype('float32')
            
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    def encode_single(self, text: str) -> List[float]:
        """Encode a single text into an embedding"""
        embeddings = self.encode([text])
        return embeddings[0].tolist()
    
    def update_model(self, new_texts: List[str]):
        """Update the model with new texts (incremental learning simulation)"""
        if not new_texts:
            return
        
        try:
            # For TF-IDF, we need to refit with all texts
            # In a production system, you might use online learning algorithms
            logger.info(f"Updating model with {len(new_texts)} new texts")
            
            # If we have existing texts, we should ideally combine them
            # For simplicity, we'll just refit on new texts if model exists
            if self.is_fitted:
                # Transform new texts with existing model
                self.encode(new_texts)
            else:
                # Fit fresh model
                self.fit(new_texts)
                
        except Exception as e:
            logger.error(f"Error updating model: {e}")
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            embeddings = self.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1])
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            "is_fitted": self.is_fitted,
            "dimension": self.dimension,
            "model_type": "TF-IDF + SVD",
            "vectorizer_features": self.vectorizer.max_features if self.vectorizer else None,
            "model_path": self.model_path
        }

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service