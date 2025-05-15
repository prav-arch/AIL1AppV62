from flask import Blueprint, render_template, request, jsonify
import random
from datetime import datetime, timedelta

kafka_browser_bp = Blueprint('kafka_browser', __name__, url_prefix='/kafka-browser')

@kafka_browser_bp.route('/')
def index():
    return render_template('kafka_browser.html')

@kafka_browser_bp.route('/api/kafka/topics', methods=['GET'])
def get_kafka_topics():
    """Return list of Kafka topics"""
    topics = [
        {
            'name': 'logs-topic',
            'partitions': 3,
            'replication_factor': 3,
            'message_count': 524892,
            'created': '2023-05-01 00:00:00'
        },
        {
            'name': 'metrics-topic',
            'partitions': 5,
            'replication_factor': 3,
            'message_count': 328157,
            'created': '2023-05-01 00:00:00'
        },
        {
            'name': 'events-topic',
            'partitions': 2,
            'replication_factor': 3,
            'message_count': 102458,
            'created': '2023-05-02 00:00:00'
        },
        {
            'name': 'alerts-topic',
            'partitions': 1,
            'replication_factor': 3,
            'message_count': 1458,
            'created': '2023-05-02 00:00:00'
        },
        {
            'name': 'system-topic',
            'partitions': 1,
            'replication_factor': 3,
            'message_count': 89254,
            'created': '2023-05-03 00:00:00'
        }
    ]
    
    # Add some additional stats
    stats = {
        'broker_count': 3,
        'total_topics': len(topics),
        'consumer_groups': 8,
        'total_messages': sum(t['message_count'] for t in topics)
    }
    
    return jsonify({
        'topics': topics,
        'stats': stats
    })

@kafka_browser_bp.route('/api/kafka/messages', methods=['GET'])
def get_kafka_messages():
    """Return messages for a specific Kafka topic"""
    topic = request.args.get('topic', 'logs-topic')
    
    # Generate random messages based on the topic
    messages = []
    for i in range(20):  # Return 20 messages
        offset = random.randint(1000, 100000)
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 60))
        
        if topic == 'logs-topic':
            content = get_random_log_message()
        elif topic == 'metrics-topic':
            content = get_random_metric_message()
        elif topic == 'alerts-topic':
            content = get_random_alert_message()
        else:
            content = f"Message content for {topic} - {i+1}"
        
        messages.append({
            'id': f"{topic}-{offset}",
            'offset': offset,
            'partition': random.randint(0, 2),
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'key': f"key-{random.randint(1, 10)}",
            'content': content,
            'size': random.randint(100, 2000)
        })
    
    # Sort by offset descending (newest first)
    messages.sort(key=lambda x: x['offset'], reverse=True)
    
    return jsonify({
        'topic': topic,
        'messages': messages,
        'stats': {
            'total': random.randint(10000, 1000000),
            'rate': f"{random.randint(10, 500)} msg/s"
        }
    })

@kafka_browser_bp.route('/api/kafka/consumer-groups', methods=['GET'])
def get_consumer_groups():
    """Return Kafka consumer groups"""
    consumer_groups = [
        {
            'name': 'log-processor',
            'members': 3,
            'topics': ['logs-topic'],
            'status': 'Active'
        },
        {
            'name': 'metrics-analyzer',
            'members': 5,
            'topics': ['metrics-topic'],
            'status': 'Active'
        },
        {
            'name': 'alert-handler',
            'members': 2,
            'topics': ['alerts-topic'],
            'status': 'Active'
        },
        {
            'name': 'event-processor',
            'members': 3,
            'topics': ['events-topic'],
            'status': 'Active'
        },
        {
            'name': 'system-monitor',
            'members': 1,
            'topics': ['system-topic'],
            'status': 'Active'
        },
        {
            'name': 'data-archiver',
            'members': 2,
            'topics': ['logs-topic', 'metrics-topic'],
            'status': 'Rebalancing'
        },
        {
            'name': 'backup-service',
            'members': 1,
            'topics': ['logs-topic', 'alerts-topic', 'system-topic'],
            'status': 'Active'
        },
        {
            'name': 'analytics-service',
            'members': 4,
            'topics': ['metrics-topic', 'events-topic'],
            'status': 'Active'
        }
    ]
    
    return jsonify(consumer_groups)

# Helper functions for message generation
def get_random_log_message():
    """Generate a random log message for logs-topic"""
    log_levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
    services = ['api-server', 'auth-service', 'database', 'cache', 'web-frontend']
    messages = [
        "User authentication successful",
        "Request processed in 235ms",
        "Database query completed",
        "Cache miss for key: user_profile",
        "Connection established with client",
        "Session expired for user",
        "File upload completed",
        "Background job started",
        "Memory usage: 78%"
    ]
    
    return f"[{random.choice(log_levels)}] {random.choice(services)}: {random.choice(messages)}"

def get_random_metric_message():
    """Generate a random metric message for metrics-topic"""
    metric_types = ['cpu', 'memory', 'disk', 'network', 'requests', 'latency']
    services = ['api', 'auth', 'db', 'cache', 'web']
    
    metric = random.choice(metric_types)
    service = random.choice(services)
    value = random.randint(1, 100)
    
    return f'{{\"service\": \"{service}\", \"{metric}\": {value}, \"unit\": \"%\", \"timestamp\": \"2023-05-20T12:34:56Z\"}}'

def get_random_alert_message():
    """Generate a random alert message for alerts-topic"""
    alert_levels = ['critical', 'warning', 'info']
    alert_types = ['performance', 'security', 'availability', 'error']
    services = ['api-server', 'auth-service', 'database', 'cache', 'web-frontend']
    
    level = random.choice(alert_levels)
    alert_type = random.choice(alert_types)
    service = random.choice(services)
    
    messages = {
        'critical': [
            f"Service {service} is down",
            f"Database connection pool exhausted",
            f"Memory leak detected in {service}",
            f"Disk space critically low (95%)"
        ],
        'warning': [
            f"High CPU usage (85%) in {service}",
            f"Increased error rate (5%)",
            f"Slow database queries detected",
            f"API rate limit approaching threshold"
        ],
        'info': [
            f"Service {service} restarted successfully",
            f"Scheduled maintenance completed",
            f"New deployment successful",
            f"Backup process completed"
        ]
    }
    
    return f'{{\"level\": \"{level}\", \"type\": \"{alert_type}\", \"service\": \"{service}\", \"message\": \"{random.choice(messages[level])}\"}}'