#!/usr/bin/env python3
"""
Fetch Kepler uncertain/candidate exoplanets for re-analysis.

This script downloads the list of Kepler Objects of Interest (KOIs) with
"CANDIDATE" status and their light curves for physics-informed re-validation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import lightkurve as lk
from astroquery.mast import Observations
import logging
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directories
OUTPUT_DIR = Path(__file__).parent.parent / 'data' / 'kepler_candidates'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_candidate_list():
    """
    Fetch list of Kepler candidates from NASA Exoplanet Archive.
    
    Returns:
        DataFrame of candidate KOIs with orbital and stellar parameters
    """
    logger.info("Fetching Kepler candidate list from NASA Exoplanet Archive...")
    
    # Query NASA Exoplanet Archive for CANDIDATE status KOIs
    query_url = (
        'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?'
        'query=select+*+from+koi+where+koi_disposition="CANDIDATE"&format=csv'
    )
    
    try:
        candidates = pd.read_csv(query_url)
        logger.info(f"✓ Downloaded {len(candidates)} candidate KOIs")
        return candidates
    except Exception as e:
        logger.error(f"Failed to fetch candidate list: {e}")
        return None

def filter_high_priority(candidates):
    """
    Filter for high-priority targets based on habitability and detectability.
    
    Criteria:
    - Earth-like radius (0.8-1.5 R⊕)
    - Habitable zone temperature (200-600K)
    - Detectable transit depth (>50 ppm)
    - Low stellar noise (quiet stars)
    """
    logger.info("Filtering for high-priority candidates...")
    
    priority = candidates[
        (candidates['koi_prad'] >= 0.8) &  # Minimum 0.8 Earth radii
        (candidates['koi_prad'] <= 1.5) &  # Maximum 1.5 Earth radii
        (candidates['koi_teq'] >= 200) &   # Minimum equilibrium temperature
        (candidates['koi_teq'] <= 600) &   # Maximum equilibrium temperature
        (candidates['koi_depth'] > 50) &   # Minimum transit depth (ppm)
        (candidates['koi_period'] > 10) &  # Exclude hot Jupiters
        (candidates['koi_period'] < 500)   # Reasonable orbital period
    ].copy()
    
    logger.info(f"✓ Filtered to {len(priority)} high-priority candidates")
    logger.info(f"  Average radius: {priority['koi_prad'].mean():.2f} R⊕")
    logger.info(f"  Average temperature: {priority['koi_teq'].mean():.0f} K")
    logger.info(f"  Average period: {priority['koi_period'].mean():.1f} days")
    
    return priority

def download_light_curves(candidates, max_targets=100):
    """
    Download Kepler light curves for candidate list.
    
    Parameters:
        candidates: DataFrame of KOIs to download
        max_targets: Maximum number of light curves to download (default: 100)
    """
    logger.info(f"Downloading light curves for {min(len(candidates), max_targets)} targets...")
    
    downloaded = 0
    failed = 0
    
    for idx, row in tqdm(candidates.head(max_targets).iterrows(), total=min(len(candidates), max_targets)):
        koi_id = row['kepoi_name']
        kepler_name = row['kepler_name'] if pd.notna(row['kepler_name']) else koi_id
        
        output_file = OUTPUT_DIR / f"{koi_id.replace(' ', '_')}.csv"
        
        # Skip if already downloaded
        if output_file.exists():
            logger.debug(f"Skipping {koi_id} (already downloaded)")
            downloaded += 1
            continue
        
        try:
            # Search for light curve
            search_result = lk.search_lightcurve(kepler_name, mission='Kepler', author='Kepler')
            
            if len(search_result) == 0:
                logger.warning(f"No light curve found for {koi_id}")
                failed += 1
                continue
            
            # Download all quarters and stitch
            lc_collection = search_result.download_all()
            
            if lc_collection is None or len(lc_collection) == 0:
                logger.warning(f"Failed to download light curve for {koi_id}")
                failed += 1
                continue
            
            # Stitch quarters together
            lc = lc_collection.stitch()
            
            # Remove NaNs and normalize
            lc = lc.remove_nans().normalize()
            
            # Save to CSV
            df = pd.DataFrame({
                'time': lc.time.value,
                'flux': lc.flux.value,
                'flux_err': lc.flux_err.value if hasattr(lc, 'flux_err') else [0.001] * len(lc.time)
            })
            
            # Add metadata
            df.attrs['koi_id'] = koi_id
            df.attrs['period'] = row['koi_period']
            df.attrs['depth'] = row['koi_depth']
            df.attrs['duration'] = row['koi_duration']
            df.attrs['temperature'] = row['koi_teq']
            df.attrs['radius'] = row['koi_prad']
            
            df.to_csv(output_file, index=False)
            downloaded += 1
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error downloading {koi_id}: {e}")
            failed += 1
            continue
    
    logger.info(f"\n✓ Download complete:")
    logger.info(f"  Downloaded: {downloaded}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Output directory: {OUTPUT_DIR}")

def save_candidate_metadata(candidates, priority):
    """Save candidate metadata for reference."""
    metadata_file = OUTPUT_DIR / 'candidate_metadata.csv'
    priority.to_csv(metadata_file, index=False)
    logger.info(f"✓ Saved metadata to {metadata_file}")
    
    # Save summary statistics
    summary_file = OUTPUT_DIR / 'candidate_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("KEPLER UNCERTAIN CANDIDATES - SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total candidates in archive: {len(candidates)}\n")
        f.write(f"High-priority candidates: {len(priority)}\n\n")
        f.write("HIGH-PRIORITY CRITERIA:\n")
        f.write("  - Radius: 0.8-1.5 R⊕ (Earth-like)\n")
        f.write("  - Temperature: 200-600 K (habitable zone)\n")
        f.write("  - Transit depth: >50 ppm (detectable)\n")
        f.write("  - Period: 10-500 days\n\n")
        f.write("STATISTICS:\n")
        f.write(f"  Average radius: {priority['koi_prad'].mean():.2f} R⊕\n")
        f.write(f"  Average temperature: {priority['koi_teq'].mean():.0f} K\n")
        f.write(f"  Average period: {priority['koi_period'].mean():.1f} days\n")
        f.write(f"  Average depth: {priority['koi_depth'].mean():.0f} ppm\n")
    
    logger.info(f"✓ Saved summary to {summary_file}")

def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("KEPLER UNCERTAIN CANDIDATE FETCHER")
    logger.info("=" * 60)
    logger.info("")
    
    # Step 1: Fetch candidate list
    candidates = fetch_candidate_list()
    if candidates is None:
        logger.error("Failed to fetch candidate list. Exiting.")
        return
    
    # Step 2: Filter for high-priority targets
    priority = filter_high_priority(candidates)
    
    if len(priority) == 0:
        logger.error("No high-priority candidates found. Exiting.")
        return
    
    # Step 3: Save metadata
    save_candidate_metadata(candidates, priority)
    
    # Step 4: Download light curves (start with 100 for testing)
    logger.info("\nStarting light curve download (first 100 targets)...")
    logger.info("This may take 30-60 minutes depending on network speed.")
    download_light_curves(priority, max_targets=100)
    
    logger.info("\n" + "=" * 60)
    logger.info("FETCH COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nNext step: Run rescue_kepler_candidates.py to re-analyze these targets")

if __name__ == '__main__':
    main()


