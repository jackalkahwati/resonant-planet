"""
Exoplanet AI - FastAPI Backend
NASA Space Apps Challenge 2025
Advanced ML-powered exoplanet classification system
"""

import os
import sys
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import io
import json
import logging
from datetime import datetime

from .data_pipeline import NASAExoplanetDataPipeline, data_pipeline
from .models import ExoplanetEnsemble, ensemble_model
from .explainability import ExoplanetExplainer, format_feature_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Exoplanet AI",
    description="Advanced AI/ML system for exoplanet detection and classification",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
model_state = {
    'is_trained': False,
    'dataset_type': None,
    'training_time': None,
    'metrics': {},
    'explainer': None
}

# Pydantic models for request/response
class PredictionInput(BaseModel):
    """Single prediction input"""
    features: Dict[str, float] = Field(..., description="Feature values for prediction")

class BatchPredictionInput(BaseModel):
    """Batch prediction input"""
    data: List[Dict[str, float]] = Field(..., description="List of feature dictionaries")

class TrainConfig(BaseModel):
    """Training configuration"""
    dataset: str = Field(default='kepler', description="Dataset to use: 'kepler' or 'tess'")
    test_size: float = Field(default=0.2, ge=0.1, le=0.4)
    balance_method: str = Field(default='smote', description="Balancing method: 'smote', 'undersample', 'combined', or 'none'")

class HyperparameterConfig(BaseModel):
    """Model hyperparameters"""
    xgb_n_estimators: int = Field(default=300, ge=50, le=1000)
    xgb_max_depth: int = Field(default=8, ge=3, le=15)
    xgb_learning_rate: float = Field(default=0.05, ge=0.001, le=0.3)
    lgbm_n_estimators: int = Field(default=300, ge=50, le=1000)
    lgbm_max_depth: int = Field(default=8, ge=3, le=15)
    nn_epochs: int = Field(default=100, ge=10, le=500)
    nn_batch_size: int = Field(default=64, ge=16, le=256)


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Exoplanet AI - NASA Space Apps Challenge",
        "version": "1.0.0",
        "status": "online",
        "model_trained": model_state['is_trained']
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/model/status")
async def get_model_status():
    """Get current model status and metrics"""
    return {
        "is_trained": model_state['is_trained'],
        "dataset_type": model_state['dataset_type'],
        "training_time": model_state['training_time'],
        "metrics": model_state['metrics'],
        "feature_names": ensemble_model.feature_names if model_state['is_trained'] else []
    }


