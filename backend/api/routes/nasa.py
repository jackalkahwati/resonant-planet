"""
NASA archive data access endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from pathlib import Path
import numpy as np
import logging

from core.data_sources import (
    fetch_kepler_lightcurve,
    fetch_tess_lightcurve,
    fetch_confirmed_planet,
    search_targets,
    get_confirmed_planet_info,
    CONFIRMED_PLANETS,
    LIGHTKURVE_AVAILABLE
)
from core.settings import settings

router = APIRouter(prefix="/nasa", tags=["NASA Data"])
logger = logging.getLogger(__name__)


class TargetSearchRequest(BaseModel):
    mission: str = "Kepler"  # Kepler, TESS, K2
    coordinates: Optional[str] = None  # e.g., "19h50m47s +40d03m47s"
    radius: float = 120.0  # arcseconds
    limit: int = 100


class FetchRequest(BaseModel):
    target_id: str  # e.g., "KIC 11442793" or "Kepler-90i"
    mission: str = "Kepler"
    quarter: Optional[int] = None  # Specific quarter/sector


class NASADataset(BaseModel):
    dataset_id: str
    target_id: str
    mission: str
    num_points: int
    time_span_days: float
    filename: str
    quarter: Optional[int] = None


@router.get("/available")
async def check_nasa_availability():
    """Check if NASA data access is available."""
    return {
        "available": LIGHTKURVE_AVAILABLE,
        "missions": ["Kepler", "TESS", "K2"] if LIGHTKURVE_AVAILABLE else [],
        "confirmed_planets": list(CONFIRMED_PLANETS.keys()),
        "message": "Ready to fetch NASA data" if LIGHTKURVE_AVAILABLE else "Install lightkurve: pip install lightkurve"
    }


@router.get("/confirmed-planets")
async def list_confirmed_planets():
    """List confirmed exoplanets available for quick access."""
    return {
        "planets": [
            {
                "name": name,
                **info
            }
            for name, info in CONFIRMED_PLANETS.items()
        ],
        "count": len(CONFIRMED_PLANETS)
    }


@router.get("/search")
async def search_nasa_targets(
    mission: str = "Kepler",
    coordinates: Optional[str] = None,
    radius: float = 120.0,
    limit: int = 100
):
    """
    Search for targets in NASA archives.
    
    Examples:
    - /nasa/search?mission=Kepler&limit=10
    - /nasa/search?mission=TESS&coordinates=19h50m47s+40d03m47s&radius=300
    """
    if not LIGHTKURVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="lightkurve not installed. Install with: pip install lightkurve"
        )
    
    try:
        targets = search_targets(
            mission=mission,
            coordinates=coordinates,
            radius=radius,
            limit=limit
        )
        
        return {
            "targets": targets,
            "count": len(targets),
            "mission": mission
        }
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch", response_model=NASADataset)
async def fetch_nasa_data(request: FetchRequest):
    """
    Fetch light curve from NASA archive.
    
    Saves data locally and returns dataset info.
    
    Examples:
    - {"target_id": "Kepler-90i", "mission": "Kepler"}
    - {"target_id": "KIC 11442793", "mission": "Kepler", "quarter": 10}
    - {"target_id": "TOI-700", "mission": "TESS"}
    """
    if not LIGHTKURVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="lightkurve not installed. Install with: pip install lightkurve"
        )
    
    try:
        # Fetch data
        logger.info(f"Fetching {request.target_id} from {request.mission}...")
        
        # Check if it's a confirmed planet name
        if request.target_id in CONFIRMED_PLANETS:
            time, flux, flux_err = fetch_confirmed_planet(request.target_id, quarter=request.quarter)
        elif request.mission.lower() == 'kepler':
            time, flux, flux_err = fetch_kepler_lightcurve(request.target_id, quarter=request.quarter)
        elif request.mission.lower() == 'tess':
            time, flux, flux_err = fetch_tess_lightcurve(request.target_id, sector=request.quarter)
        else:
            raise ValueError(f"Unsupported mission: {request.mission}")
        
        # Generate dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Save to CSV
        upload_dir = settings.base_dir / settings.upload_dir
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        filename = f"{dataset_id}_nasa_{request.mission.lower()}_{request.target_id.replace(' ', '_')}.csv"
        filepath = upload_dir / filename
        
        # Write CSV
        data = np.column_stack([time, flux, flux_err])
        np.savetxt(
            filepath,
            data,
            delimiter=',',
            header='time,flux,flux_err',
            comments=''
        )
        
        logger.info(f"Saved {len(time)} points to {filepath}")
        
        return NASADataset(
            dataset_id=dataset_id,
            target_id=request.target_id,
            mission=request.mission,
            num_points=len(time),
            time_span_days=float(time.max() - time.min()),
            filename=filename,
            quarter=request.quarter
        )
    
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/planet-info/{planet_name}")
async def get_planet_info(planet_name: str):
    """
    Get information about a confirmed exoplanet.
    
    Example: /nasa/planet-info/Kepler-90i
    """
    try:
        info = get_confirmed_planet_info(planet_name)
        return {
            "name": planet_name,
            **info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
