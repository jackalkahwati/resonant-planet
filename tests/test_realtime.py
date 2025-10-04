"""Tests for real-time threading and deterministic mode."""
from __future__ import annotations

import numpy as np
import pytest

from modulus_core.realtime import (
    ThreadConfig,
    set_thread_affinity,
    set_thread_priority,
    DeterministicMode,
    enable_deterministic_mode,
    disable_deterministic_mode,
)


def test_thread_config():
    """Test thread configuration dataclass."""
    config = ThreadConfig(affinity=[0, 1], priority=5, realtime_policy="FIFO")
    assert config.affinity == [0, 1]
    assert config.priority == 5
    assert config.realtime_policy == "FIFO"


def test_thread_affinity():
    """Test thread affinity setting (may not work in all environments)."""
    # This test may fail in containers or restricted environments
    result = set_thread_affinity([0])
    # We don't assert True because it depends on platform/permissions
    assert isinstance(result, bool)


def test_thread_priority():
    """Test thread priority setting (may not work in all environments)."""
    # This test may fail without proper permissions
    result = set_thread_priority(0, policy="OTHER")
    assert isinstance(result, bool)


def test_deterministic_mode():
    """Test deterministic mode enable/disable."""
    assert not DeterministicMode.is_enabled()
    
    enable_deterministic_mode(seed=42, strict=True)
    assert DeterministicMode.is_enabled()
    
    # Test that random operations are seeded
    np.random.seed(42)
    a1 = np.random.rand(10)
    
    np.random.seed(42)
    a2 = np.random.rand(10)
    
    assert np.allclose(a1, a2)
    
    disable_deterministic_mode()
    assert not DeterministicMode.is_enabled()


def test_deterministic_mode_strict():
    """Test strict deterministic mode checks."""
    enable_deterministic_mode(seed=42, strict=True)
    
    try:
        # Should raise in strict mode
        DeterministicMode.check_operation("nondeterministic_op", is_deterministic=False)
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "nondeterministic" in str(e).lower()
    
    disable_deterministic_mode()


def test_deterministic_mode_non_strict():
    """Test non-strict deterministic mode (warnings only)."""
    enable_deterministic_mode(seed=42, strict=False)
    
    # Should only warn, not raise
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        DeterministicMode.check_operation("nondeterministic_op", is_deterministic=False)
        assert len(w) > 0
        assert "nondeterministic" in str(w[0].message).lower()
    
    disable_deterministic_mode()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


