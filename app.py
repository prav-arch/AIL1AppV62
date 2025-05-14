import os
import logging
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key")

# Configure app settings from config.py
app.config.from_pyfile('config.py')

# Initialize Socket.IO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes to register blueprints
from routes.dashboard import dashboard_bp
from routes.llm_assistant import llm_assistant_bp
from routes.rag import rag_bp
from routes.anomalies import anomalies_bp
from routes.data_pipeline import data_pipeline_bp
from routes.kafka_browser import kafka_browser_bp

# Register blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(llm_assistant_bp)
app.register_blueprint(rag_bp)
app.register_blueprint(anomalies_bp)
app.register_blueprint(data_pipeline_bp)
app.register_blueprint(kafka_browser_bp)

# Global API routes that match what the JavaScript is expecting

@app.route('/test-urls')
def test_urls():
    """Debug endpoint to test url_for generation"""
    from flask import url_for
    urls = {
        'dashboard': url_for('dashboard.index'),
        'llm_assistant': url_for('llm_assistant.index'),
        'rag': url_for('rag.index'),
        'anomalies': url_for('anomalies.index'),
        'data_pipeline': url_for('data_pipeline.index'),
        'kafka_browser': url_for('kafka_browser.index')
    }
    return jsonify(urls)

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
        'llm_usage': [random.randint(50, 150) for _ in range(7)],  # Last 7 days of LLM usage
        'resource_distribution': [
            {'label': 'CPU', 'value': random.randint(20, 40)},
            {'label': 'Memory', 'value': random.randint(15, 35)},
            {'label': 'Storage', 'value': random.randint(10, 25)},
            {'label': 'Network', 'value': random.randint(15, 30)}
        ],
        'gpu_utilization': [random.randint(0, 100) for _ in range(24)]  # Last 24 hours of GPU usage
    }
    return jsonify(metrics)

@app.route('/api/kafka/recent-messages', methods=['GET'])
def api_recent_kafka_messages():
    """Return recent Kafka messages for the dashboard"""
    queues = ['logs-queue', 'metrics-queue', 'alerts-queue', 'events-queue', 'system-queue']
    messages = []
    
    for i in range(5):  # Generate 5 messages
        messages.append({
            'queue': random.choice(queues),
            'message': random.choice([
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
            'time_ago': f"{random.randint(1, 30)}m ago"
        })
    
    return jsonify(messages)

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
        },
        {
            'name': 'Model Training',
            'description': f"Scheduled for {(datetime.now() + timedelta(hours=2)).strftime('%H:%M')}",
            'status': 'Scheduled'
        }
    ]
    
    return jsonify(pipelines)

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
        },
        {
            'title': 'API Response Time',
            'description': 'Increased latency detected',
            'details_url': '/anomalies'
        }
    ]
    
    return jsonify(anomalies)
