from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Callable

import sympy as sp
import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    from router_pipeline.validator import NormalizedProblem

Serialized = Dict[str, Any]


@dataclass
class ResonantDeviceSpec:
    name: str
    vector_width: int
    precisions: List[str]
    memory_hierarchy: Dict[str, Any]
    concurrency: Dict[str, Any]
    instruction_latency: Dict[str, float]
    io: Dict[str, Any]
    power: Dict[str, Any]


@dataclass
class SimulatorConfig:
    timing_profile: Dict[str, float]
    memory_profile: Dict[str, Any]
    deterministic: bool = True
    seed: int = 0


class ResonantSimulator:
    def __init__(self, device_spec: ResonantDeviceSpec, config: SimulatorConfig) -> None:
        self.spec = device_spec
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    def run_kernel(self, name: str, bytes_moved: int, flops: int) -> Dict[str, Any]:
        latency_cycles = self.config.timing_profile.get(name, 1.0)
        return {
            "kernel": name,
            "cycles": latency_cycles,
            "bytes": bytes_moved,
            "flops": flops,
        }


class CPUFallback:
    def run(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)


@dataclass
class ProblemSpec:
    problem_id: str
    variables: List[str]
    equations: List[sp.Eq]
    constraints: List[sp.Eq]
    objective: sp.Expr
    objective_point: Dict[str, Any]
    parameters: Dict[str, Optional[sp.Expr]]
    constants: Dict[str, Optional[sp.Expr]]
    invariants: Dict[str, sp.Expr]
    units: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    schema_reference: Any | None = None

    @classmethod
    def from_normalized(cls, normalized: "NormalizedProblem") -> "ProblemSpec":
        schema = normalized.schema

        symbol_names = set()
        for eq in normalized.equations:
            symbol_names.update(sym.name for sym in eq.free_symbols)
        symbol_names.update(sym.name for sym in normalized.objective_expr.free_symbols)
        for name in normalized.symbol_units.keys():
            symbol_names.add(name)
        variables = sorted(symbol_names)
        symtab = {name: sp.Symbol(name) for name in variables}

        constraints: List[sp.Eq] = []
        for raw in schema.constraints or []:
            # Try to extract mathematical constraint from natural language
            # e.g., "At equilibrium, ΔG = 0" -> "ΔG = 0"
            constraint_str = raw
            if "," in raw:
                # Take the part after the last comma (likely the actual constraint)
                parts = raw.split(",")
                for part in reversed(parts):
                    if "=" in part:
                        constraint_str = part.strip()
                        break
            
            try:
                if "=" in constraint_str:
                    left, right = constraint_str.split("=", 1)
                    left_expr = sp.sympify(left.strip(), locals=symtab)
                    right_expr = sp.sympify(right.strip(), locals=symtab)
                    constraints.append(sp.Eq(left_expr, right_expr))
                else:
                    expr = sp.sympify(constraint_str.strip(), locals=symtab)
                    constraints.append(sp.Eq(expr, 0))
            except Exception as e:
                # Skip constraints that can't be parsed as symbolic math
                print(f"[ProblemSpec] Warning: Could not parse constraint '{raw}': {e}")
                continue

        invariants: Dict[str, sp.Expr] = {}
        verification = schema.verification or {}
        for key, value in verification.items():
            expr_value = value
            if isinstance(value, dict):
                expr_value = value.get("expression") or value.get("residual") or value.get("value")
            try:
                invariants[str(key)] = sp.sympify(expr_value, locals=symtab) if expr_value is not None else sp.Integer(0)
            except Exception:
                invariants[str(key)] = sp.Symbol(str(key))

        parameters: Dict[str, Optional[sp.Expr]] = {}
        for name, (value, _) in normalized.parameter_values.items():
            parameters[name] = value
        constants: Dict[str, Optional[sp.Expr]] = {}
        for name, (value, _) in normalized.constant_values.items():
            constants[name] = value

        metadata = {
            "domains": list(schema.domains or []),
            "assumptions": list(schema.assumptions or []),
            "solver_hints": dict(schema.solver_hints or {}),
            "pat_config": dict(schema.pat_config or {}),
            "data_series_count": len(schema.data_series or []),
            "objective_type": schema.objective.type if schema.objective else "solve",
        }

        return cls(
            problem_id=schema.problem_id,
            variables=variables,
            equations=list(normalized.equations),
            constraints=constraints,
            objective=normalized.objective_expr,
            objective_point=dict(normalized.objective_point),
            parameters=parameters,
            constants=constants,
            invariants=invariants,
            units=dict(normalized.symbol_units),
            metadata=metadata,
            schema_reference=schema,
        )

    def to_serializable(self) -> Serialized:
        return {
            "problem_id": self.problem_id,
            "variables": self.variables,
            "equations": [str(eq) for eq in self.equations],
            "constraints": [str(eq) for eq in self.constraints],
            "objective": str(self.objective),
            "objective_point": self.objective_point,
            "parameters": {k: str(v) if v is not None else None for k, v in self.parameters.items()},
            "constants": {k: str(v) if v is not None else None for k, v in self.constants.items()},
            "invariants": {k: str(v) for k, v in self.invariants.items()},
            "units": self.units,
            "metadata": self.metadata,
        }


