"""
Stellar Transaction Schema
Defines the canonical format for transactions flowing through the ML pipeline.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StellarTransaction(BaseModel):
    """
    A Stellar network transaction for ML processing.
    """
    tx_hash: str = Field(..., description="Unique transaction hash")
    timestamp: float = Field(..., description="Unix timestamp")
    from_addr: str = Field(..., description="Sender wallet address")
    to_addr: str = Field(..., description="Recipient wallet address")
    amount: float = Field(..., ge=0, description="Transaction amount in XLM")
    asset_type: str = Field(default="native", description="Asset type (native=XLM)")
    memo: Optional[str] = Field(default=None, description="Transaction memo")
    
    # Ground truth label (only for synthetic data)
    label: Optional[str] = Field(default=None, description="Behavior label for training")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tx_hash": "abc123...",
                "timestamp": 1706140800.0,
                "from_addr": "GABCD...",
                "to_addr": "GEFGH...",
                "amount": 100.5,
                "asset_type": "native",
                "label": "normal"
            }
        }


class RiskAssertion(BaseModel):
    """
    Sentinel SDK Risk Output Contract.
    This is the ONLY output format the ML engine produces.
    """
    wallet: str = Field(..., description="Wallet address being scored")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    reason: str = Field(..., description="Human-readable reason for the score")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    # Optional: detailed pattern scores (for debugging)
    pattern_scores: Optional[dict] = Field(default=None, description="Individual pattern scores")
    
    class Config:
        json_schema_extra = {
            "example": {
                "wallet": "GABCD...",
                "risk_score": 87,
                "reason": "abnormal circular transfers",
                "timestamp": 1706140800.0
            }
        }
