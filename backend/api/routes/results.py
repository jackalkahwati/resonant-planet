"""
Results retrieval endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List

from core.schemas import ResultsResponse, Candidate
from core.jobs import get_job_store

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/{job_id}", response_model=ResultsResponse)
async def get_results(job_id: str):
    """Get results for a completed job."""
    job_store = get_job_store()

    # Check job exists
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get candidates
    candidates_raw = job_store.get_candidates(job_id)

    # Convert to response format
    candidates = [
        Candidate(
            candidate_id=c["candidate_id"],
            probability=c["probability"],
            period_days=c["period_days"],
            t0_bjd=c["t0_bjd"],
            depth_ppm=c["depth_ppm"],
            duration_hours=c["duration_hours"],
            snr=c["snr"],
            flags=c["flags"],
            plots=c["plots"],
            rl_action=c["rl_action"],
        )
        for c in candidates_raw
    ]

    # Count by action
    accepted_count = sum(1 for c in candidates if c.rl_action == "accept")
    rejected_count = sum(1 for c in candidates if c.rl_action == "reject")
    human_review_count = sum(1 for c in candidates if c.rl_action == "human_review")

    return ResultsResponse(
        job_id=job_id,
        candidates=candidates,
        total_candidates=len(candidates),
        accepted_count=accepted_count,
        rejected_count=rejected_count,
        human_review_count=human_review_count,
    )
