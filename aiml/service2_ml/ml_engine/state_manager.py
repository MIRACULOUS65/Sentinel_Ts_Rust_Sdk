"""
Wallet State Manager
Maintains rolling transaction windows for each wallet.
"""
from collections import defaultdict
from typing import Dict, List, Optional
import time


class WalletStateManager:
    """
    Maintains rolling transaction history for wallets.
    Supports multiple time windows for feature extraction.
    """
    
    # Time windows in seconds
    WINDOWS = {
        "1m": 60,
        "10m": 600,
        "1h": 3600,
        "24h": 86400,
    }
    
    def __init__(self, max_history: int = 10000):
        """
        Args:
            max_history: Maximum transactions to keep per wallet
        """
        self.max_history = max_history
        
        # Transaction history per wallet (as sender)
        self.sender_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Transaction history per wallet (as receiver)
        self.receiver_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # All unique wallets seen
        self.all_wallets: set = set()
        
        # Total transaction count
        self.total_tx_count = 0
        
        # Last cleanup timestamp
        self.last_cleanup = 0
    
    def add_transaction(self, tx: Dict) -> None:
        """
        Add a transaction to the state.
        
        Args:
            tx: Transaction dict with from_addr, to_addr, timestamp, amount
        """
        sender = tx["from_addr"]
        receiver = tx["to_addr"]
        
        # Track all wallets
        self.all_wallets.add(sender)
        self.all_wallets.add(receiver)
        
        # Add to sender history
        self.sender_history[sender].append(tx)
        
        # Add to receiver history (for graph analysis)
        self.receiver_history[receiver].append(tx)
        
        self.total_tx_count += 1
        
        # Periodic cleanup
        if self.total_tx_count % 1000 == 0:
            self._cleanup_old_transactions()
    
    def get_sender_transactions(
        self, 
        wallet: str, 
        window: Optional[str] = None,
        current_ts: Optional[float] = None
    ) -> List[Dict]:
        """
        Get transactions where wallet is the sender.
        
        Args:
            wallet: Wallet address
            window: Time window ("1m", "10m", "1h", "24h") or None for all
            current_ts: Reference timestamp (default: now)
        
        Returns:
            List of transactions
        """
        txs = self.sender_history.get(wallet, [])
        
        if window is None:
            return txs
        
        if current_ts is None:
            current_ts = time.time()
        
        window_seconds = self.WINDOWS.get(window, 86400)
        cutoff = current_ts - window_seconds
        
        return [tx for tx in txs if tx["timestamp"] >= cutoff]
    
    def get_receiver_transactions(
        self,
        wallet: str,
        window: Optional[str] = None,
        current_ts: Optional[float] = None
    ) -> List[Dict]:
        """
        Get transactions where wallet is the receiver.
        """
        txs = self.receiver_history.get(wallet, [])
        
        if window is None:
            return txs
        
        if current_ts is None:
            current_ts = time.time()
        
        window_seconds = self.WINDOWS.get(window, 86400)
        cutoff = current_ts - window_seconds
        
        return [tx for tx in txs if tx["timestamp"] >= cutoff]
    
    def get_all_transactions(
        self,
        wallet: str,
        window: Optional[str] = None,
        current_ts: Optional[float] = None
    ) -> List[Dict]:
        """
        Get all transactions involving this wallet (as sender or receiver).
        """
        sent = self.get_sender_transactions(wallet, window, current_ts)
        received = self.get_receiver_transactions(wallet, window, current_ts)
        
        # Combine and sort by timestamp
        all_txs = sent + received
        all_txs.sort(key=lambda x: x["timestamp"])
        
        return all_txs
    
    def get_unique_recipients(
        self,
        wallet: str,
        window: Optional[str] = None,
        current_ts: Optional[float] = None
    ) -> set:
        """Get unique recipients for a wallet's outgoing transactions."""
        txs = self.get_sender_transactions(wallet, window, current_ts)
        return set(tx["to_addr"] for tx in txs)
    
    def get_unique_senders(
        self,
        wallet: str,
        window: Optional[str] = None,
        current_ts: Optional[float] = None
    ) -> set:
        """Get unique senders for a wallet's incoming transactions."""
        txs = self.get_receiver_transactions(wallet, window, current_ts)
        return set(tx["from_addr"] for tx in txs)
    
    def _cleanup_old_transactions(self):
        """Remove old transactions beyond max_history."""
        for wallet in list(self.sender_history.keys()):
            if len(self.sender_history[wallet]) > self.max_history:
                self.sender_history[wallet] = self.sender_history[wallet][-self.max_history:]
        
        for wallet in list(self.receiver_history.keys()):
            if len(self.receiver_history[wallet]) > self.max_history:
                self.receiver_history[wallet] = self.receiver_history[wallet][-self.max_history:]
    
    def get_wallet_count(self) -> int:
        """Get number of unique wallets seen."""
        return len(self.all_wallets)
    
    def get_transaction_count(self) -> int:
        """Get total transaction count."""
        return self.total_tx_count
    
    def clear(self):
        """Clear all state."""
        self.sender_history.clear()
        self.receiver_history.clear()
        self.all_wallets.clear()
        self.total_tx_count = 0
