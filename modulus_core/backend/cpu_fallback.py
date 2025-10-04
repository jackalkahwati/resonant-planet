from __future__ import annotations

from typing import Any, Callable
import numpy as np


class CPUBackend:
    """CPU fallback backend for parity testing and development."""
    
    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def run(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute kernel function directly on CPU."""
        return func(*args, rng=self.rng, deterministic=True, **kwargs)

    def validate_against(self, sim_result: np.ndarray, cpu_result: np.ndarray, rtol: float = 1e-5) -> bool:
        """Check parity between simulator and CPU results."""
        return np.allclose(sim_result, cpu_result, rtol=rtol)


