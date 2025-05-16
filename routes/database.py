"""
Database Blueprint for L1 Application
This module provides routes for database operations using ClickHouse
"""

import logging
from flask import Blueprint, jsonify, request
import mock_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create RAG service instance
rag_service = mock_database.RagService()

# Create blueprint
database_bp = Blueprint('database', __name__, url_prefix='/api/database')

@database_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get all documents from the database"""
    try:
        # Get documents from database
        documents = db_service.db.get_all_documents()
        
        # Return documents
        return jsonify(documents)
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a document by ID"""
    try:
        # Get document from database
        document = db_service.db.get_document(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Return document
        return jsonify(document)
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/documents', methods=['POST'])
def add_document():
    """Add a document to the database"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract document data
        name = data.get('name')
        description = data.get('description', '')
        text = data.get('text', '')
        metadata = data.get('metadata', {})
        
        if not name:
            return jsonify({'error': 'Document name is required'}), 400
        
        if not text:
            return jsonify({'error': 'Document text is required'}), 400
        
        # Add document to database
        document_id = db_service.add_document(name, description, text, metadata)
        
        if not document_id:
            return jsonify({'error': 'Failed to add document'}), 500
        
        # Return document ID
        return jsonify({'document_id': document_id})
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/search', methods=['POST'])
def search():
    """Search for similar documents"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract search data
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Search for similar documents
        results = db_service.search_similar(query, top_k)
        
        # Return search results
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({'error': str(e)}), 500

@database_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        # Get stats from database
        stats = db_service.get_stats()
        
        # Return stats
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500