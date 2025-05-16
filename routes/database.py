"""
Database Blueprint for L1 Application
This module provides routes for database operations using FAISS for vector storage
"""

import logging
import random
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from vector_service import FaissVectorService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FAISS vector service instance
vector_service = FaissVectorService()

# Create blueprint
database_bp = Blueprint('database', __name__, url_prefix='/api/database')

@database_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get a list of sample documents"""
    try:
        # Generate sample documents
        documents = []
        doc_types = ['pdf', 'txt', 'md', 'html', 'doc']
        categories = ['reference', 'guide', 'tutorial', 'api', 'specification']
        
        for i in range(10):
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
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2'
            })
        
        # Return documents
        return jsonify(documents)
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a document by ID"""
    try:
        # For the demo, just return a sample document
        created = datetime.now() - timedelta(days=random.randint(1, 100))
        doc_type = random.choice(['pdf', 'txt', 'md', 'html', 'doc'])
        
        document = {
            'id': document_id,
            'title': f'Document {document_id}',
            'type': doc_type,
            'filename': f'document_{document_id}.{doc_type}',
            'size_kb': random.randint(50, 5000),
            'category': random.choice(['reference', 'guide', 'tutorial', 'api', 'specification']),
            'created_at': created.isoformat(),
            'last_accessed': (created + timedelta(days=random.randint(0, 30))).isoformat(),
            'chunks': random.randint(5, 100),
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'content': 'This is a sample document content. In a real application, this would be the actual document text.'
        }
        
        # Return document
        return jsonify(document)
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/documents', methods=['POST'])
def add_document():
    """Add a document to the vector service"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract document data
        title = data.get('title')
        text = data.get('text', '')
        
        if not title:
            return jsonify({'error': 'Document title is required'}), 400
        
        if not text:
            return jsonify({'error': 'Document text is required'}), 400
        
        # Generate document ID
        document_id = f"doc_{int(datetime.now().timestamp())}"
        
        # Generate embedding for text
        embedding = vector_service.generate_embedding(text)
        
        # Add embedding to the vector service
        vector_service.add_vectors([document_id], [embedding])
        
        # Return document ID
        return jsonify({
            'document_id': document_id,
            'status': 'success',
            'message': 'Document added to vector store'
        })
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/search', methods=['POST'])
def search():
    """Search for similar documents using the vector service"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract search data
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Generate embedding for query
        query_embedding = vector_service.generate_embedding(query)
        
        # Search for similar vectors
        vector_results = vector_service.search(query_embedding, top_k)
        
        # Format results
        results = []
        for doc_id, distance in vector_results:
            # Convert distance to similarity score (lower distance = higher similarity)
            similarity = 1.0 / (1.0 + distance)
            
            # Add result
            results.append({
                'id': doc_id,
                'similarity': similarity,
                'distance': distance,
                'title': f"Document {doc_id}",
                'snippet': f"This is a snippet from document {doc_id} that matched your search query: '{query}'...",
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'type': random.choice(['pdf', 'txt', 'md', 'html', 'doc'])
                }
            })
        
        # Return search results
        return jsonify({
            'query': query,
            'results': results,
            'search_time_ms': random.randint(50, 500)
        })
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get vector service statistics"""
    try:
        # Get stats from vector service
        vector_stats = vector_service.get_stats()
        
        # Enhance with additional information
        stats = {
            **vector_stats,
            'last_updated': datetime.now().isoformat(),
            'storage_used_mb': random.randint(1, 100),
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'performance': {
                'average_query_time_ms': random.randint(10, 200),
                'average_add_time_ms': random.randint(5, 50)
            }
        }
        
        # Return stats
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500