@app.post("/api/model/train")
async def train_model(config: TrainConfig, background_tasks: BackgroundTasks):
    """Train the ensemble model on NASA exoplanet data"""
    global model_state
    
    try:
        logger.info(f"Starting training with config: {config}")
        start_time = datetime.now()
        
        # Prepare data
        pipeline = NASAExoplanetDataPipeline()
        data = pipeline.prepare_training_data(
            dataset=config.dataset,
            test_size=config.test_size,
            balance_method=config.balance_method if config.balance_method != 'none' else None
        )
        
        # Train model
        ensemble_model.fit(
            data['X_train'],
            data['y_train'],
            feature_names=data['feature_names']
        )
        
        # Evaluate
        metrics = ensemble_model.evaluate(
            data['X_test'],
            data['y_test'],
            class_names=data['class_names']
        )
        
        # Setup explainer
        model_state['explainer'] = ExoplanetExplainer(
            ensemble_model,
            data['feature_names'],
            data['class_names']
        )
        model_state['explainer'].setup_shap(data['X_train'][:100])
        
        # Update state
        end_time = datetime.now()
        model_state['is_trained'] = True
        model_state['dataset_type'] = config.dataset
        model_state['training_time'] = (end_time - start_time).total_seconds()
        model_state['metrics'] = metrics
        
        # Store pipeline for later use
        data_pipeline.scaler = pipeline.scaler
        data_pipeline.feature_names = pipeline.feature_names
        
        logger.info(f"Training complete! Accuracy: {metrics['accuracy']:.4f}")
        
        return {
            "status": "success",
            "message": "Model trained successfully",
            "training_time_seconds": model_state['training_time'],
            "metrics": {
                "accuracy": metrics['accuracy'],
                "f1_macro": metrics['f1_macro'],
                "roc_auc": metrics.get('roc_auc'),
                "individual_models": metrics['individual_models']
            }
        }
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.post("/api/predict")
async def predict_single(input_data: PredictionInput):
    """Make a single prediction with explanation"""
    if not model_state['is_trained']:
        raise HTTPException(status_code=400, detail="Model not trained. Call /api/model/train first.")
    
    try:
        # Convert features to array
        feature_values = []
        for feat in ensemble_model.feature_names:
            if feat in input_data.features:
                feature_values.append(input_data.features[feat])
            else:
                feature_values.append(0.0)  # Default for missing features
        
        X = np.array(feature_values).reshape(1, -1)
        
        # Scale features
        X_scaled = data_pipeline.scaler.transform(X)
        
        # Get prediction with explanation
        if model_state['explainer']:
            explanation = model_state['explainer'].explain_prediction(X_scaled)
        else:
            proba = ensemble_model.predict_proba(X_scaled)[0]
            pred_class = np.argmax(proba)
            explanation = {
                'predicted_class': int(pred_class),
                'predicted_class_name': ['False Positive', 'Candidate', 'Confirmed'][pred_class],
                'confidence': float(proba[pred_class]),
                'class_probabilities': {
                    'False Positive': float(proba[0]),
                    'Candidate': float(proba[1]),
                    'Confirmed': float(proba[2])
                }
            }
        
        return {
            "status": "success",
            "prediction": explanation
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/api/predict/batch")
async def predict_batch(input_data: BatchPredictionInput):
    """Make batch predictions"""
    if not model_state['is_trained']:
        raise HTTPException(status_code=400, detail="Model not trained. Call /api/model/train first.")
    
    try:
        # Convert to array
        X = []
        for item in input_data.data:
            feature_values = [item.get(feat, 0.0) for feat in ensemble_model.feature_names]
            X.append(feature_values)
        
        X = np.array(X)
        X_scaled = data_pipeline.scaler.transform(X)
        
        # Get predictions
        predictions = ensemble_model.predict(X_scaled)
        probabilities = ensemble_model.predict_proba(X_scaled)
        
        class_names = ['False Positive', 'Candidate', 'Confirmed']
        
        results = []
        for i in range(len(predictions)):
            results.append({
                'index': i,
                'predicted_class': int(predictions[i]),
                'predicted_class_name': class_names[predictions[i]],
                'confidence': float(probabilities[i][predictions[i]]),
                'probabilities': {
                    name: float(probabilities[i][j])
                    for j, name in enumerate(class_names)
                }
            })
        
        return {
            "status": "success",
            "total": len(results),
            "predictions": results,
            "summary": {
                'confirmed': sum(1 for r in results if r['predicted_class'] == 2),
                'candidates': sum(1 for r in results if r['predicted_class'] == 1),
                'false_positives': sum(1 for r in results if r['predicted_class'] == 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.post("/api/predict/upload")
async def predict_from_file(file: UploadFile = File(...)):
    """Upload CSV file for batch predictions"""
    if not model_state['is_trained']:
        raise HTTPException(status_code=400, detail="Model not trained. Call /api/model/train first.")
    
    try:
        # Read uploaded file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Check for required features
        available_features = [f for f in ensemble_model.feature_names if f in df.columns]
        
        if len(available_features) < len(ensemble_model.feature_names) * 0.5:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough matching features. Required: {ensemble_model.feature_names[:5]}..."
            )
        
        # Fill missing features with 0
        for feat in ensemble_model.feature_names:
            if feat not in df.columns:
                df[feat] = 0.0
        
        X = df[ensemble_model.feature_names].values
        X = np.nan_to_num(X, nan=0.0)
        X_scaled = data_pipeline.scaler.transform(X)
        
        # Get predictions
        predictions = ensemble_model.predict(X_scaled)
        probabilities = ensemble_model.predict_proba(X_scaled)
        
        class_names = ['False Positive', 'Candidate', 'Confirmed']
        
        results = []
        for i in range(len(predictions)):
            result = {
                'index': i,
                'predicted_class': int(predictions[i]),
                'predicted_class_name': class_names[predictions[i]],
                'confidence': float(probabilities[i][predictions[i]])
            }
            # Include original ID if available
            for id_col in ['kepid', 'kepoi_name', 'tid', 'toi', 'id']:
                if id_col in df.columns:
                    result['object_id'] = str(df.iloc[i][id_col])
                    break
            results.append(result)
        
        # Summary
        summary = {
            'total_analyzed': len(results),
            'confirmed_exoplanets': sum(1 for r in results if r['predicted_class'] == 2),
            'candidates': sum(1 for r in results if r['predicted_class'] == 1),
            'false_positives': sum(1 for r in results if r['predicted_class'] == 0),
            'high_confidence_confirmed': sum(
                1 for i, r in enumerate(results) 
                if r['predicted_class'] == 2 and probabilities[i][2] > 0.8
            )
        }
        
        return {
            "status": "success",
            "filename": file.filename,
            "summary": summary,
            "predictions": results[:100],  # Limit response size
            "total_predictions": len(results)
        }
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


@app.get("/api/model/metrics")
async def get_metrics():
    """Get detailed model performance metrics"""
    if not model_state['is_trained']:
        raise HTTPException(status_code=400, detail="Model not trained yet.")
    
    return {
        "status": "success",
        "metrics": model_state['metrics']
    }


@app.get("/api/model/features")
async def get_feature_importance():
    """Get feature importance rankings"""
    if not model_state['is_trained']:
        raise HTTPException(status_code=400, detail="Model not trained yet.")
    
    importance = model_state['metrics'].get('feature_importance', {})
    
    # Sort by importance
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "status": "success",
        "features": [
            {
                "name": feat,
                "display_name": format_feature_name(feat),
                "importance": imp
            }
            for feat, imp in sorted_features
        ]
    }


@app.get("/api/data/sample")
async def get_sample_data(dataset: str = "kepler", n_samples: int = 10):
    """Get sample data from NASA archive - uses cached data"""
    try:
        if dataset == "kepler":
            df = data_pipeline.fetch_kepler_data(use_cache=True)
            label_col = 'koi_pdisposition'
        else:
            df = data_pipeline.fetch_tess_data(use_cache=True)
            label_col = 'tfopwg_disp'
        
        # Sample from each class
        samples = []
        for label in df[label_col].unique():
            subset = df[df[label_col] == label].head(n_samples // 3 + 1)
            samples.append(subset)
        
        sample_df = pd.concat(samples).head(n_samples)
        
        # Replace NaN/inf with 0 for JSON serialization
        sample_df = sample_df.replace([np.inf, -np.inf], 0)
        sample_df = sample_df.fillna(0)
        
        # Convert to records and ensure all values are JSON serializable
        records = []
        for _, row in sample_df.iterrows():
            record = {}
            for col in sample_df.columns:
                val = row[col]
                if isinstance(val, (np.floating, float)):
                    if np.isnan(val) or np.isinf(val):
                        record[col] = 0
                    else:
                        record[col] = float(val)
                elif isinstance(val, (np.integer, int)):
                    record[col] = int(val)
                else:
                    record[col] = str(val) if val is not None else ""
            records.append(record)
        
        return {
            "status": "success",
            "dataset": dataset,
            "total_records": len(df),
            "sample_size": len(records),
            "columns": list(sample_df.columns),
            "data": records
        }
        
    except Exception as e:
        logger.error(f"Sample data error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sample data: {str(e)}")


@app.get("/api/data/statistics")
async def get_data_statistics(dataset: str = "kepler"):
    """Get statistics about the dataset - uses cached data"""
    try:
        # Use global data_pipeline with caching
        if dataset == "kepler":
            df = data_pipeline.fetch_kepler_data(use_cache=True)
            label_col = 'koi_pdisposition'
        else:
            df = data_pipeline.fetch_tess_data(use_cache=True)
            label_col = 'tfopwg_disp'
        
        # Class distribution
        class_dist = df[label_col].value_counts().to_dict()
        
        # Convert any NaN values to None for JSON serialization
        def clean_stats(obj):
            if isinstance(obj, dict):
                return {k: clean_stats(v) for k, v in obj.items()}
            elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            return obj
        
        return {
            "status": "success",
            "dataset": dataset,
            "total_records": len(df),
            "class_distribution": class_dist,
            "numeric_columns": 0,
            "statistics": {}
        }
        
    except Exception as e:
        logger.error(f"Statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.get("/api/exoplanets/confirmed")
async def get_confirmed_exoplanets(limit: int = 50):
    """Get list of confirmed exoplanets from Kepler - uses cached data"""
    try:
        df = data_pipeline.fetch_kepler_data(use_cache=True)
        
        confirmed = df[df['koi_pdisposition'] == 'CONFIRMED'].head(limit)
        
        # Select interesting columns
        cols = ['kepoi_name', 'koi_period', 'koi_prad', 'koi_teq', 'koi_insol', 'koi_steff']
        cols = [c for c in cols if c in confirmed.columns]
        
        def safe_float(val, default=0.0):
            try:
                f = float(val)
                return default if np.isnan(f) or np.isinf(f) else f
            except:
                return default
        
        exoplanets = []
        for _, row in confirmed[cols].iterrows():
            insol = safe_float(row.get('koi_insol', 0))
            exoplanet = {
                'name': str(row.get('kepoi_name', 'Unknown')),
                'orbital_period_days': safe_float(row.get('koi_period', 0)),
                'radius_earth': safe_float(row.get('koi_prad', 0)),
                'equilibrium_temp_k': safe_float(row.get('koi_teq', 0)),
                'insolation_flux': insol,
                'star_temp_k': safe_float(row.get('koi_steff', 0)),
                'potentially_habitable': 0.36 <= insol <= 1.1 if insol > 0 else False
            }
            exoplanets.append(exoplanet)
        
        return {
            "status": "success",
            "total_confirmed": len(df[df['koi_pdisposition'] == 'CONFIRMED']),
            "returned": len(exoplanets),
            "exoplanets": exoplanets
        }
        
    except Exception as e:
        logger.error(f"Confirmed exoplanets error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/planets/confirmed")
async def get_all_confirmed_planets(limit: int = 100, discovery_method: str = None):
    """
    Get confirmed exoplanets from the Planetary Systems TAP table
    This is the authoritative NASA source for confirmed planets
    """
    try:
        df = data_pipeline.fetch_confirmed_planets(use_cache=True)
        
        # Filter by discovery method if specified
        if discovery_method:
            df = df[df['discoverymethod'] == discovery_method]
        
        # Limit results
        df = df.head(limit)
        
        def safe_float(val, default=0.0):
            try:
                f = float(val)
                return default if np.isnan(f) or np.isinf(f) else f
            except:
                return default
        
        planets = []
        for _, row in df.iterrows():
            insol = safe_float(row.get('pl_insol', 0))
            planet = {
                'name': str(row.get('pl_name', 'Unknown')),
                'host_star': str(row.get('hostname', 'Unknown')),
                'discovery_method': str(row.get('discoverymethod', 'Unknown')),
                'discovery_year': int(safe_float(row.get('disc_year', 0))),
                'discovery_facility': str(row.get('disc_facility', 'Unknown')),
                'orbital_period_days': safe_float(row.get('pl_orbper', 0)),
                'radius_earth': safe_float(row.get('pl_rade', 0)),
                'mass_earth': safe_float(row.get('pl_bmasse', 0)),
                'semi_major_axis_au': safe_float(row.get('pl_orbsmax', 0)),
                'eccentricity': safe_float(row.get('pl_orbeccen', 0)),
                'equilibrium_temp_k': safe_float(row.get('pl_eqt', 0)),
                'insolation_flux': insol,
                'star_temp_k': safe_float(row.get('st_teff', 0)),
                'star_radius_solar': safe_float(row.get('st_rad', 0)),
                'star_mass_solar': safe_float(row.get('st_mass', 0)),
                'distance_pc': safe_float(row.get('sy_dist', 0)),
                'ra': safe_float(row.get('ra', 0)),
                'dec': safe_float(row.get('dec', 0)),
                'potentially_habitable': 0.36 <= insol <= 1.1 if insol > 0 else False,
                'num_planets_in_system': int(safe_float(row.get('sy_pnum', 1)))
            }
            planets.append(planet)
        
        # Get discovery method statistics
        method_counts = data_pipeline.data_cache.get('confirmed', df)['discoverymethod'].value_counts().to_dict()
        
        return {
            "status": "success",
            "total_confirmed": len(data_pipeline.data_cache.get('confirmed', df)),
            "returned": len(planets),
            "discovery_methods": method_counts,
            "planets": planets
        }
        
    except Exception as e:
        logger.error(f"Confirmed planets error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/planets/statistics")
async def get_planet_statistics():
    """Get comprehensive statistics about confirmed exoplanets"""
    try:
        df = data_pipeline.fetch_confirmed_planets(use_cache=True)
        
        def safe_stats(series):
            clean = series.dropna()
            if len(clean) == 0:
                return {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
            return {
                'min': float(clean.min()),
                'max': float(clean.max()),
                'mean': float(clean.mean()),
                'median': float(clean.median())
            }
        
        stats = {
            "total_planets": len(df),
            "discovery_methods": df['discoverymethod'].value_counts().to_dict(),
            "discoveries_by_year": df['disc_year'].value_counts().sort_index().to_dict(),
            "discovery_facilities": df['disc_facility'].value_counts().head(10).to_dict(),
            "orbital_period_stats": safe_stats(df['pl_orbper']),
            "radius_stats": safe_stats(df['pl_rade']),
            "mass_stats": safe_stats(df['pl_bmasse']),
            "temperature_stats": safe_stats(df['pl_eqt']),
            "potentially_habitable": len(df[(df['pl_insol'] >= 0.36) & (df['pl_insol'] <= 1.1)])
        }
        
        return {"status": "success", "statistics": stats}
        
    except Exception as e:
        logger.error(f"Planet statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/model/save")
async def save_model(path: str = "models/exoplanet_ensemble.joblib"):
    """Save the trained model"""
    if not model_state['is_trained']:
        raise HTTPException(status_code=400, detail="Model not trained yet.")
    
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else 'models', exist_ok=True)
        ensemble_model.save(path)
        return {"status": "success", "message": f"Model saved to {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save model: {str(e)}")


@app.post("/api/model/load")
async def load_model(path: str = "models/exoplanet_ensemble.joblib"):
    """Load a previously trained model"""
    global model_state
    
    try:
        ensemble_model.load(path)
        model_state['is_trained'] = True
        model_state['metrics'] = ensemble_model.training_metrics
        return {"status": "success", "message": f"Model loaded from {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
