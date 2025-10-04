"""
NASA data source integration using lightkurve and NASA Exoplanet Archive.

Provides access to Kepler, K2, and TESS light curve archives,
plus confirmed exoplanet parameters for validation.
"""
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

try:
    import lightkurve as lk
    LIGHTKURVE_AVAILABLE = True
except ImportError:
    LIGHTKURVE_AVAILABLE = False
    logger.warning("lightkurve not installed - NASA data fetching disabled")

try:
    # Try new import path first (astroquery >= 0.4.7)
    try:
        from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    except ImportError:
        # Fall back to old import path
        from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
    EXOPLANET_ARCHIVE_AVAILABLE = True
except ImportError:
    EXOPLANET_ARCHIVE_AVAILABLE = False
    logger.warning("astroquery not installed - Exoplanet Archive disabled")


def fetch_kepler_lightcurve(
    target_id: str, quarter: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fetch light curve from Kepler archive.
    
    Parameters
    ----------
    target_id : str
        Kepler ID (e.g., 'KIC 8462852' or 'Kepler-90')
    quarter : int, optional
        Specific quarter to download (default: first available)
    
    Returns
    -------
    tuple
        (time, flux, flux_err) arrays in days, normalized flux, and fractional errors
    
    Examples
    --------
    >>> time, flux, err = fetch_kepler_lightcurve('Kepler-90i')
    >>> time, flux, err = fetch_kepler_lightcurve('KIC 11442793', quarter=10)
    """
    if not LIGHTKURVE_AVAILABLE:
        raise RuntimeError("lightkurve not installed. Run: pip install lightkurve")
    
    logger.info(f"Searching for {target_id} in Kepler archive...")
    
    # Search for target
    search_result = lk.search_lightcurve(target_id, mission='Kepler')
    
    if len(search_result) == 0:
        raise ValueError(f"No Kepler data found for {target_id}")
    
    logger.info(f"Found {len(search_result)} observations")
    
    # Download specific quarter or first available
    if quarter is not None:
        search_result = search_result[search_result.mission == f'Kepler Quarter {quarter:02d}']
        if len(search_result) == 0:
            raise ValueError(f"No data for quarter {quarter}")
    
    lc = search_result[0].download()
    
    # Clean and normalize
    lc = lc.remove_nans().remove_outliers()
    lc = lc.normalize()
    
    # Extract arrays and convert masked arrays to regular numpy arrays
    time = np.asarray(lc.time.value)  # Days (BJD - 2454833)
    flux = np.asarray(lc.flux.value)  # Normalized
    flux_err = np.asarray(lc.flux_err.value) if lc.flux_err is not None else np.ones_like(flux) * 0.001
    
    logger.info(f"Downloaded {len(time)} points, span: {time.max() - time.min():.1f} days")
    
    return time, flux, flux_err


def fetch_tess_lightcurve(
    target_id: str, sector: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fetch light curve from TESS archive.
    
    Parameters
    ----------
    target_id : str
        TIC ID (e.g., 'TIC 307210830' or 'TOI-700')
    sector : int, optional
        Specific sector to download (default: first available)
    
    Returns
    -------
    tuple
        (time, flux, flux_err) arrays
    """
    if not LIGHTKURVE_AVAILABLE:
        raise RuntimeError("lightkurve not installed. Run: pip install lightkurve")
    
    logger.info(f"Searching for {target_id} in TESS archive...")
    
    search_result = lk.search_lightcurve(target_id, mission='TESS')
    
    if len(search_result) == 0:
        raise ValueError(f"No TESS data found for {target_id}")
    
    logger.info(f"Found {len(search_result)} observations")
    
    if sector is not None:
        search_result = search_result[search_result.mission == f'TESS Sector {sector}']
        if len(search_result) == 0:
            raise ValueError(f"No data for sector {sector}")
    
    lc = search_result[0].download()
    lc = lc.remove_nans().remove_outliers().normalize()
    
    # Convert masked arrays to regular numpy arrays
    time = np.asarray(lc.time.value)  # BJD - 2457000
    flux = np.asarray(lc.flux.value)
    flux_err = np.asarray(lc.flux_err.value) if lc.flux_err is not None else np.ones_like(flux) * 0.001
    
    logger.info(f"Downloaded {len(time)} points, span: {time.max() - time.min():.1f} days")
    
    return time, flux, flux_err


def search_targets(
    mission: str = 'Kepler',
    coordinates: Optional[str] = None,
    radius: float = 120.0,
    limit: int = 100
) -> List[str]:
    """
    Search for targets in NASA archives.
    
    Parameters
    ----------
    mission : str
        'Kepler', 'TESS', or 'K2'
    coordinates : str, optional
        Sky coordinates (e.g., '19h50m47s +40d03m47s')
    radius : float
        Search radius in arcseconds (default: 120)
    limit : int
        Maximum results to return
    
    Returns
    -------
    list
        List of target IDs
    
    Examples
    --------
    >>> targets = search_targets('Kepler', coordinates='19h50m47s +40d03m47s', radius=300)
    >>> targets = search_targets('TESS', limit=50)
    """
    if not LIGHTKURVE_AVAILABLE:
        raise RuntimeError("lightkurve not installed")
    
    logger.info(f"Searching {mission} archive...")
    
    if coordinates:
        results = lk.search_lightcurve(coordinates, radius=radius, mission=mission)
    else:
        # Return popular targets for browsing
        if mission.lower() == 'kepler':
            # Some confirmed multi-planet systems
            popular = [
                'Kepler-90',  # 8 planet system
                'Kepler-11',  # 6 planet system
                'Kepler-20',  # Rocky planets
                'Kepler-186', # Habitable zone planet
                'Kepler-452', # Earth's cousin
                'KIC 8462852', # Tabby's star
            ]
            return popular
        elif mission.lower() == 'tess':
            popular = [
                'TOI-700',    # Habitable zone
                'TOI-270',    # Super-Earths
                'TOI-175',    # Rocky
                'TOI-216',    # Sub-Neptune
            ]
            return popular
        else:
            results = lk.search_lightcurve('*', mission=mission)
    
    target_names = [str(r.target_name) for r in results[:limit]]
    
    logger.info(f"Found {len(target_names)} targets")
    
    return target_names


# Known exoplanet catalog for quick access
CONFIRMED_PLANETS = {
    'Kepler-90i': {'kic': 'KIC 11442793', 'period': 14.45, 'depth_ppm': 900, 'note': 'Earth-size in 8-planet system'},
    'Kepler-452b': {'kic': 'KIC 10593626', 'period': 384.8, 'depth_ppm': 300, 'note': "Earth's cousin"},
    'Kepler-186f': {'kic': 'KIC 8120608', 'period': 129.9, 'depth_ppm': 410, 'note': 'Habitable zone'},
    'Kepler-16b': {'kic': 'KIC 12644769', 'period': 228.8, 'depth_ppm': 15000, 'note': 'Circumbinary Tatooine'},
    'TOI-700d': {'tic': 'TIC 150428135', 'period': 37.4, 'depth_ppm': 1000, 'note': 'TESS habitable zone'},
}


def get_confirmed_planet_info(planet_name: str) -> dict:
    """
    Get information about a confirmed exoplanet.
    
    Parameters
    ----------
    planet_name : str
        Planet name (e.g., 'Kepler-90i')
    
    Returns
    -------
    dict
        Planet information including target ID and parameters
    """
    planet_name = planet_name.strip()
    
    if planet_name in CONFIRMED_PLANETS:
        return CONFIRMED_PLANETS[planet_name]
    
    raise ValueError(f"Unknown planet: {planet_name}. Try one of: {list(CONFIRMED_PLANETS.keys())}")


def fetch_confirmed_planet(planet_name: str, quarter: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fetch light curve for a confirmed exoplanet by name.
    
    Parameters
    ----------
    planet_name : str
        Planet name (e.g., 'Kepler-90i')
    quarter : int, optional
        Specific quarter/sector
    
    Returns
    -------
    tuple
        (time, flux, flux_err) arrays
    
    Examples
    --------
    >>> time, flux, err = fetch_confirmed_planet('Kepler-90i')
    >>> time, flux, err = fetch_confirmed_planet('Kepler-452b', quarter=10)
    """
    info = get_confirmed_planet_info(planet_name)
    
    if 'kic' in info:
        return fetch_kepler_lightcurve(info['kic'], quarter=quarter)
    elif 'tic' in info:
        return fetch_tess_lightcurve(info['tic'], sector=quarter)
    else:
        raise ValueError(f"No target ID found for {planet_name}")


# ========== NASA Exoplanet Archive Integration ==========

def query_exoplanet_archive(planet_name: str) -> Dict[str, Any]:
    """
    Query NASA Exoplanet Archive for confirmed planet parameters.
    
    This provides official validated parameters for cross-referencing
    your detections against known planets.
    
    Parameters
    ----------
    planet_name : str
        Planet name (e.g., 'Kepler-90 i', 'TOI-700 d', 'HAT-P-7 b')
    
    Returns
    -------
    dict
        Dictionary containing planet parameters:
        - pl_name: Planet name
        - hostname: Host star name
        - pl_orbper: Orbital period (days)
        - pl_rade: Planet radius (Earth radii)
        - pl_bmasse: Planet mass (Earth masses)
        - pl_eqt: Equilibrium temperature (K)
        - pl_insol: Insolation flux (Earth flux)
        - st_teff: Stellar effective temperature (K)
        - st_rad: Stellar radius (Solar radii)
        - st_mass: Stellar mass (Solar masses)
        - sy_dist: Distance to system (parsecs)
        - disc_year: Discovery year
        - disc_facility: Discovery facility
    
    Examples
    --------
    >>> params = query_exoplanet_archive('Kepler-90 i')
    >>> print(f"Period: {params['pl_orbper']:.2f} days")
    >>> print(f"Radius: {params['pl_rade']:.2f} Earth radii")
    
    >>> params = query_exoplanet_archive('TOI-700 d')
    >>> if params['pl_insol'] > 0.5 and params['pl_insol'] < 1.5:
    ...     print("Planet in habitable zone!")
    """
    if not EXOPLANET_ARCHIVE_AVAILABLE:
        raise RuntimeError("astroquery not installed. Run: pip install astroquery")
    
    logger.info(f"Querying NASA Exoplanet Archive for {planet_name}...")
    
    try:
        # Query the Planetary Systems Composite Parameters table
        result = NasaExoplanetArchive.query_object(
            planet_name,
            table='pscomppars'
        )
        
        if result is None or len(result) == 0:
            raise ValueError(f"No confirmed planet found: {planet_name}")
        
        # Take first result (most recent/default)
        row = result[0]
        
        # Helper function to safely extract masked values
        def safe_extract(row, key, dtype=float):
            """Safely extract value from potentially masked astropy table."""
            try:
                val = row[key]
                # Check if it's a masked value
                if hasattr(val, 'mask') and val.mask:
                    return None
                # Handle astropy Quantity objects (with units)
                if hasattr(val, 'value'):
                    return dtype(val.value)
                return dtype(val)
            except (KeyError, ValueError, TypeError):
                return None
        
        # Extract key parameters with None fallback for missing values
        params = {
            'pl_name': str(row['pl_name']),
            'hostname': str(row['hostname']),
            'pl_orbper': safe_extract(row, 'pl_orbper'),
            'pl_rade': safe_extract(row, 'pl_rade'),
            'pl_bmasse': safe_extract(row, 'pl_bmasse'),
            'pl_eqt': safe_extract(row, 'pl_eqt'),
            'pl_insol': safe_extract(row, 'pl_insol'),
            'st_teff': safe_extract(row, 'st_teff'),
            'st_rad': safe_extract(row, 'st_rad'),
            'st_mass': safe_extract(row, 'st_mass'),
            'sy_dist': safe_extract(row, 'sy_dist'),
            'disc_year': safe_extract(row, 'disc_year', int),
            'disc_facility': str(row.get('disc_facility', 'Unknown')),
        }
        
        period_str = f"{params['pl_orbper']:.2f}d" if params['pl_orbper'] is not None else "N/A"
        logger.info(f"Found confirmed planet: {params['pl_name']}, Period: {period_str}")
        
        return params
        
    except Exception as e:
        logger.error(f"Failed to query archive: {e}")
        raise


def validate_detection(
    target_id: str,
    detected_period: float,
    detected_depth_ppm: float,
    tolerance: float = 0.1
) -> Dict[str, Any]:
    """
    Validate a detection against NASA Exoplanet Archive.
    
    Checks if your detected signal matches a known confirmed planet,
    useful for verification and false positive checking.
    
    Parameters
    ----------
    target_id : str
        Target star identifier (e.g., 'Kepler-90', 'TOI-700')
    detected_period : float
        Your detected orbital period (days)
    detected_depth_ppm : float
        Your detected transit depth (ppm)
    tolerance : float
        Period match tolerance (default 0.1 = 10%)
    
    Returns
    -------
    dict
        Validation result:
        - match_found: bool
        - matched_planet: str or None
        - expected_period: float or None
        - period_difference: float or None (percentage)
        - all_planets: list of dicts with all known planets in system
    
    Examples
    --------
    >>> result = validate_detection('Kepler-90', 14.45, 900)
    >>> if result['match_found']:
    ...     print(f"Matches known planet: {result['matched_planet']}")
    ... else:
    ...     print("Potentially new candidate!")
    """
    if not EXOPLANET_ARCHIVE_AVAILABLE:
        raise RuntimeError("astroquery not installed")
    
    logger.info(f"Validating detection for {target_id}: P={detected_period:.2f}d")
    
    try:
        # Search for all planets around this star
        # First try exact hostname match
        result = NasaExoplanetArchive.query_criteria(
            table='pscomppars',
            where=f"hostname='{target_id}'"
        )
        
        if result is None or len(result) == 0:
            # Try without system suffix
            hostname = target_id.split()[0]  # 'Kepler-90 i' -> 'Kepler-90'
            result = NasaExoplanetArchive.query_criteria(
                table='pscomppars',
                where=f"hostname='{hostname}'"
            )
        
        if result is None or len(result) == 0:
            # Try searching by planet name prefix (e.g., 'Kepler-90%')
            result = NasaExoplanetArchive.query_criteria(
                table='pscomppars',
                where=f"pl_name like '{target_id}%'"
            )
        
        if result is None or len(result) == 0:
            logger.info(f"No confirmed planets found for {target_id}")
            return {
                'match_found': False,
                'matched_planet': None,
                'expected_period': None,
                'period_difference': None,
                'all_planets': []
            }
        
        # Extract all known planets
        all_planets = []
        best_match = None
        min_difference = float('inf')
        
        # Helper function to safely extract masked values
        def safe_extract(row, key, dtype=float):
            """Safely extract value from potentially masked astropy table."""
            try:
                val = row[key]
                if hasattr(val, 'mask') and val.mask:
                    return None
                # Handle astropy Quantity objects (with units)
                if hasattr(val, 'value'):
                    return dtype(val.value)
                return dtype(val)
            except (KeyError, ValueError, TypeError):
                return None
        
        for row in result:
            planet_name = str(row['pl_name'])
            planet_period = safe_extract(row, 'pl_orbper')
            
            if planet_period is not None:
                period_diff = abs(planet_period - detected_period) / planet_period
                
                all_planets.append({
                    'name': planet_name,
                    'period': planet_period,
                    'radius': safe_extract(row, 'pl_rade'),
                    'period_difference_pct': period_diff * 100
                })
                
                if period_diff < min_difference:
                    min_difference = period_diff
                    best_match = {
                        'name': planet_name,
                        'period': planet_period,
                        'difference_pct': period_diff * 100
                    }
        
        match_found = best_match is not None and min_difference <= tolerance
        
        result_dict = {
            'match_found': match_found,
            'matched_planet': best_match['name'] if best_match else None,
            'expected_period': best_match['period'] if best_match else None,
            'period_difference': best_match['difference_pct'] if best_match else None,
            'all_planets': all_planets
        }
        
        if match_found:
            logger.info(
                f"✓ Detection matches {best_match['name']}: "
                f"P={best_match['period']:.2f}d ({best_match['difference_pct']:.1f}% diff)"
            )
        else:
            logger.info(f"✗ No period match found - potentially new candidate!")
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise


def search_habitable_zone_planets(
    min_insol: float = 0.5,
    max_insol: float = 1.5,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search for confirmed planets in the habitable zone.
    
    The habitable zone is defined by stellar insolation flux
    (Earth = 1.0). Typical range: 0.5-1.5 Earth flux.
    
    Parameters
    ----------
    min_insol : float
        Minimum insolation flux (Earth flux units)
    max_insol : float
        Maximum insolation flux (Earth flux units)
    limit : int
        Maximum number of results
    
    Returns
    -------
    list
        List of planet dictionaries with parameters
    
    Examples
    --------
    >>> hz_planets = search_habitable_zone_planets()
    >>> for p in hz_planets:
    ...     print(f"{p['pl_name']}: {p['pl_insol']:.2f} Earth flux")
    """
    if not EXOPLANET_ARCHIVE_AVAILABLE:
        raise RuntimeError("astroquery not installed")
    
    logger.info(f"Searching habitable zone planets (insol: {min_insol}-{max_insol})...")
    
    result = NasaExoplanetArchive.query_criteria(
        table='pscomppars',
        where=f'pl_insol > {min_insol} and pl_insol < {max_insol}',
        select='pl_name,hostname,pl_orbper,pl_rade,pl_insol,pl_eqt,st_teff,sy_dist,disc_year'
    )
    
    if result is None or len(result) == 0:
        return []
    
    # Helper function to safely extract masked values
    def safe_extract(row, key, dtype=float):
        """Safely extract value from potentially masked astropy table."""
        try:
            val = row[key]
            if hasattr(val, 'mask') and val.mask:
                return None
            # Handle astropy Quantity objects (with units)
            if hasattr(val, 'value'):
                return dtype(val.value)
            return dtype(val)
        except (KeyError, ValueError, TypeError):
            return None
    
    planets = []
    for row in result[:limit]:
        planets.append({
            'pl_name': str(row['pl_name']),
            'hostname': str(row['hostname']),
            'pl_orbper': safe_extract(row, 'pl_orbper'),
            'pl_rade': safe_extract(row, 'pl_rade'),
            'pl_insol': safe_extract(row, 'pl_insol'),
            'pl_eqt': safe_extract(row, 'pl_eqt'),
            'st_teff': safe_extract(row, 'st_teff'),
            'sy_dist': safe_extract(row, 'sy_dist'),
            'disc_year': safe_extract(row, 'disc_year', int),
        })
    
    logger.info(f"Found {len(planets)} habitable zone planets")
    
    return planets
