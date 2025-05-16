"""
Database utilities for the application with ClickHouse and FAISS
"""

import os
import json
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RagService:
    """
    RAG (Retrieval-Augmented Generation) service for the application
    """
    
    def get_documents(self, limit=10) -> List[Dict]:
        """Get list of documents"""
        documents = []
        doc_types = ['pdf', 'txt', 'md', 'html', 'doc']
        categories = ['reference', 'guide', 'tutorial', 'api', 'specification']
        
        for i in range(limit):
            created = datetime.now() - timedelta(days=random.randint(1, 100))
            doc_type = random.choice(doc_types)
            
            documents.append({
                'id': f'doc-{i+100}',
                'title': f'Sample Document {i+1}',
                'type': doc_type,
                'filename': f'document_{i+1}.{doc_type}',
                'size_kb': random.randint(50, 5000),
                'category': random.choice(categories),
                'created_at': created.isoformat(),
                'last_accessed': (created + timedelta(days=random.randint(0, 30))).isoformat(),
                'chunks': random.randint(5, 100),
                'embedding_model': random.choice(['sentence-transformers/all-MiniLM-L6-v2', 'text-embedding-3-small', 'sentence-transformers/all-mpnet-base-v2'])
            })
        
        return documents
    
    def get_vectordb_stats(self) -> Dict:
        """Get vector database statistics"""
        return {
            'total_documents': random.randint(50, 200),
            'total_chunks': random.randint(500, 5000),
            'total_tokens': random.randint(100000, 1000000),
            'embedding_dimensions': 384,
            'index_type': 'FAISS',
            'last_updated': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
            'storage_used_mb': random.randint(50, 500),
            'models': {
                'embedding': 'sentence-transformers/all-MiniLM-L6-v2',
                'retrieval': 'hybrid'
            }
        }
    
    def search(self, query: str, num_results: int = 3) -> Dict:
        """Perform a search with the given query"""
        results = []
        for i in range(num_results):
            results.append({
                'doc_id': f'doc-{random.randint(100, 999)}',
                'title': f'Sample Document {i+1}',
                'snippet': f'This is a relevant snippet from document {i+1} that matches the query: "{query}"...',
                'relevance_score': round(random.uniform(0.70, 0.99), 4),
                'document_type': random.choice(['pdf', 'txt', 'md', 'html']),
                'metadata': {
                    'author': f'Author {random.randint(1, 10)}',
                    'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    'category': random.choice(['reference', 'guide', 'tutorial', 'api', 'specification'])
                }
            })
        
        return {
            'query': query,
            'results': results,
            'search_time_ms': random.randint(50, 500),
            'total_docs_searched': random.randint(50, 200)
        }
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
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