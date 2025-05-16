"""
Mock API Services

This module provides mock implementations of API services for development
when the real services like Kafka and Apache NiFi are not available.
"""

import random
import time
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_dashboard_metrics():
    """Get mock dashboard metrics for display"""
    # Mock LLM usage metrics
    llm_metrics = {
        'total_requests': random.randint(1200, 1500),
        'today_requests': random.randint(80, 150),
        'avg_latency': random.randint(250, 500),
        'success_rate': random.uniform(96.5, 99.9)
    }
    
    # Mock Kafka metrics
    kafka_metrics = {
        'topics': random.randint(8, 12),
        'producers': random.randint(3, 7),
        'consumers': random.randint(5, 10),
        'msg_per_sec': random.randint(50, 200)
    }
    
    # Mock pipeline metrics
    pipeline_metrics = {
        'active_workflows': random.randint(3, 8),
        'completed_jobs': random.randint(120, 180),
        'failed_jobs': random.randint(3, 12),
        'avg_processing_time': random.randint(30, 120)
    }
    
    # Mock anomaly metrics
    anomaly_metrics = {
        'detected_today': random.randint(5, 15),
        'critical': random.randint(1, 3),
        'warning': random.randint(3, 8),
        'info': random.randint(5, 15),
        'false_positives': random.randint(2, 8)
    }
    
    # Combine all metrics
    metrics = {
        'llm': llm_metrics,
        'kafka': kafka_metrics,
        'pipeline': pipeline_metrics,
        'anomaly': anomaly_metrics,
        
        # Time series data for charts
        'time_series': {
            'labels': _generate_time_labels(12),
            'llm_requests': _generate_random_series(12, 50, 150),
            'pipeline_jobs': _generate_random_series(12, 20, 80),
            'anomalies': _generate_random_series(12, 2, 15),
            'kafka_throughput': _generate_random_series(12, 100, 500)
        }
    }
    
    return metrics

def get_recent_kafka_messages():
    """Get mock recent Kafka messages"""
    message_types = ['user.event', 'transaction', 'system.log', 'notification', 'analytics']
    topics = ['users', 'transactions', 'logs', 'notifications', 'analytics', 'events']
    
    messages = []
    for _ in range(10):
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 60))
        msg_type = random.choice(message_types)
        
        # Generate sample message based on type
        if msg_type == 'user.event':
            content = {
                'user_id': f'user_{random.randint(1000, 9999)}',
                'event': random.choice(['login', 'logout', 'profile_update', 'password_change']),
                'ip': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'device': random.choice(['mobile', 'desktop', 'tablet'])
            }
        elif msg_type == 'transaction':
            content = {
                'transaction_id': f'tx_{random.randint(10000, 99999)}',
                'amount': round(random.uniform(10.5, 999.99), 2),
                'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
                'status': random.choice(['completed', 'pending', 'failed'])
            }
        else:
            # Generic message for other types
            content = {
                'id': f'msg_{random.randint(1000, 9999)}',
                'level': random.choice(['info', 'warning', 'error', 'debug']),
                'service': random.choice(['api', 'auth', 'database', 'cache', 'search']),
                'data': f'Sample data {random.randint(1, 100)}'
            }
            
        messages.append({
            'id': f'msg_{random.randint(10000, 99999)}',
            'topic': random.choice(topics),
            'type': msg_type,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'size': random.randint(100, 2000),
            'content': json.dumps(content)
        })
    
    return messages

def get_pipeline_status():
    """Get mock pipeline status information"""
    # Status options
    status_options = ['running', 'completed', 'failed', 'pending', 'queued']
    pipeline_types = ['data_ingest', 'transformation', 'analysis', 'export', 'notification', 'backup']
    
    # Generate active pipelines
    active_pipelines = []
    for i in range(random.randint(3, 8)):
        start_time = datetime.now() - timedelta(minutes=random.randint(5, 120))
        
        status = random.choice(status_options)
        progress = 100 if status == 'completed' else random.randint(0, 99)
        
        pipeline = {
            'id': f'pipe_{random.randint(1000, 9999)}',
            'name': f'{random.choice(pipeline_types)}_pipeline_{i+1}',
            'status': status,
            'progress': progress,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'runtime': random.randint(5, 300),
            'nodes': random.randint(3, 15),
            'data_processed': f'{random.randint(1, 999)} MB',
            'owner': f'user_{random.randint(100, 999)}'
        }
        
        active_pipelines.append(pipeline)
    
    # Generate recent executions
    recent_executions = []
    for i in range(random.randint(5, 10)):
        end_time = datetime.now() - timedelta(hours=random.randint(1, 48))
        start_time = end_time - timedelta(minutes=random.randint(5, 120))
        
        status = random.choice(['completed', 'failed', 'terminated'])
        
        execution = {
            'id': f'exec_{random.randint(10000, 99999)}',
            'pipeline_id': f'pipe_{random.randint(1000, 9999)}',
            'name': f'{random.choice(pipeline_types)}_execution_{i+1}',
            'status': status,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': random.randint(5, 300),
            'data_processed': f'{random.randint(1, 999)} MB',
            'error': 'Sample error message' if status == 'failed' else None
        }
        
        recent_executions.append(execution)
    
    # Combine pipeline data
    pipeline_data = {
        'active_pipelines': active_pipelines,
        'recent_executions': recent_executions,
        'system_status': {
            'cpu_usage': random.randint(10, 95),
            'memory_usage': random.randint(20, 90),
            'disk_space': random.randint(15, 85),
            'node_count': random.randint(3, 8),
            'queue_size': random.randint(0, 50)
        }
    }
    
    return pipeline_data

