"""
Stellar AI Risk Engine - Service 1: Horizon Data Fetcher
Fetches transaction data from Stellar Horizon API with caching and frequency tracking
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
HORIZON_API_URL = os.getenv("HORIZON_API_URL", "https://horizon-testnet.stellar.org")
CACHE_TTL_SECONDS = 10
MAX_RETRIES = 3
RETRY_DELAY = 1

# Initialize FastAPI app
app = FastAPI(
    title="Stellar Horizon Data Fetcher",
    description="Fetches and caches Stellar transaction data with frequency tracking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache
cache = {}
cache_timestamps = {}

# Transaction frequency tracker
wallet_tx_frequency = defaultdict(lambda: {"count": 0, "last_updated": datetime.utcnow()})


# Pydantic models
class Operation(BaseModel):
    type: str
    from_account: Optional[str] = None
    to: Optional[str] = None
    amount: Optional[str] = None
    asset_type: Optional[str] = None


class Transaction(BaseModel):
    id: str
    source_account: str
    created_at: str
    operations: List[Operation]


class TransactionResponse(BaseModel):
    transactions: List[Transaction]
    count: int


class WalletFrequency(BaseModel):
    wallet: str
    tx_count: int
    tx_per_hour: float
    last_updated: str


class WalletFrequencyResponse(BaseModel):
    wallets: List[WalletFrequency]
    total_wallets: int
    timestamp: str


# Enhanced models with Stellar Expert URLs
class TransactionWithLinks(BaseModel):
    id: str
    source_account: str
    created_at: str
    operations: List[Operation]
    explorer_url: str
    account_url: str


class TransactionResponseWithLinks(BaseModel):
    transactions: List[TransactionWithLinks]
    count: int
    network: str


class WalletFrequencyWithLinks(BaseModel):
    wallet: str
    tx_count: int
    tx_per_hour: float
    last_updated: str
    explorer_url: str
    risk_level: str


class WalletFrequencyResponseWithLinks(BaseModel):
    wallets: List[WalletFrequencyWithLinks]
    total_wallets: int
    timestamp: str
    network: str


# Helper functions
def get_cache_key(endpoint: str, params: dict) -> str:
    """Generate cache key from endpoint and parameters"""
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"{endpoint}?{param_str}"


def is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid"""
    if cache_key not in cache_timestamps:
        return False
    age = (datetime.utcnow() - cache_timestamps[cache_key]).total_seconds()
    return age < CACHE_TTL_SECONDS


async def fetch_from_horizon(endpoint: str, params: dict = None) -> dict:
    """Fetch data from Horizon API with retry logic"""
    url = f"{HORIZON_API_URL}{endpoint}"
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params or {})
                
                if response.status_code == 429:
                    # Rate limited
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(status_code=500, detail=f"Horizon API error: {str(e)}")
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
    
    raise HTTPException(status_code=500, detail="Max retries exceeded")


def parse_operations(tx_data: dict) -> List[Operation]:
    """Parse operations from transaction data"""
    operations = []
    
    # Fetch operations from embedded data if available
    if "_embedded" in tx_data and "operations" in tx_data["_embedded"]:
        for op in tx_data["_embedded"]["operations"]:
            operations.append(Operation(
                type=op.get("type", "unknown"),
                from_account=op.get("from", op.get("source_account")),
                to=op.get("to"),
                amount=op.get("amount"),
                asset_type=op.get("asset_type")
            ))
    
    return operations


def update_wallet_frequency(wallet: str):
    """Update transaction frequency for a wallet"""
    now = datetime.utcnow()
    wallet_tx_frequency[wallet]["count"] += 1
    wallet_tx_frequency[wallet]["last_updated"] = now


def calculate_tx_per_hour(wallet: str) -> float:
    """Calculate transactions per hour for a wallet"""
    data = wallet_tx_frequency[wallet]
    time_diff = (datetime.utcnow() - data["last_updated"]).total_seconds() / 3600
    
    if time_diff < 0.01:  # Less than ~36 seconds
        time_diff = 0.01  # Avoid division by very small numbers
    
    return round(data["count"] / max(time_diff, 1.0), 2)


def get_network_type() -> str:
    """Determine if using testnet or mainnet"""
    if "testnet" in HORIZON_API_URL.lower():
        return "testnet"
    return "public"


def get_stellar_expert_url(item_type: str, item_id: str) -> str:
    """
    Generate Stellar Expert URL for transactions or accounts
    
    Args:
        item_type: 'tx' for transaction or 'account' for wallet
        item_id: Transaction hash or account address
    """
    network = get_network_type()
    return f"https://stellar.expert/explorer/{network}/{item_type}/{item_id}"


