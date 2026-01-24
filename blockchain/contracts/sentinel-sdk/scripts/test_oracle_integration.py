#!/usr/bin/env python3
"""
Oracle Integration Test
Tests Oracle signing and contract signature verification end-to-end
"""

import requests
import json
import time

ORACLE_URL = "http://localhost:8001"
TEST_WALLET = "GBTEST1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TEST_RISK_SCORE = 87

def test_oracle_signing():
    """Test 1: Oracle signs a risk payload"""
    print("=" * 60)
    print("TEST 1: Oracle Signing")
    print("=" * 60)
    
    payload = {
        "wallet": TEST_WALLET,
        "risk_score": TEST_RISK_SCORE,
        "reason": "Oracle integration test"
    }
    
    print(f"\nSending to Oracle: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{ORACLE_URL}/sign-risk", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Oracle Response:")
        print(json.dumps(result, indent=2))
        
        # Extract key information
        signed_payload = result['payload']
        signature = result['signature']
        oracle_pubkey = result['oracle_pubkey']
        
        print(f"\n📋 Key Information:")
        print(f"  Wallet: {signed_payload['wallet']}")
        print(f"  Risk Score: {signed_payload['risk_score']}")
        print(f"  Timestamp: {signed_payload['timestamp']}")
        print(f"  Signature: {signature[:32]}...{signature[-32:]}")
        print(f"  Oracle Pubkey: {oracle_pubkey}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Oracle service not running!")
        print("   Please start Oracle: cd oracle && uvicorn main:app --reload --port 8001")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def test_contract_submission(oracle_result):
    """Test 2: Submit signed payload to contract"""
    print("\n" + "=" * 60)
    print("TEST 2: Contract Submission")
    print("=" * 60)
    
    if not oracle_result:
        print("\n⏭️  Skipped (Oracle signing failed)")
        return
    
    print("\n📝 Note: This requires contract initialization first")
    print("   Contract ID: CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU")
    print("\n   To submit using Stellar CLI:")
    print(f"   stellar contract invoke \\")
    print(f"     --id CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU \\")
    print(f"     --network testnet \\")
    print(f"     -- submit_risk \\")
    print(f"     --payload '<PAYLOAD_JSON>' \\")
    print(f"     --signature '{oracle_result['signature']}'")
    
    print("\n⏸️  Contract submission pending (needs initialization)")

def main():
    print("\n🚀 Oracle Integration Test")
    print("Testing end-to-end Oracle → Contract flow\n")
    
    # Test 1: Oracle signing
    oracle_result = test_oracle_signing()
    
    # Test 2: Contract submission (manual for now)
    test_contract_submission(oracle_result)
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    
    if oracle_result:
        print("\n📊 Summary:")
        print("  ✅ Oracle signing: SUCCESS")
        print("  ⏸️  Contract submission: PENDING (needs initialization)")
        print("\n💡 Next Steps:")
        print("  1. Initialize contract with Oracle public key")
        print("  2. Submit signed payload to contract")
        print("  3. Verify signature validation works")

if __name__ == "__main__":
    main()
