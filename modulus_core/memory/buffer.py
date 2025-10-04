"""Buffer management for explicit host and device memory."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import numpy as np


class BufferLocation(Enum):
    HOST = "host"
    DEVICE = "device"
    PINNED = "pinned"


@dataclass
class Buffer:
    name: str
    shape: Tuple[int, ...]
    dtype: np.dtype
    location: BufferLocation
    data: Optional[np.ndarray] = None
    device_id: int = 0

    def __post_init__(self) -> None:
        if self.data is None:
            self.data = np.zeros(self.shape, dtype=self.dtype)

    def nbytes(self) -> int:
        return self.data.nbytes if self.data is not None else 0

    def copy_to(self, target: Buffer) -> None:
        """Copy buffer contents to target buffer."""
        if self.shape != target.shape:
            raise ValueError(f"Shape mismatch: {self.shape} vs {target.shape}")
        if self.data is None or target.data is None:
            raise ValueError("Cannot copy null buffer")
        np.copyto(target.data, self.data)


class HostBuffer(Buffer):
    def __init__(self, name: str, shape: Tuple[int, ...], dtype: np.dtype = np.float64) -> None:
        super().__init__(name, shape, dtype, BufferLocation.HOST)


class DeviceBuffer(Buffer):
    def __init__(
        self,
        name: str,
        shape: Tuple[int, ...],
        dtype: np.dtype = np.float64,
        device_id: int = 0,
    ) -> None:
        super().__init__(name, shape, dtype, BufferLocation.DEVICE, device_id=device_id)


class BufferPool:
    """Simple buffer pool for reusing allocations."""

    def __init__(self, max_buffers: int = 100) -> None:
        self.max_buffers = max_buffers
        self.free_buffers: list[Buffer] = []
        self.allocated_buffers: dict[str, Buffer] = {}

    def allocate(
        self,
        name: str,
        shape: Tuple[int, ...],
        dtype: np.dtype,
        location: BufferLocation,
    ) -> Buffer:
        """Allocate or reuse a buffer."""
        for idx, buf in enumerate(self.free_buffers):
            if buf.shape == shape and buf.dtype == dtype and buf.location == location:
                reused = self.free_buffers.pop(idx)
                reused.name = name
                self.allocated_buffers[name] = reused
                return reused

        if location == BufferLocation.HOST:
            new_buffer = HostBuffer(name, shape, dtype)
        else:
            new_buffer = DeviceBuffer(name, shape, dtype)

        self.allocated_buffers[name] = new_buffer
        return new_buffer

    def free(self, name: str) -> None:
        """Return buffer to pool for reuse."""
        if name in self.allocated_buffers:
            buf = self.allocated_buffers.pop(name)
            if len(self.free_buffers) < self.max_buffers:
                self.free_buffers.append(buf)

    def clear(self) -> None:
        """Clear all buffers."""
        self.free_buffers.clear()
        self.allocated_buffers.clear()


