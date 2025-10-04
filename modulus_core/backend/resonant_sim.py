from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable
import numpy as np
import time


@dataclass
class ResonantDeviceSpec:
    name: str
    vector_width: int
    precisions: List[str]
    memory_hierarchy: Dict[str, Any]
    concurrency: Dict[str, Any]
    instruction_latency: Dict[str, float]
    io: Dict[str, Any]
    power: Dict[str, Any]


@dataclass
class SimulatorConfig:
    timing_profile: Dict[str, float] = field(default_factory=dict)
    memory_profile: Dict[str, Any] = field(default_factory=dict)
    deterministic: bool = True
    seed: int = 0

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "SimulatorConfig":
        return cls(
            timing_profile=dict(data.get("timing_profile", {})),
            memory_profile=dict(data.get("memory_profile", {})),
            deterministic=bool(data.get("deterministic", True)),
            seed=int(data.get("seed", 0)),
        )


class ResonantSimulator:
    def __init__(self, device_spec: ResonantDeviceSpec, config: SimulatorConfig) -> None:
        self.spec = device_spec
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.trace: List[Dict[str, Any]] = []

    def run_kernel(
        self,
        name: str,
        func: Callable[..., np.ndarray],
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        wall_time = (time.perf_counter() - start_time) * 1000

        bytes_moved = self._estimate_bytes(args, result)
        flops = self._estimate_flops(name, args)

        latency_cycles = self.config.timing_profile.get(name, 1.0)

        trace_entry = {
            "kernel": name,
            "cycles": latency_cycles,
            "wall_time_ms": wall_time,
            "bytes": bytes_moved,
            "flops": flops,
        }
        self.trace.append(trace_entry)
        return trace_entry

    def get_trace(self) -> List[Dict[str, Any]]:
        return self.trace

    def reset_trace(self) -> None:
        self.trace = []

    def _estimate_bytes(self, args: tuple, result: Any) -> int:
        total = 0
        for arg in args:
            if isinstance(arg, np.ndarray):
                total += arg.nbytes
        if isinstance(result, np.ndarray):
            total += result.nbytes
        return total

    def _estimate_flops(self, kernel_name: str, args: tuple) -> int:
        if "matmul" in kernel_name:
            if len(args) >= 2 and isinstance(args[0], np.ndarray) and isinstance(args[1], np.ndarray):
                m, k = args[0].shape
                k2, n = args[1].shape
                return 2 * m * n * k
        return 0


