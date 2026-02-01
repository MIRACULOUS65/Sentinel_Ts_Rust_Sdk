"""
Isolation Forest Model
Provides overall anomaly detection as a complement to pattern scoring.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import os
from typing import List, Optional, Tuple


class AnomalyModel:
    """
    Isolation Forest for detecting overall behavioral anomalies.
    Works alongside PatternScorer for comprehensive risk assessment.
    """
    
    def __init__(
        self,
        n_estimators: int = 300,
        contamination: float = 0.1,
        max_samples: str = "auto",
        random_state: int = 42
    ):
        """
        Args:
            n_estimators: Number of trees (higher = more stable)
            contamination: Expected proportion of anomalies
            max_samples: Samples per tree
            random_state: For reproducibility
        """
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.max_samples = max_samples
        self.random_state = random_state
        
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            max_samples=max_samples,
            random_state=random_state,
            n_jobs=-1,
            warm_start=False
        )
        
        self.is_fitted = False
        
        # Score calibration parameters
        self.score_p5 = None
        self.score_p95 = None
        self.score_mean = None
        self.score_std = None
    
    def fit(self, feature_matrix: np.ndarray):
        """
        Train the Isolation Forest.
        
        Args:
            feature_matrix: Shape (n_samples, n_features)
        """
        n_samples = len(feature_matrix)
        
        print(f"\n🌲 Training Isolation Forest:")
        print(f"   • Samples: {n_samples}")
        print(f"   • Estimators: {self.n_estimators}")
        print(f"   • Contamination: {self.contamination}")
        
        # Fit the model
        self.model.fit(feature_matrix)
        self.is_fitted = True
        
        # Calibrate scoring using training data
        print(f"\n📊 Calibrating score distribution...")
        raw_scores = self.model.decision_function(feature_matrix)
        
        self.score_p5 = np.percentile(raw_scores, 5)
        self.score_p95 = np.percentile(raw_scores, 95)
        self.score_mean = np.mean(raw_scores)
        self.score_std = np.std(raw_scores)
        
        print(f"   • Score range: [{self.score_p5:.4f}, {self.score_p95:.4f}]")
        print(f"   • Score mean: {self.score_mean:.4f} ± {self.score_std:.4f}")
        print(f"✅ Isolation Forest trained")
    
    def predict_raw(self, feature_vector: List[float]) -> float:
        """
        Get raw anomaly score from Isolation Forest.
        Lower = more anomalous.
        
        Args:
            feature_vector: Single feature vector
        
        Returns:
            Raw decision function score
        """
        if not self.is_fitted:
            return 0.0
        
        return self.model.decision_function([feature_vector])[0]
    
    def predict_normalized(self, feature_vector: List[float]) -> int:
        """
        Get normalized anomaly score (0-100).
        Uses percentile-based calibration.
        
        Args:
            feature_vector: Single feature vector
        
        Returns:
            Score 0-100 (higher = more anomalous)
        """
        if not self.is_fitted:
            return 0
        
        raw = self.predict_raw(feature_vector)
        
        # Map using percentiles
        # Lower raw score = more anomalous = higher output score
        if self.score_p5 is not None and self.score_p95 is not None:
            score_range = self.score_p95 - self.score_p5
            if score_range > 0:
                # Invert and normalize
                normalized = (self.score_p95 - raw) / score_range
                return min(100, max(0, int(normalized * 100)))
        
        # Fallback
        return min(100, max(0, int((0.5 - raw) * 100)))
    
    def save(self, filepath: str):
        """Save trained model to disk."""
        if not self.is_fitted:
            raise ValueError("Cannot save untrained model")
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'is_fitted': self.is_fitted,
                'n_estimators': self.n_estimators,
                'contamination': self.contamination,
                'score_p5': self.score_p5,
                'score_p95': self.score_p95,
                'score_mean': self.score_mean,
                'score_std': self.score_std,
            }, f)
        print(f"✅ Isolation Forest saved to {filepath}")
    
    def load(self, filepath: str):
        """Load trained model from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.is_fitted = data['is_fitted']
            self.n_estimators = data.get('n_estimators', 300)
            self.contamination = data.get('contamination', 0.1)
            self.score_p5 = data.get('score_p5')
            self.score_p95 = data.get('score_p95')
            self.score_mean = data.get('score_mean')
            self.score_std = data.get('score_std')
        
        print(f"✅ Isolation Forest loaded from {filepath}")
