"""Debugging utilities for shape checking and NaN detection."""
from __future__ import annotations

from typing import List, Optional, Tuple
import numpy as np


class ShapeChecker:
    """Validates tensor shapes during execution."""

    def __init__(self, strict: bool = True) -> None:
        self.strict = strict
        self.errors: List[str] = []

    def check_matmul(self, a_shape: Tuple[int, ...], b_shape: Tuple[int, ...]) -> bool:
        """Check matrix multiplication shape compatibility."""
        if len(a_shape) < 2 or len(b_shape) < 2:
            error = f"Matmul requires 2D+ tensors, got shapes {a_shape} @ {b_shape}"
            self.errors.append(error)
            if self.strict:
                raise ValueError(error)
            return False

        if a_shape[-1] != b_shape[-2]:
            error = f"Matmul shape mismatch: {a_shape[-1]} != {b_shape[-2]}"
            self.errors.append(error)
            if self.strict:
                raise ValueError(error)
            return False

        return True

    def check_broadcast(self, shape_a: Tuple[int, ...], shape_b: Tuple[int, ...]) -> bool:
        """Check if two shapes are broadcast-compatible."""
        for dim_a, dim_b in zip(reversed(shape_a), reversed(shape_b)):
            if dim_a != 1 and dim_b != 1 and dim_a != dim_b:
                error = f"Broadcast incompatible: {shape_a} vs {shape_b}"
                self.errors.append(error)
                if self.strict:
                    raise ValueError(error)
                return False
        return True

    def check_reduction(self, tensor_shape: Tuple[int, ...], axis: Optional[int]) -> bool:
        """Check reduction axis validity."""
        if axis is not None and (axis < 0 or axis >= len(tensor_shape)):
            error = f"Reduction axis {axis} out of bounds for shape {tensor_shape}"
            self.errors.append(error)
            if self.strict:
                raise ValueError(error)
            return False
        return True

    def reset(self) -> None:
        """Clear all errors."""
        self.errors.clear()


class NaNDetector:
    """Detects NaN/Inf in tensor outputs."""

    def __init__(self, raise_on_nan: bool = True, raise_on_inf: bool = True) -> None:
        self.raise_on_nan = raise_on_nan
        self.raise_on_inf = raise_on_inf
        self.nan_count = 0
        self.inf_count = 0

    def check(self, tensor: np.ndarray, context: str = "") -> bool:
        """Check tensor for NaN/Inf values."""
        has_nan = np.isnan(tensor).any()
        has_inf = np.isinf(tensor).any()

        if has_nan:
            self.nan_count += 1
            if self.raise_on_nan:
                raise ValueError(f"NaN detected in {context}: {tensor}")
            return False

        if has_inf:
            self.inf_count += 1
            if self.raise_on_inf:
                raise ValueError(f"Inf detected in {context}: {tensor}")
            return False

        return True

    def summary(self) -> dict:
        """Return detection summary."""
        return {
            "nan_count": self.nan_count,
            "inf_count": self.inf_count,
        }

    def reset(self) -> None:
        """Reset counters."""
        self.nan_count = 0
        self.inf_count = 0


