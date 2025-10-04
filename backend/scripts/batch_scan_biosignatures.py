"""Batch scan datasets for biosignatures and compare with reference catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from core.biosignature_ingest import load_atmospheric_snapshot
from core.biosignature_modulus_workflow import ModulusBiosignatureWorkflow


def load_catalog(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return data.get("biosignatures", {})


def run_scan(
    data_dir: Path,
    catalog: Dict[str, str],
    modulus_url: str,
    api_key: str | None,
    timeout: int,
    retries: int,
) -> List[Dict]:
    workflow = ModulusBiosignatureWorkflow(base_url=modulus_url, api_key=api_key, timeout=timeout)
    results: List[Dict] = []

    for csv_file in data_dir.rglob("*.csv"):
        snapshot = load_atmospheric_snapshot(csv_file)
        computations = []
        for attempt in range(retries):
            try:
                computations = workflow.run_composite_analysis(snapshot)
                break
            except Exception as exc:
                if attempt == retries - 1:
                    computations = []
                    print(f"⚠️  Modulus request failed for {snapshot.planet_name}: {exc}")
                else:
                    continue
        reported = catalog.get(snapshot.planet_name, "unknown")

        entry = {
            "planet": snapshot.planet_name,
            "reported_status": reported,
            "modulus": [
                {
                    "metric": c.metric_name,
                    "value": None if isinstance(c.value, float) and (c.value != c.value) else c.value,
                    "confidence": c.confidence,
                }
                for c in computations
            ],
        }
        results.append(entry)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("datasets", type=Path, help="Directory with datasets")
    parser.add_argument("--catalog", type=Path, default=Path("assets/spectra_kepler/catalog.json"))
    parser.add_argument("--output", type=Path, default=Path("biosignature_batch.json"))
    parser.add_argument("--modulus-url", default="http://localhost:8000")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    catalog = load_catalog(args.catalog)
    results = run_scan(
        args.datasets,
        catalog,
        args.modulus_url,
        args.api_key,
        timeout=args.timeout,
        retries=max(1, args.retries),
    )

    args.output.write_text(json.dumps({"results": results}, indent=2))
    print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()


