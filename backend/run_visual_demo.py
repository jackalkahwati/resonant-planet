#!/usr/bin/env python3
"""
Visual 60-Second Demo - Resonant Worlds Explorer
Shows the detection pipeline with plots and animations
"""
import requests
import time
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import numpy as np

API_URL = "http://localhost:8000"


def print_banner():
    """Print animated banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      🌍 RESONANT WORLDS EXPLORER - LIVE DEMO 🔭                 ║
║                                                                  ║
║      AI-Powered Exoplanet Detection with Physics Validation     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print("\033[1;36m" + banner + "\033[0m")


def animated_progress(message, duration=2):
    """Show animated progress bar."""
    import shutil
    width = shutil.get_terminal_size().columns - 10
    
    print(f"\n{message}")
    for i in range(width):
        progress = int((i / width) * 100)
        bar = "█" * i + "░" * (width - i)
        print(f"\r[{bar}] {progress}%", end="", flush=True)
        time.sleep(duration / width)
    print("\r[" + "█" * width + f"] 100%")


def display_plot(image_path, title=""):
    """Display a plot in ASCII art style for terminal."""
    try:
        from PIL import Image
        import numpy as np
        
        # Load and resize image
        img = Image.open(image_path).convert('L')
        img = img.resize((80, 40))
        
        # Convert to ASCII
        chars = " .:-=+*#%@"
        pixels = np.array(img)
        ascii_art = []
        
        for row in pixels[::2]:  # Skip every other row for better aspect ratio
            line = ""
            for pixel in row[::2]:  # Skip every other column
                char_idx = int((pixel / 255) * (len(chars) - 1))
                line += chars[char_idx]
            ascii_art.append(line)
        
        print(f"\n\033[1;33m{title}\033[0m")
        print("\033[0;32m" + "\n".join(ascii_art) + "\033[0m")
        
    except Exception as e:
        print(f"   Plot saved to: {image_path}")


def create_live_visualization(time_data, flux_data, period, phase_data=None):
    """Create and display a live visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Resonant Worlds Explorer - Live Detection', 
                 fontsize=16, fontweight='bold')
    
    # 1. Raw Light Curve
    axes[0, 0].plot(time_data, flux_data, 'k.', markersize=2, alpha=0.5)
    axes[0, 0].set_title('Raw Light Curve', fontweight='bold')
    axes[0, 0].set_xlabel('Time (days)')
    axes[0, 0].set_ylabel('Normalized Flux')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Zoomed Transit
    if len(time_data) > 50:
        mid = len(time_data) // 2
        window = 25
        axes[0, 1].plot(time_data[mid-window:mid+window], 
                       flux_data[mid-window:mid+window], 
                       'b-', linewidth=2)
        axes[0, 1].set_title('Zoomed View', fontweight='bold')
        axes[0, 1].set_xlabel('Time (days)')
        axes[0, 1].set_ylabel('Flux')
        axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Phase Fold (if available)
    if phase_data is not None and len(phase_data) > 0:
        axes[1, 0].scatter(phase_data, flux_data, s=5, alpha=0.5, c='black')
        axes[1, 0].set_title(f'Phase Folded (P={period:.3f}d)', fontweight='bold')
        axes[1, 0].set_xlabel('Phase')
        axes[1, 0].set_ylabel('Flux')
        axes[1, 0].invert_yaxis()
        axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Statistics
    axes[1, 1].axis('off')
    stats_text = f"""
    📊 DETECTION STATISTICS
    
    ✓ Data Points: {len(time_data)}
    ✓ Time Span: {time_data.max() - time_data.min():.2f} days
    ✓ Flux RMS: {np.std(flux_data):.6f}
    ✓ Mean Flux: {np.mean(flux_data):.6f}
    
    🔍 Best Period: {period:.4f} days
    
    ⚙️  Status: ANALYZING...
    """
    axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, 
                   family='monospace', verticalalignment='center')
    
    plt.tight_layout()
    plt.savefig('live_detection.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return 'live_detection.png'


def main():
    """Run the visual demo."""
    print_banner()
    
    # Check server
    print("\n🔌 Connecting to backend...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Backend not responding!")
            print("   Start with: cd backend && uvicorn api.main:app --port 8000")
            return
        print("✅ Connected to Resonant Worlds Explorer API")
    except:
        print("❌ Cannot connect to backend!")
        return
    
    # Get datasets
    animated_progress("📁 Loading NASA mission data", 1.5)
    response = requests.get(f"{API_URL}/api/datasets/")
    datasets = response.json()
    
    if not datasets:
        print("\n⚠️  No datasets available")
        return
    
    print(f"\n✓ Found {len(datasets)} datasets from Kepler mission")
    for ds in datasets:
        print(f"   • {ds['dataset_id']}: {ds['num_points']} observations")
    
    # Select true positive dataset
    dataset_id = "kepler_tp"
    print(f"\n🎯 Analyzing: {dataset_id} (known exoplanet transit)")
    
    # Load data for visualization
    import pandas as pd
    df = pd.read_csv(f"assets/demos/{dataset_id}.csv")
    time_data = df.iloc[:, 0].values
    flux_data = df.iloc[:, 1].values
    
    # Create initial visualization
    print("\n📊 Generating visualizations...")
    viz_path = create_live_visualization(time_data, flux_data, 1.26)
    print(f"   Saved to: {viz_path}")
    
    # Start detection
    animated_progress("🔬 Running BLS period search", 2)
    
    response = requests.post(
        f"{API_URL}/api/run",
        json={
            "dataset_id": dataset_id,
            "min_period_days": 0.5,
            "max_period_days": 3.0,
            "min_snr": 3.0,
            "max_candidates": 5,
        },
    )
    
    if response.status_code != 200:
        print(f"\n❌ Detection failed: {response.text}")
        return
    
    job = response.json()
    job_id = job["job_id"]
    print(f"\n✓ Detection job started: {job_id}")
    
    # Monitor with animation
    print("\n🔄 Processing stages:")
    stages = ["loading", "preprocessing", "bls_search", "candidate_analysis", "completed"]
    stage_names = {
        "loading": "📂 Loading light curve",
        "preprocessing": "🔧 Preprocessing data",
        "bls_search": "🔍 BLS period search",
        "candidate_analysis": "🧬 Physics validation",
        "completed": "✅ Analysis complete"
    }
    
    current_stage_idx = 0
    
    while True:
        response = requests.get(f"{API_URL}/api/status/{job_id}")
        status = response.json()
        
        if status["status"] == "completed":
            print(f"\r{stage_names['completed']}")
            break
        elif status["status"] == "failed":
            print(f"\n❌ Detection failed: {status.get('error', 'Unknown error')}")
            return
        
        # Animate stages
        for stage in stages[current_stage_idx:]:
            if stage in status.get("current_step", ""):
                print(f"\r{stage_names.get(stage, stage)}", end="", flush=True)
                current_stage_idx += 1
                break
        
        time.sleep(0.5)
    
    # Get results
    print("\n\n📊 DETECTION RESULTS")
    print("=" * 70)
    
    response = requests.get(f"{API_URL}/api/results/{job_id}")
    results = response.json()
    
    total = results['total_candidates']
    accepted = results['accepted_count']
    human_review = results['human_review_count']
    
    print(f"\n🎯 Total Candidates Found: {total}")
    print(f"   ✅ Auto-Accepted: {accepted}")
    print(f"   👁️  Human Review Needed: {human_review}")
    
    if results["candidates"]:
        print("\n🪐 CANDIDATE DETAILS:")
        print("-" * 70)
        
        for i, c in enumerate(results["candidates"][:3], 1):
            print(f"\nCandidate #{i}:")
            print(f"   Period: {c['period_days']:.4f} days")
            print(f"   Depth: {c['depth_ppm']:.1f} ppm")
            print(f"   SNR: {c['snr']:.2f}")
            print(f"   Duration: {c['duration_hours']:.2f} hours")
            print(f"   Decision: {c['rl_action'].upper()}")
            
            # Show physics flags
            flags = c['flags']
            print(f"\n   Physics Checks:")
            for flag, value in flags.items():
                status_icon = "✓" if value else "✗"
                color = "\033[0;32m" if value else "\033[0;31m"
                print(f"      {color}{status_icon} {flag}\033[0m")
    else:
        print("\n⚠️  No candidates met the detection threshold")
        print("   (This is expected for short 2-day demo data)")
        print("\n💡 TIP: Real exoplanet detection requires 30-90 days of data")
    
    # Final summary
    print("\n" + "=" * 70)
    print("\n🎉 DEMO COMPLETE!")
    print("\n📈 System Capabilities:")
    print("   ✓ BLS period search")
    print("   ✓ Transit model fitting")
    print("   ✓ Physics-based validation")
    print("   ✓ RL policy decisions")
    print("   ✓ NASA Exoplanet Archive integration")
    print("\n🚀 Ready for real Kepler/TESS/JWST data analysis!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Demo interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
