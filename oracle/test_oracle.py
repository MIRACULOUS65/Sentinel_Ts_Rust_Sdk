"""
Test script for Oracle cryptographic signing service.

Tests the Oracle API with mock ML data to verify:
- Keypair generation
- Signature creation
- API endpoint functionality
"""

import requests
import json

# Oracle API URL
ORACLE_URL = "http://localhost:8001"

# Mock ML outputs (simulating what the real ML engine will send)
MOCK_RISK_PAYLOADS = [
    {
        "wallet": "GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
        "risk_score": 87,
        "reason": "abnormal circular transfers"
    },
    {
        "wallet": "GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
        "risk_score": 92,
        "reason": "high-frequency suspicious activity"
    },
    {
        "wallet": "GDJB7LPPQCWBKBAMZZXJYXEVYUMWPBU43KW3P3UFEETMESKUZKIOOMAR",
        "risk_score": 15,
        "reason": "normal behavior"
    },
    {
        "wallet": "GBTORQK3ZR3RPJF4WTTSH5KVDOAZ4BJI7PD2ECLSBDNHRG4ICNC4JJZV",
        "risk_score": 65,
        "reason": "moderate risk - elevated transaction volume"
    }
]


def test_health_check():
    """Test the health check endpoint."""
    print("\n🔍 Testing health check...")
    try:
        response = requests.get(f"{ORACLE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Status: {data['status']}")
        print(f"   Service: {data['service']}")
        print(f"   Public Key: {data['oracle_pubkey'][:16]}...")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_sign_risk(payload):
    """Test the /sign-risk endpoint with a payload."""
    print(f"\n🔐 Testing signature for wallet: {payload['wallet'][:12]}...")
    print(f"   Risk Score: {payload['risk_score']}")
    print(f"   Reason: {payload['reason']}")
    
    try:
        response = requests.post(
            f"{ORACLE_URL}/sign-risk",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Signature generated successfully")
        print(f"   Wallet: {data['payload']['wallet'][:12]}...")
        print(f"   Risk Score: {data['payload']['risk_score']}")
        print(f"   Timestamp: {data['payload']['timestamp']}")
        print(f"   Signature: {data['signature'][:32]}...")
        print(f"   Oracle Pubkey: {data['oracle_pubkey'][:32]}...")
        
        return data
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_invalid_payload():
    """Test with invalid payloads to verify validation."""
    print("\n🧪 Testing validation with invalid payloads...")
    
    invalid_payloads = [
        {
            "wallet": "INVALID",
            "risk_score": 50,
            "reason": "test"
        },
        {
            "wallet": "GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
            "risk_score": 150,  # Out of range
            "reason": "test"
        },
        {
            "wallet": "GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
            "risk_score": -10,  # Negative
            "reason": "test"
        }
    ]
    
    for payload in invalid_payloads:
        try:
            response = requests.post(
                f"{ORACLE_URL}/sign-risk",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 422:
                print(f"✅ Correctly rejected invalid payload: {payload}")
            else:
                print(f"❌ Should have rejected: {payload}")
        except Exception as e:
            print(f"⚠️  Error testing invalid payload: {e}")


def main():
    """Run all tests."""
    print("="*60)
    print("🧪 ORACLE CRYPTOGRAPHIC SIGNING SERVICE - TEST SUITE")
    print("="*60)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Oracle service is not running!")
        print("   Start it with: uvicorn main:app --reload --port 8001")
        return
    
    # Test valid payloads
    print("\n" + "="*60)
    print("📝 Testing with mock ML payloads")
    print("="*60)
    
    signed_payloads = []
    for payload in MOCK_RISK_PAYLOADS:
        result = test_sign_risk(payload)
        if result:
            signed_payloads.append(result)
    
    # Test invalid payloads
    print("\n" + "="*60)
    print("🛡️  Testing validation")
    print("="*60)
    test_invalid_payload()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Successfully signed {len(signed_payloads)}/{len(MOCK_RISK_PAYLOADS)} payloads")
    
    if signed_payloads:
        print("\n🎯 Next Steps:")
        print("   1. Deploy Soroban smart contract with this public key")
        print("   2. Submit signed payloads to contract")
        print("   3. Verify on-chain enforcement")
        print(f"\n   Public Key: {signed_payloads[0]['oracle_pubkey']}")


if __name__ == "__main__":
    main()
