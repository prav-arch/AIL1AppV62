"""
RAG routes for the AI Assistant Platform.
Handles document uploads, web scraping, and RAG search using FAISS vector database.
"""

from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import logging
import time
from datetime import datetime
import uuid
import json
import requests

# Import database functions
from db import execute_query, add_document, add_document_chunk

# Import vector database service - FAISS instead of PostgreSQL
from services.faiss_vector_db import add_embedding, search_embeddings

# Web scraper module
import trafilatura

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
rag_bp = Blueprint('rag', __name__, url_prefix='/rag')

# Configure upload folder
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'html', 'htm', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@rag_bp.route('/')
def index():
    """RAG main page."""
    # Get document list from database
    documents = get_user_documents()
    
    # Get vector database stats
    vector_stats = postgres_vector_db_service.get_stats()
    
    return render_template(
        'rag.html', 
        documents=documents,
        vector_stats=vector_stats
    )

@rag_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload a document."""
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Get user_id from session, default to 1 if not set
            user_id = session.get('user_id', 1)
            
            # Extract text from file
            file_content = extract_text_from_file(file_path, file.filename)
            
            # Create document in database
            document_id = add_document(
                user_id=user_id,
                title=file.filename,
                description=f"Uploaded on {datetime.now().strftime('%Y-%m-%d')}",
                content=file_content,
                file_path=file_path,
                file_type=file.filename.rsplit('.', 1)[1].lower(),
                file_size=os.path.getsize(file_path),
                source='upload'
            )
            
            # Add document to vector database
            doc_uuid = str(uuid.uuid4())
            metadata = {
                'name': file.filename,
                'source': 'upload',
                'upload_date': datetime.now().isoformat(),
                'file_type': file.filename.rsplit('.', 1)[1].lower(),
                'file_size': os.path.getsize(file_path),
                'db_document_id': document_id
            }
            
            # Process document content and add embeddings
            # Split into chunks and add each chunk to FAISS
            chunks = [file_content[i:i+1000] for i in range(0, len(file_content), 1000)]
            for i, chunk in enumerate(chunks):
                # In a real app, we would generate embeddings here using a model
                # For now, we'll use dummy embeddings of the right dimension
                import numpy as np
                dummy_embedding = np.random.rand(1536).astype('float32') 
                add_embedding(document_id, i, dummy_embedding, chunk)
            
            return jsonify({
                'success': True, 
                'message': 'File uploaded successfully',
                'document_id': document_id,
                'file_name': file.filename
            })
        else:
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/scrape', methods=['POST'])
def scrape_webpage():
    """Scrape a webpage."""
    try:
        # Get URL from request
        data = request.json
        url = data.get('url')
        ignore_ssl = data.get('ignore_ssl', False)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get user_id from session, default to 1 if not set
        user_id = session.get('user_id', 1)
        
        # Scrape the webpage
        try:
            # Configure requests session with SSL verification settings
            req_session = requests.Session()
            req_session.verify = not ignore_ssl
            
            # Fetch webpage content
            downloaded = trafilatura.fetch_url(url, session=req_session)
            
            if not downloaded:
                return jsonify({'error': 'Failed to download webpage content'}), 400
                
            # Extract text content
            content = trafilatura.extract(downloaded)
            
            if not content:
                return jsonify({'error': 'No text content found on the webpage'}), 400
                
            # Create title from URL
            title = url.split('//')[-1].split('/')[0]
            
            # Add to database
            document_id = add_document(
                user_id=user_id,
                title=f"Web: {title}",
                description=f"Scraped from {url} on {datetime.now().strftime('%Y-%m-%d')}",
                content=content,
                file_path=None,
                file_type='web',
                file_size=len(content),
                source='web_scrape',
                source_url=url
            )
            
            # Add to vector database
            doc_uuid = str(uuid.uuid4())
            metadata = {
                'name': f"Web: {title}",
                'source': 'web_scrape',
                'scrape_date': datetime.now().isoformat(),
                'url': url,
                'db_document_id': document_id
            }
            
            postgres_vector_db_service.add_document(doc_uuid, content, metadata)
            
            return jsonify({
                'success': True, 
                'message': 'Webpage scraped successfully',
                'document_id': document_id,
                'url': url
            })
            
        except Exception as e:
            error_message = str(e)
            # Check for common HTTP errors
            if 'status code 404' in error_message:
                return jsonify({'error': 'Webpage not found (404)'}), 404
            elif 'status code 403' in error_message:
                return jsonify({'error': 'Access forbidden (403)'}), 403
            elif 'certificate verify failed' in error_message:
                return jsonify({
                    'error': 'SSL certificate verification failed. Try with "Ignore SSL" option.',
                    'ssl_error': True
                }), 400
            else:
                raise
            
    except Exception as e:
        logger.error(f"Error scraping webpage: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/search', methods=['POST'])
def search():
    """Search the vector database."""
    try:
        # Get query from request
        data = request.json
        query = data.get('query')
        top_k = data.get('top_k', 3)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Perform search using vector database
        start_time = time.time()
        results = postgres_vector_db_service.search(query, top_k)
        search_time = time.time() - start_time
        
        # Get user_id from session, default to 1 if not set
        user_id = session.get('user_id', 1)
        
        # Log the search in the database
        execute_query("""
            INSERT INTO rag_searches (user_id, query, top_k, search_time)
            VALUES (%s, %s, %s, %s)
        """, (user_id, query, top_k, search_time), fetch=False)
        
        return jsonify({
            'results': results,
            'search_time': search_time
        })
        
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get list of documents."""
    documents = get_user_documents()
    return jsonify({'documents': documents})

@rag_bp.route('/document/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document."""
    try:
        # Get user_id from session, default to 1 if not set
        user_id = session.get('user_id', 1)
        
        # Get document from database
        document = execute_query("""
            SELECT * FROM documents WHERE id = %s
        """, (document_id,))
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Get document chunks
        chunks = execute_query("""
            SELECT * FROM document_chunks 
            WHERE document_id = %s
            ORDER BY chunk_index
        """, (document_id,))
        
        document = document[0]
        document['chunks'] = chunks if chunks else []
        
        return jsonify({'document': document})
        
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_user_documents(limit=100):
    """Get documents for a user."""
    # Get user_id from session, default to 1 if not set
    user_id = session.get('user_id', 1)
    
    try:
        documents = execute_query("""
            SELECT id, title, description, file_path, file_type, file_size, source, source_url, created_at
            FROM documents
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        return documents if documents else []
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        return []

def extract_text_from_file(file_path, file_name):
    """Extract text content from file."""
    # For now, handle only text files
    # In a complete implementation, this would use libraries for PDF, DOCX, etc.
    ext = file_name.rsplit('.', 1)[1].lower()
    
    if ext == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        # For now, return a placeholder for other file types
        return f"Text extraction not implemented for {ext} files yet."