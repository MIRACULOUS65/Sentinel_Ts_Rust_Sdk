# Quick Test - Verify API is Working

import requests

API_URL = "http://localhost:8001"  # Change to your Render URL after deployment

print("Testing Stellar Horizon Data Fetcher API...\n")

# Test 1: Health Check
print("1. Health Check:")
response = requests.get(f"{API_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Service: {response.json()['service']}\n")

# Test 2: Wallet Frequencies with Explorer URLs
print("2. Wallet Frequencies (with Explorer URLs):")
response = requests.get(f"{API_URL}/explorer/wallets/frequency")
data = response.json()
print(f"   Total Wallets: {data['total_wallets']}")
print(f"   Network: {data['network']}")

if data['total_wallets'] > 0:
    wallet = data['wallets'][0]
    print(f"\n   Top Wallet:")
    print(f"   - Address: {wallet['wallet'][:40]}...")
    print(f"   - TX/Hour: {wallet['tx_per_hour']}")
    print(f"   - Risk: {wallet['risk_level']}")
    print(f"   - Explorer: {wallet['explorer_url']}")

print("\n✅ API is working! Ready for frontend integration.")
print(f"\n📖 See README.md for Next.js/Node.js integration examples")
