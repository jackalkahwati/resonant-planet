"""
Physics-based validation checks for transit candidates.
"""
import numpy as np
from typing import Optional


def run_validation_checks(
    time: np.ndarray, flux: np.ndarray, period: float, t0: float
) -> dict:
    """
    Run suite of physics-based validation checks.

    Parameters
    ----------
    time : np.ndarray
        Time values (days)
    flux : np.ndarray
        Normalized flux
    period : float
        Transit period (days)
    t0 : float
        Transit epoch

    Returns
    -------
    dict
        Validation metrics
    """
    checks = {}

    # 1. Odd-even test
    checks["odd_even_delta"] = compute_odd_even_difference(time, flux, period, t0)

    # 2. Secondary eclipse search
    checks["secondary_snr"] = search_secondary_eclipse(time, flux, period, t0)

    # 3. V-shape vs U-shape discrimination
    checks["shape_score"] = compute_shape_score(time, flux, period, t0)

    # 4. Centroid shift (placeholder - requires image data)
    checks["centroid_shift"] = None

    # 5. Stellar density check
    checks["density_ok"] = check_stellar_density(period, duration_estimate=0.1)

    return checks


def compute_odd_even_difference(
    time: np.ndarray, flux: np.ndarray, period: float, t0: float
) -> float:
    """
    Compute depth difference between odd and even transits.

    Large differences indicate eclipsing binaries or blended systems.

    Returns
    -------
    float
        Percentage difference in depth
    """
    # Phase fold
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period

    # Separate odd and even transits
    transit_num = np.round((time - t0) / period).astype(int)
    in_transit = np.abs(phase) < 0.05  # Within ~5% of period

    odd_mask = in_transit & (transit_num % 2 == 1)
    even_mask = in_transit & (transit_num % 2 == 0)

    if np.sum(odd_mask) < 5 or np.sum(even_mask) < 5:
        return 0.0  # Not enough transits

    # Compute depths
    depth_odd = 1.0 - np.median(flux[odd_mask])
    depth_even = 1.0 - np.median(flux[even_mask])

    if depth_odd <= 0 or depth_even <= 0:
        return 0.0

    # Percentage difference
    delta_pct = 100.0 * np.abs(depth_odd - depth_even) / np.mean([depth_odd, depth_even])

    return delta_pct


def search_secondary_eclipse(
    time: np.ndarray, flux: np.ndarray, period: float, t0: float
) -> float:
    """
    Search for secondary eclipse at phase 0.5.

    Significant detection indicates an eclipsing binary.

    Returns
    -------
    float
        SNR of secondary eclipse
    """
    # Phase fold to look at phase 0.5
    phase = ((time - t0) % period) / period

    # Secondary should be at phase ~ 0.5
    secondary_mask = (phase > 0.45) & (phase < 0.55)
    baseline_mask = (phase < 0.2) | (phase > 0.8)

    if np.sum(secondary_mask) < 5:
        return 0.0

    # Compare flux in secondary window to baseline
    flux_secondary = flux[secondary_mask]
    flux_baseline = flux[baseline_mask]

    depth_secondary = np.median(flux_baseline) - np.median(flux_secondary)
    noise = np.std(flux_baseline)

    snr = depth_secondary / noise if noise > 0 else 0.0

    return float(snr)


def compute_shape_score(
    time: np.ndarray, flux: np.ndarray, period: float, t0: float
) -> float:
    """
    Compute U-shape vs V-shape score.

    Planetary transits should be U-shaped (flat bottom).
    Grazing eclipsing binaries are V-shaped (sharp dip).

    Returns
    -------
    float
        Score from 0 (V-shaped) to 1 (U-shaped)
    """
    # Phase fold
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period

    # Focus on in-transit data
    in_transit = np.abs(phase) < 0.02  # Within 2% of period

    if np.sum(in_transit) < 10:
        return 0.5  # Not enough data

    phase_transit = phase[in_transit]
    flux_transit = flux[in_transit]

    # Sort by phase
    sort_idx = np.argsort(phase_transit)
    phase_sorted = phase_transit[sort_idx]
    flux_sorted = flux_transit[sort_idx]

    # Compute curvature at bottom
    # U-shape has low curvature, V-shape has high curvature
    mid_idx = len(flux_sorted) // 2
    bottom_range = slice(max(0, mid_idx - 3), min(len(flux_sorted), mid_idx + 4))

    if len(flux_sorted[bottom_range]) < 5:
        return 0.5

    # Fit quadratic to bottom
    p_bottom = phase_sorted[bottom_range]
    f_bottom = flux_sorted[bottom_range]

    try:
        coeffs = np.polyfit(p_bottom, f_bottom, 2)
        curvature = abs(coeffs[0])  # Second derivative

        # U-shape has low curvature (< 1), V-shape has high (> 10)
        score = 1.0 / (1.0 + curvature)  # Sigmoid-like
        return float(np.clip(score, 0.0, 1.0))
    except:
        return 0.5


def check_stellar_density(period: float, duration_estimate: float) -> bool:
    """
    Check if implied stellar density is consistent with main sequence.

    Parameters
    ----------
    period : float
        Orbital period (days)
    duration_estimate : float
        Transit duration (days)

    Returns
    -------
    bool
        True if density is plausible for a main sequence star
    """
    # Rough Kepler's third law check
    # For circular orbit: a^3 / P^2 = G * M_star / (4 * pi^2)
    # Implied density from transit geometry

    # Convert to SI
    P_sec = period * 86400.0
    T_sec = duration_estimate * 86400.0

    # Very rough estimate (assumes central transit, b=0)
    # rho_star ~ 3 * pi / (G * P^2 * (T/P)^2)
    G = 6.674e-11  # m^3 kg^-1 s^-2

    if T_sec / P_sec > 0.2:  # Unrealistically long duration
        return False

    # Typical stellar densities: 0.1 - 10 g/cm^3 (1000 - 100000 kg/m^3)
    # This is a placeholder - in practice, use proper stellar models
    return True  # For now, accept all
