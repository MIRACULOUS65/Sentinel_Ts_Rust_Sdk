"""
Data Ingestion
Stream transactions from files or Stellar Horizon API.
"""
import json
import httpx
import asyncio
from typing import Generator, Dict, List, AsyncGenerator, Optional
from pathlib import Path


def stream_jsonl(filepath: str) -> Generator[Dict, None, None]:
    """
    Stream transactions from a JSON Lines file.
    
    Args:
        filepath: Path to .jsonl file
    
    Yields:
        Transaction dicts
    """
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_jsonl(filepath: str) -> List[Dict]:
    """
    Load all transactions from a JSON Lines file.
    
    Args:
        filepath: Path to .jsonl file
    
    Returns:
        List of transaction dicts
    """
    return list(stream_jsonl(filepath))


async def stream_horizon(
    horizon_url: str = "https://horizon-testnet.stellar.org",
    limit: int = 100,
    cursor: Optional[str] = None
) -> AsyncGenerator[Dict, None]:
    """
    Stream transactions from Stellar Horizon API.
    
    Args:
        horizon_url: Horizon server URL
        limit: Transactions per page
        cursor: Starting cursor (None for latest)
    
    Yields:
        Transaction dicts in our schema format
    """
    async with httpx.AsyncClient() as client:
        url = f"{horizon_url}/payments"
        params = {
            "limit": limit,
            "order": "desc",
        }
        if cursor:
            params["cursor"] = cursor
        
        while True:
            try:
                response = await client.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                records = data.get("_embedded", {}).get("records", [])
                
                if not records:
                    break
                
                for record in records:
                    # Convert Horizon format to our schema
                    if record.get("type") == "payment":
                        yield {
                            "tx_hash": record.get("transaction_hash", ""),
                            "timestamp": parse_timestamp(record.get("created_at", "")),
                            "from_addr": record.get("from", ""),
                            "to_addr": record.get("to", ""),
                            "amount": float(record.get("amount", 0)),
                            "asset_type": record.get("asset_type", "native"),
                        }
                
                # Get next page
                next_link = data.get("_links", {}).get("next", {}).get("href")
                if not next_link:
                    break
                
                # Extract cursor from next link
                cursor = records[-1].get("paging_token")
                params["cursor"] = cursor
                
            except Exception as e:
                print(f"⚠️ Horizon error: {e}")
                await asyncio.sleep(5)
                continue


def parse_timestamp(iso_string: str) -> float:
    """Parse ISO timestamp to Unix timestamp."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.timestamp()
    except:
        return 0.0


class HorizonStreamer:
    """
    Real-time transaction streamer from Stellar Horizon.
    """
    
    def __init__(self, horizon_url: str = "https://horizon-testnet.stellar.org"):
        self.horizon_url = horizon_url
        self.running = False
    
    async def stream(
        self,
        callback: callable,
        poll_interval: float = 1.0
    ):
        """
        Stream transactions and call callback for each.
        
        Args:
            callback: Function to call with each transaction
            poll_interval: Seconds between polls
        """
        self.running = True
        cursor = None
        
        async with httpx.AsyncClient() as client:
            while self.running:
                try:
                    url = f"{self.horizon_url}/payments"
                    params = {"limit": 50, "order": "desc"}
                    if cursor:
                        params["cursor"] = cursor
                    
                    response = await client.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    records = data.get("_embedded", {}).get("records", [])
                    
                    for record in records:
                        if record.get("type") == "payment":
                            tx = {
                                "tx_hash": record.get("transaction_hash", ""),
                                "timestamp": parse_timestamp(record.get("created_at", "")),
                                "from_addr": record.get("from", ""),
                                "to_addr": record.get("to", ""),
                                "amount": float(record.get("amount", 0)),
                                "asset_type": record.get("asset_type", "native"),
                            }
                            await callback(tx)
                    
                    if records:
                        cursor = records[0].get("paging_token")
                    
                    await asyncio.sleep(poll_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"⚠️ Stream error: {e}")
                    await asyncio.sleep(5)
    
    def stop(self):
        """Stop the streamer."""
        self.running = False