@dataclass
class BPREncoding:
    phases: Dict[str, str]
    invariants: Dict[str, sp.Expr]
    boundary_conditions: List[str]
    conservation_laws: Dict[str, sp.Expr]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_serializable(self) -> Serialized:
        return {
            "phases": self.phases,
            "invariants": {k: str(v) for k, v in self.invariants.items()},
            "boundary_conditions": self.boundary_conditions,
            "conservation_laws": {k: str(v) for k, v in self.conservation_laws.items()},
            "metadata": self.metadata,
        }


@dataclass
class PatProgram:
    spec: ProblemSpec
    variables: List[sp.Symbol]
    matrix: sp.Matrix
    rhs: sp.Matrix
    scale_factor: int
    bpr: BPREncoding
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_serializable(self) -> Serialized:
        return {
            "spec": self.spec.to_serializable(),
            "variables": [str(v) for v in self.variables],
            "matrix": [[str(entry) for entry in row] for row in self.matrix.tolist()],
            "rhs": [str(entry) for entry in self.rhs],
            "scale_factor": self.scale_factor,
            "bpr": self.bpr.to_serializable(),
            "metadata": self.metadata,
        }


@dataclass
class PlanGraph:
    stages: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_serializable(self) -> Serialized:
        return {
            "stages": self.stages,
            "metadata": self.metadata,
        }


@dataclass
class PrimeSolveResult:
    program: PatProgram
    primes: List[int]
    per_prime_solutions: Dict[int, Dict[str, int]]
    rank: int

    def to_serializable(self) -> Serialized:
        return {
            "program": self.program.to_serializable(),
            "primes": self.primes,
            "per_prime_solutions": {
                str(prime): {var: int(value) for var, value in assignments.items()}
                for prime, assignments in self.per_prime_solutions.items()
            },
            "rank": self.rank,
        }


@dataclass
class RationalSolution:
    values: Dict[str, sp.Rational]
    objective_value: Optional[sp.Rational]
    per_prime: Dict[int, Dict[str, int]]
    modulus_product: int

    def to_serializable(self) -> Serialized:
        return {
            "values": {k: str(sp.nsimplify(v)) for k, v in self.values.items()},
            "objective_value": str(sp.nsimplify(self.objective_value)) if self.objective_value is not None else None,
            "per_prime": {
                str(prime): {var: int(value) for var, value in assignments.items()}
                for prime, assignments in self.per_prime.items()
            },
            "modulus_product": self.modulus_product,
        }


@dataclass
class Certificate:
    residuals: Dict[str, sp.Rational]
    invariants: Dict[str, bool]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_serializable(self) -> Serialized:
        return {
            "residuals": {k: str(sp.nsimplify(v)) for k, v in self.residuals.items()},
            "invariants": self.invariants,
            "metadata": self.metadata,
        }


@dataclass
class SolutionPackage:
    solution: RationalSolution
    certificate: Certificate
    trace: List[Dict[str, Any]]
    report: str

    def to_serializable(self) -> Serialized:
        return {
            "solution": self.solution.to_serializable(),
            "certificate": self.certificate.to_serializable(),
            "trace": self.trace,
            "report": self.report,
        }
