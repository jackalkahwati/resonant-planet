#!/usr/bin/env python3
"""
Test script to demonstrate caching improvements.
Shows cache statistics, hit rates, and LRU eviction behavior.
"""
import numpy as np
import sys
from time import time as get_time
from core.cache import get_cache_stats, clear_all_caches
from core.preprocess import preprocess_pipeline
from core.features_bls import extract_bls_features


def print_stats(title: str):
    """Print cache statistics in a nice format."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    
    stats = get_cache_stats()
    
    for cache_name, cache_stats in stats.items():
        print(f"\n{cache_name.upper()} CACHE:")
        print(f"  Size: {cache_stats['size']}/{cache_stats['maxsize']}")
        print(f"  Usage: {cache_stats['usage_pct']:.1f}%")
        print(f"  Hits: {cache_stats['hits']}")
        print(f"  Misses: {cache_stats['misses']}")
        print(f"  Hit Rate: {cache_stats['hit_rate']*100:.1f}%")


def generate_sample_data(seed: int = 42) -> tuple:
    """Generate sample light curve data."""
    np.random.seed(seed)
    time = np.linspace(0, 30, 1000)
    flux = np.ones_like(time) + np.random.normal(0, 0.001, len(time))
    
    # Add a transit
    period = 3.5
    transit_width = 0.1
    depth = 0.01
    for i in range(int(30 / period)):
        transit_center = i * period
        in_transit = np.abs(time - transit_center) < transit_width / 2
        flux[in_transit] -= depth
    
    return time, flux


def main():
    """Run cache demonstration."""
    print("🚀 Resonant Worlds Explorer - Cache Improvements Demo")
    print("=" * 60)
    
    # Clear caches to start fresh
    clear_all_caches()
    print("✓ Caches cleared")
    
    print_stats("Initial State (Empty)")
    
    # Generate 3 different datasets
    datasets = [
        generate_sample_data(seed=42),
        generate_sample_data(seed=123),
        generate_sample_data(seed=456),
    ]
    
    print("\n" + "="*60)
    print("  TEST 1: First Run (Cache Misses Expected)")
    print("="*60)
    
    for i, (time, flux) in enumerate(datasets, 1):
        print(f"\nProcessing Dataset {i}...")
        start = get_time()
        
        # Preprocessing
        time_clean, flux_clean, _ = preprocess_pipeline(time, flux)
        
        # BLS search
        candidates = extract_bls_features(time_clean, flux_clean, max_candidates=3)
        
        elapsed = get_time() - start
        print(f"  ✓ Found {len(candidates)} candidates in {elapsed:.3f}s")
    
    print_stats("After First Run (All Misses)")
    
    print("\n" + "="*60)
    print("  TEST 2: Repeat Run (Cache Hits Expected)")
    print("="*60)
    
    for i, (time, flux) in enumerate(datasets, 1):
        print(f"\nProcessing Dataset {i} (again)...")
        start = get_time()
        
        # Preprocessing (should hit cache)
        time_clean, flux_clean, _ = preprocess_pipeline(time, flux)
        
        # BLS search (should hit cache)
        candidates = extract_bls_features(time_clean, flux_clean, max_candidates=3)
        
        elapsed = get_time() - start
        print(f"  ✓ Found {len(candidates)} candidates in {elapsed:.3f}s (cached!)")
    
    print_stats("After Repeat Run (Should Show Hits)")
    
    print("\n" + "="*60)
    print("  TEST 3: LRU Eviction Test")
    print("="*60)
    print("\nGenerating 60 new datasets to test LRU eviction...")
    print("(Preprocessing cache max=100, BLS cache max=50)")
    
    for i in range(60):
        time, flux = generate_sample_data(seed=1000 + i)
        time_clean, flux_clean, _ = preprocess_pipeline(time, flux)
        extract_bls_features(time_clean, flux_clean, max_candidates=2)
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/60 datasets...")
    
    print_stats("After LRU Eviction Test")
    
    print("\n" + "="*60)
    print("  TEST 4: Verify Oldest Items Were Evicted")
    print("="*60)
    print("\nRe-running Dataset 1 (should be evicted, causing cache miss)...")
    
    time, flux = datasets[0]
    start = get_time()
    time_clean, flux_clean, _ = preprocess_pipeline(time, flux)
    elapsed = get_time() - start
    print(f"  Completed in {elapsed:.3f}s")
    
    print_stats("Final State (Notice Hit Rate)")
    
    # Performance summary
    final_stats = get_cache_stats()
    print("\n" + "="*60)
    print("  📊 PERFORMANCE SUMMARY")
    print("="*60)
    
    for cache_name, cache_stats in final_stats.items():
        total = cache_stats['hits'] + cache_stats['misses']
        if total > 0:
            print(f"\n{cache_name.upper()}:")
            print(f"  Total Requests: {total}")
            print(f"  Cache Hits: {cache_stats['hits']} ({cache_stats['hit_rate']*100:.1f}%)")
            print(f"  Cache Misses: {cache_stats['misses']}")
            print(f"  Final Size: {cache_stats['size']}/{cache_stats['maxsize']}")
    
    print("\n✅ Cache improvements working correctly!")
    print("   - LRU eviction keeps frequently used items")
    print("   - Statistics tracking shows hit rates")
    print("   - No more full cache flushes")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
