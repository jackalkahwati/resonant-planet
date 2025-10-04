"""Deterministic mode guards for real-time applications."""
from __future__ import annotations

import os
from typing import Optional


class DeterministicMode:
    """Global deterministic mode configuration."""
    
    _enabled: bool = False
    _strict: bool = True
    _seed: Optional[int] = None
    
    @classmethod
    def is_enabled(cls) -> bool:
        return cls._enabled
    
    @classmethod
    def enable(cls, seed: Optional[int] = None, strict: bool = True) -> None:
        """
        Enable deterministic mode.
        
        Args:
            seed: Random seed for reproducibility
            strict: If True, raise errors on nondeterministic operations
        """
        cls._enabled = True
        cls._strict = strict
        cls._seed = seed
        
        if seed is not None:
            import numpy as np
            np.random.seed(seed)
        
        # Set environment variables for deterministic behavior
        os.environ["PYTHONHASHSEED"] = str(seed) if seed is not None else "0"
        os.environ["MODULUS_DETERMINISTIC"] = "1"
    
    @classmethod
    def disable(cls) -> None:
        """Disable deterministic mode."""
        cls._enabled = False
        cls._strict = False
        cls._seed = None
        os.environ.pop("MODULUS_DETERMINISTIC", None)
    
    @classmethod
    def check_operation(cls, operation_name: str, is_deterministic: bool) -> None:
        """
        Check if an operation is allowed in deterministic mode.
        
        Args:
            operation_name: Name of the operation
            is_deterministic: Whether the operation is deterministic
            
        Raises:
            RuntimeError: If strict mode is enabled and operation is nondeterministic
        """
        if cls._enabled and not is_deterministic:
            error_msg = f"Nondeterministic operation '{operation_name}' not allowed in deterministic mode"
            if cls._strict:
                raise RuntimeError(error_msg)
            else:
                import warnings
                warnings.warn(error_msg)


def enable_deterministic_mode(seed: Optional[int] = None, strict: bool = True) -> None:
    """
    Enable deterministic mode globally.
    
    Args:
        seed: Random seed for reproducibility
        strict: If True, raise errors on nondeterministic operations
    """
    DeterministicMode.enable(seed=seed, strict=strict)


def disable_deterministic_mode() -> None:
    """Disable deterministic mode globally."""
    DeterministicMode.disable()


def require_deterministic(operation_name: str, is_deterministic: bool = True) -> None:
    """
    Assert that an operation is deterministic if mode is enabled.
    
    Args:
        operation_name: Name of the operation
        is_deterministic: Whether the operation is deterministic
    """
    DeterministicMode.check_operation(operation_name, is_deterministic)


