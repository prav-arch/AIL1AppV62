import os
import logging
import json
from flask import Flask, jsonify, render_template, request
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key")

# Basic routes for testing
@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Test endpoint working"})

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/llm-assistant')
def llm_assistant():
    return render_template('llm_assistant.html')

@app.route('/rag')
def rag():
    return render_template('rag_new.html')

@app.route('/anomalies')
def anomalies():
    return render_template('anomalies.html')

@app.route('/data-pipeline')
def data_pipeline():
    return render_template('data_pipeline.html')

@app.route('/kafka-browser')
def kafka_browser():
    return render_template('kafka_browser.html')

# API Routes
@app.route('/api/dashboard/metrics', methods=['GET'])
def api_dashboard_metrics():
    """Return dashboard metrics for display"""
    metrics = {
        'llm_requests': random.randint(800, 1200),
        'docs_indexed': random.randint(150, 300),
        'anomalies': random.randint(10, 30),
        'pipelines': random.randint(3, 12),
        'memory_usage': random.randint(60, 85),
        'cpu_load': random.randint(30, 70),
        'disk_usage': random.randint(50, 80),
        'network_throughput': random.randint(20, 60),
        'llm_usage': [random.randint(50, 150) for _ in range(7)],
        'resource_distribution': [
            {'label': 'CPU', 'value': random.randint(20, 40)},
            {'label': 'Memory', 'value': random.randint(15, 35)},
            {'label': 'Storage', 'value': random.randint(10, 25)},
            {'label': 'Network', 'value': random.randint(15, 30)}
        ],
        'gpu_utilization': [random.randint(0, 100) for _ in range(24)]
    }
    return jsonify(metrics)

@app.route('/api/kafka/recent-messages', methods=['GET'])
def api_recent_kafka_messages():
    """Return recent Kafka messages for the dashboard"""
    messages = []
    for i in range(5):
        messages.append({
            'queue': f"queue-{i}",
            'message': f"Test message {i}",
            'time_ago': f"{random.randint(1, 30)}m ago"
        })
    return jsonify({'messages': messages})

@app.route('/api/pipeline/status', methods=['GET'])
def api_pipeline_status():
    """Return pipeline status information"""
    pipelines = [
        {
            'name': 'Data Ingestion',
            'description': 'Processing files',
            'status': 'Running' 
        },
        {
            'name': 'ETL Process',
            'description': 'Transforming data',
            'status': 'Running'
        }
    ]
    return jsonify({'pipelines': pipelines})

@app.route('/api/anomalies/latest', methods=['GET'])
def api_latest_anomalies():
    """Return latest anomalies information"""
    anomalies = [
        {
            'title': 'Network Traffic Spike',
            'description': 'Unusual outbound traffic',
            'details_url': '/anomalies'
        },
        {
            'title': 'Memory Leak',
            'description': 'In application server',
            'details_url': '/anomalies'
        }
    ]
    return jsonify({'anomalies': anomalies})

@app.route('/api/anomalies/stats', methods=['GET'])
def api_anomaly_stats():
    """Return statistics about anomalies"""
    stats = {
        'success': True,
        'total': 24,
        'critical': 5,
        'warning': 12,
        'info': 7,
        'trends': {
            'labels': [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, 0, -1)],
            'datasets': [
                {
                    'label': 'Critical',
                    'data': [random.randint(3, 8) for _ in range(7)]
                },
                {
                    'label': 'Warning',
                    'data': [random.randint(8, 15) for _ in range(7)]
                },
                {
                    'label': 'Info',
                    'data': [random.randint(5, 10) for _ in range(7)]
                }
            ]
        },
        'types': {
            'labels': ['Network', 'System', 'Database', 'Application', 'Security'],
            'data': [random.randint(10, 25) for _ in range(5)]
        }
    }
    return jsonify(stats)

@app.route('/api/anomalies/list', methods=['GET'])
def api_anomalies_list():
    """Return list of anomalies with optional filtering"""
    anomalies = [
        {
            'id': 'A-1283',
            'timestamp': '2023-05-20 14:32:15',
            'type': 'Network',
            'source': 'router-edge-01',
            'description': 'Unusual outbound traffic spike',
            'severity': 'Critical'
        },
        {
            'id': 'A-1282',
            'timestamp': '2023-05-20 13:45:22',
            'type': 'System',
            'source': 'app-server-03',
            'description': 'Memory usage continuously above 92%',
            'severity': 'Warning'
        }
    ]
    return jsonify({
        'success': True,
        'anomalies': anomalies
    })

# RAG API Routes
@app.route('/api/documents', methods=['GET'])
def api_documents():
    """Return list of documents in the knowledge base"""
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

@app.route('/api/vectordb/stats', methods=['GET'])
def api_vectordb_stats():
    """Return vector database statistics"""
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

@app.route('/api/storage/info', methods=['GET'])
def api_storage_info():
    """Return file storage information"""
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

@app.route('/api/rag/search', methods=['POST'])
def api_rag_search():
    """Perform RAG search with the given query"""
    query = request.json.get('query', '')
    
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

@app.route('/api/llm/query', methods=['POST'])
def api_llm_query():
    """Process an LLM query and return the response"""
    from flask import Response, stream_with_context
    import requests
    
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Get agent settings
    settings = data.get('settings', {})
    temperature = settings.get('temperature', 0.7)
    max_tokens = settings.get('max_tokens', 1024)
    
    try:
        # Connect directly to the generate endpoint at localhost:8080
        llm_base_url = "http://localhost:8080"
        
        # Use streaming response directly to the generate endpoint
        def generate():
            try:
                
                # Connect directly to the generate endpoint
                url = f"{llm_base_url}/generate"
                
                # Prepare the request payload
                payload = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": True
                }
                
                # Make the API request with streaming enabled
                with requests.post(
                    url,
                    json=payload,
                    stream=True,
                    timeout=120  # 2-minute timeout
                ) as response:
                    # Check for successful response
                    response.raise_for_status()
                    
                    # Process the streaming response
                    for line in response.iter_lines():
                        if line:
                            # Skip empty lines
                            line = line.decode('utf-8')
                            
                            # Handle SSE format if applicable
                            if line.startswith('data: '):
                                line = line[6:]  # Remove 'data: ' prefix
                            
                            # Skip heartbeat messages
                            if line == '[DONE]':
                                yield "data: [DONE]\n\n"
                                break
                            
                            try:
                                # Try to parse as JSON
                                chunk = json.loads(line)
                                
                                # Extract the text content based on response format
                                text = None
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    # OpenAI-like format
                                    content = chunk["choices"][0].get("text", "") or chunk["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        text = content
                                elif "response" in chunk:
                                    text = chunk["response"]
                                elif "text" in chunk:
                                    text = chunk["text"]
                                elif "generated_text" in chunk:
                                    text = chunk["generated_text"]
                                
                                if text:
                                    yield f"data: {json.dumps({'text': text})}\n\n"
                            except json.JSONDecodeError:
                                # If not JSON, yield the raw line
                                yield f"data: {json.dumps({'text': line})}\n\n"
            except Exception as e:
                logging.error(f"Error in LLM streaming: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)