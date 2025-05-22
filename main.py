import os
import logging
import json
from flask import Flask, jsonify, render_template, request, Response, send_from_directory
import random
from datetime import datetime, timedelta
import time
import requests
from flask import stream_with_context

# Import the blueprints
from routes.local_llm import local_llm_bp
from routes.rag import rag_bp
from routes.database import database_bp
from routes.anomalies import anomalies_bp

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
app.register_blueprint(database_bp)
app.register_blueprint(anomalies_bp)

# The Kafka and Pipeline API routes have been moved to separate functions below

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

# Anomalies page - using blueprint now
# @app.route('/anomalies')
# def anomalies():
#     return render_template('anomalies.html')

# Data Pipeline page
@app.route('/data-pipeline')
def data_pipeline():
    return render_template('data_pipeline.html', active_tab='data_pipeline')

# Kafka Browser page
@app.route('/kafka-browser')
def kafka_browser():
    return render_template('kafka_browser.html', active_tab='kafka_browser')

# Function below is no longer used - keeping for reference
def kafka_browser_old():
    # Prepare mock data for templates
    kafka_topics = [
        {
            "name": "logs-topic",
            "partitions": 3,
            "replication": 3,
            "message_count": 524892,
            "throughput": "120 msg/sec",
            "size": "750 MB",
            "retention": "7 days",
            "created": "2025-04-01 00:00:00"
        },
        {
            "name": "metrics-topic",
            "partitions": 5,
            "replication": 3,
            "message_count": 328157,
            "throughput": "250 msg/sec",
            "size": "1.2 GB",
            "retention": "14 days",
            "created": "2025-04-01 00:00:00"
        },
        {
            "name": "events-topic",
            "partitions": 2,
            "replication": 3,
            "message_count": 125628,
            "throughput": "45 msg/sec",
            "size": "380 MB",
            "retention": "30 days",
            "created": "2025-04-02 00:00:00"
        },
        {
            "name": "alerts-topic",
            "partitions": 1,
            "replication": 3,
            "message_count": 8421,
            "throughput": "5 msg/sec",
            "size": "12 MB",
            "retention": "90 days",
            "created": "2025-04-02 00:00:00"
        },
        {
            "name": "clickstream-topic",
            "partitions": 8,
            "replication": 3,
            "message_count": 1458276,
            "throughput": "850 msg/sec",
            "size": "3.5 GB",
            "retention": "3 days",
            "created": "2025-04-03 00:00:00"
        }
    ]
    
    kafka_messages = [
        {
            "offset": 1000050,
            "partition": 1,
            "key": "srv-web-01",
            "value": {
                "timestamp": "2025-05-22T04:55:12.000Z",
                "level": "INFO",
                "service": "api-gateway",
                "message": "Request processed successfully",
                "requestId": "abcd1234",
                "duration": 125
            },
            "timestamp": "2025-05-22 04:55:12"
        },
        {
            "offset": 1000049,
            "partition": 0,
            "key": "srv-auth-02",
            "value": {
                "timestamp": "2025-05-22T04:55:10.000Z",
                "level": "WARN",
                "service": "auth-service",
                "message": "Rate limit exceeded",
                "requestId": "efgh5678",
                "duration": 350
            },
            "timestamp": "2025-05-22 04:55:10"
        },
        {
            "offset": 1000048,
            "partition": 2,
            "key": "srv-db-01",
            "value": {
                "timestamp": "2025-05-22T04:55:08.000Z",
                "level": "ERROR",
                "service": "database",
                "message": "Connection timeout",
                "requestId": "ijkl9012",
                "duration": 500
            },
            "timestamp": "2025-05-22 04:55:08"
        }
    ]
    
    consumer_groups = [
        {
            "id": "log-processor-group",
            "members": 3,
            "topics": ["logs-topic", "app-logs"],
            "total_lag": 275,
            "status": "Stable",
            "status_class": "success"
        },
        {
            "id": "metrics-analyzer",
            "members": 5,
            "topics": ["metrics-topic", "system-metrics"],
            "total_lag": 482,
            "status": "Stable",
            "status_class": "success"
        },
        {
            "id": "clickstream-processor",
            "members": 8,
            "topics": ["clickstream-topic"],
            "total_lag": 8763,
            "status": "Warning",
            "status_class": "warning"
        }
    ]
    
    stats = {
        "broker_count": 3,
        "total_topics": 15,
        "consumer_groups_count": 12,
        "total_messages": "1,862,473",
        "selected_topic": "logs-topic",
        "topic_message_count": "524,892",
        "topic_avg_size": "1.4 KB",
        "topic_top_partition": 1,
        "topic_message_rate": "120 msg/sec"
    }
    
    import json
    for msg in kafka_messages:
        msg["value_json"] = json.dumps(msg["value"])
    
    return render_template('kafka_browser.html',
                          kafka_topics=kafka_topics,
                          kafka_messages=kafka_messages,
                          consumer_groups=consumer_groups,
                          stats=stats)

# Simplified standalone pages that show data
@app.route('/simple-data-pipeline')
def simple_data_pipeline():
    return send_from_directory('static', 'simplified_data_pipeline.html')

@app.route('/simple-kafka-browser')
def simple_kafka_browser():
    return send_from_directory('static', 'simplified_kafka_browser.html')

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

@app.route('/api/kafka/recent-messages', methods=['GET'])
def api_kafka_recent_messages():
    """Return recent Kafka messages for the dashboard"""
    messages = []
    topics = ['logs', 'metrics', 'alerts', 'transactions', 'events']
    
    for _ in range(5):
        messages.append({
            'topic': random.choice(topics),
            'content': random.choice([
                "System startup completed",
                "User login successful",
                "New data received from source",
                "Processing completed successfully",
                "CPU spike detected",
                "Memory usage increased",
                "Database backup completed",
                "New anomaly detected",
                "Alert triggered by sensor",
                "Scheduled task started"
            ]),
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
            'size': random.randint(200, 1500),
            'key': f'key-{random.randint(1, 100)}'
        })
    
    return jsonify({'messages': messages})

@app.route('/api/pipeline/status', methods=['GET'])
def api_pipeline_status():
    """Return pipeline status information"""
    pipelines = []
    statuses = ['running', 'completed', 'failed', 'scheduled', 'paused']
    
    for i in range(1, 6):
        pipelines.append({
            'id': f'pipeline-{i}',
            'name': f'Data Pipeline {i}',
            'description': f'Processing data for pipeline {i}',
            'status': random.choice(statuses),
            'last_run': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
            'next_run': (datetime.now() + timedelta(hours=random.randint(1, 12))).isoformat() if random.choice([True, False]) else None,
            'success_rate': random.randint(70, 100)
        })
    
    return jsonify({'pipelines': pipelines})

@app.route('/api/anomalies/latest', methods=['GET'])
def api_latest_anomalies():
    """Return latest anomalies information"""
    anomalies = []
    types = ['spike', 'dip', 'trend_change', 'outlier', 'pattern_break']
    services = ['api', 'database', 'auth', 'payment', 'storage', 'compute']
    
    for i in range(5):
        anomaly_type = random.choice(types)
        service = random.choice(services)
        anomalies.append({
            'id': f'anomaly-{i+1}',
            'title': f'{service.title()} Service Anomaly',
            'type': anomaly_type,
            'service': service,
            'severity': random.choice(['low', 'medium', 'high']),
            'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat(),
            'description': f'Detected {anomaly_type} in {service} service metrics',
            'is_resolved': random.choice([True, False])
        })
    
    return jsonify({'anomalies': anomalies})

# API routes for anomalies are now handled by the anomalies blueprint in routes/anomalies.py

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