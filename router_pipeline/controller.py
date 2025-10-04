from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from .router import Router, RouterResult
from .schema import ProblemSchema
from .validator import SchemaValidator, ValidationResult, NormalizedProblem
from .executor import ExecutionController, ExecutionResult


@dataclass
class SolveResult:
    answer: Optional[str]
    confidence: float
    proof: Optional[Dict[str, Any]]
    schema: Optional[ProblemSchema]
    validation: Optional[ValidationResult]
    normalized: Optional[NormalizedProblem]
    execution: Optional[ExecutionResult]
    router: RouterResult
    fallback_used: bool


class ProblemSolver:
    def __init__(
        self,
        router: Optional[Router] = None,
        validator: Optional[SchemaValidator] = None,
        executor: Optional[ExecutionController] = None,
    ) -> None:
        self.router = router or Router()
        self.validator = validator or SchemaValidator()
        self.executor = executor or ExecutionController()

    def solve(self, question: str, *, context: Optional[str] = None) -> SolveResult:
        router_result = self.router.route(question=question, context=context)

        if router_result.schema is None:
            return SolveResult(
                answer=None,
                confidence=0.0,
                proof=None,
                schema=None,
                validation=None,
                normalized=None,
                execution=None,
                router=router_result,
                fallback_used=True,
            )

        validation = self.validator.validate(router_result.schema)
        if not validation.accepted:
            return SolveResult(
                answer=None,
                confidence=0.0,
                proof=None,
                schema=router_result.schema,
                validation=validation,
                normalized=None,
                execution=None,
                router=router_result,
                fallback_used=True,
            )

        normalized = validation.normalized
        execution = self.executor.execute(normalized)
        return SolveResult(
            answer=execution.answer,
            confidence=execution.confidence,
            proof=execution.proof,
            schema=router_result.schema,
            validation=validation,
            normalized=normalized,
            execution=execution,
            router=router_result,
            fallback_used=execution.fallback_used,
        )
