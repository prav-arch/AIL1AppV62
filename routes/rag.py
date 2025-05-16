from flask import Blueprint, render_template, request, jsonify
import random
import time
from datetime import datetime, timedelta
import logging
import os

# Import vector database service
# Using ClickHouse vector database service
from services.clickhouse_vector_db import clickhouse_vector_db_service as vector_db_service

# Set up logger
logger = logging.getLogger(__name__)

rag_bp = Blueprint('rag', __name__, url_prefix='/rag')

@rag_bp.route('/')
def index():
    response = render_template('rag.html')
    # Set headers to prevent caching
    return response, 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
@rag_bp.route('/api/upload-test', methods=['GET'])
def test_upload():
    """A simple test endpoint to verify that the upload directory can be created and written to"""
    import os
    import tempfile
    
    # Local directory that should always be writable
    local_dir = os.path.join(os.getcwd(), 'uploads')
    # Remote directory that may not be writable
    remote_dir = '/home/users/praveen.joe/uploads'
    
    # Test results
    results = {
        'local': {
            'directory': local_dir,
            'exists': os.path.exists(local_dir),
            'is_dir': os.path.isdir(local_dir) if os.path.exists(local_dir) else False,
            'writable': os.access(local_dir, os.W_OK) if os.path.exists(local_dir) else False,
            'test_file_created': False
        },
        'remote': {
            'directory': remote_dir,
            'exists': os.path.exists(remote_dir),
            'is_dir': os.path.isdir(remote_dir) if os.path.exists(remote_dir) else False,
            'writable': os.access(remote_dir, os.W_OK) if os.path.exists(remote_dir) else False,
            'test_file_created': False
        }
    }
    
    # Try to create directories
    try:
        os.makedirs(local_dir, exist_ok=True)
        results['local']['directory_created'] = True
    except Exception as e:
        results['local']['directory_error'] = str(e)
    
    try:
        os.makedirs(remote_dir, exist_ok=True)
        results['remote']['directory_created'] = True
    except Exception as e:
        results['remote']['directory_error'] = str(e)
    
    # Try to write test files
    try:
        test_file_path = os.path.join(local_dir, 'test_upload.txt')
        with open(test_file_path, 'w') as f:
            f.write('Test file content')
        results['local']['test_file_created'] = True
        results['local']['test_file_path'] = test_file_path
    except Exception as e:
        results['local']['test_file_error'] = str(e)
    
    try:
        test_file_path = os.path.join(remote_dir, 'test_upload.txt')
        with open(test_file_path, 'w') as f:
            f.write('Test file content')
        results['remote']['test_file_created'] = True
        results['remote']['test_file_path'] = test_file_path
    except Exception as e:
        results['remote']['test_file_error'] = str(e)
    
    return jsonify(results)

