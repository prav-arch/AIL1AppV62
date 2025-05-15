"""
Kafka Browser routes for the AI Assistant Platform.
Handles Kafka topic and message management.
"""

from flask import Blueprint, render_template, request, jsonify, session
from db import execute_query
import logging
import json
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
kafka_browser_bp = Blueprint('kafka_browser', __name__, url_prefix='/kafka_browser')

@kafka_browser_bp.route('/')
def index():
    """Kafka Browser main page."""
    # Get Kafka topics from database
    topics = get_kafka_topics()
    
    # Get consumer groups
    consumer_groups = get_consumer_groups()
    
    return render_template(
        'kafka_browser.html', 
        topics=topics,
        consumer_groups=consumer_groups
    )

@kafka_browser_bp.route('/topics', methods=['GET'])
def list_topics():
    """List Kafka topics."""
    topics = get_kafka_topics()
    return jsonify({'topics': topics})

@kafka_browser_bp.route('/topics', methods=['POST'])
def create_topic():
    """Create a new Kafka topic."""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        partition_count = data.get('partition_count', 1)
        replication_factor = data.get('replication_factor', 1)
        
        # Validate inputs
        if not name:
            return jsonify({'error': 'Topic name is required'}), 400
        
        # Add topic to database
        topic_id = execute_query("""
            INSERT INTO kafka_topics (name, description, partition_count, replication_factor, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (name, description, partition_count, replication_factor, datetime.now()))
        
        return jsonify({
            'success': True,
            'topic_id': topic_id[0]['id'] if topic_id else None,
            'message': f'Topic {name} created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating Kafka topic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@kafka_browser_bp.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    """Get a specific Kafka topic."""
    try:
        # Get topic from database
        topic = execute_query("""
            SELECT * FROM kafka_topics WHERE id = %s
        """, (topic_id,))
        
        if not topic:
            return jsonify({'error': 'Topic not found'}), 404
            
        # Get message count
        message_count = execute_query("""
            SELECT COUNT(*) as count FROM kafka_messages WHERE topic_id = %s
        """, (topic_id,))
        
        topic = topic[0]
        topic['message_count'] = message_count[0]['count'] if message_count else 0
        
        return jsonify({'topic': topic})
        
    except Exception as e:
        logger.error(f"Error getting Kafka topic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@kafka_browser_bp.route('/topics/<int:topic_id>/messages', methods=['GET'])
def get_topic_messages(topic_id):
    """Get messages for a Kafka topic."""
    try:
        # Get pagination parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Get messages from database
        messages = execute_query("""
            SELECT * FROM kafka_messages 
            WHERE topic_id = %s
            ORDER BY timestamp DESC, "offset" DESC
            LIMIT %s OFFSET %s
        """, (topic_id, limit, offset))
        
        # Get total count
        count = execute_query("""
            SELECT COUNT(*) as count FROM kafka_messages WHERE topic_id = %s
        """, (topic_id,))
        
        return jsonify({
            'messages': messages if messages else [],
            'total': count[0]['count'] if count else 0
        })
        
    except Exception as e:
        logger.error(f"Error getting Kafka messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@kafka_browser_bp.route('/topics/<int:topic_id>/messages', methods=['POST'])
def publish_message(topic_id):
    """Publish a message to a Kafka topic."""
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')
        headers = data.get('headers')
        
        # Validate inputs
        if not value:
            return jsonify({'error': 'Message value is required'}), 400
        
        # Get topic from database
        topic = execute_query("""
            SELECT * FROM kafka_topics WHERE id = %s
        """, (topic_id,))
        
        if not topic:
            return jsonify({'error': 'Topic not found'}), 404
        
        # Get highest offset for this topic/partition
        last_offset = execute_query("""
            SELECT MAX("offset") as max_offset FROM kafka_messages 
            WHERE topic_id = %s AND partition = 0
        """, (topic_id,))
        
        next_offset = (last_offset[0]['max_offset'] + 1 if last_offset and last_offset[0]['max_offset'] is not None else 0)
        
        # Add message to database
        message_id = execute_query("""
            INSERT INTO kafka_messages (topic_id, partition, "offset", key, value, headers, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (topic_id, 0, next_offset, key, value, 
              json.dumps(headers) if headers else None, datetime.now()))
        
        return jsonify({
            'success': True,
            'message_id': message_id[0]['id'] if message_id else None,
            'offset': next_offset
        })
        
    except Exception as e:
        logger.error(f"Error publishing Kafka message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@kafka_browser_bp.route('/consumer_groups', methods=['GET'])
def list_consumer_groups():
    """List Kafka consumer groups."""
    consumer_groups = get_consumer_groups()
    return jsonify({'consumer_groups': consumer_groups})

# Helper functions
def get_kafka_topics():
    """Get Kafka topics."""
    try:
        topics = execute_query("""
            SELECT t.*, COUNT(m.id) as message_count
            FROM kafka_topics t
            LEFT JOIN kafka_messages m ON t.id = m.topic_id
            GROUP BY t.id
            ORDER BY t.name
        """)
        
        return topics if topics else []
    except Exception as e:
        logger.error(f"Error getting Kafka topics: {str(e)}")
        return []

def get_consumer_groups():
    """Get Kafka consumer groups."""
    try:
        groups = execute_query("""
            SELECT * FROM kafka_consumer_groups
            ORDER BY name
        """)
        
        return groups if groups else []
    except Exception as e:
        logger.error(f"Error getting Kafka consumer groups: {str(e)}")
        return []