"""
Anomalies routes module
This module provides routes for anomaly detection and recommendations.
"""
import json
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from services.anomaly_detection import get_anomalies, get_anomaly_recommendations, get_anomaly_stats

anomalies_bp = Blueprint('anomalies', __name__)

@anomalies_bp.route('/anomalies')
def anomalies_page():
    """
    Render the anomalies page with detected anomalies
    """
    return render_template('anomalies.html')

@anomalies_bp.route('/anomalies/recommendations/<anomaly_id>')
def anomaly_recommendations_page(anomaly_id):
    """
    Render the recommendations page for a specific anomaly
    """
    return render_template('recommendations.html', anomaly_id=anomaly_id)

@anomalies_bp.route('/api/anomalies')
def api_anomalies_list():
    """
    API endpoint to get the list of detected anomalies
    
    Query Parameters:
        - severity (optional): Filter by minimum severity level
        - component (optional): Filter by component name
        - type (optional): Filter by anomaly type
        - sort (optional): Sort by 'severity', 'timestamp', or 'type'
    """
    # Get query parameters
    severity = request.args.get('severity', default=None, type=int)
    component = request.args.get('component', default=None, type=str)
    anomaly_type = request.args.get('type', default=None, type=str)
    sort_by = request.args.get('sort', default='severity', type=str)
    
    # Get all anomalies
    anomalies = get_anomalies()
    
    # Apply filters
    if severity is not None:
        anomalies = [a for a in anomalies if a.get('severity', 0) >= severity]
    
    if component is not None:
        anomalies = [a for a in anomalies if component.lower() in a.get('component', '').lower()]
    
    if anomaly_type is not None:
        anomalies = [a for a in anomalies if anomaly_type.lower() in a.get('type', '').lower()]
    
    # Apply sorting
    if sort_by == 'timestamp':
        anomalies = sorted(anomalies, key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_by == 'type':
        anomalies = sorted(anomalies, key=lambda x: x.get('type', ''))
    # Default is already severity
    
    return jsonify({
        'success': True,
        'count': len(anomalies),
        'anomalies': anomalies
    })

@anomalies_bp.route('/api/anomalies/stats')
def api_anomaly_stats():
    """
    API endpoint to get statistics about detected anomalies
    """
    stats = get_anomaly_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

@anomalies_bp.route('/api/anomalies/recommendations/<anomaly_id>')
def api_anomaly_recommendations(anomaly_id):
    """
    API endpoint to get recommendations for a specific anomaly
    """
    recommendations = get_anomaly_recommendations(anomaly_id)
    return jsonify({
        'success': True,
        'recommendations': recommendations
    })