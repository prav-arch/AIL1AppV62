"""
Anomaly detection routes for the AI Assistant Platform.
Handles time series data and anomaly detection.
"""

from flask import Blueprint, render_template, request, jsonify, session
from db import execute_query, add_time_series_data, add_anomaly, get_anomalies
import logging
import time
from datetime import datetime, timedelta
import json
import numpy as np

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
anomalies_bp = Blueprint('anomalies', __name__, url_prefix='/anomalies')

@anomalies_bp.route('/')
def index():
    """Anomaly detection main page."""
    # Get anomalies from database
    anomalies = get_anomalies(limit=10)
    
    # Get time series list
    time_series = get_time_series_list()
    
    return render_template(
        'anomalies.html', 
        anomalies=anomalies,
        time_series=time_series
    )

@anomalies_bp.route('/data', methods=['POST'])
def add_data():
    """Add time series data."""
    try:
        # Get data from request
        data = request.json
        source = data.get('source')
        metric_name = data.get('metric_name')
        value = data.get('value')
        timestamp = data.get('timestamp')
        tags = data.get('tags')
        
        # Validate inputs
        if not source or not metric_name or value is None:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse timestamp or use current time
        if timestamp:
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                return jsonify({'error': 'Invalid timestamp format'}), 400
        else:
            timestamp = datetime.now()
        
        # Add time series data
        time_series_id = add_time_series_data(
            source=source,
            metric_name=metric_name,
            timestamp=timestamp,
            value=float(value),
            tags=json.dumps(tags) if tags else None
        )
        
        # Check for anomalies
        detect_anomalies(time_series_id, source, metric_name)
        
        return jsonify({
            'success': True,
            'time_series_id': time_series_id
        })
        
    except Exception as e:
        logger.error(f"Error adding time series data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@anomalies_bp.route('/list', methods=['GET'])
def list_anomalies():
    """List anomalies."""
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    
    anomalies = get_anomalies(status, limit)
    
    return jsonify({'anomalies': anomalies})

@anomalies_bp.route('/update_status', methods=['POST'])
def update_anomaly_status():
    """Update anomaly status."""
    try:
        data = request.json
        anomaly_id = data.get('anomaly_id')
        status = data.get('status')
        
        if not anomaly_id or not status:
            return jsonify({'error': 'Missing anomaly_id or status'}), 400
        
        # Update status in database
        execute_query("""
            UPDATE anomalies SET status = %s WHERE id = %s
        """, (status, anomaly_id), fetch=False)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating anomaly status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@anomalies_bp.route('/time_series/<string:source>/<string:metric_name>/data', methods=['GET'])
def get_time_series_data(source, metric_name):
    """Get time series data for a specific source and metric."""
    try:
        # Get time range from request
        hours = int(request.args.get('hours', 24))
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get data from database
        data = execute_query("""
            SELECT timestamp, value 
            FROM time_series 
            WHERE source = %s AND metric_name = %s AND timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp
        """, (source, metric_name, start_time, end_time))
        
        # Format for chart
        chart_data = []
        for row in data:
            chart_data.append({
                'timestamp': row['timestamp'].isoformat(),
                'value': float(row['value'])
            })
        
        return jsonify({'data': chart_data})
        
    except Exception as e:
        logger.error(f"Error getting time series data: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_time_series_list():
    """Get list of time series."""
    try:
        # Get distinct source and metric combinations
        data = execute_query("""
            SELECT DISTINCT source, metric_name 
            FROM time_series 
            ORDER BY source, metric_name
        """)
        
        return data if data else []
        
    except Exception as e:
        logger.error(f"Error getting time series list: {str(e)}")
        return []

def detect_anomalies(time_series_id, source, metric_name):
    """
    Detect anomalies in time series data.
    
    This is a simple implementation that uses Z-scores for anomaly detection.
    More advanced algorithms would be used in a production environment.
    """
    try:
        # Get recent data for this source and metric
        hours = 24
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        data = execute_query("""
            SELECT id, timestamp, value 
            FROM time_series 
            WHERE source = %s AND metric_name = %s AND timestamp >= %s
            ORDER BY timestamp
        """, (source, metric_name, start_time))
        
        if not data or len(data) < 10:
            # Not enough data for anomaly detection
            return
        
        # Extract values
        values = [row['value'] for row in data]
        
        # Calculate mean and standard deviation
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            # All values are the same, no anomalies
            return
        
        # Calculate Z-scores
        z_scores = [(value - mean) / std for value in values]
        
        # Check if the last value is an anomaly (Z-score > 3)
        last_z_score = abs(z_scores[-1])
        if last_z_score > 3:
            # This is an anomaly
            severity = min(1.0, last_z_score / 10)  # Scale to 0-1
            
            # Add anomaly to database
            anomaly_id = add_anomaly(
                time_series_id=time_series_id,
                algorithm='z_score',
                start_time=end_time,
                severity=severity,
                score=last_z_score
            )
            
            logger.info(f"Detected anomaly {anomaly_id} with severity {severity}")
            
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        # Don't re-raise, we don't want this to affect data ingestion