#!/usr/bin/env python3
"""
Run exoplanet detection on REAL NASA data!
"""
import requests
import json
import time

API_BASE = "http://localhost:8888"

print("=" * 80)
print("🔭 EXOPLANET DETECTION - REAL NASA DATA")
print("=" * 80)
print()

# Step 1: Check API
print("1. Checking API status...")
response = requests.get(f"{API_BASE}/health")
if response.status_code == 200:
    print("   ✅ API is healthy!")
else:
    print(f"   ❌ API error: {response.status_code}")
    exit(1)

# Step 2: Check NASA data availability
print("\n2. Checking NASA data access...")
response = requests.get(f"{API_BASE}/nasa/available")
data = response.json()
if data['available']:
    print(f"   ✅ NASA data access: AVAILABLE")
    print(f"   ✅ Missions: {', '.join(data['missions'])}")
    print(f"   ✅ Confirmed planets: {len(data['confirmed_planets'])}")
else:
    print(f"   ⚠️  {data['message']}")

# Step 3: List confirmed planets
print("\n3. Available confirmed planets:")
response = requests.get(f"{API_BASE}/nasa/confirmed-planets")
planets = response.json()['planets']
for i, p in enumerate(planets[:6], 1):
    print(f"   {i}. {p['name']:15s} - Period: {p.get('period', 'N/A')}d, {p.get('note', '')}")

# Step 4: Fetch Kepler-90i (8-planet system)
print("\n4. Fetching Kepler-90i from NASA archives...")
print("   (This is a CONFIRMED exoplanet - we should detect it!)")
response = requests.post(
    f"{API_BASE}/nasa/fetch",
    json={
        "target_id": "Kepler-90i",
        "mission": "Kepler"
    },
    timeout=120
)

if response.status_code == 200:
    dataset = response.json()
    print(f"   ✅ Downloaded {dataset['num_points']} data points")
    print(f"   ✅ Time span: {dataset['time_span_days']:.1f} days")
    print(f"   ✅ Dataset ID: {dataset['dataset_id']}")
    dataset_id = dataset['dataset_id']
else:
    print(f"   ❌ Failed to fetch data: {response.status_code}")
    print(f"   {response.text}")
    exit(1)

# Step 5: Run detection
print("\n5. Running exoplanet detection...")
print("   (BLS search + Transit fitting + Validation)")
response = requests.post(
    f"{API_BASE}/api/run",
    json={
        "dataset_id": dataset_id,
        "min_period": 10.0,  # Kepler-90i has 14.45d period
        "max_period": 20.0,
        "snr_threshold": 5.0
    }
)

if response.status_code == 200:
    job = response.json()
    job_id = job['job_id']
    print(f"   ✅ Detection job started: {job_id}")
else:
    print(f"   ❌ Failed to start job: {response.status_code}")
    exit(1)

# Step 6: Poll for results
print("\n6. Waiting for detection to complete...")
max_wait = 120  # 2 minutes
start_time = time.time()

while time.time() - start_time < max_wait:
    response = requests.get(f"{API_BASE}/api/status/{job_id}")
    status = response.json()
    
    progress = status.get('progress', 0)
    stage = status.get('stage', 'unknown')
    state = status.get('status', 'unknown')
    
    print(f"   Progress: {progress}% - {stage}")
    
    if state == 'completed':
        print("   ✅ Detection complete!")
        break
    elif state == 'failed':
        print(f"   ❌ Detection failed: {status.get('error', 'unknown')}")
        exit(1)
    
    time.sleep(2)

# Step 7: Get results
print("\n7. Retrieving results...")
response = requests.get(f"{API_BASE}/api/results/{job_id}")

if response.status_code == 200:
    candidates = response.json()
    print(f"   ✅ Found {len(candidates)} candidate(s)!")
    
    print("\n" + "=" * 80)
    print("🪐 DETECTION RESULTS - Kepler-90i")
    print("=" * 80)
    
    for i, c in enumerate(candidates, 1):
        print(f"\nCandidate #{i}:")
        print(f"  Period:        {c['period']:.3f} days")
        print(f"  Depth:         {c['depth']:.0f} ppm")
        print(f"  SNR:           {c['snr']:.1f}")
        print(f"  Probability:   {c['probability']:.1%}")
        print(f"  Disposition:   {c['disposition']}")
        
        flags = c.get('flags', {})
        if flags:
            print(f"\n  Validation Checks:")
            print(f"    Odd/even delta:   {flags.get('odd_even_depth_delta_pct', 0):.1f}%")
            print(f"    Secondary SNR:    {flags.get('secondary_eclipse_snr', 0):.2f}")
            print(f"    Shape score:      {flags.get('v_vs_u_shape_score', 0):.2f}")
            print(f"    Density OK:       {flags.get('stellar_density_consistent', False)}")
    
    # Compare to known values
    print("\n" + "=" * 80)
    print("📊 COMPARISON TO PUBLISHED VALUES")
    print("=" * 80)
    print("\nKnown Kepler-90i parameters:")
    print("  Period:   14.45 days")
    print("  Depth:    ~900 ppm")
    print("\nOur detection:")
    if candidates:
        print(f"  Period:   {candidates[0]['period']:.2f} days")
        print(f"  Depth:    {candidates[0]['depth']:.0f} ppm")
        
        period_diff = abs(candidates[0]['period'] - 14.45) / 14.45 * 100
        print(f"\n  Period accuracy: {100-period_diff:.1f}%")
        
        if period_diff < 10:
            print("  ✅ CONFIRMED - We detected Kepler-90i!")
        else:
            print("  ⚠️  Period differs significantly")

else:
    print(f"   ❌ Failed to get results: {response.status_code}")

print("\n" + "=" * 80)
print("Detection complete! Check results above.")
print("=" * 80)
