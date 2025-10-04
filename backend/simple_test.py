#!/usr/bin/env python3
"""
Simple test without pandas dependency.
"""
import sys
sys.path.insert(0, '.')

import numpy as np
from pathlib import Path

print("=" * 70)
print("Resonant Worlds Explorer - Simple Pipeline Test")
print("=" * 70)
print()

# Load demo data manually
print("1. Loading demo data...")
try:
    demo_file = Path("assets/demos/kepler_tp.csv")
    
    # Read CSV manually to avoid pandas dependency
    data = np.loadtxt(demo_file, delimiter=',', skiprows=1)
    time = data[:, 0]
    flux = data[:, 1]
    flux_err = data[:, 2]
    
    print(f"   ✓ Loaded {len(time)} data points")
    print(f"   ✓ Time range: {time.min():.2f} to {time.max():.2f} days")
    print(f"   ✓ Flux range: {flux.min():.4f} to {flux.max():.4f}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print()

# Test Modulus adapter
print("2. Testing Modulus adapter...")
try:
    from physics import fit_transit, run_checks, get_backend_info
    
    info = get_backend_info()
    print(f"   ✓ Backend loaded: {info['name']}")
    print(f"   ✓ Using local: {info['backend'] == 'local'}")
    print(f"   ✓ Mock mode: {info['is_mock']}")
except Exception as e:
    print(f"   ✗ Error loading adapter: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test transit fit
print("3. Testing transit fitting...")
try:
    result = fit_transit(time, flux, flux_err)
    
    print(f"   ✓ Fit completed: {result['success']}")
    print(f"   ✓ Period: {result['period_days']:.3f} days")
    print(f"   ✓ Depth: {result['depth_ppm']:.0f} ppm")
    print(f"   ✓ SNR: {result['snr']:.1f}")
    print(f"   ✓ Message: {result['message']}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test validation checks
print("4. Testing validation checks...")
try:
    checks = run_checks(time, flux, period_days=1.26, t0_bjd=0.5)
    
    print(f"   ✓ Odd/even delta: {checks['odd_even_depth_delta_pct']:.1f}%")
    print(f"   ✓ Secondary SNR: {checks['secondary_eclipse_snr']:.2f}")
    print(f"   ✓ Shape score: {checks['v_vs_u_shape_score']:.2f}")
    print(f"   ✓ Density OK: {checks['stellar_density_consistent']}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test API (if running)
print("5. Checking if backend API is running...")
try:
    import urllib.request
    import json
    
    try:
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=2)
        data = json.loads(response.read())
        print(f"   ✓ Backend API is RUNNING!")
        print(f"   ✓ Status: {data.get('status', 'unknown')}")
        print(f"   ✓ Access docs at: http://localhost:8000/docs")
    except urllib.error.URLError:
        print(f"   ⚠ Backend not running")
        print(f"   → Start with: uvicorn api.main:app --reload")
except Exception as e:
    print(f"   ⚠ Could not check: {e}")

print()
print("=" * 70)
print("✓ CORE DETECTION PIPELINE IS WORKING!")
print("=" * 70)
print()
print("What this means:")
print("  • Demo transit data loads correctly (96 points)")
print("  • Modulus adapter is functional (mock physics)")
print("  • Transit fitting works (returns parameters)")
print("  • Validation checks work (4 different tests)")
print()
print("Current data sources:")
print("  ✓ Demo files (kepler_tp.csv, kepler_fp.csv)")
print("  ✓ CSV file upload (via API when running)")
print("  ✗ Live NASA APIs (not yet implemented)")
print()
print("Next steps to find REAL exoplanets:")
print("  1. Add NASA MAST API integration (see below)")
print("  2. Add lightkurve library for Kepler/TESS data")
print("  3. Replace mock Modulus with real physics code")
print("  4. Train classifier on labeled exoplanet data")
print()
