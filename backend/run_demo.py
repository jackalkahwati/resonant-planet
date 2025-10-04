#!/usr/bin/env python3
"""
Quick demo script for testing the Resonant Worlds Explorer backend.

Usage:
    python run_demo.py
"""
import requests
import time
import sys
from pathlib import Path

API_URL = "http://localhost:8000"


def check_server():
    """Check if server is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    print("=" * 70)
    print("Resonant Worlds Explorer - Demo Script")
    print("=" * 70)
    print()

    # Check server
    print("1. Checking server status...")
    if not check_server():
        print("   ❌ Server not responding at", API_URL)
        print("   Start the server first:")
        print("   $ uvicorn api.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    print("   ✓ Server is running")
    print()

    # Get backend info
    response = requests.get(f"{API_URL}/")
    info = response.json()
    print(f"   Backend: {info['modulus_backend']['name']}")
    print(f"   Using local Modulus: {info['modulus_backend']['backend'] == 'local'}")
    print()

    # List datasets
    print("2. Listing available datasets...")
    response = requests.get(f"{API_URL}/api/datasets/")
    datasets = response.json()
    print(f"   Found {len(datasets)} datasets:")
    for ds in datasets:
        print(f"   - {ds['dataset_id']}: {ds['num_points']} points, {ds['time_span_days']:.1f} days")
    print()

    if not datasets:
        print("   ⚠️  No datasets found. Make sure DEMO_MODE=true and demo files exist.")
        print("   Demo files should be in: backend/assets/demos/")
        return

    # Select first dataset
    dataset_id = datasets[0]["dataset_id"]
    print(f"3. Running detection on dataset: {dataset_id}...")

    # Start run
    response = requests.post(
        f"{API_URL}/api/run",
        json={
            "dataset_id": dataset_id,
            "min_period_days": 0.5,
            "max_period_days": 10.0,
            "min_snr": 7.0,
            "max_candidates": 5,
        },
    )

    if response.status_code != 200:
        print(f"   ❌ Failed to start run: {response.text}")
        return

    job = response.json()
    job_id = job["job_id"]
    print(f"   ✓ Started job: {job_id}")
    print()

    # Monitor progress
    print("4. Monitoring progress...")
    last_stage = None

    while True:
        response = requests.get(f"{API_URL}/api/status/{job_id}")
        status = response.json()

        if status["stage"] != last_stage:
            print(f"   [{status['progress']:5.1f}%] {status['stage']}: {status['message']}")
            last_stage = status["stage"]

        if status["status"] == "completed":
            print("   ✓ Job completed!")
            break
        elif status["status"] == "failed":
            print(f"   ❌ Job failed: {status['message']}")
            return

        time.sleep(1)

    print()

    # Get results
    print("5. Retrieving results...")
    response = requests.get(f"{API_URL}/api/results/{job_id}")
    results = response.json()

    print(f"   Total candidates: {results['total_candidates']}")
    print(f"   - Accepted: {results['accepted_count']}")
    print(f"   - Rejected: {results['rejected_count']}")
    print(f"   - Human review: {results['human_review_count']}")
    print()

    # Show candidates
    if results["candidates"]:
        print("6. Candidate summary:")
        print()
        print("   ID          | Period (d) | Depth (ppm) | SNR  | Action")
        print("   " + "-" * 62)

        for i, c in enumerate(results["candidates"], 1):
            print(
                f"   {c['candidate_id'][:12]:<12}| {c['period_days']:10.4f} | {c['depth_ppm']:11.1f} | {c['snr']:4.1f} | {c['rl_action']}"
            )

        print()

        # Show flags for first candidate
        if results["candidates"]:
            c = results["candidates"][0]
            print("7. Physics flags for first candidate:")
            for flag, value in c["flags"].items():
                status = "✓" if value else "✗"
                print(f"   {status} {flag}")
            print()

    # Download report
    print("8. Downloading PDF report...")
    response = requests.get(f"{API_URL}/api/report/{job_id}")

    if response.status_code == 200:
        output_path = Path(f"demo_report_{job_id}.pdf")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"   ✓ Saved to: {output_path}")
        print(f"   File size: {len(response.content) / 1024:.1f} KB")
    else:
        print(f"   ⚠️  Could not generate report: {response.text}")

    print()
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
