"""
Pattern-Specific Scorer V2
Improved scoring with more diverse risk distribution.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import pickle
import os


class PatternScorer:
    """
    Computes pattern-specific anomaly scores using Z-score analysis.
    V2: Improved thresholds for more diverse scoring.
    """
    
    # Pattern definitions with IMPROVED weights and thresholds
    PATTERN_FEATURES = {
        "circular": {
            "features": ["return_ratio", "self_transfer_ratio"],
            "weights": [0.6, 0.4],
            "threshold": 2.0,  # Higher threshold = fewer false positives
            "reason": "circular transfer pattern detected"
        },
        "bot": {
            # Bots: HIGH tx_count, LOW fan_out_score, similar amounts
            "features": ["tx_count_1h", "fan_out_score", "std_amount"],
            "weights": [0.3, -0.4, -0.3],  # Negative = LOW value is suspicious
            "threshold": 2.5,  # Higher threshold for bot detection
            "reason": "automated bot-like behavior"
        },
        "burst": {
            "features": ["tx_velocity", "tx_count_10m", "tx_count_1m"],
            "weights": [0.4, 0.3, 0.3],
            "threshold": 2.0,
            "reason": "sudden transaction burst"
        },
        "fan_out": {
            "features": ["unique_recipients_1h", "fan_out_score", "tx_count_1h"],
            "weights": [0.4, 0.3, 0.3],
            "threshold": 2.0,
            "reason": "high fan-out distribution"
        },
        "layering": {
            "features": ["tx_velocity", "avg_interval", "tx_count_10m"],
            "weights": [0.3, -0.4, 0.3],
            "threshold": 2.5,
            "reason": "rapid fund layering"
        },
        "dust": {
            "features": ["dust_tx_ratio", "mean_amount"],
            "weights": [0.7, -0.3],
            "threshold": 1.5,
            "reason": "dust spam activity"
        }
    }
    
    REASON_MAP = {
        "circular": "circular transfer pattern detected",
        "bot": "automated bot-like behavior",
        "burst": "sudden transaction burst",
        "fan_out": "high fan-out distribution",
        "layering": "rapid fund layering",
        "dust": "dust spam activity",
        "normal": "normal transaction pattern"
    }
    
    def __init__(self):
        self.feature_stats: Dict[str, Dict] = {}
        self.is_fitted = False
    
    def fit(self, feature_matrix: np.ndarray, feature_names: List[str]):
        """Compute baseline statistics from training data."""
        print("\n📊 Fitting pattern scorer V2...")
        
        for i, name in enumerate(feature_names):
            values = feature_matrix[:, i]
            self.feature_stats[name] = {
                "mean": np.mean(values),
                "std": np.std(values) + 1e-9,
                "p25": np.percentile(values, 25),
                "p75": np.percentile(values, 75),
                "p90": np.percentile(values, 90),
            }
            print(f"   {name}: μ={self.feature_stats[name]['mean']:.3f}, σ={self.feature_stats[name]['std']:.3f}")
        
        self.is_fitted = True
        print("✅ Pattern scorer V2 fitted")
    
    def compute_zscore(self, feature_name: str, value: float) -> float:
        """Compute Z-score for a feature value."""
        if feature_name not in self.feature_stats:
            return 0.0
        
        stats = self.feature_stats[feature_name]
        return (value - stats["mean"]) / stats["std"]
    
    def score_pattern(self, pattern: str, features: Dict[str, float]) -> Tuple[float, float]:
        """Score a specific pattern with improved thresholds."""
        if not self.is_fitted:
            return 0.0, 0
        
        pattern_config = self.PATTERN_FEATURES.get(pattern)
        if not pattern_config:
            return 0.0, 0
        
        weighted_z = 0.0
        total_weight = 0.0
        
        for feat_name, weight in zip(pattern_config["features"], pattern_config["weights"]):
            if feat_name in features:
                z = self.compute_zscore(feat_name, features[feat_name])
                weighted_z += abs(weight) * z * np.sign(weight)
                total_weight += abs(weight)
        
        if total_weight > 0:
            weighted_z /= total_weight
        
        threshold = pattern_config["threshold"]
        
        # IMPROVED scoring curve - more diverse distribution
        # Only flag as high risk if significantly above threshold
        if weighted_z >= threshold * 2:  # Very extreme
            score = 80 + min(20, (weighted_z - threshold * 2) * 10)
        elif weighted_z >= threshold * 1.5:  # High
            score = 60 + (weighted_z - threshold * 1.5) / (threshold * 0.5) * 20
        elif weighted_z >= threshold:  # Moderate
            score = 35 + (weighted_z - threshold) / (threshold * 0.5) * 25
        elif weighted_z >= threshold * 0.5:  # Low concern
            score = 15 + (weighted_z - threshold * 0.5) / (threshold * 0.5) * 20
        elif weighted_z > 0:  # Minimal
            score = weighted_z / (threshold * 0.5) * 15
        else:
            score = 0
        
        return weighted_z, min(100, max(0, int(score)))
    
    def score_all_patterns(self, features: Dict[str, float]) -> Dict[str, int]:
        """Score all patterns for a wallet."""
        scores = {}
        for pattern in self.PATTERN_FEATURES:
            _, score = self.score_pattern(pattern, features)
            scores[pattern] = score
        return scores
    
    def get_risk_assessment(self, features: Dict[str, float]) -> Tuple[int, str, Dict[str, int]]:
        """Get final risk assessment with improved diversity."""
        pattern_scores = self.score_all_patterns(features)
        
        max_pattern = max(pattern_scores, key=pattern_scores.get)
        max_score = pattern_scores[max_pattern]
        
        # Better reasoning based on score level
        if max_score >= 70:
            reason = self.REASON_MAP.get(max_pattern, "anomalous behavior")
        elif max_score >= 35:
            reason = f"moderate {max_pattern} signals"
        else:
            reason = "normal transaction pattern"
        
        return max_score, reason, pattern_scores
    
    def save(self, filepath: str):
        """Save fitted scorer to disk."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted scorer")
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'feature_stats': self.feature_stats,
                'is_fitted': self.is_fitted
            }, f)
        print(f"✅ Pattern scorer saved to {filepath}")
    
    def load(self, filepath: str):
        """Load fitted scorer from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Scorer file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.feature_stats = data['feature_stats']
            self.is_fitted = data['is_fitted']
        print(f"✅ Pattern scorer loaded from {filepath}")
