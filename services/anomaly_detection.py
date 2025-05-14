"""
Advanced Anomaly Detection Service

This module provides various anomaly detection algorithms for detecting
anomalies in time series data, including:
1. Statistical methods (Z-score, IQR)
2. Machine learning methods (Isolation Forest, One-Class SVM)
3. Density-based methods (DBSCAN, LOF)
4. Time series methods (ARIMA, LSTM Autoencoder)
"""

import numpy as np
import logging
from enum import Enum
from typing import Dict, List, Tuple, Union, Optional, Any
from dataclasses import dataclass

# Set up logging
logger = logging.getLogger(__name__)

class AnomalyAlgorithm(Enum):
    """Enum of supported anomaly detection algorithms"""
    ZSCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    DBSCAN = "dbscan"
    LOF = "local_outlier_factor"
    ARIMA = "arima"
    LSTM_AUTOENCODER = "lstm_autoencoder"


@dataclass
class AnomalyResult:
    """Result from an anomaly detection algorithm"""
    algorithm: str
    anomaly_indices: List[int]  # Indices of detected anomalies
    anomaly_scores: List[float]  # Anomaly scores (higher = more anomalous)
    threshold: float  # Threshold used to determine anomalies
    metadata: Optional[Dict[str, Any]] = None  # Additional algorithm-specific info


