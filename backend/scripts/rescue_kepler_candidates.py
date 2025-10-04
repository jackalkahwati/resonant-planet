#!/usr/bin/env python3
"""
Re-analyze Kepler uncertain candidates with physics-informed filtering.

This script applies the full detection pipeline (BLS + Modulus physics + RL triage)
to rescue real exoplanets from the uncertain candidate pile.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from glob import glob
import logging
import json
from tqdm import tqdm
from datetime import datetime

from core.preprocess import preprocess_light_curve
from core.features_bls import run_bls_search
from physics.modulus_adapter import ModulusBackend
from core.rl_policy import RLTriagePolicy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Input/output directories
INPUT_DIR = Path(__file__).parent.parent / 'data' / 'kepler_candidates'
OUTPUT_DIR = Path(__file__).parent.parent / 'data' / 'rescued_candidates'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_candidate_metadata():
    """Load candidate metadata from fetch step."""
    metadata_file = INPUT_DIR / 'candidate_metadata.csv'
    if not metadata_file.exists():
        logger.error(f"Metadata file not found: {metadata_file}")
        logger.error("Run fetch_kepler_uncertain.py first!")
        return None
    
    metadata = pd.read_csv(metadata_file)
    logger.info(f"✓ Loaded metadata for {len(metadata)} candidates")
    return metadata

def analyze_candidate(lc_file, metadata_row, modulus, rl_policy):
    """
    Analyze a single candidate with full pipeline.
    
    Returns:
        dict with analysis results
    """
    try:
        # Load light curve
        lc = pd.read_csv(lc_file)
        
        if len(lc) < 100:
            return {'status': 'failed', 'reason': 'too_short'}
        
        # Preprocess
        time, flux = preprocess_light_curve(lc['time'].values, lc['flux'].values)
        
        if time is None:
            return {'status': 'failed', 'reason': 'preprocessing_failed'}
        
        # BLS period search
        periods, powers, depths, durations, snrs = run_bls_search(
            time, flux,
            period_min=10.0,
            period_max=500.0
        )
        
        if len(periods) == 0:
            return {'status': 'no_transits', 'reason': 'bls_found_nothing'}
        
        # Get best period
        best_idx = np.argmax(snrs)
        period = periods[best_idx]
        depth = depths[best_idx]
        duration = durations[best_idx]
        snr = snrs[best_idx]
        
        # Get stellar parameters from metadata
        star_mass = metadata_row.get('koi_smass', 1.0)
        star_radius = metadata_row.get('koi_srad', 1.0)
        
        # Modulus physics validation
        physics_result = modulus.fit_transit(
            period=period,
            depth=depth,
            duration=duration,
            star_mass=star_mass,
            star_radius=star_radius
        )
        
        # RL triage policy
        features = {
            'snr': physics_result.get('snr', snr),
            'depth': depth,
            'period': period,
            'duration': duration,
            'planet_radius': physics_result.get('planet_radius_earth', 0),
            'impact_parameter': physics_result.get('impact_parameter', 0.5)
        }
        
        triage_result = rl_policy.triage(features)
        
        # Determine status
        if triage_result['action'] == 'accept' and physics_result.get('valid', False):
            status = 'CONFIRMED'
            confidence = 'high' if physics_result.get('snr', 0) > 10 else 'medium'
        elif triage_result['action'] == 'review':
            status = 'NEEDS_REVIEW'
            confidence = 'medium'
        else:
            status = 'FALSE_POSITIVE'
            confidence = 'low'
        
        return {
            'status': status,
            'confidence': confidence,
            'period': period,
            'depth': depth,
            'duration': duration,
            'snr': physics_result.get('snr', snr),
            'planet_radius_earth': physics_result.get('planet_radius_earth', np.nan),
            'semi_major_axis_au': physics_result.get('semi_major_axis_au', np.nan),
            'impact_parameter': physics_result.get('impact_parameter', np.nan),
            'equilibrium_temperature': physics_result.get('equilibrium_temperature_k', np.nan),
            'triage_action': triage_result['action'],
            'physics_valid': physics_result.get('valid', False),
            'rejection_reason': physics_result.get('rejection_reason', None)
        }
    
    except Exception as e:
        logger.error(f"Error analyzing {lc_file}: {e}")
        return {'status': 'failed', 'reason': str(e)}

def main():
    """Main execution function."""
    logger.info("=" * 80)
    logger.info("KEPLER CANDIDATE RESCUE - PHYSICS-INFORMED RE-ANALYSIS")
    logger.info("=" * 80)
    logger.info("")
    
    # Load metadata
    metadata = load_candidate_metadata()
    if metadata is None:
        return
    
    # Get list of light curve files
    lc_files = sorted(glob(str(INPUT_DIR / '*.csv')))
    lc_files = [f for f in lc_files if 'metadata' not in f and 'summary' not in f]
    
    logger.info(f"Found {len(lc_files)} light curve files to analyze")
    
    if len(lc_files) == 0:
        logger.error("No light curve files found!")
        logger.error("Run fetch_kepler_uncertain.py first!")
        return
    
    # Initialize pipeline components
    logger.info("Initializing pipeline components...")
    modulus = ModulusBackend(mode='local')  # Use local mode for now
    rl_policy = RLTriagePolicy()
    
    # Analyze all candidates
    results = []
    
    logger.info("\nStarting bulk re-analysis...")
    for lc_file in tqdm(lc_files, desc="Analyzing candidates"):
        # Extract KOI ID from filename
        koi_id = Path(lc_file).stem.replace('_', ' ')
        
        # Get metadata for this candidate
        metadata_row = metadata[metadata['kepoi_name'] == koi_id]
        if len(metadata_row) == 0:
            logger.warning(f"No metadata for {koi_id}, skipping")
            continue
        
        metadata_row = metadata_row.iloc[0]
        
        # Analyze
        result = analyze_candidate(lc_file, metadata_row, modulus, rl_policy)
        result['koi_id'] = koi_id
        result['kepler_name'] = metadata_row.get('kepler_name', koi_id)
        result['original_period'] = metadata_row.get('koi_period', np.nan)
        result['original_depth'] = metadata_row.get('koi_depth', np.nan)
        result['original_radius'] = metadata_row.get('koi_prad', np.nan)
        result['original_temperature'] = metadata_row.get('koi_teq', np.nan)
        
        results.append(result)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = OUTPUT_DIR / f'rescue_results_{timestamp}.csv'
    results_df.to_csv(results_file, index=False)
    
    # Generate summary statistics
    logger.info("\n" + "=" * 80)
    logger.info("RESCUE RESULTS SUMMARY")
    logger.info("=" * 80)
    logger.info("")
    
    total = len(results_df)
    confirmed = len(results_df[results_df['status'] == 'CONFIRMED'])
    needs_review = len(results_df[results_df['status'] == 'NEEDS_REVIEW'])
    false_positive = len(results_df[results_df['status'] == 'FALSE_POSITIVE'])
    failed = len(results_df[results_df['status'] == 'failed'])
    
    logger.info(f"Total analyzed: {total}")
    logger.info(f"✅ CONFIRMED planets: {confirmed} ({confirmed/total*100:.1f}%)")
    logger.info(f"🔍 NEEDS REVIEW: {needs_review} ({needs_review/total*100:.1f}%)")
    logger.info(f"❌ FALSE POSITIVES: {false_positive} ({false_positive/total*100:.1f}%)")
    logger.info(f"⚠️  FAILED analysis: {failed} ({failed/total*100:.1f}%)")
    
    # High-confidence confirmations
    high_conf = results_df[(results_df['status'] == 'CONFIRMED') & (results_df['confidence'] == 'high')]
    logger.info(f"\n⭐ HIGH-CONFIDENCE confirmations: {len(high_conf)}")
    
    if len(high_conf) > 0:
        logger.info("\nTop 10 high-confidence rescues:")
        logger.info("-" * 80)
        for idx, row in high_conf.head(10).iterrows():
            logger.info(f"  {row['koi_id']}: "
                       f"P={row['period']:.2f}d, "
                       f"R={row['planet_radius_earth']:.2f}R⊕, "
                       f"T={row['equilibrium_temperature']:.0f}K, "
                       f"SNR={row['snr']:.1f}")
    
    # Habitable zone candidates
    habitable = results_df[
        (results_df['status'] == 'CONFIRMED') &
        (results_df['equilibrium_temperature'] >= 200) &
        (results_df['equilibrium_temperature'] <= 600) &
        (results_df['planet_radius_earth'] >= 0.8) &
        (results_df['planet_radius_earth'] <= 1.5)
    ]
    
    logger.info(f"\n🌍 HABITABLE ZONE candidates (200-600K, 0.8-1.5R⊕): {len(habitable)}")
    
    if len(habitable) > 0:
        logger.info("\nHabitable zone rescues:")
        logger.info("-" * 80)
        for idx, row in habitable.iterrows():
            logger.info(f"  {row['koi_id']}: "
                       f"P={row['period']:.2f}d, "
                       f"R={row['planet_radius_earth']:.2f}R⊕, "
                       f"T={row['equilibrium_temperature']:.0f}K")
    
    # Save summary report
    summary_file = OUTPUT_DIR / f'rescue_summary_{timestamp}.txt'
    with open(summary_file, 'w') as f:
        f.write("KEPLER CANDIDATE RESCUE - SUMMARY REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"System: Modulus-Small (Qwen 2-1.5B) + Physics-Informed Filtering\n\n")
        f.write(f"Total Analyzed: {total}\n")
        f.write(f"Confirmed Planets: {confirmed} ({confirmed/total*100:.1f}%)\n")
        f.write(f"Needs Review: {needs_review} ({needs_review/total*100:.1f}%)\n")
        f.write(f"False Positives: {false_positive} ({false_positive/total*100:.1f}%)\n")
        f.write(f"Failed Analysis: {failed} ({failed/total*100:.1f}%)\n\n")
        f.write(f"High-Confidence Confirmations: {len(high_conf)}\n")
        f.write(f"Habitable Zone Candidates: {len(habitable)}\n\n")
        f.write("NEXT STEPS:\n")
        f.write("1. Review high-confidence confirmations for publication\n")
        f.write("2. Manual vetting of 'NEEDS_REVIEW' candidates\n")
        f.write("3. Generate figures and tables for paper\n")
        f.write("4. Prepare manuscript for AJ/MNRAS submission\n")
    
    logger.info(f"\n✓ Results saved to: {results_file}")
    logger.info(f"✓ Summary saved to: {summary_file}")
    logger.info("\n" + "=" * 80)
    logger.info("RESCUE COMPLETE")
    logger.info("=" * 80)

if __name__ == '__main__':
    main()


