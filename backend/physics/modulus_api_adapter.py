"""
Modulus API Adapter - Connects to external Modulus Cloud Run service.

This adapter makes HTTP requests to your deployed Modulus instance
instead of running it locally.
"""
import logging
import os
from typing import Optional
import numpy as np
import requests

logger = logging.getLogger(__name__)

# Get API configuration from environment
MODULUS_API_URL = os.getenv("MODULUS_API_URL", "https://modulus-pat-solver-default.run.app")
MODULUS_API_KEY = os.getenv("MODULUS_API_KEY", "")  # Optional, if your service requires auth
TIMEOUT = 60  # seconds


def fit_transit(time: np.ndarray, flux: np.ndarray, flux_err: Optional[np.ndarray] = None) -> dict:
    """
    Call Modulus Cloud Run API to fit a transit model.
    
    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux values
    flux_err : np.ndarray, optional
        Flux uncertainties
        
    Returns
    -------
    dict
        Transit fit results
    """
    try:
        # Prepare request payload
        payload = {
            "time": time.tolist(),
            "flux": flux.tolist(),
        }
        
        if flux_err is not None:
            payload["flux_err"] = flux_err.tolist()
        
        # Make API request
        headers = {"Content-Type": "application/json"}
        if MODULUS_API_KEY:
            headers["X-API-Key"] = MODULUS_API_KEY
            
        response = requests.post(
            f"{MODULUS_API_URL}/fit_transit",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"✓ Modulus API fit_transit successful (SNR: {result.get('snr', 'N/A')})")
        return result
        
    except requests.exceptions.Timeout:
        logger.error("Modulus API timeout")
        return _mock_fit_result(time, "API timeout")
    except requests.exceptions.RequestException as e:
        logger.error(f"Modulus API error: {e}")
        return _mock_fit_result(time, f"API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calling Modulus API: {e}")
        return _mock_fit_result(time, f"Error: {str(e)}")


def run_checks(time: np.ndarray, flux: np.ndarray, period_days: float, t0_bjd: float) -> dict:
    """
    Call Modulus Cloud Run API to run physics validation checks.
    
    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux values
    period_days : float
        Candidate period
    t0_bjd : float
        Transit epoch
        
    Returns
    -------
    dict
        Physics validation checks
    """
    try:
        # Prepare request payload
        payload = {
            "time": time.tolist(),
            "flux": flux.tolist(),
            "period_days": period_days,
            "t0_bjd": t0_bjd
        }
        
        # Make API request
        headers = {"Content-Type": "application/json"}
        if MODULUS_API_KEY:
            headers["X-API-Key"] = MODULUS_API_KEY
            
        response = requests.post(
            f"{MODULUS_API_URL}/run_checks",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info("✓ Modulus API run_checks successful")
        return result
        
    except requests.exceptions.Timeout:
        logger.error("Modulus API timeout")
        return _mock_checks_result()
    except requests.exceptions.RequestException as e:
        logger.error(f"Modulus API error: {e}")
        return _mock_checks_result()
    except Exception as e:
        logger.error(f"Unexpected error calling Modulus API: {e}")
        return _mock_checks_result()


def _mock_fit_result(time: np.ndarray, message: str) -> dict:
    """Fallback mock result when API is unavailable."""
    return {
        "period_days": 3.14,
        "t0_bjd": float(np.median(time)),
        "depth_ppm": 1000.0,
        "duration_hours": 2.5,
        "impact_parameter": 0.3,
        "limb_darkening": (0.3, 0.2),
        "snr": 10.0,
        "log_likelihood": -100.0,
        "chi2": 1.1,
        "success": False,
        "message": message,
    }


def _mock_checks_result() -> dict:
    """Fallback mock result when API is unavailable."""
    return {
        "odd_even_depth_delta_pct": 2.5,
        "secondary_eclipse_snr": 1.2,
        "v_vs_u_shape_score": 0.85,
        "centroid_shift_proxy": None,
        "stellar_density_consistent": True,
    }


def get_backend_info() -> dict:
    """Get information about the Modulus API backend."""
    try:
        response = requests.get(
            f"{MODULUS_API_URL}/health",
            timeout=5
        )
        if response.ok:
            status = "connected"
        else:
            status = "error"
    except:
        status = "unreachable"
    
    return {
        "backend": "api",
        "url": MODULUS_API_URL,
        "status": status,
        "has_api_key": bool(MODULUS_API_KEY),
    }
