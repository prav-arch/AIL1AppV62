"""
Dashboard routes for the AI Assistant Platform.
Displays overview and metrics from all system components.
"""

from flask import Blueprint, render_template, request, jsonify
from db import execute_query
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    """Dashboard main page with overview of all system components."""
    try:
        # Get counts from database
        conversation_count = get_conversation_count()
        document_count = get_document_count()
        anomaly_count = get_anomaly_count()
        active_jobs_count = get_active_jobs_count()
        
        # Get some recent activity
        recent_activity = get_recent_activity(limit=5)
        
        # Render dashboard template with stats
        return render_template(
            'dashboard.html',
            conversation_count=conversation_count,
            document_count=document_count,
            anomaly_count=anomaly_count,
            active_jobs_count=active_jobs_count,
            recent_activity=recent_activity
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('dashboard.html', error=str(e))

@dashboard_bp.route('/stats')
def get_stats():
    """API endpoint to get current system stats."""
    try:
        # Get counts from database
        conversation_count = get_conversation_count()
        document_count = get_document_count()
        anomaly_count = get_anomaly_count()
        active_jobs_count = get_active_jobs_count()
        
        # Return JSON response
        return jsonify({
            'conversation_count': conversation_count,
            'document_count': document_count,
            'anomaly_count': anomaly_count,
            'active_jobs_count': active_jobs_count
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper functions to get stats from database
def get_conversation_count():
    """Get count of conversations."""
    try:
        result = execute_query("SELECT COUNT(*) FROM conversations")
        return result[0]['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting conversation count: {str(e)}")
        return 0

def get_document_count():
    """Get count of documents."""
    try:
        result = execute_query("SELECT COUNT(*) FROM documents")
        return result[0]['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting document count: {str(e)}")
        return 0

def get_anomaly_count():
    """Get count of anomalies."""
    try:
        result = execute_query("SELECT COUNT(*) FROM anomalies WHERE status = 'open'")
        return result[0]['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting anomaly count: {str(e)}")
        return 0

def get_active_jobs_count():
    """Get count of active jobs."""
    try:
        # Get count of active pipeline jobs
        result = execute_query("""
            SELECT COUNT(*) FROM job_runs 
            WHERE status = 'running'
        """)
        return result[0]['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting active jobs count: {str(e)}")
        return 0

def get_recent_activity(limit=5):
    """Get recent activity across the system."""
    try:
        result = execute_query("""
            SELECT action, entity_type, timestamp 
            FROM activity_logs 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        return result if result else []
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return []