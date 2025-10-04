"""Modulus API adapter operations integrated with the new workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from core.biosignature_modulus_workflow import ModulusBiosignatureWorkflow


@dataclass
class TransitFit:
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


def fit_transit(time: np.ndarray, flux: np.ndarray, flux_err: Optional[np.ndarray] = None) -> TransitFit:
    period_days = float(max(np.ptp(time) / 2.0, 1.0))
    min_idx = int(np.argmin(flux))
    depth = float(max(1.0 - flux[min_idx], 0.0))
    snr = depth * np.sqrt(len(time))

    return TransitFit(
        period_days=period_days,
        t0_bjd=float(time[min_idx]),
        depth_ppm=depth * 1e6,
        duration_hours=2.0,
        impact_parameter=0.5,
        limb_darkening=(0.3, 0.2),
        snr=snr,
        log_likelihood=-snr,
        chi2=1.0,
        success=True,
        message="Fallback Modulus fit",
    )


def run_checks(time: np.ndarray, flux: np.ndarray, period_days: float, t0_bjd: float):
    return {
        "odd_even_depth_delta_pct": 0.0,
        "secondary_eclipse_snr": 0.0,
        "v_vs_u_shape_score": 0.5,
        "centroid_shift_proxy": None,
        "stellar_density_consistent": True,
    }


def get_backend_info():
    workflow = ModulusBiosignatureWorkflow()
    return {
        "backend": "modulus_api",
        "name": "Modulus workflow integration",
        "is_mock": True,
        "has_fit_transit": True,
        "has_run_checks": True,
        "modulus_url": workflow.base_url,
    }


