"""
Spectroscopic data ingestion and processing for biosignature detection.

Supports:
- JWST NIRSpec, NIRISS transmission spectra
- Hubble WFC3/STIS spectra  
- Ground-based high-resolution spectroscopy
- Simulated/synthetic spectra for testing
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


def load_jwst_spectrum(filepath: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load JWST transmission spectrum.
    
    JWST data format (CSV):
    - wavelength_um: Wavelength in microns
    - transit_depth_ppm: Transit depth in parts per million
    - uncertainty_ppm: 1-sigma uncertainty
    
    Parameters
    ----------
    filepath : Path
        Path to JWST spectrum file
    
    Returns
    -------
    wavelengths_um : array
        Wavelengths in microns
    depths_ppm : array
        Transit depths in ppm
    uncertainties_ppm : array
        Uncertainties in ppm
    """
    try:
        df = pd.read_csv(filepath)
        
        if 'wavelength_um' in df.columns:
            wavelengths = df['wavelength_um'].values
        elif 'WAVELENGTH' in df.columns:
            wavelengths = df['WAVELENGTH'].values
        else:
            wavelengths = df.iloc[:, 0].values
        
        if 'transit_depth_ppm' in df.columns:
            depths = df['transit_depth_ppm'].values
        elif 'DEPTH' in df.columns:
            depths = df['DEPTH'].values
        else:
            depths = df.iloc[:, 1].values
        
        if 'uncertainty_ppm' in df.columns:
            uncertainties = df['uncertainty_ppm'].values
        elif 'ERROR' in df.columns:
            uncertainties = df['ERROR'].values
        elif len(df.columns) > 2:
            uncertainties = df.iloc[:, 2].values
        else:
            uncertainties = np.ones_like(depths) * np.std(depths) * 0.1
        
        logger.info(f"Loaded JWST spectrum: {len(wavelengths)} points, "
                   f"{wavelengths.min():.2f}-{wavelengths.max():.2f} μm")
        
        return wavelengths, depths, uncertainties
        
    except Exception as e:
        logger.error(f"Failed to load JWST spectrum from {filepath}: {e}")
        raise


