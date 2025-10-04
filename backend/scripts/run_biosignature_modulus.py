"""Batch-run Modulus biosignature computations on uploaded datasets."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict

from core.biosignature_ingest import load_atmospheric_snapshot as load_snapshot
from core.biosignature_modulus_workflow import ModulusBiosignatureWorkflow


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV file with atmospheric/observation summary")
    parser.add_argument("--output", type=Path, default=Path("biosignature_results.json"))
    parser.add_argument("--modulus-url", default="http://localhost:8000")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    snapshot = load_snapshot(args.input)

    workflow = ModulusBiosignatureWorkflow(base_url=args.modulus_url, api_key=args.api_key)
    computations = workflow.run_composite_analysis(snapshot)

    payload = {
        "planet": snapshot.planet_name,
        "results": [
            {
                "metric": comp.metric_name,
                "value": comp.value,
                "confidence": comp.confidence,
                "trace_id": comp.trace_id,
                "explanation": comp.explanation,
            }
            for comp in computations
        ],
    }

    args.output.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()


