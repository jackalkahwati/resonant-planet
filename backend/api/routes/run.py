"""
Run detection pipeline endpoints.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import time

from core.settings import settings
from core.schemas import RunParams, JobStatus
from core.jobs import get_job_store
from core.preprocess import preprocess_pipeline
from core.features_bls import extract_bls_features
from core.embeddings_qwen import get_qwen_embeddings
from core.rl_policy import get_policy
from core.explain import generate_all_plots
from physics import fit_transit, run_checks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/run", tags=["run"])


def load_light_curve(dataset_id: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load light curve from dataset ID.

    Returns
    -------
    tuple
        (time, flux, flux_err) arrays
    """
    # Check demo datasets
    demo_file = settings.base_dir / settings.demo_datasets_path / f"{dataset_id}.csv"
    upload_file = settings.base_dir / settings.upload_dir / f"{dataset_id}.csv"
    
    # Also check for files starting with dataset_id (for NASA fetched data)
    upload_dir = settings.base_dir / settings.upload_dir
    if upload_dir.exists():
        import glob
        pattern = str(upload_dir / f"{dataset_id}*.csv")
        matches = glob.glob(pattern)
        if matches:
            upload_file = Path(matches[0])

    if demo_file.exists():
        df = pd.read_csv(demo_file)
    elif upload_file.exists():
        df = pd.read_csv(upload_file)
    else:
        raise FileNotFoundError(f"Dataset {dataset_id} not found")

    # Extract columns
    time = df.iloc[:, 0].values
    flux = df.iloc[:, 1].values
    flux_err = df.iloc[:, 2].values if len(df.columns) > 2 else None

    return time, flux, flux_err


def run_detection_pipeline(job_id: str, dataset_id: str, params: dict):
    """
    Execute the full detection pipeline.

    This runs as a background task.
    """
    job_store = get_job_store()

    try:
        # Update status
        job_store.update_job(job_id, status="running", progress=5.0, stage="loading", message="Loading data")

        # Load data
        time, flux, flux_err = load_light_curve(dataset_id)

        logger.info(f"[Job {job_id}] Loaded {len(time)} points")

        # Preprocess
        job_store.update_job(job_id, progress=15.0, stage="preprocessing", message="Preprocessing light curve")

        time_clean, flux_clean, flux_err_clean = preprocess_pipeline(time, flux, flux_err)

        logger.info(f"[Job {job_id}] Preprocessed to {len(time_clean)} points")

        # BLS search
        job_store.update_job(
            job_id, progress=30.0, stage="bls_search", message="Running BLS period search"
        )

        bls_candidates = extract_bls_features(
            time_clean,
            flux_clean,
            min_period=params.get("min_period_days", 0.5),
            max_period=params.get("max_period_days", 50.0),
            max_candidates=params.get("max_candidates", 10),
        )

        logger.info(f"[Job {job_id}] Found {len(bls_candidates)} BLS candidates")

        # Filter by SNR
        min_snr = params.get("min_snr", 7.0)
        bls_candidates = [c for c in bls_candidates if c.snr >= min_snr]

        logger.info(f"[Job {job_id}] {len(bls_candidates)} candidates pass SNR threshold")

        # Process each candidate
        candidates = []
        qwen = get_qwen_embeddings(weights_path=str(settings.base_dir / settings.qwen_weights_path))
        policy = get_policy(config_path=str(settings.base_dir / settings.rl_policy_path))

        for i, bls_cand in enumerate(bls_candidates):
            progress = 40.0 + 50.0 * (i + 1) / len(bls_candidates)
            job_store.update_job(
                job_id,
                progress=progress,
                stage="candidate_analysis",
                message=f"Analyzing candidate {i+1}/{len(bls_candidates)}",
            )

            # Transit fit
            transit_fit = fit_transit(time_clean, flux_clean, flux_err_clean)

            if not transit_fit["success"]:
                logger.warning(f"[Job {job_id}] Transit fit failed for candidate {i+1}")
                continue

            # Physics checks
            physics_checks = run_checks(time_clean, flux_clean, bls_cand.period, bls_cand.t0)

            # Qwen embedding
            embedding = qwen.embed(time_clean, flux_clean)

            # Combine features and compute probability
            # For now, use a simple heuristic (in production, use trained classifier)
            probability = min(0.99, max(0.01, bls_cand.snr / 20.0))

            # RL policy decision
            flags = {
                "odd_even_ok": physics_checks["odd_even_depth_delta_pct"] < 10.0,
                "secondary_low": physics_checks["secondary_eclipse_snr"] < 3.0,
                "shape_u_like": physics_checks["v_vs_u_shape_score"] > 0.6,
                "density_consistent": physics_checks["stellar_density_consistent"],
            }

            rl_action = policy.predict_action(probability, bls_cand.snr, flags)

            # Generate plots
            candidate_id = f"{job_id}_{i+1}"
            plots_dir = settings.base_dir / settings.artifacts_dir / job_id / "plots"
            plot_urls = generate_all_plots(
                time_clean,
                flux_clean,
                bls_cand.period,
                bls_cand.t0,
                None,  # periods_bls
                None,  # powers_bls
                plots_dir,
                candidate_id,
            )

            # Package candidate
            candidate = {
                "candidate_id": candidate_id,
                "probability": probability,
                "period_days": bls_cand.period,
                "t0_bjd": bls_cand.t0,
                "depth_ppm": transit_fit["depth_ppm"],
                "duration_hours": transit_fit["duration_hours"],
                "snr": bls_cand.snr,
                "rl_action": rl_action,
                "flags": flags,
                "plots": {
                    "phase_fold_png": f"/api/plots/{job_id}/{candidate_id}/phase.png",
                    "bls_png": f"/api/plots/{job_id}/{candidate_id}/bls.png",
                    "oddeven_png": f"/api/plots/{job_id}/{candidate_id}/oddeven.png",
                    "secondary_png": f"/api/plots/{job_id}/{candidate_id}/secondary.png",
                },
            }

            candidates.append(candidate)
            job_store.add_candidate(job_id, candidate)

        # Complete
        job_store.update_job(
            job_id,
            status="completed",
            progress=100.0,
            stage="completed",
            message=f"Found {len(candidates)} candidates",
        )

        logger.info(f"[Job {job_id}] Completed successfully with {len(candidates)} candidates")

    except Exception as e:
        logger.error(f"[Job {job_id}] Failed: {e}", exc_info=True)
        job_store.update_job(
            job_id, status="failed", progress=0.0, stage="failed", message=f"Error: {str(e)}"
        )


@router.post("/", response_model=JobStatus)
async def start_run(params: RunParams, background_tasks: BackgroundTasks):
    """
    Start a detection run.

    Creates a job and runs the pipeline in the background.
    """
    # Determine dataset ID
    dataset_id = params.dataset_id or params.upload_ref

    if not dataset_id:
        raise HTTPException(status_code=400, detail="Either dataset_id or upload_ref must be provided")

    # Create job
    job_store = get_job_store()
    job_id = job_store.create_job(dataset_id, params.model_dump())

    # Start background task
    background_tasks.add_task(run_detection_pipeline, job_id, dataset_id, params.model_dump())

    logger.info(f"Started job {job_id} for dataset {dataset_id}")

    return RunResponse(job_id=job_id, status="queued")
