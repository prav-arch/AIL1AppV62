from flask import Blueprint, render_template, request, jsonify
import random
import json
import numpy as np
from datetime import datetime, timedelta
import logging

from services.anomaly_detection import (
    AnomalyDetectionService, 
    AnomalyAlgorithm, 
    AnomalyDetector,
    AnomalyResult
)

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Initialize the anomaly detection service
anomaly_service = AnomalyDetectionService()

# Create some default detectors with different algorithms
anomaly_service.create_detector("zscore", AnomalyAlgorithm.ZSCORE, {"threshold": 3.0})
anomaly_service.create_detector("iqr", AnomalyAlgorithm.IQR, {"k": 1.5})
anomaly_service.create_detector("isolation_forest", AnomalyAlgorithm.ISOLATION_FOREST, {"contamination": 0.05})
anomaly_service.create_detector("one_class_svm", AnomalyAlgorithm.ONE_CLASS_SVM, {"nu": 0.05})
anomaly_service.create_detector("dbscan", AnomalyAlgorithm.DBSCAN, {"eps": 0.5})
anomaly_service.create_detector("lof", AnomalyAlgorithm.LOF, {"n_neighbors": 20})
anomaly_service.create_detector("arima", AnomalyAlgorithm.ARIMA, {"order": (5, 1, 0)})

anomalies_bp = Blueprint('anomalies', __name__, url_prefix='/anomalies')

@anomalies_bp.route('/')
def index():
    return render_template('anomalies.html')

@anomalies_bp.route('/api/anomalies/stats', methods=['GET'])
def get_anomaly_stats():
    """Return statistics about anomalies"""
    total = random.randint(20, 30)
    critical = random.randint(3, 8)
    warning = random.randint(8, 15)
    info = total - critical - warning
    
    stats = {
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

@anomalies_bp.route('/api/anomalies', methods=['GET'])
def get_anomalies():
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
        },
        {
            'id': 'A-1277',
            'timestamp': '2023-05-20 08:35:19',
            'type': 'Network',
            'source': 'switch-core-01',
            'description': 'Packet loss rate exceeding threshold (1.5%)',
            'severity': 'Warning'
        },
        {
            'id': 'A-1276',
            'timestamp': '2023-05-20 07:22:54',
            'type': 'System',
            'source': 'monitoring-server',
            'description': 'NTP time drift detected (2.5s)',
            'severity': 'Info'
        },
        {
            'id': 'A-1275',
            'timestamp': '2023-05-20 06:18:42',
            'type': 'Application',
            'source': 'mobile-api',
            'description': 'Increased 4xx responses (8% of requests)',
            'severity': 'Info'
        }
    ]
    
    # Apply filtering
    if filter_type.lower() != 'all':
        anomalies = [a for a in anomalies if a['severity'].lower() == filter_type.lower()]
    
    return jsonify(anomalies)

