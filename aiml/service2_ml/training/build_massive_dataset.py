"""
Massive Stellar Dataset Builder
Creates a large, properly distributed dataset for serious ML training.
Target: 1GB+ dataset with diverse transaction patterns.

Usage:
    python build_massive_dataset.py --transactions 500000 --output massive_stellar.jsonl

This will take 1-2 hours to build a comprehensive dataset.
"""
import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
import time

HORIZON_MAINNET = "https://horizon.stellar.org"


class MassiveDatasetBuilder:
    """Builds a large, diverse dataset from Stellar Mainnet."""
    
    def __init__(self, target_transactions: int = 500000):
        self.target = target_transactions
        self.transactions = []
        self.wallet_stats = defaultdict(lambda: {
            "tx_count": 0, "amounts": [], "recipients": set()
        })
        self.seen_hashes = set()
        
        # Collect accounts to track
        self.high_volume_accounts = []
        self.normal_accounts = []
        self.exchange_accounts = []
        
    async def fetch_recent_accounts(self, client: httpx.AsyncClient, limit: int = 500):
        """Fetch diverse account pool from recent transactions."""
        print("\n📥 Building diverse account pool...")
        accounts = set()
        cursor = None
        
        with tqdm(total=limit, desc="Collecting accounts") as pbar:
            while len(accounts) < limit:
                try:
                    params = {"limit": 200, "order": "desc"}
                    if cursor:
                        params["cursor"] = cursor
                    
                    response = await client.get(
                        f"{HORIZON_MAINNET}/payments",
                        params=params,
                        timeout=30
                    )
                    data = response.json()
                    records = data.get("_embedded", {}).get("records", [])
                    
                    for r in records:
                        if r.get("type") == "payment":
                            if r.get("from"):
                                accounts.add(r["from"])
                            if r.get("to"):
                                accounts.add(r["to"])
                            pbar.update(min(1, limit - len(accounts)))
                    
                    if records:
                        cursor = records[-1].get("paging_token")
                    else:
                        break
                        
                except Exception as e:
                    await asyncio.sleep(1)
                    continue
        
        self.all_accounts = list(accounts)
        print(f"✅ Collected {len(self.all_accounts)} unique accounts")
        return self.all_accounts
    
    async def fetch_account_history(
        self, 
        client: httpx.AsyncClient, 
        account: str, 
        limit: int = 200
    ):
        """Fetch transaction history for a specific account."""
        try:
            response = await client.get(
                f"{HORIZON_MAINNET}/accounts/{account}/payments",
                params={"limit": limit, "order": "desc"},
                timeout=20
            )
            data = response.json()
            return data.get("_embedded", {}).get("records", [])
        except:
            return []
    
    async def fetch_ledger_payments(
        self, 
        client: httpx.AsyncClient,
        cursor: str = None,
        limit: int = 200
    ):
        """Fetch payments from ledger stream."""
        try:
            params = {"limit": limit, "order": "desc"}
            if cursor:
                params["cursor"] = cursor
            
            response = await client.get(
                f"{HORIZON_MAINNET}/payments",
                params=params,
                timeout=30
            )
            data = response.json()
            return data.get("_embedded", {}).get("records", [])
        except:
            return []
    
    def process_record(self, record: dict) -> dict:
        """Convert Horizon record to training format."""
        if record.get("type") != "payment":
            return None
        
        tx_hash = record.get("transaction_hash", "")
        if tx_hash in self.seen_hashes:
            return None
        
        from_addr = record.get("from", "")
        to_addr = record.get("to", "")
        
        if not from_addr or not to_addr:
            return None
        
        self.seen_hashes.add(tx_hash)
        
        try:
            amount = float(record.get("amount", 0))
        except:
            amount = 0
        
        tx = {
            "tx_hash": tx_hash[:16],
            "timestamp": self.parse_timestamp(record.get("created_at", "")),
            "from_addr": from_addr,
            "to_addr": to_addr,
            "amount": amount,
            "asset_type": record.get("asset_type", "native"),
            "label": self.classify_transaction(from_addr, to_addr, amount)
        }
        
        # Update stats
        self.wallet_stats[from_addr]["tx_count"] += 1
        self.wallet_stats[from_addr]["amounts"].append(amount)
        self.wallet_stats[from_addr]["recipients"].add(to_addr)
        
        return tx
    
    def classify_transaction(self, from_addr: str, to_addr: str, amount: float) -> str:
        """Classify transaction for training labels."""
        stats = self.wallet_stats[from_addr]
        
        # Self-transfer
        if from_addr == to_addr:
            return "circular"
        
        # Dust (tiny amounts)
        if amount < 0.01:
            return "dust"
        
        # High volume
        if stats["tx_count"] > 100:
            return "high_volume"
        
        # Fan-out (many recipients)
        if len(stats["recipients"]) > 50:
            return "fan_out"
        
        # Large amount
        if amount > 10000:
            return "whale"
        
        return "normal"
    
    def parse_timestamp(self, iso_string: str) -> float:
        try:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return datetime.now().timestamp()
    
    async def build_dataset(self):
        """Main dataset building loop."""
        print("=" * 80)
        print("🚀 MASSIVE STELLAR DATASET BUILDER")
        print("=" * 80)
        print(f"Target: {self.target:,} transactions")
        print(f"Estimated size: ~{self.target * 200 / 1024 / 1024:.0f} MB")
        print()
        
        start_time = time.time()
        cursor = None
        batch_size = 200
        
        async with httpx.AsyncClient() as client:
            # First, collect diverse accounts
            await self.fetch_recent_accounts(client, limit=1000)
            
            print("\n📥 Fetching transaction history...")
            
            with tqdm(total=self.target, desc="Building dataset") as pbar:
                # Method 1: Fetch from ledger stream
                while len(self.transactions) < self.target * 0.6:  # 60% from stream
                    try:
                        records = await self.fetch_ledger_payments(client, cursor, batch_size)
                        
                        if not records:
                            await asyncio.sleep(1)
                            continue
                        
                        for r in records:
                            tx = self.process_record(r)
                            if tx:
                                self.transactions.append(tx)
                                pbar.update(1)
                                
                                if len(self.transactions) >= self.target * 0.6:
                                    break
                        
                        cursor = records[-1].get("paging_token") if records else cursor
                        
                        # Rate limiting
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        await asyncio.sleep(2)
                        continue
                
                # Method 2: Fetch account histories for diversity
                print("\n📥 Fetching account histories for diversity...")
                random.shuffle(self.all_accounts)
                
                for account in self.all_accounts[:200]:
                    if len(self.transactions) >= self.target:
                        break
                    
                    try:
                        records = await self.fetch_account_history(client, account, 200)
                        
                        for r in records:
                            tx = self.process_record(r)
                            if tx:
                                self.transactions.append(tx)
                                pbar.update(1)
                                
                                if len(self.transactions) >= self.target:
                                    break
                        
                        await asyncio.sleep(0.2)
                        
                    except:
                        continue
        
        elapsed = time.time() - start_time
        print(f"\n✅ Collected {len(self.transactions):,} transactions in {elapsed/60:.1f} minutes")
        
        return self.transactions
    
    def analyze_dataset(self):
        """Print dataset analysis."""
        print("\n" + "=" * 80)
        print("📊 DATASET ANALYSIS")
        print("=" * 80)
        
        # Label distribution
        labels = defaultdict(int)
        for tx in self.transactions:
            labels[tx["label"]] += 1
        
        print("\n📋 Label Distribution:")
        for label, count in sorted(labels.items(), key=lambda x: -x[1]):
            pct = count / len(self.transactions) * 100
            print(f"   • {label}: {count:,} ({pct:.1f}%)")
        
        # Amount distribution
        amounts = [tx["amount"] for tx in self.transactions]
        print(f"\n💰 Amount Statistics:")
        print(f"   • Min: {min(amounts):.4f} XLM")
        print(f"   • Max: {max(amounts):,.2f} XLM")
        print(f"   • Mean: {sum(amounts)/len(amounts):,.2f} XLM")
        
        # Wallet stats
        print(f"\n👛 Wallet Statistics:")
        tx_counts = [s["tx_count"] for s in self.wallet_stats.values()]
        print(f"   • Unique wallets: {len(self.wallet_stats):,}")
        print(f"   • Max tx/wallet: {max(tx_counts):,}")
        print(f"   • Avg tx/wallet: {sum(tx_counts)/len(tx_counts):.1f}")
    
    def save_dataset(self, filepath: str):
        """Save dataset to JSONL file."""
        print(f"\n💾 Saving to {filepath}...")
        
        with open(filepath, 'w') as f:
            for tx in self.transactions:
                f.write(json.dumps(tx) + "\n")
        
        size_mb = Path(filepath).stat().st_size / 1024 / 1024
        print(f"✅ Saved {len(self.transactions):,} transactions ({size_mb:.1f} MB)")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build massive Stellar dataset")
    parser.add_argument("--transactions", type=int, default=500000, help="Target transaction count")
    parser.add_argument("--output", type=str, default="massive_stellar.jsonl", help="Output file")
    args = parser.parse_args()
    
    builder = MassiveDatasetBuilder(target_transactions=args.transactions)
    
    await builder.build_dataset()
    builder.analyze_dataset()
    builder.save_dataset(args.output)
    
    print("\n" + "=" * 80)
    print("✅ DATASET BUILD COMPLETE")
    print("=" * 80)
    print(f"\nTo train the model:")
    print(f"   python -m service4_ml train --dataset {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
