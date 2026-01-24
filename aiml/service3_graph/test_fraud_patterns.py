import requests
import time
import random

BASE_URL = "http://localhost:8009"

def inject_tx(from_w, to_w, amount):
    try:
        requests.post(f"{BASE_URL}/debug/inject", json={
            "from_w": from_w,
            "to_w": to_w,
            "amount": amount
        })
        # print(f"Injected: {from_w[:4]} -> {to_w[:4]} (${amount})")
    except Exception as e:
        print(f"Failed to inject: {e}")

def run_test():
    print("🚀 Starting Fraud Simulation...")
    
    # 1. Simulate Money Laundering Ring (A -> B -> C -> A)
    # High amounts + Cycle = High Risk
    print("  Injecting Cyber-Criminal Ring (Cycle)...")
    ring = [
        "CRIMINAL_MASTER_WALLET_001", 
        "MULE_ACCOUNT_ALPHA_002", 
        "LAYER_ACCOUNT_BETA_003"
    ]
    
    # Loop it 5 times rapidly
    for _ in range(5):
        inject_tx(ring[0], ring[1], 5000)
        inject_tx(ring[1], ring[2], 4800)
        inject_tx(ring[2], ring[0], 4500)
        time.sleep(0.1)

    # 2. Simulate Burst Attack (Fan-out)
    # High out-degree = High Risk
    print("  Injecting Burst Attack (Fan-out)...")
    attacker = "BURST_ATTACKER_WALLET_999"
    for i in range(15):
        victim = f"VICTIM_WALLET_{i:03d}"
        inject_tx(attacker, victim, 0.0001)
        time.sleep(0.05)
        
    print("✅ Injection Complete.")
    print("⏳ Waiting for graph update...")
    time.sleep(2)
    
    # 3. Get Visualization
    print("📸 Downloading Visualization...")
    r = requests.get(f"{BASE_URL}/graph/visualize?limit=50")
    if r.status_code == 200:
        with open("fraud_test_result.png", "wb") as f:
            f.write(r.content)
        print("✅ SUCCESS: Saved 'fraud_test_result.png'")
        print("   -> Open this image to see RED nodes (High Risk)!")
    else:
        print(f"❌ Failed to get image: {r.status_code}")

if __name__ == "__main__":
    run_test()
