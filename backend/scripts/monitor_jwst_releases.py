#!/usr/bin/env python3
"""
Monitor JWST MAST archive for new transmission spectroscopy observations.

This script checks for newly released JWST data daily and triggers rapid analysis
to enable first-to-publish opportunities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import schedule
import time
import logging
from datetime import datetime, timedelta
import json
import pandas as pd
from astroquery.mast import Observations
from astropy.time import Time

from core.spectroscopy import load_jwst_spectrum
from core.biosignatures import BiosignatureDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL_HOURS = 6  # Check every 6 hours
LOOKBACK_DAYS = 7  # Check for data released in last 7 days
ANALYSIS_LOG = Path(__file__).parent.parent / 'data' / 'jwst_monitoring' / 'analysis_log.json'
OUTPUT_DIR = Path(__file__).parent.parent / 'data' / 'jwst_new'

# Ensure directories exist
ANALYSIS_LOG.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_analysis_log():
    """Load log of previously analyzed observations."""
    if ANALYSIS_LOG.exists():
        with open(ANALYSIS_LOG, 'r') as f:
            return json.load(f)
    return {'analyzed': [], 'last_check': None}

def save_analysis_log(log):
    """Save updated analysis log."""
    log['last_check'] = datetime.now().isoformat()
    with open(ANALYSIS_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def is_analyzed(obs_id, log):
    """Check if observation has already been analyzed."""
    return obs_id in log['analyzed']

def get_target_params(target_name):
    """
    Get target parameters from SIMBAD or ExoplanetArchive.
    
    For rapid analysis, use reasonable defaults if data unavailable.
    """
    # TODO: Query SIMBAD/ExoplanetArchive for actual parameters
    # For now, return reasonable defaults
    logger.info(f"Getting parameters for {target_name}...")
    
    # Check if it's a known exoplanet
    # This is a placeholder - in production, query NASA Exoplanet Archive
    known_targets = {
        'K2-18 b': {'temperature_k': 270, 'planet_radius_earth': 2.6},
        'TRAPPIST-1 e': {'temperature_k': 250, 'planet_radius_earth': 0.92},
        'WASP-96 b': {'temperature_k': 1350, 'planet_radius_earth': 13.4},
        'WASP-39 b': {'temperature_k': 1100, 'planet_radius_earth': 14.1},
        'LHS 475 b': {'temperature_k': 580, 'planet_radius_earth': 0.99},
    }
    
    # Normalize target name
    for known_name, params in known_targets.items():
        if known_name.lower() in target_name.lower():
            logger.info(f"✓ Found known target: {known_name}")
            return {
                'name': target_name,
                'temperature_k': params['temperature_k'],
                'planet_radius_earth': params['planet_radius_earth'],
                'stellar_uv_flux': 1.0,
                'age_gyr': 4.5
            }
    
    # Default for unknown targets (assume temperate mini-Neptune)
    logger.warning(f"Unknown target {target_name}, using default parameters")
    return {
        'name': target_name,
        'temperature_k': 400,
        'planet_radius_earth': 2.0,
        'stellar_uv_flux': 1.0,
        'age_gyr': 4.5
    }

def run_rapid_analysis(obs_id, target_name, data_file):
    """
    Perform rapid biosignature analysis on new JWST observation.
    
    Returns:
        Analysis result dict
    """
    logger.info(f"Starting rapid analysis of {target_name}...")
    
    try:
        # Load spectrum
        wavelengths, depths, uncertainties = load_jwst_spectrum(data_file)
        
        if len(wavelengths) < 10:
            logger.warning(f"Insufficient data points ({len(wavelengths)}) for {target_name}")
            return None
        
        # Get target parameters
        params = get_target_params(target_name)
        
        # Run biosignature detection
        detector = BiosignatureDetector()
        result = detector.analyze_spectrum(wavelengths, depths, params)
        
        # Format result
        analysis = {
            'obs_id': obs_id,
            'target': target_name,
            'analysis_time': datetime.now().isoformat(),
            'biosignature_score': result.biosignature_score,
            'detected_molecules': result.detected_molecules,
            'disequilibrium_score': result.disequilibrium_score,
            'confidence': result.confidence_level,
            'temperature_k': params['temperature_k'],
            'explanation': result.explanation
        }
        
        # Log result
        if result.biosignature_score > 0.5:
            logger.info(f"🌟 POTENTIAL BIOSIGNATURE: {target_name}")
            logger.info(f"   Score: {result.biosignature_score:.3f}")
            logger.info(f"   Molecules: {', '.join(result.detected_molecules)}")
            logger.info(f"   Confidence: {result.confidence_level}")
            
            # Generate alert
            generate_biosignature_alert(analysis)
        else:
            logger.info(f"✓ Analyzed {target_name}: No biosignatures")
            logger.info(f"   Score: {result.biosignature_score:.3f}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing {target_name}: {e}")
        return None

def generate_biosignature_alert(analysis):
    """
    Generate alert for potential biosignature detection.
    
    This creates a draft report and notifies for immediate review.
    """
    alert_file = OUTPUT_DIR / f"ALERT_{analysis['obs_id']}.txt"
    
    with open(alert_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("🚨 BIOSIGNATURE ALERT - RAPID ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Target: {analysis['target']}\n")
        f.write(f"Observation ID: {analysis['obs_id']}\n")
        f.write(f"Analysis Time: {analysis['analysis_time']}\n")
        f.write(f"Biosignature Score: {analysis['biosignature_score']:.3f}\n")
        f.write(f"Confidence Level: {analysis['confidence']}\n")
        f.write(f"Temperature: {analysis['temperature_k']:.0f} K\n\n")
        f.write(f"Detected Molecules:\n")
        for mol in analysis['detected_molecules']:
            f.write(f"  - {mol}\n")
        f.write(f"\nDisequilibrium Score: {analysis['disequilibrium_score']:.3f}\n\n")
        f.write("EXPLANATION:\n")
        f.write("-" * 80 + "\n")
        f.write(analysis['explanation'])
        f.write("\n\n")
        f.write("RECOMMENDED ACTIONS:\n")
        f.write("1. Manual review of spectrum and detection\n")
        f.write("2. Compare with published results (if any)\n")
        f.write("3. Prepare rapid-communication paper draft\n")
        f.write("4. Submit to ApJ Letters or Nature Astronomy\n")
    
    logger.info(f"✓ Alert saved to: {alert_file}")

def check_new_jwst_spectra():
    """
    Check MAST archive for new transmission spectroscopy observations.
    """
    logger.info("=" * 80)
    logger.info(f"JWST MONITORING CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    # Load analysis log
    log = load_analysis_log()
    
    try:
        # Query for recent JWST observations
        # Focus on transmission spectroscopy programs
        end_time = Time.now()
        start_time = end_time - timedelta(days=LOOKBACK_DAYS)
        
        logger.info(f"Querying MAST for observations from {start_time.iso} to {end_time.iso}")
        
        observations = Observations.query_criteria(
            obs_collection='JWST',
            instrument_name=['NIRISS', 'NIRSpec', 'MIRI'],
            dataproduct_type='spectrum',
            t_min=start_time.mjd,
            t_max=end_time.mjd
        )
        
        if len(observations) == 0:
            logger.info("No new observations found")
            save_analysis_log(log)
            return
        
        logger.info(f"Found {len(observations)} recent observations")
        
        # Filter for new observations
        new_obs = []
        for obs in observations:
            obs_id = obs['obs_id']
            if not is_analyzed(obs_id, log):
                new_obs.append(obs)
        
        if len(new_obs) == 0:
            logger.info("All observations already analyzed")
            save_analysis_log(log)
            return
        
        logger.info(f"🚨 {len(new_obs)} NEW observations to analyze!")
        
        # Analyze each new observation
        for obs in new_obs:
            obs_id = obs['obs_id']
            target_name = obs['target_name']
            
            logger.info(f"\n{'=' * 80}")
            logger.info(f"NEW OBSERVATION: {target_name} ({obs_id})")
            logger.info(f"{'=' * 80}")
            
            # Download data products
            try:
                data_products = Observations.get_product_list(obs)
                
                # Filter for 1D extracted spectra
                spec_products = [p for p in data_products 
                                if 'x1d' in p['productSubGroupDescription'].lower() or
                                   'spectrum' in p['productSubGroupDescription'].lower()]
                
                if len(spec_products) == 0:
                    logger.warning(f"No spectrum products found for {obs_id}")
                    continue
                
                # Download
                download_dir = OUTPUT_DIR / obs_id
                download_dir.mkdir(parents=True, exist_ok=True)
                
                logger.info(f"Downloading {len(spec_products)} spectrum files...")
                Observations.download_products(spec_products, download_dir=str(download_dir))
                
                # Find downloaded spectrum file
                spec_files = list(download_dir.rglob('*x1d*.fits'))
                if len(spec_files) == 0:
                    spec_files = list(download_dir.rglob('*.fits'))
                
                if len(spec_files) == 0:
                    logger.warning(f"No FITS files downloaded for {obs_id}")
                    continue
                
                spec_file = spec_files[0]
                logger.info(f"Using spectrum file: {spec_file.name}")
                
                # Run rapid analysis
                result = run_rapid_analysis(obs_id, target_name, spec_file)
                
                if result:
                    # Save result
                    result_file = download_dir / 'analysis_result.json'
                    with open(result_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    
                    logger.info(f"✓ Analysis saved to: {result_file}")
                
                # Mark as analyzed
                log['analyzed'].append(obs_id)
                
            except Exception as e:
                logger.error(f"Error processing {obs_id}: {e}")
                continue
        
        # Save updated log
        save_analysis_log(log)
        
    except Exception as e:
        logger.error(f"Error checking MAST archive: {e}")
    
    logger.info(f"\n{'=' * 80}")
    logger.info("CHECK COMPLETE")
    logger.info(f"{'=' * 80}\n")

def main():
    """Main monitoring loop."""
    logger.info("=" * 80)
    logger.info("JWST RAPID ANALYSIS MONITORING SERVICE")
    logger.info("=" * 80)
    logger.info(f"Check interval: Every {CHECK_INTERVAL_HOURS} hours")
    logger.info(f"Lookback window: {LOOKBACK_DAYS} days")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info("=" * 80)
    logger.info("\nService starting...")
    logger.info("Press Ctrl+C to stop\n")
    
    # Run initial check
    check_new_jwst_spectra()
    
    # Schedule periodic checks
    schedule.every(CHECK_INTERVAL_HOURS).hours.do(check_new_jwst_spectra)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour if scheduled task should run
    except KeyboardInterrupt:
        logger.info("\n\nMonitoring service stopped by user")
        logger.info("Goodbye!")

if __name__ == '__main__':
    main()


