from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import sympy as sp
from pint import UnitRegistry

from .schema import ProblemSchema


def _symbol_table(schema: ProblemSchema) -> Dict[str, sp.Symbol]:
    table: Dict[str, sp.Symbol] = {}
    for name in schema.symbols.keys():
        table[name] = sp.Symbol(name)
    return table


@dataclass
class NormalizedProblem:
    schema: ProblemSchema
    equations: List[sp.Eq]
    objective_expr: sp.Expr
    objective_point: Dict[str, Any]
    symbol_units: Dict[str, str]
    parameter_values: Dict[str, Tuple[sp.Expr, str]]
    constant_values: Dict[str, Tuple[sp.Expr, str]]


@dataclass
class ValidationResult:
    accepted: bool
    messages: List[str]
    normalized: NormalizedProblem | None


class SchemaValidator:
    def validate(self, schema: ProblemSchema) -> ValidationResult:
        messages: List[str] = []

        if not schema.equations:
            messages.append("No equations provided")
            return ValidationResult(False, messages, None)

        if not schema.objective.expression:
            messages.append("Objective expression missing")
            return ValidationResult(False, messages, None)

        ureg = UnitRegistry()
        symbol_units: Dict[str, str] = {}
        for name, info in schema.symbols.items():
            unit = info.unit
            if unit:
                try:
                    ureg.Quantity(1, unit)
                    symbol_units[name] = unit
                except Exception:
                    messages.append(f"Unknown unit '{unit}' for symbol '{name}'")
                    return ValidationResult(False, messages, None)

        parameter_values: Dict[str, Tuple[sp.Expr, str]] = {}
        for name, info in schema.parameters.items():
            unit = info.unit
            value = info.value
            if unit:
                try:
                    ureg.Quantity(1, unit)
                except Exception:
                    messages.append(f"Unknown unit '{unit}' for parameter '{name}'")
                    return ValidationResult(False, messages, None)
            try:
                expr_value = sp.sympify(value) if value is not None else None
            except Exception as exc:
                messages.append(f"Failed to parse parameter '{name}': {exc}")
                return ValidationResult(False, messages, None)
            parameter_values[name] = (expr_value, unit)

        constant_values: Dict[str, Tuple[sp.Expr, str]] = {}
        for name, info in schema.constants.items():
            unit = info.unit
            value = info.value
            if unit:
                try:
                    ureg.Quantity(1, unit)
                except Exception:
                    messages.append(f"Unknown unit '{unit}' for constant '{name}'")
                    return ValidationResult(False, messages, None)
            try:
                expr_value = sp.sympify(value) if value is not None else None
            except Exception as exc:
                messages.append(f"Failed to parse constant '{name}': {exc}")
                return ValidationResult(False, messages, None)
            constant_values[name] = (expr_value, unit)

        symtab = _symbol_table(schema)

        equations: List[sp.Eq] = []
        for raw_eq in schema.equations:
            try:
                if "=" in raw_eq:
                    left, right = raw_eq.split("=", 1)
                    eq = sp.Eq(sp.sympify(left, locals=symtab), sp.sympify(right, locals=symtab))
                else:
                    eq = sp.Eq(sp.sympify(raw_eq, locals=symtab), 0)
                equations.append(eq)
            except Exception as exc:
                messages.append(f"Failed to parse equation '{raw_eq}': {exc}")
                return ValidationResult(False, messages, None)

        try:
            objective_expr = sp.sympify(schema.objective.expression, locals=symtab)
        except Exception as exc:
            messages.append(f"Failed to parse objective expression: {exc}")
            return ValidationResult(False, messages, None)

        normalized = NormalizedProblem(
            schema=schema,
            equations=equations,
            objective_expr=objective_expr,
            objective_point=dict(schema.objective.at),
            symbol_units=symbol_units,
            parameter_values=parameter_values,
            constant_values=constant_values,
        )
        return ValidationResult(True, messages, normalized)

