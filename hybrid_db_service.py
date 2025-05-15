"""
Hybrid Database Service that combines ClickHouse 18.16.1 and FAISS

This service provides:
1. ClickHouse integration for regular document storage and retrieval
2. FAISS integration for vector similarity search
"""

import os
import json
import time
import uuid
import faiss
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime
from clickhouse_driver import Client
from hybrid_config import DB_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaissVectorStore:
    """FAISS vector store for embedding vectors"""
    
    def __init__(self, dimension=384, index_type="L2", use_gpu=False):
        """Initialize FAISS vector store"""
        self.dimension = dimension
        self.index_type = index_type
        self.use_gpu = use_gpu
        self.index_path = os.path.join(DB_CONFIG['faiss']['index_dir'], 'vector_index.faiss')
        self.mapping_path = os.path.join(DB_CONFIG['faiss']['index_dir'], 'id_mapping.json')
        self.index = self._create_or_load_index()
        self.id_to_index_mapping = self._load_mapping()
        self.index_to_id_mapping = {v: k for k, v in self.id_to_index_mapping.items()}
    
    def _create_or_load_index(self):
        """Create or load FAISS index"""
        if os.path.exists(self.index_path):
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            try:
                index = faiss.read_index(self.index_path)
                logger.info(f"FAISS index loaded with {index.ntotal} vectors")
                return index
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                return self._create_new_index()
        else:
            return self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        logger.info(f"Creating new FAISS index with dimension {self.dimension}")
        if self.index_type == "L2":
            index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "IP":
            index = faiss.IndexFlatIP(self.dimension)
        else:
            # Default to L2
            index = faiss.IndexFlatL2(self.dimension)
        
        # If we want to use GPU and have GPU support
        if self.use_gpu and faiss.get_num_gpus() > 0:
            logger.info("Using GPU acceleration for FAISS")
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index)
        
        # For larger indices, we might want to use more complex index types
        # index = faiss.IndexIVFFlat(index, self.dimension, 100)
        # index.train(np.random.random((1000, self.dimension)).astype('float32'))
        
        return index
    
    def _load_mapping(self):
        """Load ID mapping from disk"""
        if os.path.exists(self.mapping_path):
            try:
                with open(self.mapping_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading ID mapping: {e}")
                return {}
        return {}
    
    def _save_mapping(self):
        """Save ID mapping to disk"""
        try:
            with open(self.mapping_path, 'w') as f:
                json.dump(self.id_to_index_mapping, f)
        except Exception as e:
            logger.error(f"Error saving ID mapping: {e}")
    
    def _save_index(self):
        """Save FAISS index to disk"""
        # If using GPU, convert back to CPU for storage
        index_to_save = self.index
        if self.use_gpu and faiss.get_num_gpus() > 0:
            index_to_save = faiss.index_gpu_to_cpu(self.index)
        
        try:
            faiss.write_index(index_to_save, self.index_path)
            logger.info(f"FAISS index saved to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def add_vectors(self, ids: List[str], vectors: List[List[float]]):
        """Add vectors to the index"""
        if not ids or not vectors:
            return
        
        # Convert to numpy array
        vectors_np = np.array(vectors).astype('float32')
        
        # Get current index size
        current_size = self.index.ntotal
        
        # Add vectors to index
        self.index.add(vectors_np)
        
        # Update mappings
        for i, id_str in enumerate(ids):
            idx = current_size + i
            self.id_to_index_mapping[id_str] = idx
            self.index_to_id_mapping[idx] = id_str
        
        # Save index and mappings
        self._save_index()
        self._save_mapping()
        
        logger.info(f"Added {len(ids)} vectors to FAISS index")
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty, returning empty results")
            return []
        
        # Convert to numpy array
        query_np = np.array([query_vector]).astype('float32')
        
        # Search index
        distances, indices = self.index.search(query_np, top_k)
        
        # Map indices to IDs
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < 0:  # FAISS returns -1 if fewer than top_k results are found
                continue
            
            distance = distances[0][i]
            id_str = self.index_to_id_mapping.get(int(idx))
            if id_str:
                results.append((id_str, float(distance)))
        
        return results
    
    def delete_vectors(self, ids: List[str]):
        """Delete vectors from the index (not supported in all FAISS indices)"""
        # FAISS doesn't support direct deletion for most index types
        # For production, you would implement a more complex solution
        # Here we'll rebuild the index without the deleted vectors
        
        # Get indices to remove
        indices_to_remove = set()
        for id_str in ids:
            if id_str in self.id_to_index_mapping:
                indices_to_remove.add(self.id_to_index_mapping[id_str])
        
        if not indices_to_remove:
            return
        
        # Create a new index
        new_index = self._create_new_index()
        new_id_to_index = {}
        new_index_to_id = {}
        
        # Copy vectors to keep
        if self.index.ntotal > 0:
            all_vectors = np.zeros((self.index.ntotal, self.dimension), dtype='float32')
            faiss.extract_index_vectors(self.index, all_vectors)
            
            # Add vectors to new index
            new_idx = 0
            for old_idx in range(self.index.ntotal):
                if old_idx not in indices_to_remove:
                    id_str = self.index_to_id_mapping.get(old_idx)
                    if id_str:
                        vector = all_vectors[old_idx].reshape(1, -1)
                        new_index.add(vector)
                        new_id_to_index[id_str] = new_idx
                        new_index_to_id[new_idx] = id_str
                        new_idx += 1
        
        # Replace old index and mappings
        self.index = new_index
        self.id_to_index_mapping = new_id_to_index
        self.index_to_id_mapping = new_index_to_id
        
        # Save index and mappings
        self._save_index()
        self._save_mapping()
        
        logger.info(f"Deleted {len(indices_to_remove)} vectors from FAISS index")
    
    def get_stats(self):
        """Get stats about the vector index"""
        return {
            "vector_count": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "use_gpu": self.use_gpu,
            "index_path": self.index_path
        }


class ClickHouseDB:
    """ClickHouse database connection for version 18.16.1"""
    
    def __init__(self):
        """Initialize ClickHouse database connection"""
        self.config = DB_CONFIG['clickhouse']
        self.client = self._get_client()
    
    def _get_client(self):
        """Get ClickHouse client connection"""
        try:
            client = Client(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                connect_timeout=10
            )
            logger.info(f"Connected to ClickHouse at {self.config['host']}:{self.config['port']}")
            return client
        except Exception as e:
            logger.error(f"Error connecting to ClickHouse: {e}")
            raise
    
    def execute(self, query, params=None):
        """Execute a query with parameters"""
        try:
            return self.client.execute(query, params or {})
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def create_tables(self):
        """Create necessary tables"""
        # Read the schema file
        try:
            with open('clickhouse_schema.sql', 'r') as f:
                schema = f.read()
            
            # Split the schema into individual queries
            queries = [q.strip() for q in schema.split(';') if q.strip()]
            
            # Execute each query
            for query in queries:
                try:
                    self.execute(query)
                except Exception as e:
                    logger.error(f"Error executing schema query: {e}")
                    logger.error(f"Query: {query}")
            
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            raise
    
    def add_document(self, document_id, name, description, metadata, file_path):
        """Add a document to the database"""
        query = """
        INSERT INTO documents (id, name, description, metadata, file_path)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (document_id, name, description, metadata, file_path)
        self.execute(query, params)
        
        # Update document count
        self.execute("""
        UPDATE vector_db_stats 
        SET documents_count = documents_count + 1, last_modified = now() 
        WHERE id = 1
        """)
        
        logger.info(f"Added document {document_id} to ClickHouse")
        return document_id
    
    def add_chunks(self, chunks):
        """Add document chunks to the database"""
        if not chunks:
            return
        
        # ClickHouse bulk insert
        query = """
        INSERT INTO document_chunks (id, document_id, chunk_index, chunk_text, metadata)
        VALUES
        """
        params = []
        for chunk in chunks:
            chunk_id = chunk.get('id') or int(time.time() * 1000000)
            params.append((
                chunk_id,
                chunk['document_id'],
                chunk['chunk_index'],
                chunk['chunk_text'],
                json.dumps(chunk.get('metadata', {}))
            ))
        
        self.client.execute(query, params)
        
        # Update chunk count
        self.execute("""
        UPDATE vector_db_stats 
        SET chunks_count = chunks_count + %s, last_modified = now() 
        WHERE id = 1
        """, (len(chunks),))
        
        logger.info(f"Added {len(chunks)} chunks to ClickHouse")
    
    def get_document(self, document_id):
        """Get a document by ID"""
        query = "SELECT id, name, description, metadata, file_path, created_at FROM documents WHERE id = %s"
        result = self.execute(query, (document_id,))
        
        if not result:
            return None
        
        row = result[0]
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "metadata": row[3],
            "file_path": row[4],
            "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None
        }
    
    def get_chunks_by_document(self, document_id):
        """Get all chunks for a document"""
        query = """
        SELECT id, document_id, chunk_index, chunk_text, metadata, created_at 
        FROM document_chunks 
        WHERE document_id = %s 
        ORDER BY chunk_index
        """
        result = self.execute(query, (document_id,))
        
        chunks = []
        for row in result:
            chunks.append({
                "id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "chunk_text": row[3],
                "metadata": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None
            })
        
        return chunks
    
    def get_chunks_by_ids(self, chunk_ids):
        """Get chunks by IDs"""
        if not chunk_ids:
            return []
        
        # Convert to list of strings for the IN clause
        id_strings = [str(id) for id in chunk_ids]
        id_list = ", ".join([f"'{id}'" for id in id_strings])
        
        query = f"""
        SELECT id, document_id, chunk_index, chunk_text, metadata, created_at 
        FROM document_chunks 
        WHERE id IN ({id_list})
        """
        result = self.execute(query)
        
        chunks = []
        for row in result:
            chunks.append({
                "id": str(row[0]),
                "document_id": row[1],
                "chunk_index": row[2],
                "chunk_text": row[3],
                "metadata": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None
            })
        
        return chunks
    
    def get_all_documents(self):
        """Get all documents"""
        query = "SELECT id, name, description, metadata, file_path, created_at FROM documents ORDER BY created_at DESC"
        result = self.execute(query)
        
        documents = []
        for row in result:
            documents.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "metadata": row[3],
                "file_path": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None
            })
        
        return documents
    
    def get_db_stats(self):
        """Get database statistics"""
        query = "SELECT documents_count, chunks_count, vector_dim, last_modified FROM vector_db_stats WHERE id = 1"
        result = self.execute(query)
        
        if not result:
            return {
                "documents_count": 0,
                "chunks_count": 0,
                "vector_dim": 384,
                "last_modified": None
            }
        
        row = result[0]
        return {
            "documents_count": row[0],
            "chunks_count": row[1],
            "vector_dim": row[2],
            "last_modified": row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else None
        }


class HybridDBService:
    """Hybrid database service combining ClickHouse and FAISS"""
    
    def __init__(self):
        """Initialize the hybrid database service"""
        self.clickhouse = ClickHouseDB()
        self.vector_store = FaissVectorStore(
            dimension=DB_CONFIG['faiss']['dimension'],
            index_type=DB_CONFIG['faiss']['index_type'],
            use_gpu=DB_CONFIG['faiss']['use_gpu']
        )
        
        # Create tables if needed
        try:
            self.clickhouse.create_tables()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
    
    def add_document(self, name, description, metadata=None, file_path=None):
        """Add a document to the database"""
        document_id = str(uuid.uuid4())
        metadata_str = json.dumps(metadata) if metadata else "{}"
        
        self.clickhouse.add_document(
            document_id=document_id,
            name=name,
            description=description,
            metadata=metadata_str,
            file_path=file_path or ""
        )
        
        return document_id
    
    def add_chunks_with_embeddings(self, document_id, chunks, embeddings):
        """
        Add document chunks with embeddings
        
        Args:
            document_id: The document ID
            chunks: List of chunk texts
            embeddings: List of embeddings for each chunk
        """
        if not chunks or not embeddings or len(chunks) != len(embeddings):
            logger.error("Chunks and embeddings must be non-empty and of the same length")
            return
        
        # Prepare chunk data for ClickHouse
        chunk_data = []
        chunk_ids = []
        
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)
            
            chunk_data.append({
                "id": chunk_id,
                "document_id": document_id,
                "chunk_index": i,
                "chunk_text": chunk_text,
                "metadata": json.dumps({"index": i})
            })
        
        # Add chunks to ClickHouse
        self.clickhouse.add_chunks(chunk_data)
        
        # Add embeddings to FAISS
        self.vector_store.add_vectors(chunk_ids, embeddings)
        
        return chunk_ids
    
    def search_similar(self, query_embedding, top_k=5):
        """
        Search for chunks similar to the query embedding
        
        Args:
            query_embedding: The query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of chunks with similarity scores
        """
        # Search in FAISS
        results = self.vector_store.search(query_embedding, top_k)
        
        if not results:
            return []
        
        # Get chunk IDs
        chunk_ids = [result[0] for result in results]
        
        # Get chunks from ClickHouse
        chunks = self.clickhouse.get_chunks_by_ids(chunk_ids)
        
        # Add similarity scores
        similarity_map = {result[0]: result[1] for result in results}
        for chunk in chunks:
            chunk["similarity"] = similarity_map.get(chunk["id"], 0.0)
        
        # Sort by similarity
        chunks.sort(key=lambda x: x["similarity"])
        
        return chunks
    
    def get_document(self, document_id):
        """Get a document by ID"""
        return self.clickhouse.get_document(document_id)
    
    def get_chunks_by_document(self, document_id):
        """Get all chunks for a document"""
        return self.clickhouse.get_chunks_by_document(document_id)
    
    def get_all_documents(self):
        """Get all documents"""
        return self.clickhouse.get_all_documents()
    
    def get_stats(self):
        """Get database statistics"""
        clickhouse_stats = self.clickhouse.get_db_stats()
        vector_stats = self.vector_store.get_stats()
        
        return {
            **clickhouse_stats,
            "vector_store": vector_stats
        }