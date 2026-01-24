# Oracle Cryptographic Signing Service

Cryptographic trust bridge between AI risk scores and Soroban smart contracts using Ed25519 signatures.

## 🎯 Purpose

The Oracle service:
- Accepts risk scores from ML engine (or mock data)
- Signs payloads with Ed25519
- Returns cryptographically verifiable signatures
- Enables Soroban smart contracts to trust AI outputs

## 🏗️ Architecture

```
ML Engine → Oracle (Ed25519 Sign) → Soroban Contract (Verify) → Enforcement
```

## 📦 Fixed Input Interface

The Oracle accepts this payload format (WILL NOT CHANGE):

```json
{
  "wallet": "GABCD...",
  "risk_score": 87,
  "reason": "abnormal circular transfers"
}
```

**Today**: Mock data  
**Later**: Real ML output (zero code changes)

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
cd oracle
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Oracle Keypair

```powershell
python crypto.py --generate-keys
```

This creates:
- `keys/oracle_private.key` (keep secret!)
- `keys/oracle_public.key` (embed in Soroban contract)

### 3. Start Oracle Service

```powershell
uvicorn main:app --reload --port 8001
```

Service runs at: `http://localhost:8001`

### 4. Test with Mock Data

```powershell
python test_oracle.py
```

## 📡 API Endpoints

### `POST /sign-risk`

Sign a risk score.

**Request**:
```json
{
  "wallet": "GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
  "risk_score": 87,
  "reason": "abnormal circular transfers"
}
```

**Response**:
```json
{
  "payload": {
    "wallet": "GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
    "risk_score": 87,
    "timestamp": 1737718800
  },
  "signature": "3a7f8b9c...",
  "oracle_pubkey": "ed5f9a2d..."
}
```

### `GET /health`

Health check.

**Response**:
```json
{
  "status": "healthy",
  "service": "sentinel-oracle",
  "oracle_pubkey": "ed5f9a2d..."
}
```

## 🔐 Cryptographic Design

### What Gets Signed

```json
{
  "wallet": "GABCD...",
  "risk_score": 87,
  "timestamp": 1737718800
}
```

### What Does NOT Get Signed

- `reason` field (UI-only, not enforced on-chain)

### Why This Matters

- Smart contract verifies signature ✅
- Timestamp prevents replay attacks ✅
- Oracle cannot be spoofed ✅
- ML output becomes trustworthy on-chain ✅

## 🧪 Testing

### Manual cURL Test

```powershell
curl -X POST http://localhost:8001/sign-risk `
  -H "Content-Type: application/json" `
  -d '{\"wallet\":\"GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR\",\"risk_score\":87,\"reason\":\"test\"}'
```

### Automated Test Suite

```powershell
python test_oracle.py
```

Tests:
- Health check
- Signature generation
- Validation (invalid inputs)
- Multiple risk levels

## 🔑 Key Management

**Private Key**: `keys/oracle_private.key`
- Never commit to git
- Never share
- Never send over network

**Public Key**: `keys/oracle_public.key`
- Embed in Soroban contract
- Return in API responses
- Safe to share

## 📝 File Structure

```
oracle/
├── main.py              # FastAPI service
├── crypto.py            # Ed25519 signing
├── models.py            # Pydantic validation
├── requirements.txt     # Dependencies
├── test_oracle.py       # Test suite
├── README.md            # This file
└── keys/                # Generated keypair
    ├── oracle_private.key
    └── oracle_public.key
```

## 🔗 Integration

### From ML Engine (Future)

```python
import requests

ml_output = {
    "wallet": "GABCD...",
    "risk_score": model.predict(data),
    "reason": model.explain(data)
}

response = requests.post(
    "http://oracle:8001/sign-risk",
    json=ml_output
)

signed = response.json()
# Submit to Soroban contract
```

### From Soroban Contract

The contract will:
1. Receive signed payload
2. Verify Ed25519 signature
3. Check timestamp freshness
4. Enforce risk rules

## 🎯 Next Steps

1. ✅ Oracle service built
2. ⏳ Build Soroban smart contract
3. ⏳ Deploy contract to Stellar testnet
4. ⏳ Submit signed payloads
5. ⏳ Verify on-chain enforcement

## 📚 API Documentation

Interactive docs at: `http://localhost:8001/docs`
