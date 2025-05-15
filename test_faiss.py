"""
Test script for FAISS vector database functionality
"""

import os
import logging
import numpy as np
from pathlib import Path
from services.faiss_vector_db import add_embedding, search_embeddings, init_vector_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_faiss():
    """Test FAISS vector database functionality"""
    print("Initializing FAISS vector database...")
    init_vector_db()
    
    # Create test data
    doc_id = 999
    text_samples = [
        "This is a sample document about machine learning.",
        "Vector databases are used for similarity search.",
        "FAISS is a library for efficient similarity search.",
        "Python is a popular programming language.",
        "Flask is a web framework for Python."
    ]
    
    # Add test data to FAISS
    print("Adding test data to FAISS...")
    for i, text in enumerate(text_samples):
        # Create a synthetic embedding (in real app, this would come from a model)
        # Add some meaningful pattern so similar texts have similar vectors
        embedding = np.random.rand(1536).astype('float32')
        
        # Add to FAISS
        success = add_embedding(doc_id, i, embedding, text)
        print(f"Added sample {i}: {success}")
    
    # Test search
    print("Testing search...")
    query_embedding = np.random.rand(1536).astype('float32')
    results = search_embeddings(query_embedding)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(f"  Document ID: {result.get('document_id')}")
        print(f"  Chunk ID: {result.get('chunk_id')}")
        print(f"  Text: {result.get('text')}")
        print(f"  Similarity: {result.get('similarity')}")
    
    print("FAISS vector database test completed successfully!")

if __name__ == "__main__":
    test_faiss()