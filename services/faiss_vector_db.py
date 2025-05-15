"""
FAISS Vector Database implementation for the AI Assistant Platform.
Replaces PostgreSQL pgvector with FAISS for vector storage and similarity search.
"""

import os
import numpy as np
import faiss
import pickle
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Create directory to store FAISS indexes and metadata
FAISS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'faiss')
Path(FAISS_DIR).mkdir(parents=True, exist_ok=True)

class FAISSVectorDB:
    def __init__(self):
        self.indexes = {}
        self.metadata = {}
        self.initialize()
    
    def initialize(self):
        """Initialize FAISS storage"""
        logger.info("Initializing FAISS vector database")
        
        # Check for existing indexes
        if os.path.exists(FAISS_DIR):
            for file in os.listdir(FAISS_DIR):
                if file.endswith('.index'):
                    collection_name = file.replace('.index', '')
                    self.load_index(collection_name)
    
    def load_index(self, collection_name):
        """Load an existing index and metadata"""
        index_path = os.path.join(FAISS_DIR, f"{collection_name}.index")
        meta_path = os.path.join(FAISS_DIR, f"{collection_name}.meta")
        
        try:
            if os.path.exists(index_path):
                self.indexes[collection_name] = faiss.read_index(index_path)
                
                if os.path.exists(meta_path):
                    with open(meta_path, 'rb') as f:
                        self.metadata[collection_name] = pickle.load(f)
                else:
                    self.metadata[collection_name] = {"ids": [], "data": []}
                
                logger.info(f"Loaded FAISS index for {collection_name} with {self.indexes[collection_name].ntotal} vectors")
            else:
                logger.info(f"No existing index found for {collection_name}")
                # Create new index
                self.create_collection(collection_name, 1536)  # Default dimension for many embedding models
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            # Create new index as fallback
            self.create_collection(collection_name, 1536)
    
    def create_collection(self, collection_name, dimension):
        """Create a new vector collection"""
        if collection_name in self.indexes:
            logger.info(f"Collection {collection_name} already exists")
            return True
        
        try:
            # Create a new index - using L2 distance and flat index for simplicity
            index = faiss.IndexFlatL2(dimension)
            self.indexes[collection_name] = index
            self.metadata[collection_name] = {"ids": [], "data": []}
            
            # Save to disk
            self._save_index(collection_name)
            logger.info(f"Created new FAISS collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating FAISS collection: {str(e)}")
            return False
    
    def _save_index(self, collection_name):
        """Save index and metadata to disk"""
        index_path = os.path.join(FAISS_DIR, f"{collection_name}.index")
        meta_path = os.path.join(FAISS_DIR, f"{collection_name}.meta")
        
        try:
            faiss.write_index(self.indexes[collection_name], index_path)
            with open(meta_path, 'wb') as f:
                pickle.dump(self.metadata[collection_name], f)
            logger.info(f"Saved FAISS index for {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            return False
    
    def add_vectors(self, collection_name, ids, vectors, metadata=None):
        """Add vectors to a collection"""
        if collection_name not in self.indexes:
            dimension = len(vectors[0])
            self.create_collection(collection_name, dimension)
        
        try:
            vectors_np = np.array(vectors).astype('float32')
            self.indexes[collection_name].add(vectors_np)
            
            # Update metadata
            start_idx = len(self.metadata[collection_name]["ids"])
            self.metadata[collection_name]["ids"].extend(ids)
            
            if metadata:
                if "data" not in self.metadata[collection_name]:
                    self.metadata[collection_name]["data"] = []
                self.metadata[collection_name]["data"].extend(metadata)
            
            # Save updated index
            self._save_index(collection_name)
            logger.info(f"Added {len(vectors)} vectors to collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding vectors to FAISS: {str(e)}")
            return False
    
    def search_vectors(self, collection_name, query_vector, limit=5):
        """Search for similar vectors"""
        if collection_name not in self.indexes:
            logger.error(f"Collection {collection_name} not found")
            return []
        
        try:
            query_np = np.array([query_vector]).astype('float32')
            distances, indices = self.indexes[collection_name].search(query_np, limit)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.metadata[collection_name]["ids"]):
                    result = {
                        "id": self.metadata[collection_name]["ids"][idx],
                        "score": float(distances[0][i])
                    }
                    
                    if "data" in self.metadata[collection_name] and idx < len(self.metadata[collection_name]["data"]):
                        result["metadata"] = self.metadata[collection_name]["data"][idx]
                    
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            return []

# Singleton instance
vector_db = FAISSVectorDB()

# API functions that match the PostgreSQL vector DB interface
def init_vector_db():
    """Initialize the vector database"""
    vector_db.initialize()
    return True

def create_vector_collection(collection_name, dimension=1536):
    """Create a new vector collection"""
    return vector_db.create_collection(collection_name, dimension)

def add_vectors_to_collection(collection_name, ids, vectors, metadata=None):
    """Add vectors to a collection"""
    return vector_db.add_vectors(collection_name, ids, vectors, metadata)

def search_vector_collection(collection_name, query_vector, limit=5):
    """Search for similar vectors"""
    return vector_db.search_vectors(collection_name, query_vector, limit)

# Create the same API as postgres_vector_db.py to make it a drop-in replacement
def add_embedding(document_id, chunk_id, embedding_data, text):
    """Add an embedding to the RAG collection"""
    collection_name = "rag_embeddings"
    try:
        return add_vectors_to_collection(
            collection_name, 
            [f"{document_id}_{chunk_id}"], 
            [embedding_data], 
            [{"document_id": document_id, "chunk_id": chunk_id, "text": text}]
        )
    except Exception as e:
        logger.error(f"Error adding embedding: {str(e)}")
        return False

def search_embeddings(query_embedding, limit=5):
    """Search embeddings for similar vectors"""
    collection_name = "rag_embeddings"
    try:
        results = search_vector_collection(collection_name, query_embedding, limit)
        # Format results to match the expected format from postgres_vector_db
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document_id": result["metadata"]["document_id"],
                "chunk_id": result["metadata"]["chunk_id"],
                "text": result["metadata"]["text"],
                "similarity": 1.0 - (result["score"] / 100.0) if result["score"] > 0 else 1.0
            })
        return formatted_results
    except Exception as e:
        logger.error(f"Error searching embeddings: {str(e)}")
        return []