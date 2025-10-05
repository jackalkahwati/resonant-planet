#!/usr/bin/env python3
"""
Quick test of the detection pipeline on demo data.
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
from pathlib import Path

print("=" * 70)
print("Resonant Worlds Explorer - Quick Test")
print("=" * 70)
print()

# Test 1: Load demo data
print("1. Testing data loading...")
try:
    demo_file = Path("assets/demos/kepler_tp.csv")
    if demo_file.exists():
        df = pd.read_csv(demo_file)
        print(f"   ✓ Loaded {len(df)} data points from demo file")
        print(f"   ✓ Time span: {df.iloc[:, 0].min():.2f} to {df.iloc[:, 0].max():.2f} days")
    else:
        print("   ✗ Demo file not found")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print()

# Test 2: Preprocessing
print("2. Testing preprocessing...")
try:
    from core.preprocess import preprocess_pipeline
    
    time = df.iloc[:, 0].values
    flux = df.iloc[:, 1].values
    flux_err = df.iloc[:, 2].values if len(df.columns) > 2 else None
    
    time_clean, flux_clean, flux_err_clean = preprocess_pipeline(time, flux, flux_err)
    
    print(f"   ✓ Preprocessed {len(time_clean)} points")
    print(f"   ✓ Removed {len(time) - len(time_clean)} outliers")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: BLS Search
print("3. Testing BLS period search...")
try:
    from core.features_bls import extract_bls_features
    
    candidates = extract_bls_features(
        time_clean, 
        flux_clean,
        min_period=0.5,
        max_period=5.0,
        max_candidates=3
    )
    
    print(f"   ✓ Found {len(candidates)} BLS candidates:")
    for i, c in enumerate(candidates, 1):
        print(f"      {i}. Period: {c.period:.3f}d, SNR: {c.snr:.1f}, Depth: {c.depth*1e6:.0f}ppm")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Modulus Adapter
print("4. Testing Modulus adapter...")
try:
    from physics import fit_transit, run_checks, get_backend_info
    
    info = get_backend_info()
    print(f"   ✓ Backend: {info['backend']} (mock: {info['is_mock']})")
    
    # Test transit fit on first candidate
    if candidates:
        c = candidates[0]
        result = fit_transit(time_clean, flux_clean, flux_err_clean)
        
        if result['success']:
            print(f"   ✓ Transit fit successful")
            print(f"      Period: {result['period_days']:.3f}d")
            print(f"      Depth: {result['depth_ppm']:.0f}ppm")
            print(f"      SNR: {result['snr']:.1f}")
        else:
            print(f"   ⚠ Fit completed but flagged: {result['message']}")
            
        # Test validation checks
        checks = run_checks(time_clean, flux_clean, c.period, c.t0)
        print(f"   ✓ Validation checks completed")
        print(f"      Odd/even delta: {checks['odd_even_depth_delta_pct']:.1f}%")
        print(f"      Secondary SNR: {checks['secondary_eclipse_snr']:.2f}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: API Health Check
print("5. Testing API availability...")
try:
    import requests
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        print(f"   ✓ Backend API is running!")
        print(f"   ✓ Access at: http://localhost:8000/docs")
    else:
        print(f"   ⚠ API returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"   ⚠ Backend not running (this is OK for quick test)")
    print(f"   → Start with: uvicorn api.main:app --reload")
except Exception as e:
    print(f"   ⚠ Could not check API: {e}")

print()
print("=" * 70)
print("✓ Core pipeline is working!")
print("=" * 70)
print()
print("Summary:")
print(f"  • Demo data loads correctly ({len(df)} points)")
print(f"  • Preprocessing works ({len(time_clean)} clean points)")
print(f"  • BLS finds candidates ({len(candidates)} found)")
print(f"  • Physics adapter is functional (mock mode)")
print()
print("Next steps:")
print("  1. Start backend: uvicorn api.main:app --reload")
print("  2. Run full demo: python run_demo.py")
print("  3. Test integration: ./test_integration.sh")
print()
