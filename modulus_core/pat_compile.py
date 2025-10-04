from __future__ import annotations

from typing import Dict, Any

import sympy as sp

from .spec import ProblemSpec, PatProgram
from . import bpr


def compile_problem(spec: ProblemSpec) -> PatProgram:
    bpr_encoding = bpr.encode_bpr(spec)

    variables = [sp.Symbol(name) for name in spec.variables]

    lhs_rows = []
    rhs_entries = []
    for eq in spec.equations:
        lhs_rows.append([eq.lhs.coeff(var) for var in variables])
        rhs_entries.append(eq.rhs)

    matrix = sp.Matrix(lhs_rows) if lhs_rows else sp.zeros(0, len(variables))
    rhs = sp.Matrix(rhs_entries) if rhs_entries else sp.zeros(0, 1)

    metadata: Dict[str, Any] = {
        "assumptions": spec.metadata.get("assumptions", []),
        "domains": spec.metadata.get("domains", []),
        "solver_hints": spec.metadata.get("solver_hints", {}),
    }

    return PatProgram(
        spec=spec,
        variables=variables,
        matrix=matrix,
        rhs=rhs,
        scale_factor=1,
        bpr=bpr_encoding,
        metadata=metadata,
    )

