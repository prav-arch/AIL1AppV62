"""
Application Integration for ClickHouse 18.16.1 + FAISS
This module integrates the hybrid database solution with the main application
"""

import os
import logging
import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
import faiss
from clickhouse_models import Document, DocumentChunk, VectorDBStats, initialize_database
from webscraper_with_fallback import WebScraper, TextProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory for FAISS indices
FAISS_INDEX_DIR = os.getenv('FAISS_INDEX_DIR', os.path.join(os.path.expanduser('~'), 'faiss_indices'))
FAISS_DIMENSION = int(os.getenv('FAISS_DIMENSION', 384))

class VectorSearchService:
    """Service for vector similarity search using FAISS"""
    
    def __init__(self, dimension=FAISS_DIMENSION, index_path=None):
        """Initialize the vector search service"""
        self.dimension = dimension
        self.index_path = index_path or os.path.join(FAISS_INDEX_DIR, 'faiss_index.bin')
        self.id_mapping_path = os.path.join(FAISS_INDEX_DIR, 'id_mapping.json')
        self.index = self._load_or_create_index()
        self.id_to_index = self._load_id_mapping()
        self.index_to_id = {v: k for k, v in self.id_to_index.items()}
        
        # Create directory if it doesn't exist
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    
    def _load_or_create_index(self):
        """Load an existing index or create a new one"""
        if os.path.exists(self.index_path):
            try:
                logger.info(f"Loading FAISS index from {self.index_path}")
                index = faiss.read_index(self.index_path)
                logger.info(f"Loaded index with {index.ntotal} vectors")
                return index
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                return self._create_new_index()
        else:
            return self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        logger.info(f"Creating new FAISS index with dimension {self.dimension}")
        index = faiss.IndexFlatL2(self.dimension)  # Simple L2 distance index
        return index
    
    def _load_id_mapping(self):
        """Load ID mapping from disk"""
        if os.path.exists(self.id_mapping_path):
            try:
                with open(self.id_mapping_path, 'r') as f:
                    return {int(k): int(v) for k, v in json.load(f).items()}
            except Exception as e:
                logger.error(f"Error loading ID mapping: {e}")
                return {}
        return {}
    
    def _save_id_mapping(self):
        """Save ID mapping to disk"""
        try:
            with open(self.id_mapping_path, 'w') as f:
                json.dump({str(k): v for k, v in self.id_to_index.items()}, f)
            logger.info(f"Saved ID mapping to {self.id_mapping_path}")
        except Exception as e:
            logger.error(f"Error saving ID mapping: {e}")
    
    def _save_index(self):
        """Save index to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            logger.info(f"Saved index to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def add_vectors(self, ids: List[int], vectors: List[List[float]]):
        """Add vectors to the index"""
        if not ids or not vectors or len(ids) != len(vectors):
            logger.error("Invalid input: ids and vectors must be non-empty and of the same length")
            return False
        
        # Convert to numpy array and ensure float32 type
        vectors_np = np.array(vectors).astype('float32')
        
        # Get current index size
        current_size = self.index.ntotal
        
        # Add vectors to index
        try:
            self.index.add(vectors_np)
            logger.info(f"Added {len(vectors_np)} vectors to FAISS index")
            
            # Update mapping
            for i, id_val in enumerate(ids):
                idx = current_size + i
                self.id_to_index[id_val] = idx
                self.index_to_id[idx] = id_val
            
            # Save index and mapping
            self._save_index()
            self._save_id_mapping()
            
            return True
        except Exception as e:
            logger.error(f"Error adding vectors to index: {e}")
            return False
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        
        # Convert to numpy array and ensure float32 type
        query_np = np.array([query_vector]).astype('float32')
        
        # Search index
        try:
            distances, indices = self.index.search(query_np, top_k)
            
            # Map indices to IDs
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:  # -1 means no result
                    chunk_id = self.index_to_id.get(idx)
                    if chunk_id is not None:
                        distance = distances[0][i]
                        results.append((chunk_id, float(distance)))
            
            return results
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []
    
    def delete_vectors(self, ids: List[int]) -> bool:
        """Delete vectors from the index"""
        if not ids:
            return True
        
        # FAISS doesn't support direct deletion for flat indices
        # We need to rebuild the index without the deleted vectors
        
        # Get indices to remove
        indices_to_remove = set()
        for id_val in ids:
            if id_val in self.id_to_index:
                indices_to_remove.add(self.id_to_index[id_val])
        
        if not indices_to_remove:
            return True
        
        # Create a new index
        new_index = self._create_new_index()
        new_id_to_index = {}
        new_index_to_id = {}
        
        # Only needed if we have vectors
        if self.index.ntotal > 0:
            # Get all vectors
            all_vectors = np.zeros((self.index.ntotal, self.dimension), dtype='float32')
            for i in range(self.index.ntotal):
                if i not in indices_to_remove:
                    # Get the original ID
                    original_id = self.index_to_id.get(i)
                    if original_id is not None:
                        # Get the vector
                        vector = np.zeros((1, self.dimension), dtype='float32')
                        self.index.reconstruct(i, vector[0])
                        
                        # Add to new index
                        new_index.add(vector)
                        new_idx = new_index.ntotal - 1
                        new_id_to_index[original_id] = new_idx
                        new_index_to_id[new_idx] = original_id
        
        # Replace old index and mappings
        self.index = new_index
        self.id_to_index = new_id_to_index
        self.index_to_id = new_index_to_id
        
        # Save index and mapping
        self._save_index()
        self._save_id_mapping()
        
        logger.info(f"Deleted {len(indices_to_remove)} vectors from FAISS index")
        return True
    
    def get_stats(self):
        """Get stats about the vector index"""
        return {
            "vector_count": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": "FlatL2",
            "index_path": self.index_path
        }

class ApplicationService:
    """Main application service integrating ClickHouse and FAISS"""
    
    def __init__(self):
        """Initialize the application service"""
        # Initialize database schema
        initialize_database()
        
        # Initialize vector search service
        self.vector_search = VectorSearchService()
        
        # Initialize web scraper
        self.web_scraper = WebScraper()
        
        # Initialize text processor
        self.text_processor = TextProcessor()
        
        logger.info("Application service initialized")
    
    def add_document(self, name: str, description: str, content: str, metadata: Dict = None) -> str:
        """Add a document with content"""
        # Create document
        document_id = Document.create(name, description, metadata)
        
        # Process content into chunks
        chunks = self.text_processor.chunk_text(content)
        
        # Create document chunks
        chunk_data = []
        for i, chunk_text in enumerate(chunks):
            chunk_data.append({
                'document_id': document_id,
                'chunk_index': i,
                'chunk_text': chunk_text,
                'metadata': {'index': i}
            })
        
        # Bulk create chunks
        chunk_ids = DocumentChunk.bulk_create(chunk_data)
        
        # Generate embeddings for chunks (mock implementation)
        # In a real application, you would use a proper embedding model
        embeddings = [self._mock_embedding(chunk_text) for chunk_text in chunks]
        
        # Add vectors to FAISS
        self.vector_search.add_vectors(chunk_ids, embeddings)
        
        logger.info(f"Added document {document_id} with {len(chunks)} chunks")
        return document_id
    
    def _mock_embedding(self, text: str) -> List[float]:
        """
        Generate a mock embedding for a text
        In a real application, you would use a proper embedding model
        """
        # Generate a deterministic vector based on text hash
        import hashlib
        text_hash = hashlib.md5(text.encode('utf-8')).digest()
        np.random.seed(int.from_bytes(text_hash[:4], byteorder='little'))
        
        # Generate a random vector with the specified dimension
        vector = np.random.randn(FAISS_DIMENSION).astype('float32')
        
        # Normalize to unit length
        vector = vector / np.linalg.norm(vector)
        
        return vector.tolist()
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for chunks similar to the query"""
        # Generate embedding for query
        query_embedding = self._mock_embedding(query)
        
        # Search for similar vectors
        results = self.vector_search.search(query_embedding, top_k)
        
        if not results:
            return []
        
        # Get chunk IDs
        chunk_ids = [result[0] for result in results]
        
        # Get chunks
        chunks = DocumentChunk.get_by_ids(chunk_ids)
        
        # Add similarity scores
        similarity_map = {result[0]: result[1] for result in results}
        for chunk in chunks:
            chunk['similarity'] = similarity_map.get(chunk['id'], 0.0)
        
        # Sort by similarity (lower distance is better)
        chunks.sort(key=lambda x: x['similarity'])
        
        return chunks
    
    def add_url(self, url: str, ignore_ssl_errors: bool = True) -> Dict:
        """Add content from a URL"""
        # Scrape URL
        result = self.web_scraper.extract_content(url, ignore_ssl_errors)
        
        if not result['success']:
            return {
                'success': False,
                'error': result['error'],
                'message': f"Failed to extract content from {url}"
            }
        
        # Create document
        document_id = Document.create(
            name=result['title'],
            description=f"Scraped from {url}",
            metadata={
                'source': 'web',
                'url': url,
                'domain': result['domain']
            }
        )
        
        # Process content into chunks
        content = result['content']
        chunks = self.text_processor.chunk_text(content)
        
        # Create document chunks
        chunk_data = []
        for i, chunk_text in enumerate(chunks):
            chunk_data.append({
                'document_id': document_id,
                'chunk_index': i,
                'chunk_text': chunk_text,
                'metadata': {'index': i, 'source': 'web', 'url': url}
            })
        
        # Bulk create chunks
        chunk_ids = DocumentChunk.bulk_create(chunk_data)
        
        # Generate embeddings for chunks
        embeddings = [self._mock_embedding(chunk_text) for chunk_text in chunks]
        
        # Add vectors to FAISS
        self.vector_search.add_vectors(chunk_ids, embeddings)
        
        logger.info(f"Added document {document_id} from URL {url} with {len(chunks)} chunks")
        
        return {
            'success': True,
            'document_id': document_id,
            'title': result['title'],
            'url': url,
            'chunks_count': len(chunks),
            'message': f"Successfully added content from {url}"
        }
    
    def get_document(self, document_id: str) -> Dict:
        """Get a document by ID"""
        return Document.get(document_id)
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        return Document.get_all()
    
    def get_chunks(self, document_id: str) -> List[Dict]:
        """Get all chunks for a document"""
        return DocumentChunk.get_by_document(document_id)
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks"""
        # Get chunk IDs first
        chunks = DocumentChunk.get_by_document(document_id)
        chunk_ids = [chunk['id'] for chunk in chunks]
        
        # Delete document (this will also delete chunks from ClickHouse)
        Document.delete(document_id)
        
        # Delete vectors from FAISS
        if chunk_ids:
            self.vector_search.delete_vectors(chunk_ids)
        
        return True
    
    def get_stats(self) -> Dict:
        """Get stats about the database and vector index"""
        db_stats = VectorDBStats.get()
        vector_stats = self.vector_search.get_stats()
        
        return {
            **db_stats,
            'vector_index': vector_stats
        }

# Example usage
if __name__ == "__main__":
    # Initialize application service
    app_service = ApplicationService()
    
    # Add a test document
    document_id = app_service.add_document(
        name="Test Document",
        description="This is a test document",
        content="This is a test document with some content. It can be split into multiple chunks for vector search.",
        metadata={"test": True}
    )
    
    print(f"Added document with ID: {document_id}")
    
    # Test search
    results = app_service.search_similar("test document")
    print(f"Search results: {len(results)} chunks found")
    for result in results:
        print(f"Chunk: {result['chunk_text'][:50]}... (similarity: {result['similarity']})")
    
    # Test URL import
    url_result = app_service.add_url("https://en.wikipedia.org/wiki/ClickHouse")
    if url_result['success']:
        print(f"Added document from URL: {url_result['title']}")
    else:
        print(f"Failed to add document from URL: {url_result['error']}")
    
    # Get stats
    stats = app_service.get_stats()
    print(f"Database stats: {stats}")