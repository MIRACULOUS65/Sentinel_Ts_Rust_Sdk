"""
Behavior Profiles for Synthetic Data Generation
Each profile generates transactions with DISTINCT statistical patterns.
"""
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict
import hashlib


def generate_wallet_address(seed: int) -> str:
    """Generate deterministic Stellar-like wallet address."""
    h = hashlib.sha256(f"wallet_{seed}".encode()).hexdigest().upper()
    return f"G{h[:55]}"


class BehaviorProfile(ABC):
    """Base class for wallet behavior profiles."""
    
    def __init__(self, wallet: str, universe: List[str], rng: np.random.Generator):
        self.wallet = wallet
        self.universe = universe  # All wallets in the simulation
        self.rng = rng
    
    @property
    @abstractmethod
    def label(self) -> str:
        """Ground truth label for this behavior."""
        pass
    
    @abstractmethod
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        """Generate transactions for this wallet."""
        pass
    
    def _random_recipient(self, exclude_self: bool = True) -> str:
        """Pick a random recipient from the universe."""
        candidates = [w for w in self.universe if w != self.wallet] if exclude_self else self.universe
        return self.rng.choice(candidates)


class NormalBehavior(BehaviorProfile):
    """
    Normal wallet behavior:
    - Moderate transaction frequency (2-8 per day)
    - Log-normal amount distribution (median ~50 XLM)
    - Diverse recipients
    - No unusual patterns
    """
    
    @property
    def label(self) -> str:
        return "normal"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # 2-8 transactions per day on average
        daily_rate = self.rng.integers(2, 9)
        avg_interval = 86400 / daily_rate
        
        while current_ts < end_ts:
            # Poisson-like interval
            interval = self.rng.exponential(avg_interval)
            current_ts += interval
            
            if current_ts >= end_ts:
                break
            
            # Log-normal amounts (median ~50, can go 1-500)
            amount = self.rng.lognormal(mean=3.9, sigma=1.0)
            amount = min(max(amount, 1.0), 500.0)
            
            txs.append({
                "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}_{self.rng.random()}".encode()).hexdigest()[:16],
                "timestamp": current_ts,
                "from_addr": self.wallet,
                "to_addr": self._random_recipient(),
                "amount": round(amount, 2),
                "label": self.label
            })
        
        return txs


class WhaleBehavior(BehaviorProfile):
    """
    Whale behavior:
    - Low frequency (1-3 per day)
    - Very high amounts (10k-500k XLM)
    - Diverse recipients
    """
    
    @property
    def label(self) -> str:
        return "whale"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # 1-3 transactions per day
        daily_rate = self.rng.integers(1, 4)
        avg_interval = 86400 / daily_rate
        
        while current_ts < end_ts:
            interval = self.rng.exponential(avg_interval)
            current_ts += interval
            
            if current_ts >= end_ts:
                break
            
            # Very high amounts (10k-500k)
            amount = self.rng.uniform(10000, 500000)
            
            txs.append({
                "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}".encode()).hexdigest()[:16],
                "timestamp": current_ts,
                "from_addr": self.wallet,
                "to_addr": self._random_recipient(),
                "amount": round(amount, 2),
                "label": self.label
            })
        
        return txs


class CircularBehavior(BehaviorProfile):
    """
    Circular transfer pattern:
    - A → B → C → A loops
    - Regular intervals
    - Similar amounts in each cycle
    """
    
    @property
    def label(self) -> str:
        return "anomaly_circular"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # Create a fixed ring of 3-5 wallets
        ring_size = self.rng.integers(3, 6)
        ring = [self.wallet] + [self._random_recipient() for _ in range(ring_size - 1)]
        
        # Cycle every 30-120 minutes
        cycle_interval = self.rng.integers(1800, 7200)
        base_amount = self.rng.uniform(100, 1000)
        
        cycle_idx = 0
        while current_ts < end_ts:
            # Complete one cycle through the ring
            for i in range(ring_size):
                sender = ring[i]
                receiver = ring[(i + 1) % ring_size]
                
                # Only record transactions FROM our wallet
                if sender == self.wallet:
                    txs.append({
                        "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}_{cycle_idx}".encode()).hexdigest()[:16],
                        "timestamp": current_ts,
                        "from_addr": sender,
                        "to_addr": receiver,
                        "amount": round(base_amount * (1 + self.rng.uniform(-0.05, 0.05)), 2),
                        "label": self.label
                    })
                
                current_ts += self.rng.integers(10, 60)  # Small delay between hops
            
            cycle_idx += 1
            current_ts += cycle_interval
        
        return txs


class BotBehavior(BehaviorProfile):
    """
    Bot-like repetitive payments:
    - Same amount to same recipient repeatedly
    - Very regular intervals
    - High frequency
    """
    
    @property
    def label(self) -> str:
        return "anomaly_bot"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # Fixed recipient and amount
        target = self._random_recipient()
        fixed_amount = round(self.rng.uniform(10, 100), 2)
        
        # Very regular intervals (every 30-180 seconds)
        interval = self.rng.integers(30, 180)
        
        while current_ts < end_ts:
            txs.append({
                "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}".encode()).hexdigest()[:16],
                "timestamp": current_ts,
                "from_addr": self.wallet,
                "to_addr": target,
                "amount": fixed_amount,  # SAME amount every time
                "label": self.label
            })
            
            # Very consistent timing (±5 seconds)
            current_ts += interval + self.rng.integers(-5, 6)
        
        return txs