@anomalies_bp.route('/api/anomalies/<anomaly_id>/recommendation', methods=['GET'])
def get_anomaly_recommendation(anomaly_id):
    """Get LLM recommendation for an anomaly"""
    # Sample recommendations for different anomaly types
    recommendations = {
        'Network': [
            "1. **Analyze Traffic Patterns**: Review traffic logs to identify the source and destination of the unusual traffic spike.",
            "2. **Check for DDoS Attack**: Verify if this is a potential DDoS attack by analyzing packet signatures and IP distributions.",
            "3. **Rate Limiting**: Implement temporary rate limiting on affected interfaces.",
            "4. **Update Firewall Rules**: Add temporary filtering rules to block suspicious traffic sources.",
            "5. **Increase Monitoring**: Set up real-time alerts for similar patterns in the next 24 hours."
        ],
        'System': [
            "1. **Identify Memory-Intensive Processes**: Use `top` or `htop` to identify processes consuming excessive memory.",
            "2. **Check for Memory Leaks**: Review application logs for evidence of memory leaks.",
            "3. **Increase Swap Space**: Temporarily increase swap space to prevent immediate service disruption.",
            "4. **Restart Memory-Intensive Services**: Consider restarting problematic services during low-traffic periods.",
            "5. **Scale Resources**: If this is a persistent issue, consider scaling up the server's memory resources."
        ],
        'Database': [
            "1. **Analyze Slow Queries**: Use database monitoring tools to identify slow-running queries.",
            "2. **Check Indexing**: Verify that proper indexes are in place for common query patterns.",
            "3. **Review Recent Schema Changes**: Check if any recent schema changes might be affecting performance.",
            "4. **Database Cache**: Ensure the database cache is properly sized and functioning.",
            "5. **Connection Pooling**: Verify connection pooling is correctly configured to handle the current load."
        ],
        'Security': [
            "1. **Lock Down Affected Accounts**: Temporarily lock any accounts associated with the suspicious activity.",
            "2. **IP Blocking**: Add the suspicious IP addresses to your firewall block list.",
            "3. **Enable Additional Authentication**: Consider implementing two-factor authentication for affected services.",
            "4. **Review Authentication Logs**: Check for patterns or indications of credential stuffing attacks.",
            "5. **Update Intrusion Detection Rules**: Adjust your IDS rules to better catch similar future attempts."
        ],
        'Application': [
            "1. **Code Profiling**: Run application profiling to identify bottlenecks in the request handling path.",
            "2. **Database Query Optimization**: Check if slow database queries are affecting API response times.",
            "3. **Caching Implementation**: Implement or review caching strategies for frequently accessed data.",
            "4. **Load Balancing**: Ensure load balancing is correctly distributing requests.",
            "5. **Service Dependencies**: Check if downstream service dependencies are experiencing issues."
        ],
        'Storage': [
            "1. **Clean Temporary Files**: Remove unused temporary files and clear log archives.",
            "2. **Review Large Directories**: Identify and address directories consuming excessive space.",
            "3. **Implement Disk Quotas**: Set up disk quotas to prevent any single user or service from filling the disk.",
            "4. **Archive Old Data**: Move older, infrequently accessed data to lower-tier storage.",
            "5. **Storage Expansion**: Plan for storage expansion if current capacity is consistently near capacity."
        ],
        'Time Series': [
            "1. **Check for Seasonality**: Analyze for regular patterns or seasonal effects that might explain the anomaly.",
            "2. **External Factors**: Investigate external events that might correlate with the anomalous time period.",
            "3. **Smoothing Techniques**: Apply moving averages or exponential smoothing to reduce noise and better visualize trends.",
            "4. **Decomposition Analysis**: Break down the time series into trend, seasonal, and residual components.",
            "5. **Adjust Threshold Parameters**: Fine-tune detection thresholds based on historical data analysis."
        ]
    }
    
    # Find the anomaly by ID
    anomaly = None
    all_anomalies = [
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
            'type': 'Time Series',
            'source': 'metrics-server-01',
            'description': 'Anomalous pattern detected in CPU utilization time series',
            'severity': 'Warning',
            'algorithm': 'ARIMA'
        },
        {
            'id': 'A-1277',
            'timestamp': '2023-05-20 08:35:19',
            'type': 'Time Series',
            'source': 'metrics-server-01',
            'description': 'Outlier detected in network latency measurements',
            'severity': 'Critical',
            'algorithm': 'Isolation Forest'
        }
    ]
    
    for a in all_anomalies:
        if a['id'] == anomaly_id:
            anomaly = a
            break
    
    if not anomaly:
        return jsonify({'error': 'Anomaly not found'}), 404
    
    # Get similar past incidents
    similar_incidents = get_similar_incidents(anomaly['type'], anomaly['severity'])
    
    return jsonify({
        'anomaly': anomaly,
        'recommendation': recommendations.get(anomaly['type'], recommendations['System']),
        'similar_incidents': similar_incidents
    })

