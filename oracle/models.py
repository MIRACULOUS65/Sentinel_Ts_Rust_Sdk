"""
Pydantic models for Oracle API request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
import re


class RiskInput(BaseModel):
    """Input model for risk scoring - this interface is FIXED and won't change."""
    wallet: str = Field(..., description="Stellar wallet address (G...)")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score from 0-100")
    reason: str = Field(..., description="Human-readable reason (UI-only, not signed)")
    
    @field_validator('wallet')
    @classmethod
    def validate_wallet_address(cls, v: str) -> str:
        """Validate Stellar wallet address format."""
        if not v.startswith('G'):
            raise ValueError('Wallet address must start with G')
        if len(v) != 56:
            raise ValueError('Wallet address must be 56 characters')
        # Basic alphanumeric check
        if not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Wallet address contains invalid characters')
        return v


class SignedPayload(BaseModel):
    """The payload that gets signed (wallet + risk_score + timestamp)."""
    wallet: str
    risk_score: int
    timestamp: int


class SignedRiskResponse(BaseModel):
    """Response containing the signed risk payload."""
    payload: SignedPayload = Field(..., description="The data that was signed")
    signature: str = Field(..., description="Ed25519 signature (hex)")
    oracle_pubkey: str = Field(..., description="Oracle's public key (hex)")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    oracle_pubkey: str
