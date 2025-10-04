from __future__ import annotations

from typing import Dict, Any, List, Tuple

import sympy as sp

from .spec import PatProgram, PlanGraph, RationalSolution, Certificate


def _residuals(program: PatProgram, solution: RationalSolution) -> Dict[str, sp.Rational]:
    substitutions = {sp.Symbol(name): value for name, value in solution.values.items()}
    residuals: Dict[str, sp.Rational] = {}
    for idx, equation in enumerate(program.spec.equations):
        residual = equation.lhs.subs(substitutions) - equation.rhs.subs(substitutions)
        residuals[f"eq_{idx}"] = sp.nsimplify(residual)
    for idx, constraint in enumerate(program.spec.constraints):
        residual = constraint.lhs.subs(substitutions) - constraint.rhs.subs(substitutions)
        residuals[f"constraint_{idx}"] = sp.nsimplify(residual)
    return residuals


def _check_invariants(program: PatProgram, solution: RationalSolution) -> Dict[str, Dict[str, Any]]:
    substitutions = {sp.Symbol(name): value for name, value in solution.values.items()}
    invariant_results: Dict[str, Dict[str, Any]] = {}
    for name, expr in program.spec.invariants.items():
        value = sp.nsimplify(expr.subs(substitutions))
        invariant_results[name] = {
            "passed": value == 0,
            "value": value,
        }
    return invariant_results


def validate(solution: RationalSolution, program: PatProgram) -> Certificate:
    residuals = _residuals(program, solution)
    invariants_info = _check_invariants(program, solution)
    invariants = {name: info["passed"] for name, info in invariants_info.items()}
    metadata: Dict[str, Any] = {
        "problem_id": program.spec.problem_id,
        "domains": program.spec.metadata.get("domains", []),
        "assumptions": program.spec.metadata.get("assumptions", []),
        "modulus_product": solution.modulus_product,
        "rank": program.matrix.rank() if program.matrix else 0,
        "invariant_values": {name: str(info["value"]) for name, info in invariants_info.items()},
    }
    return Certificate(residuals=residuals, invariants=invariants, metadata=metadata)


def explain(solution: RationalSolution, certificate: Certificate) -> str:
    lines = []
    problem_id = certificate.metadata.get("problem_id", "unknown")
    lines.append(f"Certified solution for {problem_id}:")

    domains = certificate.metadata.get("domains") or []
    if domains:
        lines.append(f"  Domains: {', '.join(domains)}")
    assumptions = certificate.metadata.get("assumptions") or []
    if assumptions:
        lines.append("  Assumptions:")
        for assumption in assumptions:
            lines.append(f"    - {assumption}")

    lines.append("  Variable assignments (exact rationals):")
    for name, value in solution.values.items():
        lines.append(f"    {name} = {sp.nsimplify(value)}")

    if solution.objective_value is not None:
        lines.append(f"  Objective value: {sp.nsimplify(solution.objective_value)}")

    lines.append("  Invariant checks:")
    invariant_values = certificate.metadata.get("invariant_values", {})
    for name, passed in certificate.invariants.items():
        status = "OK" if passed else "FAILED"
        value = invariant_values.get(name)
        value_str = f" (value={value})" if value is not None else ""
        lines.append(f"    {name}: {status}{value_str}")

    lines.append("  Residuals:")
    for name, residual in certificate.residuals.items():
        lines.append(f"    {name}: {sp.nsimplify(residual)}")

    lines.append(f"  Modulus product used for CRT: {certificate.metadata.get('modulus_product')}")
    lines.append(f"  Linear system rank: {certificate.metadata.get('rank')}")
    return "\n".join(lines)


def build_trace(
    program: PatProgram,
    plan_graph: PlanGraph,
    prime_result: Any,
    solution: RationalSolution,
    certificate: Certificate,
    timings: List[Tuple[str, float]],
) -> List[Dict[str, Any]]:
    trace: List[Dict[str, Any]] = [
        {
            "stage": "compile_to_pat",
            "variables": [str(v) for v in program.variables],
            "matrix_shape": list(program.matrix.shape),
            "domains": program.spec.metadata.get("domains", []),
            "duration_ms": _stage_duration("compile_to_pat", timings),
        },
        {
            "stage": "plan",
            "stages": plan_graph.stages,
            "metadata": plan_graph.metadata,
            "duration_ms": _stage_duration("plan", timings),
        },
        {
            "stage": "solve_over_primes",
            "primes": list(prime_result.primes),
            "per_prime_solution_sizes": {
                str(prime): len(assignments)
                for prime, assignments in prime_result.per_prime_solutions.items()
            },
            "duration_ms": _stage_duration("solve_over_primes", timings),
        },
        {
            "stage": "lift",
            "modulus_product": solution.modulus_product,
            "duration_ms": _stage_duration("lift", timings),
        },
        {
            "stage": "validate",
            "residuals": {k: str(v) for k, v in certificate.residuals.items()},
            "invariants": certificate.invariants,
            "invariant_values": certificate.metadata.get("invariant_values", {}),
            "duration_ms": _stage_duration("validate", timings),
        },
    ]
    return trace


def _stage_duration(stage: str, timings: List[Tuple[str, float]]) -> float:
    for name, duration in timings:
        if name == stage:
            return duration
    return 0.0
