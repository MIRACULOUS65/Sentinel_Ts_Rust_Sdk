"""
Training Script
Orchestrates the full training pipeline.
"""
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import Optional

from .ingest import load_jsonl
from .state_manager import WalletStateManager
from .risk_engine import RiskEngine


def train_from_dataset(
    dataset_path: str,
    model_dir: str = "models",
    min_wallet_txs: int = 5,
    validation_split: float = 0.2
) -> RiskEngine:
    """
    Train risk engine from a dataset file.
    
    Args:
        dataset_path: Path to synthetic_dataset.jsonl
        model_dir: Directory to save models
        min_wallet_txs: Minimum transactions per wallet
        validation_split: Proportion of data for validation
    
    Returns:
        Trained RiskEngine
    """
    print("=" * 60)
    print("🚀 SENTINEL ML TRAINING PIPELINE")
    print("=" * 60)
    
    # Load data
    print(f"\n📂 Loading dataset: {dataset_path}")
    transactions = load_jsonl(dataset_path)
    print(f"   • Loaded {len(transactions):,} transactions")
    
    # Split into train/validation
    split_idx = int(len(transactions) * (1 - validation_split))
    train_txs = transactions[:split_idx]
    val_txs = transactions[split_idx:]
    
    print(f"   • Training: {len(train_txs):,} txs")
    print(f"   • Validation: {len(val_txs):,} txs")
    
    # Build state from training data
    print(f"\n🔄 Building wallet state...")
    state_manager = WalletStateManager()
    
    for tx in tqdm(train_txs, desc="Ingesting"):
        state_manager.add_transaction(tx)
    
    print(f"   • Unique wallets: {state_manager.get_wallet_count()}")
    
    # Initialize and train risk engine
    engine = RiskEngine()
    engine.train(state_manager)
    
    # Validation
    print("\n" + "=" * 60)
    print("📊 VALIDATION")
    print("=" * 60)
    
    # Add validation transactions to state
    for tx in val_txs:
        state_manager.add_transaction(tx)
    
    # Get predictions for validation wallets
    val_wallets = set(tx["from_addr"] for tx in val_txs)
    predictions = []
    labels = []
    
    for wallet in tqdm(list(val_wallets)[:200], desc="Validating"):
        sender_txs = state_manager.sender_history.get(wallet, [])
        if len(sender_txs) < min_wallet_txs:
            continue
        
        # Get ground truth label from transactions
        wallet_labels = [tx.get("label", "normal") for tx in sender_txs]
        true_label = max(set(wallet_labels), key=wallet_labels.count)
        
        # Get prediction
        score, reason, details = engine.predict(wallet, state_manager)
        
        predictions.append({
            "wallet": wallet[:16] + "...",
            "score": score,
            "reason": reason,
            "true_label": true_label
        })
        labels.append(true_label)
    
    # Print validation results
    if predictions:
        scores = [p["score"] for p in predictions]
        print(f"\n📈 Score Distribution:")
        print(f"   • Min: {min(scores)}")
        print(f"   • Max: {max(scores)}")
        print(f"   • Mean: {np.mean(scores):.1f}")
        print(f"   • Std: {np.std(scores):.1f}")
        
        # Distribution by category
        freeze = sum(1 for s in scores if s >= 70)
        limit = sum(1 for s in scores if 31 <= s < 70)
        allow = sum(1 for s in scores if s < 31)
        
        print(f"\n🎯 Risk Category Distribution:")
        print(f"   🔴 Freeze (70-100): {freeze} ({freeze/len(scores)*100:.1f}%)")
        print(f"   🟡 Limit (31-69): {limit} ({limit/len(scores)*100:.1f}%)")
        print(f"   🟢 Allow (0-30): {allow} ({allow/len(scores)*100:.1f}%)")
        
        # Sample predictions
        print(f"\n📋 Sample Predictions:")
        for pred in predictions[:10]:
            emoji = "🔴" if pred["score"] >= 70 else ("🟡" if pred["score"] >= 31 else "🟢")
            print(f"   {emoji} {pred['wallet']} | Score: {pred['score']:3d} | {pred['reason']}")
            print(f"      True Label: {pred['true_label']}")
    
    # Save models
    print("\n" + "=" * 60)
    print("💾 SAVING MODELS")
    print("=" * 60)
    
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    engine.save(model_dir)
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print("=" * 60)
    
    return engine


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Sentinel ML Risk Engine")
    parser.add_argument("--dataset", type=str, default="synthetic_dataset.jsonl")
    parser.add_argument("--model-dir", type=str, default="models")
    parser.add_argument("--min-txs", type=int, default=5)
    parser.add_argument("--val-split", type=float, default=0.2)
    
    args = parser.parse_args()
    
    train_from_dataset(
        dataset_path=args.dataset,
        model_dir=args.model_dir,
        min_wallet_txs=args.min_txs,
        validation_split=args.val_split
    )