@anomalies_bp.route('/api/anomaly-detection/detect', methods=['POST'])
def detect_anomalies():
    """Detect anomalies in time series data using the specified algorithm"""
    try:
        # Parse the request data
        data = request.json
        
        # Extract the required fields
        time_series_data = data.get('data')
        algorithm_name = data.get('algorithm', 'zscore')
        params = data.get('params', {})
        
        # Validate the data
        if not time_series_data or not isinstance(time_series_data, list):
            return jsonify({'error': 'Invalid or missing time series data'}), 400
        
        # Convert data to numpy array and ensure it's numeric
        try:
            numeric_data = np.array([float(x) for x in time_series_data])
        except (ValueError, TypeError):
            return jsonify({'error': 'Time series data must be numeric values'}), 400
            
        # Get timestamps if provided
        timestamps = data.get('timestamps')
        
        # Use the specified algorithm or create a new detector
        if algorithm_name in anomaly_service.detectors:
            detector = anomaly_service.get_detector(algorithm_name)
        else:
            # Create a new detector with the specified algorithm and parameters
            try:
                algorithm = AnomalyAlgorithm(algorithm_name)
                detector = AnomalyDetector(algorithm, params)
            except ValueError:
                return jsonify({'error': f'Unknown algorithm: {algorithm_name}'}), 400
        
        # Detect anomalies
        result = detector.detect(numeric_data, timestamps)
        
        # Convert the result to a JSON-serializable format
        response = {
            'algorithm': result.algorithm,
            'anomaly_indices': result.anomaly_indices,
            'anomaly_scores': result.anomaly_scores,
            'threshold': result.threshold,
            'metadata': result.metadata
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in anomaly detection: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@anomalies_bp.route('/api/anomaly-detection/algorithms', methods=['GET'])
def list_algorithms():
    """List available anomaly detection algorithms"""
    algorithms = []
    for algo in AnomalyAlgorithm:
        algorithms.append({
            'id': algo.value,
            'name': algo.name,
            'description': get_algorithm_description(algo)
        })
    
    return jsonify(algorithms)

@anomalies_bp.route('/api/anomaly-detection/ensemble', methods=['POST'])
def ensemble_anomaly_detection():
    """Perform ensemble anomaly detection using multiple algorithms"""
    try:
        # Parse the request data
        data = request.json
        
        # Extract the required fields
        time_series_data = data.get('data')
        algorithms = data.get('algorithms')
        threshold = data.get('threshold', 0.5)
        
        # Validate the data
        if not time_series_data or not isinstance(time_series_data, list):
            return jsonify({'error': 'Invalid or missing time series data'}), 400
            
        # Convert data to numpy array and ensure it's numeric
        try:
            numeric_data = np.array([float(x) for x in time_series_data])
        except (ValueError, TypeError):
            return jsonify({'error': 'Time series data must be numeric values'}), 400
        
        # Convert algorithm strings to enum values if needed
        if algorithms:
            algo_enums = []
            for algo_str in algorithms:
                try:
                    algo_enums.append(AnomalyAlgorithm(algo_str))
                except ValueError:
                    return jsonify({'error': f'Unknown algorithm: {algo_str}'}), 400
            algorithms = algo_enums
        
        # Get timestamps if provided
        timestamps = data.get('timestamps')
        
        # Perform ensemble detection
        anomaly_indices, ensemble_scores = anomaly_service.ensemble_detection(
            numeric_data, algorithms, threshold, timestamps
        )
        
        # Prepare response
        response = {
            'anomaly_indices': anomaly_indices,
            'ensemble_scores': ensemble_scores,
            'threshold': threshold,
            'algorithms_used': [algo.value for algo in (algorithms or [])]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in ensemble anomaly detection: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def get_algorithm_description(algorithm):
    """Return a human-readable description of the anomaly detection algorithm"""
    descriptions = {
        AnomalyAlgorithm.ZSCORE: "Z-score measures how many standard deviations a data point is from the mean. Good for normally distributed data.",
        AnomalyAlgorithm.IQR: "Interquartile Range (IQR) identifies outliers based on the distance from the first and third quartiles. Robust to non-normal distributions.",
        AnomalyAlgorithm.ISOLATION_FOREST: "Isolation Forest isolates observations by randomly selecting features. Effective for high-dimensional data and large datasets.",
        AnomalyAlgorithm.ONE_CLASS_SVM: "One-Class SVM learns a boundary around normal data points. Effective when training data is clean (anomaly-free).",
        AnomalyAlgorithm.DBSCAN: "DBSCAN clusters points by density. Points that cannot be clustered are considered anomalies. Good for data with varying densities.",
        AnomalyAlgorithm.LOF: "Local Outlier Factor compares the local density of a point with its neighbors. Effective at finding local anomalies.",
        AnomalyAlgorithm.ARIMA: "ARIMA models time series data and identifies points that deviate from the prediction. Best for seasonal and trending time series.",
        AnomalyAlgorithm.LSTM_AUTOENCODER: "LSTM Autoencoder uses deep learning to learn patterns in sequence data. Effective for complex time series with non-linear patterns."
    }
    return descriptions.get(algorithm, "No description available.")

# Helper function to generate similar past incidents
def get_similar_incidents(anomaly_type, severity):
    """Generate similar past incidents based on the anomaly type and severity"""
    past_incidents = []
    
    # Generate between 2 and 4 similar incidents
    for i in range(random.randint(2, 4)):
        # Generate incident ID (older than A-1275)
        incident_id = f"A-{random.randint(1000, 1274)}"
        
        # Generate timestamp from past 90 days
        days_ago = random.randint(5, 90)
        timestamp = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Resolution status
        resolution_status = random.choice(["Resolved", "Resolved", "Resolved", "Unresolved"])
        
        # Resolution time in minutes
        resolution_time = random.randint(15, 120) if resolution_status == "Resolved" else None
        
        # Create incident
        incident = {
            'id': incident_id,
            'title': f"{anomaly_type} Issue - {incident_id}",
            'timestamp': timestamp,
            'resolution_status': resolution_status,
            'resolution_time': f"{resolution_time} min" if resolution_time else "Unresolved",
            'severity': severity
        }
        
        past_incidents.append(incident)
    
    return past_incidents