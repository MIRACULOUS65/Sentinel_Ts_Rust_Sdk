"""
Update Risk Score for Demo
Signs a new risk payload with the specified score and saves it to oracle_real_wallet.json
"""

import sys
import os
import json
import time

# Add parent directory to path to import crypto module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../oracle')))
# Add current directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from oracle.crypto import load_keys, sign_payload, canonical_json
except ImportError:
    # Try alternate path structure if running from different cwd
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../oracle')))
    from crypto import load_keys, sign_payload, canonical_json

def update_risk(score):
    print(f"Updating risk score to: {score}")
    
    # Load Oracle keys
    signing_key, verify_key = load_keys()
    oracle_pubkey = verify_key.encode().hex()
    
    # Create payload
    real_wallet = "GBGNKU6A27K5CITQQFIBA4EJZRXHF5PCDFDSL7T6JUTZ3LOONVM3QPXT"
    timestamp = int(time.time())
    
    payload = {
        "wallet": real_wallet,
        "risk_score": int(score),
        "timestamp": timestamp
    }
    
    # Sign
    signature_hex = sign_payload(payload, signing_key)
    
    # Canonical JSON for verification
    canonical = canonical_json(payload).decode('utf-8')

    # Save output for JS to pick up
    output = {
        "contract_id": "CBH4H6ODNCQZGS5WQPPSGWKTKJKE5XCKFC4DRMTLMYTM2ZS43XK2SS3W", # V6
        "oracle_pubkey": oracle_pubkey,
        "payload": payload,
        "canonical_json": canonical,
        "signature": signature_hex
    }
    
    # Save to the specific location our scripts look for
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../oracle/oracle_real_wallet.json'))
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Risk updated! Payload saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_risk.py <SCORE>")
        sys.exit(1)
    
    score = sys.argv[1]
    update_risk(score)
