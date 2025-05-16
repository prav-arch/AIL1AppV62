from flask import Flask, render_template, jsonify, request, Response, stream_with_context
import time
import json
import logging
import random
import os
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize LLM service
try:
    from services.llm_service_manager import start_llm_service
    # Start LLM service in background thread to avoid blocking app startup
    import threading
    threading.Thread(target=start_llm_service, daemon=True).start()
    logging.info("LLM service initialization started in background")
except Exception as e:
    logging.warning(f"Could not initialize LLM service: {str(e)}")

# Routes for main pages
@app.route('/')
def test():
    return render_template('dashboard.html')

@app.route('/dashboard')
def index():
    return render_template('dashboard.html')

@app.route('/llm-assistant')
def llm_assistant():
    return render_template('llm_assistant.html')

@app.route('/anomalies')
def anomalies():
    return render_template('anomalies.html')

@app.route('/data-pipeline')
def data_pipeline():
    return render_template('data_pipeline.html')

@app.route('/kafka-browser')
def kafka_browser():
    return render_template('kafka_browser.html')

# API Endpoints for Dashboard
@app.route('/api/dashboard/metrics')
def api_dashboard_metrics():
    """Return dashboard metrics for display"""
    try:
        import clickhouse_llm_query
        # Generate sample metrics for the dashboard
        metrics = {
            'llm_requests': 250,
            'today_llm_requests': 25,
            'documents_indexed': 120,
            'today_indexed': 15,
            'anomalies_detected': 45,
            'today_anomalies': 5,
            'pipeline_jobs': 12,
            'active_jobs': 3
        }
        
        return jsonify(metrics)
    except Exception as e:
        logging.error(f"Error fetching dashboard metrics: {str(e)}")
        # Return a successful response even if there's an error
        return jsonify({
            'llm_requests': 250,
            'today_llm_requests': 25,
            'documents_indexed': 120,
            'today_indexed': 15,
            'anomalies_detected': 45,
            'today_anomalies': 5,
            'pipeline_jobs': 12,
            'active_jobs': 3
        })

@app.route('/api/dashboard/recent-kafka-messages')
def api_recent_kafka_messages():
    """Return recent Kafka messages for the dashboard"""
    messages = []
    topics = ['user-events', 'transactions', 'system-logs', 'metrics']
    
    for i in range(10):
        topic = random.choice(topics)
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 60))
        
        messages.append({
            'id': f"msg-{i+1}",
            'topic': topic,
            'partition': random.randint(0, 3),
            'offset': random.randint(1000, 9999),
            'key': f"key-{random.randint(1, 100)}",
            'size': random.randint(200, 1500),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(messages)

@app.route('/api/dashboard/pipeline-status')
def api_pipeline_status():
    """Return pipeline status information"""
    statuses = ['running', 'completed', 'failed', 'pending']
    jobs = []
    
    for i in range(5):
        status = random.choice(statuses)
        started = datetime.now() - timedelta(hours=random.randint(1, 24))
        
        job = {
            'id': f"job-{i+1}",
            'name': f"Data Processing Job {i+1}",
            'status': status,
            'started': started.strftime('%Y-%m-%d %H:%M:%S'),
            'progress': random.randint(0, 100) if status != 'completed' else 100,
        }
        
        if status == 'completed':
            job['completed'] = (started + timedelta(minutes=random.randint(10, 60))).strftime('%Y-%m-%d %H:%M:%S')
        elif status == 'failed':
            job['error'] = random.choice([
                'Connection timeout', 
                'Resource not found', 
                'Permission denied', 
                'Out of memory'
            ])
            
        jobs.append(job)
    
    return jsonify(jobs)

@app.route('/api/dashboard/latest-anomalies')
def api_latest_anomalies():
    """Return latest anomalies information"""
    anomaly_types = ['spike', 'drop', 'pattern_change', 'outlier']
    severities = ['low', 'medium', 'high', 'critical']
    metrics = ['cpu_usage', 'memory_usage', 'disk_io', 'network_traffic', 'api_latency']
    
    anomalies = []
    
    for i in range(5):
        detected = datetime.now() - timedelta(hours=random.randint(0, 24))
        anomaly_type = random.choice(anomaly_types)
        severity = random.choice(severities)
        metric = random.choice(metrics)
        
        anomalies.append({
            'id': f"anomaly-{i+1}",
            'type': anomaly_type,
            'severity': severity,
            'metric': metric,
            'value': round(random.uniform(0, 100), 2),
            'detected': detected.strftime('%Y-%m-%d %H:%M:%S'),
            'threshold': round(random.uniform(0, 100), 2),
            'description': f"Unusual {anomaly_type} detected in {metric} exceeding threshold"
        })
    
    return jsonify(anomalies)

@app.route('/api/anomalies/stats')
def api_anomaly_stats():
    """Return statistics about anomalies"""
    categories = ['cpu_usage', 'memory_usage', 'disk_io', 'network_traffic', 'api_latency']
    
    # Create time series data for the past 7 days
    time_series = []
    for i in range(7):
        day = datetime.now() - timedelta(days=i)
        time_series.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': random.randint(5, 30)
        })
    
    # Create category distribution
    distribution = []
    for category in categories:
        distribution.append({
            'category': category,
            'count': random.randint(10, 50)
        })
    
    # Create severity distribution
    severity = {
        'low': random.randint(20, 40),
        'medium': random.randint(10, 30),
        'high': random.randint(5, 15),
        'critical': random.randint(1, 10)
    }
    
    return jsonify({
        'total': sum(item['count'] for item in distribution),
        'time_series': time_series,
        'distribution': distribution,
        'severity': severity
    })

