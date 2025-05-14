import os
import logging
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
    return render_template('rag.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000, debug=True)