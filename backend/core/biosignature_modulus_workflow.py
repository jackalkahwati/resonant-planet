"""Modulus-integrated biosignature workflow utilities.

This module provides a light-weight bridge between existing biosignature
analysis components and the running Modulus `/solve_v2` endpoint.

It focuses on deterministic queries that we can assemble directly from
observational data (mixing ratios, stellar fluxes, etc.) and returns an
interpretable result bundle that higher-level orchestrators can consume.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class AtmosphericSnapshot:
    """Minimal set of atmospheric features for biosignature evaluation."""

    planet_name: str
    stellar_flux_rel_solar: float
    equilibrium_temperature_k: float
    greenhouse_temperature_k: Optional[float] = None
    gas_mixing_ratios_ppm: Dict[str, float] = field(default_factory=dict)


@dataclass
class BiosignatureComputation:
    """Structured response from a Modulus biosignature query."""

    metric_name: str
    value: float
    confidence: float
    trace_id: str
    explanation: str


class ModulusBiosignatureWorkflow:
    """Utility wrapper around the Modulus `/solve_v2` endpoint."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 45,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------
    def compute_gas_disequilibrium(self, gases_ppm: Dict[str, float]) -> BiosignatureComputation:
        """Evaluate log10(CO2/CH4) disequilibrium index using Modulus."""

        if "CO2" not in gases_ppm or "CH4" not in gases_ppm:
            raise ValueError("CO2 and CH4 mixing ratios are required for the disequilibrium metric")

        question = (
            "A greenhouse atmosphere contains CO2 and CH4 with the following mixing ratios in ppm:\n"
            f"- CO2: {gases_ppm['CO2']} ppm\n"
            f"- CH4: {gases_ppm['CH4']} ppm\n\n"
            "Compute the disequilibrium index defined as log10(CO2 / CH4)."
        )

        response = self._post_solve_v2(question)

        value = self._coerce_float(response.get("answer"))
        confidence = float(response.get("confidence", 0.0))
        trace_id = str(response.get("trace_id", ""))
        explanation = response.get("router", {}).get("explanation", "")

        return BiosignatureComputation(
            metric_name="log10_CO2_CH4",
            value=value,
            confidence=confidence,
            trace_id=trace_id,
            explanation=explanation or "Modulus evaluation of log10(CO2/CH4).",
        )

    def compute_greenhouse_offset(self, snapshot: AtmosphericSnapshot) -> BiosignatureComputation:
        """Compare greenhouse vs. equilibrium temperature using Modulus."""

        if snapshot.greenhouse_temperature_k is None:
            raise ValueError("Greenhouse temperature is required to compute the offset")

        question = (
            f"An exoplanet named {snapshot.planet_name} receives {snapshot.stellar_flux_rel_solar}x solar flux.\n"
            f"Its equilibrium temperature is {snapshot.equilibrium_temperature_k} K, and the observed greenhouse temperature is "
            f"{snapshot.greenhouse_temperature_k} K.\n\n"
            "Compute the greenhouse disequilibrium defined as the difference between greenhouse and equilibrium temperatures."
        )

        response = self._post_solve_v2(question)

        value = self._coerce_float(response.get("answer"))
        confidence = float(response.get("confidence", 0.0))
        trace_id = str(response.get("trace_id", ""))
        explanation = response.get("router", {}).get("explanation", "")

        return BiosignatureComputation(
            metric_name="greenhouse_temperature_offset",
            value=value,
            confidence=confidence,
            trace_id=trace_id,
            explanation=explanation or "Greenhouse-equilibrium temperature offset computed by Modulus.",
        )

    def run_composite_analysis(self, snapshot: AtmosphericSnapshot) -> List[BiosignatureComputation]:
        """Convenience method running all available Modulus computations."""

        computations: List[BiosignatureComputation] = []

        if {"CO2", "CH4"}.issubset(snapshot.gas_mixing_ratios_ppm):
            try:
                computations.append(self.compute_gas_disequilibrium(snapshot.gas_mixing_ratios_ppm))
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Failed to compute CO2/CH4 disequilibrium via Modulus: %s", exc)

        if snapshot.greenhouse_temperature_k is not None:
            try:
                computations.append(self.compute_greenhouse_offset(snapshot))
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Failed to compute greenhouse offset via Modulus: %s", exc)

        return computations

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _post_solve_v2(self, question: str) -> Dict[str, Any]:
        payload = {"question": question}
        url = f"{self.base_url}/solve_v2"
        logger.debug("Submitting Modulus solve_v2 request: %s", payload)

        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _coerce_float(raw: Optional[str]) -> float:
        if raw is None:
            return float("nan")
        try:
            return float(raw)
        except (TypeError, ValueError):
            logger.debug("Could not coerce %r to float; returning NaN", raw)
            return float("nan")


__all__ = [
    "AtmosphericSnapshot",
    "BiosignatureComputation",
    "ModulusBiosignatureWorkflow",
]