@rag_bp.route('/api/documents', methods=['GET'])
def get_documents():
    """Return list of documents in the knowledge base"""
    try:
        # Sample document data
        documents = [
            {
                'id': 'doc_001',
                'name': 'network_guide.pdf',
                'type': 'PDF',
                'size': '1.2 MB',
                'date_added': '2023-05-20',
                'status': 'indexed',
                'chunks': 45,
                'category': 'Technical'
            },
            {
                'id': 'doc_002',
                'name': 'financial_report.xlsx',
                'type': 'Excel',
                'size': '0.8 MB',
                'date_added': '2023-05-18',
                'status': 'indexed',
                'chunks': 32,
                'category': 'Finance'
            },
            {
                'id': 'doc_003',
                'name': 'network_capture.pcap',
                'type': 'PCAP',
                'size': '5.6 MB',
                'date_added': '2023-05-15',
                'status': 'processing',
                'chunks': 0,
                'category': 'Technical'
            },
            {
                'id': 'doc_004',
                'name': 'product_documentation.docx',
                'type': 'Word',
                'size': '3.1 MB',
                'date_added': '2023-05-12',
                'status': 'indexed',
                'chunks': 56,
                'category': 'Product'
            },
            {
                'id': 'doc_005',
                'name': 'ai_research_paper.pdf',
                'type': 'PDF',
                'size': '2.3 MB',
                'date_added': '2023-05-10',
                'status': 'indexed',
                'chunks': 37,
                'category': 'Research'
            }
        ]
        
        return jsonify(documents)
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/api/vectordb/stats', methods=['GET'])
def get_vectordb_stats():
    """Return vector database statistics"""
    try:
        # Sample vector database statistics
        stats = {
            'total_chunks': 1245,
            'vector_dimension': 384,
            'index_size': '8.5 MB',
            'embedding_model': 'all-MiniLM-L6-v2',
            'index_type': 'HNSW',
            'recent_queries': [
                {
                    'query': 'How to configure network settings',
                    'time': '12:45:32',
                    'matches': 3,
                    'latency': 45
                },
                {
                    'query': 'Troubleshoot CPU performance issues',
                    'time': '12:42:18',
                    'matches': 5,
                    'latency': 62
                },
                {
                    'query': 'Financial report summary 2023',
                    'time': '12:35:56',
                    'matches': 4,
                    'latency': 38
                }
            ],
            'performance': {
                'average_query_time': 48,
                'index_build_time': 320,
                'memory_usage': '125 MB'
            },
            'monthly_stats': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'documents': [25, 37, 52, 68, 85],
                'chunks': [320, 480, 670, 820, 1245],
                'queries': [120, 180, 250, 310, 390]
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting vector database stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/api/storage/info', methods=['GET'])
def get_storage_info():
    """Return file storage information"""
    try:
        # Sample storage information
        storage_info = {
            'total_space': '1 TB',
            'used_space': '243.5 GB',
            'buckets': [
                {
                    'name': 'documents',
                    'size': '156.2 GB',
                    'files': 145
                },
                {
                    'name': 'embeddings',
                    'size': '45.8 GB',
                    'files': 32
                },
                {
                    'name': 'images',
                    'size': '28.5 GB',
                    'files': 214
                },
                {
                    'name': 'backups',
                    'size': '13.0 GB',
                    'files': 18
                }
            ],
            'file_types': {
                'labels': ['PDF', 'Word', 'Excel', 'Images', 'Text', 'Other'],
                'values': [35, 22, 15, 12, 10, 6]
            }
        }
        
        return jsonify(storage_info)
    except Exception as e:
        logger.error(f"Error getting storage info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/api/rag/search', methods=['POST'])
def search_rag():
    """Perform RAG search with the given query"""
    try:
        query = request.json.get('query', '') if request.json else ''
        top_k = request.json.get('top_k', 3) if request.json else 3
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Record start time for performance measurement
        start_time = time.time()
        
        # Perform vector search using FAISS
        search_results = vector_db_service.search(query, top_k=top_k)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # If we have no documents in the vector db yet, provide sample results
        if not search_results:
            # Get stats to check if we have any documents
            stats = vector_db_service.get_stats()
            if stats.get('documents_count', 0) == 0:
                logger.warning("No documents in vector database, returning sample results")
                # Sample search results for empty database
                results = [
                    {
                        'chunk_id': 'sample_chunk_1',
                        'document_id': 'sample_doc_1',
                        'document_name': 'Sample Document',
                        'text': 'This is a sample result. Please add documents to the vector database to get real search results.',
                        'relevance_score': 0.95,
                        'metadata': {
                            'note': 'Sample data'
                        }
                    }
                ]
                
                return jsonify({
                    'query': query,
                    'results': results,
                    'total_matches': len(results),
                    'search_time': search_time,
                    'note': 'No documents have been added to the vector database yet. These are sample results.',
                    'metadata': {
                        'embedding_model': 'pgvector',
                        'similarity_metric': 'L2',
                        'retrieval_method': 'postgresql'
                    }
                })
        
        # Format the real search results
        results = []
        
        # Safely get documents, with fallback for None
        documents = vector_db_service.get_documents() or {}
        
        for result in search_results:
            if not result:
                continue
                
            doc_id = result.get('document_id', '')
            if not doc_id:
                continue
                
            if doc_id in documents:
                doc_metadata = documents[doc_id] or {}
                doc_name = doc_metadata.get('name', doc_id)
                
                # Try to read a snippet of text from the document
                text_snippet = "Content not available"
                file_path = doc_metadata.get('file_path', '')
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            # Read first 300 characters as a preview
                            text_snippet = f.read(300) + '...'
                    except Exception as e:
                        logger.error(f"Error reading file for search result: {str(e)}")
                
                # Get the score with a fallback
                score = 0
                try:
                    score = float(result.get('score', 0))
                except (ValueError, TypeError):
                    pass
                
                # Normalize score to a 0-1 range for display
                relevance_score = max(0.0, min(1.0, 1.0 - (score / 10)))
                
                results.append({
                    'chunk_id': f"{doc_id}_chunk_{result.get('chunk_id', 0)}",
                    'document_id': doc_id,
                    'document_name': doc_name,
                    'text': text_snippet if text_snippet else "Content not available",
                    'relevance_score': relevance_score,
                    'metadata': doc_metadata
                })
        
        return jsonify({
            'query': query,
            'results': results,
            'total_matches': len(results),
            'search_time': search_time,
            'metadata': {
                'embedding_model': 'pgvector',
                'similarity_metric': 'L2',
                'retrieval_method': 'postgresql'
            }
        })
    except Exception as e:
        logger.error(f"Error performing RAG search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/api/documents/upload', methods=['POST'])
@rag_bp.route('/api/upload-document', methods=['POST'])  # Added alternate route to match frontend
def upload_document():
    """Upload a document to the RAG system"""
    import os
    import traceback
    from werkzeug.utils import secure_filename
    
    # Create a local directory that we can definitely write to
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    # The remote directory can't be created because of filesystem restrictions
    # So we'll record it for reference but only save to the local directory
    remote_dir = '/home/users/praveen.joe/uploads'  # This is just for reference
    
    # Log request details for debugging
    logger.info(f"====== Upload document request received ======")
    logger.info(f"Request form data keys: {list(request.form.keys())}")
    logger.info(f"Request files keys: {list(request.files.keys())}")
    for key in request.files:
        file_obj = request.files[key]
        logger.info(f"File '{key}': {file_obj.filename}, {file_obj.content_type}, {file_obj.content_length}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"=======================================")
    
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"Ensuring upload directory exists: {upload_dir}")
        
        # Check for file in request
        file_key = None
        
        # First try with 'document' key as expected
        if 'document' in request.files:
            file_key = 'document'
        else:
            # Otherwise, check if there's any file field, regardless of its name
            for key in request.files:
                if key or 'file' in key.lower() or 'document' in key.lower():
                    file_key = key
                    logger.info(f"Found alternative file field name: {key}")
                    break
                    
            # If we still don't have a file key but there are files, use the first one
            if not file_key and len(request.files) > 0:
                file_key = list(request.files.keys())[0]
                logger.info(f"Using first available file key: {file_key}")
        
        if not file_key:
            logger.error("No file field found in the request files")
            return jsonify({'error': 'No file part in the request'}), 400
            
        file = request.files[file_key]
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file selected for uploading'}), 400
            
        # Get form data
        document_name = request.form.get('name', file.filename) 
        description = request.form.get('description', '')
        index_immediately = request.form.get('index_immediately', 'false') == 'true'
        
        logger.info(f"Document name: {document_name}, Index immediately: {index_immediately}")
        
        # Make sure the filename is secure
        if not file.filename:
            return jsonify({'error': 'Filename cannot be empty'}), 400
            
        # At this point we know file.filename is a valid string
        filename = secure_filename(str(file.filename))
        file_path = os.path.join(upload_dir, filename)
        # Also log the intended remote path even though we may not be able to write to it
        remote_path = os.path.join(remote_dir, filename)
        
        logger.info(f"Saving file to: {file_path}")
        # Save the file
        file.save(file_path)
        logger.info(f"File saved successfully to {file_path}")
        
        # We can't write to the remote path because of filesystem restrictions
        logger.warning(f"Cannot save to remote path {remote_path} due to filesystem restrictions. " +
                      f"File is saved locally at {file_path} instead.")
        
        # Generate a unique document ID
        doc_id = f'doc_{random.randint(100, 999)}'
        
        # Add to vector database if index_immediately is True
        indexed = False
        if index_immediately:
            try:
                logger.info(f"Indexing document {doc_id} in vector database")
                # Read the file content with error handling for various encodings
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    logger.warning(f"UTF-8 decoding failed for {file_path}, trying with latin-1")
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                
                # Add document metadata
                doc_metadata = {
                    'name': document_name,
                    'description': description,
                    'file_path': file_path,
                    'file_type': file.content_type,
                    'file_size': os.path.getsize(file_path),
                    'upload_date': datetime.now().isoformat()
                }
                
                # Add to vector database
                indexed = vector_db_service.add_document(doc_id, content, doc_metadata)
                
                if indexed:
                    logger.info(f"Document {doc_id} added to vector database successfully")
                else:
                    logger.warning(f"Failed to add document {doc_id} to vector database")
            except Exception as index_error:
                logger.error(f"Error indexing document: {str(index_error)}")
                # Continue even if indexing fails, as we've already saved the file
        
        # Return success response
        response_data = {
            'success': True,
            'document_id': doc_id,
            'name': document_name,
            'path': file_path,
            'intended_remote_path': remote_path,  # This is just for reference, file wasn't actually saved here
            'note': 'File was saved locally. Remote path is not accessible due to filesystem restrictions.',
            'status': 'indexed' if indexed else ('processing' if index_immediately else 'uploaded'),
            'indexed': indexed
        }
        logger.info(f"Returning success response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error uploading document: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        return jsonify({'error': str(e), 'traceback': error_details}), 500

@rag_bp.route('/api/documents/scrape', methods=['POST'])
def scrape_webpage():
    """Scrape a webpage and add it to the RAG system"""
    from trafilatura import fetch_url, extract
    import requests
    from urllib.parse import urlparse
    import os
    from werkzeug.utils import secure_filename
    
    try:
        # Log the request to debug
        logger.info(f"====== Scrape webpage request received ======")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request form data: {request.form}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"=======================================")
        
        # Use request.form for form data instead of request.json
        if request.is_json:
            data = request.json
            logger.info(f"Processing JSON data: {data}")
        else:
            data = request.form
            logger.info(f"Processing form data: {data}")
        
        # Initialize default values
        url = ''
        name = ''
        description = ''
        index_immediately = True
        ignore_ssl_errors = False
        
        # Get request parameters from either form or json
        if data:
            url = data.get('url', '')
            name = data.get('name', '')
            description = data.get('description', '')
            index_immediately_val = data.get('index_immediately')
            if index_immediately_val is not None:
                if isinstance(index_immediately_val, str):
                    index_immediately = index_immediately_val.lower() == 'true'
                else:
                    index_immediately = bool(index_immediately_val)
                    
            ignore_ssl_val = data.get('ignore_ssl_errors')
            if ignore_ssl_val is not None:
                if isinstance(ignore_ssl_val, str):
                    ignore_ssl_errors = ignore_ssl_val.lower() == 'true'
                else:
                    ignore_ssl_errors = bool(ignore_ssl_val)
        
        logger.info(f"Scraping webpage: {url}, ignore_ssl: {ignore_ssl_errors}")
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return jsonify({'error': 'Invalid URL format. Please include http:// or https://'}), 400
        except Exception as url_error:
            logger.error(f"URL parsing error: {str(url_error)}")
            return jsonify({'error': f'Invalid URL: {str(url_error)}'}), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate default name if not provided
        if not name:
            domain = parsed_url.netloc
            path = parsed_url.path.strip('/')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            if path:
                path = path.replace('/', '_')
                name = f"{domain}_{path}_{timestamp}"
            else:
                name = f"{domain}_{timestamp}"
        
        # Log SSL verification status
        if ignore_ssl_errors:
            logger.info("Ignoring SSL certificate verification")
        
        # Try to fetch webpage content
        try:
            # Set up SSL verification for requests
            ssl_verify = not ignore_ssl_errors
            
            # For trafilatura, we don't use the SSL verification directly
            # as it doesn't accept this parameter
            logger.info(f"Fetching URL with trafilatura: {url}")
            try:
                # Import requests and temporarily modify its SSL verification behavior
                import urllib3
                if ignore_ssl_errors:
                    # Disable SSL warnings when verification is disabled
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    
                # Try with trafilatura (which doesn't have a verify param)
                downloaded = fetch_url(url)
            except Exception as trafilatura_error:
                logger.warning(f"Trafilatura error: {str(trafilatura_error)}")
                downloaded = None
            
            if not downloaded:
                # If trafilatura fails, try with requests
                logger.info(f"Trafilatura failed, trying with requests: {url}")
                response = requests.get(url, verify=ssl_verify, timeout=10)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                downloaded = response.text
            
            # Extract main content
            text_content = extract(downloaded)
            
            if not text_content:
                logger.warning(f"No text content extracted from {url}")
                text_content = downloaded  # Use the raw HTML if extraction fails
            
            # Save the content to a file
            safe_filename = secure_filename(name)
            if not safe_filename.endswith('.txt'):
                safe_filename += '.txt'
                
            file_path = os.path.join(upload_dir, safe_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"Webpage content saved to {file_path}")
            
            # Generate a unique document ID
            doc_id = f'doc_{random.randint(100, 999)}'
            
            # Add to vector database if index_immediately is True
            indexed = False
            if index_immediately:
                try:
                    logger.info(f"Indexing scraped document {doc_id} in vector database")
                    
                    # Add document metadata
                    doc_metadata = {
                        'name': safe_filename,
                        'description': f"Scraped from {url}",
                        'file_path': file_path,
                        'url': url,
                        'content_length': len(text_content),
                        'scraped_date': datetime.now().isoformat(),
                        'content_type': 'text/plain',
                        'source': 'web_scraper'
                    }
                    
                    # Add to vector database
                    indexed = vector_db_service.add_document(doc_id, text_content, doc_metadata)
                    
                    if indexed:
                        logger.info(f"Scraped document {doc_id} added to vector database successfully")
                    else:
                        logger.warning(f"Failed to add scraped document {doc_id} to vector database")
                except Exception as index_error:
                    logger.error(f"Error indexing scraped document: {str(index_error)}")
                    # Continue even if indexing fails, as we've already saved the file
            
            # Return success response
            return jsonify({
                'success': True,
                'document_id': doc_id,
                'url': url,
                'name': safe_filename,
                'path': file_path,
                'content_length': len(text_content),
                'status': 'indexed' if indexed else ('processing' if index_immediately else 'uploaded'),
                'indexed': indexed
            })
            
        except requests.exceptions.SSLError as ssl_error:
            logger.error(f"SSL Error scraping {url}: {str(ssl_error)}")
            return jsonify({
                'success': False,
                'error': f'SSL Certificate Error: {str(ssl_error)}. Try enabling "Ignore SSL certificate errors" option.'
            }), 400
            
        except requests.exceptions.ConnectionError as conn_error:
            logger.error(f"Connection Error for {url}: {str(conn_error)}")
            return jsonify({
                'success': False,
                'error': f'Connection Error: Could not connect to {parsed_url.netloc}. The site may be down or blocking requests.'
            }), 400
            
        except requests.exceptions.Timeout as timeout_error:
            logger.error(f"Timeout Error for {url}: {str(timeout_error)}")
            return jsonify({
                'success': False,
                'error': 'The request timed out. The website took too long to respond.'
            }), 408
            
        except requests.exceptions.HTTPError as http_error:
            status_code = http_error.response.status_code if hasattr(http_error, 'response') else 0
            logger.error(f"HTTP Error {status_code} for {url}: {str(http_error)}")
            
            if status_code == 403:
                error_msg = 'Access Denied (403 Forbidden). The website blocked our request.'
            elif status_code == 404:
                error_msg = 'Page Not Found (404). The requested URL does not exist.'
            elif status_code == 429:
                error_msg = 'Too Many Requests (429). The website is rate limiting our access.'
            else:
                error_msg = f'HTTP Error {status_code}: {str(http_error)}'
                
            return jsonify({
                'success': False,
                'error': error_msg
            }), status_code if status_code else 400
            
    except Exception as e:
        logger.error(f"Error scraping webpage: {str(e)}")
        logger.exception("Exception traceback:")
        return jsonify({'success': False, 'error': str(e)}), 500