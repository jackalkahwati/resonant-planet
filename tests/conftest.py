"""Pytest configuration and fixtures for Modulus tests."""
from __future__ import annotations

import pytest
import numpy as np

from modulus_core import enable_deterministic_mode, disable_deterministic_mode


@pytest.fixture(autouse=True)
def enable_determinism():
    """Enable deterministic mode for all tests."""
    enable_deterministic_mode(seed=42, strict=True)
    yield
    disable_deterministic_mode()


@pytest.fixture
def sample_matrix():
    """Provide a sample matrix for testing."""
    return np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)


@pytest.fixture
def sample_vector():
    """Provide a sample vector for testing."""
    return np.array([1.0, 2.0], dtype=np.float64)


@pytest.fixture
def sample_image():
    """Provide a sample image tensor for testing."""
    return np.random.rand(1, 3, 32, 32).astype(np.float64)


@pytest.fixture
def sample_sparse_matrix():
    """Provide a sample sparse matrix in CSR format."""
    data = np.array([1.0, 2.0, 3.0, 4.0])
    indices = np.array([0, 1, 1, 2])
    indptr = np.array([0, 2, 3, 4])
    return {"data": data, "indices": indices, "indptr": indptr}


