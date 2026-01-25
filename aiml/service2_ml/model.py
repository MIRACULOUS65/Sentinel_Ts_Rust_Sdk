"""
Sentinel Service 2: ML Risk Engine
Analyzes wallet features using Isolation Forest to detect anomalies.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os
import random

# Mock model path
MODEL_PATH = "risk_model.pkl"

class RiskEngine:
    def __init__(self):
        self.model = None
        self._train_mock_model()
        
    def _train_mock_model(self):
        """
        Train a lightweight model on synthetic data for the demo.
        Normal behavior: consistent low frequency, moderate amounts.
        Anomalous behavior: high bursts, circular patterns.
        """
        # Generate synthetic "normal" data
        # Feature vector: [tx_count, burst_rate, unique_interactions, age_days]
        X_train = np.random.normal(loc=[10, 0.01, 5, 30], scale=[5, 0.005, 2, 10], size=(100, 4))
        
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(X_train)
        
    def analyze_risk(self, features):
        """
        Predict risk score based on features.
        Returns: { risk_score (0-100), reason }
        """
        if features['tx_count'] == 0:
            return {
                "risk_score": 0,
                "reason": "New/Inactive wallet"
            }
            
        # Prepare vector
        vec = np.array([[
            features['tx_count'],
            features['burst_rate'],
            features['unique_interactions'],
            features['age_days']
        ]])
        
        # Predict anomaly score
        # Isolation Forest returns -1 for anomaly, 1 for normal
        # decision_function returns negative for anomaly, positive for normal
        score_raw = self.model.decision_function(vec)[0]
        
        # Normalize to 0-100 Risk Score
        # Typical range of score_raw is -0.5 to 0.5
        # We want: Low score_raw (anomaly) -> High Risk
        #          High score_raw (normal) -> Low Risk
        
        risk_score = 0
        reason = "Normal Activity"
        
        if score_raw < 0:
            # Anomaly
            risk_score = 70 + int(abs(score_raw) * 50)
            risk_score = min(99, risk_score)
            
            # Simple heuristic for reason
            if features['burst_rate'] > 0.1:
                reason = "High Frequency Burst Detected"
            elif features['age_days'] < 1:
                reason = "Suspiciously New Account Activity"
            else:
                reason = "Statistical Anomaly Detected"
        else:
            # Normal
            risk_score = max(0, 10 - int(score_raw * 20))
            
        return {
            "wallet": features['wallet'],
            "risk_score": risk_score,
            "reason": reason,
            "raw_anomaly_score": float(score_raw)
        }

if __name__ == "__main__":
    engine = RiskEngine()
    # Test normal
    test_feat = {"wallet": "G...", "tx_count": 10, "burst_rate": 0.01, "unique_interactions": 5, "age_days": 50}
    print(f"Normal: {engine.analyze_risk(test_feat)}")
    
    # Test anomaly
    bad_feat = {"wallet": "G...", "tx_count": 50, "burst_rate": 0.5, "unique_interactions": 2, "age_days": 0.1}
    print(f"Anomaly: {engine.analyze_risk(bad_feat)}")
