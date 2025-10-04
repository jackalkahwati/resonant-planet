from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class SymbolInfo:
    unit: Optional[str] = None
    description: Optional[str] = None
    dimension: Optional[str] = None
    kind: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolInfo":
        return cls(
            unit=data.get("unit"),
            description=data.get("description"),
            dimension=data.get("dimension"),
            kind=data.get("kind"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit": self.unit,
            "description": self.description,
            "dimension": self.dimension,
            "kind": self.kind,
        }


@dataclass
class QuantityInfo:
    value: Optional[Any] = None
    unit: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuantityInfo":
        return cls(
            value=data.get("value"),
            unit=data.get("unit"),
            description=data.get("description"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "unit": self.unit,
            "description": self.description,
        }


@dataclass
class DataSeries:
    name: str
    description: Optional[str] = None
    columns: Dict[str, SymbolInfo] = field(default_factory=dict)
    values: Any = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSeries":
        columns = {
            key: SymbolInfo.from_dict(val)
            for key, val in (data.get("columns") or {}).items()
        }
        return cls(
            name=data.get("name", "data"),
            description=data.get("description"),
            columns=columns,
            values=data.get("values"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "columns": {k: v.to_dict() for k, v in self.columns.items()},
            "values": self.values,
        }


@dataclass
class Objective:
    type: str
    expression: str
    at: Dict[str, Any] = field(default_factory=dict)
    target: Optional[Any] = None
    tolerance: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Objective":
        return cls(
            type=data.get("type", "evaluate"),
            expression=data.get("expression", ""),
            at=dict(data.get("at", {})),
            target=data.get("target"),
            tolerance=data.get("tolerance"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "expression": self.expression,
            "at": self.at,
            "target": self.target,
            "tolerance": self.tolerance,
        }


@dataclass
class ProblemSchema:
    problem_id: str
    title: Optional[str]
    domains: List[str]
    assumptions: List[str]
    symbols: Dict[str, SymbolInfo]
    parameters: Dict[str, QuantityInfo]
    constants: Dict[str, QuantityInfo]
    data_series: List[DataSeries]
    equations: List[str]
    constraints: List[str]
    objective: Objective
    verification: Dict[str, Any]
    solver_hints: Dict[str, Any]
    pat_config: Dict[str, Any] = field(default_factory=dict)
    n_samples: int = 5

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSchema":
        symbols = {
            key: SymbolInfo.from_dict(val)
            for key, val in (data.get("symbols") or {}).items()
        }
        parameters = {
            key: QuantityInfo.from_dict(val)
            for key, val in (data.get("parameters") or {}).items()
        }
        constants = {
            key: QuantityInfo.from_dict(val)
            for key, val in (data.get("constants") or {}).items()
        }
        data_series = [DataSeries.from_dict(item) for item in data.get("data_series", [])]

        return cls(
            problem_id=data.get("problem_id", "unknown"),
            title=data.get("title"),
            domains=list(data.get("domains", [])),
            assumptions=list(data.get("assumptions", [])),
            symbols=symbols,
            parameters=parameters,
            constants=constants,
            data_series=data_series,
            equations=list(data.get("equations", [])),
            constraints=list(data.get("constraints", [])),
            objective=Objective.from_dict(data.get("objective", {})),
            verification=dict(data.get("verification", {})),
            solver_hints=dict(data.get("solver_hints", {})),
            pat_config=dict(data.get("pat_config", {})),
            n_samples=int(data.get("n_samples", 5)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "title": self.title,
            "domains": self.domains,
            "assumptions": self.assumptions,
            "symbols": {k: v.to_dict() for k, v in self.symbols.items()},
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "constants": {k: v.to_dict() for k, v in self.constants.items()},
            "data_series": [series.to_dict() for series in self.data_series],
            "equations": self.equations,
            "constraints": self.constraints,
            "objective": self.objective.to_dict(),
            "verification": self.verification,
            "solver_hints": self.solver_hints,
            "pat_config": self.pat_config,
            "n_samples": self.n_samples,
        }

