"""
Model Explainability Module
Provides feature importance explanations
"""

import numpy as np
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExoplanetExplainer:
    """
    Provides model interpretability using feature importance
    """
    
    def __init__(self, model, feature_names: List[str], class_names: List[str] = None):
        self.model = model
        self.feature_names = feature_names
        self.class_names = class_names or ['False Positive', 'Candidate', 'Confirmed']
        self.background_data = None
        
    def setup_shap(self, background_data: np.ndarray, n_samples: int = 100):
        """Store background data for feature analysis"""
        # Use a subset for efficiency
        if len(background_data) > n_samples:
            indices = np.random.choice(len(background_data), n_samples, replace=False)
            self.background_data = background_data[indices]
        else:
            self.background_data = background_data
        logger.info("Background data stored for explanations")
    
    def explain_prediction(self, X: np.ndarray, top_k: int = 10) -> Dict:
        """
        Generate explanation for a single prediction
        Returns feature contributions and confidence breakdown
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get prediction
        proba = self.model.predict_proba(X)[0]
        predicted_class = np.argmax(proba)
        
        explanation = {
            'predicted_class': int(predicted_class),
            'predicted_class_name': self.class_names[predicted_class],
            'confidence': float(proba[predicted_class]),
            'class_probabilities': {
                self.class_names[i]: float(proba[i]) 
                for i in range(len(self.class_names))
            },
            'feature_contributions': {},
            'top_features': []
        }
        
        # Use feature importance for explanation
        explanation['top_features'] = self._feature_importance_explanation(X, top_k)
        
        # Get individual model predictions for transparency
        explanation['model_breakdown'] = self._get_model_breakdown(X)
        
        return explanation
    
    def _feature_importance_explanation(self, X: np.ndarray, top_k: int) -> List[Dict]:
        """Use feature importance as explanation fallback"""
        if hasattr(self.model, 'training_metrics') and 'feature_importance' in self.model.training_metrics:
            importance = self.model.training_metrics['feature_importance']
            
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            return [
                {
                    'feature': feat,
                    'importance': float(imp),
                    'feature_value': float(X[0, self.feature_names.index(feat)]) if feat in self.feature_names else 0,
                    'direction': 'important'
                }
                for feat, imp in sorted_features
            ]
        return []
    
    def _get_model_breakdown(self, X: np.ndarray) -> Dict:
        """Get predictions from each model in the ensemble"""
        breakdown = {}
        
        if hasattr(self.model, 'get_model_predictions'):
            predictions = self.model.get_model_predictions(X)
            
            for model_name, proba in predictions.items():
                pred_class = np.argmax(proba[0])
                breakdown[model_name] = {
                    'predicted_class': self.class_names[pred_class],
                    'confidence': float(proba[0][pred_class]),
                    'probabilities': {
                        self.class_names[i]: float(proba[0][i])
                        for i in range(len(self.class_names))
                    }
                }
        
        return breakdown
    
    def batch_explain(self, X: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Generate explanations for multiple predictions"""
        explanations = []
        for i in range(len(X)):
            explanations.append(self.explain_prediction(X[i:i+1], top_k))
        return explanations
    
    def get_global_importance(self) -> Dict[str, float]:
        """Get global feature importance from the model"""
        if hasattr(self.model, 'training_metrics'):
            return self.model.training_metrics.get('feature_importance', {})
        return {}
    
    def generate_summary(self, X: np.ndarray, y_true: np.ndarray = None) -> Dict:
        """Generate summary statistics for a dataset"""
        predictions = self.model.predict(X)
        probas = self.model.predict_proba(X)
        
        summary = {
            'total_samples': len(X),
            'class_distribution': {
                self.class_names[i]: int(np.sum(predictions == i))
                for i in range(len(self.class_names))
            },
            'average_confidence': {
                self.class_names[i]: float(np.mean(probas[predictions == i, i])) if np.sum(predictions == i) > 0 else 0
                for i in range(len(self.class_names))
            },
            'high_confidence_predictions': int(np.sum(np.max(probas, axis=1) > 0.8)),
            'low_confidence_predictions': int(np.sum(np.max(probas, axis=1) < 0.5)),
        }
        
        if y_true is not None:
            from sklearn.metrics import accuracy_score, f1_score
            summary['accuracy'] = float(accuracy_score(y_true, predictions))
            summary['f1_macro'] = float(f1_score(y_true, predictions, average='macro'))
        
        return summary


# Helper functions
def format_feature_name(feature: str) -> str:
    """Convert technical feature names to human-readable format"""
    name_map = {
        'koi_period': 'Orbital Period (days)',
        'koi_duration': 'Transit Duration (hours)',
        'koi_depth': 'Transit Depth (ppm)',
        'koi_prad': 'Planet Radius (Earth radii)',
        'koi_teq': 'Equilibrium Temperature (K)',
        'koi_insol': 'Insolation Flux',
        'koi_model_snr': 'Signal-to-Noise Ratio',
        'koi_steff': 'Star Temperature (K)',
        'koi_srad': 'Star Radius (Solar radii)',
        'koi_smass': 'Star Mass (Solar masses)',
        'koi_impact': 'Impact Parameter',
        'koi_slogg': 'Surface Gravity',
        'radius_ratio': 'Planet/Star Radius Ratio',
        'transit_duty_cycle': 'Transit Duty Cycle',
        'in_habitable_zone': 'In Habitable Zone',
        'stellar_density': 'Stellar Density',
        'temp_ratio': 'Temperature Ratio',
    }
    return name_map.get(feature, feature.replace('_', ' ').title())
