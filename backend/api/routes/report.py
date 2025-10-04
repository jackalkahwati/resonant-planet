"""
Report generation endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from core.settings import settings
from core.jobs import get_job_store
from core.report import generate_pdf_report

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/{job_id}")
async def get_report(job_id: str):
    """
    Generate and download PDF report for a job.
    """
    job_store = get_job_store()

    # Get job
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get candidates
    candidates = job_store.get_candidates(job_id)

    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates to report")

    # Generate report
    report_dir = settings.base_dir / settings.artifacts_dir / job_id
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"report_{job_id}.pdf"

    generate_pdf_report(
        job_id=job_id,
        candidates=candidates,
        dataset_name=job["dataset_id"],
        output_path=str(report_path),
    )

    # Return file
    return FileResponse(
        path=report_path,
        filename=f"resonant_worlds_report_{job_id}.pdf",
        media_type="application/pdf",
    )
