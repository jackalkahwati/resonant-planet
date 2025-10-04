"""
Explainability: generate diagnostic plots for candidates.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Set matplotlib style
plt.style.use("seaborn-v0_8-darkgrid")


def plot_phase_fold(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    t0: float,
    save_path: str,
    title: Optional[str] = None,
) -> str:
    """
    Generate phase-folded light curve plot.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux
    period : float
        Period in days
    t0 : float
        Epoch
    save_path : str
        Output path for PNG
    title : str, optional
        Plot title

    Returns
    -------
    str
        Path to saved plot
    """
    # Phase fold
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
    phase = phase / period  # Normalize to [-0.5, 0.5]

    # Sort by phase
    sort_idx = np.argsort(phase)
    phase_sorted = phase[sort_idx]
    flux_sorted = flux[sort_idx]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter plot
    ax.scatter(phase_sorted, flux_sorted, s=2, alpha=0.5, c="black", label="Data")

    # Binned data for clarity
    bin_edges = np.linspace(-0.5, 0.5, 50)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_means = []

    for i in range(len(bin_edges) - 1):
        mask = (phase_sorted >= bin_edges[i]) & (phase_sorted < bin_edges[i + 1])
        if np.sum(mask) > 0:
            bin_means.append(np.median(flux_sorted[mask]))
        else:
            bin_means.append(np.nan)

    ax.plot(bin_centers, bin_means, "r-", linewidth=2, label="Binned", alpha=0.7)

    # Labels
    ax.set_xlabel("Phase", fontsize=12, fontweight="bold")
    ax.set_ylabel("Normalized Flux", fontsize=12, fontweight="bold")
    ax.set_title(title or f"Phase Fold (P = {period:.3f} d)", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Invert y-axis for transits
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved phase fold plot to {save_path}")
    return save_path


def plot_bls_periodogram(
    periods: np.ndarray,
    powers: np.ndarray,
    best_period: float,
    save_path: str,
    title: Optional[str] = None,
) -> str:
    """
    Plot BLS periodogram with best period marked.

    Parameters
    ----------
    periods : np.ndarray
        Period grid
    powers : np.ndarray
        BLS powers
    best_period : float
        Best period to mark
    save_path : str
        Output path
    title : str, optional
        Plot title

    Returns
    -------
    str
        Path to saved plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot periodogram
    ax.plot(periods, powers, "k-", linewidth=1, alpha=0.7)

    # Mark best period
    best_idx = np.argmin(np.abs(periods - best_period))
    ax.axvline(best_period, color="red", linestyle="--", linewidth=2, label=f"Best P = {best_period:.3f} d")
    ax.scatter([best_period], [powers[best_idx]], color="red", s=100, zorder=10)

    # Labels
    ax.set_xlabel("Period (days)", fontsize=12, fontweight="bold")
    ax.set_ylabel("BLS Power", fontsize=12, fontweight="bold")
    ax.set_title(title or "BLS Periodogram", fontsize=14, fontweight="bold")
    ax.set_xscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved BLS periodogram to {save_path}")
    return save_path


def plot_odd_even(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    t0: float,
    save_path: str,
    title: Optional[str] = None,
) -> str:
    """
    Plot odd vs even transits overlay.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux
    period : float
        Period
    t0 : float
        Epoch
    save_path : str
        Output path
    title : str, optional
        Plot title

    Returns
    -------
    str
        Path to saved plot
    """
    # Phase fold
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
    phase = phase / period

    # Separate odd and even
    transit_num = np.round((time - t0) / period).astype(int)

    odd_mask = transit_num % 2 == 1
    even_mask = transit_num % 2 == 0

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot odd and even separately
    ax.scatter(phase[odd_mask], flux[odd_mask], s=3, alpha=0.5, c="blue", label="Odd transits")
    ax.scatter(phase[even_mask], flux[even_mask], s=3, alpha=0.5, c="red", label="Even transits")

    # Labels
    ax.set_xlabel("Phase", fontsize=12, fontweight="bold")
    ax.set_ylabel("Normalized Flux", fontsize=12, fontweight="bold")
    ax.set_title(title or "Odd vs Even Transits", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved odd/even plot to {save_path}")
    return save_path


def plot_secondary_search(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    t0: float,
    save_path: str,
    title: Optional[str] = None,
) -> str:
    """
    Plot secondary eclipse search window.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux
    period : float
        Period
    t0 : float
        Epoch
    save_path : str
        Output path
    title : str, optional
        Plot title

    Returns
    -------
    str
        Path to saved plot
    """
    # Phase fold
    phase = ((time - t0) % period) / period

    # Sort
    sort_idx = np.argsort(phase)
    phase_sorted = phase[sort_idx]
    flux_sorted = flux[sort_idx]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot full phase
    ax.scatter(phase_sorted, flux_sorted, s=2, alpha=0.5, c="black")

    # Highlight secondary window
    secondary_mask = (phase_sorted > 0.45) & (phase_sorted < 0.55)
    ax.scatter(
        phase_sorted[secondary_mask],
        flux_sorted[secondary_mask],
        s=20,
        alpha=0.8,
        c="orange",
        label="Secondary window",
    )

    # Mark expected secondary
    ax.axvline(0.5, color="red", linestyle="--", linewidth=2, label="Expected secondary")

    # Labels
    ax.set_xlabel("Phase", fontsize=12, fontweight="bold")
    ax.set_ylabel("Normalized Flux", fontsize=12, fontweight="bold")
    ax.set_title(title or "Secondary Eclipse Search", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved secondary search plot to {save_path}")
    return save_path


def generate_all_plots(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    t0: float,
    periods_bls: Optional[np.ndarray],
    powers_bls: Optional[np.ndarray],
    output_dir: Path,
    candidate_id: str,
) -> dict:
    """
    Generate all diagnostic plots for a candidate.

    Parameters
    ----------
    time : np.ndarray
        Time values
    flux : np.ndarray
        Normalized flux
    period : float
        Best period
    t0 : float
        Epoch
    periods_bls : np.ndarray, optional
        BLS period grid
    powers_bls : np.ndarray, optional
        BLS powers
    output_dir : Path
        Output directory
    candidate_id : str
        Candidate identifier

    Returns
    -------
    dict
        Paths to generated plots
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    plots = {}

    # Phase fold
    plots["phase_fold_png"] = plot_phase_fold(
        time, flux, period, t0, str(output_dir / f"{candidate_id}_phase.png")
    )

    # BLS periodogram
    if periods_bls is not None and powers_bls is not None:
        plots["bls_png"] = plot_bls_periodogram(
            periods_bls, powers_bls, period, str(output_dir / f"{candidate_id}_bls.png")
        )
    else:
        plots["bls_png"] = None

    # Odd/even
    plots["oddeven_png"] = plot_odd_even(
        time, flux, period, t0, str(output_dir / f"{candidate_id}_oddeven.png")
    )

    # Secondary search
    plots["secondary_png"] = plot_secondary_search(
        time, flux, period, t0, str(output_dir / f"{candidate_id}_secondary.png")
    )

    return plots
