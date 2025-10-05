"""
Job status endpoints.
"""
from fastapi import APIRouter, HTTPException

from core.schemas import JobStatus
from core.jobs import get_job_store

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """Get status of a running job."""
    job_store = get_job_store()
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        progress_pct=job["progress"],
        current_step=job["stage"],
        error=job["message"] if job["status"] == "failed" else None,
    )
