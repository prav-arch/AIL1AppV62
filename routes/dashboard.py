from flask import Blueprint, render_template, jsonify
import random
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

@dashboard_bp.route('/')
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
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
        'llm_usage': get_chart_data(7, 50, 150),  # Last 7 days of LLM usage
        'resource_distribution': [
            {'label': 'CPU', 'value': random.randint(20, 40)},
            {'label': 'Memory', 'value': random.randint(15, 35)},
            {'label': 'Storage', 'value': random.randint(10, 25)},
            {'label': 'Network', 'value': random.randint(15, 30)}
        ],
        'gpu_utilization': get_chart_data(24, 0, 100),  # Last 24 hours of GPU usage
    }
    return jsonify(metrics)

@dashboard_bp.route('/api/dashboard/kafka-messages', methods=['GET'])
def get_recent_kafka_messages():
    """Return recent Kafka messages for the dashboard"""
    queues = ['logs-queue', 'metrics-queue', 'alerts-queue', 'events-queue', 'system-queue']
    messages = []
    
    for i in range(5):  # Generate 5 messages
        messages.append({
            'queue': random.choice(queues),
            'message': get_random_message(),
            'time_ago': f"{random.randint(1, 30)}m ago"
        })
    
    return jsonify(messages)

@dashboard_bp.route('/api/dashboard/pipeline-status', methods=['GET'])
def get_pipeline_status():
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

@dashboard_bp.route('/api/dashboard/anomalies', methods=['GET'])
def get_latest_anomalies():
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

# Helper functions
def get_chart_data(points, min_value, max_value):
    """Generate random chart data with the specified number of points"""
    return [random.randint(min_value, max_value) for _ in range(points)]

def get_random_message():
    """Return a random message for Kafka logs"""
    messages = [
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
    ]
    return random.choice(messages)