"""Debug version of batch scan with detailed error logging."""

from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path
from typing import Dict, List

from core.biosignature_ingest import load_atmospheric_snapshot
from core.biosignature_modulus_workflow import ModulusBiosignatureWorkflow


def run_debug_scan(
    data_dir: Path,
    modulus_url: str,
    api_key: str | None,
    timeout: int,
    retries: int,
) -> List[Dict]:
    workflow = ModulusBiosignatureWorkflow(base_url=modulus_url, api_key=api_key, timeout=timeout)
    results: List[Dict] = []
    errors: List[Dict] = []

    csv_files = list(data_dir.rglob("*.csv"))
    print(f"\n🔍 Found {len(csv_files)} CSV files to process\n")

    for idx, csv_file in enumerate(csv_files, 1):
        print(f"[{idx}/{len(csv_files)}] Processing: {csv_file.name}")
        
        try:
            # Load snapshot
            snapshot = load_atmospheric_snapshot(csv_file)
            print(f"   ✓ Loaded snapshot for {snapshot.planet_name}")
            print(f"     CO2: {snapshot.gas_mixing_ratios_ppm.get('CO2', 'N/A')} ppm")
            print(f"     CH4: {snapshot.gas_mixing_ratios_ppm.get('CH4', 'N/A')} ppm")
            print(f"     Eq Temp: {snapshot.equilibrium_temperature_k} K")
            print(f"     GH Temp: {snapshot.greenhouse_temperature_k} K")
            
            # Validate data
            if "CO2" in snapshot.gas_mixing_ratios_ppm and "CH4" in snapshot.gas_mixing_ratios_ppm:
                co2 = snapshot.gas_mixing_ratios_ppm["CO2"]
                ch4 = snapshot.gas_mixing_ratios_ppm["CH4"]
                
                # Check for invalid values
                if co2 <= 0 or ch4 <= 0:
                    print(f"   ⚠️  Invalid gas ratios (non-positive): CO2={co2}, CH4={ch4}")
                    errors.append({
                        "file": str(csv_file),
                        "planet": snapshot.planet_name,
                        "error": f"Invalid gas ratios: CO2={co2}, CH4={ch4}"
                    })
                    continue
                
                if co2 != co2 or ch4 != ch4:  # NaN check
                    print(f"   ⚠️  NaN gas ratios: CO2={co2}, CH4={ch4}")
                    errors.append({
                        "file": str(csv_file),
                        "planet": snapshot.planet_name,
                        "error": f"NaN gas ratios: CO2={co2}, CH4={ch4}"
                    })
                    continue
            
            # Try Modulus computation with retries
            computations = []
            last_error = None
            
            for attempt in range(retries):
                try:
                    print(f"   🔄 Attempt {attempt + 1}/{retries}...")
                    computations = workflow.run_composite_analysis(snapshot)
                    print(f"   ✅ Success! Got {len(computations)} computations")
                    for comp in computations:
                        print(f"      - {comp.metric_name}: {comp.value} (confidence: {comp.confidence})")
                    break
                except Exception as exc:
                    last_error = exc
                    print(f"   ⚠️  Attempt {attempt + 1} failed: {exc}")
                    if attempt == retries - 1:
                        print(f"   ❌ All retries exhausted")
                        errors.append({
                            "file": str(csv_file),
                            "planet": snapshot.planet_name,
                            "error": str(exc),
                            "traceback": traceback.format_exc()
                        })
                        computations = []

            # Build result entry
            entry = {
                "planet": snapshot.planet_name,
                "file": str(csv_file.relative_to(data_dir)),
                "snapshot_data": {
                    "co2_ppm": snapshot.gas_mixing_ratios_ppm.get("CO2"),
                    "ch4_ppm": snapshot.gas_mixing_ratios_ppm.get("CH4"),
                    "eq_temp_k": snapshot.equilibrium_temperature_k,
                    "gh_temp_k": snapshot.greenhouse_temperature_k,
                    "stellar_flux": snapshot.stellar_flux_rel_solar
                },
                "modulus": [
                    {
                        "metric": c.metric_name,
                        "value": None if isinstance(c.value, float) and (c.value != c.value) else c.value,
                        "confidence": c.confidence,
                    }
                    for c in computations
                ],
                "success": len(computations) > 0
            }
            results.append(entry)
            print()

        except Exception as exc:
            print(f"   ❌ Fatal error loading/processing {csv_file.name}: {exc}")
            errors.append({
                "file": str(csv_file),
                "error": str(exc),
                "traceback": traceback.format_exc()
            })
            print()

    # Print summary
    print("=" * 80)
    print(f"📊 SUMMARY")
    print("=" * 80)
    print(f"Total files: {len(csv_files)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {len(errors)}")
    print()
    
    if errors:
        print("❌ ERRORS:")
        for err in errors:
            print(f"\n   File: {err['file']}")
            print(f"   Error: {err['error']}")
            if 'traceback' in err:
                print(f"   Traceback (last 500 chars):")
                print("   " + err['traceback'][-500:].replace('\n', '\n   '))
    
    return results, errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("datasets", type=Path, help="Directory with datasets")
    parser.add_argument("--output", type=Path, default=Path("debug_batch_output.json"))
    parser.add_argument("--modulus-url", default="http://localhost:8000")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    results, errors = run_debug_scan(
        args.datasets,
        args.modulus_url,
        args.api_key,
        timeout=args.timeout,
        retries=max(1, args.retries),
    )

    output_data = {
        "results": results,
        "errors": errors,
        "summary": {
            "total": len(results) + len(errors),
            "successful": sum(1 for r in results if r.get('success', False)),
            "failed": len(errors)
        }
    }

    args.output.write_text(json.dumps(output_data, indent=2))
    print(f"\n💾 Results saved to: {args.output}")
    
    if errors:
        print(f"\n⚠️  {len(errors)} files had errors - check the output JSON for details")
        exit(1)
    else:
        print(f"\n✅ All {len(results)} files processed successfully!")
        exit(0)


if __name__ == "__main__":
    main()


