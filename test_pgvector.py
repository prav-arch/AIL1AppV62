#!/usr/bin/env python3
"""
Test script for pgvector functionality.
This script verifies that pgvector is working correctly with the PostgreSQL installation.
"""

import os
import sys
import uuid
import numpy as np
import time
import logging
from datetime import datetime
from services.pgvector_db import (
    init_vector_db, 
    add_embedding, 
    batch_add_embeddings,
    search_embeddings, 
    delete_embeddings,
    get_document_embeddings,
    count_embeddings
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_embedding(dim=1536):
    """Generate a random embedding vector for testing"""
    return np.random.rand(dim).astype('float32')

def test_pgvector_setup():
    """Test that pgvector is properly set up"""
    print("\n1. Testing pgvector initialization...")
    success = init_vector_db()
    
    if success:
        print("✅ pgvector extension and tables are properly initialized")
    else:
        print("❌ Failed to initialize pgvector extension or tables")
        return False
    
    return True

def test_adding_embeddings():
    """Test adding embeddings to pgvector"""
    print("\n2. Testing adding embeddings...")
    
    # Generate a test document ID
    doc_id = f"test-document-{uuid.uuid4()}"
    print(f"Using test document ID: {doc_id}")
    
    # Add a single embedding
    test_text = "This is a test document for pgvector embeddings."
    embedding = generate_random_embedding()
    metadata = {
        "source": "test_script",
        "created": datetime.now().isoformat(),
        "topic": "testing"
    }
    
    print("Adding a single embedding...")
    success = add_embedding(doc_id, 1, embedding, test_text, metadata)
    
    if success:
        print("✅ Successfully added a single embedding")
    else:
        print("❌ Failed to add a single embedding")
        return False, None
    
    # Batch add several embeddings
    print("Adding a batch of embeddings...")
    batch_data = []
    for i in range(2, 6):
        batch_data.append({
            "document_id": doc_id,
            "chunk_id": i,
            "embedding": generate_random_embedding(),
            "text": f"Test document chunk {i}",
            "metadata": {
                "source": "test_script",
                "chunk_number": i,
                "topic": "testing"
            }
        })
    
    success = batch_add_embeddings(batch_data)
    
    if success:
        print(f"✅ Successfully added a batch of {len(batch_data)} embeddings")
    else:
        print("❌ Failed to add batch embeddings")
        return False, None
    
    # Count total embeddings
    count = count_embeddings()
    print(f"Total embeddings in database: {count}")
    
    return True, doc_id

def test_searching_embeddings(doc_id):
    """Test searching for similar embeddings"""
    print("\n3. Testing embedding similarity search...")
    
    # Generate a query embedding
    query_embedding = generate_random_embedding()
    
    # Search with no filters
    print("Searching for similar embeddings with no filters...")
    results = search_embeddings(query_embedding, limit=5)
    
    if results:
        print(f"✅ Found {len(results)} similar embeddings")
        print("Top result:")
        top = results[0]
        print(f"  Document ID: {top['document_id']}")
        print(f"  Chunk ID: {top['chunk_id']}")
        print(f"  Similarity: {top['similarity']:.4f}")
        print(f"  Text: {top['text'][:50]}...")
    else:
        print("❌ No search results found")
        return False
    
    # Search with document filter
    print(f"\nSearching only within document {doc_id}...")
    filtered_results = search_embeddings(
        query_embedding, 
        limit=5,
        filter_criteria={"document_id": doc_id}
    )
    
    if filtered_results:
        print(f"✅ Found {len(filtered_results)} similar embeddings in document {doc_id}")
    else:
        print(f"❌ No search results found for document {doc_id}")
        return False
    
    return True

def test_retrieving_embeddings(doc_id):
    """Test retrieving embeddings for a document"""
    print("\n4. Testing embedding retrieval...")
    
    embeddings = get_document_embeddings(doc_id)
    
    if embeddings:
        print(f"✅ Retrieved {len(embeddings)} embeddings for document {doc_id}")
        for i, emb in enumerate(embeddings[:2]):  # Show just the first 2
            print(f"  Embedding {i+1}:")
            print(f"    Chunk ID: {emb['chunk_id']}")
            print(f"    Text: {emb['text'][:50]}...")
        if len(embeddings) > 2:
            print(f"  ... and {len(embeddings)-2} more")
    else:
        print(f"❌ No embeddings found for document {doc_id}")
        return False
    
    return True

def test_deleting_embeddings(doc_id):
    """Test deleting embeddings"""
    print("\n5. Testing embedding deletion...")
    
    # Count before deletion
    before_count = count_embeddings()
    print(f"Embeddings before deletion: {before_count}")
    
    # Delete all embeddings for the test document
    success = delete_embeddings(document_id=doc_id)
    
    if success:
        print(f"✅ Successfully deleted embeddings for document {doc_id}")
    else:
        print(f"❌ Failed to delete embeddings for document {doc_id}")
        return False
    
    # Count after deletion
    after_count = count_embeddings()
    print(f"Embeddings after deletion: {after_count}")
    
    # Verify embeddings were deleted
    deleted_count = before_count - after_count
    print(f"Deleted {deleted_count} embeddings")
    
    return True

def run_all_tests():
    """Run all pgvector tests"""
    print("=== pgvector PostgreSQL Tests ===\n")
    
    if not test_pgvector_setup():
        print("\n❌ Testing stopped due to initialization failure")
        return False
    
    success, doc_id = test_adding_embeddings()
    if not success:
        print("\n❌ Testing stopped due to embedding addition failure")
        return False
    
    if not test_searching_embeddings(doc_id):
        print("\n❌ Testing stopped due to embedding search failure")
        return False
    
    if not test_retrieving_embeddings(doc_id):
        print("\n❌ Testing stopped due to embedding retrieval failure")
        return False
    
    if not test_deleting_embeddings(doc_id):
        print("\n❌ Testing stopped due to embedding deletion failure")
        return False
    
    print("\n✅ All pgvector tests completed successfully! The PostgreSQL + pgvector setup is working correctly.")
    return True

if __name__ == "__main__":
    run_all_tests()