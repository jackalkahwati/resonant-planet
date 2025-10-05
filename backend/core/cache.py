"""
Simple caching layer for expensive computations.
Uses LRU (Least Recently Used) eviction strategy.
"""
import hashlib
import numpy as np
from collections import OrderedDict
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def hash_array(arr: np.ndarray) -> str:
    """Generate hash for numpy array."""
    return hashlib.md5(arr.tobytes()).hexdigest()


class LRUCache:
    """Simple LRU cache with statistics tracking."""
    
    def __init__(self, maxsize: int = 128):
        self.cache: OrderedDict = OrderedDict()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache, moving it to end (most recently used)."""
        if key in self.cache:
            self.hits += 1
            # Move to end to mark as recently used
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache, evicting oldest if full."""
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.maxsize:
                # Remove oldest (first) item
                evicted_key = next(iter(self.cache))
                self.cache.pop(evicted_key)
                logger.debug(f"Cache evicted: {evicted_key[:16]}...")
        
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all cached items and reset stats."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "usage_pct": len(self.cache) / self.maxsize * 100
        }


# Global cache instances
preprocess_cache = LRUCache(maxsize=100)
bls_cache = LRUCache(maxsize=50)


def clear_all_caches():
    """Clear all caches and reset statistics."""
    preprocess_cache.clear()
    bls_cache.clear()
    logger.info("All caches cleared")


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all caches."""
    return {
        "preprocess": preprocess_cache.stats(),
        "bls": bls_cache.stats()
    }
