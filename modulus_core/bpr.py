from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import sympy as sp

from .spec import ProblemSpec, BPREncoding


@dataclass
class ResonanceStencil:
    operator: str
    coefficients: Dict[str, int]
    modulus: int
    description: str | None = None


class BPREncoder:
    def encode(self, spec: ProblemSpec) -> BPREncoding:
        boundary_conditions = []
        conservation_laws: Dict[str, sp.Expr] = {}

        for name, expr in spec.invariants.items():
            if "flux" in name.lower():
                conservation_laws[name] = expr
            else:
                boundary_conditions.append(str(expr))

        phases = {var: "default" for var in spec.variables}

        metadata: Dict[str, Any] = {
            "assumptions": spec.metadata.get("assumptions", []),
            "domains": spec.metadata.get("domains", []),
        }

        return BPREncoding(
            phases=phases,
            invariants=spec.invariants,
            boundary_conditions=boundary_conditions,
            conservation_laws=conservation_laws,
            metadata=metadata,
        )


def encode_bpr(spec: ProblemSpec) -> BPREncoding:
    encoder = BPREncoder()
    return encoder.encode(spec)

