from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Dict

from .schema import ProblemSchema


@dataclass
class RouterResult:
    schema: Optional[ProblemSchema]
    confidence: float
    explanation: Optional[str]
    raw_response: Dict[str, Any]


class Router:
    def __init__(self, grok_client: Optional[Any] = None) -> None:
        self.grok_client = grok_client

    def route(self, question: str, *, context: Optional[str] = None) -> RouterResult:
        schema_dict: Optional[Dict[str, Any]] = None
        explanation = None
        confidence = 0.0
        raw_response: Dict[str, Any] = {}

        if self.grok_client:
            response = self.grok_client.generate_schema(question=question, context=context)
            raw_response = response or {}
            payload = response or {}
            schema_dict = payload.get("problem_schema") if isinstance(payload, dict) else None
            confidence = float(payload.get("confidence", 0.0)) if isinstance(payload, dict) else 0.0
            explanation = payload.get("explanation") if isinstance(payload, dict) else None

        if not schema_dict:
            schema_dict = {
                "problem_id": "linear_demo",
                "domains": ["algebra"],
                "assumptions": ["Variables represent rational numbers."],
                "symbols": {
                    "x": {"unit": None, "description": "unknown"},
                },
                "parameters": {},
                "constants": {},
                "data_series": [],
                "equations": ["Eq(y - 2*x, 3)"],
                "constraints": [],
                "objective": {"type": "evaluate", "expression": "y", "at": {}},
                "verification": {},
                "solver_hints": {"module": "pat"},
            }
            explanation = "Fallback linear schema (y = 2x + 3)."
            confidence = 0.1

        schema = ProblemSchema.from_dict(schema_dict)
        return RouterResult(
            schema=schema,
            confidence=confidence,
            explanation=explanation,
            raw_response=raw_response,
        )

