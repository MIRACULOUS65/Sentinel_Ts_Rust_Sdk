"""
Synthetic Data Generator
Creates a diverse, balanced dataset for training the anomaly detection model.
"""
import json
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Optional

from .behaviors import (
    BEHAVIOR_CLASSES,
    generate_wallet_address,
    NormalBehavior,
    WhaleBehavior,
    CircularBehavior,
    BotBehavior,
    BurstBehavior,
    FanOutBehavior,
    LayeringBehavior,
    DustBehavior,
)


class SyntheticGenerator:
    """
    Generates synthetic Stellar transaction data with diverse behavior profiles.
    """
    
    def __init__(
        self,
        num_wallets: int = 500,
        duration_hours: int = 48,
        seed: int = 42,
        anomaly_ratio: float = 0.5  # 50% normal, 50% anomalies
    ):
        self.num_wallets = num_wallets
        self.duration_hours = duration_hours
        self.seed = seed
        self.anomaly_ratio = anomaly_ratio
        self.rng = np.random.default_rng(seed)
        
        self.wallets: List[str] = []
        self.wallet_behaviors: Dict[str, str] = {}
        self.transactions: List[Dict] = []
    
    def setup_universe(self):
        """Create wallet universe and assign behaviors."""
        print(f"\n🌐 Creating {self.num_wallets} wallets...")
        
        # Generate all wallet addresses
        self.wallets = [generate_wallet_address(i) for i in range(self.num_wallets)]
        
        # Calculate distribution
        # 50% normal/whale, 50% anomalies (evenly split among 6 types)
        num_normal = int(self.num_wallets * (1 - self.anomaly_ratio) * 0.7)
        num_whale = int(self.num_wallets * (1 - self.anomaly_ratio) * 0.3)
        num_anomaly_per_type = int(self.num_wallets * self.anomaly_ratio / 6)
        
        # Ensure we use all wallets
        distribution = {
            "normal": num_normal,
            "whale": num_whale,
            "anomaly_circular": num_anomaly_per_type,
            "anomaly_bot": num_anomaly_per_type,
            "anomaly_burst": num_anomaly_per_type,
            "anomaly_fan_out": num_anomaly_per_type,
            "anomaly_layering": num_anomaly_per_type,
            "anomaly_dust": num_anomaly_per_type,
        }
        
        # Adjust to match total
        total_assigned = sum(distribution.values())
        if total_assigned < self.num_wallets:
            distribution["normal"] += self.num_wallets - total_assigned
        
        print("\n📊 Wallet Distribution:")
        for behavior, count in distribution.items():
            print(f"   {behavior}: {count}")
        
        # Assign behaviors
        wallet_idx = 0
        for behavior, count in distribution.items():
            for _ in range(count):
                if wallet_idx >= self.num_wallets:
                    break
                self.wallet_behaviors[self.wallets[wallet_idx]] = behavior
                wallet_idx += 1
        
        # Shuffle to mix behaviors
        shuffled_items = list(self.wallet_behaviors.items())
        self.rng.shuffle(shuffled_items)
        self.wallet_behaviors = dict(shuffled_items)
    
    def generate_transactions(self):
        """Generate transactions for all wallets."""
        print(f"\n🔄 Generating transactions for {self.duration_hours} hours...")
        
        start_ts = datetime.now(timezone.utc).timestamp()
        
        for wallet, behavior_name in tqdm(self.wallet_behaviors.items(), desc="Generating"):
            # Get behavior class
            behavior_class = BEHAVIOR_CLASSES[behavior_name]
            
            # Create behavior instance with its own RNG
            behavior = behavior_class(
                wallet=wallet,
                universe=self.wallets,
                rng=np.random.default_rng(self.rng.integers(0, 2**32))
            )
            
            # Generate transactions
            txs = behavior.generate_transactions(start_ts, self.duration_hours)
            self.transactions.extend(txs)
        
        # Sort by timestamp
        self.transactions.sort(key=lambda x: x["timestamp"])
        
        print(f"\n✅ Generated {len(self.transactions):,} transactions")
        
        # Print statistics
        self._print_statistics()
    
    def _print_statistics(self):
        """Print dataset statistics."""
        print("\n📈 Dataset Statistics:")
        
        # Count by label
        label_counts = {}
        for tx in self.transactions:
            label = tx.get("label", "unknown")
            label_counts[label] = label_counts.get(label, 0) + 1
        
        for label, count in sorted(label_counts.items()):
            pct = count / len(self.transactions) * 100
            print(f"   {label}: {count:,} ({pct:.1f}%)")
        
        # Amount statistics
        amounts = [tx["amount"] for tx in self.transactions]
        print(f"\n💰 Amount Statistics:")
        print(f"   Min: {min(amounts):.4f}")
        print(f"   Max: {max(amounts):.2f}")
        print(f"   Mean: {np.mean(amounts):.2f}")
        print(f"   Median: {np.median(amounts):.2f}")
    
    def save(self, output_path: str = "synthetic_dataset.jsonl"):
        """Save transactions to JSON Lines file."""
        print(f"\n💾 Saving to {output_path}...")
        
        with open(output_path, 'w') as f:
            for tx in self.transactions:
                f.write(json.dumps(tx) + "\n")
        
        print(f"✅ Saved {len(self.transactions):,} transactions")
    
    def generate(self, output_path: str = "synthetic_dataset.jsonl"):
        """Full generation pipeline."""
        print("=" * 60)
        print("🚀 SYNTHETIC DATA GENERATOR")
        print("=" * 60)
        
        self.setup_universe()
        self.generate_transactions()
        self.save(output_path)
        
        print("\n" + "=" * 60)
        print("✅ GENERATION COMPLETE")
        print("=" * 60)
        
        return self.transactions


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic Stellar transactions")
    parser.add_argument("--wallets", type=int, default=500, help="Number of wallets")
    parser.add_argument("--hours", type=int, default=48, help="Duration in hours")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default="synthetic_dataset.jsonl", help="Output file")
    parser.add_argument("--anomaly-ratio", type=float, default=0.5, help="Ratio of anomalous wallets")
    
    args = parser.parse_args()
    
    generator = SyntheticGenerator(
        num_wallets=args.wallets,
        duration_hours=args.hours,
        seed=args.seed,
        anomaly_ratio=args.anomaly_ratio
    )
    
    generator.generate(args.output)


if __name__ == "__main__":
    main()
