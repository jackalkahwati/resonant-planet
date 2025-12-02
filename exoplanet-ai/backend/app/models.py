"""
Advanced ML Models for Exoplanet Classification
Implements ensemble learning with XGBoost, LightGBM, CatBoost
Plus neural network with attention mechanism
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.ensemble import VotingClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import joblib
from typing import Dict, Tuple, Optional, List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttentionBlock(nn.Module):
    """Self-attention mechanism for feature importance"""
    def __init__(self, input_dim: int, num_heads: int = 4):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = input_dim // num_heads
        
        self.query = nn.Linear(input_dim, input_dim)
        self.key = nn.Linear(input_dim, input_dim)
        self.value = nn.Linear(input_dim, input_dim)
        self.out = nn.Linear(input_dim, input_dim)
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # Reshape for multi-head attention
        q = self.query(x).view(batch_size, 1, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.key(x).view(batch_size, 1, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.value(x).view(batch_size, 1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / np.sqrt(self.head_dim)
        attn_weights = F.softmax(scores, dim=-1)
        
        # Apply attention
        attn_output = torch.matmul(attn_weights, v)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1)
        
        return self.out(attn_output), attn_weights


class ExoplanetNeuralNet(nn.Module):
    """
    Deep Neural Network with Attention for Exoplanet Classification
    Architecture inspired by latest transformer research for tabular data
    """
    def __init__(self, input_dim: int, num_classes: int = 3, hidden_dims: List[int] = None):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [256, 128, 64]
        
        # Input embedding
        self.input_norm = nn.BatchNorm1d(input_dim)
        self.input_proj = nn.Linear(input_dim, hidden_dims[0])
        
        # Self-attention layer
        self.attention = AttentionBlock(hidden_dims[0], num_heads=4)
        
        # Deep layers with residual connections
        self.layers = nn.ModuleList()
        self.norms = nn.ModuleList()
        
        for i in range(len(hidden_dims) - 1):
            self.layers.append(nn.Sequential(
                nn.Linear(hidden_dims[i], hidden_dims[i+1]),
                nn.GELU(),
                nn.Dropout(0.3)
            ))
            self.norms.append(nn.LayerNorm(hidden_dims[i+1]))
        
        # Output layer
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dims[-1], 32),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes)
        )
        
        self.attention_weights = None
        
    def forward(self, x):
        # Input processing
        x = self.input_norm(x)
        x = F.gelu(self.input_proj(x))
        
        # Self-attention
        x, self.attention_weights = self.attention(x)
        
        # Deep layers
        for layer, norm in zip(self.layers, self.norms):
            x = layer(x)
            x = norm(x)
        
        # Classification
        return self.classifier(x)
    
    def get_attention_weights(self):
        return self.attention_weights


class NeuralNetClassifier:
    """Wrapper for PyTorch neural network"""
    def __init__(self, input_dim: int, num_classes: int = 3, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ExoplanetNeuralNet(input_dim, num_classes).to(self.device)
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, batch_size: int = 64, lr: float = 0.001):
        """Train the neural network"""
        self.model.train()
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.LongTensor(y).to(self.device)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Optimizer with weight decay
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        
        # Class weights for imbalanced data
        class_counts = np.bincount(y.astype(int))
        class_weights = 1.0 / class_counts
        class_weights = class_weights / class_weights.sum() * len(class_weights)
        weight_tensor = torch.FloatTensor(class_weights).to(self.device)
        
        criterion = nn.CrossEntropyLoss(weight=weight_tensor)
        
        best_loss = float('inf')
        patience_counter = 0
        patience = 15
        
        for epoch in range(epochs):
            total_loss = 0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                total_loss += loss.item()
            
            scheduler.step()
            avg_loss = total_loss / len(dataloader)
            
            # Early stopping
            if avg_loss < best_loss:
                best_loss = avg_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break
            
            if (epoch + 1) % 20 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            outputs = self.model(X_tensor)
            predictions = torch.argmax(outputs, dim=1)
            return predictions.cpu().numpy()
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            outputs = self.model(X_tensor)
            probs = F.softmax(outputs, dim=1)
            return probs.cpu().numpy()


class ExoplanetEnsemble:
    """
    Advanced Ensemble Model combining:
    - XGBoost (gradient boosting)
    - LightGBM (fast gradient boosting)
    - CatBoost (handles categorical features)
    - Neural Network with Attention
    - Random Forest (bagging)
    
    Uses soft voting with optimized weights
    """
    
    def __init__(self, input_dim: int = None, num_classes: int = 3):
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.models = {}
        self.weights = {'xgb': 0.35, 'lgbm': 0.35, 'gb': 0.15, 'rf': 0.15}
        self.is_fitted = False
        self.feature_names = []
        self.training_metrics = {}
        
    def _init_models(self):
        """Initialize all models with optimized hyperparameters"""
        
        # XGBoost - excellent for structured data
        self.models['xgb'] = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
            eval_metric='mlogloss'
        )
        
        # LightGBM - fast and efficient
        self.models['lgbm'] = LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            num_leaves=63,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_samples=20,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        
        # Gradient Boosting - robust baseline
        self.models['gb'] = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        # Random Forest - ensemble diversity
        self.models['rf'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        
        # Neural Network disabled for faster training on CPU
        # Can be re-enabled with GPU support
        # if self.input_dim:
        #     self.models['nn'] = NeuralNetClassifier(self.input_dim, self.num_classes)
    
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None):
        """Train all models in the ensemble"""
        self.input_dim = X.shape[1]
        self.feature_names = feature_names or [f'feature_{i}' for i in range(X.shape[1])]
        
        self._init_models()
        
        logger.info("Training ensemble models...")
        
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            model.fit(X, y)
        
        self.is_fitted = True
        logger.info("Ensemble training complete!")
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make weighted ensemble predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
        
        # Get probability predictions from all models
        proba_sum = np.zeros((X.shape[0], self.num_classes))
        
        for name, model in self.models.items():
            proba = model.predict_proba(X)
            proba_sum += proba * self.weights[name]
        
        return np.argmax(proba_sum, axis=1)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble probability predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
        
        proba_sum = np.zeros((X.shape[0], self.num_classes))
        
        for name, model in self.models.items():
            proba = model.predict_proba(X)
            proba_sum += proba * self.weights[name]
        
        return proba_sum
    
    def evaluate(self, X: np.ndarray, y: np.ndarray, class_names: List[str] = None) -> Dict:
        """Comprehensive model evaluation"""
        y_pred = self.predict(X)
        y_proba = self.predict_proba(X)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision_macro': precision_score(y, y_pred, average='macro', zero_division=0),
            'recall_macro': recall_score(y, y_pred, average='macro', zero_division=0),
            'f1_macro': f1_score(y, y_pred, average='macro', zero_division=0),
            'precision_per_class': precision_score(y, y_pred, average=None, zero_division=0).tolist(),
            'recall_per_class': recall_score(y, y_pred, average=None, zero_division=0).tolist(),
            'f1_per_class': f1_score(y, y_pred, average=None, zero_division=0).tolist(),
            'confusion_matrix': confusion_matrix(y, y_pred).tolist(),
        }
        
        # ROC AUC for multi-class
        try:
            metrics['roc_auc'] = roc_auc_score(y, y_proba, multi_class='ovr', average='macro')
        except:
            metrics['roc_auc'] = None
        
        # Per-model performance
        individual_metrics = {}
        for name, model in self.models.items():
            if name == 'nn':
                pred = model.predict(X)
            else:
                pred = model.predict(X)
            individual_metrics[name] = {
                'accuracy': accuracy_score(y, pred),
                'f1_macro': f1_score(y, pred, average='macro', zero_division=0)
            }
        
        metrics['individual_models'] = individual_metrics
        
        # Feature importance (average across tree-based models)
        feature_importance = self._get_feature_importance()
        metrics['feature_importance'] = feature_importance
        
        self.training_metrics = metrics
        return metrics
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Calculate average feature importance from tree-based models"""
        importance_sum = np.zeros(len(self.feature_names))
        count = 0
        
        for name in ['xgb', 'lgbm', 'rf', 'gb']:
            if name in self.models:
                model = self.models[name]
                if hasattr(model, 'feature_importances_'):
                    importance_sum += model.feature_importances_
                    count += 1
        
        if count > 0:
            avg_importance = importance_sum / count
            return dict(zip(self.feature_names, avg_importance.tolist()))
        return {}
    
    def get_model_predictions(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """Get predictions from each individual model"""
        predictions = {}
        for name, model in self.models.items():
            if name == 'nn':
                predictions[name] = model.predict_proba(X)
            else:
                predictions[name] = model.predict_proba(X)
        return predictions
    
    def save(self, path: str):
        """Save ensemble model"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        # Save sklearn models
        sklearn_models = {k: v for k, v in self.models.items() if k != 'nn'}
        joblib.dump({
            'sklearn_models': sklearn_models,
            'weights': self.weights,
            'feature_names': self.feature_names,
            'training_metrics': self.training_metrics,
            'input_dim': self.input_dim,
            'num_classes': self.num_classes
        }, path)
        
        # Save neural network separately
        if 'nn' in self.models:
            nn_path = path.replace('.joblib', '_nn.pt')
            torch.save(self.models['nn'].model.state_dict(), nn_path)
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load ensemble model"""
        data = joblib.load(path)
        
        self.weights = data['weights']
        self.feature_names = data['feature_names']
        self.training_metrics = data['training_metrics']
        self.input_dim = data['input_dim']
        self.num_classes = data['num_classes']
        
        self.models = data['sklearn_models']
        
        # Load neural network
        nn_path = path.replace('.joblib', '_nn.pt')
        if os.path.exists(nn_path):
            self.models['nn'] = NeuralNetClassifier(self.input_dim, self.num_classes)
            self.models['nn'].model.load_state_dict(torch.load(nn_path, map_location='cpu'))
            self.models['nn'].is_fitted = True
        
        self.is_fitted = True
        logger.info(f"Model loaded from {path}")
        return self


# Singleton model instance
ensemble_model = ExoplanetEnsemble()
