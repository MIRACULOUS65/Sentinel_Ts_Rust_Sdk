"""
Sentinel Service 1: Horizon Tracker
Fetches transaction history for a wallet and extracts behavioral features.
"""

from stellar_sdk import Server
from statistics import mean, stdev
import datetime

# Horizon Testnet Server
HORIZON_URL = "https://horizon-testnet.stellar.org"
server = Server(HORIZON_URL)

def fetch_wallet_history(wallet_address, limit=50):
    """
    Fetch last N transactions for a wallet.
    """
    try:
        transactions = server.transactions().for_account(wallet_address).limit(limit).order(desc=True).call()
        return transactions['_embedded']['records']
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

def extract_features(wallet_address):
    """
    Extract behavioral features from transaction history.
    Values are mocked if not enough history exists (for demo purposes).
    """
    history = fetch_wallet_history(wallet_address)
    
    # Defaults
    features = {
        "wallet": wallet_address,
        "tx_count": len(history),
        "avg_amount": 0.0,
        "burst_rate": 0.0,
        "unique_interactions": 0,
        "age_days": 0
    }
    
    if not history:
        return features

    # Extract data
    timestamps = []
    
    # Note: Analyzing amounts requires diving into operations, 
    # for this demo we'll use simplified heuristics based on Tx metadata
    
    for tx in history:
        # Parse timestamp
        dt = datetime.datetime.strptime(tx['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        timestamps.append(dt.timestamp())
        
    # Calculate features
    if len(timestamps) > 1:
        # Burst rate: inverse of avg time between txs
        intervals = [timestamps[i] - timestamps[i+1] for i in range(len(timestamps)-1)]
        avg_interval = mean(intervals) if intervals else 1
        features["burst_rate"] = 1.0 / (avg_interval + 1) # Avoid div by zero
        
        # Age
        features["age_days"] = (timestamps[0] - timestamps[-1]) / 86400
        
    features["unique_interactions"] = len(set(tx['source_account'] for tx in history))

    return features

if __name__ == "__main__":
    # Test with a wallet
    test_wallet = "GBGNKU6A27K5CITQQFIBA4EJZRXHF5PCDFDSL7T6JUTZ3LOONVM3QPXT"
    print(extract_features(test_wallet))
