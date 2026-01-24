"""
Oracle Cryptographic Signing Service

This service acts as a trust bridge between AI risk scores and Soroban smart contracts.
It accepts risk scores (from ML or mock data) and signs them with Ed25519.

Key Design Principles:
- Fixed input interface: {wallet, risk_score, reason}
- Stateless operation
- Ed25519 signatures
- Timestamp for replay protection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from models import RiskInput, SignedRiskResponse, SignedPayload, HealthResponse
from crypto import load_keys, sign_payload

app = FastAPI(
    title="Sentinel Oracle Service",
    description="Cryptographic signing service for AI risk scores",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Oracle keypair on startup
try:
    signing_key, verify_key = load_keys()
    ORACLE_PUBLIC_KEY = verify_key.encode().hex()
    print(f"✅ Oracle service initialized")
    print(f"🔑 Public Key: {ORACLE_PUBLIC_KEY}")
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print(f"🔧 Run: python crypto.py --generate-keys")
    signing_key = None
    verify_key = None
    ORACLE_PUBLIC_KEY = None


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    if not ORACLE_PUBLIC_KEY:
        raise HTTPException(
            status_code=503,
            detail="Oracle not initialized. Generate keypair first."
        )
    
    return HealthResponse(
        status="healthy",
        service="oracle",
        oracle_pubkey=ORACLE_PUBLIC_KEY
    )


@app.post("/sign-risk", response_model=SignedRiskResponse)
async def sign_risk(risk_input: RiskInput):
    """
    Sign a risk score with Ed25519.
    
    This endpoint accepts risk scores from the ML engine (or mock data)
    and returns a cryptographically signed payload for Soroban verification.
    
    The 'reason' field is NOT included in the signature (UI-only).
    """
    if not signing_key:
        raise HTTPException(
            status_code=503,
            detail="Oracle not initialized. Generate keypair first."
        )
    
    # Add timestamp (Unix timestamp in seconds)
    current_timestamp = int(time.time())
    
    # Create the payload that will be signed
    # NOTE: 'reason' is intentionally excluded from signature
    payload_dict = {
        "wallet": risk_input.wallet,
        "risk_score": risk_input.risk_score,
        "timestamp": current_timestamp
    }
    
    # Sign the payload
    signature = sign_payload(payload_dict, signing_key)
    
    # Return signed response
    return SignedRiskResponse(
        payload=SignedPayload(**payload_dict),
        signature=signature,
        oracle_pubkey=ORACLE_PUBLIC_KEY
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint."""
    if not ORACLE_PUBLIC_KEY:
        raise HTTPException(
            status_code=503,
            detail="Oracle not initialized"
        )
    
    return HealthResponse(
        status="healthy",
        service="sentinel-oracle",
        oracle_pubkey=ORACLE_PUBLIC_KEY
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
