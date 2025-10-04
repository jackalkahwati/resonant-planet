"""
API endpoints for biosignature detection and spectroscopic analysis.

Endpoints:
- POST /biosignatures/upload - Upload transmission spectrum
- POST /biosignatures/analyze - Analyze spectrum for life
- GET /biosignatures/simulate - Generate test spectra
- GET /biosignatures/results/{spectrum_id} - Get analysis results
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional
import logging

from core.schemas import (
    SpectrumUploadResponse,
    BiosignatureRequest,
    BiosignatureResult,
)
from core.settings import settings
from core.spectroscopy import (
    load_jwst_spectrum,
    create_simulated_biosignature_spectrum,
    validate_spectrum,
    bin_spectrum
)
from core.biosignatures import BiosignatureDetector
from core.biosignature_modulus_workflow import ModulusBiosignatureWorkflow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/biosignatures", tags=["biosignatures"])


# Initialize detector
biosignature_detector = None

def get_detector():
    """Get or create biosignature detector instance."""
    global biosignature_detector
    if biosignature_detector is None:
        import os
        modulus_url = os.getenv("MODULUS_API_URL", "https://modulus-865475771210.europe-west1.run.app")
        detector = BiosignatureDetector(modulus_api_url=modulus_url)
        detector.modulus_workflow = ModulusBiosignatureWorkflow(base_url=modulus_url)
        biosignature_detector = detector
    return biosignature_detector


@router.post("/upload", response_model=SpectrumUploadResponse)
async def upload_spectrum(file: UploadFile = File(...)):
    """
    Upload a transmission spectrum file for biosignature analysis.
    
    Accepts CSV with columns:
    - wavelength_um (or WAVELENGTH)
    - transit_depth_ppm (or DEPTH)
    - uncertainty_ppm (or ERROR) - optional
    """
    try:
        # Generate unique ID
        spectrum_id = str(uuid.uuid4())
        
        # Save uploaded file
        spectra_dir = settings.base_dir / "assets" / "spectra" / "uploaded"
        spectra_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = spectra_dir / f"{spectrum_id}_{file.filename}"
        
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # Load and validate
        wavelengths, depths, uncertainties = load_jwst_spectrum(filepath)
        
        validation = validate_spectrum(wavelengths, depths, uncertainties)
        
        if not validation['all_pass']:
            failed_checks = [k for k, v in validation.items() if not v and k != 'all_pass']
            logger.warning(f"Spectrum validation issues: {failed_checks}")
        
        return SpectrumUploadResponse(
            spectrum_id=spectrum_id,
            filename=file.filename,
            num_points=len(wavelengths),
            wavelength_range_um=(float(wavelengths.min()), float(wavelengths.max())),
            message=f"Uploaded spectrum with {len(wavelengths)} data points"
        )
        
    except Exception as e:
        logger.error(f"Failed to upload spectrum: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze", response_model=BiosignatureResult)
async def analyze_biosignatures(request: BiosignatureRequest):
    """
    Analyze a spectrum for biosignatures using Modulus chemistry.
    
    This endpoint:
    1. Loads the spectrum
    2. Identifies molecular features
    3. Uses Modulus to check chemical equilibrium
    4. Analyzes false positive scenarios
    5. Computes biosignature confidence
    """
    try:
        # Load spectrum
        spectra_dir = settings.base_dir / "assets" / "spectra"
        
        # Check both demo and uploaded directories
        filepath = None
        for subdir in ['uploaded', '']:
            check_dir = spectra_dir / subdir if subdir else spectra_dir
            matches = list(check_dir.glob(f"{request.spectrum_id}*"))
            if matches:
                filepath = matches[0]
                break
        
        if not filepath:
            raise HTTPException(status_code=404, detail=f"Spectrum {request.spectrum_id} not found")
        
        wavelengths, depths, uncertainties = load_jwst_spectrum(filepath)
        
        # Run biosignature analysis
        detector = get_detector()
        
        planet_params = {
            'radius_earth': request.planet_radius_earth,
            'temperature_k': request.planet_temp_k,
            'stellar_uv_flux': request.stellar_uv_flux,
            'age_gyr': request.planet_age_gyr,
        }
        
        result = detector.analyze_spectrum(wavelengths, depths, planet_params)
        
        logger.info(f"Biosignature analysis complete: score={result.biosignature_score:.2f}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Biosignature analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate")
async def simulate_spectrum(
    has_life: bool = True,
    planet_radius_earth: float = 1.0,
    noise_ppm: float = 30.0
):
    """
    Generate a simulated transmission spectrum for testing.
    
    Query params:
    - has_life: Include biosignature features (O2, CH4)
    - planet_radius_earth: Planet size in Earth radii
    - noise_ppm: Photon noise level
    
    Returns:
    - CSV file with simulated spectrum
    """
    try:
        wl, depth, err = create_simulated_biosignature_spectrum(
            has_life=has_life,
            planet_radius_earth=planet_radius_earth,
            noise_level_ppm=noise_ppm
        )
        
        # Save to temp file
        temp_dir = settings.base_dir / "assets" / "spectra" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"simulated_{'with' if has_life else 'no'}_life.csv"
        filepath = temp_dir / filename
        
        df = pd.DataFrame({
            'wavelength_um': wl,
            'transit_depth_ppm': depth,
            'uncertainty_ppm': err
        })
        df.to_csv(filepath, index=False)
        
        return FileResponse(
            filepath,
            media_type='text/csv',
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Failed to simulate spectrum: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets")
async def list_spectroscopic_datasets():
    """
    List available spectroscopic datasets.
    
    Returns datasets from:
    - Demo spectra (earth_like, mars_like, etc.)
    - Uploaded spectra
    """
    datasets = []
    
    spectra_dir = settings.base_dir / "assets" / "spectra"
    
    # Find all CSV files
    if spectra_dir.exists():
        for filepath in spectra_dir.rglob("*.csv"):
            if 'temp' in str(filepath):
                continue
            
            # Extract spectrum ID from filename
            stem = filepath.stem
            if '_' in stem:
                spectrum_id = stem.split('_')[0]
            else:
                spectrum_id = stem
            
            # Try to load to get stats
            try:
                df = pd.read_csv(filepath)
                wl_range = (df.iloc[:, 0].min(), df.iloc[:, 0].max())
                
                datasets.append({
                    'spectrum_id': spectrum_id,
                    'filename': filepath.name,
                    'num_points': len(df),
                    'wavelength_range_um': wl_range,
                    'source': 'demo' if 'demo' in str(filepath) or filepath.parent.name == 'spectra' else 'uploaded'
                })
            except:
                pass
    
    logger.info(f"Found {len(datasets)} spectroscopic datasets")
    
    return {"datasets": datasets}


@router.get("/molecules")
async def list_biosignature_molecules():
    """
    List known biosignature molecules and their properties.
    
    Returns information about key molecules to look for.
    """
    molecules = {
        'O2': {
            'name': 'Oxygen',
            'primary_wavelength_um': 0.76,
            'biosignature_strength': 'high',
            'abiotic_sources': ['water photolysis', 'photodissociation'],
            'notes': 'Strong biosignature when with CH4 (disequilibrium)'
        },
        'O3': {
            'name': 'Ozone',
            'primary_wavelength_um': 9.6,
            'biosignature_strength': 'high',
            'abiotic_sources': ['oxygen photochemistry'],
            'notes': 'Product of O2 - indicates photosynthesis'
        },
        'CH4': {
            'name': 'Methane',
            'primary_wavelength_um': 3.3,
            'biosignature_strength': 'medium',
            'abiotic_sources': ['serpentinization', 'volcanic outgassing'],
            'notes': 'Strong biosignature when with O2'
        },
        'N2O': {
            'name': 'Nitrous Oxide',
            'primary_wavelength_um': 7.8,
            'biosignature_strength': 'medium',
            'abiotic_sources': ['lightning', 'stellar proton events'],
            'notes': 'Produced by bacterial processes'
        },
        'PH3': {
            'name': 'Phosphine',
            'primary_wavelength_um': 4.3,
            'biosignature_strength': 'controversial',
            'abiotic_sources': ['volcanic', 'photochemistry (debated)'],
            'notes': 'Venus controversy - unclear if biosignature'
        },
        'H2O': {
            'name': 'Water',
            'primary_wavelength_um': 1.4,
            'biosignature_strength': 'low',
            'abiotic_sources': ['common in all atmospheres'],
            'notes': 'Not a biosignature, but required for life'
        },
        'CO2': {
            'name': 'Carbon Dioxide',
            'primary_wavelength_um': 4.3,
            'biosignature_strength': 'none',
            'abiotic_sources': ['volcanic', 'atmospheric chemistry'],
            'notes': 'Common abiotic gas'
        }
    }
    
    return {"molecules": molecules}


@router.post("/quick-analyze")
async def quick_biosignature_check(
    spectrum_file: str,
    planet_radius_earth: float = 1.0
):
    """
    Quick biosignature check on demo spectra.
    
    Parameters:
    - spectrum_file: Filename from assets/spectra (e.g., 'earth_like_with_life.csv')
    - planet_radius_earth: Planet size
    """
    try:
        filepath = settings.base_dir / "assets" / "spectra" / spectrum_file
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail=f"Spectrum file not found: {spectrum_file}")
        
        wavelengths, depths, uncertainties = load_jwst_spectrum(filepath)
        
        detector = get_detector()
        
        result = detector.analyze_spectrum(
            wavelengths,
            depths,
            planet_params={'radius_earth': planet_radius_earth}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