def get_latest_anomalies():
    """Get mock latest anomalies information"""
    anomaly_types = ['network', 'system', 'application', 'security', 'performance', 'database']
    severity_levels = ['critical', 'warning', 'info']
    components = ['api-server', 'database', 'cache', 'frontend', 'auth-service', 'file-storage']
    
    # Generate anomalies
    anomalies = []
    for i in range(random.randint(5, 15)):
        detected_time = datetime.now() - timedelta(minutes=random.randint(5, 1440))
        
        severity = random.choice(severity_levels)
        anomaly_type = random.choice(anomaly_types)
        
        # Generate a realistic message based on type and severity
        if anomaly_type == 'network':
            message = random.choice([
                'Unusual network latency detected',
                'Network packet loss above threshold',
                'Connection timeout to external service',
                'DNS resolution failure'
            ])
        elif anomaly_type == 'system':
            message = random.choice([
                'CPU utilization spike',
                'Memory usage exceeding threshold',
                'Disk space critically low',
                'Unusual system load detected'
            ])
        elif anomaly_type == 'database':
            message = random.choice([
                'Slow query performance detected',
                'Database connection pool exhausted',
                'Deadlock detected in transaction',
                'Unusual query pattern detected'
            ])
        else:
            message = f'Anomaly detected in {anomaly_type} component'
        
        anomaly = {
            'id': f'anomaly_{random.randint(1000, 9999)}',
            'type': anomaly_type,
            'severity': severity,
            'component': random.choice(components),
            'message': message,
            'detected_at': detected_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': random.choice(['new', 'investigating', 'resolved', 'false_positive']),
            'value': round(random.uniform(0.1, 1.0), 2),
            'threshold': round(random.uniform(0.1, 0.9), 2)
        }
        
        anomalies.append(anomaly)
    
    return anomalies

def get_anomaly_stats():
    """Get mock anomaly statistics"""
    # Generate daily counts for the last 14 days
    days = 14
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    dates.reverse()  # Put in chronological order
    
    critical_values = _generate_random_series(days, 0, 5)
    warning_values = _generate_random_series(days, 2, 12)
    info_values = _generate_random_series(days, 5, 25)
    
    # Generate component breakdown
    components = ['api-server', 'database', 'cache', 'frontend', 'auth-service', 'file-storage']
    component_data = {}
    
    for component in components:
        component_data[component] = random.randint(5, 30)
    
    # Generate type breakdown
    anomaly_types = ['network', 'system', 'application', 'security', 'performance', 'database']
    type_data = {}
    
    for anomaly_type in anomaly_types:
        type_data[anomaly_type] = random.randint(5, 30)
    
    # Combine all stats
    stats = {
        'total_anomalies': sum(critical_values) + sum(warning_values) + sum(info_values),
        'critical_count': sum(critical_values),
        'warning_count': sum(warning_values),
        'info_count': sum(info_values),
        'false_positive_rate': round(random.uniform(0.05, 0.15), 2),
        'avg_resolution_time': random.randint(30, 240),
        
        'time_series': {
            'labels': dates,
            'critical': critical_values,
            'warning': warning_values,
            'info': info_values
        },
        
        'components': component_data,
        'types': type_data
    }
    
    return stats

def get_anomalies_list(params=None):
    """
    Get a list of mock anomalies with optional filtering
    
    Args:
        params: Dictionary with filtering parameters
            - severity: Filter by severity level
            - component: Filter by component
            - status: Filter by status
            - date_from: Filter from date
            - date_to: Filter to date
            - page: Page number
            - limit: Results per page
    """
    params = params or {}
    
    # Use params for filtering (in a real implementation)
    page = int(params.get('page', 1))
    limit = int(params.get('limit', 20))
    
    # Get base anomalies
    all_anomalies = get_latest_anomalies()
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    anomalies = all_anomalies[start_idx:end_idx]
    
    # Return with pagination metadata
    return {
        'anomalies': anomalies,
        'total': len(all_anomalies),
        'page': page,
        'limit': limit,
        'pages': (len(all_anomalies) + limit - 1) // limit
    }

# Helper functions
def _generate_time_labels(count):
    """Generate time labels for charts"""
    now = datetime.now()
    labels = []
    
    for i in range(count):
        time_point = now - timedelta(hours=i)
        labels.append(time_point.strftime('%H:%M'))
    
    labels.reverse()  # Put in chronological order
    return labels

def _generate_random_series(count, min_val, max_val):
    """Generate a series of random values"""
    return [random.randint(min_val, max_val) for _ in range(count)]