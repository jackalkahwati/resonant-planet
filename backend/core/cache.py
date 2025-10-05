"""
Simple caching layer for expensive computations.
"""
from functools import lru_cache
import hashlib
import numpy as np


def hash_array(arr: np.ndarray) -> str:
    """Generate hash for numpy array."""
    return hashlib.md5(arr.tobytes()).hexdigest()


@lru_cache(maxsize=100)
def get_cached_preprocess(data_hash: str, time: tuple, flux: tuple, flux_err: tuple):
    """Cache preprocessing results - actual computation done elsewhere."""
    return None  # Placeholder for cache key


@lru_cache(maxsize=50)
def get_cached_bls(data_hash: str, min_period: float, max_period: float):
    """Cache BLS search results - actual computation done elsewhere."""
    return None  # Placeholder for cache key


def clear_cache():
    """Clear all caches."""
    get_cached_preprocess.cache_clear()
    get_cached_bls.cache_clear()
