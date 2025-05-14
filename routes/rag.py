from flask import Blueprint, render_template, request, jsonify
import random
from datetime import datetime, timedelta
import logging

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
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Sample search results
        results = [
            {
                'chunk_id': 'chunk_042',
                'document_id': 'doc_001',
                'document_name': 'network_guide.pdf',
                'text': 'To configure network settings on a Linux system, you need to edit the interface configuration files. On most modern distributions, you can find these in the /etc/netplan/ directory...',
                'relevance_score': 0.92,
                'page_number': 15,
                'metadata': {
                    'section': 'Network Configuration',
                    'author': 'John Doe'
                }
            },
            {
                'chunk_id': 'chunk_156',
                'document_id': 'doc_004',
                'document_name': 'product_documentation.docx',
                'text': 'The product includes advanced network configuration options. Users can modify interface settings through the admin panel by navigating to Settings > Network > Interfaces...',
                'relevance_score': 0.87,
                'page_number': 32,
                'metadata': {
                    'section': 'Administrator Guide',
                    'author': 'Jane Smith'
                }
            },
            {
                'chunk_id': 'chunk_072',
                'document_id': 'doc_001',
                'document_name': 'network_guide.pdf',
                'text': 'Network troubleshooting often begins with checking interface configuration. Use the command "ip a" to list all network interfaces and their status...',
                'relevance_score': 0.83,
                'page_number': 28,
                'metadata': {
                    'section': 'Troubleshooting',
                    'author': 'John Doe'
                }
            }
        ]
        
        return jsonify({
            'query': query,
            'results': results,
            'total_matches': len(results),
            'search_time': 0.048,  # seconds
            'metadata': {
                'embedding_model': 'all-MiniLM-L6-v2',
                'similarity_metric': 'cosine',
                'retrieval_method': 'faiss'
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
        if 'document' not in request.files:
            logger.error("No 'document' field in the request files")
            return jsonify({'error': 'No file part in the request. Make sure the file field is named "document"'}), 400
            
        file = request.files['document']
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
        
        # Return success response
        response_data = {
            'success': True,
            'document_id': f'doc_{random.randint(100, 999)}',
            'name': document_name,
            'path': file_path,
            'intended_remote_path': remote_path,  # This is just for reference, file wasn't actually saved here
            'note': 'File was saved locally. Remote path is not accessible due to filesystem restrictions.',
            'status': 'processing' if index_immediately else 'uploaded'
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
        # Get request parameters
        url = request.json.get('url', '') if request.json else ''
        name = request.json.get('name', '') if request.json else ''
        description = request.json.get('description', '') if request.json else ''
        index_immediately = request.json.get('index_immediately', True) if request.json else True
        ignore_ssl_errors = request.json.get('ignore_ssl_errors', False) if request.json else False
        
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
            
            # Return success response
            return jsonify({
                'success': True,
                'document_id': f'doc_{random.randint(100, 999)}',
                'url': url,
                'name': safe_filename,
                'path': file_path,
                'content_length': len(text_content),
                'status': 'processing' if index_immediately else 'uploaded'
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