@app.route('/api/anomalies/list')
def api_anomalies_list():
    """Return list of anomalies with optional filtering"""
    # Get query parameters for filtering
    days = request.args.get('days', default=7, type=int)
    category = request.args.get('category', default=None, type=str)
    severity = request.args.get('severity', default=None, type=str)
    
    anomaly_types = ['spike', 'drop', 'pattern_change', 'outlier']
    severities = ['low', 'medium', 'high', 'critical']
    categories = ['cpu_usage', 'memory_usage', 'disk_io', 'network_traffic', 'api_latency']
    
    # Apply filters if provided
    if severity and severity in severities:
        used_severities = [severity]
    else:
        used_severities = severities
        
    if category and category in categories:
        used_categories = [category]
    else:
        used_categories = categories
    
    # Generate random anomalies data
    anomalies = []
    
    # Determine number of results based on filters
    if category or severity:
        count = random.randint(5, 15)
    else:
        count = random.randint(15, 30)
    
    for i in range(count):
        detected = datetime.now() - timedelta(hours=random.randint(0, days*24))
        anomaly_type = random.choice(anomaly_types)
        chosen_severity = random.choice(used_severities)
        chosen_category = random.choice(used_categories)
        
        # Generate values based on severity
        if chosen_severity == 'critical':
            value = round(random.uniform(90, 100), 2)
            threshold = round(random.uniform(70, 85), 2)
        elif chosen_severity == 'high':
            value = round(random.uniform(70, 89), 2)
            threshold = round(random.uniform(50, 69), 2)
        elif chosen_severity == 'medium':
            value = round(random.uniform(40, 69), 2)
            threshold = round(random.uniform(20, 39), 2)
        else:  # low
            value = round(random.uniform(10, 39), 2)
            threshold = round(random.uniform(5, 9), 2)
            
        anomalies.append({
            'id': f"anomaly-{random.randint(1000, 9999)}",
            'type': anomaly_type,
            'severity': chosen_severity,
            'metric': chosen_category,
            'value': value,
            'detected': detected.strftime('%Y-%m-%d %H:%M:%S'),
            'threshold': threshold,
            'description': f"Unusual {anomaly_type} detected in {chosen_category} exceeding threshold",
            'is_resolved': random.choice([True, False])
        })
    
    # Sort by detected time, most recent first
    anomalies.sort(key=lambda x: x['detected'], reverse=True)
    
    return jsonify(anomalies)

