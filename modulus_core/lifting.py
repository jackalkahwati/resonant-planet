from __future__ import annotations

from functools import reduce
from typing import Dict

import sympy as sp

from .spec import PrimeSolveResult, RationalSolution


def _crt(remainders: Dict[int, int]) -> tuple[int, int]:
    moduli = list(remainders.keys())
    total_modulus = reduce(lambda a, b: a * b, moduli, 1)
    result = 0
    for modulus, remainder in remainders.items():
        partial = total_modulus // modulus
        inverse = pow(partial, -1, modulus)
        result += remainder * partial * inverse
    return result % total_modulus, total_modulus


def lift_solution(prime_result: PrimeSolveResult) -> RationalSolution:
    variables = prime_result.program.variables
    per_prime = prime_result.per_prime_solutions

    lifted_values: Dict[str, sp.Rational] = {}
    per_var_prime_values: Dict[int, Dict[str, int]] = {
        prime: {var: vals.get(var) for var in per_prime[prime].keys()}
        for prime, vals in per_prime.items()
    }

    for symbol in variables:
        remainders = {prime: assignments.get(str(symbol), 0) for prime, assignments in per_prime.items()}
        residue, modulus_product = _crt(remainders)
        lifted_values[str(symbol)] = sp.Rational(residue, 1)

    objective_value = None
    if prime_result.program.spec.objective is not None:
        expr = prime_result.program.spec.objective
        substitutions = {sp.Symbol(name): value for name, value in lifted_values.items()}
        objective_value = expr.subs(substitutions)
        if isinstance(objective_value, (int, float)):
            objective_value = sp.Rational(objective_value)

    return RationalSolution(
        values=lifted_values,
        objective_value=objective_value,
        per_prime=prime_result.per_prime_solutions,
        modulus_product=reduce(lambda a, b: a * b, prime_result.primes, 1) if prime_result.primes else 1,
    )

