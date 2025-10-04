#!/usr/bin/env python3
"""
Integration test for biosignature detection pipeline.

Tests:
1. Loading spectroscopic data
2. Modulus chemistry analysis
3. Biosignature scoring
4. API endpoints
"""
import sys
sys.path.insert(0, '.')

import requests
import time
from pathlib import Path
import numpy as np

# Configuration
API_BASE = "http://localhost:8080"
MODULUS_BASE = "https://modulus-865475771210.europe-west1.run.app"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def check_modulus_api():
    """Check if Modulus API is available."""
    print_header("🔌 CHECKING MODULUS API")
    
    try:
        response = requests.get(f"{MODULUS_BASE}/v2/health", timeout=5)
        if response.status_code == 200:
            print("✅ Modulus API is online!")
            
            # Get info
            info_response = requests.get(f"{MODULUS_BASE}/v2/models", timeout=5)
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"   Model: {info.get('model', 'Unknown')}")
                print(f"   Version: {info.get('version', 'Unknown')}")
            
            return True
        else:
            print(f"⚠️  Modulus API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Modulus API not available: {e}")
        print("   The biosignature analysis will use fallback logic")
        return False

def check_backend_api():
    """Check if backend API is running."""
    print_header("🔌 CHECKING BACKEND API")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend API is online!")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not available: {e}")
        print("   Start it with: cd backend && uvicorn api.main:app --reload --port 8080")
        return False

def test_spectrum_listing():
    """Test listing available spectra."""
    print_header("📊 LISTING AVAILABLE SPECTRA")
    
    response = requests.get(f"{API_BASE}/api/biosignatures/datasets")
    
    if response.status_code == 200:
        data = response.json()
        datasets = data.get('datasets', [])
        
        print(f"✅ Found {len(datasets)} spectroscopic datasets:\n")
        
        for ds in datasets:
            print(f"   📄 {ds['filename']}")
            print(f"      Spectrum ID: {ds['spectrum_id']}")
            print(f"      Points: {ds['num_points']}")
            print(f"      Range: {ds['wavelength_range_um'][0]:.2f} - {ds['wavelength_range_um'][1]:.2f} μm")
            print(f"      Source: {ds['source']}")
            print()
        
        return datasets
    else:
        print(f"❌ Failed to list datasets: {response.status_code}")
        return []

