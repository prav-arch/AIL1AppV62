"""
Advanced Anomaly Detection Service
This module provides functionality to detect anomalies in log files using machine learning techniques
and generate intelligent recommendations based on the detected anomalies.
"""
import os
import re
import json
import logging
import datetime
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
from collections import defaultdict, Counter
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Anomaly severity levels
SEVERITY_LEVELS = {
    "INFO": 0,
    "WARN": 1,
    "WARNING": 1,
    "ERROR": 2,
    "CRITICAL": 3,
    "FATAL": 3
}

# Singleton instance for the anomaly detector
_anomaly_detector = None

class AnomalyDetector:
    """Service for detecting anomalies in log files using advanced ML techniques"""
    
    def __init__(self, logs_dir="/tmp/logs"):
        """Initialize the anomaly detector with ML models"""
        self.logs_dir = logs_dir
        
        # ML models for anomaly detection
        self.isolation_forest = IsolationForest(
            contamination=0.05,  # Expected proportion of anomalies
            random_state=42,
            n_estimators=100
        )
        
        # DBSCAN for clustering similar log messages
        self.dbscan = DBSCAN(
            eps=0.5,  # Maximum distance between samples
            min_samples=5,  # Minimum samples in a cluster
            metric='cosine'  # Use cosine similarity for text
        )
        
        # TF-IDF vectorizer for text-based features
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            lowercase=True,
            token_pattern=r'\b[a-zA-Z][a-zA-Z0-9_]+\b'
        )
        
        # Feature extraction for log messages
        self.feature_reducer = TruncatedSVD(n_components=10)
    
    def load_log_files(self) -> Dict[str, List[str]]:
        """Load all log files from the logs directory"""
        log_files = {}
        
        if not os.path.exists(self.logs_dir):
            logger.warning(f"Logs directory {self.logs_dir} does not exist")
            os.makedirs(self.logs_dir, exist_ok=True)
            
            # Create sample log files for testing if none exist
            self._create_sample_logs()
        
        # Read all log files in the directory
        for filename in os.listdir(self.logs_dir):
            if filename.endswith('.log'):
                try:
                    filepath = os.path.join(self.logs_dir, filename)
                    with open(filepath, 'r') as f:
                        content = f.readlines()
                    log_files[filename] = content
                except Exception as e:
                    logger.error(f"Error reading log file {filename}: {e}")
        
        if not log_files:
            logger.warning("No log files found, creating sample logs")
            self._create_sample_logs()
            return self.load_log_files()
            
        return log_files
    
    def _create_sample_logs(self):
        """Create sample log files for testing if no real logs exist"""
        sample_logs = {
            'application.log': [
                "2025-05-20 08:00:12 INFO [App] Application started successfully\n",
                "2025-05-20 08:15:23 INFO [DataService] Loaded 1275 records from database\n",
                "2025-05-20 08:30:45 WARNING [DbConnector] Slow database response (305ms)\n",
                "2025-05-20 09:12:33 ERROR [AuthService] Failed to authenticate user: Invalid credentials\n",
                "2025-05-20 09:12:34 ERROR [AuthService] Failed to authenticate user: Invalid credentials\n",
                "2025-05-20 09:12:35 ERROR [AuthService] Failed to authenticate user: Invalid credentials\n",
                "2025-05-20 09:12:40 ERROR [AuthService] Account locked due to multiple failed attempts\n",
                "2025-05-20 09:45:22 WARNING [MemoryMonitor] High memory usage: 85%\n",
                "2025-05-20 10:15:01 CRITICAL [SystemMonitor] CPU usage exceeded threshold: 95%\n",
                "2025-05-20 10:15:05 ERROR [ApiService] Connection timeout when calling external service\n",
                "2025-05-20 10:15:10 ERROR [ApiService] Failed to process request due to upstream service error\n"
            ],
            'system.log': [
                "2025-05-20 07:58:02 INFO [Kernel] System booted successfully in 23.4s\n",
                "2025-05-20 08:02:15 INFO [NetworkManager] Established connection to network 'main-network'\n",
                "2025-05-20 09:30:11 WARNING [DiskMonitor] Disk space running low on /dev/sda1 (85% used)\n",
                "2025-05-20 10:14:30 ERROR [Driver] Failed to initialize hardware acceleration\n",
                "2025-05-20 10:14:35 ERROR [Graphics] Falling back to software rendering\n",
                "2025-05-20 10:16:22 CRITICAL [PowerManager] Unexpected power state transition detected\n",
                "2025-05-20 10:16:25 CRITICAL [SystemMonitor] Multiple system services failing\n",
                "2025-05-20 10:17:01 CRITICAL [Kernel] Unhandled exception in kernel mode: 0xC000021A\n"
            ]
        }
        
        # Write sample logs to files
        for filename, lines in sample_logs.items():
            filepath = os.path.join(self.logs_dir, filename)
            with open(filepath, 'w') as f:
                f.writelines(lines)
    
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """Parse a log line into structured data"""
        parsed = {
            'timestamp': None,
            'level': 'INFO',  # Default level
            'component': 'Unknown',
            'message': line.strip(),
            'raw': line.strip()
        }
        
        # Extract timestamp
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
        if timestamp_match:
            parsed['timestamp'] = timestamp_match.group(1)
            
        # Extract severity level
        level_match = re.search(r'\b(INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b', line)
        if level_match:
            parsed['level'] = level_match.group(1)
            
        # Extract component
        component_match = re.search(r'\[([^]]+)\]', line)
        if component_match:
            parsed['component'] = component_match.group(1)
            
        # Extract message - everything after timestamp and level
        if timestamp_match and level_match:
            level_pos = line.find(level_match.group(0)) + len(level_match.group(0))
            
            # If we have a component, start message after it
            if component_match:
                level_pos = line.find(component_match.group(0)) + len(component_match.group(0))
            
            if level_pos < len(line):
                parsed['message'] = line[level_pos:].strip()
        
        # Calculate severity based on level
        parsed['severity'] = SEVERITY_LEVELS.get(parsed['level'], 0)
        
        return parsed
    
    def extract_features_from_logs(self, parsed_lines: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract numerical features from parsed log lines for ML-based anomaly detection
        """
        if not parsed_lines:
            return np.array([])
            
        # Extract message texts
        messages = [line['message'] for line in parsed_lines]
        
        # Vectorize messages using TF-IDF
        try:
            message_vectors = self.vectorizer.fit_transform(messages)
            
            # Reduce dimensionality for efficiency
            reduced_vectors = self.feature_reducer.fit_transform(message_vectors)
        except Exception as e:
            logger.error(f"Error vectorizing messages: {e}")
            # Fallback to simple features
            reduced_vectors = np.zeros((len(messages), 10))
        
        # Create additional numerical features
        numerical_features = np.zeros((len(parsed_lines), 4))
        
        for i, line in enumerate(parsed_lines):
            # Feature 1: Message length
            numerical_features[i, 0] = len(line['message'])
            
            # Feature 2: Severity level
            numerical_features[i, 1] = line['severity']
            
            # Feature 3: Has error code?
            numerical_features[i, 2] = 1 if re.search(r'(error|exception).*?(\d+|0x[a-fA-F0-9]+)', 
                                                     line['message'], re.IGNORECASE) else 0
            
            # Feature 4: Has stack trace indicator?
            numerical_features[i, 3] = 1 if re.search(r'(stack|trace|at\s+[\w\.]+\.[\w<>]+\(|exception in thread)', 
                                                     line['message'], re.IGNORECASE) else 0
            
        # Combine text and numerical features
        combined_features = np.hstack((reduced_vectors, numerical_features))
        
        # Normalize features
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(combined_features)
        
        return normalized_features
    
    def detect_ml_anomalies(self, filename: str, lines: List[str], parsed_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies using machine learning techniques:
        1. Isolation Forest for detecting outliers based on numerical features
        2. DBSCAN clustering for detecting contextual anomalies in log messages
        """
        anomalies = []
        
        if not parsed_lines:
            return anomalies
            
        # Extract features from log lines
        features = self.extract_features_from_logs(parsed_lines)
        
        if features.size == 0:
            return anomalies
        
        # 1. Isolation Forest for outlier detection
        try:
            isolation_predictions = self.isolation_forest.fit_predict(features)
            for i, pred in enumerate(isolation_predictions):
                if pred == -1:  # Isolation Forest marks outliers as -1
                    anomaly = {
                        "id": f"ml_isolation_{filename}_{i}",
                        "type": "ml_isolation_forest",
                        "algorithm": "Isolation Forest",
                        "source_file": filename,
                        "line_number": i,
                        "severity": max(2, parsed_lines[i]['severity']),  # At least ERROR level
                        "confidence": 0.8,  # Fixed confidence for Isolation Forest
                        "timestamp": parsed_lines[i].get('timestamp', ''),
                        "component": parsed_lines[i].get('component', 'Unknown'),
                        "message": f"ML-detected anomaly: {parsed_lines[i]['message']}",
                        "explanation": "This log entry was detected as anomalous based on its unusual patterns compared to other log entries.",
                        "context": self._get_context(lines, i)
                    }
                    anomalies.append(anomaly)
        except Exception as e:
            logger.error(f"Error in Isolation Forest anomaly detection: {e}")
        
        # 2. DBSCAN clustering for contextual anomalies
        try:
            # Extract only text features for DBSCAN
            messages = [line['message'] for line in parsed_lines]
            message_vectors = self.vectorizer.fit_transform(messages)
            
            # Apply dimensionality reduction
            reduced_vectors = self.feature_reducer.fit_transform(message_vectors)
            
            # Perform DBSCAN clustering
            dbscan_labels = self.dbscan.fit_predict(reduced_vectors)
            
            # Find outliers (points not assigned to any cluster, labeled as -1)
            for i, label in enumerate(dbscan_labels):
                if label == -1 and parsed_lines[i]['severity'] >= 1:  # Only consider WARNING+ as anomalies
                    anomaly = {
                        "id": f"ml_dbscan_{filename}_{i}",
                        "type": "ml_dbscan_cluster",
                        "algorithm": "DBSCAN Clustering",
                        "source_file": filename,
                        "line_number": i,
                        "severity": max(1, parsed_lines[i]['severity']),
                        "confidence": 0.7,  # Fixed confidence for DBSCAN
                        "timestamp": parsed_lines[i].get('timestamp', ''),
                        "component": parsed_lines[i].get('component', 'Unknown'),
                        "message": f"ML-detected unusual pattern: {parsed_lines[i]['message']}",
                        "explanation": "This log entry contains unusual language patterns that don't match any common log message clusters.",
                        "context": self._get_context(lines, i)
                    }
                    anomalies.append(anomaly)
        except Exception as e:
            logger.error(f"Error in DBSCAN anomaly detection: {e}")
        
        return anomalies
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in log files using multiple techniques:
        1. Rule-based detection for known patterns
        2. ML-based detection for complex and unknown patterns
        """
        all_anomalies = []
        log_files = self.load_log_files()
        
        for filename, lines in log_files.items():
            file_anomalies = self._detect_file_anomalies(filename, lines)
            all_anomalies.extend(file_anomalies)
        
        # Sort anomalies by severity (descending) and timestamp
        all_anomalies.sort(key=lambda x: (-x.get('severity', 0), x.get('timestamp', '')))
        
        return all_anomalies
    
    def _detect_file_anomalies(self, filename: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect anomalies in a specific log file"""
        anomalies = []
        
        # Parse all lines
        parsed_lines = [self.parse_log_line(line) for line in lines]
        
        # 1. Detect high severity anomalies (ERROR/CRITICAL)
        for i, parsed in enumerate(parsed_lines):
            if parsed['severity'] >= 2:  # ERROR or higher
                anomaly = {
                    "id": f"high_severity_{filename}_{i}",
                    "type": "high_severity",
                    "source_file": filename,
                    "line_number": i,
                    "severity": parsed['severity'],
                    "timestamp": parsed.get('timestamp', ''),
                    "component": parsed.get('component', 'Unknown'),
                    "message": parsed['message'],
                    "context": self._get_context(lines, i)
                }
                anomalies.append(anomaly)
        
        # 2. Detect known error patterns
        pattern_anomalies = []
        for i, parsed in enumerate(parsed_lines):
            message = parsed['message'].lower()
            component = parsed.get('component', '').lower()
            
            # Detect memory-related issues
            if re.search(r'(out of memory|memory.*?leak|memory.*?(full|exceeded))', message):
                pattern_anomalies.append({
                    "id": f"pattern_memory_{filename}_{i}",
                    "type": "pattern_match",
                    "pattern": "memory_issue",
                    "source_file": filename,
                    "line_number": i,
                    "severity": max(2, parsed['severity']),
                    "timestamp": parsed.get('timestamp', ''),
                    "component": parsed.get('component', 'Unknown'),
                    "message": parsed['message'],
                    "context": self._get_context(lines, i)
                })
            
            # Detect disk space issues
            elif re.search(r'(disk space|disk.*?full|no space left)', message):
                pattern_anomalies.append({
                    "id": f"pattern_disk_{filename}_{i}",
                    "type": "pattern_match",
                    "pattern": "disk_issue",
                    "source_file": filename,
                    "line_number": i,
                    "severity": max(2, parsed['severity']),
                    "timestamp": parsed.get('timestamp', ''),
                    "component": parsed.get('component', 'Unknown'),
                    "message": parsed['message'],
                    "context": self._get_context(lines, i)
                })
            
            # Detect connectivity issues
            elif re.search(r'(timeout|connection.*?fail|cannot connect|unreachable)', message):
                pattern_anomalies.append({
                    "id": f"pattern_connection_{filename}_{i}",
                    "type": "pattern_match",
                    "pattern": "connectivity_issue",
                    "source_file": filename,
                    "line_number": i,
                    "severity": max(2, parsed['severity']),
                    "timestamp": parsed.get('timestamp', ''),
                    "component": parsed.get('component', 'Unknown'),
                    "message": parsed['message'],
                    "context": self._get_context(lines, i)
                })
            
            # Detect database issues
            elif re.search(r'(database|db).*?(error|fail|issue|timeout)', message) or ('database' in component and parsed['severity'] >= 2):
                pattern_anomalies.append({
                    "id": f"pattern_database_{filename}_{i}",
                    "type": "pattern_match",
                    "pattern": "database_issue",
                    "source_file": filename,
                    "line_number": i,
                    "severity": max(2, parsed['severity']),
                    "timestamp": parsed.get('timestamp', ''),
                    "component": parsed.get('component', 'Unknown'),
                    "message": parsed['message'],
                    "context": self._get_context(lines, i)
                })
            
            # Detect security issues
            elif re.search(r'(security|auth.*?fail|invalid.*?token|permission denied|unauthorized)', message):
                pattern_anomalies.append({
                    "id": f"pattern_security_{filename}_{i}",
                    "type": "pattern_match",
                    "pattern": "security_issue",
                    "source_file": filename,
                    "line_number": i,
                    "severity": max(2, parsed['severity']),
                    "timestamp": parsed.get('timestamp', ''),
                    "component": parsed.get('component', 'Unknown'),
                    "message": parsed['message'],
                    "context": self._get_context(lines, i)
                })
                
        anomalies.extend(pattern_anomalies)
        
        # 3. Detect sequences of related errors
        entries = [(i, parsed) for i, parsed in enumerate(parsed_lines) if parsed['severity'] >= 1]
        sequence_anomalies = self._detect_error_sequences(entries, lines)
        anomalies.extend(sequence_anomalies)
        
        # 4. Detect ML-based anomalies using advanced techniques
        ml_anomalies = self.detect_ml_anomalies(filename, lines, parsed_lines)
        anomalies.extend(ml_anomalies)
        
        return anomalies
    
    def _detect_error_sequences(self, entries: List[Tuple[int, Dict]], lines: List[str]) -> List[Dict[str, Any]]:
        """Detect sequences of related errors"""
        anomalies = []
        
        if len(entries) < 3:
            return anomalies
            
        # Group errors by component
        component_errors = defaultdict(list)
        for i, entry in entries:
            component = entry.get('component', 'Unknown')
            component_errors[component].append((i, entry))
        
        # Look for sequences of errors in the same component
        for component, errors in component_errors.items():
            if len(errors) < 3:
                continue
                
            # Check for errors close together in time
            sequence_lines = []
            current_sequence = []
            
            for i in range(len(errors) - 1):
                current_sequence.append(errors[i][0])  # Line number
                
                # If next error is within 5 lines, continue the sequence
                if errors[i+1][0] - errors[i][0] <= 5:
                    continue
                
                # Otherwise, check if we have a sequence
                if len(current_sequence) >= 3:
                    sequence_lines.append(current_sequence)
                
                current_sequence = []
            
            # Check last sequence
            if len(current_sequence) >= 3:
                sequence_lines.append(current_sequence)
            
            # Create anomalies for sequences
            for seq_idx, sequence in enumerate(sequence_lines):
                first_line = sequence[0]
                last_line = sequence[-1]
                context = []
                
                # Collect all context lines
                for line_num in range(max(0, first_line - 2), min(len(lines), last_line + 3)):
                    context.append(lines[line_num].strip())
                
                anomaly = {
                    "id": f"seq_{component}_{seq_idx}",
                    "type": "error_sequence",
                    "source_file": errors[0][1].get('source_file', 'unknown_file'),
                    "line_number": first_line,
                    "severity": 3,  # Sequences are always high severity
                    "timestamp": errors[0][1].get('timestamp', ''),
                    "component": component,
                    "message": f"Sequence of {len(sequence)} related errors in component {component}",
                    "related_lines": sequence,
                    "context": context
                }
                anomalies.append(anomaly)
                
                # Skip the lines we've included in this sequence
                i = max(sequence_lines)
        
        return anomalies
    
    def _get_context(self, lines: List[str], index: int, context_size: int = 3) -> List[str]:
        """Get context lines around an anomaly"""
        start = max(0, index - context_size)
        end = min(len(lines), index + context_size + 1)
        return [line.strip() for line in lines[start:end]]
    
    def get_recommendations(self, anomaly_id: str) -> Dict[str, Any]:
        """Generate recommendations for a specific anomaly using local Mistral model"""
        from services.llm_recommendation_service import get_recommendations_for_anomaly
        
        # First, get the anomaly details
        anomalies = self.detect_anomalies()
        anomaly = next((a for a in anomalies if a["id"] == anomaly_id), None)
        
        if not anomaly:
            return {
                "found": False,
                "message": f"Anomaly with ID {anomaly_id} not found",
                "recommendations": []
            }
            
        # Try to get ML-based recommendations from Mistral
        llm_recommendations = get_recommendations_for_anomaly(anomaly)
        
        # If we got valid recommendations from the LLM, use them
        if llm_recommendations and len(llm_recommendations) > 0:
            logger.info(f"Using Mistral-generated recommendations for anomaly {anomaly_id}")
            return {
                "found": True,
                "anomaly": anomaly,
                "recommendations": llm_recommendations,
                "source": "mistral"
            }
        
        # Fall back to rule-based recommendations
        logger.info(f"Using rule-based recommendations for anomaly {anomaly_id}")
        
        recommendations = []
        
        # Generic recommendations based on anomaly type
        if anomaly["type"] == "high_severity":
            recommendations.extend(self._get_severity_recommendations(anomaly))
        
        if anomaly["type"] == "pattern_match":
            recommendations.extend(self._get_pattern_recommendations(anomaly))
        
        if anomaly["type"] == "error_sequence":
            recommendations.extend(self._get_sequence_recommendations(anomaly))
        
        # Component-specific recommendations
        component_recs = self._get_component_recommendations(anomaly["component"], anomaly["message"])
        if component_recs:
            recommendations.extend(component_recs)
        
        return {
            "found": True,
            "anomaly": anomaly,
            "recommendations": recommendations,
            "source": "rules"
        }
    
    def _get_severity_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recommendations for high severity anomalies"""
        recs = [{
            "title": "Check System Resources",
            "description": "Verify CPU, memory, and disk usage on the server. High severity errors often correlate with resource exhaustion."
        }, {
            "title": "Review Recent Changes",
            "description": "Investigate recent deployments, configuration changes, or updates that may have triggered this issue."
        }, {
            "title": "Monitor Related Components",
            "description": f"Watch for issues in systems that interact with {anomaly['component']} as this could be a cascading failure from another component."
        }]
        
        return recs
    
    def _get_pattern_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recommendations based on pattern matching"""
        pattern = anomaly.get("pattern", "")
        
        if pattern == "memory_issue":
            return [{
                "title": "Increase Memory Allocation",
                "description": "Consider adding more RAM to the system or increasing memory limits in configuration."
            }, {
                "title": "Check for Memory Leaks",
                "description": "Review application code for memory leaks, especially in long-running processes."
            }, {
                "title": "Implement Memory Monitoring",
                "description": "Set up alerts for memory usage thresholds to proactively detect issues before they become critical."
            }]
            
        elif pattern == "disk_issue":
            return [{
                "title": "Clean Up Disk Space",
                "description": "Remove temporary files, logs, and unused data to free up disk space."
            }, {
                "title": "Increase Storage Capacity",
                "description": "Add more storage or migrate to a larger disk/volume."
            }, {
                "title": "Implement Log Rotation",
                "description": "Configure log rotation to prevent log files from consuming all available disk space."
            }]
            
        elif pattern == "connectivity_issue":
            return [{
                "title": "Check Network Configuration",
                "description": "Verify network settings, DNS resolution, and firewall rules."
            }, {
                "title": "Increase Timeout Values",
                "description": "Adjust connection timeout settings to be more tolerant of network latency."
            }, {
                "title": "Implement Retry Mechanism",
                "description": "Add retry logic with exponential backoff for critical connections."
            }]
            
        elif pattern == "database_issue":
            return [{
                "title": "Optimize Database Queries",
                "description": "Review and optimize slow or resource-intensive database queries."
            }, {
                "title": "Check Connection Pool",
                "description": "Verify database connection pool settings and increase capacity if needed."
            }, {
                "title": "Monitor Database Performance",
                "description": "Set up monitoring for database metrics like CPU, memory, I/O, and query execution time."
            }]
            
        elif pattern == "security_issue":
            return [{
                "title": "Review Authentication Settings",
                "description": "Check authentication configuration and credentials management."
            }, {
                "title": "Implement Rate Limiting",
                "description": "Add rate limiting for authentication attempts to prevent brute force attacks."
            }, {
                "title": "Audit Access Logs",
                "description": "Review security logs for suspicious activity patterns."
            }]
            
        # Generic recommendations for other patterns
        return [{
            "title": "Investigate Root Cause",
            "description": f"Analyze the specific error pattern '{pattern}' to determine underlying causes."
        }, {
            "title": "Add Detailed Logging",
            "description": "Enhance logging around this issue to capture more context for future occurrences."
        }]
    
    def _get_sequence_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recommendations for error sequences"""
        return [{
            "title": "Perform Root Cause Analysis",
            "description": f"Investigate the first error in the sequence within the {anomaly['component']} component as it likely triggered subsequent failures."
        }, {
            "title": "Implement Circuit Breaker",
            "description": "Add circuit breaker patterns to prevent cascading failures when errors occur."
        }, {
            "title": "Enhance Error Handling",
            "description": "Improve error handling to make the system more resilient to this sequence of failures."
        }, {
            "title": "Add Automatic Recovery",
            "description": "Implement automatic recovery mechanisms that can detect and resolve this error pattern."
        }]
    
    def _get_component_recommendations(self, component: str, message: str) -> List[Dict[str, str]]:
        """Get component-specific recommendations"""
        component = component.lower()
        
        if "database" in component or "db" in component:
            return [{
                "title": "Check Database Connectivity",
                "description": "Verify database connection settings and ensure the database is accessible."
            }, {
                "title": "Optimize Database Queries",
                "description": "Review and optimize database queries to improve performance."
            }]
            
        elif "network" in component:
            return [{
                "title": "Check Network Configuration",
                "description": "Verify network settings, DNS resolution, and firewall rules."
            }, {
                "title": "Monitor Network Latency",
                "description": "Set up monitoring for network latency and packet loss."
            }]
            
        elif "auth" in component or "security" in component:
            return [{
                "title": "Review Authentication Settings",
                "description": "Check authentication configuration and credentials management."
            }, {
                "title": "Audit Security Logs",
                "description": "Review security logs for suspicious activity patterns."
            }]
            
        elif "api" in component:
            return [{
                "title": "Verify API Endpoints",
                "description": "Check API endpoint configuration and accessibility."
            }, {
                "title": "Implement API Monitoring",
                "description": "Set up monitoring for API response times and error rates."
            }]
            
        elif "memory" in component or "cache" in component:
            return [{
                "title": "Optimize Memory Usage",
                "description": "Review memory usage patterns and optimize memory-intensive operations."
            }, {
                "title": "Implement Cache Eviction",
                "description": "Add cache eviction policies to prevent memory issues."
            }]
            
        # Generic recommendations if no specific component match
        return []

def get_anomaly_detector():
    """Get or create the anomaly detector singleton"""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetector()
    return _anomaly_detector

def get_anomalies():
    """Get all detected anomalies from real database"""
    try:
        from clickhouse_models import get_clickhouse_client
        
        client = get_clickhouse_client()
        query = """
        SELECT
            CASE CAST(severity AS UInt8)
                WHEN 4 THEN 'Critical'
                WHEN 3 THEN 'High'
                WHEN 1 THEN 'Warning'
                ELSE 'Other'
            END AS severity,
            description,
            log_line,
            source_table
        FROM
        (
            -- fh_violations: log_line
            SELECT
                severity,
                description,
                log_line,
                'fh_violations' AS source_table
            FROM l1_app_db.fh_violations
            WHERE CAST(severity AS UInt8) IN (4, 3, 1)

            UNION ALL

            -- cp_up_coupling: cp_log + up_log as log_line
            SELECT
                severity,
                description,
                concat(cp_log, ' | ', up_log) AS log_line,
                'cp_up_coupling' AS source_table
            FROM l1_app_db.cp_up_coupling
            WHERE CAST(severity AS UInt8) IN (4, 3, 1)

            UNION ALL

            -- interference_splane: log_line
            SELECT
                severity,
                description,
                log_line,
                'interference_splane' AS source_table
            FROM l1_app_db.interference_splane
            WHERE CAST(severity AS UInt8) IN (4, 3, 1)
        )
        ORDER BY severity, source_table, log_line
        """
        
        result = client.execute(query)
        
        anomalies = []
        for i, row in enumerate(result):
            severity = row[0]
            description = row[1]
            log_line = row[2]
            source_table = row[3]
            
            # Map severity to numeric values for consistency
            severity_map = {
                'Critical': 4,
                'High': 3,
                'Warning': 1
            }
            
            # Generate unique ID
            anomaly_id = f"db_anomaly_{source_table}_{i}"
            
            anomalies.append({
                'id': anomaly_id,
                'severity': severity_map.get(severity, 1),
                'severity_label': severity,
                'title': f"{severity} issue detected",
                'message': description,
                'log_line': log_line,
                'source': source_table,
                'timestamp': 'Recent',  # You can add timestamp from DB if available
                'type': 'database_detected',
                'component': source_table.replace('_', ' ').title()
            })
        
        return anomalies
        
    except Exception as e:
        logger.error(f"Error fetching anomalies from database: {e}")
        # Return empty list if database query fails
        return []

def get_anomaly_recommendations(anomaly_id):
    """Get recommendations for an anomaly"""
    detector = get_anomaly_detector()
    return detector.get_recommendations(anomaly_id)

def get_anomaly_stats():
    """Get statistics about detected anomalies from real database"""
    try:
        from clickhouse_models import get_clickhouse_client
        
        # Execute the real query to get anomaly counts
        client = get_clickhouse_client()
        query = """
        SELECT
            sum(critical_count) AS total_critical,
            sum(high_count) AS total_high,
            sum(warning_count) AS total_warning,
            sum(total_critical_high_warning) AS total_sum
        FROM
        (
            SELECT * FROM l1_app_db.fh_violations_daily
            UNION ALL
            SELECT * FROM l1_app_db.cp_up_coupling_daily
            UNION ALL
            SELECT * FROM l1_app_db.interference_splane_daily
        )
        """
        
        result = client.execute(query)
        
        if result and len(result) > 0:
            row = result[0]
            critical_count = row[0] if row[0] is not None else 0
            high_count = row[1] if row[1] is not None else 0
            warning_count = row[2] if row[2] is not None else 0
            total_count = row[3] if row[3] is not None else 0
            
            return {
                'critical': critical_count,
                'errors': high_count,  # High priority mapped to errors
                'warnings': warning_count,
                'total': total_count,
                'by_severity': {
                    'CRITICAL': critical_count,
                    'ERROR': high_count,
                    'WARNING': warning_count
                },
                'total_anomalies': total_count
            }
        else:
            # Return zeros if no data found
            return {
                'critical': 0,
                'errors': 0,
                'warnings': 0,
                'total': 0,
                'by_severity': {
                    'CRITICAL': 0,
                    'ERROR': 0,
                    'WARNING': 0
                },
                'total_anomalies': 0
            }
            
    except Exception as e:
        logger.error(f"Error fetching anomaly stats from database: {e}")
        # Return zeros if database query fails
        return {
            'critical': 0,
            'errors': 0,
            'warnings': 0,
            'total': 0,
            'by_severity': {
                'CRITICAL': 0,
                'ERROR': 0,
                'WARNING': 0
            },
            'total_anomalies': 0
        }