# API for NiFi Job Management
@app.route('/api/nifi/jobs')
def api_nifi_jobs():
    """Return NiFi jobs for the data pipeline dashboard"""
    jobs = []
    statuses = ['running', 'stopped', 'failed', 'completed']
    
    for i in range(10):
        status = random.choice(statuses)
        started = datetime.now() - timedelta(hours=random.randint(1, 48))
        job = {
            'id': f"nifi-job-{1000+i}",
            'name': f"Data Flow {i+1}",
            'description': f"Process and transform data from source {i+1}",
            'status': status,
            'created': (started - timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d %H:%M:%S'),
            'last_started': started.strftime('%Y-%m-%d %H:%M:%S'),
            'type': random.choice(['Extract', 'Transform', 'Load', 'Validate']),
            'source': random.choice(['Kafka', 'S3', 'Database', 'API', 'File']),
            'destination': random.choice(['S3', 'Database', 'API', 'File', 'Kafka']),
        }
        
        if status == 'completed' or status == 'failed':
            job['last_completed'] = (started + timedelta(minutes=random.randint(5, 120))).strftime('%Y-%m-%d %H:%M:%S')
            
        if status == 'running':
            job['progress'] = str(random.randint(0, 99))
            
        if status == 'failed':
            job['error'] = random.choice([
                'Connection refused', 
                'Timeout',
                'Missing dependencies',
                'Data validation error',
                'Insufficient resources'
            ])
            
        jobs.append(job)
    
    return jsonify(jobs)

@app.route('/api/nifi/job/<job_id>', methods=['GET', 'DELETE'])
def api_nifi_job_detail(job_id):
    """Get or delete a specific NiFi job"""
    if request.method == 'DELETE':
        # Simulate deleting a job
        return jsonify({
            'success': True,
            'message': f"Job {job_id} deleted successfully"
        })
    
    # GET method - return job details
    status = random.choice(['running', 'stopped', 'failed', 'completed'])
    started = datetime.now() - timedelta(hours=random.randint(1, 48))
    
    # Generate job details
    job = {
        'id': job_id,
        'name': f"Data Flow {job_id.split('-')[-1]}",
        'description': "Process and transform data from source to destination",
        'status': status,
        'created': (started - timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d %H:%M:%S'),
        'last_started': started.strftime('%Y-%m-%d %H:%M:%S'),
        'type': random.choice(['Extract', 'Transform', 'Load', 'Validate']),
        'source': random.choice(['Kafka', 'S3', 'Database', 'API', 'File']),
        'destination': random.choice(['S3', 'Database', 'API', 'File', 'Kafka']),
        'processor_count': random.randint(3, 15),
        'connections': random.randint(4, 20),
        'input_port_count': random.randint(1, 3),
        'output_port_count': random.randint(1, 3),
        'configuration': {
            'scheduled_interval': f"{random.randint(1, 30)} min",
            'concurrent_tasks': random.randint(1, 8),
            'run_duration': f"{random.randint(1, 120)} min",
            'backpressure_threshold': f"{random.randint(1000, 10000)} objects",
            'bulletins_enabled': random.choice([True, False])
        }
    }
    
    # Add statistics based on status
    if status == 'running' or status == 'completed':
        job['statistics'] = {
            'bytes_read': random.randint(1000000, 100000000),
            'bytes_written': random.randint(1000000, 100000000),
            'files_read': random.randint(10, 1000),
            'files_written': random.randint(10, 1000),
            'flowfiles_received': random.randint(100, 10000),
            'flowfiles_sent': random.randint(100, 10000),
            'average_lineage_duration': random.randint(100, 10000)
        }
    
    if status == 'running':
        job['progress'] = random.randint(0, 99)
    
    if status == 'failed':
        job['error'] = {
            'message': random.choice([
                'Connection refused', 
                'Timeout',
                'Missing dependencies',
                'Data validation error',
                'Insufficient resources'
            ]),
            'timestamp': (started + timedelta(minutes=random.randint(5, 120))).strftime('%Y-%m-%d %H:%M:%S'),
            'component': random.choice(['Processor', 'Connection', 'Controller Service', 'Remote Process Group']),
            'details': "Detailed error information would be displayed here"
        }
    
    return jsonify(job)

@app.route('/api/nifi/job/<job_id>/<action>', methods=['POST'])
def api_nifi_job_action(job_id, action):
    """Perform actions on a NiFi job (start, stop, pause, restart)"""
    valid_actions = ['start', 'stop', 'pause', 'restart']
    
    if action not in valid_actions:
        return jsonify({
            'success': False,
            'message': f"Invalid action '{action}'. Valid actions are: {', '.join(valid_actions)}"
        }), 400
    
    # Process the action
    return jsonify({
        'success': True,
        'message': f"Job {job_id} {action}ed successfully",
        'job_id': job_id,
        'action': action,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# API for Airflow DAG Management
@app.route('/api/airflow/dags')
def api_airflow_dags():
    """Return Airflow DAGs for the data pipeline dashboard"""
    dags = []
    statuses = ['running', 'scheduled', 'failed', 'succeeded']
    
    for i in range(10):
        status = random.choice(statuses)
        last_run = datetime.now() - timedelta(hours=random.randint(1, 48))
        
        dag = {
            'id': f"dag_{i+1}",
            'name': f"ETL Pipeline {i+1}",
            'description': f"Extract, transform and load data for pipeline {i+1}",
            'status': status,
            'is_paused': random.choice([True, False]),
            'last_run': last_run.strftime('%Y-%m-%d %H:%M:%S'),
            'next_run': (datetime.now() + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S'),
            'schedule': random.choice(['0 * * * *', '0 0 * * *', '*/15 * * * *', '@daily', '@hourly']),
            'owner': random.choice(['data_team', 'etl_service', 'data_admin', 'system']),
            'tags': random.sample(['etl', 'data', 'production', 'development', 'critical', 'reporting'], k=random.randint(1, 3))
        }
        
        if status != 'scheduled':
            dag['duration'] = f"{random.randint(10, 120)} minutes"
            
        if status == 'failed':
            dag['error'] = random.choice([
                'Operator failure',
                'Timeout',
                'Resource constraint',
                'Upstream failure',
                'Data validation error'
            ])
            
        dags.append(dag)
    
    return jsonify(dags)

@app.route('/api/airflow/dag/<dag_id>/trigger', methods=['POST'])
def api_trigger_dag(dag_id):
    """Trigger a specific Airflow DAG"""
    # Process the action
    return jsonify({
        'success': True,
        'message': f"DAG {dag_id} triggered successfully",
        'dag_id': dag_id,
        'trigger_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'run_id': f"manual_{int(time.time())}"
    })

@app.route('/api/airflow/schedule', methods=['POST'])
def api_schedule_dag():
    """Schedule a new Airflow DAG"""
    data = request.json
    
    if not data or 'dag_id' not in data or 'schedule' not in data:
        return jsonify({
            'success': False,
            'message': "Missing required parameters: dag_id and schedule"
        }), 400
    
    return jsonify({
        'success': True,
        'message': f"DAG {data['dag_id']} scheduled successfully",
        'dag_id': data['dag_id'],
        'schedule': data['schedule'],
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/pipeline/jobs-status')
def api_jobs_status():
    """Return status overview for jobs in the data pipeline"""
    # Count by status
    status_counts = {
        'running': random.randint(1, 10),
        'scheduled': random.randint(5, 20),
        'failed': random.randint(0, 5),
        'succeeded': random.randint(10, 30),
        'total': 0
    }
    
    # Calculate total
    status_counts['total'] = sum(v for k, v in status_counts.items() if k != 'total')
    
    # Jobs by type
    job_types = {
        'extract': random.randint(5, 15),
        'transform': random.randint(10, 20),
        'load': random.randint(5, 15),
        'validate': random.randint(2, 10)
    }
    
    # Recent activity
    recent_activity = []
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=random.randint(5, 120))
        
        recent_activity.append({
            'id': f"job-{random.randint(1000, 9999)}",
            'type': random.choice(['NiFi Flow', 'Airflow DAG']),
            'name': f"Data Job {i+1}",
            'action': random.choice(['started', 'completed', 'failed', 'scheduled', 'modified']),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user': random.choice(['system', 'admin', 'data_team', 'scheduler'])
        })
    
    # Sort by timestamp
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        'status_counts': status_counts,
        'job_types': job_types,
        'recent_activity': recent_activity
    })

# API for Kafka topics
@app.route('/api/kafka/topics')
def api_kafka_topics():
    """Return Kafka topics for the Kafka browser"""
    topics = []
    
    # Define some common topics
    topic_names = [
        'user-events', 'transactions', 'system-logs', 'metrics', 
        'notifications', 'orders', 'inventory-updates', 'customer-activity',
        'clickstream', 'app-events', 'sensor-data', 'analytics'
    ]
    
    for i, name in enumerate(topic_names):
        created = datetime.now() - timedelta(days=random.randint(1, 90))
        
        topics.append({
            'id': i + 1,
            'name': name,
            'partitions': random.randint(1, 12),
            'replication_factor': random.randint(1, 3),
            'message_count': random.randint(1000, 1000000),
            'size_bytes': random.randint(10000, 1000000000),
            'created': created.strftime('%Y-%m-%d %H:%M:%S'),
            'last_message': (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S'),
            'retention_time': f"{random.choice([24, 48, 72, 168, 336])} hours",
            'configs': {
                'cleanup.policy': random.choice(['delete', 'compact']),
                'segment.bytes': random.choice([1073741824, 536870912, 268435456]),
                'compression.type': random.choice(['producer', 'gzip', 'snappy', 'lz4']),
                'max.message.bytes': random.choice([1000012, 2000000, 5000000])
            }
        })
    
    return jsonify(topics)

@app.route('/api/kafka/topics/<topic_name>/messages')
def api_topic_messages(topic_name):
    """Return messages for a specific Kafka topic"""
    # Get query parameters for pagination
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=20, type=int)
    
    # Generate some sample data
    messages = []
    
    for i in range(limit):
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 60))
        
        # Generate message content based on topic
        if 'user' in topic_name:
            content = {
                'user_id': f"user_{random.randint(1000, 9999)}",
                'event': random.choice(['login', 'logout', 'signup', 'profile_update', 'password_change']),
                'device': random.choice(['web', 'mobile', 'tablet', 'api']),
                'ip': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            }
        elif 'transaction' in topic_name:
            content = {
                'transaction_id': f"tx_{random.randint(10000, 99999)}",
                'user_id': f"user_{random.randint(1000, 9999)}",
                'amount': round(random.uniform(1, 1000), 2),
                'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
                'status': random.choice(['completed', 'pending', 'failed', 'refunded'])
            }
        elif 'log' in topic_name:
            content = {
                'level': random.choice(['INFO', 'WARN', 'ERROR', 'DEBUG']),
                'service': random.choice(['api', 'auth', 'backend', 'frontend', 'database']),
                'message': f"Log message {i+1} for offset {offset+i}",
                'trace_id': f"{random.randint(100000, 999999)}"
            }
        elif 'metric' in topic_name:
            content = {
                'metric': random.choice(['cpu', 'memory', 'disk', 'network', 'api_latency']),
                'value': round(random.uniform(0, 100), 2),
                'unit': random.choice(['percent', 'ms', 'count', 'bytes']),
                'host': f"host-{random.randint(1, 10)}"
            }
        else:
            content = {
                'id': f"msg_{random.randint(10000, 99999)}",
                'type': random.choice(['create', 'update', 'delete', 'notify']),
                'payload': f"Sample message payload for {topic_name}"
            }
        
        messages.append({
            'offset': offset + i,
            'partition': random.randint(0, 5),
            'key': f"key-{random.randint(1, 100)}",
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'size': random.randint(200, 1500),
            'content': content
        })
    
    return jsonify({
        'topic': topic_name,
        'messages': messages,
        'total_count': random.randint(1000, 1000000),
        'has_more': True if random.random() > 0.2 else False
    })

@app.route('/api/pipeline/storage-info')
def api_pipeline_storage_info():
    """Return pipeline storage information"""
    # Storage types
    storage_types = {
        'hdfs': random.randint(100, 1000),
        's3': random.randint(500, 2000),
        'local': random.randint(10, 100),
        'database': random.randint(50, 500)
    }
    
    # Storage usage over time
    time_series = []
    base_value = random.randint(1000, 2000)
    for i in range(30):
        day = datetime.now() - timedelta(days=i)
        value = max(0, base_value - i * random.randint(10, 50))
        time_series.append({
            'date': day.strftime('%Y-%m-%d'),
            'usage_gb': value
        })
    
    # Reverse to get chronological order
    time_series.reverse()
    
    # File categories
    file_categories = {
        'raw': random.randint(100, 500),
        'processed': random.randint(200, 600),
        'analytics': random.randint(50, 300),
        'archive': random.randint(300, 1000),
        'temp': random.randint(10, 100)
    }
    
    # Storage capacity
    capacity = {
        'total_gb': 5000,
        'used_gb': sum(storage_types.values()),
        'available_gb': 5000 - sum(storage_types.values())
    }
    
    return jsonify({
        'storage_types': storage_types,
        'time_series': time_series,
        'file_categories': file_categories,
        'capacity': capacity
    })

# API for RAG
@app.route('/api/rag/storage-info')
def api_rag_storage_info():
    """Return RAG-specific file storage information"""
    # Document types
    document_types = {
        'pdf': random.randint(50, 200),
        'txt': random.randint(100, 300),
        'html': random.randint(20, 100),
        'doc': random.randint(10, 50),
        'md': random.randint(30, 150)
    }
    
    # Document ingestion over time
    time_series = []
    for i in range(30):
        day = datetime.now() - timedelta(days=i)
        time_series.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': random.randint(1, 20)
        })
    
    # Reverse to get chronological order
    time_series.reverse()
    
    # Knowledge base categories
    categories = {
        'technical_docs': random.randint(50, 200),
        'product_info': random.randint(30, 150),
        'research_papers': random.randint(20, 100),
        'user_guides': random.randint(40, 180),
        'reports': random.randint(10, 50)
    }
    
    # Vector database info
    vector_db = {
        'total_embeddings': random.randint(10000, 100000),
        'dimension': 384,
        'index_type': 'HNSW',
        'storage_size_mb': random.randint(500, 5000)
    }
    
    return jsonify({
        'document_count': sum(document_types.values()),
        'document_types': document_types,
        'ingestion_history': time_series,
        'categories': categories,
        'vector_db': vector_db
    })

