"""
Dataset management endpoints.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import pandas as pd
from pathlib import Path
import uuid
import logging

from core.settings import settings
from core.schemas import Dataset, UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("/", response_model=List[Dataset])
async def list_datasets():
    """
    List available datasets.

    Returns bundled demo datasets if DEMO_MODE is enabled.
    """
    datasets = []

    if settings.demo_mode:
        demo_dir = settings.base_dir / settings.demo_datasets_path

        if demo_dir.exists():
            for csv_file in demo_dir.glob("*.csv"):
                # Load to get metadata
                try:
                    df = pd.read_csv(csv_file)
                    time_col = df.columns[0]
                    flux_col = df.columns[1]

                    datasets.append(
                        Dataset(
                            dataset_id=csv_file.stem,
                            name=csv_file.stem.replace("_", " ").title(),
                            description=f"Demo dataset: {csv_file.stem}",
                            source="demo",
                            num_points=len(df),
                            time_span_days=float(df[time_col].max() - df[time_col].min()),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to load demo dataset {csv_file}: {e}")

    return datasets


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a light curve dataset.

    Accepts CSV files with columns: time, flux, [flux_err]
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    # Generate upload ID
    upload_id = str(uuid.uuid4())

    # Save file
    upload_dir = settings.base_dir / settings.upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{upload_id}.csv"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Validate CSV
    try:
        df = pd.read_csv(file_path)

        if len(df.columns) < 2:
            raise ValueError("CSV must have at least 2 columns (time, flux)")

        logger.info(f"Uploaded dataset {upload_id}: {len(df)} points")

    except Exception as e:
        file_path.unlink()  # Delete invalid file
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

    return UploadResponse(
        dataset_id=upload_id,
        filename=file.filename,
        message="Dataset uploaded successfully",
    )


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset_info(dataset_id: str):
    """Get information about a specific dataset."""
    # Check demo datasets
    if settings.demo_mode:
        demo_file = settings.base_dir / settings.demo_datasets_path / f"{dataset_id}.csv"

        if demo_file.exists():
            df = pd.read_csv(demo_file)
            time_col = df.columns[0]

            return DatasetInfo(
                dataset_id=dataset_id,
                name=dataset_id.replace("_", " ").title(),
                description=f"Demo dataset: {dataset_id}",
                source="demo",
                num_points=len(df),
                time_span_days=float(df[time_col].max() - df[time_col].min()),
            )

    # Check uploaded datasets
    upload_file = settings.base_dir / settings.upload_dir / f"{dataset_id}.csv"

    if upload_file.exists():
        df = pd.read_csv(upload_file)
        time_col = df.columns[0]

        return DatasetInfo(
            dataset_id=dataset_id,
            name=dataset_id,
            description="Uploaded dataset",
            source="upload",
            num_points=len(df),
            time_span_days=float(df[time_col].max() - df[time_col].min()),
        )

    raise HTTPException(status_code=404, detail="Dataset not found")
