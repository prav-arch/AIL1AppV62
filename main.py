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

# Set up database access - always use real ClickHouse
try:
    logging.info("Using real ClickHouse implementation")
    from clickhouse_models import Document, DocumentChunk, VectorDBStats, get_clickhouse_client
    from clickhouse_llm_query import (
        initialize_database, save_llm_query, update_llm_query_response,
        get_llm_query_count, get_today_llm_query_count, get_llm_queries
    )
    
    # Initialize the ClickHouse database
    initialize_database()
    logging.info("ClickHouse database initialized successfully")
except Exception as e:
    logging.error(f"Error initializing ClickHouse: {e}")
    # Fallback to mock if ClickHouse fails to initialize
    logging.info("Falling back to mock ClickHouse implementation")
    from mock_clickhouse import (
        get_llm_query_count, get_today_llm_query_count, save_llm_query, 
        update_llm_query_response, get_llm_queries
    )

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
    # Get real count of LLM queries from ClickHouse
    try:
        # Count total queries
        total_queries = get_llm_query_count()
        
        # Count queries from today
        queries_today = get_today_llm_query_count()
    except Exception as e:
        logging.error(f"Error getting query counts: {str(e)}")
        total_queries = 0
        queries_today = 0
    
    return jsonify({
        'total_documents': random.randint(50, 200),
        'active_pipelines': random.randint(5, 15),
        'kafka_topics': random.randint(10, 30),
        'anomalies_detected': random.randint(0, 20),
        'system_health': random.choice(['good', 'excellent', 'fair']),
        'llm_queries_today': queries_today,
        'total_llm_queries': total_queries,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/kafka/messages', methods=['GET'])
def api_recent_kafka_messages():
    """Return recent Kafka messages for the dashboard"""
    try:
        from services.mock_api_services import get_recent_kafka_messages
        messages = get_recent_kafka_messages()
        return jsonify({'messages': messages})
    except Exception as e:
        logging.error(f"Error getting Kafka messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/status', methods=['GET'])
def api_pipeline_status():
    """Return pipeline status information"""
    try:
        from services.mock_api_services import get_pipeline_status
        data = get_pipeline_status()
        # Format the response to match what the frontend expects
        pipelines = data.get('active_pipelines', [])
        # Add description field to each pipeline as expected by frontend
        for pipeline in pipelines:
            pipeline['description'] = f"Processing {pipeline.get('data_processed', '0 MB')} with {pipeline.get('nodes', 0)} nodes"
        
        return jsonify({'pipelines': pipelines})
    except Exception as e:
        logging.error(f"Error getting pipeline status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/nifi/jobs', methods=['GET'])
def api_nifi_jobs():
    """Return NiFi jobs for the data pipeline dashboard"""
    try:
        # Generate mock NiFi jobs
        jobs = []
        for i in range(5):
            jobs.append({
                'id': f'nifi-job-{i+1}',
                'name': f'Data Collection Job {i+1}',
                'status': random.choice(['running', 'stopped', 'failed', 'waiting']),
                'type': 'file-processing',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'last_run': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'schedule': f'Every {random.randint(1, 6)} hours'
            })
        return jsonify({'jobs': jobs})
    except Exception as e:
        logging.error(f"Error getting NiFi jobs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/airflow/dags', methods=['GET'])
def api_airflow_dags():
    """Return Airflow DAGs for the data pipeline dashboard"""
    try:
        # Generate mock Airflow DAGs
        dags = []
        for i in range(5):
            dags.append({
                'id': f'airflow-dag-{i+1}',
                'name': f'Processing Workflow {i+1}',
                'status': random.choice(['active', 'paused', 'failed']),
                'schedule': f'0 {random.randint(0, 23)} * * *',
                'last_run': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'next_run': (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat(),
                'duration': f'{random.randint(10, 120)} minutes'
            })
        return jsonify({'dags': dags})
    except Exception as e:
        logging.error(f"Error getting Airflow DAGs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/jobs/status', methods=['GET'])
def api_jobs_status():
    """Return status overview for jobs in the data pipeline"""
    try:
        # Generate mock job status statistics
        status = {
            'total': random.randint(20, 50),
            'running': random.randint(5, 15),
            'failed': random.randint(0, 5),
            'waiting': random.randint(3, 10),
            'completed': random.randint(10, 30)
        }
        return jsonify(status)
    except Exception as e:
        logging.error(f"Error getting job status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kafka/topics', methods=['GET'])
def api_kafka_topics():
    """Return Kafka topics for the Kafka browser"""
    try:
        # Generate mock Kafka topics
        topics = []
        for i in range(10):
            topics.append({
                'name': f'topic-{i+1}',
                'partitions': random.randint(1, 10),
                'replication_factor': random.randint(1, 3),
                'messages': random.randint(100, 10000),
                'size': f'{random.randint(1, 100)} MB',
                'retention': f'{random.randint(1, 7)} days',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
            })
        return jsonify({'topics': topics})
    except Exception as e:
        logging.error(f"Error getting Kafka topics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies/latest', methods=['GET'])
def api_latest_anomalies():
    """Return latest anomalies information"""
    try:
        from services.mock_api_services import get_latest_anomalies
        import random
        # get_latest_anomalies() returns a list directly
        anomalies = get_latest_anomalies()
        # Ensure each anomaly has the fields expected by the frontend
        for anomaly in anomalies:
            if 'time_ago' not in anomaly:
                # Ensure time_ago field exists for the frontend
                anomaly['time_ago'] = f"{random.randint(1, 60)} minutes ago"
        
        return jsonify({'anomalies': anomalies})
    except Exception as e:
        logging.error(f"Error fetching latest anomalies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies/stats', methods=['GET'])
def api_anomaly_stats():
    """Return statistics about anomalies"""
    try:
        from services.mock_api_services import get_anomaly_stats
        data = get_anomaly_stats()
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error getting anomaly stats: {str(e)}")
        return jsonify({'error': str(e)}), 500





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
    
    # Create a new LLM query record in ClickHouse
    start_time = time.time()
    agent_type = data.get('agent_type', 'general')
    use_rag = data.get('use_rag', False)
    
    # Save to database using ClickHouse storage
    try:
        query_id = save_llm_query(
            query_text=prompt, 
            agent_type=agent_type,
            temperature=temperature, 
            max_tokens=max_tokens,
            used_rag=use_rag
        )
        logging.info(f"Saved LLM query to database with ID: {query_id}")
    except Exception as e:
        logging.error(f"Error saving LLM query to database: {str(e)}")
        query_id = None
    
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
            full_response = ""
            try:
                # Make request to the local LLM API on port 15000
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
                    
                    # Update the LLMQuery record with the error
                    try:
                        llm_query.error = error_msg
                        llm_query.response_time_ms = int((time.time() - start_time) * 1000)
                        db.session.commit()
                    except Exception as e:
                        logging.error(f"Error updating LLM query: {str(e)}")
                        db.session.rollback()
                    
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                
                # Stream the response
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        
                        # Extract text token if possible
                        try:
                            if line.startswith('data: ') and line != 'data: [DONE]':
                                data_json = json.loads(line[6:])
                                if 'text' in data_json:
                                    full_response += data_json['text']
                        except:
                            pass
                            
                        yield f"{line}\n\n"
                
                # Update the LLMQuery record with the full response
                try:
                    llm_query.response_text = full_response
                    llm_query.response_time_ms = int((time.time() - start_time) * 1000)
                    db.session.commit()
                    logging.info(f"Updated LLM query {llm_query.id} with response")
                except Exception as e:
                    logging.error(f"Error updating LLM query response: {str(e)}")
                    db.session.rollback()
                    
            except Exception as e:
                error_msg = f"Error in LLM streaming: {str(e)}"
                logging.error(error_msg)
                
                # Update the LLMQuery record with the error
                try:
                    llm_query.error = error_msg
                    llm_query.response_time_ms = int((time.time() - start_time) * 1000)
                    db.session.commit()
                except Exception as err:
                    logging.error(f"Error updating LLM query: {str(err)}")
                    db.session.rollback()
                
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                yield "data: [DONE]\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    except Exception as e:
        error_msg = f"Error processing LLM request: {str(e)}"
        logging.error(error_msg)
        
        # Update the LLMQuery record with the error
        try:
            llm_query.error = error_msg
            llm_query.response_time_ms = int((time.time() - start_time) * 1000)
            db.session.commit()
        except Exception as err:
            logging.error(f"Error updating LLM query: {str(err)}")
            db.session.rollback()
            
        return jsonify({'error': error_msg}), 500

# Add API endpoint to get LLM queries for dashboard
@app.route('/api/llm/queries', methods=['GET'])
def api_llm_queries():
    """Return list of LLM queries for the dashboard"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get queries from ClickHouse
        result = get_llm_queries(page=page, per_page=per_page)
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error retrieving LLM queries: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Start the server when run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000, debug=True)