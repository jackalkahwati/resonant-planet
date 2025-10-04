"""Efficient buffer copy operations with DMA simulation."""
from __future__ import annotations

from typing import Optional
import numpy as np
import time

from .buffer import Buffer, BufferLocation


class CopyEngine:
    """Simulates DMA copy operations with bandwidth constraints."""

    def __init__(self, host_device_bw_gbps: float = 10.0, device_device_bw_gbps: float = 100.0) -> None:
        self.host_device_bw = host_device_bw_gbps * 1e9 / 8  # bytes/sec
        self.device_device_bw = device_device_bw_gbps * 1e9 / 8  # bytes/sec

    def copy(self, src: Buffer, dst: Buffer, async_copy: bool = False) -> float:
        """Copy buffer with bandwidth simulation. Returns estimated latency in seconds."""
        if src.data is None or dst.data is None:
            raise ValueError("Cannot copy from/to null buffer")

        if src.shape != dst.shape:
            raise ValueError(f"Shape mismatch: {src.shape} vs {dst.shape}")

        nbytes = src.nbytes()

        if src.location == BufferLocation.HOST and dst.location == BufferLocation.DEVICE:
            bandwidth = self.host_device_bw
        elif src.location == BufferLocation.DEVICE and dst.location == BufferLocation.HOST:
            bandwidth = self.host_device_bw
        elif src.location == BufferLocation.DEVICE and dst.location == BufferLocation.DEVICE:
            bandwidth = self.device_device_bw
        else:
            bandwidth = 1e12  # Host-to-host is very fast

        latency = nbytes / bandwidth

        if not async_copy:
            time.sleep(latency)

        np.copyto(dst.data, src.data)
        return latency

    def copy_async(self, src: Buffer, dst: Buffer) -> float:
        """Asynchronous copy (non-blocking)."""
        return self.copy(src, dst, async_copy=True)


def h2d_copy(host_buf: Buffer, device_buf: Buffer, engine: Optional[CopyEngine] = None) -> float:
    """Host-to-device copy."""
    if engine is None:
        engine = CopyEngine()
    return engine.copy(host_buf, device_buf)


def d2h_copy(device_buf: Buffer, host_buf: Buffer, engine: Optional[CopyEngine] = None) -> float:
    """Device-to-host copy."""
    if engine is None:
        engine = CopyEngine()
    return engine.copy(device_buf, host_buf)


def d2d_copy(src_buf: Buffer, dst_buf: Buffer, engine: Optional[CopyEngine] = None) -> float:
    """Device-to-device copy."""
    if engine is None:
        engine = CopyEngine()
    return engine.copy(src_buf, dst_buf)


