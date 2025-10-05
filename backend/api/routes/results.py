"""
Results retrieval endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List

from core.schemas import ResultsResponse
from core.jobs import get_job_store

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/{job_id}", response_model=ResultsResponse)
async def get_results(job_id: str):
    """Get results for a completed job."""
    job_store = get_job_store()

    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates_raw = job_store.get_candidates(job_id)

    accepted_count = sum(1 for c in candidates_raw if c["rl_action"] == "accept")
    rejected_count = sum(1 for c in candidates_raw if c["rl_action"] == "reject")
    human_review_count = sum(1 for c in candidates_raw if c["rl_action"] == "human_review")

    return {
        "job_id": job_id,
        "candidates": candidates_raw,
        "total_candidates": len(candidates_raw),
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "human_review_count": human_review_count,
        "message": f"Found {len(candidates_raw)} candidates"
    }
