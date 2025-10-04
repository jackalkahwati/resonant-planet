"""Integration tests for end-to-end Modulus pipeline."""
from __future__ import annotations

import numpy as np
import pytest

from modulus_core import (
    solve,
    ProblemSpec,
    enable_deterministic_mode,
)


def test_full_pipeline_linear_solve():
    """Test full pipeline with a simple linear problem."""
    enable_deterministic_mode(seed=42, strict=True)

    # Create a simple linear problem spec
    spec = ProblemSpec(
        problem_type="linear_system",
        domains=["algebra"],
        equations=["x + y = 5", "2*x - y = 1"],
        symbols={"x": {"unit": ""}, "y": {"unit": ""}},
        objective="solve",
    )

    # Solve (placeholder implementation will run)
    result = solve(spec)

    # Check that we got a result structure
    assert result is not None
    assert hasattr(result, "solution")
    assert hasattr(result, "certificate")
    assert hasattr(result, "trace")


def test_deterministic_execution_consistency():
    """Verify that multiple runs with same seed produce identical results."""
    spec = ProblemSpec(
        problem_type="linear_system",
        domains=["algebra"],
        equations=["x = 2"],
        symbols={"x": {"unit": ""}},
        objective="solve",
    )

    enable_deterministic_mode(seed=100, strict=True)
    result1 = solve(spec)

    enable_deterministic_mode(seed=100, strict=True)
    result2 = solve(spec)

    # Results should be identical
    assert result1.solution.values == result2.solution.values


def test_proof_generation():
    """Test that proof package is generated."""
    spec = ProblemSpec(
        problem_type="optimization",
        domains=["optimization"],
        equations=["x^2 + y^2"],
        symbols={"x": {"unit": ""}, "y": {"unit": ""}},
        objective="minimize",
    )

    result = solve(spec)

    # Check proof structure
    assert result.certificate is not None
    assert hasattr(result.certificate, "residuals")
    assert hasattr(result.certificate, "invariants")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


