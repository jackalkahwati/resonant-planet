#!/usr/bin/env python3
"""
2D Heat Equation Solver using Modulus 5-point stencil.

Solves: ∂u/∂t = α ∇²u
with fixed boundary conditions.
"""
from __future__ import annotations

import argparse
import time
import numpy as np

from modulus_core import (
    enable_deterministic_mode,
    Profiler,
    Graph,
    Node,
    Tensor,
    GraphExecutor,
    ExecutionContext,
)
from modulus_core.kernels.optimized import stencil_5pt_opt


def setup_initial_condition(nx: int, ny: int) -> np.ndarray:
    """Create initial temperature distribution with hot center."""
    u = np.zeros((nx, ny), dtype=np.float64)
    # Hot spot in the center
    cx, cy = nx // 2, ny // 2
    radius = min(nx, ny) // 8
    for i in range(nx):
        for j in range(ny):
            if (i - cx)**2 + (j - cy)**2 < radius**2:
                u[i, j] = 100.0
    return u


def compute_energy(u: np.ndarray) -> float:
    """Compute total energy (integral of temperature)."""
    return float(np.sum(u))


def main():
    parser = argparse.ArgumentParser(description="2D Heat Equation Solver")
    parser.add_argument("--nx", type=int, default=128, help="Grid points in x")
    parser.add_argument("--ny", type=int, default=128, help="Grid points in y")
    parser.add_argument("--nt", type=int, default=100, help="Number of time steps")
    parser.add_argument("--alpha", type=float, default=0.01, help="Thermal diffusivity")
    parser.add_argument("--dt", type=float, default=0.01, help="Time step size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default="heat_output.npy", help="Output file")
    args = parser.parse_args()

    # Enable deterministic mode
    enable_deterministic_mode(seed=args.seed, strict=True)
    print(f"Deterministic mode enabled with seed={args.seed}")

    # Initialize
    u = setup_initial_condition(args.nx, args.ny)
    initial_energy = compute_energy(u)
    print(f"Initial energy: {initial_energy:.2f}")

    # Profiler
    profiler = Profiler()

    # Time-stepping
    print(f"Running {args.nt} time steps...")
    start_time = time.perf_counter()

    for step in range(args.nt):
        profiler.start_kernel("stencil_5pt", input_shapes=[u.shape])

        # Apply 5-point stencil for Laplacian
        rng = np.random.default_rng(args.seed)
        laplacian = stencil_5pt_opt(
            u,
            attributes={},
            rng=rng,
            deterministic=True,
        )

        # Explicit Euler time step
        u = u + args.alpha * args.dt * laplacian

        # Enforce boundary conditions (fixed at 0)
        u[0, :] = 0.0
        u[-1, :] = 0.0
        u[:, 0] = 0.0
        u[:, -1] = 0.0

        flops = args.nx * args.ny * 5  # 5 operations per point
        bytes_moved = u.nbytes * 6  # Read u 5 times + write once
        profiler.end_kernel(flops=flops, bytes_moved=bytes_moved, output_shape=u.shape)

        if step % 10 == 0:
            energy = compute_energy(u)
            max_temp = np.max(u)
            print(f"Step {step:4d}: max_temp={max_temp:6.2f}, energy={energy:8.1f}")

    elapsed = time.perf_counter() - start_time
    print(f"\nCompleted in {elapsed:.3f}s ({args.nt/elapsed:.1f} steps/sec)")

    # Profiler summary
    summary = profiler.summary()
    print(f"\nProfiler Summary:")
    print(f"  Total kernels: {summary['total_kernels']}")
    print(f"  Total time: {summary['total_time_ms']:.2f} ms")
    print(f"  Avg latency: {summary['avg_latency_ms']:.3f} ms/kernel")

    # Save output
    np.save(args.output, u)
    print(f"\nFinal state saved to {args.output}")

    # Validate energy conservation (should be approximately conserved)
    final_energy = compute_energy(u)
    energy_change = abs(final_energy - initial_energy) / initial_energy * 100
    print(f"Energy change: {energy_change:.2f}%")


if __name__ == "__main__":
    main()


