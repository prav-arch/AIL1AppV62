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

# Direct navigation routes to handle tab navigation
@app.route('/llm-assistant')
def llm_assistant_direct():
    from flask import redirect, url_for
    return redirect(url_for('llm_assistant.index'))

@app.route('/rag')
def rag_direct():
    from flask import redirect, url_for
    return redirect(url_for('rag.index'))

@app.route('/anomalies')
def anomalies_direct():
    from flask import redirect, url_for
    return redirect(url_for('anomalies.index'))

@app.route('/data-pipeline')
def data_pipeline_direct():
    from flask import redirect, url_for
    return redirect(url_for('data_pipeline.index'))

@app.route('/kafka-browser')
def kafka_browser_direct():
    from flask import redirect, url_for
    return redirect(url_for('kafka_browser.index'))

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
        },
        {
            'name': 'Model Training',
            'description': f"Scheduled for {(datetime.now() + timedelta(hours=2)).strftime('%H:%M')}",
            'status': 'Scheduled'
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
        },
        {
            'title': 'API Response Time',
            'description': 'Increased latency detected',
            'details_url': '/anomalies'
        }
    ]
    
    return jsonify({'anomalies': anomalies})

@app.route('/api/anomalies/stats', methods=['GET'])
def api_anomaly_stats():
    """Return statistics about anomalies"""
    total = random.randint(20, 30)
    critical = random.randint(3, 8)
    warning = random.randint(8, 15)
    info = total - critical - warning
    
    stats = {
        'success': True,
        'total': total,
        'critical': critical,
        'warning': warning,
        'info': info,
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
    # Get filter parameter (all, critical, warning, info)
    filter_type = request.args.get('filter', 'all')
    
    # Sample anomalies data
    anomalies = [
        {
            'id': 'A-1283',
            'timestamp': '2023-05-20 14:32:15',
            'type': 'Network',
            'source': 'router-edge-01',
            'description': 'Unusual outbound traffic spike detected (4.5GB in 5 minutes)',
            'severity': 'Critical'
        },
        {
            'id': 'A-1282',
            'timestamp': '2023-05-20 13:45:22',
            'type': 'System',
            'source': 'app-server-03',
            'description': 'Memory usage continuously above 92% for 15 minutes',
            'severity': 'Warning'
        },
        {
            'id': 'A-1281',
            'timestamp': '2023-05-20 12:58:45',
            'type': 'Database',
            'source': 'db-cluster-main',
            'description': 'Query latency increased by 300% in the last hour',
            'severity': 'Critical'
        },
        {
            'id': 'A-1280',
            'timestamp': '2023-05-20 11:23:18',
            'type': 'Application',
            'source': 'web-frontend',
            'description': 'API response time exceeding SLA (avg 3.2s)',
            'severity': 'Warning'
        },
        {
            'id': 'A-1279',
            'timestamp': '2023-05-20 10:15:36',
            'type': 'Security',
            'source': 'firewall-main',
            'description': 'Multiple failed login attempts from IP 192.168.1.45',
            'severity': 'Critical'
        },
        {
            'id': 'A-1278',
            'timestamp': '2023-05-20 09:42:05',
            'type': 'Storage',
            'source': 'storage-array-02',
            'description': 'Disk space trending to full (92% used)',
            'severity': 'Warning'
        }
    ]
    
    # Apply filtering
    if filter_type.lower() != 'all':
        anomalies = [a for a in anomalies if a['severity'].lower() == filter_type.lower()]
    
    return jsonify({
        'success': True,
        'anomalies': anomalies
    })
