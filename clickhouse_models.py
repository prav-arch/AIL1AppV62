"""
ClickHouse Models for version 18.16.1
This module provides model classes and database schema specific to ClickHouse 18.16.1
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import json
import time
import uuid
import logging
from clickhouse_driver import Client
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ClickHouse connection parameters
CLICKHOUSE_CONFIG = {
    'host': 'localhost',
    'port': 9000,
    'user': 'default',
    'password': '',
    'database': 'l1_app_db',
    'connect_timeout': 10
}

def get_clickhouse_client():
    """Get a ClickHouse client connection"""
    try:
        client = Client(**CLICKHOUSE_CONFIG)
        return client
    except Exception as e:
        logger.error(f"Error connecting to ClickHouse: {e}")
        raise

class BaseModel:
    """Base model for ClickHouse tables"""
    
    table_name = None
    fields = []
    
    @classmethod
    def create_table(cls):
        """Create the table if it doesn't exist"""
        if not cls.table_name or not cls.fields:
            raise NotImplementedError("Subclasses must define table_name and fields")
        
        client = get_clickhouse_client()
        
        # Create database if it doesn't exist
        client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_CONFIG['database']}")
        
        # Create table
        create_query = f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({', '.join(cls.fields)}) ENGINE = MergeTree() ORDER BY id"
        
        try:
            client.execute(create_query)
            logger.info(f"Table {cls.table_name} created or already exists")
            return True
        except Exception as e:
            logger.error(f"Error creating table {cls.table_name}: {e}")
            return False
    
    @classmethod
    def execute(cls, query, params=None):
        """Execute a query"""
        client = get_clickhouse_client()
        try:
            return client.execute(query, params or {})
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

class Document(BaseModel):
    """Document model for ClickHouse"""
    
    table_name = 'documents'
    fields = [
        'id String',
        'name String',
        'description String',
        'metadata String',
        'file_path String',
        'created_at DateTime DEFAULT now()',
        'minio_url String',
        'bucket String',
        'storage_type String',
        'status String',
        'indexed UInt8',
        'filename String',
        'file_size UInt64'
    ]
    
    @classmethod
    def create(cls, name: str, description: str, metadata: Dict = None, file_path: str = None, 
               minio_url: str = None, bucket: str = None, storage_type: str = None, 
               status: str = None, indexed: bool = False, filename: str = None, file_size: int = 0) -> str:
        """Create a new document with Minio storage information"""
        document_id = str(uuid.uuid4())
        metadata_str = json.dumps(metadata) if metadata else '{}'
        
        query = f"""
        INSERT INTO {cls.table_name} (
            id, name, description, metadata, file_path, 
            minio_url, bucket, storage_type, status, indexed, 
            filename, file_size
        )
        VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s
        )
        """
        params = (
            document_id, name, description, metadata_str, file_path or '',
            minio_url or '', bucket or '', storage_type or '', status or '', 1 if indexed else 0,
            filename or '', file_size or 0
        )
        
        cls.execute(query, params)
        
        # Update document count in stats
        VectorDBStats.increment_document_count()
        
        return document_id
    
    @classmethod
    def get(cls, document_id: str) -> Dict:
        """Get a document by ID"""
        query = f"""
        SELECT id, name, description, metadata, file_path, created_at
        FROM {cls.table_name}
        WHERE id = %s
        """
        
        result = cls.execute(query, (document_id,))
        
        if not result:
            return None
        
        row = result[0]
        return {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'metadata': json.loads(row[3]) if row[3] else {},
            'file_path': row[4],
            'created_at': row[5].isoformat() if row[5] else None
        }
    
    @classmethod
    def get_all(cls) -> List[Dict]:
        """Get all documents"""
        query = f"""
        SELECT id, name, description, metadata, file_path, created_at
        FROM {cls.table_name}
        ORDER BY created_at DESC
        """
        
        result = cls.execute(query)
        
        documents = []
        for row in result:
            documents.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'file_path': row[4],
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return documents
    
    @classmethod
    def delete(cls, document_id: str) -> bool:
        """Delete a document by ID"""
        # First find related chunks to update stats correctly
        chunk_count = DocumentChunk.count_by_document(document_id)
        
        query = f"""
        DELETE FROM {cls.table_name}
        WHERE id = %s
        """
        
        cls.execute(query, (document_id,))
        
        # Also delete related chunks
        DocumentChunk.delete_by_document(document_id)
        
        # Update stats
        VectorDBStats.decrement_document_count()
        if chunk_count > 0:
            VectorDBStats.decrement_chunk_count(chunk_count)
        
        return True
    
    @classmethod
    def search(cls, search_term: str, limit: int = 10) -> List[Dict]:
        """Search documents by name or description"""
        query = f"""
        SELECT id, name, description, metadata, file_path, created_at
        FROM {cls.table_name}
        WHERE name LIKE %s OR description LIKE %s
        ORDER BY created_at DESC
        LIMIT {limit}
        """
        
        search_pattern = f'%{search_term}%'
        result = cls.execute(query, (search_pattern, search_pattern))
        
        documents = []
        for row in result:
            documents.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'file_path': row[4],
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return documents