class BurstBehavior(BehaviorProfile):
    """
    Sudden burst of activity:
    - Normal activity with sudden spike
    - 10-50x increase in frequency during burst
    - Burst lasts 5-30 minutes
    """
    
    @property
    def label(self) -> str:
        return "anomaly_burst"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # Normal phase: 2-4 tx per day
        normal_interval = self.rng.integers(6 * 3600, 12 * 3600)
        
        # Burst parameters
        burst_start = start_ts + self.rng.uniform(0.3, 0.7) * duration_hours * 3600
        burst_duration = self.rng.integers(300, 1800)  # 5-30 minutes
        burst_end = burst_start + burst_duration
        burst_interval = self.rng.integers(5, 30)  # 5-30 seconds during burst
        
        while current_ts < end_ts:
            # Check if we're in burst mode
            if burst_start <= current_ts < burst_end:
                interval = burst_interval
                amount = self.rng.uniform(50, 500)  # Higher amounts during burst
            else:
                interval = normal_interval
                amount = self.rng.lognormal(3.5, 0.8)
            
            txs.append({
                "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}".encode()).hexdigest()[:16],
                "timestamp": current_ts,
                "from_addr": self.wallet,
                "to_addr": self._random_recipient(),
                "amount": round(min(amount, 1000), 2),
                "label": self.label
            })
            
            current_ts += interval + self.rng.uniform(-interval * 0.1, interval * 0.1)
        
        return txs


class FanOutBehavior(BehaviorProfile):
    """
    Fan-out pattern:
    - One wallet sends to MANY unique recipients
    - 50-200 unique recipients per day
    - Similar amounts
    """
    
    @property
    def label(self) -> str:
        return "anomaly_fan_out"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # High number of unique recipients
        num_recipients = min(self.rng.integers(50, 200), len(self.universe) - 1)
        recipients = self.rng.choice(
            [w for w in self.universe if w != self.wallet],
            size=num_recipients,
            replace=False
        )
        
        # Similar amounts for all
        base_amount = self.rng.uniform(10, 100)
        
        # Send to each recipient
        interval = (duration_hours * 3600) / num_recipients
        
        for recipient in recipients:
            if current_ts >= end_ts:
                break
            
            txs.append({
                "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}".encode()).hexdigest()[:16],
                "timestamp": current_ts,
                "from_addr": self.wallet,
                "to_addr": recipient,
                "amount": round(base_amount * (1 + self.rng.uniform(-0.1, 0.1)), 2),
                "label": self.label
            })
            
            current_ts += interval * self.rng.uniform(0.5, 1.5)
        
        return txs


class LayeringBehavior(BehaviorProfile):
    """
    Multi-hop layering:
    - A → B → C → D → E chains
    - Rapid succession (seconds between hops)
    - Amount decreases slightly per hop
    """
    
    @property
    def label(self) -> str:
        return "anomaly_layering"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # Create layering chains periodically
        chain_interval = self.rng.integers(3600, 7200)  # Every 1-2 hours
        
        while current_ts < end_ts:
            # Create a chain of 4-8 hops
            chain_length = self.rng.integers(4, 9)
            chain = [self.wallet] + [self._random_recipient() for _ in range(chain_length - 1)]
            
            base_amount = self.rng.uniform(500, 5000)
            
            # Quick succession through the chain
            for i in range(chain_length - 1):
                sender = chain[i]
                receiver = chain[i + 1]
                
                # Amount decreases (fees, splits)
                amount = base_amount * (0.95 ** i)
                
                # Only record from our wallet
                if sender == self.wallet:
                    txs.append({
                        "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}_{i}".encode()).hexdigest()[:16],
                        "timestamp": current_ts,
                        "from_addr": sender,
                        "to_addr": receiver,
                        "amount": round(amount, 2),
                        "label": self.label
                    })
                
                current_ts += self.rng.integers(5, 30)  # Very fast hops
            
            current_ts += chain_interval
        
        return txs


class DustBehavior(BehaviorProfile):
    """
    Dust spam:
    - Tiny amounts (0.0001 - 0.01 XLM)
    - Many recipients
    - High frequency
    """
    
    @property
    def label(self) -> str:
        return "anomaly_dust"
    
    def generate_transactions(self, start_ts: float, duration_hours: int) -> List[Dict]:
        txs = []
        current_ts = start_ts
        end_ts = start_ts + duration_hours * 3600
        
        # Very high frequency (every 10-60 seconds)
        interval = self.rng.integers(10, 60)
        
        while current_ts < end_ts:
            # Tiny amounts
            amount = self.rng.uniform(0.0001, 0.01)
            
            txs.append({
                "tx_hash": hashlib.sha256(f"{self.wallet}_{current_ts}".encode()).hexdigest()[:16],
                "timestamp": current_ts,
                "from_addr": self.wallet,
                "to_addr": self._random_recipient(),
                "amount": round(amount, 7),
                "label": self.label
            })
            
            current_ts += interval + self.rng.integers(-5, 6)
        
        return txs


# Mapping for easy access
BEHAVIOR_CLASSES = {
    "normal": NormalBehavior,
    "whale": WhaleBehavior,
    "anomaly_circular": CircularBehavior,
    "anomaly_bot": BotBehavior,
    "anomaly_burst": BurstBehavior,
    "anomaly_fan_out": FanOutBehavior,
    "anomaly_layering": LayeringBehavior,
    "anomaly_dust": DustBehavior,
}
