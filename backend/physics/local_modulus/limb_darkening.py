"""
Limb darkening coefficient computation.

Provides quadratic limb darkening coefficients based on stellar parameters.
"""
import numpy as np


def compute_limb_darkening(
    stellar_teff: float = 5778.0, stellar_logg: float = 4.4, stellar_feh: float = 0.0
) -> tuple[float, float]:
    """
    Compute quadratic limb darkening coefficients.

    Uses empirical relations from Claret & Bloemen (2011).

    Parameters
    ----------
    stellar_teff : float
        Effective temperature in Kelvin
    stellar_logg : float
        Surface gravity (log g)
    stellar_feh : float
        Metallicity [Fe/H]

    Returns
    -------
    tuple[float, float]
        (u1, u2) quadratic limb darkening coefficients

    Notes
    -----
    This is a simplified lookup table. For production, use proper
    interpolation from Claret tables or compute from stellar models.
    """
    # Simplified lookup for solar-like stars
    # Format: Teff range -> (u1, u2)
    ld_table = {
        (3000, 4000): (0.65, 0.15),
        (4000, 5000): (0.55, 0.20),
        (5000, 6000): (0.45, 0.25),
        (6000, 7000): (0.35, 0.30),
        (7000, 8000): (0.25, 0.30),
        (8000, 10000): (0.20, 0.25),
    }

    # Find matching range
    for (teff_min, teff_max), (u1, u2) in ld_table.items():
        if teff_min <= stellar_teff < teff_max:
            return u1, u2

    # Default to solar-like if outside range
    return 0.30, 0.20


def apply_limb_darkening(mu: np.ndarray, u1: float, u2: float) -> np.ndarray:
    """
    Apply quadratic limb darkening law.

    I(mu) / I(1) = 1 - u1 * (1 - mu) - u2 * (1 - mu)^2

    Parameters
    ----------
    mu : np.ndarray
        Cosine of angle from surface normal
    u1 : float
        Linear limb darkening coefficient
    u2 : float
        Quadratic limb darkening coefficient

    Returns
    -------
    np.ndarray
        Intensity relative to disk center
    """
    return 1.0 - u1 * (1.0 - mu) - u2 * (1.0 - mu) ** 2
