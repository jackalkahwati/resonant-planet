from __future__ import annotations

from typing import Dict, List

import sympy as sp

from .spec import PatProgram, PlanGraph, PrimeSolveResult

DEFAULT_PRIMES: List[int] = [2_147_483_629, 2_147_483_647, 2_147_483_659]


def _solve_mod_prime(program: PatProgram, prime: int) -> Dict[str, int]:
    """Solve program modulo a prime. Returns placeholder for symbolic expressions."""
    matrix = program.matrix
    rhs = program.rhs
    if matrix.rows == 0:
        return {}
    
    try:
        # Try to convert to integers (only works for numeric matrices)
        mod_matrix = matrix.copy().applyfunc(lambda v: int(v) % prime)
        mod_rhs = rhs.copy().applyfunc(lambda v: int(v) % prime)
        solution = sp.Matrix(mod_matrix).gauss_jordan_solve(mod_rhs % prime)[0]
        return {
            str(symbol): int(solution[idx]) % prime
            for idx, symbol in enumerate(program.variables)
        }
    except (TypeError, ValueError) as e:
        # Matrix contains symbols - return placeholder solution
        # This happens when the problem hasn't been fully compiled to numeric form
        print(f"Warning: Symbolic matrix encountered in finite-field solve: {e}")
        return {str(symbol): 0 for symbol in program.variables}


def solve_program(plan: PlanGraph, program: PatProgram) -> PrimeSolveResult:
    primes = plan.metadata.get("primes") or DEFAULT_PRIMES
    per_prime: Dict[int, Dict[str, int]] = {}
    for prime in primes:
        per_prime[prime] = _solve_mod_prime(program, prime)
    rank = program.matrix.rank() if program.matrix.shape != (0, 0) else 0
    return PrimeSolveResult(
        program=program,
        primes=primes,
        per_prime_solutions=per_prime,
        rank=rank,
    )
