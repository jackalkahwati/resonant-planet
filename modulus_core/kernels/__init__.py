from __future__ import annotations

from typing import Dict, Callable
import numpy as np


def dense_matmul(a: np.ndarray, b: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    return a @ b


def csr_spmv(matrix: Dict[str, np.ndarray], vector: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    data = matrix["data"]
    indices = matrix["indices"]
    indptr = matrix["indptr"]
    result = np.zeros(vector.shape[0], dtype=vector.dtype)
    for row in range(len(indptr) - 1):
        start = indptr[row]
        end = indptr[row + 1]
        result[row] = (data[start:end] * vector[indices[start:end]]).sum()
    return result


def coo_spmv(rows: np.ndarray, cols: np.ndarray, values: np.ndarray, vector: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    result = np.zeros(vector.shape[0], dtype=vector.dtype)
    for row, col, value in zip(rows, cols, values):
        result[row] += value * vector[col]
    return result


def fft_1d(signal: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    return np.fft.fft(signal)


def fft_2d(signal: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    return np.fft.fft2(signal)


def conv2d(input_tensor: np.ndarray, kernel: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    stride = attributes.get("stride", (1, 1))
    padding = attributes.get("padding", (0, 0))
    input_padded = np.pad(input_tensor, ((0, 0), (0, 0), (padding[0], padding[0]), (padding[1], padding[1])))
    batch, channels, height, width = input_padded.shape
    out_channels, _, kernel_h, kernel_w = kernel.shape
    out_h = (height - kernel_h) // stride[0] + 1
    out_w = (width - kernel_w) // stride[1] + 1
    output = np.zeros((batch, out_channels, out_h, out_w))
    for b in range(batch):
        for oc in range(out_channels):
            for ic in range(channels):
                output[b, oc] += scipy_signal_convolve2d(
                    input_padded[b, ic], kernel[oc, ic], stride, out_h, out_w
                )
    return output


def reduction_sum(tensor: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    axis = attributes.get("axis")
    keepdims = attributes.get("keepdims", False)
    return tensor.sum(axis=axis, keepdims=keepdims)


def stencil_op(field: np.ndarray, kernel: np.ndarray, *, attributes, rng, deterministic) -> np.ndarray:
    return np.convolve(field, kernel, mode="same")


def autodiff_placeholder(*outputs: np.ndarray, attributes, rng, deterministic) -> np.ndarray:
    raise NotImplementedError("Autodiff requires backward graph construction")


def scipy_signal_convolve2d(image: np.ndarray, kernel: np.ndarray, stride: tuple[int, int], out_h: int, out_w: int) -> np.ndarray:
    result = np.zeros((out_h, out_w))
    for i in range(out_h):
        for j in range(out_w):
            region = image[i * stride[0] : i * stride[0] + kernel.shape[-2], j * stride[1] : j * stride[1] + kernel.shape[-1]]
            result[i, j] = np.sum(region * kernel)
    return result


def kernel_registry(optimized: bool = True) -> Dict[str, Callable]:
    if optimized:
        from .optimized import optimized_kernel_registry
        return optimized_kernel_registry()
    return {
        "dense_matmul": dense_matmul,
        "csr_spmv": csr_spmv,
        "coo_spmv": coo_spmv,
        "fft_1d": fft_1d,
        "fft_2d": fft_2d,
        "conv2d": conv2d,
        "reduction_sum": reduction_sum,
        "stencil_op": stencil_op,
        "autodiff": autodiff_placeholder,
    }