def get_risk_level(tx_per_hour: float) -> str:
    """Determine risk level based on transaction frequency"""
    if tx_per_hour > 50:
        return "high"
    elif tx_per_hour > 20:
        return "elevated"
    elif tx_per_hour > 10:
        return "medium"
    else:
        return "normal"


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "service": "horizon-data-fetcher",
        "horizon_url": HORIZON_API_URL,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/transactions/recent", response_model=TransactionResponse)
async def get_recent_transactions(
    limit: int = Query(default=200, ge=1, le=200, description="Number of transactions to fetch")
):
    """
    Fetch recent network transactions from Stellar Horizon API
    
    - **limit**: Number of transactions (1-200)
    """
    cache_key = get_cache_key("/transactions", {"limit": limit})
    
    # Check cache
    if is_cache_valid(cache_key):
        return cache[cache_key]
    
    # Fetch from Horizon
    data = await fetch_from_horizon("/transactions", {"order": "desc", "limit": limit})
    
    transactions = []
    if "_embedded" in data and "records" in data["_embedded"]:
        for record in data["_embedded"]["records"]:
            # Fetch operations for each transaction
            try:
                ops_data = await fetch_from_horizon(f"/transactions/{record['id']}/operations")
                operations = parse_operations({"_embedded": {"operations": ops_data.get("_embedded", {}).get("records", [])}})
            except:
                operations = []
            
            tx = Transaction(
                id=record["id"],
                source_account=record["source_account"],
                created_at=record["created_at"],
                operations=operations
            )
            transactions.append(tx)
            
            # Update frequency tracking
            update_wallet_frequency(record["source_account"])
            for op in operations:
                if op.from_account:
                    update_wallet_frequency(op.from_account)
                if op.to:
                    update_wallet_frequency(op.to)
    
    response = TransactionResponse(
        transactions=transactions,
        count=len(transactions)
    )
    
    # Cache the response
    cache[cache_key] = response
    cache_timestamps[cache_key] = datetime.utcnow()
    
    return response


@app.get("/transactions/wallet/{address}")
async def get_wallet_transactions(
    address: str,
    limit: int = Query(default=50, ge=1, le=200, description="Number of transactions to fetch")
):
    """
    Get transaction history for a specific wallet
    
    - **address**: Stellar wallet address (public key)
    - **limit**: Number of transactions (1-200)
    """
    cache_key = get_cache_key(f"/accounts/{address}/transactions", {"limit": limit})
    
    # Check cache
    if is_cache_valid(cache_key):
        return cache[cache_key]
    
    # Fetch from Horizon
    try:
        data = await fetch_from_horizon(f"/accounts/{address}/transactions", {"order": "desc", "limit": limit})
    except HTTPException as e:
        if "404" in str(e.detail):
            raise HTTPException(status_code=404, detail=f"Wallet {address} not found")
        raise
    
    transactions = []
    if "_embedded" in data and "records" in data["_embedded"]:
        for record in data["_embedded"]["records"]:
            # Fetch operations
            try:
                ops_data = await fetch_from_horizon(f"/transactions/{record['id']}/operations")
                operations = parse_operations({"_embedded": {"operations": ops_data.get("_embedded", {}).get("records", [])}})
            except:
                operations = []
            
            tx = Transaction(
                id=record["id"],
                source_account=record["source_account"],
                created_at=record["created_at"],
                operations=operations
            )
            transactions.append(tx)
    
    response = {
        "wallet": address,
        "transactions": transactions,
        "count": len(transactions)
    }
    
    # Cache the response
    cache[cache_key] = response
    cache_timestamps[cache_key] = datetime.utcnow()
    
    return response


