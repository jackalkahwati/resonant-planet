"""Profiler for collecting kernel performance metrics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import numpy as np


@dataclass
class KernelProfile:
    """Profile data for a single kernel execution."""
    kernel_name: str
    latency_ms: float
    flops: int
    bytes_moved: int
    start_time: float
    end_time: float
    input_shapes: List[tuple] = field(default_factory=list)
    output_shape: Optional[tuple] = None

    def gflops(self) -> float:
        """Compute GFLOP/s."""
        if self.latency_ms == 0:
            return 0.0
        return (self.flops / 1e9) / (self.latency_ms / 1000.0)

    def bandwidth_gbps(self) -> float:
        """Compute effective bandwidth in GB/s."""
        if self.latency_ms == 0:
            return 0.0
        return (self.bytes_moved / 1e9) / (self.latency_ms / 1000.0)


class Profiler:
    """Performance profiler for tracking kernel execution metrics."""

    def __init__(self) -> None:
        self.profiles: List[KernelProfile] = []
        self.active_profile: Optional[KernelProfile] = None

    def start_kernel(
        self,
        kernel_name: str,
        input_shapes: Optional[List[tuple]] = None,
    ) -> None:
        """Start profiling a kernel."""
        self.active_profile = KernelProfile(
            kernel_name=kernel_name,
            latency_ms=0.0,
            flops=0,
            bytes_moved=0,
            start_time=time.perf_counter(),
            end_time=0.0,
            input_shapes=input_shapes or [],
        )

    def end_kernel(
        self,
        flops: int = 0,
        bytes_moved: int = 0,
        output_shape: Optional[tuple] = None,
    ) -> None:
        """End profiling for the active kernel."""
        if self.active_profile is None:
            return

        self.active_profile.end_time = time.perf_counter()
        self.active_profile.latency_ms = (
            self.active_profile.end_time - self.active_profile.start_time
        ) * 1000.0
        self.active_profile.flops = flops
        self.active_profile.bytes_moved = bytes_moved
        self.active_profile.output_shape = output_shape

        self.profiles.append(self.active_profile)
        self.active_profile = None

    def summary(self) -> Dict[str, any]:
        """Generate summary statistics."""
        if not self.profiles:
            return {"total_kernels": 0}

        total_time_ms = sum(p.latency_ms for p in self.profiles)
        total_flops = sum(p.flops for p in self.profiles)
        total_bytes = sum(p.bytes_moved for p in self.profiles)

        return {
            "total_kernels": len(self.profiles),
            "total_time_ms": total_time_ms,
            "total_gflops": total_flops / 1e9,
            "total_bytes_gb": total_bytes / 1e9,
            "avg_latency_ms": total_time_ms / len(self.profiles),
            "kernel_breakdown": [
                {
                    "name": p.kernel_name,
                    "latency_ms": p.latency_ms,
                    "gflops": p.gflops(),
                    "bandwidth_gbps": p.bandwidth_gbps(),
                }
                for p in self.profiles
            ],
        }

    def reset(self) -> None:
        """Clear all profiling data."""
        self.profiles.clear()
        self.active_profile = None


def roofline_analysis(
    profile: KernelProfile,
    peak_flops: float = 1e12,
    peak_bandwidth: float = 100e9,
) -> Dict[str, any]:
    """
    Compute roofline analysis for a kernel.
    
    Args:
        profile: Kernel profile data
        peak_flops: Peak FLOP/s of hardware
        peak_bandwidth: Peak bandwidth in bytes/s
        
    Returns:
        Analysis dict with operational intensity and bottleneck classification
    """
    if profile.bytes_moved == 0:
        return {"error": "No bytes moved, cannot compute operational intensity"}

    operational_intensity = profile.flops / profile.bytes_moved
    compute_bound_threshold = peak_flops / peak_bandwidth

    achieved_gflops = profile.gflops() * 1e9
    achieved_bandwidth = profile.bandwidth_gbps() * 1e9

    if operational_intensity > compute_bound_threshold:
        bottleneck = "compute_bound"
        efficiency = achieved_gflops / peak_flops
    else:
        bottleneck = "memory_bound"
        efficiency = achieved_bandwidth / peak_bandwidth

    return {
        "operational_intensity": operational_intensity,
        "compute_bound_threshold": compute_bound_threshold,
        "bottleneck": bottleneck,
        "efficiency": efficiency,
        "achieved_gflops": achieved_gflops / 1e9,
        "achieved_bandwidth_gbps": achieved_bandwidth / 1e9,
    }


