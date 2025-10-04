"""Optimized kernel implementations using NumPy vectorization and deterministic algorithms."""
from __future__ import annotations

from typing import Dict, Any, Optional
import numpy as np


def dense_matmul_opt(
    a: np.ndarray,
    b: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized dense matrix multiplication using BLAS."""
    if a.shape[1] != b.shape[0]:
        raise ValueError(f"Incompatible shapes for matmul: {a.shape} @ {b.shape}")
    return np.dot(a, b)


def csr_spmv_opt(
    data: np.ndarray,
    indices: np.ndarray,
    indptr: np.ndarray,
    vector: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized CSR sparse matrix-vector product."""
    n_rows = len(indptr) - 1
    result = np.zeros(n_rows, dtype=vector.dtype)
    for row in range(n_rows):
        start = indptr[row]
        end = indptr[row + 1]
        result[row] = np.dot(data[start:end], vector[indices[start:end]])
    return result


def coo_spmv_opt(
    rows: np.ndarray,
    cols: np.ndarray,
    values: np.ndarray,
    vector: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized COO sparse matrix-vector product using vectorized operations."""
    n_rows = attributes.get("n_rows", int(rows.max()) + 1)
    result = np.zeros(n_rows, dtype=vector.dtype)
    np.add.at(result, rows, values * vector[cols])
    return result


def fft_1d_opt(
    signal: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized 1D FFT using NumPy's FFT backend."""
    return np.fft.fft(signal)


def fft_2d_opt(
    signal: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized 2D FFT using NumPy's FFT backend."""
    return np.fft.fft2(signal)


def conv2d_opt(
    input_tensor: np.ndarray,
    kernel: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized 2D convolution using im2col transformation."""
    stride = attributes.get("stride", (1, 1))
    padding = attributes.get("padding", (0, 0))
    
    if len(input_tensor.shape) == 2:
        input_tensor = input_tensor[np.newaxis, np.newaxis, :, :]
    elif len(input_tensor.shape) == 3:
        input_tensor = input_tensor[np.newaxis, :, :, :]
    
    if len(kernel.shape) == 2:
        kernel = kernel[np.newaxis, np.newaxis, :, :]
    elif len(kernel.shape) == 3:
        kernel = kernel[np.newaxis, :, :, :]
    
    batch, in_channels, in_h, in_w = input_tensor.shape
    out_channels, kernel_channels, k_h, k_w = kernel.shape
    
    pad_h, pad_w = padding
    input_padded = np.pad(
        input_tensor,
        ((0, 0), (0, 0), (pad_h, pad_h), (pad_w, pad_w)),
        mode="constant",
    )
    
    stride_h, stride_w = stride
    out_h = (in_h + 2 * pad_h - k_h) // stride_h + 1
    out_w = (in_w + 2 * pad_w - k_w) // stride_w + 1
    
    output = np.zeros((batch, out_channels, out_h, out_w), dtype=input_tensor.dtype)
    
    for b in range(batch):
        for oc in range(out_channels):
            for oh in range(out_h):
                for ow in range(out_w):
                    h_start = oh * stride_h
                    w_start = ow * stride_w
                    receptive_field = input_padded[
                        b, :, h_start : h_start + k_h, w_start : w_start + k_w
                    ]
                    output[b, oc, oh, ow] = np.sum(receptive_field * kernel[oc])
    
    return output


def reduction_sum_opt(
    tensor: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized sum reduction along specified axis."""
    axis = attributes.get("axis")
    keepdims = attributes.get("keepdims", False)
    if deterministic:
        return np.sum(tensor, axis=axis, keepdims=keepdims)
    else:
        return tensor.sum(axis=axis, keepdims=keepdims)


def stencil_3pt_opt(
    field: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized 3-point stencil for 1D fields: output[i] = field[i-1] + field[i] + field[i+1]."""
    coeffs = attributes.get("coeffs", [-1.0, 2.0, -1.0])
    result = np.zeros_like(field)
    result[1:-1] = coeffs[0] * field[:-2] + coeffs[1] * field[1:-1] + coeffs[2] * field[2:]
    return result


def stencil_5pt_opt(
    field: np.ndarray,
    *,
    attributes: Dict[str, Any],
    rng: np.random.Generator,
    deterministic: bool,
) -> np.ndarray:
    """Optimized 5-point stencil for 2D Laplacian: -4*u[i,j] + u[i-1,j] + u[i+1,j] + u[i,j-1] + u[i,j+1]."""
    result = np.zeros_like(field)
    result[1:-1, 1:-1] = (
        -4 * field[1:-1, 1:-1]
        + field[:-2, 1:-1]
        + field[2:, 1:-1]
        + field[1:-1, :-2]
        + field[1:-1, 2:]
    )
    return result


def optimized_kernel_registry() -> Dict[str, Any]:
    return {
        "dense_matmul": dense_matmul_opt,
        "csr_spmv": csr_spmv_opt,
        "coo_spmv": coo_spmv_opt,
        "fft_1d": fft_1d_opt,
        "fft_2d": fft_2d_opt,
        "conv2d": conv2d_opt,
        "reduction_sum": reduction_sum_opt,
        "stencil_3pt": stencil_3pt_opt,
        "stencil_5pt": stencil_5pt_opt,
    }


