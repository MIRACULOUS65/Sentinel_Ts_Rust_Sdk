"""
Enhanced ML Training with Real Stellar Data
Fetches real transactions from Stellar Mainnet to train the model on actual patterns.
"""
import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

HORIZON_MAINNET = "https://horizon.stellar.org"
HORIZON_TESTNET = "https://horizon-testnet.stellar.org"


async def fetch_real_transactions(
    num_transactions: int = 10000,
    use_mainnet: bool = True
) -> list:
    """
    Fetch real transactions from Stellar network.
    """
    horizon_url = HORIZON_MAINNET if use_mainnet else HORIZON_TESTNET
    network_name = "MAINNET" if use_mainnet else "TESTNET"
    
    print(f"\n🌐 Fetching real transactions from Stellar {network_name}...")
    print(f"   Target: {num_transactions} transactions")
    
    transactions = []
    cursor = None
    
    async with httpx.AsyncClient() as client:
        with tqdm(total=num_transactions, desc="Fetching") as pbar:
            while len(transactions) < num_transactions:
                try:
                    params = {"limit": 200, "order": "desc"}
                    if cursor:
                        params["cursor"] = cursor
                    
                    response = await client.get(
                        f"{horizon_url}/payments",
                        params=params,
                        timeout=30
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    records = data.get("_embedded", {}).get("records", [])
                    
                    if not records:
                        break
                    
                    for record in records:
                        if record.get("type") == "payment":
                            tx = {
                                "tx_hash": record.get("transaction_hash", "")[:16],
                                "timestamp": parse_timestamp(record.get("created_at", "")),
                                "from_addr": record.get("from", ""),
                                "to_addr": record.get("to", ""),
                                "amount": float(record.get("amount", 0)),
                                "asset_type": record.get("asset_type", "native"),
                                "label": "real_data"  # Not synthetic
                            }
                            
                            if tx["from_addr"] and tx["to_addr"]:
                                transactions.append(tx)
                                pbar.update(1)
                                
                                if len(transactions) >= num_transactions:
                                    break
                    
                    cursor = records[-1].get("paging_token") if records else None
                    
                except Exception as e:
                    print(f"\n⚠️ Error: {e}")
                    await asyncio.sleep(2)
                    continue
    
    print(f"\n✅ Fetched {len(transactions)} real transactions")
    return transactions


def parse_timestamp(iso_string: str) -> float:
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.timestamp()
    except:
        return datetime.now().timestamp()


def analyze_real_data(transactions: list):
    """Analyze patterns in real transaction data."""
    print("\n📊 Analyzing real transaction patterns...")
    
    wallet_stats = defaultdict(lambda: {
        "tx_count": 0,
        "total_amount": 0,
        "recipients": set(),
        "amounts": [],
        "intervals": []
    })
    
    last_tx_time = {}
    
    for tx in transactions:
        wallet = tx["from_addr"]
        stats = wallet_stats[wallet]
        
        stats["tx_count"] += 1
        stats["total_amount"] += tx["amount"]
        stats["recipients"].add(tx["to_addr"])
        stats["amounts"].append(tx["amount"])
        
        if wallet in last_tx_time:
            interval = tx["timestamp"] - last_tx_time[wallet]
            if 0 < interval < 86400:  # Within 24 hours
                stats["intervals"].append(interval)
        
        last_tx_time[wallet] = tx["timestamp"]
    
    # Print analysis
    tx_counts = [s["tx_count"] for s in wallet_stats.values()]
    amounts = [tx["amount"] for tx in transactions]
    
    print(f"\n   📈 Wallet Statistics:")
    print(f"      • Unique wallets: {len(wallet_stats)}")
    print(f"      • Tx per wallet: min={min(tx_counts)}, max={max(tx_counts)}, avg={sum(tx_counts)/len(tx_counts):.1f}")
    
    print(f"\n   💰 Amount Statistics:")
    print(f"      • Min: {min(amounts):.4f}")
    print(f"      • Max: {max(amounts):.2f}")
    print(f"      • Mean: {sum(amounts)/len(amounts):.2f}")
    
    # Identify patterns
    bot_wallets = [w for w, s in wallet_stats.items() if s["tx_count"] > 50 and len(s["recipients"]) < 5]
    dust_wallets = [w for w, s in wallet_stats.items() if s["amounts"] and max(s["amounts"]) < 1]
    high_value = [w for w, s in wallet_stats.items() if s["total_amount"] > 10000]
    
    print(f"\n   🎯 Pattern Detection:")
    print(f"      • Potential bots (>50 tx, <5 recipients): {len(bot_wallets)}")
    print(f"      • Dust patterns (max <1 XLM): {len(dust_wallets)}")
    print(f"      • High value wallets (>10K XLM): {len(high_value)}")
    
    return wallet_stats


def save_real_dataset(transactions: list, filepath: str = "real_stellar_data.jsonl"):
    """Save fetched transactions to file."""
    print(f"\n💾 Saving to {filepath}...")
    
    with open(filepath, 'w') as f:
        for tx in transactions:
            # Remove set objects for JSON serialization
            tx_clean = {k: v for k, v in tx.items()}
            f.write(json.dumps(tx_clean) + "\n")
    
    print(f"✅ Saved {len(transactions)} transactions")


async def main():
    print("=" * 70)
    print("🚀 REAL STELLAR DATA FETCHER")
    print("=" * 70)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5000, help="Number of transactions")
    parser.add_argument("--mainnet", action="store_true", help="Use mainnet (default: testnet)")
    parser.add_argument("--output", type=str, default="real_stellar_data.jsonl")
    args = parser.parse_args()
    
    transactions = await fetch_real_transactions(
        num_transactions=args.count,
        use_mainnet=args.mainnet
    )
    
    if transactions:
        analyze_real_data(transactions)
        save_real_dataset(transactions, args.output)
    
    print("\n✅ Done! Now train with:")
    print(f"   python -m service4_ml train --dataset {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