class DocumentChunk(BaseModel):
    """Document chunk model for ClickHouse"""
    
    table_name = 'document_chunks'
    fields = [
        'id UInt64',
        'document_id String',
        'chunk_index UInt32',
        'chunk_text String',
        'metadata String',
        'created_at DateTime DEFAULT now()'
    ]
    
    @classmethod
    def create(cls, document_id: str, chunk_index: int, chunk_text: str, metadata: Dict = None) -> int:
        """Create a new document chunk"""
        chunk_id = int(time.time() * 1000000)  # Use timestamp as ID for simplicity
        metadata_str = json.dumps(metadata) if metadata else '{}'
        
        query = f"""
        INSERT INTO {cls.table_name} (id, document_id, chunk_index, chunk_text, metadata)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (chunk_id, document_id, chunk_index, chunk_text, metadata_str)
        
        cls.execute(query, params)
        
        # Update chunk count in stats
        VectorDBStats.increment_chunk_count()
        
        return chunk_id
    
    @classmethod
    def bulk_create(cls, chunks: List[Dict]) -> List[int]:
        """Create multiple document chunks at once"""
        if not chunks:
            return []
        
        # Prepare data for bulk insert
        bulk_data = []
        chunk_ids = []
        
        for chunk in chunks:
            chunk_id = int(time.time() * 1000000) + len(bulk_data)  # Use timestamp + counter as ID
            chunk_ids.append(chunk_id)
            
            metadata_str = json.dumps(chunk.get('metadata', {})) if chunk.get('metadata') else '{}'
            
            bulk_data.append((
                chunk_id,
                chunk['document_id'],
                chunk['chunk_index'],
                chunk['chunk_text'],
                metadata_str
            ))
        
        # Execute bulk insert
        query = f"""
        INSERT INTO {cls.table_name} (id, document_id, chunk_index, chunk_text, metadata)
        VALUES
        """
        
        cls.execute(query, bulk_data)
        
        # Update chunk count in stats
        VectorDBStats.increment_chunk_count(len(chunks))
        
        return chunk_ids
    
    @classmethod
    def get(cls, chunk_id: int) -> Dict:
        """Get a chunk by ID"""
        query = f"""
        SELECT id, document_id, chunk_index, chunk_text, metadata, created_at
        FROM {cls.table_name}
        WHERE id = %s
        """
        
        result = cls.execute(query, (chunk_id,))
        
        if not result:
            return None
        
        row = result[0]
        return {
            'id': row[0],
            'document_id': row[1],
            'chunk_index': row[2],
            'chunk_text': row[3],
            'metadata': json.loads(row[4]) if row[4] else {},
            'created_at': row[5].isoformat() if row[5] else None
        }
    
    @classmethod
    def get_by_document(cls, document_id: str) -> List[Dict]:
        """Get all chunks for a document"""
        query = f"""
        SELECT id, document_id, chunk_index, chunk_text, metadata, created_at
        FROM {cls.table_name}
        WHERE document_id = %s
        ORDER BY chunk_index
        """
        
        result = cls.execute(query, (document_id,))
        
        chunks = []
        for row in result:
            chunks.append({
                'id': row[0],
                'document_id': row[1],
                'chunk_index': row[2],
                'chunk_text': row[3],
                'metadata': json.loads(row[4]) if row[4] else {},
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return chunks
    
    @classmethod
    def get_by_ids(cls, chunk_ids: List[int]) -> List[Dict]:
        """Get chunks by IDs"""
        if not chunk_ids:
            return []
        
        # Convert to list of strings for the IN clause
        id_strings = [str(id) for id in chunk_ids]
        id_list = ", ".join(id_strings)
        
        query = f"""
        SELECT id, document_id, chunk_index, chunk_text, metadata, created_at
        FROM {cls.table_name}
        WHERE id IN ({id_list})
        """
        
        result = cls.execute(query)
        
        chunks = []
        for row in result:
            chunks.append({
                'id': row[0],
                'document_id': row[1],
                'chunk_index': row[2],
                'chunk_text': row[3],
                'metadata': json.loads(row[4]) if row[4] else {},
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return chunks
    
    @classmethod
    def delete(cls, chunk_id: int) -> bool:
        """Delete a chunk by ID"""
        query = f"""
        DELETE FROM {cls.table_name}
        WHERE id = %s
        """
        
        cls.execute(query, (chunk_id,))
        
        # Update stats
        VectorDBStats.decrement_chunk_count()
        
        return True
    
    @classmethod
    def delete_by_document(cls, document_id: str) -> bool:
        """Delete all chunks for a document"""
        query = f"""
        DELETE FROM {cls.table_name}
        WHERE document_id = %s
        """
        
        cls.execute(query, (document_id,))
        
        return True
    
    @classmethod
    def count_by_document(cls, document_id: str) -> int:
        """Count chunks for a document"""
        query = f"""
        SELECT COUNT(*)
        FROM {cls.table_name}
        WHERE document_id = %s
        """
        
        result = cls.execute(query, (document_id,))
        
        if not result:
            return 0
        
        return result[0][0]
    
    @classmethod
    def search_text(cls, search_term: str, limit: int = 10) -> List[Dict]:
        """Search chunks by text content"""
        query = f"""
        SELECT id, document_id, chunk_index, chunk_text, metadata, created_at
        FROM {cls.table_name}
        WHERE chunk_text LIKE %s
        LIMIT {limit}
        """
        
        search_pattern = f'%{search_term}%'
        result = cls.execute(query, (search_pattern,))
        
        chunks = []
        for row in result:
            chunks.append({
                'id': row[0],
                'document_id': row[1],
                'chunk_index': row[2],
                'chunk_text': row[3],
                'metadata': json.loads(row[4]) if row[4] else {},
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return chunks

class VectorDBStats(BaseModel):
    """Vector database stats model for ClickHouse"""
    
    table_name = 'vector_db_stats'
    fields = [
        'id UInt8',
        'documents_count UInt32 DEFAULT 0',
        'chunks_count UInt32 DEFAULT 0',
        'vector_dim UInt16',
        'last_modified DateTime DEFAULT now()'
    ]
    
    @classmethod
    def initialize(cls, vector_dim: int = 384) -> bool:
        """Initialize stats if they don't exist"""
        query = f"""
        INSERT INTO {cls.table_name} (id, documents_count, chunks_count, vector_dim)
        VALUES (1, 0, 0, {vector_dim})
        """
        
        try:
            cls.execute(query)
            return True
        except Exception as e:
            logger.warning(f"Stats may already exist: {e}")
            return False
    
    @classmethod
    def get(cls) -> Dict:
        """Get database statistics"""
        query = f"""
        SELECT documents_count, chunks_count, vector_dim, last_modified
        FROM {cls.table_name}
        WHERE id = 1
        """
        
        result = cls.execute(query)
        
        if not result:
            # Initialize stats if they don't exist
            cls.initialize()
            result = cls.execute(query)
            
            if not result:
                return {
                    'documents_count': 0,
                    'chunks_count': 0,
                    'vector_dim': 384,
                    'last_modified': datetime.now().isoformat()
                }
        
        row = result[0]
        return {
            'documents_count': row[0],
            'chunks_count': row[1],
            'vector_dim': row[2],
            'last_modified': row[3].isoformat() if row[3] else None
        }
    
    @classmethod
    def increment_document_count(cls, count: int = 1) -> bool:
        """Increment document count"""
        query = f"""
        UPDATE {cls.table_name}
        SET documents_count = documents_count + {count}, last_modified = now()
        WHERE id = 1
        """
        
        cls.execute(query)
        return True
    
    @classmethod
    def decrement_document_count(cls, count: int = 1) -> bool:
        """Decrement document count"""
        query = f"""
        UPDATE {cls.table_name}
        SET documents_count = greatest(documents_count - {count}, 0), last_modified = now()
        WHERE id = 1
        """
        
        cls.execute(query)
        return True
    
    @classmethod
    def increment_chunk_count(cls, count: int = 1) -> bool:
        """Increment chunk count"""
        query = f"""
        UPDATE {cls.table_name}
        SET chunks_count = chunks_count + {count}, last_modified = now()
        WHERE id = 1
        """
        
        cls.execute(query)
        return True
    
    @classmethod
    def decrement_chunk_count(cls, count: int = 1) -> bool:
        """Decrement chunk count"""
        query = f"""
        UPDATE {cls.table_name}
        SET chunks_count = greatest(chunks_count - {count}, 0), last_modified = now()
        WHERE id = 1
        """
        
        cls.execute(query)
        return True