class AnomalyDetector:
    """Main class for detecting anomalies using various algorithms"""
    
    def __init__(self, algorithm: Union[str, AnomalyAlgorithm] = AnomalyAlgorithm.ZSCORE, 
                 params: Optional[Dict[str, Any]] = None):
        """
        Initialize the anomaly detector with the specified algorithm
        
        Args:
            algorithm: Algorithm to use for anomaly detection
            params: Parameters for the algorithm
        """
        if isinstance(algorithm, str):
            try:
                self.algorithm = AnomalyAlgorithm(algorithm)
            except ValueError:
                logger.warning(f"Unknown algorithm '{algorithm}', falling back to Z-score")
                self.algorithm = AnomalyAlgorithm.ZSCORE
        else:
            self.algorithm = algorithm
            
        self.params = params or {}
        logger.info(f"Initialized anomaly detector with algorithm: {self.algorithm.value}")
    
    def detect(self, data: Union[List[float], np.ndarray], 
               timestamps: Optional[Union[List[str], np.ndarray]] = None) -> AnomalyResult:
        """
        Detect anomalies in the given data
        
        Args:
            data: Time series data to analyze
            timestamps: Optional timestamps corresponding to the data points
            
        Returns:
            AnomalyResult object containing the detected anomalies
        """
        # Convert data to numpy array if needed
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        # Call the appropriate algorithm based on the selection
        if self.algorithm == AnomalyAlgorithm.ZSCORE:
            return self._detect_zscore(data)
        elif self.algorithm == AnomalyAlgorithm.IQR:
            return self._detect_iqr(data)
        elif self.algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
            return self._detect_isolation_forest(data)
        elif self.algorithm == AnomalyAlgorithm.ONE_CLASS_SVM:
            return self._detect_one_class_svm(data)
        elif self.algorithm == AnomalyAlgorithm.DBSCAN:
            return self._detect_dbscan(data)
        elif self.algorithm == AnomalyAlgorithm.LOF:
            return self._detect_lof(data)
        elif self.algorithm == AnomalyAlgorithm.ARIMA:
            return self._detect_arima(data, timestamps)
        elif self.algorithm == AnomalyAlgorithm.LSTM_AUTOENCODER:
            return self._detect_lstm_autoencoder(data)
        else:
            logger.warning(f"Unknown algorithm '{self.algorithm}', falling back to Z-score")
            return self._detect_zscore(data)
    
    def _detect_zscore(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using Z-score method
        
        Z-score measures how many standard deviations a data point is from the mean.
        Points with |z| > threshold are considered anomalies.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        threshold = self.params.get('threshold', 3.0)  # Default threshold: 3.0
        
        # Calculate mean and standard deviation
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            # Handle the case where all values are the same
            logger.warning("Z-score calculation: Standard deviation is zero, no anomalies detected")
            return AnomalyResult(
                algorithm=self.algorithm.value,
                anomaly_indices=[],
                anomaly_scores=[0.0] * len(data),
                threshold=threshold
            )
        
        # Calculate z-scores
        z_scores = np.abs((data - mean) / std)
        
        # Identify anomalies
        anomaly_indices = np.where(z_scores > threshold)[0].tolist()
        
        return AnomalyResult(
            algorithm=self.algorithm.value,
            anomaly_indices=anomaly_indices,
            anomaly_scores=z_scores.tolist(),
            threshold=threshold,
            metadata={
                'mean': float(mean),
                'std': float(std)
            }
        )
    
    def _detect_iqr(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using Interquartile Range (IQR) method
        
        IQR is the range between the first quartile (Q1) and third quartile (Q3).
        Points outside Q1 - k*IQR to Q3 + k*IQR are considered anomalies.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        k = self.params.get('k', 1.5)  # Default multiplier: 1.5
        
        # Calculate quartiles
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        # Calculate lower and upper bounds
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr
        
        # Calculate "scores" as distance from the nearest bound
        scores = np.zeros_like(data, dtype=float)
        for i, val in enumerate(data):
            if val < lower_bound:
                scores[i] = (lower_bound - val) / iqr
            elif val > upper_bound:
                scores[i] = (val - upper_bound) / iqr
        
        # Identify anomalies
        anomaly_indices = np.where((data < lower_bound) | (data > upper_bound))[0].tolist()
        
        return AnomalyResult(
            algorithm=self.algorithm.value,
            anomaly_indices=anomaly_indices,
            anomaly_scores=scores.tolist(),
            threshold=k,
            metadata={
                'q1': float(q1),
                'q3': float(q3),
                'iqr': float(iqr),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            }
        )
    
    def _detect_isolation_forest(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using Isolation Forest algorithm
        
        Isolation Forest isolates observations by randomly selecting a feature
        and then randomly selecting a split value between the maximum and minimum
        values of that feature. Anomalies require fewer splits to isolate.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            logger.error("scikit-learn is not installed. Cannot use Isolation Forest.")
            return self._detect_zscore(data)  # Fallback to Z-score
            
        # Get parameters for the algorithm
        contamination = self.params.get('contamination', 'auto')
        n_estimators = self.params.get('n_estimators', 100)
        max_samples = self.params.get('max_samples', 'auto')
        
        # Reshape data for scikit-learn
        X = data.reshape(-1, 1)
        
        # Create and fit the model
        model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=42
        )
        model.fit(X)
        
        # Get anomaly scores (-1 for anomalies, 1 for normal points)
        predictions = model.predict(X)
        scores = model.decision_function(X)
        
        # Normalize scores to [0, 1] where higher values indicate more anomalous points
        normalized_scores = 1.0 - (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
        
        # Get anomaly indices
        anomaly_indices = np.where(predictions == -1)[0].tolist()
        
        return AnomalyResult(
            algorithm=self.algorithm.value,
            anomaly_indices=anomaly_indices,
            anomaly_scores=normalized_scores.tolist(),
            threshold=0.5,  # Decision boundary value
            metadata={
                'contamination': contamination,
                'n_estimators': n_estimators
            }
        )
    
    def _detect_one_class_svm(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using One-Class Support Vector Machine
        
        One-Class SVM learns a boundary around the normal data points and
        classifies points outside this boundary as anomalies.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        try:
            from sklearn.svm import OneClassSVM
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            logger.error("scikit-learn is not installed. Cannot use One-Class SVM.")
            return self._detect_zscore(data)  # Fallback to Z-score
            
        # Get parameters for the algorithm
        nu = self.params.get('nu', 0.05)  # Upper bound on the fraction of outliers
        kernel = self.params.get('kernel', 'rbf')
        gamma = self.params.get('gamma', 'scale')
        
        # Reshape data for scikit-learn
        X = data.reshape(-1, 1)
        
        # Scale the data for better performance
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Create and fit the model
        model = OneClassSVM(
            nu=nu,
            kernel=kernel,
            gamma=gamma
        )
        model.fit(X_scaled)
        
        # Get predictions (-1 for anomalies, +1 for normal points)
        predictions = model.predict(X_scaled)
        
        # Get decision function values (distance from the separating hyperplane)
        scores = model.decision_function(X_scaled)
        
        # Normalize scores to [0, 1] where higher values indicate more anomalous points
        normalized_scores = 1.0 - (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
        
        # Get anomaly indices
        anomaly_indices = np.where(predictions == -1)[0].tolist()
        
        return AnomalyResult(
            algorithm=self.algorithm.value,
            anomaly_indices=anomaly_indices,
            anomaly_scores=normalized_scores.tolist(),
            threshold=0.5,
            metadata={
                'nu': nu,
                'kernel': kernel,
                'gamma': gamma
            }
        )
    
    def _detect_dbscan(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using DBSCAN clustering
        
        DBSCAN (Density-Based Spatial Clustering of Applications with Noise)
        groups together points that are close to each other. Points that
        cannot be grouped are considered anomalies.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        try:
            from sklearn.cluster import DBSCAN
        except ImportError:
            logger.error("scikit-learn is not installed. Cannot use DBSCAN.")
            return self._detect_zscore(data)  # Fallback to Z-score
            
        # Get parameters for the algorithm
        eps = self.params.get('eps', 0.5)  # Maximum distance between points
        min_samples = self.params.get('min_samples', 5)  # Minimum points to form a dense region
        
        # Reshape data for scikit-learn
        X = data.reshape(-1, 1)
        
        # Create and fit the model
        model = DBSCAN(
            eps=eps,
            min_samples=min_samples
        )
        clusters = model.fit_predict(X)
        
        # Points labeled as -1 are anomalies
        anomaly_indices = np.where(clusters == -1)[0].tolist()
        
        # Generate anomaly scores (1.0 for anomalies, 0.0 for normal points)
        scores = np.zeros_like(data, dtype=float)
        scores[anomaly_indices] = 1.0
        
        return AnomalyResult(
            algorithm=self.algorithm.value,
            anomaly_indices=anomaly_indices,
            anomaly_scores=scores.tolist(),
            threshold=0.5,
            metadata={
                'eps': eps,
                'min_samples': min_samples,
                'n_clusters': len(np.unique(clusters)) - (1 if -1 in clusters else 0)
            }
        )
    
    def _detect_lof(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using Local Outlier Factor
        
        LOF compares the local density of a point with the densities of its neighbors.
        Points with a significantly lower density than their neighbors are considered anomalies.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        try:
            from sklearn.neighbors import LocalOutlierFactor
        except ImportError:
            logger.error("scikit-learn is not installed. Cannot use Local Outlier Factor.")
            return self._detect_zscore(data)  # Fallback to Z-score
            
        # Get parameters for the algorithm
        n_neighbors = self.params.get('n_neighbors', 20)
        contamination = self.params.get('contamination', 'auto')
        
        # Reshape data for scikit-learn
        X = data.reshape(-1, 1)
        
        # Create and fit the model
        model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination,
            novelty=False  # We're using it for outlier detection, not novelty detection
        )
        
        # Fit predict returns labels (-1 for anomalies, 1 for normal points)
        predictions = model.fit_predict(X)
        
        # Get the negative outlier factor
        scores = -model.negative_outlier_factor_
        
        # Normalize scores to [0, 1]
        min_score = np.min(scores)
        max_score = np.max(scores)
        if max_score > min_score:
            normalized_scores = (scores - min_score) / (max_score - min_score)
        else:
            normalized_scores = np.zeros_like(scores)
        
        # Get anomaly indices
        anomaly_indices = np.where(predictions == -1)[0].tolist()
        
        return AnomalyResult(
            algorithm=self.algorithm.value,
            anomaly_indices=anomaly_indices,
            anomaly_scores=normalized_scores.tolist(),
            threshold=model.offset_,
            metadata={
                'n_neighbors': n_neighbors,
                'contamination': contamination
            }
        )
    
    def _detect_arima(self, data: np.ndarray, 
                      timestamps: Optional[Union[List[str], np.ndarray]] = None) -> AnomalyResult:
        """
        Detect anomalies using ARIMA (AutoRegressive Integrated Moving Average)
        
        ARIMA models the time series data and identifies points that deviate
        significantly from the predicted values.
        
        Args:
            data: Time series data
            timestamps: Timestamps corresponding to the data points
            
        Returns:
            AnomalyResult with detected anomalies
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
        except ImportError:
            logger.error("statsmodels is not installed. Cannot use ARIMA.")
            return self._detect_zscore(data)  # Fallback to Z-score
            
        # Get parameters for the algorithm
        order = self.params.get('order', (5, 1, 0))  # (p, d, q) parameters
        threshold = self.params.get('threshold', 3.0)  # Number of std deviations to consider anomalous
        
        # Handle missing data - ARIMA can't handle NaN values
        is_nan = np.isnan(data)
        if np.any(is_nan):
            logger.warning(f"Found {np.sum(is_nan)} NaN values. Imputing with mean.")
            data_filled = data.copy()
            data_filled[is_nan] = np.mean(data[~is_nan])
        else:
            data_filled = data
            
        try:
            # Fit the ARIMA model
            model = ARIMA(data_filled, order=order)
            model_fit = model.fit()
            
            # Get predictions and residuals
            predictions = model_fit.predict()
            residuals = data_filled - predictions
            
            # Calculate mean and standard deviation of residuals
            residuals_mean = np.mean(residuals)
            residuals_std = np.std(residuals)
            
            # Calculate z-scores of residuals
            if residuals_std > 0:
                z_scores = np.abs((residuals - residuals_mean) / residuals_std)
            else:
                z_scores = np.zeros_like(residuals)
            
            # Identify anomalies
            anomaly_indices = np.where(z_scores > threshold)[0].tolist()
            
            return AnomalyResult(
                algorithm=self.algorithm.value,
                anomaly_indices=anomaly_indices,
                anomaly_scores=z_scores.tolist(),
                threshold=threshold,
                metadata={
                    'order': order,
                    'residuals_mean': float(residuals_mean),
                    'residuals_std': float(residuals_std),
                    'aic': model_fit.aic
                }
            )
        except Exception as e:
            logger.error(f"Error in ARIMA modeling: {str(e)}")
            return self._detect_zscore(data)  # Fallback to Z-score
    
    def _detect_lstm_autoencoder(self, data: np.ndarray) -> AnomalyResult:
        """
        Detect anomalies using LSTM Autoencoder
        
        LSTM Autoencoder is a deep learning model that learns to reconstruct normal data.
        Points with high reconstruction error are considered anomalies.
        
        This is a placeholder implementation that returns a message indicating
        that actual implementation would require TensorFlow/Keras.
        
        Args:
            data: Time series data
            
        Returns:
            AnomalyResult with detected anomalies
        """
        # This would require TensorFlow/Keras, so we'll fall back to a simpler method
        logger.warning("LSTM Autoencoder requires TensorFlow and Keras. Falling back to Z-score.")
        return self._detect_zscore(data)


class AnomalyDetectionService:
    """
    Service for managing anomaly detection across multiple data sources and algorithms
    """
    
    def __init__(self):
        """Initialize the anomaly detection service"""
        self.detectors = {}
        
    def create_detector(self, name: str, algorithm: Union[str, AnomalyAlgorithm], 
                        params: Optional[Dict[str, Any]] = None) -> AnomalyDetector:
        """
        Create a new anomaly detector with the specified algorithm
        
        Args:
            name: Name to identify this detector
            algorithm: Algorithm to use for anomaly detection
            params: Parameters for the algorithm
            
        Returns:
            The created AnomalyDetector
        """
        detector = AnomalyDetector(algorithm, params)
        self.detectors[name] = detector
        return detector
    
    def get_detector(self, name: str) -> Optional[AnomalyDetector]:
        """
        Get an existing detector by name
        
        Args:
            name: Name of the detector
            
        Returns:
            The AnomalyDetector if found, None otherwise
        """
        return self.detectors.get(name)
    
    def detect_anomalies(self, name: str, data: Union[List[float], np.ndarray],
                         timestamps: Optional[Union[List[str], np.ndarray]] = None) -> Optional[AnomalyResult]:
        """
        Detect anomalies using the named detector
        
        Args:
            name: Name of the detector to use
            data: Time series data to analyze
            timestamps: Optional timestamps corresponding to the data points
            
        Returns:
            AnomalyResult if the detector exists, None otherwise
        """
        detector = self.get_detector(name)
        if detector:
            return detector.detect(data, timestamps)
        else:
            logger.warning(f"No detector found with name '{name}'")
            return None
    
    def detect_with_multiple_algorithms(self, data: Union[List[float], np.ndarray],
                                       algorithms: List[Union[str, AnomalyAlgorithm]] = None,
                                       timestamps: Optional[Union[List[str], np.ndarray]] = None
                                      ) -> Dict[str, AnomalyResult]:
        """
        Detect anomalies using multiple algorithms and combine the results
        
        Args:
            data: Time series data to analyze
            algorithms: List of algorithms to use (default: all available algorithms)
            timestamps: Optional timestamps corresponding to the data points
            
        Returns:
            Dictionary mapping algorithm names to AnomalyResult objects
        """
        if algorithms is None:
            # Use all available algorithms except LSTM Autoencoder
            algorithms = [algo for algo in AnomalyAlgorithm if algo != AnomalyAlgorithm.LSTM_AUTOENCODER]
        
        results = {}
        for algorithm in algorithms:
            detector = AnomalyDetector(algorithm)
            result = detector.detect(data, timestamps)
            results[result.algorithm] = result
            
        return results
    
    def ensemble_detection(self, data: Union[List[float], np.ndarray],
                          algorithms: List[Union[str, AnomalyAlgorithm]] = None,
                          threshold: float = 0.5,
                          timestamps: Optional[Union[List[str], np.ndarray]] = None
                         ) -> Tuple[List[int], List[float]]:
        """
        Perform ensemble anomaly detection by combining results from multiple algorithms
        
        Args:
            data: Time series data to analyze
            algorithms: List of algorithms to use (default: [ZSCORE, IQR, ISOLATION_FOREST])
            threshold: Fraction of algorithms that must agree for a point to be considered anomalous
            timestamps: Optional timestamps corresponding to the data points
            
        Returns:
            Tuple of (anomaly_indices, ensemble_scores)
        """
        if algorithms is None:
            # Default to a reasonable set of algorithms
            algorithms = [
                AnomalyAlgorithm.ZSCORE, 
                AnomalyAlgorithm.IQR, 
                AnomalyAlgorithm.ISOLATION_FOREST
            ]
        
        # Get results from each algorithm
        algorithm_results = []
        for algorithm in algorithms:
            detector = AnomalyDetector(algorithm)
            result = detector.detect(data, timestamps)
            algorithm_results.append(result)
        
        # Count how many algorithms consider each point anomalous
        n_points = len(data)
        anomaly_counts = np.zeros(n_points)
        
        for result in algorithm_results:
            for idx in result.anomaly_indices:
                if 0 <= idx < n_points:  # Ensure index is valid
                    anomaly_counts[idx] += 1
        
        # Normalize to get ensemble score
        ensemble_scores = anomaly_counts / len(algorithms)
        
        # Points are anomalies if at least threshold fraction of algorithms agree
        min_count = threshold * len(algorithms)
        anomaly_indices = np.where(anomaly_counts >= min_count)[0].tolist()
        
        return anomaly_indices, ensemble_scores.tolist()