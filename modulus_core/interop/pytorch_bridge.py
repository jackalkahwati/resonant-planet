"""PyTorch execution provider for offloading to Modulus."""
from __future__ import annotations

from typing import Optional, Any, Dict, List
import numpy as np

try:
    import torch
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

from ..ir import Graph, Node, Tensor
from ..executor import GraphExecutor, ExecutionContext


class PyTorchExecutionProvider:
    """
    PyTorch execution provider that offloads supported ops to Modulus.
    
    This allows seamless integration of Modulus deterministic computation
    into PyTorch workflows.
    """

    def __init__(self, enable_fallback: bool = True) -> None:
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is not installed. Install with: pip install torch")
        self.enable_fallback = enable_fallback
        self.executor = GraphExecutor()

    def can_execute(self, op_name: str) -> bool:
        """Check if Modulus can execute this operation."""
        supported_ops = {
            "matmul", "mm", "bmm",
            "conv2d",
            "add", "sub", "mul", "div",
            "sum", "mean",
            "relu", "sigmoid", "tanh",
        }
        return op_name.lower() in supported_ops

    def execute_op(
        self,
        op_name: str,
        inputs: List[torch.Tensor],
        **kwargs: Any,
    ) -> torch.Tensor:
        """
        Execute a single operation using Modulus backend.
        
        Args:
            op_name: Operation name
            inputs: Input PyTorch tensors
            **kwargs: Operation attributes
            
        Returns:
            Output PyTorch tensor
        """
        # Convert PyTorch tensors to NumPy
        np_inputs = [inp.detach().cpu().numpy() for inp in inputs]

        # Build a simple single-op graph
        input_tensors = [
            Tensor(name=f"input_{i}", shape=inp.shape, dtype=str(inp.dtype))
            for i, inp in enumerate(np_inputs)
        ]

        output_tensor = Tensor(
            name="output",
            shape=np_inputs[0].shape,  # Placeholder, should infer
            dtype=str(np_inputs[0].dtype),
        )

        node = Node(
            op=op_name,
            inputs=input_tensors,
            outputs=[output_tensor],
            attributes=kwargs,
        )

        graph = Graph(
            nodes=[node],
            inputs=input_tensors,
            outputs=[output_tensor],
        )

        # Execute with Modulus
        context = ExecutionContext()
        for i, tensor in enumerate(input_tensors):
            context.buffers[tensor.name] = np_inputs[i]

        self.executor.execute(graph, context)

        # Convert result back to PyTorch
        result_np = context.buffers[output_tensor.name]
        result_torch = torch.from_numpy(result_np)

        # Restore device/dtype if needed
        if inputs[0].is_cuda:
            result_torch = result_torch.cuda()

        return result_torch


class ModulusFunction(torch.autograd.Function):
    """
    Custom PyTorch autograd function for Modulus operations.
    
    Enables gradient flow through Modulus computations.
    """

    @staticmethod
    def forward(ctx: Any, provider: PyTorchExecutionProvider, op_name: str, *inputs: torch.Tensor) -> torch.Tensor:
        ctx.provider = provider
        ctx.op_name = op_name
        ctx.save_for_backward(*inputs)
        return provider.execute_op(op_name, list(inputs))

    @staticmethod
    def backward(ctx: Any, grad_output: torch.Tensor) -> tuple:
        # Placeholder: implement backward pass using Modulus autodiff
        inputs = ctx.saved_tensors
        return (None, None, *[grad_output for _ in inputs])


def modulus_to_pytorch(graph: Graph, enable_grad: bool = False) -> torch.nn.Module:
    """
    Convert a Modulus graph into a PyTorch Module.
    
    Args:
        graph: Modulus IR graph
        enable_grad: Whether to enable gradient computation
        
    Returns:
        PyTorch Module that wraps the Modulus graph
    """
    if not PYTORCH_AVAILABLE:
        raise ImportError("PyTorch is not installed")

    class ModulusModule(torch.nn.Module):
        def __init__(self, graph: Graph):
            super().__init__()
            self.graph = graph
            self.executor = GraphExecutor()

        def forward(self, *inputs: torch.Tensor) -> torch.Tensor:
            # Convert inputs to NumPy
            np_inputs = [inp.detach().cpu().numpy() for inp in inputs]

            # Execute graph
            context = ExecutionContext()
            for i, inp_tensor in enumerate(self.graph.inputs):
                context.buffers[inp_tensor.name] = np_inputs[i]

            self.executor.execute(self.graph, context)

            # Get outputs
            outputs = [context.buffers[out.name] for out in self.graph.outputs]

            # Convert back to PyTorch
            result = torch.from_numpy(outputs[0])
            if inputs[0].is_cuda:
                result = result.cuda()

            return result

    return ModulusModule(graph)


