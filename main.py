import os
import logging
import json
from flask import Flask, jsonify, render_template, request, Response
import random
from datetime import datetime, timedelta
import time
import requests
from flask import stream_with_context

# Import the blueprints
from routes.local_llm import local_llm_bp
from routes.rag import rag_bp

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key")

# Disable template caching during development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Register the blueprints
app.register_blueprint(local_llm_bp)
app.register_blueprint(rag_bp)

# Basic routes for testing
@app.route('/test')
def test():
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'timestamp': datetime.now().isoformat()
    })

# Main dashboard page
@app.route('/')
def index():
    return render_template('dashboard.html')

# LLM Assistant page
@app.route('/llm-assistant')
def llm_assistant():
    return render_template('llm_assistant.html')

# RAG page - using blueprint now
# @app.route('/rag')
# def rag():
#     return render_template('rag.html')

# Anomalies page
@app.route('/anomalies')
def anomalies():
    return render_template('anomalies.html')

# Data Pipeline page
@app.route('/data-pipeline')
def data_pipeline():
    return render_template('data_pipeline.html')

# Kafka Browser page
@app.route('/kafka-browser')
def kafka_browser():
    return render_template('kafka_browser.html')

# API routes for dashboard metrics
@app.route('/api/dashboard/metrics', methods=['GET'])
def api_dashboard_metrics():
    """Return dashboard metrics for display"""
    return jsonify({
        'total_documents': random.randint(50, 200),
        'active_pipelines': random.randint(5, 15),
        'kafka_topics': random.randint(10, 30),
        'anomalies_detected': random.randint(0, 20),
        'system_health': random.choice(['good', 'excellent', 'fair']),
        'llm_queries_today': random.randint(100, 500),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/dashboard/kafka-messages', methods=['GET'])
def api_recent_kafka_messages():
    """Return recent Kafka messages for the dashboard"""
    messages = []
    topics = ['logs', 'metrics', 'alerts', 'transactions', 'events']
    
    for _ in range(5):
        messages.append({
            'topic': random.choice(topics),
            'partition': random.randint(0, 3),
            'offset': random.randint(1000, 9999),
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
            'size': random.randint(200, 1500),
            'key': f'key-{random.randint(1, 100)}'
        })
    
    return jsonify(messages)

@app.route('/api/dashboard/pipeline-status', methods=['GET'])
def api_pipeline_status():
    """Return pipeline status information"""
    pipelines = []
    statuses = ['running', 'completed', 'failed', 'scheduled', 'paused']
    
    for i in range(1, 6):
        pipelines.append({
            'id': f'pipeline-{i}',
            'name': f'Data Pipeline {i}',
            'status': random.choice(statuses),
            'last_run': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
            'next_run': (datetime.now() + timedelta(hours=random.randint(1, 12))).isoformat() if random.choice([True, False]) else None,
            'success_rate': random.randint(70, 100)
        })
    
    return jsonify(pipelines)

@app.route('/api/dashboard/latest-anomalies', methods=['GET'])
def api_latest_anomalies():
    """Return latest anomalies information"""
    anomalies = []
    types = ['spike', 'dip', 'trend_change', 'outlier', 'pattern_break']
    services = ['api', 'database', 'auth', 'payment', 'storage', 'compute']
    
    for i in range(5):
        anomalies.append({
            'id': f'anomaly-{i+1}',
            'type': random.choice(types),
            'service': random.choice(services),
            'severity': random.choice(['low', 'medium', 'high']),
            'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat(),
            'description': f'Detected {random.choice(types)} in {random.choice(services)} service metrics',
            'is_resolved': random.choice([True, False])
        })
    
    return jsonify(anomalies)

@app.route('/api/anomalies/stats', methods=['GET'])
def api_anomaly_stats():
    """Return statistics about anomalies"""
    return jsonify({
        'total_anomalies': random.randint(50, 200),
        'open_anomalies': random.randint(5, 30),
        'closed_last_week': random.randint(10, 50),
        'severity_distribution': {
            'low': random.randint(20, 40),
            'medium': random.randint(30, 60),
            'high': random.randint(10, 30),
            'critical': random.randint(0, 15)
        },
        'type_distribution': {
            'spike': random.randint(20, 50),
            'dip': random.randint(15, 40),
            'trend_change': random.randint(10, 30),
            'outlier': random.randint(5, 20),
            'pattern_break': random.randint(10, 25)
        }
    })

@app.route('/api/anomalies/list', methods=['GET'])
def api_anomalies_list():
    """Return list of anomalies with optional filtering"""
    anomalies = []
    types = ['spike', 'dip', 'trend_change', 'outlier', 'pattern_break']
    services = ['api', 'database', 'auth', 'payment', 'storage', 'compute']
    
    # Generate random anomalies for demonstration
    for i in range(20):
        anomaly_type = random.choice(types)
        severity = random.choice(['low', 'medium', 'high', 'critical'])
        service = random.choice(services)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30), 
                                            hours=random.randint(0, 23), 
                                            minutes=random.randint(0, 59))
        
        anomalies.append({
            'id': f'anomaly-{i+100}',
            'type': anomaly_type,
            'service': service,
            'severity': severity,
            'timestamp': timestamp.isoformat(),
            'description': f'Detected {anomaly_type} in {service} service metrics',
            'is_resolved': random.choice([True, False]),
            'resolution_time': random.randint(5, 240) if random.choice([True, False]) else None,
            'metric_name': f'{service}.{random.choice(["cpu", "memory", "latency", "errors", "throughput"])}',
            'metric_value': round(random.uniform(0.1, 99.9), 2),
            'baseline': round(random.uniform(10, 90), 2)
        })
    
    return jsonify(anomalies)

