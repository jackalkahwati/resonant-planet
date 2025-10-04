"""Fetch open-source exoplanet spectra and light curves."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pandas as pd

from core.data_sources import fetch_kepler_lightcurve, fetch_tess_lightcurve, CONFIRMED_PLANETS


OPEN_PLANETS = {
    "Kepler-452b": {"type": "kepler"},
    "Kepler-186f": {"type": "kepler"},
    "Kepler-62f": {"type": "kepler"},
    "TRAPPIST-1e": {"type": "kepler"},
    "GJ 1214 b": {"type": "tess"},
    "K2-18b": {"type": "tess"},
}


def save_lightcurve(name: str, time, flux, flux_err, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"time": time, "flux": flux, "flux_err": flux_err})
    path = directory / f"{name.replace(' ', '_')}.csv"
    df.to_csv(path, index=False)
    return path


def fetch_kepler_planets(planets: Iterable[str], output_dir: Path) -> list[Path]:
    paths = []
    for planet in planets:
        try:
            time, flux, err = fetch_kepler_lightcurve(planet)
            paths.append(save_lightcurve(planet, time, flux, err, output_dir))
        except Exception as exc:
            print(f"⚠️  Failed to fetch {planet}: {exc}")
    return paths


def fetch_tess_planets(planets: Iterable[str], output_dir: Path) -> list[Path]:
    paths = []
    for planet in planets:
        try:
            time, flux, err = fetch_tess_lightcurve(planet)
            paths.append(save_lightcurve(planet, time, flux, err, output_dir))
        except Exception as exc:
            print(f"⚠️  Failed to fetch {planet}: {exc}")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("assets/spectra"))
    args = parser.parse_args()

    kepler_planets = [p for p, meta in OPEN_PLANETS.items() if meta["type"] == "kepler" and p in CONFIRMED_PLANETS]
    tess_planets = [p for p, meta in OPEN_PLANETS.items() if meta["type"] == "tess"]

    saved_paths: list[Path] = []
    saved_paths += fetch_kepler_planets(kepler_planets, args.output / "kepler")
    saved_paths += fetch_tess_planets(tess_planets, args.output / "tess")

    fetched_planets = [p.stem.replace("_", " ") for p in saved_paths]

    biosignatures = {
        "Kepler-452b": "none",
        "Kepler-186f": "candidate",
        "Kepler-62f": "speculative",
        "TRAPPIST-1e": "candidate",
        "GJ 1214 b": "candidate",
        "K2-18b": "claimed",
    }

    catalog = {
        "planets": fetched_planets,
        "files": [str(p) for p in saved_paths],
        "biosignatures": biosignatures,
    }
    (args.output / "catalog.json").write_text(json.dumps(catalog, indent=2))

    print("Fetched:")
    for path in saved_paths:
        print(" -", path)


if __name__ == "__main__":
    main()


