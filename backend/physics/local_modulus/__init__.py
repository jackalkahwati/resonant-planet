"""
Local Modulus backend implementation.

This module wraps the vendored Modulus code and provides the interface
expected by modulus_adapter.py.
"""
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Import local Modulus components
try:
    from .transit_model import fit_transit_parameters
    from .limb_darkening import compute_limb_darkening
    from .fits import run_validation_checks

    MODULUS_AVAILABLE = True
    logger.info("Local Modulus components loaded successfully")
except ImportError as e:
    logger.warning(f"Could not import local Modulus components: {e}")
    MODULUS_AVAILABLE = False


def fit_transit(time: np.ndarray, flux: np.ndarray, flux_err: Optional[np.ndarray] = None) -> dict:
    """
    Fit transit model using local Modulus code.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux (1.0 = baseline)
    flux_err : np.ndarray, optional
        Flux uncertainties

    Returns
    -------
    dict
        Fitted transit parameters
    """
    if not MODULUS_AVAILABLE:
        raise ImportError("Local Modulus components not available")

    try:
        # Estimate uncertainties if not provided
        if flux_err is None:
            flux_err = np.ones_like(flux) * np.std(flux)

        # Call Modulus fitter
        result = fit_transit_parameters(time, flux, flux_err)

        # Compute limb darkening
        u1, u2 = compute_limb_darkening(stellar_teff=5778.0)  # Default solar-like

        # Package results
        return {
            "period_days": result["period"],
            "t0_bjd": result["t0"],
            "depth_ppm": result["depth"] * 1e6,  # Convert to ppm
            "duration_hours": result["duration"] * 24.0,  # Convert to hours
            "impact_parameter": result["impact_param"],
            "limb_darkening": (u1, u2),
            "snr": result["snr"],
            "log_likelihood": result["log_like"],
            "chi2": result["chi2"],
            "success": result["success"],
            "message": result.get("message", "Fit completed"),
        }

    except Exception as e:
        logger.error(f"Transit fit failed: {e}")
        return {
            "period_days": 0.0,
            "t0_bjd": 0.0,
            "depth_ppm": 0.0,
            "duration_hours": 0.0,
            "impact_parameter": 0.0,
            "limb_darkening": (0.0, 0.0),
            "snr": 0.0,
            "log_likelihood": -np.inf,
            "chi2": np.inf,
            "success": False,
            "message": f"Fit failed: {str(e)}",
        }


def run_checks(time: np.ndarray, flux: np.ndarray, period_days: float, t0_bjd: float) -> dict:
    """
    Run physics-based validation checks.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux
    period_days : float
        Candidate period
    t0_bjd : float
        Transit epoch

    Returns
    -------
    dict
        Validation metrics
    """
    if not MODULUS_AVAILABLE:
        raise ImportError("Local Modulus components not available")

    try:
        checks = run_validation_checks(time, flux, period_days, t0_bjd)

        return {
            "odd_even_depth_delta_pct": checks["odd_even_delta"],
            "secondary_eclipse_snr": checks["secondary_snr"],
            "v_vs_u_shape_score": checks["shape_score"],
            "centroid_shift_proxy": checks.get("centroid_shift"),
            "stellar_density_consistent": checks["density_ok"],
        }

    except Exception as e:
        logger.error(f"Validation checks failed: {e}")
        return {
            "odd_even_depth_delta_pct": 0.0,
            "secondary_eclipse_snr": 0.0,
            "v_vs_u_shape_score": 0.0,
            "centroid_shift_proxy": None,
            "stellar_density_consistent": False,
        }
