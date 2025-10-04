import time
from typing import Optional, Dict, Any, List

from fastapi import FastAPI
from pydantic import BaseModel

from router_pipeline import ProblemSolver

app = FastAPI(title="Modulus Solver API")
solver = ProblemSolver()


class SolveV2Request(BaseModel):
    question: str
    context: Optional[str] = None


class SolveV2Response(BaseModel):
    answer: Optional[str]
    confidence: float
    trace_id: str
    fallback_used: bool
    router: Dict[str, Any]
    validation: Dict[str, Any]
    execution: Dict[str, Any]


@app.post("/solve_v2", response_model=SolveV2Response)
def solve_v2(req: SolveV2Request) -> SolveV2Response:
    start = time.time()
    result = solver.solve(question=req.question, context=req.context)

    router_info = {
        "confidence": result.router.confidence,
        "explanation": result.router.explanation,
        "raw_response": result.router.raw_response,
    }

    validation_info = {
        "accepted": bool(result.validation.accepted) if result.validation else False,
        "messages": result.validation.messages if result.validation else [],
    }

    execution_info = {
        "answer": result.execution.answer if result.execution else None,
        "confidence": result.execution.confidence if result.execution else 0.0,
        "solver_module": result.execution.solver_module if result.execution else None,
        "fallback_used": result.execution.fallback_used if result.execution else True,
        "proof": result.execution.proof if result.execution else None,
        "solution_package": result.execution.serialized_package if result.execution else None,
        "trace": result.execution.serialized_package.get("trace") if result.execution else None,
    }

    return SolveV2Response(
        answer=result.answer,
        confidence=result.confidence,
        trace_id=str(int(start * 1e6)),
        fallback_used=result.fallback_used,
        router=router_info,
        validation=validation_info,
        execution=execution_info,
    )