@app.route('/api/rag/search', methods=['POST'])
def api_rag_search():
    """Perform RAG search with the given query"""
    data = request.json or {}
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Mock search results
    results = []
    for i in range(5):
        score = round(random.uniform(0.6, 0.95), 2)
        results.append({
            'id': f"doc_{random.randint(1000, 9999)}",
            'title': f"Document {i+1} for query: {query[:20]}{'...' if len(query) > 20 else ''}",
            'content': f"This is a sample content snippet that relates to the query '{query}'. It contains relevant information about {query.split()[0] if query.split() else ''} and other related topics.",
            'score': score,
            'source': random.choice(['knowledge_base', 'technical_docs', 'product_info', 'user_guides']),
            'file_type': random.choice(['pdf', 'txt', 'html', 'doc']),
            'last_updated': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'query': query,
        'results': results,
        'search_time_ms': random.randint(50, 500),
        'total_docs_searched': random.randint(50, 200)
    })

# LLM API route
@app.route('/api/llm/query', methods=['POST'])
def api_llm_query():
    """Process an LLM query and return the response using the updated handler"""
    from updated_llm_query import new_llm_query_handler
    return new_llm_query_handler()

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors gracefully"""
    logging.error(f"Internal server error: {error}")
    return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

@app.route('/api/llm/queries')
def api_llm_queries():
    """Return list of LLM queries for the dashboard"""
    try:
        import clickhouse_llm_query
        # Try to fetch real queries if available
        real_queries = clickhouse_llm_query.get_llm_queries()
        return jsonify(real_queries)
    except Exception as e:
        logging.error(f"Error fetching LLM queries: {str(e)}")
        
        # If real queries are not available, use mock data
        queries = []
        agent_types = ['general', 'coding', 'data']
        
        for i in range(10):
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
            
            query = {
                'id': f"query_{random.randint(10000, 99999)}",
                'query_text': f"Sample query {i+1} about {'coding issues' if i % 3 == 1 else 'data analysis' if i % 3 == 2 else 'general information'}",
                'agent_type': agent_types[i % 3],
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'response_time_ms': random.randint(500, 5000),
                'used_rag': bool(random.getrandbits(1)),
                'temperature': round(random.uniform(0.5, 0.9), 1),
                'max_tokens': random.choice([1024, 2048, 4096])
            }
            
            # Add a long response text
            query['response_text'] = f"This is a sample response to the query about {'coding' if i % 3 == 1 else 'data analysis' if i % 3 == 2 else 'general information'}. It contains detailed information and explanations that would typically be generated by an LLM."
            
            queries.append(query)
        
        # Sort by timestamp, most recent first
        queries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'queries': queries,
            'total': len(queries),
            'page': 1,
            'per_page': 10,
            'mock': True  # Indicate this is mock data
        })

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)