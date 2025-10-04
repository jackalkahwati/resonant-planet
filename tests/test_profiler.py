"""Tests for profiler and debugger tools."""
from __future__ import annotations

import numpy as np
import pytest

from modulus_core.profiler import (
    Profiler,
    KernelProfile,
    roofline_analysis,
    ShapeChecker,
    NaNDetector,
)


def test_profiler_basic():
    """Test basic profiling workflow."""
    profiler = Profiler()

    profiler.start_kernel("dense_matmul", input_shapes=[(100, 100), (100, 100)])
    # Simulate some work
    result = np.dot(np.random.rand(100, 100), np.random.rand(100, 100))
    profiler.end_kernel(flops=2 * 100**3, bytes_moved=3 * 100 * 100 * 8, output_shape=(100, 100))

    summary = profiler.summary()
    assert summary["total_kernels"] == 1
    assert summary["total_time_ms"] > 0
    assert len(summary["kernel_breakdown"]) == 1


def test_roofline_analysis():
    """Test roofline model computation."""
    profile = KernelProfile(
        kernel_name="test_kernel",
        latency_ms=10.0,
        flops=int(1e9),
        bytes_moved=int(1e8),
        start_time=0.0,
        end_time=0.01,
    )

    analysis = roofline_analysis(
        profile,
        peak_flops=1e12,
        peak_bandwidth=100e9,
    )

    assert "operational_intensity" in analysis
    assert "bottleneck" in analysis
    assert analysis["bottleneck"] in ["compute_bound", "memory_bound"]


def test_shape_checker():
    """Test shape validation."""
    checker = ShapeChecker(strict=False)

    assert checker.check_matmul((10, 20), (20, 30))
    assert not checker.check_matmul((10, 20), (10, 30))
    assert len(checker.errors) == 1

    checker.reset()
    assert len(checker.errors) == 0


def test_nan_detector():
    """Test NaN/Inf detection."""
    detector = NaNDetector(raise_on_nan=False, raise_on_inf=False)

    clean_tensor = np.random.rand(10, 10)
    assert detector.check(clean_tensor, context="clean")

    nan_tensor = np.array([1.0, 2.0, np.nan, 4.0])
    assert not detector.check(nan_tensor, context="nan_test")
    assert detector.nan_count == 1

    inf_tensor = np.array([1.0, np.inf, 3.0])
    assert not detector.check(inf_tensor, context="inf_test")
    assert detector.inf_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


