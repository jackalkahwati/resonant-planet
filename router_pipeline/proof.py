from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class InvariantCheck:
    name: str
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class ProofStep:
    description: str
    artifacts: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "artifacts": self.artifacts,
        }


@dataclass
class ProofPackage:
    solver: str
    steps: List[ProofStep] = field(default_factory=list)
    invariants: List[InvariantCheck] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "solver": self.solver,
            "steps": [step.to_dict() for step in self.steps],
            "invariants": [inv.to_dict() for inv in self.invariants],
            "raw_data": self.raw_data,
        }

