"""
Sign payload with real wallet address
"""

from crypto import load_keys, sign_payload, canonical_json
import json
import time

def main():
    print("="*60)
    print("ORACLE SIGNING - Real Wallet Address")
    print("="*60)
    
    # Load Oracle keys
    print("\n[1] Loading Oracle keypair...")
    signing_key, verify_key = load_keys()
    oracle_pubkey = verify_key.encode().hex()
    print(f"  Oracle public key: {oracle_pubkey}")
    
    # Create payload with real wallet
    real_wallet = "GBGNKU6A27K5CITQQFIBA4EJZRXHF5PCDFDSL7T6JUTZ3LOONVM3QPXT"
    risk_score = 87
    timestamp = int(time.time())
    
    payload = {
        "wallet": real_wallet,
        "risk_score": risk_score,
        "timestamp": timestamp
    }
    
    print(f"\n[2] Payload:")
    print(f"  Wallet: {real_wallet}")
    print(f"  Risk Score: {risk_score}")
    print(f"  Timestamp: {timestamp}")
    
    # Canonical JSON
    canonical = canonical_json(payload).decode('utf-8')
    print(f"\n[3] Canonical JSON:")
    print(f"  {canonical}")
    
    # Sign
    print(f"\n[4] Signing...")
    signature_hex = sign_payload(payload, signing_key)
    print(f"  Signature: {signature_hex}")
    
    # Save
    output = {
        "contract_id": "CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU",
        "oracle_pubkey": oracle_pubkey,
        "payload": payload,
        "canonical_json": canonical,
        "signature": signature_hex
    }
    
    with open("oracle_real_wallet.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[5] Saved to: oracle_real_wallet.json")
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)

if __name__ == "__main__":
    main()
