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

class AnomalyDetector:
    """Service for detecting anomalies in log files using advanced ML techniques"""
    
    def __init__(self, logs_dir="/tmp/logs"):
        """Initialize the anomaly detector with ML models"""
        self.logs_dir = logs_dir
        # Patterns for traditional rule-based detection
        self.anomaly_patterns = [
            (r"ERROR|CRITICAL|FATAL", "High severity log entry"),
            (r"exception|fail|failed|timeout|timed out", "Failure or exception indication"),
            (r"memory leak|out of memory|memory usage exceed", "Memory issues"),
            (r"CPU usage|high load|overload", "CPU performance issues"),
            (r"disk space|storage|capacity", "Storage capacity issues"),
            (r"attack|security|breach|unauthorized|hack", "Security concerns"),
            (r"latency|slow|performance|degraded", "Performance degradation"),
            (r"crash|abort|terminate|killed", "Application crash or termination"),
            (r"database|connection lost|reconnect", "Database connectivity issues"),
            (r"API|service unavailable|endpoint", "API or service availability issues")
        ]
        
        # ML model configurations
        self.isolation_forest = IsolationForest(
            n_estimators=100, 
            contamination="auto",  # Auto-detect contamination 
            random_state=42,
            max_samples='auto'
        )
        
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            min_df=2
        )
        
        self.svd = TruncatedSVD(n_components=10)
        
        self.dbscan = DBSCAN(
            eps=0.5,
            min_samples=2,
            metric='cosine'
        )
    
    def load_log_files(self) -> Dict[str, List[str]]:
        """Load all log files from the logs directory"""
        log_files = {}
        
        try:
            if not os.path.exists(self.logs_dir):
                logger.warning(f"Logs directory {self.logs_dir} not found")
                return log_files
            
            for filename in os.listdir(self.logs_dir):
                if filename.endswith(".log"):
                    file_path = os.path.join(self.logs_dir, filename)
                    try:
                        with open(file_path, 'r') as file:
                            log_files[filename] = file.readlines()
                    except Exception as e:
                        logger.error(f"Error reading log file {filename}: {e}")
        except Exception as e:
            logger.error(f"Error accessing logs directory: {e}")
        
        return log_files
    
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """Parse a log line into structured data"""
        # Basic log format: YYYY-MM-DD HH:MM:SS LEVEL [Component] Message
        match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) \[([^\]]+)\] (.+)$', line.strip())
        
        if match:
            timestamp, level, component, message = match.groups()
            return {
                "timestamp": timestamp,
                "level": level,
                "component": component,
                "message": message,
                "severity": SEVERITY_LEVELS.get(level, 0)
            }
        
        return {
            "timestamp": "",
            "level": "UNKNOWN",
            "component": "UNKNOWN",
            "message": line.strip(),
            "severity": 0
        }
    
    def extract_features_from_logs(self, parsed_lines: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract numerical features from parsed log lines for ML-based anomaly detection
        """
        features = []
        
        for parsed in parsed_lines:
            # Extract features that might be useful for anomaly detection
            severity = parsed["severity"]
            message_length = len(parsed["message"])
            has_error = 1 if severity >= 2 else 0
            has_warning = 1 if severity == 1 else 0
            hour = 0
            minute = 0
            
            # Extract time features if timestamp exists
            if parsed["timestamp"]:
                try:
                    dt = datetime.datetime.strptime(parsed["timestamp"], "%Y-%m-%d %H:%M:%S")
                    hour = dt.hour
                    minute = dt.minute
                except ValueError:
                    pass
            
            # Create feature vector
            feature_vector = [
                severity,
                message_length,
                has_error,
                has_warning,
                hour,
                minute
            ]
            features.append(feature_vector)
        
        # If no features, return empty array
        if not features:
            return np.array([])
        
        # Normalize features
        scaler = StandardScaler()
        return scaler.fit_transform(np.array(features))
    
    def detect_ml_anomalies(self, filename: str, lines: List[str], parsed_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies using machine learning techniques:
        1. Isolation Forest for detecting outliers based on numerical features
        2. DBSCAN clustering for detecting contextual anomalies in log messages
        """
        anomalies = []
        
        # Need enough data for meaningful ML analysis
        if len(parsed_lines) < 5:
            return anomalies
        
        # Extract messages for text-based analysis
        messages = [parsed["message"] for parsed in parsed_lines]
        
        # ---------- Isolation Forest for numerical features ----------
        # Extract and normalize features
        features = self.extract_features_from_logs(parsed_lines)
        
        if len(features) > 0:
            # Fit the Isolation Forest model
            self.isolation_forest.fit(features)
            
            # Predict anomalies (-1 for anomalies, 1 for normal)
            predictions = self.isolation_forest.predict(features)
            
            # Find anomalies
            for i, pred in enumerate(predictions):
                if pred == -1:  # Anomaly detected
                    parsed = parsed_lines[i]
                    
                    # Create anomaly record
                    anomaly = {
                        "id": f"{filename}_{i}_ml_isolation",
                        "type": "ml_isolation_forest",
                        "algorithm": "Isolation Forest",
                        "timestamp": parsed["timestamp"],
                        "component": parsed["component"],
                        "message": parsed["message"],
                        "severity": max(1, parsed["severity"]),  # At least WARNING level
                        "source_file": filename,
                        "line_number": i + 1,
                        "context": self._get_context(lines, i),
                        "confidence": 0.85,  # Base confidence level
                        "explanation": "Statistical outlier detected based on temporal patterns and severity"
                    }
                    anomalies.append(anomaly)
        
        # ---------- Text-based anomaly detection with DBSCAN ----------
        try:
            # Only proceed if we have enough messages
            if len(messages) >= 5:
                # Generate TF-IDF vectors
                tfidf_matrix = self.vectorizer.fit_transform(messages)
                
                # Apply dimensionality reduction if we have enough features
                if tfidf_matrix.shape[1] > 10:
                    text_features = self.svd.fit_transform(tfidf_matrix)
                else:
                    text_features = tfidf_matrix.toarray()
                
                # Apply DBSCAN clustering
                clusters = self.dbscan.fit_predict(text_features)
                
                # Find outliers (labeled as -1 by DBSCAN)
                for i, cluster_id in enumerate(clusters):
                    if cluster_id == -1:  # This is an outlier
                        parsed = parsed_lines[i]
                        
                        # Create anomaly record
                        anomaly = {
                            "id": f"{filename}_{i}_ml_dbscan",
                            "type": "ml_dbscan_cluster",
                            "algorithm": "DBSCAN Clustering",
                            "timestamp": parsed["timestamp"],
                            "component": parsed["component"],
                            "message": parsed["message"],
                            "severity": max(1, parsed["severity"]),  # At least WARNING level
                            "source_file": filename,
                            "line_number": i + 1,
                            "context": self._get_context(lines, i),
                            "confidence": 0.75,  # Base confidence level
                            "explanation": "Unusual log message content compared to other messages in this log file"
                        }
                        anomalies.append(anomaly)
        except Exception as e:
            logger.warning(f"Text-based anomaly detection failed: {e}")
        
        return anomalies
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in log files using multiple techniques:
        1. Rule-based detection for known patterns
        2. ML-based detection for complex and unknown patterns
        """
        log_files = self.load_log_files()
        anomalies = []
        
        for filename, lines in log_files.items():
            # Traditional rule-based anomaly detection
            rule_based_anomalies = self._detect_file_anomalies(filename, lines)
            anomalies.extend(rule_based_anomalies)
            
            # Parse lines for ML detection
            parsed_lines = [self.parse_log_line(line) for line in lines]
            
            # ML-based anomaly detection
            ml_anomalies = self.detect_ml_anomalies(filename, lines, parsed_lines)
            anomalies.extend(ml_anomalies)
        
        # Remove duplicates (same line detected by multiple methods)
        unique_anomalies = {}
        for anomaly in anomalies:
            key = f"{anomaly['source_file']}_{anomaly['line_number']}"
            # Keep the anomaly with highest confidence/severity if duplicate
            if key not in unique_anomalies or unique_anomalies[key]['severity'] < anomaly['severity']:
                unique_anomalies[key] = anomaly
        
        # Sort by severity (descending) and timestamp (descending)
        return sorted(list(unique_anomalies.values()), 
                      key=lambda x: (-x.get("severity", 0), x.get("timestamp", "")), 
                      reverse=True)
    
    def _detect_file_anomalies(self, filename: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect anomalies in a specific log file"""
        anomalies = []
        parsed_lines = [self.parse_log_line(line) for line in lines]
        
        # Detect high severity log entries
        for i, parsed in enumerate(parsed_lines):
            if parsed["severity"] >= 2:  # ERROR or higher
                anomaly = {
                    "id": f"{filename}_{i}",
                    "type": "high_severity",
                    "timestamp": parsed["timestamp"],
                    "component": parsed["component"],
                    "message": parsed["message"],
                    "severity": parsed["severity"],
                    "source_file": filename,
                    "line_number": i + 1,
                    "context": self._get_context(lines, i)
                }
                anomalies.append(anomaly)
            
            # Check for pattern-based anomalies
            for pattern, description in self.anomaly_patterns:
                if re.search(pattern, parsed["message"], re.IGNORECASE):
                    if not any(a["line_number"] == i + 1 and a["source_file"] == filename for a in anomalies):
                        anomaly = {
                            "id": f"{filename}_{i}",
                            "type": "pattern_match",
                            "pattern_description": description,
                            "timestamp": parsed["timestamp"],
                            "component": parsed["component"],
                            "message": parsed["message"],
                            "severity": max(1, parsed["severity"]),  # At least WARN level
                            "source_file": filename,
                            "line_number": i + 1,
                            "context": self._get_context(lines, i)
                        }
                        anomalies.append(anomaly)
        
        # Detect sequences of related errors (e.g., multiple retries)
        components = defaultdict(list)
        for i, parsed in enumerate(parsed_lines):
            components[parsed["component"]].append((i, parsed))
        
        for component, entries in components.items():
            if len(entries) >= 3:  # At least 3 entries from the same component
                error_sequences = self._detect_error_sequences(entries, lines)
                anomalies.extend(error_sequences)
        
        return anomalies
    
    def _detect_error_sequences(self, entries: List[Tuple[int, Dict]], lines: List[str]) -> List[Dict[str, Any]]:
        """Detect sequences of related errors"""
        anomalies = []
        component = entries[0][1]["component"]
        filename = entries[0][1].get("source_file", "unknown")
        
        # Look for retries, reconnections, or repeated errors
        retry_patterns = [
            r"retry|attempt|reconnect",
            r"\(\d+/\d+\)"  # Matches patterns like (1/3), (2/5), etc.
        ]
        
        for i in range(len(entries) - 1):
            idx1, entry1 = entries[i]
            
            # Skip if not an error
            if entry1["severity"] < 2:
                continue
            
            sequence_found = False
            sequence_lines = [idx1]
            
            # Look for related errors in the next entries
            for j in range(i + 1, min(i + 5, len(entries))):
                idx2, entry2 = entries[j]
                
                # Check if entries are likely related
                if entry2["severity"] >= 2 and any(re.search(pattern, entry1["message"], re.IGNORECASE) and 
                                               re.search(pattern, entry2["message"], re.IGNORECASE) 
                                               for pattern in retry_patterns):
                    sequence_found = True
                    sequence_lines.append(idx2)
            
            if sequence_found and len(sequence_lines) >= 2:
                # Get all lines in sequence
                context = []
                for idx in sorted(sequence_lines):
                    context.append(lines[idx].strip())
                
                anomaly = {
                    "id": f"{filename}_{idx1}_sequence",
                    "type": "error_sequence",
                    "timestamp": entry1["timestamp"],
                    "component": component,
                    "message": f"Sequence of related errors in component {component}",
                    "severity": 2,  # ERROR level
                    "source_file": filename,
                    "line_number": idx1 + 1,
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
        import json
        import os
        from llama_cpp import Llama  # Direct import for local LLM
        
        # First, get the anomaly details
        anomalies = self.detect_anomalies()
        anomaly = next((a for a in anomalies if a["id"] == anomaly_id), None)
        
        if not anomaly:
            return {
                "found": False,
                "message": f"Anomaly with ID {anomaly_id} not found",
                "recommendations": []
            }
        
        # Convert context to string for LLM input
        context_str = "\n".join(anomaly.get("context", []))
        
        # Format severity level text
        severity_text = "CRITICAL" if anomaly.get('severity', 0) >= 3 else "ERROR" if anomaly.get('severity', 0) == 2 else "WARNING"
        
        # Prepare the prompt for the local LLM
        system_prompt = "You are a system administrator expert who provides recommendations to fix issues."
        
        prompt = f"""
        You are an expert system administrator and software developer. Analyze the following log anomaly and provide specific, actionable recommendations to address the issue.
        
        ANOMALY DETAILS:
        Type: {anomaly.get('type', '')}
        Component: {anomaly.get('component', '')}
        Message: {anomaly.get('message', '')}
        Severity: {severity_text}
        Source: {anomaly.get('source_file', '')}:{anomaly.get('line_number', 0)}
        
        CONTEXT:
        {context_str}
        
        Based on this information, provide 3-5 actionable recommendations to fix this issue. For each recommendation, include:
        1. A clear title (max 10 words)
        2. A detailed description of what to do (2-3 sentences)
        
        Format your response as a JSON array of objects with 'title' and 'description' fields.
        Example:
        [
          {
            "title": "First recommendation title",
            "description": "Detailed description of what to do and why it will help resolve the issue."
          },
          {
            "title": "Second recommendation title",
            "description": "Another detailed description with specific actions to take."
          }
        ]
        """
        
        # Format prompt in the chat completion format
        formatted_prompt = f"<s>[INST] {system_prompt} [/INST]</s>[INST] {prompt} [/INST]"
        
        try:
            # Set path to the local Mistral model
            model_path = "/tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
            
            # Check if the model exists
            if not os.path.exists(model_path):
                logging.warning(f"Mistral model not found at {model_path}")
                # Fall back to predefined recommendations
                return {
                    "found": True,
                    "anomaly": anomaly,
                    "recommendations": self._get_fallback_recommendations(anomaly)
                }
            
            # Load the model directly
            try:
                # Initialize the Llama model with minimal context window to save memory
                llm = Llama(
                    model_path=model_path,
                    n_ctx=2048,        # Smaller context window to reduce memory usage
                    n_batch=512,       # Batch size for prompt processing
                    verbose=False
                )
                
                # Generate response from the local model
                output = llm(
                    formatted_prompt,
                    max_tokens=1000,    # Limit response length
                    temperature=0.2,    # Low temperature for more focused recommendations
                    stop=["</s>"]       # Stop at the end of the response
                )
                
                # The llama-cpp-python interface returns a different output format than OpenAI
                # For llama-cpp's output we need to get the text from the returned dict
                response_text = output.get('choices', [{}])[0].get('text', '')
                
                # Try to extract JSON from the response
                try:
                    import re
                    # First, try to find and extract the JSON array
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
                    
                    if json_match:
                        json_str = json_match.group(0)
                        recommendations = json.loads(json_str)
                    else:
                        # If no JSON array found, try to manually extract recommendations
                        recommendations = []
                        
                        # Find recommendation titles (often numbered or with clear headings)
                        title_pattern = r'(?:^\d+\.\s+|\*\*|\b)([A-Z][^.!?:]*(?::|\.))(?:\s|\n)'
                        titles = re.findall(title_pattern, response_text, re.MULTILINE)
                        
                        # Extract descriptions following titles
                        for i, title in enumerate(titles[:5]):  # Limit to 5 recommendations
                            title = title.strip(': .\n\r\t')
                            description = ""
                            
                            # Try to find the description after the title until the next title or end
                            start_pos = response_text.find(title) + len(title)
                            end_pos = len(response_text)
                            
                            if i < len(titles) - 1:
                                next_title = titles[i + 1]
                                next_pos = response_text.find(next_title)
                                if next_pos > start_pos:
                                    end_pos = next_pos
                            
                            description = response_text[start_pos:end_pos].strip(': .\n\r\t')
                            
                            # Clean up the description
                            description = re.sub(r'^\s*[-:]\s*', '', description)
                            description = description.strip()
                            
                            if title and description:
                                recommendations.append({
                                    "title": title[:50],  # Limit title length
                                    "description": description[:300]  # Limit description length
                                })
                    
                    # Validate recommendations format and ensure we have at least one
                    if isinstance(recommendations, list) and len(recommendations) > 0 and all(isinstance(r, dict) and 'title' in r and 'description' in r for r in recommendations):
                        return {
                            "found": True,
                            "anomaly": anomaly,
                            "recommendations": recommendations
                        }
                except Exception as e:
                    logging.warning(f"Error parsing LLM response: {e}")
                        # First, try to find and extract the JSON array
                        import re
                        json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
                        
                        if json_match:
                            json_str = json_match.group(0)
                            recommendations = json.loads(json_str)
                        else:
                            # If no JSON array found, try to manually extract recommendations
                            recommendations = []
                            # Find recommendation titles (often numbered or with clear headings)
                            title_pattern = r'(?:^\d+\.\s+|\*\*|\b)([A-Z][^.!?:]*(?::|\.))(?:\s|\n)'
                            titles = re.findall(title_pattern, content, re.MULTILINE)
                            
                            # Extract descriptions following titles
                            for i, title in enumerate(titles[:5]):  # Limit to 5 recommendations
                                title = title.strip(': .\n\r\t')
                                description = ""
                                
                                # Try to find the description after the title until the next title or end
                                start_pos = content.find(title) + len(title)
                                end_pos = len(content)
                                
                                if i < len(titles) - 1:
                                    next_title = titles[i + 1]
                                    next_pos = content.find(next_title)
                                    if next_pos > start_pos:
                                        end_pos = next_pos
                                
                                description = content[start_pos:end_pos].strip(': .\n\r\t')
                                
                                # Clean up the description
                                description = re.sub(r'^\s*[-:]\s*', '', description)
                                description = description.strip()
                                
                                if title and description:
                                    recommendations.append({
                                        "title": title[:50],  # Limit title length
                                        "description": description[:300]  # Limit description length
                                    })
                            
                        # Validate recommendations format and ensure we have at least one
                        if isinstance(recommendations, list) and len(recommendations) > 0 and all(isinstance(r, dict) and 'title' in r and 'description' in r for r in recommendations):
                            return {
                                "found": True,
                                "anomaly": anomaly,
                                "recommendations": recommendations
                            }
                    except Exception as e:
                        logger.warning(f"Error parsing response: {e}")
                        # Continue to fallback
            except Exception as e:
                logger.warning(f"Error connecting to local service: {e}")
                # Continue to fallback
                
            # If any step fails, fall back to predefined recommendations
            recommendations = self._get_fallback_recommendations(anomaly)
            return {
                "found": True,
                "anomaly": anomaly,
                "recommendations": recommendations
            }
                
        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")
            recommendations = self._get_fallback_recommendations(anomaly)
            return {
                "found": True,
                "anomaly": anomaly,
                "recommendations": recommendations
            }
        
    def _get_fallback_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate fallback recommendations if LLM is not available"""
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
            
        return recommendations
    
    def _get_severity_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recommendations for high severity anomalies"""
        recs = [{
            "title": "Investigate Error",
            "description": f"Investigate the {anomaly['component']} component to identify the root cause of the error."
        }]
        
        if "exception" in anomaly["message"].lower() or "stack trace" in anomaly["message"].lower():
            recs.append({
                "title": "Review Stack Trace",
                "description": "Analyze the stack trace to identify the specific method or line where the error occurred."
            })
        
        return recs
    
    def _get_pattern_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recommendations based on pattern matching"""
        pattern_desc = anomaly.get("pattern_description", "").lower()
        message = anomaly.get("message", "").lower()
        
        recs = []
        
        if "memory" in pattern_desc:
            recs.append({
                "title": "Memory Optimization",
                "description": "Check for memory leaks and optimize memory usage in the application."
            })
            recs.append({
                "title": "Increase Memory Allocation",
                "description": "Consider increasing the memory allocation for the service if consistently hitting limits."
            })
        
        elif "cpu" in pattern_desc:
            recs.append({
                "title": "CPU Profiling",
                "description": "Run CPU profiling to identify performance bottlenecks."
            })
            recs.append({
                "title": "Optimize Algorithms",
                "description": "Review and optimize CPU-intensive algorithms in the codebase."
            })
        
        elif "storage" in pattern_desc or "disk" in pattern_desc:
            recs.append({
                "title": "Disk Space Management",
                "description": "Implement log rotation and cleanup of temporary files."
            })
            recs.append({
                "title": "Storage Monitoring",
                "description": "Set up alerts for disk space usage before it reaches critical levels."
            })
        
        elif "security" in pattern_desc:
            recs.append({
                "title": "Security Audit",
                "description": "Conduct a security audit of the affected component."
            })
            recs.append({
                "title": "Update Security Policies",
                "description": "Review and update security policies and access controls."
            })
        
        elif "performance" in pattern_desc or "latency" in pattern_desc:
            recs.append({
                "title": "Performance Tuning",
                "description": "Optimize database queries and API calls for better performance."
            })
            recs.append({
                "title": "Load Testing",
                "description": "Conduct load testing to identify performance bottlenecks under stress."
            })
        
        elif "database" in pattern_desc:
            recs.append({
                "title": "Database Connection Pooling",
                "description": "Implement or optimize database connection pooling."
            })
            recs.append({
                "title": "Database Failover",
                "description": "Set up database failover mechanisms if not already in place."
            })
        
        elif "api" in pattern_desc or "service" in pattern_desc:
            recs.append({
                "title": "Service Resilience",
                "description": "Implement circuit breakers and fallback mechanisms for external services."
            })
            recs.append({
                "title": "Retry Strategy",
                "description": "Optimize retry strategies with exponential backoff for external API calls."
            })
        
        return recs
    
    def _get_sequence_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recommendations for error sequences"""
        return [
            {
                "title": "Retry Strategy Review",
                "description": "Review the retry strategy to ensure it's not too aggressive and includes proper backoff."
            },
            {
                "title": "Failover Mechanisms",
                "description": "Implement or improve failover mechanisms to handle repeated failures more gracefully."
            },
            {
                "title": "Circuit Breaker Pattern",
                "description": "Implement a circuit breaker pattern to prevent cascading failures when a service is consistently unavailable."
            }
        ]
    
    def _get_component_recommendations(self, component: str, message: str) -> List[Dict[str, str]]:
        """Get component-specific recommendations"""
        component = component.lower()
        message = message.lower()
        
        if "database" in component or "db" in component:
            return [
                {
                    "title": "Database Health Check",
                    "description": "Verify database server status, connection pool settings, and query performance."
                },
                {
                    "title": "Database Monitoring",
                    "description": "Set up monitoring for database connection counts, query performance, and server resources."
                }
            ]
        
        elif "network" in component or "connection" in component:
            return [
                {
                    "title": "Network Diagnostics",
                    "description": "Run network diagnostics to check for packet loss, latency, or connectivity issues."
                },
                {
                    "title": "Network Redundancy",
                    "description": "Ensure redundant network paths are available and properly configured."
                }
            ]
        
        elif "security" in component or "auth" in component:
            return [
                {
                    "title": "Security Audit",
                    "description": "Conduct a security audit focusing on authentication and authorization mechanisms."
                },
                {
                    "title": "Rate Limiting",
                    "description": "Implement or adjust rate limiting to prevent brute force attacks."
                }
            ]
        
        elif "api" in component or "service" in component:
            return [
                {
                    "title": "Service Health Monitoring",
                    "description": "Set up health checks and monitoring for the API service."
                },
                {
                    "title": "Service Documentation",
                    "description": "Ensure API contracts and documentation are up to date for proper integration."
                }
            ]
        
        return []

# Singleton instance for the application
_anomaly_detector = None

def get_anomaly_detector():
    """Get or create the anomaly detector singleton"""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetector()
    return _anomaly_detector

def get_anomalies():
    """Get all detected anomalies"""
    detector = get_anomaly_detector()
    return detector.detect_anomalies()

def get_anomaly_recommendations(anomaly_id):
    """Get recommendations for an anomaly"""
    detector = get_anomaly_detector()
    return detector.get_recommendations(anomaly_id)

def get_anomaly_stats():
    """Get statistics about detected anomalies"""
    anomalies = get_anomalies()
    
    stats = {
        "total_count": len(anomalies),
        "by_severity": defaultdict(int),
        "by_component": defaultdict(int),
        "by_type": defaultdict(int),
        "by_file": defaultdict(int),
        "recent_anomalies": anomalies[:5] if anomalies else []
    }
    
    for anomaly in anomalies:
        severity_name = "UNKNOWN"
        for name, level in SEVERITY_LEVELS.items():
            if level == anomaly["severity"]:
                severity_name = name
                break
        
        stats["by_severity"][severity_name] += 1
        stats["by_component"][anomaly["component"]] += 1
        stats["by_type"][anomaly["type"]] += 1
        stats["by_file"][anomaly["source_file"]] += 1
    
    return stats