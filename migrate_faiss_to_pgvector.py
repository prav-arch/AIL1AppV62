#!/usr/bin/env python3
"""
Migration script to transfer vector embeddings from FAISS to pgvector

This script will:
1. Load embeddings from FAISS indexes
2. Insert them into the PostgreSQL pgvector database
3. Verify the transfer was successful
"""

import os
import sys
import logging
import numpy as np
import faiss
import json
import time
from tqdm import tqdm
from typing import Dict, List, Any, Tuple

# Import both vector DB implementations
from services.faiss_vector_db import load_index, get_metadata
from services.pgvector_db import (
    init_vector_db, 
    batch_add_embeddings,
    count_embeddings,
    search_embeddings
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_faiss_data(collection_name='rag_embeddings'):
    """
    Load vector embeddings and metadata from FAISS
    
    Returns:
        Tuple of (vectors, metadata)
    """
    logger.info(f"Loading FAISS index for collection: {collection_name}")
    
    # Path to FAISS index and metadata
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    index_path = os.path.join(data_dir, f"{collection_name}.index")
    metadata_path = os.path.join(data_dir, f"{collection_name}_metadata.json")
    
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        logger.error(f"FAISS index or metadata file not found: {index_path}, {metadata_path}")
        return None, None
    
    # Load FAISS index
    index = faiss.read_index(index_path)
    logger.info(f"Loaded FAISS index with {index.ntotal} vectors")
    
    # Extract vectors from index
    vectors = None
    if index.ntotal > 0:
        vectors = np.zeros((index.ntotal, index.d), dtype=np.float32)
        for i in range(index.ntotal):
            faiss.extract_index_vector(index, i, vectors[i])
    
    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    logger.info(f"Loaded metadata for {len(metadata)} vectors")
    
    return vectors, metadata

def prepare_pgvector_data(vectors, metadata):
    """
    Prepare vector data for pgvector import
    
    Args:
        vectors: NumPy array of vectors from FAISS
        metadata: Dictionary of metadata from FAISS
        
    Returns:
        List of dictionaries ready for pgvector import
    """
    if vectors is None or metadata is None:
        logger.error("Cannot prepare data: vectors or metadata is None")
        return []
    
    pgvector_data = []
    
    for i, vector_id in enumerate(metadata.keys()):
        try:
            # Extract and parse the document information from metadata
            doc_info = metadata[vector_id]
            
            # Skip if missing required fields
            if 'document_id' not in doc_info or 'chunk_id' not in doc_info or 'text' not in doc_info:
                logger.warning(f"Skipping vector {vector_id}, missing required fields")
                continue
            
            # Create pgvector entry
            pgvector_entry = {
                'document_id': doc_info['document_id'],
                'chunk_id': doc_info['chunk_id'],
                'embedding': vectors[i] if i < len(vectors) else None,
                'text': doc_info['text'],
                'metadata': {
                    'source': doc_info.get('source', 'faiss_migration'),
                    'original_id': vector_id,
                    **{k: v for k, v in doc_info.items() if k not in ['document_id', 'chunk_id', 'text']}
                }
            }
            
            # Skip if embedding is None
            if pgvector_entry['embedding'] is None:
                logger.warning(f"Skipping vector {vector_id}, no embedding found")
                continue
                
            pgvector_data.append(pgvector_entry)
            
        except Exception as e:
            logger.error(f"Error preparing vector {vector_id}: {e}")
    
    logger.info(f"Prepared {len(pgvector_data)} vectors for pgvector import")
    return pgvector_data

def migrate_to_pgvector(batch_size=100):
    """
    Migrate data from FAISS to pgvector
    
    Args:
        batch_size: Number of vectors to migrate in each batch
        
    Returns:
        bool: True if migration successful, False otherwise
    """
    # Initialize pgvector
    logger.info("Initializing pgvector database...")
    if not init_vector_db():
        logger.error("Failed to initialize pgvector database")
        return False
    
    # Count existing embeddings in pgvector
    initial_count = count_embeddings()
    logger.info(f"Found {initial_count} existing embeddings in pgvector")
    
    # Load data from FAISS
    vectors, metadata = load_faiss_data()
    if vectors is None or metadata is None:
        logger.error("Failed to load data from FAISS")
        return False
    
    # Prepare data for pgvector
    pgvector_data = prepare_pgvector_data(vectors, metadata)
    if not pgvector_data:
        logger.error("No data prepared for pgvector import")
        return False
    
    # Migrate in batches
    total_batches = (len(pgvector_data) + batch_size - 1) // batch_size
    success_count = 0
    
    logger.info(f"Starting migration of {len(pgvector_data)} vectors in {total_batches} batches...")
    
    for i in range(0, len(pgvector_data), batch_size):
        batch = pgvector_data[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        logger.info(f"Migrating batch {batch_num}/{total_batches} ({len(batch)} vectors)...")
        
        if batch_add_embeddings(batch):
            success_count += len(batch)
            logger.info(f"Successfully migrated batch {batch_num}")
        else:
            logger.error(f"Failed to migrate batch {batch_num}")
    
    # Verify migration
    final_count = count_embeddings()
    new_count = final_count - initial_count
    
    logger.info(f"Migration complete: {success_count}/{len(pgvector_data)} vectors migrated")
    logger.info(f"pgvector database now contains {final_count} embeddings (added {new_count})")
    
    if new_count != success_count:
        logger.warning(f"Discrepancy in counts: reported success for {success_count} but added {new_count}")
    
    return True

def verify_migration():
    """
    Verify migration was successful by running a test search
    
    Returns:
        bool: True if verification successful, False otherwise
    """
    logger.info("Verifying migration with a test search...")
    
    # Generate a random test vector
    test_vector = np.random.rand(1536).astype('float32')
    
    # Run search
    results = search_embeddings(test_vector, limit=5)
    
    if not results:
        logger.error("Verification failed: No search results returned")
        return False
    
    logger.info(f"Verification successful: Found {len(results)} results")
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: doc={result['document_id']}, "
                   f"chunk={result['chunk_id']}, similarity={result['similarity']:.4f}")
    
    return True

def run_migration():
    """Run the full migration process"""
    print("=== FAISS to pgvector Migration Tool ===\n")
    
    # Check if we should proceed
    answer = input("This will migrate vector embeddings from FAISS to PostgreSQL pgvector.\n"
                  "Make sure PostgreSQL with pgvector is running first.\n"
                  "Do you want to proceed? (y/n): ")
    
    if answer.lower() != 'y':
        print("Migration cancelled.")
        return
    
    print("\nStarting migration process...\n")
    start_time = time.time()
    
    success = migrate_to_pgvector()
    
    if success:
        verify_success = verify_migration()
        if verify_success:
            print("\n✅ Migration completed successfully!")
        else:
            print("\n⚠️ Migration completed, but verification failed.")
    else:
        print("\n❌ Migration failed.")
    
    elapsed_time = time.time() - start_time
    print(f"\nTotal time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    run_migration()