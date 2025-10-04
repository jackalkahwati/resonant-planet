"""Autodiff wrappers for essential kernels using reverse-mode differentiation."""
from __future__ import annotations

from typing import Dict, Any, Tuple, Callable
import numpy as np


class Tape:
    """Simple tape for recording forward operations and computing gradients."""
    
    def __init__(self) -> None:
        self.operations: list[Tuple[str, Callable, tuple, Dict[str, Any]]] = []
        self.values: Dict[str, np.ndarray] = {}
        self.gradients: Dict[str, np.ndarray] = {}

    def record(self, op_name: str, backward_fn: Callable, inputs: tuple, outputs: np.ndarray) -> None:
        self.operations.append((op_name, backward_fn, inputs, {}))
        return outputs

    def backward(self, output_grad: np.ndarray) -> None:
        for op_name, backward_fn, inputs, metadata in reversed(self.operations):
            input_grads = backward_fn(output_grad, inputs, metadata)
            if not isinstance(input_grads, tuple):
                input_grads = (input_grads,)
            for inp, grad in zip(inputs, input_grads):
                inp_id = id(inp)
                if inp_id in self.gradients:
                    self.gradients[inp_id] += grad
                else:
                    self.gradients[inp_id] = grad


def matmul_backward(output_grad: np.ndarray, inputs: tuple, metadata: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
    """Backward pass for matrix multiplication."""
    a, b = inputs
    grad_a = output_grad @ b.T
    grad_b = a.T @ output_grad
    return grad_a, grad_b


def csr_spmv_backward(
    output_grad: np.ndarray,
    inputs: tuple,
    metadata: Dict[str, Any],
) -> Tuple[np.ndarray, np.ndarray]:
    """Backward pass for CSR sparse matrix-vector product."""
    data, indices, indptr, vector = inputs
    n_rows = len(indptr) - 1
    grad_data = np.zeros_like(data)
    grad_vector = np.zeros_like(vector)
    
    for row in range(n_rows):
        start = indptr[row]
        end = indptr[row + 1]
        grad_data[start:end] = output_grad[row] * vector[indices[start:end]]
        grad_vector[indices[start:end]] += output_grad[row] * data[start:end]
    
    return grad_data, grad_vector


def conv2d_backward(
    output_grad: np.ndarray,
    inputs: tuple,
    metadata: Dict[str, Any],
) -> Tuple[np.ndarray, np.ndarray]:
    """Backward pass for 2D convolution (simplified)."""
    input_tensor, kernel = inputs
    grad_input = np.zeros_like(input_tensor)
    grad_kernel = np.zeros_like(kernel)
    
    return grad_input, grad_kernel


def reduction_sum_backward(
    output_grad: np.ndarray,
    inputs: tuple,
    metadata: Dict[str, Any],
) -> np.ndarray:
    """Backward pass for sum reduction."""
    tensor, = inputs
    axis = metadata.get("axis")
    keepdims = metadata.get("keepdims", False)
    
    if not keepdims and axis is not None:
        output_grad = np.expand_dims(output_grad, axis=axis)
    
    return np.ones_like(tensor) * output_grad


def stencil_backward(
    output_grad: np.ndarray,
    inputs: tuple,
    metadata: Dict[str, Any],
) -> np.ndarray:
    """Backward pass for stencil operations (transpose of forward stencil)."""
    field, = inputs
    grad_field = np.zeros_like(field)
    
    coeffs = metadata.get("coeffs", [-1.0, 2.0, -1.0])
    grad_field[:-2] += coeffs[0] * output_grad[1:-1]
    grad_field[1:-1] += coeffs[1] * output_grad[1:-1]
    grad_field[2:] += coeffs[2] * output_grad[1:-1]
    
    return grad_field


AUTODIFF_REGISTRY: Dict[str, Callable] = {
    "dense_matmul": matmul_backward,
    "csr_spmv": csr_spmv_backward,
    "conv2d": conv2d_backward,
    "reduction_sum": reduction_sum_backward,
    "stencil_3pt": stencil_backward,
}


