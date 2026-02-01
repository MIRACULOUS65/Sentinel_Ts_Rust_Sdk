"""
Streaming API Server
FastAPI server for real-time risk scoring.
"""
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .state_manager import WalletStateManager
from .risk_engine import RiskEngine
from .ingest import HorizonStreamer

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel ML Risk Engine",
    description="Streaming behavioral anomaly detection for Stellar wallets",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
state_manager = WalletStateManager()
risk_engine = RiskEngine()
horizon_streamer: Optional[HorizonStreamer] = None
websocket_clients: List[WebSocket] = []


# Request/Response models
class TransactionRequest(BaseModel):
    tx_hash: str
    timestamp: float
    from_addr: str
    to_addr: str
    amount: float
    asset_type: str = "native"


class RiskResponse(BaseModel):
    wallet: str
    risk_score: int
    reason: str
    timestamp: float
    pattern_scores: Optional[Dict[str, int]] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    wallet_count: int
    tx_count: int


@app.on_event("startup")
async def startup():
    """Load models on startup."""
    # Find models directory relative to this file
    base_dir = Path(__file__).parent.parent
    model_dir = base_dir / "models"
    
    if model_dir.exists():
        try:
            risk_engine.load(model_dir)
            print("✅ Models loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load models: {e}")
            print("   Train the model first with: python -m service4_ml.ml_engine.train")
    else:
        print("⚠️ No models found. Train first.")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=risk_engine.is_fitted,
        wallet_count=state_manager.get_wallet_count(),
        tx_count=state_manager.get_transaction_count()
    )


@app.post("/ingest", response_model=RiskResponse)
async def ingest_transaction(tx: TransactionRequest):
    """
    Ingest a transaction and return updated risk score.
    """
    if not risk_engine.is_fitted:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Add to state
    tx_dict = tx.model_dump()
    state_manager.add_transaction(tx_dict)
    
    # Get risk score for sender
    score, reason, details = risk_engine.predict(
        tx.from_addr, 
        state_manager,
        tx.timestamp
    )
    
    response = RiskResponse(
        wallet=tx.from_addr,
        risk_score=score,
        reason=reason,
        timestamp=datetime.now().timestamp(),
        pattern_scores=details.get("pattern_details")
    )
    
    # Broadcast to WebSocket clients
    await broadcast_risk(response)
    
    return response


@app.get("/risk/{wallet}", response_model=RiskResponse)
async def get_risk(wallet: str):
    """
    Get current risk score for a wallet.
    """
    if not risk_engine.is_fitted:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if wallet not in state_manager.all_wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    score, reason, details = risk_engine.predict(wallet, state_manager)
    
    return RiskResponse(
        wallet=wallet,
        risk_score=score,
        reason=reason,
        timestamp=datetime.now().timestamp(),
        pattern_scores=details.get("pattern_details")
    )


@app.get("/wallets")
async def list_wallets(limit: int = 100):
    """List all known wallets with their risk scores."""
    if not risk_engine.is_fitted:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    wallets = list(state_manager.all_wallets)[:limit]
    results = []
    
    for wallet in wallets:
        score, reason, _ = risk_engine.predict(wallet, state_manager)
        results.append({
            "wallet": wallet,
            "risk_score": score,
            "reason": reason,
            "tx_count": len(state_manager.sender_history.get(wallet, []))
        })
    
    # Sort by risk score descending
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {"wallets": results, "total": len(state_manager.all_wallets)}


@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time risk updates.
    """
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle ping
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)


async def broadcast_risk(response: RiskResponse):
    """Broadcast risk update to all connected clients."""
    if not websocket_clients:
        return
    
    message = response.model_dump_json()
    
    for client in websocket_clients:
        try:
            await client.send_text(message)
        except:
            pass


@app.post("/start-horizon")
async def start_horizon_stream():
    """Start streaming from Stellar Horizon."""
    global horizon_streamer
    
    if horizon_streamer and horizon_streamer.running:
        return {"status": "already running"}
    
    horizon_streamer = HorizonStreamer()
    
    async def handle_tx(tx):
        state_manager.add_transaction(tx)
        
        if risk_engine.is_fitted:
            score, reason, details = risk_engine.predict(
                tx["from_addr"],
                state_manager,
                tx["timestamp"]
            )
            
            response = RiskResponse(
                wallet=tx["from_addr"],
                risk_score=score,
                reason=reason,
                timestamp=datetime.now().timestamp()
            )
            
            await broadcast_risk(response)
    
    asyncio.create_task(horizon_streamer.stream(handle_tx))
    
    return {"status": "started"}


@app.post("/stop-horizon")
async def stop_horizon_stream():
    """Stop Horizon streaming."""
    global horizon_streamer
    
    if horizon_streamer:
        horizon_streamer.stop()
        return {"status": "stopped"}
    
    return {"status": "not running"}


def run_server(host: str = "0.0.0.0", port: int = 8084):
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
