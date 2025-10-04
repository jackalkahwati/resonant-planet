from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional

from .validator import NormalizedProblem
from .proof import ProofPackage, ProofStep, InvariantCheck

from modulus_core.spec import ProblemSpec, SolutionPackage
from modulus_core.pipeline import solve as solve_pat


@dataclass
class ExecutionResult:
    answer: Optional[str]
    confidence: float
    fallback_used: bool
    solver_module: Optional[str] = None
    proof: Optional[Dict[str, Any]] = None
    raw_solution: Optional[SolutionPackage] = None
    serialized_package: Optional[Dict[str, Any]] = None


class SolverRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, callable] = {}

    def register(self, key: str, handler: callable) -> None:
        self._registry[key] = handler

    def get(self, key: str) -> Optional[callable]:
        return self._registry.get(key)


def _problem_spec_from_normalized(normalized: NormalizedProblem) -> ProblemSpec:
    return ProblemSpec.from_normalized(normalized)


def _pat_solver(normalized: NormalizedProblem) -> ExecutionResult:
    problem_spec = _problem_spec_from_normalized(normalized)
    package = solve_pat(problem_spec)
    serialized = package.to_serializable()

    answer_value = package.solution.objective_value
    if answer_value is None and package.solution.values:
        first_key = next(iter(package.solution.values.keys()))
        answer_value = package.solution.values[first_key]

    invariants = []
    for name, passed in package.certificate.invariants.items():
        value = package.certificate.metadata.get("invariant_values", {}).get(name)
        invariants.append(
            InvariantCheck(
                name=name,
                passed=passed,
                details={
                    "value": value,
                    "solution_snapshot": serialized["solution"]["values"],
                },
            )
        )

    proof_package = ProofPackage(
        solver="pat",
        steps=[
            ProofStep(
                description="Compile→Solve→Lift→Validate",
                artifacts={
                    "trace": serialized["trace"],
                },
            )
        ],
        invariants=invariants,
        raw_data=serialized,
    )

    return ExecutionResult(
        answer=str(answer_value) if answer_value is not None else None,
        confidence=1.0 if answer_value is not None else 0.0,
        fallback_used=False,
        solver_module="pat",
        proof=proof_package.to_dict(),
        raw_solution=package,
        serialized_package=serialized,
    )


class ExecutionController:
    def __init__(self, registry: Optional[SolverRegistry] = None) -> None:
        self.registry = registry or SolverRegistry()
        if self.registry.get("pat") is None:
            self.registry.register("pat", _pat_solver)

    def execute(self, normalized: NormalizedProblem) -> ExecutionResult:
        schema = normalized.schema
        module_hint = schema.solver_hints.get("module") if hasattr(schema, "solver_hints") else None

        solver_key = module_hint or "pat"
        solver = self.registry.get(solver_key) or self.registry.get("pat")

        return solver(normalized)