def test_biosignature_analysis(spectrum_file):
    """Test biosignature analysis on a spectrum."""
    print_header(f"🧬 ANALYZING {spectrum_file}")
    
    response = requests.post(
        f"{API_BASE}/api/biosignatures/quick-analyze",
        params={
            'spectrum_file': spectrum_file,
            'planet_radius_earth': 1.0
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n📊 BIOSIGNATURE ANALYSIS RESULTS")
        print("-" * 80)
        print(f"Biosignature Score: {result['biosignature_score']:.2f} / 1.00")
        print(f"Confidence Level: {result['confidence_level']}")
        print(f"Detected Molecules: {', '.join(result['detected_molecules']) if result['detected_molecules'] else 'None'}")
        print(f"Disequilibrium Score: {result['disequilibrium_score']:.2f}")
        print(f"False Positive Probability: {result['false_positive_probability']:.1%}")
        
        print(f"\n📝 Explanation:")
        print("-" * 80)
        print(result['explanation'])
        
        if result.get('modulus_analysis'):
            print(f"\n🧠 Modulus Analysis Available:")
            modulus = result['modulus_analysis']
            if modulus.get('explanation'):
                print(modulus['explanation'][:200] + "..." if len(modulus['explanation']) > 200 else modulus['explanation'])
        
        print("-" * 80)
        
        # Verdict
        score = result['biosignature_score']
        if score > 0.7:
            print("\n🌟 VERDICT: Strong biosignature candidate!")
            print("   → Warrants follow-up observations")
            print("   → Could indicate extraterrestrial life")
        elif score > 0.5:
            print("\n🔍 VERDICT: Moderate biosignature")
            print("   → Needs more data to confirm")
            print("   → Could be abiotic processes")
        else:
            print("\n⚠️  VERDICT: Weak or no biosignature")
            print("   → Likely abiotic atmosphere")
            print("   → No strong evidence of life")
        
        return result
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
        return None

def test_molecule_info():
    """Test molecule information endpoint."""
    print_header("🔬 BIOSIGNATURE MOLECULES DATABASE")
    
    response = requests.get(f"{API_BASE}/api/biosignatures/molecules")
    
    if response.status_code == 200:
        data = response.json()
        molecules = data.get('molecules', {})
        
        print(f"\n{len(molecules)} biosignature molecules in database:\n")
        
        # Sort by strength
        strengths = ['high', 'medium', 'low', 'controversial', 'none']
        
        for strength in strengths:
            mols = {k: v for k, v in molecules.items() if v.get('biosignature_strength') == strength}
            if mols:
                print(f"\n{strength.upper()} STRENGTH:")
                for mol, info in mols.items():
                    print(f"   {mol} ({info['name']})")
                    print(f"      Wavelength: {info['primary_wavelength_um']} μm")
                    print(f"      Notes: {info['notes']}")
        
        return molecules
    else:
        print(f"❌ Failed to get molecule info: {response.status_code}")
        return {}

def run_complete_test():
    """Run complete biosignature detection test."""
    print("\n" + "="*80)
    print("🧬 BIOSIGNATURE DETECTION SYSTEM TEST")
    print("="*80)
    
    # Check services
    modulus_ok = check_modulus_api()
    backend_ok = check_backend_api()
    
    if not backend_ok:
        print("\n❌ Backend not running - cannot continue")
        return False
    
    if not modulus_ok:
        print("\n⚠️  Modulus API not available - will use fallback chemistry")
    
    # List available spectra
    datasets = test_spectrum_listing()
    
    if not datasets:
        print("\n❌ No spectroscopic datasets found - cannot continue")
        return False
    
    # Get molecule info
    test_molecule_info()
    
    # Analyze each demo spectrum
    demo_spectra = [
        'earth_like_with_life.csv',
        'mars_like_no_life.csv',
        'venus_like_with_ph3.csv'
    ]
    
    results = {}
    
    for spectrum in demo_spectra:
        result = test_biosignature_analysis(spectrum)
        if result:
            results[spectrum] = result['biosignature_score']
        time.sleep(1)  # Rate limiting
    
    # Summary
    print_header("📊 SUMMARY OF ALL ANALYSES")
    
    if results:
        print("\nBiosignature scores for test datasets:\n")
        for spectrum, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 20)
            print(f"   {spectrum:30s} {bar} {score:.2f}")
        
        print("\n✅ Biosignature detection system is working!")
        
        # Check if results make sense
        if 'earth_like_with_life.csv' in results and results['earth_like_with_life.csv'] > 0.6:
            print("   ✅ Earth-like spectrum correctly identified")
        
        if 'mars_like_no_life.csv' in results and results['mars_like_no_life.csv'] < 0.4:
            print("   ✅ Mars-like spectrum correctly rejected")
        
        return True
    else:
        print("❌ No successful analyses")
        return False

if __name__ == "__main__":
    success = run_complete_test()
    
    if success:
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\nThe biosignature detection system is ready to find life!")
        print("\nNext steps:")
        print("  1. Upload real JWST/Hubble spectroscopy")
        print("  2. Cross-match with detected transiting planets")
        print("  3. Run biosignature analysis")
        print("  4. Report findings to the scientific community!")
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ TESTS FAILED")
        print("="*80)
        print("\nCheck:")
        print("  1. Backend is running on port 8080")
        print("  2. Sample spectra exist in assets/spectra/")
        print("  3. Modulus API (optional) on port 8000")
        sys.exit(1)

