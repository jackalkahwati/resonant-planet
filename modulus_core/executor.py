from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional
import numpy as np

from .ir import Graph, Tensor


@dataclass
class ExecutionContext:
    seed: int
    config_hash: str
    deterministic: bool
    buffers: Dict[str, np.ndarray]


class GraphExecutor:
    def __init__(self, kernel_registry: Optional[Dict[str, Callable[..., np.ndarray]]] = None) -> None:
        self.kernel_registry = kernel_registry or {}

    def register_kernel(self, op_type: str, func: Callable[..., np.ndarray]) -> None:
        self.kernel_registry[op_type] = func

    def execute(
        self,
        graph: Graph,
        *,
        seed: int = 0,
        deterministic: bool = True,
        inputs: Optional[Dict[str, np.ndarray]] = None,
    ) -> ExecutionContext:
        config_hash = graph.signature()
        rng = np.random.default_rng(seed)

        buffers: Dict[str, np.ndarray] = {}
        input_map = inputs or {}
        for tensor in graph.inputs:
            if tensor.name in input_map:
                buffers[tensor.name] = input_map[tensor.name]
            else:
                buffers[tensor.name] = np.zeros(tensor.shape, dtype=np.float64)

        intermediates = graph.metadata.get("intermediates", [])
        for tensor in intermediates:
            buffers[tensor.name] = np.zeros(tensor.shape, dtype=np.float64)

        for node in graph.nodes:
            if node.op_type not in self.kernel_registry:
                raise ValueError(f"Kernel for op_type '{node.op_type}' not registered")
            kernel = self.kernel_registry[node.op_type]
            input_tensors = [buffers[name] for name in node.inputs]
            outputs = kernel(
                *input_tensors,
                attributes=node.attributes,
                rng=rng,
                deterministic=deterministic,
            )
            if not isinstance(outputs, tuple):
                outputs = (outputs,)
            for name, value in zip(node.outputs, outputs):
                buffers[name] = value

        return ExecutionContext(
            seed=seed,
            config_hash=config_hash,
            deterministic=deterministic,
            buffers=buffers,
        )
