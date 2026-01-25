"""
Sentinel Coordinator
Orchestrates the full risk pipeline:
1. Fetch Wallet History (Service 1)
2. Analyze Risk (Service 2)
3. Sign & Submit to Chain (Service 3 + Contract)
"""

import sys
import os
import time

# Add paths to import services
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../oracle')))

from service1_horizon.tracker import extract_features
from service2_ml.model import RiskEngine
from crypto import load_keys, sign_payload

# Contract Configuration (V6)
CONTRACT_ID = 'CBH4H6ODNCQZGS5WQPPSGWKTKJKE5XCKFC4DRMTLMYTM2ZS43XK2SS3W'

# Initialize Risk Engine once
ml_engine = RiskEngine()

def run_pipeline(wallet_address):
    print(f"\\n{'='*60}")
    print(f"SENTINEL RISK PIPELINE")
    print(f"Target: {wallet_address}")
    print(f"{'='*60}\\n")
    
    # --- Step 1: Horizon Tracker ---
    print(f"[1] Fetching transaction history (Service 1)...")
    try:
        features = extract_features(wallet_address)
        print(f"    Found {features['tx_count']} transactions")
        print(f"    Avg Amount: {features['avg_amount']}")
        print(f"    Burst Rate: {features['burst_rate']:.4f}")
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return

    # --- Step 2: ML Analysis ---
    print(f"\\n[2] Analyzing behavior (Service 2 - Isolation Forest)...")
    try:
        analysis = ml_engine.analyze_risk(features)
        risk_score = analysis['risk_score']
        reason = analysis['reason']
        print(f"    Risk Score: {risk_score}/100")
        print(f"    Reason: {reason}")
    except Exception as e:
        print(f"❌ Error analyzing risk: {e}")
        return

    # --- Step 3: Oracle Signing ---
    print(f"\\n[3] Signing with Oracle (Service 3)...")
    try:
        signing_key, verify_key = load_keys()
        
        timestamp = int(time.time())
        payload = {
            "wallet": wallet_address,
            "risk_score": int(risk_score),
            "timestamp": timestamp
        }
        
        signature = sign_payload(payload, signing_key)
        print(f"    Signature generated (64 bytes)")
    except Exception as e:
        print(f"❌ Error signing payload: {e}")
        return

    # --- Step 4: Submission (via Node script) ---
    print(f"\\n[4] Submitting to Sentinel Contract...")
    
    # Save payload to json for the JS script to pick up
    # We reuse the same interface as Phase 2
    import json
    oracle_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../oracle/oracle_real_wallet.json'))
    
    output_data = {
        "contract_id": CONTRACT_ID,
        "oracle_pubkey": verify_key.encode().hex(),
        "payload": payload,
        "signature": signature
    }
    
    with open(oracle_output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"    Payload saved to {oracle_output_path}")
    
    # Call the JS submission script
    submit_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../blockchain/contracts/sentinel-sdk/scripts/test_submit_risk.js'))
    
    import subprocess
    try:
        # Use node to run the submission
        # We need to run it from its own directory context usually, or handle paths carefully
        # The script we updated in Phase 3 uses absolute paths now, so it should be robust.
        
        result = subprocess.run(['node', submit_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"    ✅ Submission Successful!")
            # Extract hash from output if possible
            for line in result.stdout.splitlines():
                if "TX Hash:" in line:
                    print(f"    {line.strip()}")
        else:
            print(f"    ❌ Submission Failed!")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error invoking submission script: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <WALLET_ADDRESS>")
        # Default test wallet
        test_wallet = "GBGNKU6A27K5CITQQFIBA4EJZRXHF5PCDFDSL7T6JUTZ3LOONVM3QPXT"
        print(f"Using default test wallet: {test_wallet}")
        run_pipeline(test_wallet)
    else:
        run_pipeline(sys.argv[1])