@app.get("/wallets/frequency", response_model=WalletFrequencyResponse)
async def get_wallet_frequencies():
    """
    Get real-time transaction frequency for all tracked wallets
    
    Returns transaction count and transactions per hour for each wallet.
    This data updates in real-time as transactions are fetched.
    """
    wallets = []
    
    for wallet_address, data in wallet_tx_frequency.items():
        tx_per_hour = calculate_tx_per_hour(wallet_address)
        
        wallets.append(WalletFrequency(
            wallet=wallet_address,
            tx_count=data["count"],
            tx_per_hour=tx_per_hour,
            last_updated=data["last_updated"].isoformat()
        ))
    
    # Sort by transaction frequency (highest first)
    wallets.sort(key=lambda x: x.tx_per_hour, reverse=True)
    
    return WalletFrequencyResponse(
        wallets=wallets,
        total_wallets=len(wallets),
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/wallets/frequency/{address}")
async def get_wallet_frequency(address: str):
    """
    Get transaction frequency for a specific wallet
    
    - **address**: Stellar wallet address
    """
    if address not in wallet_tx_frequency:
        return {
            "wallet": address,
            "tx_count": 0,
            "tx_per_hour": 0.0,
            "message": "Wallet not yet tracked. Fetch transactions first."
        }
    
    data = wallet_tx_frequency[address]
    tx_per_hour = calculate_tx_per_hour(address)
    
    return {
        "wallet": address,
        "tx_count": data["count"],
        "tx_per_hour": tx_per_hour,
        "last_updated": data["last_updated"].isoformat()
    }


@app.get("/explorer/transactions/recent", response_model=TransactionResponseWithLinks)
async def get_recent_transactions_with_links(
    limit: int = Query(default=200, ge=1, le=200, description="Number of transactions to fetch")
):
    """
    Fetch recent transactions WITH Stellar Expert URLs for frontend integration
    
    - **limit**: Number of transactions (1-200)
    
    Returns transactions with clickable explorer links for easy viewing
    """
    # Get base transaction data
    tx_response = await get_recent_transactions(limit)
    
    # Enrich with Stellar Expert URLs
    transactions_with_links = []
    for tx in tx_response.transactions:
        transactions_with_links.append(TransactionWithLinks(
            id=tx.id,
            source_account=tx.source_account,
            created_at=tx.created_at,
            operations=tx.operations,
            explorer_url=get_stellar_expert_url("tx", tx.id),
            account_url=get_stellar_expert_url("account", tx.source_account)
        ))
    
    return TransactionResponseWithLinks(
        transactions=transactions_with_links,
        count=len(transactions_with_links),
        network=get_network_type()
    )


@app.get("/explorer/wallets/frequency", response_model=WalletFrequencyResponseWithLinks)
async def get_wallet_frequencies_with_links():
    """
    Get wallet frequencies WITH Stellar Expert URLs and risk levels
    
    Perfect for frontend dashboards - includes:
    - Transaction frequency metrics
    - Clickable Stellar Expert links
    - Risk level classification (normal/medium/elevated/high)
    """
    # Get base frequency data
    freq_response = await get_wallet_frequencies()
    
    # Enrich with Stellar Expert URLs and risk levels
    wallets_with_links = []
    for wallet in freq_response.wallets:
        wallets_with_links.append(WalletFrequencyWithLinks(
            wallet=wallet.wallet,
            tx_count=wallet.tx_count,
            tx_per_hour=wallet.tx_per_hour,
            last_updated=wallet.last_updated,
            explorer_url=get_stellar_expert_url("account", wallet.wallet),
            risk_level=get_risk_level(wallet.tx_per_hour)
        ))
    
    return WalletFrequencyResponseWithLinks(
        wallets=wallets_with_links,
        total_wallets=len(wallets_with_links),
        timestamp=datetime.utcnow().isoformat(),
        network=get_network_type()
    )


@app.get("/explorer/wallet/{address}")
async def get_wallet_with_links(address: str):
    """
    Get wallet details WITH Stellar Expert URL
    
    - **address**: Stellar wallet address
    
    Returns wallet info with clickable explorer link
    """
    # Get frequency data
    if address not in wallet_tx_frequency:
        return {
            "wallet": address,
            "tx_count": 0,
            "tx_per_hour": 0.0,
            "risk_level": "unknown",
            "explorer_url": get_stellar_expert_url("account", address),
            "message": "Wallet not yet tracked. Fetch transactions first."
        }
    
    data = wallet_tx_frequency[address]
    tx_per_hour = calculate_tx_per_hour(address)
    
    return {
        "wallet": address,
        "tx_count": data["count"],
        "tx_per_hour": tx_per_hour,
        "risk_level": get_risk_level(tx_per_hour),
        "last_updated": data["last_updated"].isoformat(),
        "explorer_url": get_stellar_expert_url("account", address),
        "network": get_network_type()
    }


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "Stellar Horizon Data Fetcher",
        "version": "1.0.0",
        "network": get_network_type(),
        "endpoints": {
            "health": "/health",
            "recent_transactions": "/transactions/recent?limit=200",
            "wallet_transactions": "/transactions/wallet/{address}?limit=50",
            "all_wallet_frequencies": "/wallets/frequency",
            "wallet_frequency": "/wallets/frequency/{address}",
            "explorer_transactions": "/explorer/transactions/recent?limit=200",
            "explorer_wallets": "/explorer/wallets/frequency",
            "explorer_wallet": "/explorer/wallet/{address}",
            "docs": "/docs"
        },
        "horizon_api": HORIZON_API_URL,
        "note": "Use /explorer/* endpoints for frontend integration - includes Stellar Expert URLs"
    }


# Background task to clean old cache entries
@app.on_event("startup")
async def startup_event():
    """Startup event to initialize background tasks"""
    asyncio.create_task(cache_cleanup_task())


async def cache_cleanup_task():
    """Clean up old cache entries every minute"""
    while True:
        await asyncio.sleep(60)  # Run every minute
        
        now = datetime.utcnow()
        expired_keys = [
            key for key, timestamp in cache_timestamps.items()
            if (now - timestamp).total_seconds() > CACHE_TTL_SECONDS * 2
        ]
        
        for key in expired_keys:
            cache.pop(key, None)
            cache_timestamps.pop(key, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
