"""
Risk Engine V2
Uses Neural Network model with Pattern Scorer fallback.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import pickle
import os

from .features import FeatureExtractor
from .pattern_scorer import PatternScorer
from .model import AnomalyModel
from .state_manager import WalletStateManager


class RiskEngine:
    """
    Main risk assessment engine.
    Uses Neural Network (if available) with Pattern Scorer fallback.
    """
    
    def __init__(
        self,
        pattern_weight: float = 0.5,  # Weight for pattern scoring
        neural_weight: float = 0.5    # Weight for neural network
    ):
        self.pattern_weight = pattern_weight
        self.neural_weight = neural_weight
        
        self.extractor = FeatureExtractor()
        self.scorer = PatternScorer()
        self.model = AnomalyModel()
        
        # Neural network model (optional)
        self.neural_model = None
        self.use_neural = False
        
        # Feature normalization params
        self.feature_mins = None
        self.feature_maxs = None
        
        self.is_fitted = False
    
    def train(
        self,
        state_manager: WalletStateManager,
        progress_callback: Optional[callable] = None
    ):
        """Train the risk engine from wallet state."""
        print("\n" + "=" * 60)
        print("🧠 TRAINING RISK ENGINE")
        print("=" * 60)
        
        wallets = list(state_manager.sender_history.keys())
        min_txs = 5
        valid_wallets = [
            w for w in wallets 
            if len(state_manager.sender_history[w]) >= min_txs
        ]
        
        print(f"\n📊 Training Data:")
        print(f"   • Total wallets: {len(wallets)}")
        print(f"   • Valid wallets (≥{min_txs} txs): {len(valid_wallets)}")
        
        if not valid_wallets:
            raise ValueError("No wallets with sufficient transaction history")
        
        print(f"\n🔍 Extracting features...")
        feature_matrix = []
        feature_names = FeatureExtractor.get_feature_names()
        
        for i, wallet in enumerate(valid_wallets):
            sender_txs = state_manager.sender_history[wallet]
            receiver_txs = state_manager.receiver_history.get(wallet, [])
            current_ts = max(tx["timestamp"] for tx in sender_txs)
            
            features = self.extractor.extract_features(sender_txs, receiver_txs, current_ts)
            feature_vec = [features[name] for name in feature_names]
            feature_matrix.append(feature_vec)
            
            if progress_callback and i % 100 == 0:
                progress_callback(i, len(valid_wallets))
        
        feature_matrix = np.array(feature_matrix)
        
        # Store normalization parameters
        self.feature_mins = np.min(feature_matrix, axis=0)
        self.feature_maxs = np.max(feature_matrix, axis=0)
        
        print(f"   • Feature matrix shape: {feature_matrix.shape}")
        
        self.scorer.fit(feature_matrix, feature_names)
        self.model.fit(feature_matrix)
        
        self.is_fitted = True
        
        print("\n" + "=" * 60)
        print("✅ TRAINING COMPLETE")
        print("=" * 60)
    
    def _normalize_features(self, feature_vec: List[float]) -> np.ndarray:
        """Normalize features to 0-1 range."""
        if self.feature_mins is None or self.feature_maxs is None:
            return np.array(feature_vec)
        
        features = np.array(feature_vec)
        ranges = self.feature_maxs - self.feature_mins
        ranges[ranges == 0] = 1  # Avoid division by zero
        
        return (features - self.feature_mins) / ranges
    
    def predict(
        self,
        wallet: str,
        state_manager: WalletStateManager,
        current_ts: Optional[float] = None
    ) -> Tuple[int, str, Dict]:
        """Predict risk for a wallet using neural network if available."""
        if not self.is_fitted:
            return 0, "model not trained", {}
        
        sender_txs = state_manager.sender_history.get(wallet, [])
        receiver_txs = state_manager.receiver_history.get(wallet, [])
        
        if len(sender_txs) < 2:
            return 0, "insufficient transaction history", {"tx_count": len(sender_txs)}
        
        if current_ts is None:
            current_ts = max(tx["timestamp"] for tx in sender_txs)
        
        # Extract features
        features = self.extractor.extract_features(sender_txs, receiver_txs, current_ts)
        feature_vec = [features[name] for name in FeatureExtractor.get_feature_names()]
        
        # Get pattern scores
        pattern_score, pattern_reason, pattern_details = self.scorer.get_risk_assessment(features)
        
        # Try neural network if available
        neural_score = 0
        if self.use_neural and self.neural_model is not None:
            try:
                normalized = self._normalize_features(feature_vec)
                neural_pred = self.neural_model.predict(normalized.reshape(1, -1))
                neural_score = int(neural_pred[0])
            except Exception as e:
                neural_score = pattern_score  # Fallback
        else:
            # Use Isolation Forest as fallback
            neural_score = self.model.predict_normalized(feature_vec)
        
        # Combine scores
        if self.use_neural:
            final_score = int(
                self.pattern_weight * pattern_score + 
                self.neural_weight * neural_score
            )
        else:
            final_score = int(
                0.7 * pattern_score + 
                0.3 * neural_score
            )
        
        final_score = min(100, max(0, final_score))
        
        # Determine reason
        if final_score >= 70:
            reason = pattern_reason if "normal" not in pattern_reason else "high-risk behavioral pattern"
        elif final_score >= 31:
            reason = f"moderate {pattern_reason.split()[-1]} signals" if pattern_reason else "elevated risk signals"
        else:
            reason = "normal transaction pattern"
        
        details = {
            "pattern_score": pattern_score,
            "neural_score": neural_score,
            "pattern_reason": pattern_reason,
            "pattern_details": pattern_details,
            "final_score": final_score,
            "features": features,
            "tx_count": len(sender_txs),
            "using_neural": self.use_neural
        }
        
        return final_score, reason, details
    
    def save(self, directory: str):
        """Save all models to a directory."""
        os.makedirs(directory, exist_ok=True)
        
        self.scorer.save(os.path.join(directory, "pattern_scorer.pkl"))
        self.model.save(os.path.join(directory, "isolation_forest.pkl"))
        
        with open(os.path.join(directory, "metadata.pkl"), 'wb') as f:
            pickle.dump({
                'is_fitted': self.is_fitted,
                'pattern_weight': self.pattern_weight,
                'neural_weight': self.neural_weight,
                'feature_mins': self.feature_mins,
                'feature_maxs': self.feature_maxs,
                'use_neural': self.use_neural
            }, f)
        
        print(f"\n✅ Risk engine saved to {directory}/")
    
    def load(self, directory: str):
        """Load all models from a directory."""
        self.scorer.load(os.path.join(directory, "pattern_scorer.pkl"))
        self.model.load(os.path.join(directory, "isolation_forest.pkl"))
        
        # Try to load neural model
        neural_path = os.path.join(directory, "neural_model.pkl")
        if os.path.exists(neural_path):
            try:
                from .neural_model import NeuralRiskModel
                self.neural_model = NeuralRiskModel()
                self.neural_model.load(neural_path)
                self.use_neural = True
                print("✅ Neural network model loaded")
            except Exception as e:
                print(f"⚠️ Could not load neural model: {e}")
                self.use_neural = False
        
        with open(os.path.join(directory, "metadata.pkl"), 'rb') as f:
            meta = pickle.load(f)
            self.is_fitted = meta['is_fitted']
            self.pattern_weight = meta.get('pattern_weight', 0.5)
            self.neural_weight = meta.get('neural_weight', 0.5)
            self.feature_mins = meta.get('feature_mins')
            self.feature_maxs = meta.get('feature_maxs')
            if 'use_neural' in meta:
                self.use_neural = meta['use_neural'] and self.neural_model is not None
        
        print(f"\n✅ Risk engine loaded from {directory}/")
        print(f"   • Using neural network: {self.use_neural}")
