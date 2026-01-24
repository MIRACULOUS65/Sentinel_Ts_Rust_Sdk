"""
Direct Oracle Crypto Test - No Service Required
Tests Oracle signing functionality without running the web service
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'oracle'))

from crypto import load_keys, sign_payload
import json
import time

def main():
    print("="*60)
    print("ORACLE SIGNING TEST - Direct Crypto Module")
    print("="*60)
    
    # Load Oracle keys
    print("\n[1] Loading Oracle keypair...")
    try:
        signing_key, verify_key = load_keys()
        oracle_pubkey = verify_key.encode().hex()
        print(f"  Success! Oracle public key: {oracle_pubkey}")
    except Exception as e:
        print(f"  Error: {e}")
        return
    
    # Create test payload
    test_wallet = "GBTEST1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    test_risk_score = 87
    timestamp = int(time.time())
    
    payload = {
        "wallet": test_wallet,
        "risk_score": test_risk_score,
        "timestamp": timestamp
    }
    
    print(f"\n[2] Payload to sign:")
    print(f"  {json.dumps(payload, indent=2)}")
    
    # Sign payload
    print(f"\n[3] Signing payload with Oracle private key...")
    signature_hex = sign_payload(payload, signing_key)
    print(f"  Signature: {signature_hex[:32]}...{signature_hex[-32:]}")
    print(f"  Length: {len(signature_hex)} chars ({len(signature_hex)//2} bytes)")
    
    # Output for contract submission
    print(f"\n[4] Contract Submission Data:")
    print(f"  Contract ID: CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU")
    print(f"  Oracle Pubkey: {oracle_pubkey}")
    print(f"  Signature: {signature_hex}")
    print(f"  Payload: {json.dumps(payload)}")
    
    print("\n=" * 60)
    print("SUCCESS - Oracle Signing Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Initialize contract with Oracle public key")
    print("2. Submit this signed payload to contract")
    print("3. Contract will verify signature using ed25519_verify()")
    
    # Save to file for easy access
    output = {
        "oracle_pubkey": oracle_pubkey,
        "payload": payload,
        "signature": signature_hex,
        "contract_id": "CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU"
    }
    
    output_file = "oracle_signed_payload.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    main()
