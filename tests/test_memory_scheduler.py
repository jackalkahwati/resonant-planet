"""Tests for memory management and scheduling system."""
from __future__ import annotations

import numpy as np
import pytest

from modulus_core.memory import (
    Buffer,
    HostBuffer,
    DeviceBuffer,
    BufferPool,
    Stream,
    Event,
    Scheduler,
    CopyEngine,
    h2d_copy,
    d2h_copy,
    d2d_copy,
)


def test_buffer_allocation():
    """Test basic buffer allocation."""
    host_buf = HostBuffer("test_host", (10, 10), dtype=np.float32)
    assert host_buf.name == "test_host"
    assert host_buf.shape == (10, 10)
    assert host_buf.data.shape == (10, 10)
    assert host_buf.nbytes() == 10 * 10 * 4

    device_buf = DeviceBuffer("test_device", (5, 5), dtype=np.float64)
    assert device_buf.shape == (5, 5)
    assert device_buf.nbytes() == 5 * 5 * 8


def test_buffer_pool():
    """Test buffer pool reuse."""
    pool = BufferPool(max_buffers=10)

    from modulus_core.memory.buffer import BufferLocation

    buf1 = pool.allocate("buf1", (100, 100), np.float32, BufferLocation.HOST)
    assert buf1.name == "buf1"

    pool.free("buf1")
    buf2 = pool.allocate("buf2", (100, 100), np.float32, BufferLocation.HOST)
    assert buf2.name == "buf2"
    assert id(buf1) == id(buf2)


def test_copy_engine():
    """Test copy engine with bandwidth simulation."""
    engine = CopyEngine(host_device_bw_gbps=10.0, device_device_bw_gbps=100.0)

    host_buf = HostBuffer("host", (1000, 1000), dtype=np.float64)
    device_buf = DeviceBuffer("device", (1000, 1000), dtype=np.float64)

    host_buf.data[:] = np.random.rand(1000, 1000)

    latency = engine.copy_async(host_buf, device_buf)
    assert latency > 0
    assert np.allclose(host_buf.data, device_buf.data)


def test_stream_scheduler():
    """Test stream scheduling and event synchronization."""
    scheduler = Scheduler(num_streams=2)

    event1 = scheduler.create_event("kernel_1_done")
    stream1 = scheduler.streams[0]
    stream2 = scheduler.streams[1]

    results = []

    def kernel_a():
        results.append("a")

    def kernel_b():
        results.append("b")

    scheduler.enqueue_kernel(kernel_a, stream=stream1)
    stream1.record_event(event1)

    scheduler.enqueue_kernel(kernel_b, stream=stream2, wait_events=[event1])

    scheduler.synchronize_all()

    assert "a" in results
    assert "b" in results


def test_h2d_d2h_copies():
    """Test host-device copy helpers."""
    host_src = HostBuffer("host_src", (50, 50), dtype=np.float32)
    device_buf = DeviceBuffer("device", (50, 50), dtype=np.float32)
    host_dst = HostBuffer("host_dst", (50, 50), dtype=np.float32)

    host_src.data[:] = np.random.rand(50, 50)

    h2d_copy(host_src, device_buf)
    assert np.allclose(host_src.data, device_buf.data)

    d2h_copy(device_buf, host_dst)
    assert np.allclose(host_src.data, host_dst.data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


