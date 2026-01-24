"""
Advanced Training Pipeline
Proper epoch-based training with loss tracking, early stopping, and comprehensive metrics.
"""
import numpy as np
import json
import time
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict

from service4_ml.ml_engine.ingest import load_jsonl
from service4_ml.ml_engine.state_manager import WalletStateManager
from service4_ml.ml_engine.features import FeatureExtractor
from service4_ml.ml_engine.neural_model import NeuralRiskModel, create_synthetic_labels
from service4_ml.ml_engine.pattern_scorer import PatternScorer


class AdvancedTrainer:
    """
    Advanced training pipeline with proper ML practices.
    
    Features:
    - Epoch-based training with progress
    - Early stopping to prevent overfitting
    - Train/validation/test splits
    - Loss and accuracy curves
    - Model checkpointing
    - Learning rate scheduling
    """
    
    def __init__(
        self,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        patience: int = 15,
        val_split: float = 0.2,
        test_split: float = 0.1
    ):
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.patience = patience
        self.val_split = val_split
        self.test_split = test_split
        
        self.state_manager = WalletStateManager()
        self.feature_extractor = FeatureExtractor()
        self.neural_model = None
        self.pattern_scorer = PatternScorer()
        
    def load_data(self, dataset_path: str):
        """Load and preprocess dataset."""
        print("\n" + "=" * 80)
        print("📂 LOADING DATASET")
        print("=" * 80)
        
        transactions = load_jsonl(dataset_path)
        print(f"   • Loaded {len(transactions):,} transactions")
        
        # Build wallet state
        print("   • Building wallet state...")
        for tx in tqdm(transactions, desc="Processing"):
            self.state_manager.add_transaction(tx)
        
        print(f"   • Unique wallets: {len(self.state_manager.sender_history):,}")
        
        return transactions
    
    def extract_features(self, min_tx: int = 5):
        """Extract features from wallet histories."""
        print("\n" + "=" * 80)
        print("🔬 FEATURE EXTRACTION")
        print("=" * 80)
        
        features_list = []
        wallet_list = []
        
        for wallet in tqdm(self.state_manager.sender_history.keys(), desc="Extracting"):
            sender_txs = self.state_manager.sender_history.get(wallet, [])
            
            if len(sender_txs) < min_tx:
                continue
            
            receiver_txs = self.state_manager.receiver_history.get(wallet, [])
            latest_ts = max(tx['timestamp'] for tx in sender_txs)
            
            features = self.feature_extractor.extract_features(sender_txs, receiver_txs, latest_ts)
            features_list.append(list(features.values()))
            wallet_list.append(wallet)
        
        X = np.array(features_list)
        feature_names = list(features.keys())
        
        print(f"   • Feature matrix shape: {X.shape}")
        print(f"   • Features: {len(feature_names)}")
        
        return X, wallet_list, feature_names
    
    def normalize_features(self, X: np.ndarray) -> np.ndarray:
        """Normalize features to 0-1 range."""
        X_norm = X.copy()
        
        for i in range(X.shape[1]):
            col = X[:, i]
            min_val = np.min(col)
            max_val = np.max(col)
            
            if max_val > min_val:
                X_norm[:, i] = (col - min_val) / (max_val - min_val)
            else:
                X_norm[:, i] = 0
        
        return X_norm
    
    def split_data(self, X: np.ndarray, y: np.ndarray):
        """Split data into train/val/test sets."""
        n = len(X)
        indices = np.random.permutation(n)
        
        test_size = int(n * self.test_split)
        val_size = int(n * self.val_split)
        
        test_idx = indices[:test_size]
        val_idx = indices[test_size:test_size + val_size]
        train_idx = indices[test_size + val_size:]
        
        return (
            X[train_idx], y[train_idx],
            X[val_idx], y[val_idx],
            X[test_idx], y[test_idx]
        )
    
    def train(self, dataset_path: str, output_dir: str = "models"):
        """Run complete training pipeline."""
        start_time = time.time()
        
        print("\n" + "=" * 80)
        print("🚀 ADVANCED NEURAL NETWORK TRAINING PIPELINE")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Dataset: {dataset_path}")
        print(f"Configuration:")
        print(f"   • Epochs: {self.epochs}")
        print(f"   • Batch size: {self.batch_size}")
        print(f"   • Learning rate: {self.learning_rate}")
        print(f"   • Early stopping patience: {self.patience}")
        print(f"   • Validation split: {self.val_split:.0%}")
        print(f"   • Test split: {self.test_split:.0%}")
        
        # Load data
        transactions = self.load_data(dataset_path)
        
        # Extract features
        X, wallets, feature_names = self.extract_features()
        
        # Normalize
        print("\n   • Normalizing features...")
        X_norm = self.normalize_features(X)
        
        # Fit pattern scorer for baseline
        self.pattern_scorer.fit(X, feature_names)
        
        # Create labels from pattern scorer
        print("\n" + "=" * 80)
        print("🏷️ CREATING TRAINING LABELS")
        print("=" * 80)
        
        y = np.zeros(len(wallets))
        for i, wallet in enumerate(wallets):
            features_dict = dict(zip(feature_names, X[i]))
            risk_score, _, _ = self.pattern_scorer.get_risk_assessment(features_dict)
            y[i] = risk_score / 100.0  # Normalize to 0-1
        
        print(f"   • Label distribution:")
        print(f"      - Low risk (0-30): {np.sum(y < 0.31):,} ({np.mean(y < 0.31):.1%})")
        print(f"      - Medium risk (31-69): {np.sum((y >= 0.31) & (y < 0.70)):,} ({np.mean((y >= 0.31) & (y < 0.70)):.1%})")
        print(f"      - High risk (70-100): {np.sum(y >= 0.70):,} ({np.mean(y >= 0.70):.1%})")
        
        # Split data
        print("\n" + "=" * 80)
        print("📊 DATA SPLITTING")
        print("=" * 80)
        
        X_train, y_train, X_val, y_val, X_test, y_test = self.split_data(X_norm, y)
        
        print(f"   • Training set: {len(X_train):,} samples")
        print(f"   • Validation set: {len(X_val):,} samples")
        print(f"   • Test set: {len(X_test):,} samples")
        
        # Create neural network
        self.neural_model = NeuralRiskModel(
            input_dim=X_norm.shape[1],
            hidden_layers=[64, 32, 16],
            learning_rate=self.learning_rate,
            dropout_rate=0.2
        )
        
        # Train
        history = self.neural_model.fit(
            X_train, y_train,
            X_val, y_val,
            epochs=self.epochs,
            batch_size=self.batch_size,
            patience=self.patience,
            verbose=True
        )
        
        # Evaluate on test set
        print("\n" + "=" * 80)
        print("📈 TEST SET EVALUATION")
        print("=" * 80)
        
        test_pred = self.neural_model.predict(X_test)
        test_true = (y_test * 100).astype(int)
        
        # Calculate metrics
        mae = np.mean(np.abs(test_pred - test_true))
        mse = np.mean((test_pred - test_true) ** 2)
        rmse = np.sqrt(mse)
        
        # Category accuracy
        true_cat = np.where(test_true < 31, 0, np.where(test_true < 70, 1, 2))
        pred_cat = np.where(test_pred < 31, 0, np.where(test_pred < 70, 1, 2))
        cat_acc = np.mean(true_cat == pred_cat)
        
        print(f"   • Mean Absolute Error: {mae:.2f}")
        print(f"   • Root Mean Squared Error: {rmse:.2f}")
        print(f"   • Category Accuracy: {cat_acc:.2%}")
        print(f"\n   Sample Predictions:")
        
        for i in range(min(10, len(test_pred))):
            true = test_true[i]
            pred = test_pred[i]
            diff = abs(true - pred)
            marker = "✅" if diff < 15 else "⚠️" if diff < 30 else "❌"
            print(f"      {marker} True: {true:3d}, Predicted: {pred:3d}, Diff: {diff:3d}")
        
        # Save models
        print("\n" + "=" * 80)
        print("💾 SAVING MODELS")
        print("=" * 80)
        
        Path(output_dir).mkdir(exist_ok=True)
        
        self.neural_model.save(f"{output_dir}/neural_model.pkl")
        self.pattern_scorer.save(f"{output_dir}/pattern_scorer.pkl")
        
        # Save training history
        with open(f"{output_dir}/training_history.json", 'w') as f:
            json.dump({
                "epochs_trained": len(history["train_losses"]),
                "final_train_loss": history["train_losses"][-1] if history["train_losses"] else None,
                "final_val_loss": history["val_losses"][-1] if history["val_losses"] else None,
                "best_val_loss": history["best_val_loss"],
                "test_mae": float(mae),
                "test_rmse": float(rmse),
                "test_accuracy": float(cat_acc)
            }, f, indent=2)
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("✅ TRAINING COMPLETE")
        print("=" * 80)
        print(f"   • Total time: {elapsed/60:.1f} minutes")
        print(f"   • Epochs trained: {len(history['train_losses'])}")
        print(f"   • Best validation loss: {history['best_val_loss']:.6f}")
        print(f"   • Test accuracy: {cat_acc:.2%}")
        print(f"\n   Models saved to: {output_dir}/")
        
        return history


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Advanced ML Training")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset path")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--patience", type=int, default=15, help="Early stopping patience")
    parser.add_argument("--output", type=str, default="models", help="Output directory")
    args = parser.parse_args()
    
    trainer = AdvancedTrainer(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        patience=args.patience
    )
    
    trainer.train(args.dataset, args.output)


if __name__ == "__main__":
    main()
