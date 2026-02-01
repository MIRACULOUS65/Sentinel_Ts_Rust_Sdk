"""
Feature Extractor
Extracts 16 behavioral features from wallet transaction history.
All features are designed to have HIGH VARIANCE for effective anomaly detection.
"""
import numpy as np
from typing import Dict, List, Optional
from collections import Counter


class FeatureExtractor:
    """
    Extracts behavioral features from wallet transaction history.
    """
    
    # Feature names (must be consistent across training and inference)
    FEATURE_NAMES = [
        # Frequency features
        "tx_count_1m",
        "tx_count_10m", 
        "tx_count_1h",
        "tx_velocity",        # Rate of change in tx frequency
        
        # Amount features
        "mean_amount",
        "std_amount",
        "max_amount",
        "amount_range",       # max - min
        
        # Recipient diversity features
        "unique_recipients_1h",
        "same_recipient_ratio",
        "fan_out_score",       # unique_recipients / tx_count
        
        # Pattern features
        "burstiness_index",    # Variance in inter-tx times
        "dust_tx_ratio",       # Proportion of tiny txs
        "self_transfer_ratio", # A->A patterns (via intermediate)
        
        # Graph features (limited in streaming)
        "return_ratio",        # Funds returning to sender
        "avg_interval",        # Average time between txs
    ]
    
    # Dust threshold (0.01 XLM)
    DUST_THRESHOLD = 0.01
    
    def extract_features(
        self,
        sender_txs: List[Dict],
        receiver_txs: List[Dict],
        current_ts: float
    ) -> Dict[str, float]:
        """
        Extract all 16 features for a wallet.
        
        Args:
            sender_txs: Transactions where wallet is sender (all history)
            receiver_txs: Transactions where wallet is receiver (all history)
            current_ts: Current timestamp for windowing
        
        Returns:
            Dict mapping feature names to values
        """
        features = {}
        
        # Window the transactions
        def window(txs, seconds):
            cutoff = current_ts - seconds
            return [tx for tx in txs if tx["timestamp"] >= cutoff]
        
        # Windowed sender transactions
        sent_1m = window(sender_txs, 60)
        sent_10m = window(sender_txs, 600)
        sent_1h = window(sender_txs, 3600)
        sent_24h = window(sender_txs, 86400)
        
        # Windowed receiver transactions
        recv_1h = window(receiver_txs, 3600)
        recv_24h = window(receiver_txs, 86400)
        
        # === FREQUENCY FEATURES ===
        features["tx_count_1m"] = len(sent_1m)
        features["tx_count_10m"] = len(sent_10m)
        features["tx_count_1h"] = len(sent_1h)
        
        # Velocity: change in rate (10m vs 1h normalized)
        rate_10m = len(sent_10m) / 10 if sent_10m else 0
        rate_1h = len(sent_1h) / 60 if sent_1h else 0.001
        features["tx_velocity"] = rate_10m / rate_1h if rate_1h > 0 else 0
        
        # === AMOUNT FEATURES ===
        amounts = [tx["amount"] for tx in sent_1h] if sent_1h else [0]
        features["mean_amount"] = np.mean(amounts)
        features["std_amount"] = np.std(amounts) if len(amounts) > 1 else 0
        features["max_amount"] = max(amounts)
        features["amount_range"] = max(amounts) - min(amounts) if len(amounts) > 1 else 0
        
        # === RECIPIENT DIVERSITY FEATURES ===
        recipients_1h = [tx["to_addr"] for tx in sent_1h]
        unique_recipients = len(set(recipients_1h))
        features["unique_recipients_1h"] = unique_recipients
        
        # Same recipient ratio (most common / total)
        if recipients_1h:
            recipient_counts = Counter(recipients_1h)
            most_common_count = recipient_counts.most_common(1)[0][1]
            features["same_recipient_ratio"] = most_common_count / len(recipients_1h)
        else:
            features["same_recipient_ratio"] = 0
        
        # Fan-out score
        tx_count = len(sent_1h)
        features["fan_out_score"] = unique_recipients / tx_count if tx_count > 0 else 0
        
        # === PATTERN FEATURES ===
        
        # Burstiness: variance in inter-transaction times
        if len(sent_1h) >= 2:
            timestamps = sorted([tx["timestamp"] for tx in sent_1h])
            intervals = np.diff(timestamps)
            if len(intervals) > 0:
                mean_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                # Coefficient of variation (higher = more bursty)
                features["burstiness_index"] = std_interval / (mean_interval + 1)
            else:
                features["burstiness_index"] = 0
        else:
            features["burstiness_index"] = 0
        
        # Dust transaction ratio
        dust_count = sum(1 for tx in sent_1h if tx["amount"] <= self.DUST_THRESHOLD)
        features["dust_tx_ratio"] = dust_count / len(sent_1h) if sent_1h else 0
        
        # Self-transfer ratio (sender received funds back within 24h)
        sent_to = set(tx["to_addr"] for tx in sent_24h)
        recv_from = set(tx["from_addr"] for tx in recv_24h)
        overlap = sent_to & recv_from
        features["self_transfer_ratio"] = len(overlap) / len(sent_to) if sent_to else 0
        
        # === GRAPH FEATURES (limited in streaming) ===
        
        # Return ratio: proportion of recipients who sent back
        if sent_24h and recv_24h:
            recipients = set(tx["to_addr"] for tx in sent_24h)
            senders_back = set(tx["from_addr"] for tx in recv_24h)
            returns = recipients & senders_back
            features["return_ratio"] = len(returns) / len(recipients) if recipients else 0
        else:
            features["return_ratio"] = 0
        
        # Average interval between transactions
        if len(sent_1h) >= 2:
            timestamps = sorted([tx["timestamp"] for tx in sent_1h])
            intervals = np.diff(timestamps)
            features["avg_interval"] = np.mean(intervals)
        else:
            features["avg_interval"] = 3600  # Default to 1 hour
        
        return features
    
    def extract_feature_vector(
        self,
        sender_txs: List[Dict],
        receiver_txs: List[Dict],
        current_ts: float
    ) -> List[float]:
        """
        Extract features as a list (for sklearn).
        
        Returns:
            List of feature values in FEATURE_NAMES order
        """
        features = self.extract_features(sender_txs, receiver_txs, current_ts)
        return [features[name] for name in self.FEATURE_NAMES]
    
    @classmethod
    def get_feature_names(cls) -> List[str]:
        """Get ordered feature names."""
        return cls.FEATURE_NAMES.copy()
