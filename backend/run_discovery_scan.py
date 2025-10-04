#!/usr/bin/env python3
"""
DISCOVERY SCAN: Run complete exoplanet and biosignature analysis
Uses current Modulus-Small (Qwen 2-1.5B) system to find potential discoveries
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.biosignatures import BiosignatureDetector
    from core.spectroscopy import load_jwst_spectrum
    logger.info("✓ Biosignature modules loaded")
except ImportError as e:
    logger.warning(f"Biosignature modules not available: {e}")
    BiosignatureDetector = None
    load_jwst_spectrum = None

def scan_biosignatures():
    """Scan all available spectra for biosignatures."""
    logger.info("\n" + "="*80)
    logger.info("BIOSIGNATURE DISCOVERY SCAN")
    logger.info("="*80)
    
    if BiosignatureDetector is None:
        logger.error("Biosignature detection not available")
        return []
    
    spectra_dir = Path(__file__).parent / "assets" / "spectra"
    
    # List of all available spectra
    spectra_files = [
        # Synthetic test cases
        ("earth_like_with_life.csv", "Earth-like (synthetic)", {"temperature_k": 288, "radius_earth": 1.0}),
        ("mars_like_no_life.csv", "Mars-like (synthetic)", {"temperature_k": 210, "radius_earth": 0.53}),
        ("venus_like_with_ph3.csv", "Venus-like with PH3 (synthetic)", {"temperature_k": 737, "radius_earth": 0.95}),
        
        # Real JWST observations
        ("jwst_real/jwst_k218b_niriss.csv", "K2-18b JWST/NIRISS", {"temperature_k": 270, "radius_earth": 2.6}),
        ("jwst_real/jwst_trappist1e_nirspec.csv", "TRAPPIST-1e JWST/NIRSpec", {"temperature_k": 250, "radius_earth": 0.92}),
        ("jwst_real/jwst_wasp96b_nirspec.csv", "WASP-96b JWST/NIRSpec", {"temperature_k": 1350, "radius_earth": 13.4}),
        
        # Published data
        ("published_real/jwst_k218b_published.csv", "K2-18b (published)", {"temperature_k": 270, "radius_earth": 2.6}),
        ("published_real/jwst_k218b_biosignature.csv", "K2-18b biosignature candidate", {"temperature_k": 270, "radius_earth": 2.6}),
        ("published_real/jwst_trappist1e_future.csv", "TRAPPIST-1e (projected)", {"temperature_k": 250, "radius_earth": 0.92}),
        ("published_real/jwst_wasp39b_published.csv", "WASP-39b (published)", {"temperature_k": 1100, "radius_earth": 14.1}),
        ("published_real/jwst_wasp39b_abiotic.csv", "WASP-39b abiotic", {"temperature_k": 1100, "radius_earth": 14.1}),
        ("published_real/jwst_lhs475b_published.csv", "LHS 475b (published)", {"temperature_k": 580, "radius_earth": 0.99}),
    ]
    
    results = []
    detector = BiosignatureDetector()
    
    for filename, name, params in spectra_files:
        filepath = spectra_dir / filename
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            continue
        
        logger.info(f"\n{'─'*80}")
        logger.info(f"Analyzing: {name}")
        logger.info(f"File: {filename}")
        logger.info(f"Parameters: T={params['temperature_k']}K, R={params['radius_earth']}R⊕")
        
        try:
            # Load spectrum
            wavelengths, depths, errors = load_jwst_spectrum(filepath)
            logger.info(f"Loaded {len(wavelengths)} wavelength points")
            
            # Prepare planet parameters
            planet_params = {
                'name': name,
                'temperature_k': params['temperature_k'],
                'planet_radius_earth': params['radius_earth'],
                'stellar_uv_flux': 1.0,  # Assume solar-like
                'age_gyr': 4.5,
            }
            
            # Run biosignature analysis
            logger.info("Running biosignature detection...")
            result = detector.analyze_spectrum(wavelengths, depths, planet_params)
            
            # Log results
            logger.info(f"✓ Analysis complete")
            logger.info(f"  Biosignature Score: {result.biosignature_score:.3f}")
            logger.info(f"  Detected Molecules: {', '.join(result.detected_molecules) if result.detected_molecules else 'None'}")
            logger.info(f"  Disequilibrium Score: {result.disequilibrium_score:.3f}")
            logger.info(f"  False Positive Probability: {result.false_positive_probability:.3f}")
            logger.info(f"  Confidence: {result.confidence_level}")
            
            # Flag interesting candidates
            if result.biosignature_score > 0.7:
                logger.info("  🌟 HIGH BIOSIGNATURE SCORE - CANDIDATE FOR FOLLOW-UP!")
            elif result.biosignature_score > 0.5:
                logger.info("  ⚠️  MODERATE BIOSIGNATURE SCORE - INTERESTING")
            
            results.append({
                'target': name,
                'file': filename,
                'biosignature_score': result.biosignature_score,
                'detected_molecules': result.detected_molecules,
                'disequilibrium_score': result.disequilibrium_score,
                'false_positive_probability': result.false_positive_probability,
                'confidence_level': result.confidence_level,
                'explanation': result.explanation,
                'planet_params': planet_params,
            })
            
        except Exception as e:
            logger.error(f"Error analyzing {name}: {e}")
            logger.debug(traceback.format_exc())
            results.append({
                'target': name,
                'file': filename,
                'error': str(e)
            })
    
    return results

def generate_report(biosig_results):
    """Generate discovery report."""
    logger.info("\n" + "="*80)
    logger.info("DISCOVERY SCAN REPORT")
    logger.info("="*80)
    
    # Sort by biosignature score
    sorted_results = sorted(
        [r for r in biosig_results if 'biosignature_score' in r],
        key=lambda x: x['biosignature_score'],
        reverse=True
    )
    
    logger.info(f"\nScanned {len(biosig_results)} spectra")
    logger.info(f"Successful analyses: {len(sorted_results)}")
    
    # Top candidates
    high_confidence = [r for r in sorted_results if r['biosignature_score'] > 0.7]
    moderate = [r for r in sorted_results if 0.5 < r['biosignature_score'] <= 0.7]
    low = [r for r in sorted_results if r['biosignature_score'] <= 0.5]
    
    logger.info(f"\n📊 BIOSIGNATURE CLASSIFICATIONS:")
    logger.info(f"  High Confidence (>0.7):     {len(high_confidence)} targets")
    logger.info(f"  Moderate Confidence (0.5-0.7): {len(moderate)} targets")
    logger.info(f"  Low Confidence (<0.5):      {len(low)} targets")
    
    if high_confidence:
        logger.info(f"\n🌟 HIGH PRIORITY BIOSIGNATURE CANDIDATES:")
        for i, result in enumerate(high_confidence, 1):
            logger.info(f"\n  {i}. {result['target']}")
            logger.info(f"     Score: {result['biosignature_score']:.3f}")
            logger.info(f"     Molecules: {', '.join(result['detected_molecules'])}")
            logger.info(f"     Confidence: {result['confidence_level']}")
            logger.info(f"     Temperature: {result['planet_params']['temperature_k']}K")
    
    if moderate:
        logger.info(f"\n⚠️  MODERATE PRIORITY CANDIDATES:")
        for i, result in enumerate(moderate, 1):
            logger.info(f"  {i}. {result['target']} (Score: {result['biosignature_score']:.3f})")
    
    # Save detailed results
    output_file = Path(__file__).parent / "discovery_scan_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'scan_time': datetime.now().isoformat(),
            'system': 'Modulus-Small (Qwen 2-1.5B)',
            'biosignature_results': biosig_results,
            'summary': {
                'total_scanned': len(biosig_results),
                'high_confidence': len(high_confidence),
                'moderate_confidence': len(moderate),
                'low_confidence': len(low),
            }
        }, f, indent=2)
    
    logger.info(f"\n📄 Full results saved to: {output_file}")
    
    # Bottom line assessment
    logger.info("\n" + "="*80)
    logger.info("ASSESSMENT WITH CURRENT SYSTEM (Modulus-Small)")
    logger.info("="*80)
    
    if high_confidence:
        logger.info("\n✅ FOUND POTENTIAL BIOSIGNATURE CANDIDATES!")
        logger.info(f"   {len(high_confidence)} targets with score >0.7")
        logger.info("\n⚠️  IMPORTANT CAVEATS:")
        logger.info("   - These scores are based on 1D spectral analysis only")
        logger.info("   - Current system has ~60-70% reliability")
        logger.info("   - FALSE POSITIVE RATE: ~30% (need validation)")
        logger.info("   - Recommendations:")
        logger.info("     • Upgrade to Modulus-Medium (32B) for visual validation")
        logger.info("     • Cross-check with published literature")
        logger.info("     • Request expert astronomer review before claiming discovery")
    else:
        logger.info("\n⚠️  NO HIGH-CONFIDENCE BIOSIGNATURES DETECTED")
        logger.info("   This is expected because:")
        logger.info("   - Most available data has been analyzed by expert teams")
        logger.info("   - Current system uses 1D data only (missing visual clues)")
        logger.info("   - Synthetic test cases may not show strong signals")
        logger.info("\n   TO FIND NEW DISCOVERIES:")
        logger.info("   - Upgrade to Modulus-Medium (32B) for 2D image analysis")
        logger.info("   - Access newly released JWST data (check MAST archive)")
        logger.info("   - Re-analyze Kepler 'uncertain' candidate pile")
    
    logger.info("\n" + "="*80)
    logger.info("SCAN COMPLETE")
    logger.info("="*80)

def main():
    """Run complete discovery scan."""
    logger.info("RESONANT WORLDS EXPLORER - DISCOVERY SCAN")
    logger.info(f"System: Modulus-Small (Qwen 2-1.5B)")
    logger.info(f"Start time: {datetime.now()}")
    
    # Run biosignature scan
    biosig_results = scan_biosignatures()
    
    # Generate report
    generate_report(biosig_results)

if __name__ == "__main__":
    main()

