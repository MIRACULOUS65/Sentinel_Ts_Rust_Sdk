"""
Direct Oracle Crypto Test
Tests Oracle signing functionality
"""

from crypto import load_keys, sign_payload, canonical_json
import json
import time

def main():
    print("="*60)
    print("ORACLE SIGNING TEST")
    print("="*60)
    
    # Load Oracle keys
    print("\n[1] Loading Oracle keypair...")
    signing_key, verify_key = load_keys()
    oracle_pubkey = verify_key.encode().hex()
    print(f"  Oracle public key: {oracle_pubkey}")
    
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
    
    # Show canonical JSON
    canonical = canonical_json(payload).decode('utf-8')
    print(f"\n[3] Canonical JSON (what gets signed):")
    print(f"  {canonical}")
    
    # Sign payload
    print(f"\n[4] Signing payload...")
    signature_hex = sign_payload(payload, signing_key)
    print(f"  Signature: {signature_hex}")
    print(f"  Length: {len(signature_hex)//2} bytes")
    
   # Output for contract
    print(f"\n[5] For Contract Submission:")
    print(f"  Contract: CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU")
    print(f"  Oracle Key: {oracle_pubkey}")
    print(f"  Wallet: {test_wallet}")
    print(f"  Risk Score: {test_risk_score}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Signature: {signature_hex}")
    
    # Save output
    output = {
        "contract_id": "CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU",
        "oracle_pubkey": oracle_pubkey,
        "payload": payload,
        "canonical_json": canonical,
        "signature": signature_hex
    }
    
    with open("oracle_test_output.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[6] Output saved to: oracle_test_output.json")
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)

if __name__ == "__main__":
    main()
