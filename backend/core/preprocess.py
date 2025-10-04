"""
Light curve preprocessing and normalization.
"""
import numpy as np
from scipy.signal import medfilt, savgol_filter
from scipy.interpolate import interp1d
from typing import Optional, Tuple


def normalize_flux(flux: np.ndarray, method: str = "median") -> np.ndarray:
    """
    Normalize flux to unity baseline.

    Parameters
    ----------
    flux : np.ndarray
        Raw flux values
    method : str
        Normalization method: 'median' or 'polyfit'

    Returns
    -------
    np.ndarray
        Normalized flux (1.0 = baseline)
    """
    if method == "median":
        baseline = np.median(flux)
        return flux / baseline
    elif method == "polyfit":
        # Polynomial detrending
        x = np.arange(len(flux))
        coeffs = np.polyfit(x, flux, deg=3)
        trend = np.polyval(coeffs, x)
        return flux / trend
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def remove_outliers(
    time: np.ndarray, flux: np.ndarray, sigma_clip: float = 5.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove outliers using sigma clipping.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Flux values
    sigma_clip : float
        Number of standard deviations for clipping

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Cleaned (time, flux) arrays
    """
    median = np.median(flux)
    std = np.std(flux)

    # Identify outliers
    outlier_mask = np.abs(flux - median) < sigma_clip * std

    return time[outlier_mask], flux[outlier_mask]


def detrend_light_curve(
    time: np.ndarray, flux: np.ndarray, window_hours: float = 24.0
) -> np.ndarray:
    """
    Remove long-term trends from light curve.

    Uses median filtering to preserve transits while removing stellar variability.

    Parameters
    ----------
    time : np.ndarray
        Time values in days
    flux : np.ndarray
        Normalized flux
    window_hours : float
        Detrending window size in hours

    Returns
    -------
    np.ndarray
        Detrended flux
    """
    # Convert window to number of points
    if len(time) < 10:
        return flux

    median_dt = np.median(np.diff(time)) * 24.0  # hours
    window_points = int(window_hours / median_dt)
    window_points = max(5, min(window_points, len(flux) // 3))

    # Ensure odd window
    if window_points % 2 == 0:
        window_points += 1

    # Median filter for baseline
    baseline = medfilt(flux, kernel_size=window_points)

    # Detrend
    detrended = flux / baseline

    return detrended


def handle_gaps(
    time: np.ndarray, flux: np.ndarray, max_gap_hours: float = 12.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Identify and handle gaps in light curve.

    Parameters
    ----------
    time : np.ndarray
        Time values in days
    flux : np.ndarray
        Flux values
    max_gap_hours : float
        Maximum gap size to consider continuous

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (time, flux, gap_mask) where gap_mask indicates gap boundaries
    """
    dt = np.diff(time) * 24.0  # hours
    gaps = dt > max_gap_hours

    # Create gap mask
    gap_mask = np.zeros(len(time), dtype=bool)
    gap_mask[:-1] = gaps

    return time, flux, gap_mask


def fold_light_curve(
    time: np.ndarray, flux: np.ndarray, period: float, t0: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Phase-fold light curve at given period.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Flux values
    period : float
        Folding period in days
    t0 : float
        Reference epoch

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (phase, flux) where phase is in [-0.5, 0.5]
    """
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
    phase = phase / period  # Normalize to [-0.5, 0.5]

    # Sort by phase
    sort_idx = np.argsort(phase)

    return phase[sort_idx], flux[sort_idx]


def bin_light_curve(
    time: np.ndarray, flux: np.ndarray, bin_size_minutes: float = 30.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Bin light curve to reduce noise.

    Parameters
    ----------
    time : np.ndarray
        Time values in days
    flux : np.ndarray
        Flux values
    bin_size_minutes : float
        Bin size in minutes

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (binned_time, binned_flux, binned_err)
    """
    bin_size_days = bin_size_minutes / (24.0 * 60.0)

    # Create bins
    time_min, time_max = time.min(), time.max()
    bins = np.arange(time_min, time_max + bin_size_days, bin_size_days)

    # Compute bin indices
    bin_indices = np.digitize(time, bins)

    # Compute binned values
    binned_time = []
    binned_flux = []
    binned_err = []

    for i in range(1, len(bins)):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            binned_time.append(np.mean(time[mask]))
            binned_flux.append(np.mean(flux[mask]))
            binned_err.append(np.std(flux[mask]) / np.sqrt(np.sum(mask)))

    return np.array(binned_time), np.array(binned_flux), np.array(binned_err)


def estimate_noise(flux: np.ndarray, method: str = "mad") -> float:
    """
    Estimate noise level in light curve.

    Parameters
    ----------
    flux : np.ndarray
        Normalized flux
    method : str
        'mad' (median absolute deviation) or 'std' (standard deviation)

    Returns
    -------
    float
        Estimated noise level
    """
    if method == "mad":
        mad = np.median(np.abs(flux - np.median(flux)))
        # Convert MAD to equivalent std
        return 1.4826 * mad
    elif method == "std":
        return np.std(flux)
    else:
        raise ValueError(f"Unknown noise estimation method: {method}")


def preprocess_pipeline(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: Optional[np.ndarray] = None,
    sigma_clip: float = 5.0,
    detrend_window_hours: float = 24.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Full preprocessing pipeline.

    Steps:
    1. Normalize flux
    2. Remove outliers
    3. Detrend
    4. Estimate uncertainties

    Parameters
    ----------
    time : np.ndarray
        Time values in days
    flux : np.ndarray
        Raw flux values
    flux_err : np.ndarray, optional
        Flux uncertainties (estimated if not provided)
    sigma_clip : float
        Sigma clipping threshold
    detrend_window_hours : float
        Detrending window in hours

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (time, flux, flux_err) preprocessed arrays
    """
    # Normalize
    flux_norm = normalize_flux(flux, method="median")

    # Remove outliers
    time_clean, flux_clean = remove_outliers(time, flux_norm, sigma_clip=sigma_clip)

    # Detrend
    flux_detrended = detrend_light_curve(time_clean, flux_clean, window_hours=detrend_window_hours)

    # Estimate uncertainties if not provided
    if flux_err is None:
        noise = estimate_noise(flux_detrended, method="mad")
        flux_err_clean = np.ones_like(flux_detrended) * noise
    else:
        # Interpolate flux_err to match cleaned time
        if len(flux_err) == len(flux):
            interp_func = interp1d(
                time, flux_err, kind="nearest", fill_value="extrapolate", bounds_error=False
            )
            flux_err_clean = interp_func(time_clean)
        else:
            noise = estimate_noise(flux_detrended, method="mad")
            flux_err_clean = np.ones_like(flux_detrended) * noise

    return time_clean, flux_detrended, flux_err_clean
