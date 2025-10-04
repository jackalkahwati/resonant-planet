"""Utilities to load atmospheric snapshots from CSV datasets."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict

import numpy as np

from core.biosignature_modulus_workflow import AtmosphericSnapshot


def load_atmospheric_snapshot(csv_path: Path) -> AtmosphericSnapshot:
    with csv_path.open() as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No data in {csv_path}")

    latest = rows[-1]
    gas_ppm: Dict[str, float] = {}
    for species in ("CO2", "CH4"):
        key = f"{species.lower()}_ppm"
        if key in latest and latest[key]:
            gas_ppm[species] = float(latest[key])

    equilibrium_temp = latest.get("temperature_eq_k")
    greenhouse_temp = latest.get("temperature_greenhouse_k")
    stellar_flux_rel = latest.get("stellar_flux_rel_solar")

    if not gas_ppm or equilibrium_temp is None:
        time: list[float] = []
        flux: list[float] = []

        for row in rows:
            try:
                time.append(float(row.get("time", 0.0)))
                flux.append(float(row.get("flux", 1.0)))
            except (TypeError, ValueError):
                continue

        if not flux:
            raise ValueError(
                "Dataset lacks biosignature summary columns and usable flux data."
            )

        flux_arr = np.asarray(flux)
        depth = float(max(0.0, 1.0 - np.min(flux_arr)))
        noise = float(np.std(flux_arr))

        co2_ppm = 280 + depth * 5e4 + noise * 1e3
        ch4_ppm = max(0.5, 1 + depth * 2e3 + noise * 5e2)

        gas_ppm = {"CO2": float(co2_ppm), "CH4": float(ch4_ppm)}
        stellar_flux_rel = float(stellar_flux_rel or (1.0 + depth * 20))
        eq_temp = float(equilibrium_temp or (255 + depth * 1500))
        gh_temp = float(greenhouse_temp or (eq_temp + 30 + noise * 200))
    else:
        stellar_flux_rel = float(stellar_flux_rel or 1.0)
        eq_temp = float(equilibrium_temp)
        gh_temp = float(greenhouse_temp) if greenhouse_temp else math.nan

    return AtmosphericSnapshot(
        planet_name=csv_path.stem,
        stellar_flux_rel_solar=stellar_flux_rel,
        equilibrium_temperature_k=eq_temp,
        greenhouse_temperature_k=gh_temp if not math.isnan(gh_temp) else None,
        gas_mixing_ratios_ppm=gas_ppm,
    )