def load_hubble_spectrum(filepath: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load Hubble Space Telescope (WFC3/STIS) spectrum.
    
    Similar format to JWST but may have different column names.
    """
    try:
        df = pd.read_csv(filepath)
        
        wavelengths = df.iloc[:, 0].values
        
        if wavelengths.max() > 100:
            wavelengths = wavelengths / 10000.0
            logger.info("Converted wavelengths from Angstroms to microns")
        
        depths = df.iloc[:, 1].values
        
        if depths.max() < 0.1:
            depths = depths * 1e6
            logger.info("Converted depths from fraction to ppm")
        
        uncertainties = df.iloc[:, 2].values if len(df.columns) > 2 else np.ones_like(depths) * 50
        
        if uncertainties.max() < 0.1:
            uncertainties = uncertainties * 1e6
        
        logger.info(f"Loaded Hubble spectrum: {len(wavelengths)} points")
        
        return wavelengths, depths, uncertainties
        
    except Exception as e:
        logger.error(f"Failed to load Hubble spectrum: {e}")
        raise


def create_simulated_biosignature_spectrum(
    has_life: bool = True,
    planet_radius_earth: float = 1.0,
    scale_height_km: float = 8.0,
    noise_level_ppm: float = 30.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a simulated transmission spectrum with or without biosignatures.
    
    Useful for testing the pipeline and demonstrating capabilities.
    
    Parameters
    ----------
    has_life : bool
        If True, add biosignature features (O2, CH4, H2O)
    planet_radius_earth : float
        Planet radius in Earth radii
    scale_height_km : float
        Atmospheric scale height
    noise_level_ppm : float
        Photon noise level in ppm
    
    Returns
    -------
    wavelengths_um : array
        Wavelengths from 0.5 to 5.0 μm
    depths_ppm : array
        Simulated transit depths
    uncertainties_ppm : array
        Noise level per point
    """
    wavelengths = np.linspace(0.6, 5.3, 200)
    
    base_depth = (planet_radius_earth * 6371 / 696000) ** 2 * 1e6
    
    depths = np.ones_like(wavelengths) * base_depth
    
    rayleigh = 100 * (0.5 / wavelengths) ** 4
    depths += rayleigh
    
    if has_life:
        logger.info("Adding biosignature features to simulated spectrum")
        
        water_bands = [(1.15, 0.1, 150), (1.4, 0.15, 200), (1.9, 0.1, 180)]
        for center, width, amplitude in water_bands:
            depths += amplitude * np.exp(-((wavelengths - center) / width) ** 2)
        
        o2_band = (0.76, 0.02, 300)
        center, width, amplitude = o2_band
        depths += amplitude * np.exp(-((wavelengths - center) / width) ** 2)
        
        ch4_bands = [(2.3, 0.08, 120), (3.3, 0.1, 180)]
        for center, width, amplitude in ch4_bands:
            depths += amplitude * np.exp(-((wavelengths - center) / width) ** 2)
        
        
        logger.info("Added O2 (0.76μm), CH4 (2.3, 3.3μm), H2O features")
    else:
        logger.info("Creating abiotic spectrum (no biosignatures)")
        
        water_bands = [(1.4, 0.15, 200), (1.9, 0.1, 180)]
        for center, width, amplitude in water_bands:
            depths += amplitude * np.exp(-((wavelengths - center) / width) ** 2)
        
        co2_band = (4.3, 0.15, 250)
        center, width, amplitude = co2_band
        depths += amplitude * np.exp(-((wavelengths - center) / width) ** 2)
    
    noise = np.random.normal(0, noise_level_ppm, size=len(wavelengths))
    depths += noise
    
    uncertainties = np.ones_like(wavelengths) * noise_level_ppm
    
    logger.info(f"Created simulated spectrum: {len(wavelengths)} points, "
               f"SNR ~ {base_depth/noise_level_ppm:.1f}")
    
    return wavelengths, depths, uncertainties


def bin_spectrum(
    wavelengths: np.ndarray,
    depths: np.ndarray,
    uncertainties: np.ndarray,
    bin_width_um: float = 0.1
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Bin spectrum to increase signal-to-noise.
    
    Parameters
    ----------
    wavelengths : array
        Wavelength points
    depths : array
        Transit depths
    uncertainties : array
        Uncertainties
    bin_width_um : float
        Bin width in microns
    
    Returns
    -------
    binned_wavelengths, binned_depths, binned_uncertainties
    """
    bin_edges = np.arange(wavelengths.min(), wavelengths.max() + bin_width_um, bin_width_um)
    
    binned_wl = []
    binned_depth = []
    binned_err = []
    
    for i in range(len(bin_edges) - 1):
        mask = (wavelengths >= bin_edges[i]) & (wavelengths < bin_edges[i + 1])
        
        if np.sum(mask) > 0:
            weights = 1 / uncertainties[mask] ** 2
            avg_wl = np.average(wavelengths[mask], weights=weights)
            avg_depth = np.average(depths[mask], weights=weights)
            avg_err = 1 / np.sqrt(np.sum(weights))
            
            binned_wl.append(avg_wl)
            binned_depth.append(avg_depth)
            binned_err.append(avg_err)
    
    logger.info(f"Binned spectrum: {len(wavelengths)} → {len(binned_wl)} points")
    
    return np.array(binned_wl), np.array(binned_depth), np.array(binned_err)


def fetch_jwst_from_mast(target_name: str, output_dir: Path) -> Optional[Path]:
    """
    Fetch JWST spectroscopic data from MAST archive.
    
    NOTE: This requires astroquery and MAST API access.
    Currently a placeholder - would need full implementation.
    
    Parameters
    ----------
    target_name : str
        Target name (e.g., 'WASP-39 b', 'TRAPPIST-1 e')
    output_dir : Path
        Directory to save downloaded spectrum
    
    Returns
    -------
    filepath : Path or None
        Path to downloaded spectrum file
    """
    logger.warning("JWST MAST fetching not yet implemented - use simulated data or manual download")
    
    
    return None


def validate_spectrum(
    wavelengths: np.ndarray,
    depths: np.ndarray,
    uncertainties: np.ndarray
) -> Dict[str, bool]:
    """
    Validate spectrum data quality.
    
    Returns
    -------
    dict
        Validation checks and whether they pass
    """
    checks = {}
    
    checks['wavelength_range_ok'] = (wavelengths.min() < 1.0) and (wavelengths.max() > 2.0)
    
    checks['no_nans'] = not (np.any(np.isnan(wavelengths)) or 
                             np.any(np.isnan(depths)) or 
                             np.any(np.isnan(uncertainties)))
    
    median_snr = np.median(depths / uncertainties)
    checks['sufficient_snr'] = median_snr > 3.0
    
    resolution = len(wavelengths) / (wavelengths.max() - wavelengths.min())
    checks['sufficient_resolution'] = resolution > 10
    
    checks['monotonic_wavelengths'] = np.all(np.diff(wavelengths) > 0)
    
    all_pass = all(checks.values())
    checks['all_pass'] = all_pass
    
    if all_pass:
        logger.info("✅ Spectrum validation passed all checks")
    else:
        failed = [k for k, v in checks.items() if not v and k != 'all_pass']
        logger.warning(f"⚠️  Spectrum validation failed: {', '.join(failed)}")
    
    return checks

