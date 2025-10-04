"""
Modulus adapter: unified interface for physics-informed transit modeling.

This adapter provides a clean abstraction layer that can switch between:
- Local vendored Modulus code
- External Modulus package
- Mock implementation for testing

Set USE_LOCAL_MODULUS=true to use local vendored code.
"""
import logging
import os
from typing import TypedDict, Optional
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# Type definitions
# ============================================================================


class TransitFit(TypedDict):
    """Results from a physics-informed transit fit."""

    period_days: float
    t0_bjd: float
    depth_ppm: float
    duration_hours: float
    impact_parameter: float
    limb_darkening: tuple[float, float]
    snr: float
    log_likelihood: float
    chi2: float
    success: bool
    message: str


class PhysicsChecks(TypedDict):
    """Physics-based validation checks for vetting."""

    odd_even_depth_delta_pct: float
    secondary_eclipse_snr: float
    v_vs_u_shape_score: float
    centroid_shift_proxy: Optional[float]
    stellar_density_consistent: bool


# ============================================================================
# Backend selection
# ============================================================================


def _get_modulus_backend():
    """
    Select and import the appropriate Modulus backend.

    Priority:
    1. Modulus Universal Problem Solver API (if USE_MODULUS_API=true)
    2. Local Modulus code (if USE_LOCAL_MODULUS=true)
    3. Mock backend (for testing)
    """
    use_api = os.getenv("USE_MODULUS_API", "false").lower() == "true"
    use_local = os.getenv("USE_LOCAL_MODULUS", "true").lower() == "true"

    if use_api:
        try:
            from . import modulus_api_adapter as backend

            logger.info("✓ Using Modulus Universal Problem Solver API")
            return backend
        except ImportError as e:
            logger.warning(f"Failed to import Modulus API adapter: {e}")
            logger.info("Falling back to local backend")
            # Try local instead
            use_local = True

    if use_local:
        try:
            from . import local_modulus as backend

            logger.info("✓ Using local Modulus backend")
            return backend
        except ImportError as e:
            logger.warning(f"Failed to import local Modulus: {e}")
            logger.info("Falling back to mock backend")
            return _get_mock_backend()
    else:
        try:
            import modulus as backend

            logger.info("✓ Using external Modulus package")
            return backend
        except ImportError:
            logger.warning("External Modulus not found, using mock backend")
            return _get_mock_backend()


def _get_mock_backend():
    """Return a mock backend for testing when Modulus is unavailable."""

    class MockBackend:
        @staticmethod
        def fit_transit_mock(time, flux, flux_err=None):
            """Simple mock transit fitter for testing."""
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
                "success": True,
                "message": "Mock fit (Modulus not available)",
            }

        @staticmethod
        def run_checks_mock(time, flux, period_days, t0_bjd):
            """Simple mock checks for testing."""
            return {
                "odd_even_depth_delta_pct": 2.5,
                "secondary_eclipse_snr": 1.2,
                "v_vs_u_shape_score": 0.85,
                "centroid_shift_proxy": None,
                "stellar_density_consistent": True,
            }

    return MockBackend()


# Global backend instance
_backend = _get_modulus_backend()


# ============================================================================
# Public API
# ============================================================================


def fit_transit(
    time: np.ndarray, flux: np.ndarray, flux_err: Optional[np.ndarray] = None
) -> TransitFit:
    """
    Run a physics-informed transit fit on a light curve.

    This function wraps the Modulus transit modeling code with a stable interface.
    The backend is selected at import time based on USE_LOCAL_MODULUS.

    Parameters
    ----------
    time : np.ndarray
        Time values (BJD or relative days)
    flux : np.ndarray
        Normalized flux values (1.0 = baseline)
    flux_err : np.ndarray, optional
        Flux uncertainties (if None, estimated from scatter)

    Returns
    -------
    TransitFit
        Dictionary containing fitted parameters, SNR, and success flag

    Notes
    -----
    - Input flux should be normalized to 1.0 baseline
    - Automatically estimates uncertainties if not provided
    - Returns success=False if fit fails or is unphysical
    """
    # Ensure arrays are numpy
    time = np.asarray(time, dtype=np.float64)
    flux = np.asarray(flux, dtype=np.float64)
    if flux_err is not None:
        flux_err = np.asarray(flux_err, dtype=np.float64)

    # Call backend implementation
    if hasattr(_backend, "fit_transit"):
        result = _backend.fit_transit(time, flux, flux_err)
    else:
        # Use mock if backend doesn't have the function
        result = _backend.fit_transit_mock(time, flux, flux_err)

    return TransitFit(**result)


def run_checks(time: np.ndarray, flux: np.ndarray, period_days: float, t0_bjd: float) -> PhysicsChecks:
    """
    Compute physics-based validation checks for vetting.

    Performs rule-out tests including:
    - Odd/even transit depth comparison
    - Secondary eclipse search
    - V-shaped vs U-shaped transit discrimination
    - Centroid shift proxy (if available)
    - Stellar density consistency

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux values
    period_days : float
        Candidate period in days
    t0_bjd : float
        Transit epoch in BJD

    Returns
    -------
    PhysicsChecks
        Dictionary of validation metrics

    Notes
    -----
    - These checks help identify false positives
    - All checks are designed to be conservative (favor recall over precision)
    """
    time = np.asarray(time, dtype=np.float64)
    flux = np.asarray(flux, dtype=np.float64)

    # Call backend implementation
    if hasattr(_backend, "run_checks"):
        result = _backend.run_checks(time, flux, period_days, t0_bjd)
    else:
        # Use mock if backend doesn't have the function
        result = _backend.run_checks_mock(time, flux, period_days, t0_bjd)

    return PhysicsChecks(**result)


def get_backend_info() -> dict:
    """
    Get information about the current Modulus backend.

    Returns
    -------
    dict
        Backend name, version, and capabilities
    """
    backend_name = _backend.__class__.__name__ if hasattr(_backend, "__class__") else str(type(_backend))
    is_mock = "Mock" in backend_name

    return {
        "backend": "local" if os.getenv("USE_LOCAL_MODULUS", "true").lower() == "true" else "external",
        "name": backend_name,
        "is_mock": is_mock,
        "has_fit_transit": hasattr(_backend, "fit_transit") or hasattr(_backend, "fit_transit_mock"),
        "has_run_checks": hasattr(_backend, "run_checks") or hasattr(_backend, "run_checks_mock"),
    }
