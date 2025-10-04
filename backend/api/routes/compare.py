"""
Method comparison endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List
import numpy as np

from core.schemas import ComparisonRequest, ComparisonResponse, MethodMetrics

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("/", response_model=List[ComparisonResponse])
async def compare_methods(request: ComparisonRequest):
    """
    Compare baseline vs resonant methods for given candidates.

    This is a placeholder that returns mock comparisons.
    In production, this would run both pipelines and compare metrics.
    """
    comparisons = []

    for candidate_id in request.candidate_ids:
        # Mock comparison data
        # In production, actually run both methods

        baseline = MethodMetrics(
            method_name="baseline",
            precision=0.7,
            recall=0.8,
            f1_score=0.75,
            runtime_seconds=45.2,
        )

        resonant = MethodMetrics(
            method_name="resonant",
            precision=0.88,
            recall=0.92,
            f1_score=0.90,
            runtime_seconds=38.7,
        )

        improvement_factor = resonant.f1_score / max(baseline.f1_score, 1e-6)

        comparisons.append(
            ComparisonResponse(
                candidate_id=candidate_id,
                baseline_id=request.baseline_id,
                period_match=True,
                depth_match=True,
                similarity_score=float(improvement_factor),
                notes="Synthetic comparison",
                baseline=baseline,
                resonant=resonant,
                improvement_factor=improvement_factor,
            )
        )

    return comparisons
