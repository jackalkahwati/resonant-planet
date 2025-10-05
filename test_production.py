#!/usr/bin/env python3
"""
Production Integration Test
Tests the full stack: Vercel frontend + Railway backend
"""

import requests
import time
import sys

# Production URLs
FRONTEND_URL = "https://resonant-planet.vercel.app"
BACKEND_URL = "https://backend-api-production-6a91.up.railway.app"

def test_frontend():
    """Test that frontend is accessible"""
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200 and "Resonant" in response.text:
            print("   ✅ Frontend is live and responding")
            return True
        else:
            print(f"   ❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
        return False


def test_backend_health():
    """Test backend health endpoint"""
    print("\n🏥 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        data = response.json()
        print(f"   ✅ Backend: {data['name']} v{data['version']}")
        print(f"   ✅ Modulus: {data['modulus_backend']['name']} (mock={data['modulus_backend']['is_mock']})")
        return True
    except Exception as e:
        print(f"   ❌ Backend health check failed: {e}")
        return False


def test_datasets_endpoint():
    """Test datasets listing"""
    print("\n📊 Testing Datasets Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/datasets/", timeout=10)
        datasets = response.json()
        print(f"   ✅ Found {len(datasets)} datasets:")
        for ds in datasets:
            print(f"      - {ds['name']} ({ds['source']}, {ds['num_points']} points)")
        return True
    except Exception as e:
        print(f"   ❌ Datasets endpoint failed: {e}")
        return False


def test_full_detection_pipeline():
    """Test the complete detection pipeline"""
    print("\n🔬 Testing Full Detection Pipeline...")
    
    try:
        # 1. Start a run
        print("   → Starting detection run...")
        run_payload = {
            "dataset_id": "kepler_tp",
            "min_period_days": 0.5,
            "max_period_days": 3.0,
            "min_snr": 3.0,
            "max_candidates": 5
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/run/",
            json=run_payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to start run: {response.status_code} - {response.text}")
            return False
        
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"   ✅ Run started: {job_id}")
        
        # 2. Poll for completion
        print("   → Monitoring progress...")
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(f"{BACKEND_URL}/api/status/{job_id}", timeout=10)
            status = response.json()
            
            status_str = status.get("status", "unknown")
            progress = status.get("progress_pct", 0) or 0
            current_step = status.get("current_step", "")
            
            print(f"      [{status_str}] {progress:.0f}% - {current_step}")
            
            if status_str == "completed":
                print("   ✅ Detection completed!")
                break
            elif status_str == "failed":
                print(f"   ❌ Detection failed: {status.get('message', 'Unknown error')}")
                return False
            
            time.sleep(2)
        else:
            print("   ⚠️  Detection timed out (still may succeed)")
            return False
        
        # 3. Get results
        print("   → Fetching results...")
        response = requests.get(f"{BACKEND_URL}/api/results/{job_id}", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get results: {response.status_code}")
            return False
        
        results = response.json()
        total = results.get("total_candidates", 0)
        accepted = results.get("accepted_count", 0)
        rejected = results.get("rejected_count", 0)
        review = results.get("human_review_count", 0)
        
        print(f"   ✅ Results retrieved:")
        print(f"      - Total candidates: {total}")
        print(f"      - Accepted: {accepted}")
        print(f"      - Rejected: {rejected}")
        print(f"      - Human review: {review}")
        
        if total > 0:
            print(f"\n   📋 First candidate details:")
            first = results["candidates"][0]
            print(f"      - ID: {first['candidate_id']}")
            print(f"      - Period: {first['period_days']:.3f} days")
            print(f"      - Depth: {first['depth_ppm']:.1f} ppm")
            print(f"      - SNR: {first['snr']:.2f}")
            print(f"      - Action: {first['rl_action']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 RESONANT WORLDS EXPLORER - PRODUCTION INTEGRATION TEST")
    print("=" * 70)
    print(f"\nFrontend: {FRONTEND_URL}")
    print(f"Backend:  {BACKEND_URL}")
    
    results = {
        "Frontend": test_frontend(),
        "Backend Health": test_backend_health(),
        "Datasets API": test_datasets_endpoint(),
        "Detection Pipeline": test_full_detection_pipeline(),
    }
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        print("=" * 70)
        print(f"\n🌍 Visit: {FRONTEND_URL}")
        print(f"📚 API Docs: {BACKEND_URL}/docs")
        return 0
    else:
        print("❌ SOME TESTS FAILED. Please review errors above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
