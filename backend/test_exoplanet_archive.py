#!/usr/bin/env python3
"""
Test NASA Exoplanet Archive Integration

Demonstrates:
1. Querying confirmed planet parameters
2. Validating detections against known planets
3. Searching habitable zone planets
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.data_sources import (
    query_exoplanet_archive,
    validate_detection,
    search_habitable_zone_planets
)


def test_query_planet():
    """Test querying a confirmed planet."""
    print("\n" + "="*70)
    print("TEST 1: Query Confirmed Planet Parameters")
    print("="*70)
    
    planets = ['Kepler-90 i', 'TOI-700 d', 'Kepler-452 b']
    
    for planet_name in planets:
        try:
            print(f"\n🔍 Querying: {planet_name}")
            params = query_exoplanet_archive(planet_name)
            
            print(f"  ✓ Planet: {params['pl_name']}")
            print(f"  ✓ Host Star: {params['hostname']}")
            if params['pl_orbper'] is not None:
                print(f"  ✓ Period: {params['pl_orbper']:.2f} days")
            if params['pl_rade'] is not None:
                print(f"  ✓ Radius: {params['pl_rade']:.2f} Earth radii")
            if params['pl_eqt'] is not None:
                print(f"  ✓ Temperature: {params['pl_eqt']:.0f} K")
            if params['pl_insol'] is not None:
                print(f"  ✓ Insolation: {params['pl_insol']:.2f} Earth flux")
            if params['sy_dist'] is not None:
                print(f"  ✓ Distance: {params['sy_dist']:.1f} parsecs")
            if params['disc_year'] is not None:
                print(f"  ✓ Discovered: {params['disc_year']} by {params['disc_facility']}")
            else:
                print(f"  ✓ Discovery facility: {params['disc_facility']}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_validate_detection():
    """Test validating detections against known planets."""
    print("\n" + "="*70)
    print("TEST 2: Validate Detections Against Known Planets")
    print("="*70)
    
    # Test cases: (target, period, depth_ppm, description)
    test_cases = [
        ('Kepler-90', 14.45, 900, 'Kepler-90i - Should match'),
        ('Kepler-90', 59.74, 700, 'Kepler-90g - Should match'),
        ('Kepler-90', 100.5, 500, 'Unknown signal - Should not match'),
        ('TOI-700', 37.42, 1000, 'TOI-700d - Should match'),
    ]
    
    for target, period, depth, description in test_cases:
        print(f"\n🔬 Testing: {description}")
        print(f"   Target: {target}, P={period}d, Depth={depth}ppm")
        
        try:
            result = validate_detection(target, period, depth, tolerance=0.1)
            
            if result['match_found']:
                print(f"   ✓ MATCH FOUND: {result['matched_planet']}")
                print(f"     Expected period: {result['expected_period']:.2f}d")
                print(f"     Difference: {result['period_difference']:.1f}%")
            else:
                print(f"   ✗ NO MATCH - Potentially new candidate!")
            
            if result['all_planets']:
                print(f"   Known planets in system: {len(result['all_planets'])}")
                for p in result['all_planets'][:3]:  # Show first 3
                    print(f"     - {p['name']}: P={p['period']:.2f}d")
                    
        except Exception as e:
            print(f"   ✗ Error: {e}")


def test_habitable_zone():
    """Test searching for habitable zone planets."""
    print("\n" + "="*70)
    print("TEST 3: Search Habitable Zone Planets")
    print("="*70)
    
    try:
        print(f"\n🌍 Searching for planets in habitable zone (0.5-1.5 Earth flux)...")
        planets = search_habitable_zone_planets(min_insol=0.5, max_insol=1.5, limit=10)
        
        print(f"   Found {len(planets)} planets\n")
        
        for i, planet in enumerate(planets[:10], 1):
            print(f"{i}. {planet['pl_name']} ({planet['hostname']})")
            parts = []
            if planet['pl_orbper'] is not None:
                parts.append(f"Period: {planet['pl_orbper']:.1f}d")
            if planet['pl_rade'] is not None:
                parts.append(f"Radius: {planet['pl_rade']:.2f} R⊕")
            if planet['pl_insol'] is not None:
                parts.append(f"Insolation: {planet['pl_insol']:.2f} S⊕")
            if parts:
                print(f"   {' | '.join(parts)}")
            
            parts2 = []
            if planet['pl_eqt'] is not None:
                parts2.append(f"Temp: {planet['pl_eqt']:.0f} K")
            if planet['sy_dist'] is not None:
                parts2.append(f"Distance: {planet['sy_dist']:.1f} pc")
            if parts2:
                print(f"   {' | '.join(parts2)}")
            print()
            
    except Exception as e:
        print(f"   ✗ Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("NASA EXOPLANET ARCHIVE INTEGRATION TEST")
    print("="*70)
    
    try:
        test_query_planet()
        test_validate_detection()
        test_habitable_zone()
        
        print("\n" + "="*70)
        print("✓ ALL TESTS COMPLETED")
        print("="*70)
        print("\nYou can now use these functions to:")
        print("  1. Query confirmed planet parameters")
        print("  2. Validate your detections against NASA's database")
        print("  3. Search for interesting targets (habitable zone, etc.)")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