@app.route('/api/rag/documents', methods=['GET'])
def api_documents():
    """Return list of documents in the knowledge base"""
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
            'embedding_model': random.choice(['openai-ada-002', 'text-embedding-3-small', 'local-minilm'])
        })
    
    return jsonify(documents)

@app.route('/api/rag/stats', methods=['GET'])
def api_vectordb_stats():
    """Return vector database statistics"""
    return jsonify({
        'total_documents': random.randint(50, 200),
        'total_chunks': random.randint(500, 5000),
        'total_tokens': random.randint(100000, 1000000),
        'embedding_dimensions': random.choice([384, 768, 1024, 1536]),
        'index_type': 'FAISS',
        'last_updated': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
        'storage_used_mb': random.randint(50, 500),
        'models': {
            'embedding': random.choice(['openai-ada-002', 'text-embedding-3-small', 'local-minilm']),
            'retrieval': 'hybrid'
        }
    })

@app.route('/api/rag/storage', methods=['GET'])
def api_storage_info():
    """Return file storage information"""
    return jsonify({
        'total_storage_mb': 1000,
        'used_storage_mb': random.randint(100, 800),
        'file_counts': {
            'pdf': random.randint(10, 50),
            'txt': random.randint(20, 100),
            'md': random.randint(5, 30),
            'html': random.randint(15, 60),
            'doc': random.randint(0, 20)
        },
        'largest_file_mb': random.randint(10, 50),
        'smallest_file_kb': random.randint(1, 100),
        'average_file_size_mb': round(random.uniform(0.5, 5.0), 2)
    })

@app.route('/api/rag/search', methods=['POST'])
def api_rag_search():
    """Perform RAG search with the given query"""
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    query = data.get('query')
    num_results = data.get('num_results', 3)
    
    # Simulated search results
    results = []
    for i in range(num_results):
        results.append({
            'doc_id': f'doc-{random.randint(100, 999)}',
            'title': f'Sample Document {i+1}',
            'snippet': f'This is a relevant snippet from document {i+1} that matches the query: "{query}"...',
            'relevance_score': round(random.uniform(0.70, 0.99), 4),
            'document_type': random.choice(['pdf', 'txt', 'md', 'html']),
            'metadata': {
                'author': f'Author {random.randint(1, 10)}',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'category': random.choice(['reference', 'guide', 'tutorial', 'api', 'specification'])
            }
        })
    
    return jsonify({
        'query': query,
        'results': results,
        'search_time_ms': random.randint(50, 500),
        'total_docs_searched': random.randint(50, 200)
    })

# LLM API route
@app.route('/api/llm/query', methods=['POST'])
def api_llm_query():
    """Process an LLM query and return the response"""
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Get agent settings
    settings = data.get('settings', {})
    temperature = settings.get('temperature', 0.7)
    max_tokens = settings.get('max_tokens', 1024)
    
    # Use streaming response to the local LLM endpoint
    try:
        # Create system prompt based on agent type
        agent_type = data.get('agent_type', 'general')
        
        if agent_type == 'general':
            system_prompt = "You are a helpful, friendly assistant that provides accurate and concise information."
        elif agent_type == 'coding':
            system_prompt = "You are a coding expert that helps with programming problems, explains code, and suggests best practices."
        elif agent_type == 'data':
            system_prompt = "You are a data analysis expert that helps with statistics, data visualization, and data science concepts."
        else:
            system_prompt = "You are a helpful assistant that provides accurate and useful information."
            
        # Handle RAG if enabled
        use_rag = data.get('use_rag', False)
        if use_rag:
            # This is a placeholder for actual RAG implementation
            system_prompt += "\n\n[Relevant information from knowledge base would be added here]"
        
        def generate():
            try:
                # Make request to the local LLM API
                response = requests.post(
                    'http://localhost:15000/api/local-llm/generate',
                    json={
                        'prompt': prompt, 
                        'system_prompt': system_prompt,
                        'stream': True,
                        'max_tokens': max_tokens,
                        'temperature': temperature
                    },
                    stream=True
                )
                
                # Check if the request was successful
                if response.status_code != 200:
                    error_msg = f"Error from LLM API: {response.text}"
                    logging.error(error_msg)
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                
                # Stream the response
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        yield f"{line}\n\n"
            except Exception as e:
                error_msg = f"Error in LLM streaming: {str(e)}"
                logging.error(error_msg)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                yield "data: [DONE]\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    except Exception as e:
        error_msg = f"Error processing LLM request: {str(e)}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

# Start the server when run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000, debug=True)