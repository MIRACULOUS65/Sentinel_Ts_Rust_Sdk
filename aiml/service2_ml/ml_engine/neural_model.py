"""
Neural Network Risk Scorer
Proper epoch-based training with loss tracking, early stopping, and validation metrics.
"""
import numpy as np
import pickle
import os
from typing import Dict, List, Tuple
from datetime import datetime


class NeuralRiskModel:
    """
    Neural network for risk scoring with proper training pipeline.
    
    Features:
    - Epoch-based training
    - Early stopping with patience
    - Loss tracking (MSE/BCE)
    - Validation metrics
    - Learning progress visualization
    """
    
    def __init__(
        self,
        input_dim: int = 16,
        hidden_layers: List[int] = [64, 32, 16],
        learning_rate: float = 0.001,
        dropout_rate: float = 0.2
    ):
        self.input_dim = input_dim
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        self.best_val_loss = float('inf')
        self.best_weights = None
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Xavier initialization for weights."""
        np.random.seed(42)
        
        self.weights = []
        self.biases = []
        
        layer_dims = [self.input_dim] + self.hidden_layers + [1]
        
        for i in range(len(layer_dims) - 1):
            # Xavier initialization
            w = np.random.randn(layer_dims[i], layer_dims[i+1]) * np.sqrt(2.0 / layer_dims[i])
            b = np.zeros((1, layer_dims[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def _relu(self, x):
        return np.maximum(0, x)
    
    def _relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def _sigmoid(self, x):
        x = np.clip(x, -500, 500)  # Prevent overflow
        return 1 / (1 + np.exp(-x))
    
    def _forward(self, X: np.ndarray, training: bool = True) -> Tuple[np.ndarray, List]:
        """Forward pass through the network."""
        activations = [X]
        current = X
        
        for i in range(len(self.weights) - 1):
            z = current @ self.weights[i] + self.biases[i]
            current = self._relu(z)
            
            # Dropout during training
            if training and self.dropout_rate > 0:
                mask = np.random.binomial(1, 1 - self.dropout_rate, current.shape) / (1 - self.dropout_rate)
                current = current * mask
            
            activations.append(current)
        
        # Output layer with sigmoid
        z = current @ self.weights[-1] + self.biases[-1]
        output = self._sigmoid(z)
        activations.append(output)
        
        return output, activations
    
    def _backward(self, X: np.ndarray, y: np.ndarray, activations: List) -> Tuple[List, List]:
        """Backpropagation."""
        m = X.shape[0]
        
        # Output layer error
        output = activations[-1]
        delta = output - y.reshape(-1, 1)
        
        weight_grads = []
        bias_grads = []
        
        # Backpropagate through layers
        for i in range(len(self.weights) - 1, -1, -1):
            weight_grad = activations[i].T @ delta / m
            bias_grad = np.mean(delta, axis=0, keepdims=True)
            
            weight_grads.insert(0, weight_grad)
            bias_grads.insert(0, bias_grad)
            
            if i > 0:
                delta = (delta @ self.weights[i].T) * self._relu_derivative(activations[i])
        
        return weight_grads, bias_grads
    
    def _compute_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Binary cross-entropy loss."""
        eps = 1e-7
        y_pred = np.clip(y_pred, eps, 1 - eps)
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
    def _compute_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute accuracy for risk classification."""
        # Convert to risk categories: 0=low, 1=medium, 2=high
        y_true_cat = np.where(y_true < 0.31, 0, np.where(y_true < 0.70, 1, 2))
        y_pred_cat = np.where(y_pred < 0.31, 0, np.where(y_pred < 0.70, 1, 2))
        return np.mean(y_true_cat == y_pred_cat)
    
    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        epochs: int = 100,
        batch_size: int = 32,
        patience: int = 10,
        verbose: bool = True
    ) -> Dict:
        """
        Train the neural network.
        
        Args:
            X_train: Training features
            y_train: Training labels (0-1 normalized risk)
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Mini-batch size
            patience: Early stopping patience
            verbose: Print progress
        
        Returns:
            Training history dict
        """
        # Normalize labels to 0-1
        y_train = np.clip(y_train / 100, 0, 1) if y_train.max() > 1 else y_train
        if y_val is not None:
            y_val = np.clip(y_val / 100, 0, 1) if y_val.max() > 1 else y_val
        
        n_samples = X_train.shape[0]
        n_batches = max(1, n_samples // batch_size)
        
        # Early stopping
        no_improve_count = 0
        
        if verbose:
            print("\n" + "=" * 80)
            print("🧠 NEURAL NETWORK TRAINING")
            print("=" * 80)
            print(f"Architecture: {self.input_dim} → {' → '.join(map(str, self.hidden_layers))} → 1")
            print(f"Training samples: {n_samples:,}")
            print(f"Batch size: {batch_size}")
            print(f"Learning rate: {self.learning_rate}")
            print(f"Early stopping patience: {patience}")
            print("-" * 80)
            print(f"{'Epoch':>6} | {'Train Loss':>12} | {'Val Loss':>12} | {'Train Acc':>10} | {'Val Acc':>10} | Status")
            print("-" * 80)
        
        for epoch in range(epochs):
            # Shuffle training data
            indices = np.random.permutation(n_samples)
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]
            
            epoch_loss = 0
            
            # Mini-batch training
            for batch_idx in range(n_batches):
                start = batch_idx * batch_size
                end = min(start + batch_size, n_samples)
                
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]
                
                # Forward pass
                output, activations = self._forward(X_batch, training=True)
                
                # Compute loss
                batch_loss = self._compute_loss(y_batch, output.flatten())
                epoch_loss += batch_loss
                
                # Backward pass
                weight_grads, bias_grads = self._backward(X_batch, y_batch, activations)
                
                # Update weights (SGD with momentum could be added)
                for i in range(len(self.weights)):
                    self.weights[i] -= self.learning_rate * weight_grads[i]
                    self.biases[i] -= self.learning_rate * bias_grads[i]
            
            # Compute epoch metrics
            train_loss = epoch_loss / n_batches
            train_pred, _ = self._forward(X_train, training=False)
            train_acc = self._compute_accuracy(y_train, train_pred.flatten())
            
            self.train_losses.append(train_loss)
            self.train_accuracies.append(train_acc)
            
            # Validation
            val_loss = 0
            val_acc = 0
            status = ""
            
            if X_val is not None:
                val_pred, _ = self._forward(X_val, training=False)
                val_loss = self._compute_loss(y_val, val_pred.flatten())
                val_acc = self._compute_accuracy(y_val, val_pred.flatten())
                
                self.val_losses.append(val_loss)
                self.val_accuracies.append(val_acc)
                
                # Early stopping check
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.best_weights = [(w.copy(), b.copy()) for w, b in zip(self.weights, self.biases)]
                    no_improve_count = 0
                    status = "✅ Best!"
                else:
                    no_improve_count += 1
                    if no_improve_count >= patience:
                        status = "🛑 Early Stop"
                        if verbose:
                            print(f"{epoch+1:>6} | {train_loss:>12.6f} | {val_loss:>12.6f} | {train_acc:>9.2%} | {val_acc:>9.2%} | {status}")
                            print("-" * 80)
                            print(f"⚠️ Early stopping at epoch {epoch+1} (no improvement for {patience} epochs)")
                        break
            
            # Print progress
            if verbose and (epoch % 5 == 0 or epoch == epochs - 1 or status):
                val_loss_str = f"{val_loss:>12.6f}" if X_val is not None else "N/A".center(12)
                val_acc_str = f"{val_acc:>9.2%}" if X_val is not None else "N/A".center(10)
                print(f"{epoch+1:>6} | {train_loss:>12.6f} | {val_loss_str} | {train_acc:>9.2%} | {val_acc_str} | {status}")
        
        # Restore best weights
        if self.best_weights:
            for i, (w, b) in enumerate(self.best_weights):
                self.weights[i] = w
                self.biases[i] = b
        
        if verbose:
            print("-" * 80)
            print(f"✅ Training complete! Best validation loss: {self.best_val_loss:.6f}")
        
        return {
            "train_losses": self.train_losses,
            "val_losses": self.val_losses,
            "train_accuracies": self.train_accuracies,
            "val_accuracies": self.val_accuracies,
            "best_val_loss": self.best_val_loss,
            "epochs_trained": len(self.train_losses)
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict risk scores (0-100)."""
        output, _ = self._forward(X, training=False)
        return (output.flatten() * 100).astype(int)
    
    def save(self, filepath: str):
        """Save model to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'weights': self.weights,
                'biases': self.biases,
                'input_dim': self.input_dim,
                'hidden_layers': self.hidden_layers,
                'train_losses': self.train_losses,
                'val_losses': self.val_losses,
                'best_val_loss': self.best_val_loss
            }, f)
        print(f"✅ Neural model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.weights = data['weights']
            self.biases = data['biases']
            self.input_dim = data['input_dim']
            self.hidden_layers = data['hidden_layers']
            self.train_losses = data.get('train_losses', [])
            self.val_losses = data.get('val_losses', [])
            self.best_val_loss = data.get('best_val_loss', float('inf'))
        print(f"✅ Neural model loaded from {filepath}")


def create_synthetic_labels(features: np.ndarray) -> np.ndarray:
    """
    Create synthetic risk labels based on feature patterns.
    Uses proper feature indices from FeatureExtractor.
    
    Feature Order (from features.py):
        0: tx_count_1m      6: max_amount        12: dust_tx_ratio
        1: tx_count_10m     7: amount_range      13: self_transfer_ratio
        2: tx_count_1h      8: unique_recipients 14: return_ratio
        3: tx_velocity      9: same_recipient    15: avg_interval
        4: mean_amount     10: fan_out_score
        5: std_amount      11: burstiness_index
    """
    n_samples = features.shape[0]
    labels = np.zeros(n_samples)
    
    for i in range(n_samples):
        f = features[i]
        risk = 0.10  # Base risk (lower starting point)
        
        # === FREQUENCY PATTERNS ===
        # High transaction count in 1 hour
        tx_1h = f[2] if len(f) > 2 else 0
        if tx_1h > 100:
            risk += 0.30  # Very high frequency
        elif tx_1h > 50:
            risk += 0.20
        elif tx_1h > 20:
            risk += 0.10
        
        # === AMOUNT PATTERNS ===
        mean_amt = f[4] if len(f) > 4 else 0
        std_amt = f[5] if len(f) > 5 else 0
        
        # Dust transactions (very small amounts)
        dust_ratio = f[12] if len(f) > 12 else 0
        if dust_ratio > 0.8:
            risk += 0.35  # Mostly dust = high risk
        elif dust_ratio > 0.5:
            risk += 0.20
        elif dust_ratio > 0.2:
            risk += 0.10
        
        # Low variance with high count = bot pattern
        if std_amt < 1.0 and tx_1h > 10:
            risk += 0.15
        
        # === RECIPIENT PATTERNS ===
        unique_recip = f[8] if len(f) > 8 else 0
        same_recip = f[9] if len(f) > 9 else 0
        fan_out = f[10] if len(f) > 10 else 0
        
        # High fan-out (many unique recipients)
        if unique_recip > 100:
            risk += 0.25
        elif unique_recip > 50:
            risk += 0.15
        
        # Always same recipient = bot-like
        if same_recip > 0.95 and tx_1h > 10:
            risk += 0.20
        
        # === SELF-TRANSFER PATTERNS ===
        self_transfer = f[13] if len(f) > 13 else 0
        return_ratio = f[14] if len(f) > 14 else 0
        
        # Self-transfers (circular)
        if self_transfer > 0.5:
            risk += 0.25
        elif self_transfer > 0.2:
            risk += 0.10
        
        # Money returning = layering
        if return_ratio > 0.5:
            risk += 0.20
        
        # === BURSTINESS ===
        burstiness = f[11] if len(f) > 11 else 0
        if burstiness > 0.5:
            risk += 0.15  # Irregular timing bursts
        
        # Clamp to valid range
        labels[i] = min(1.0, max(0.0, risk))
    
    return labels