class LLMPrompt(BaseModel):
    """LLM Prompt model for ClickHouse"""
    
    table_name = 'llm_prompts'
    fields = [
        'id String',
        'prompt String',
        'response String',
        'metadata String',
        'user_id String',
        'created_at DateTime DEFAULT now()',
        'response_time Float64'
    ]
    
    @classmethod
    def create(cls, prompt: str, response: str, metadata: Dict = None, user_id: str = None) -> str:
        """Create a new LLM prompt record"""
        prompt_id = str(uuid.uuid4())
        metadata_str = json.dumps(metadata) if metadata else '{}'
        
        query = f"""
        INSERT INTO {cls.table_name} (id, prompt, response, metadata, user_id, response_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Calculate response time if metadata exists and has start/end time
        response_time = 0.0
        if metadata and 'start_time' in metadata and 'end_time' in metadata:
            response_time = metadata['end_time'] - metadata['start_time']
        
        params = (prompt_id, prompt, response, metadata_str, user_id or '', response_time)
        
        try:
            cls.execute(query, params)
            logger.info(f"LLM prompt saved with ID: {prompt_id}")
            return prompt_id
        except Exception as e:
            logger.error(f"Error saving LLM prompt: {e}")
            return None
    
    @classmethod
    def get_recent(cls, limit: int = 10) -> List[Dict]:
        """Get recent LLM prompts"""
        query = f"""
        SELECT id, prompt, response, metadata, user_id, created_at, response_time
        FROM {cls.table_name}
        ORDER BY created_at DESC
        LIMIT {limit}
        """
        
        result = cls.execute(query)
        
        prompts = []
        for row in result:
            prompts.append({
                'id': row[0],
                'prompt': row[1],
                'response': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'user_id': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'response_time': row[6]
            })
        
        return prompts

# Initialize tables when module is imported
def initialize_database():
    """Initialize database schema"""
    try:
        Document.create_table()
        DocumentChunk.create_table()
        VectorDBStats.create_table()
        LLMPrompt.create_table()  # Add LLM Prompts table
        VectorDBStats.initialize()
        logger.info("Database schema initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Initialize database schema
    initialize_database()
    
    # Test creating a document
    doc_id = Document.create(
        name="Test Document",
        description="This is a test document",
        metadata={"test": True}
    )
    
    print(f"Created document with ID: {doc_id}")
    
    # Test creating chunks
    for i in range(3):
        chunk_id = DocumentChunk.create(
            document_id=doc_id,
            chunk_index=i,
            chunk_text=f"This is chunk {i} for document {doc_id}",
            metadata={"index": i}
        )
        print(f"Created chunk with ID: {chunk_id}")
    
    # Test getting document
    doc = Document.get(doc_id)
    print(f"Retrieved document: {doc['name']}")
    
    # Test getting chunks
    chunks = DocumentChunk.get_by_document(doc_id)
    print(f"Retrieved {len(chunks)} chunks")
    
    # Test getting stats
    stats = VectorDBStats.get()
    print(f"Database stats: {stats}")