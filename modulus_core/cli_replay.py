#!/usr/bin/env python3
"""CLI tool for replaying deterministic Modulus executions."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from modulus_core.replay import ReplayConfig, replay_execution
from modulus_core.executor import GraphExecutor
from modulus_core.kernels import kernel_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay deterministic Modulus execution")
    parser.add_argument("config", type=Path, help="Path to replay config JSON")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"Error: config file {args.config} not found", file=sys.stderr)
        return 1

    config = ReplayConfig.from_file(args.config)
    executor = GraphExecutor(kernel_registry=kernel_registry())
    
    if args.verbose:
        print(f"Replaying execution with seed={config.seed}, config_hash={config.config_hash}")

    try:
        result = replay_execution(config, executor)
        print(f"Execution successful. Config hash verified: {result.config_hash}")
        print(f"Output buffers: {list(result.buffers.keys())}")
        return 0
    except ValueError as e:
        print(f"Replay failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


