"""
Box Least Squares (BLS) period search and feature extraction.
"""
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BLSCandidate:
    """BLS detection candidate."""

    period: float
    t0: float
    duration: float
    depth: float
    snr: float
    power: float
    rank: int


def box_model(time: np.ndarray, period: float, t0: float, duration: float) -> np.ndarray:
    """
    Generate box-shaped transit model.

    Parameters
    ----------
    time : np.ndarray
        Time values
    period : float
        Period in days
    t0 : float
        Transit epoch
    duration : float
        Transit duration in days

    Returns
    -------
    np.ndarray
        Binary mask (1 = in transit, 0 = out of transit)
    """
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
    return (np.abs(phase) < duration / 2.0).astype(float)


def compute_bls_power(
    time: np.ndarray, flux: np.ndarray, period: float, t0: float, duration: float
) -> float:
    """
    Compute BLS power for given parameters.

    BLS power = (depth^2 * n_in * n_out) / (n_in + n_out)

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux (1.0 = baseline)
    period : float
        Test period
    t0 : float
        Test epoch
    duration : float
        Test duration

    Returns
    -------
    float
        BLS power statistic
    """
    # Generate box model
    in_transit = box_model(time, period, t0, duration)

    # Compute in-transit and out-of-transit statistics
    n_in = np.sum(in_transit)
    n_out = len(time) - n_in

    if n_in < 3 or n_out < 3:
        return 0.0

    flux_in = np.mean(flux[in_transit > 0.5])
    flux_out = np.mean(flux[in_transit < 0.5])

    depth = flux_out - flux_in

    if depth <= 0:
        return 0.0

    # BLS power (Signal Detection Efficiency)
    power = (depth**2 * n_in * n_out) / (n_in + n_out)

    return power


def bls_search(
    time: np.ndarray,
    flux: np.ndarray,
    min_period: float = 0.5,
    max_period: float = 50.0,
    n_periods: int = 10000,
    duration_grid: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run BLS period search.

    Parameters
    ----------
    time : np.ndarray
        Time values in days
    flux : np.ndarray
        Normalized flux
    min_period : float
        Minimum period to search (days)
    max_period : float
        Maximum period to search (days)
    n_periods : int
        Number of period trials
    duration_grid : np.ndarray, optional
        Duration grid to test (if None, auto-generate)

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (periods, powers) arrays
    """
    # Generate period grid (logarithmic spacing)
    periods = np.logspace(np.log10(min_period), np.log10(max_period), n_periods)

    # Duration grid (0.5% to 10% of period)
    if duration_grid is None:
        duration_fractions = np.array([0.01, 0.02, 0.05, 0.10])
    else:
        duration_fractions = duration_grid

    powers = np.zeros(len(periods))

    for i, period in enumerate(periods):
        # Search over durations
        max_power = 0.0

        for duration_frac in duration_fractions:
            duration = period * duration_frac

            # Search over phases (use a few samples per period)
            n_phase = max(3, int(period / np.median(np.diff(time))))
            phase_samples = np.linspace(0, period, min(n_phase, 20))

            for t0_offset in phase_samples:
                t0 = time[0] + t0_offset

                power = compute_bls_power(time, flux, period, t0, duration)
                max_power = max(max_power, power)

        powers[i] = max_power

    return periods, powers


def find_bls_peaks(
    periods: np.ndarray,
    powers: np.ndarray,
    n_peaks: int = 5,
    min_separation: float = 0.1,
) -> List[int]:
    """
    Find top peaks in BLS periodogram.

    Parameters
    ----------
    periods : np.ndarray
        Period values
    powers : np.ndarray
        BLS powers
    n_peaks : int
        Number of peaks to find
    min_separation : float
        Minimum fractional separation between peaks

    Returns
    -------
    List[int]
        Indices of peak periods
    """
    peak_indices = []

    # Sort by power
    sorted_indices = np.argsort(powers)[::-1]

    for idx in sorted_indices:
        if len(peak_indices) >= n_peaks:
            break

        period = periods[idx]

        # Check separation from existing peaks
        too_close = False
        for peak_idx in peak_indices:
            peak_period = periods[peak_idx]
            separation = abs(period - peak_period) / min(period, peak_period)

            if separation < min_separation:
                too_close = True
                break

        if not too_close:
            peak_indices.append(idx)

    return peak_indices


def refine_period(
    time: np.ndarray, flux: np.ndarray, period_guess: float, tolerance: float = 0.01
) -> Tuple[float, float, float, float]:
    """
    Refine period estimate using fine grid search.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux
    period_guess : float
        Initial period estimate
    tolerance : float
        Fractional tolerance for refinement

    Returns
    -------
    Tuple[float, float, float, float]
        (refined_period, best_t0, best_duration, best_depth)
    """
    # Fine grid around guess
    period_min = period_guess * (1 - tolerance)
    period_max = period_guess * (1 + tolerance)
    periods_fine = np.linspace(period_min, period_max, 100)

    best_power = 0.0
    best_params = (period_guess, time[0], 0.1, 0.01)

    # Duration grid
    duration_fractions = np.linspace(0.005, 0.15, 20)

    for period in periods_fine:
        for duration_frac in duration_fractions:
            duration = period * duration_frac

            # Phase grid
            n_phase = 10
            phases = np.linspace(0, period, n_phase)

            for t0_offset in phases:
                t0 = time[0] + t0_offset

                power = compute_bls_power(time, flux, period, t0, duration)

                if power > best_power:
                    # Compute depth
                    in_transit = box_model(time, period, t0, duration)
                    flux_in = np.mean(flux[in_transit > 0.5])
                    flux_out = np.mean(flux[in_transit < 0.5])
                    depth = flux_out - flux_in

                    best_power = power
                    best_params = (period, t0, duration, depth)

    return best_params


def extract_bls_features(
    time: np.ndarray,
    flux: np.ndarray,
    min_period: float = 0.5,
    max_period: float = 50.0,
    max_candidates: int = 5,
) -> List[BLSCandidate]:
    """
    Full BLS pipeline: search and extract top candidates.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Preprocessed, normalized flux
    min_period : float
        Minimum period (days)
    max_period : float
        Maximum period (days)
    max_candidates : int
        Maximum number of candidates to return

    Returns
    -------
    List[BLSCandidate]
        Top BLS candidates, ranked by SNR
    """
    # Run BLS search
    periods, powers = bls_search(time, flux, min_period, max_period)

    # Find peaks
    peak_indices = find_bls_peaks(periods, powers, n_peaks=max_candidates)

    # Refine and package candidates
    candidates = []

    for rank, idx in enumerate(peak_indices):
        period_guess = periods[idx]

        # Refine
        period, t0, duration, depth = refine_period(time, flux, period_guess)

        # Estimate SNR
        noise = np.std(flux)
        snr = depth / noise if noise > 0 else 0.0

        candidate = BLSCandidate(
            period=period,
            t0=t0,
            duration=duration,
            depth=depth,
            snr=snr,
            power=powers[idx],
            rank=rank + 1,
        )

        candidates.append(candidate)

    # Sort by SNR
    candidates.sort(key=lambda c: c.snr, reverse=True)

    return candidates
