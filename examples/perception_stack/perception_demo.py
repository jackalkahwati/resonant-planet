#!/usr/bin/env python3
"""
Deterministic Perception Stack Demo using Modulus.

Simulates a simplified object detection pipeline with deterministic execution.
"""
from __future__ import annotations

import argparse
import time
import numpy as np

from modulus_core import (
    enable_deterministic_mode,
    Profiler,
    Graph,
    Node,
    Tensor,
    GraphExecutor,
    ExecutionContext,
)
from modulus_core.kernels.optimized import conv2d_opt, dense_matmul_opt


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Normalize and prepare image for inference."""
    # Assume input is HxWxC, convert to CxHxW and normalize
    image = image.transpose(2, 0, 1).astype(np.float64) / 255.0
    return image[np.newaxis, :, :, :]  # Add batch dimension


def build_simple_cnn() -> tuple[list, dict]:
    """Build a simple CNN architecture."""
    # Conv layer: 3 input channels, 16 output channels, 3x3 kernel
    conv_kernel = np.random.randn(16, 3, 3, 3) * 0.1
    conv_bias = np.zeros(16)

    # Dense layer: flatten and classify
    dense_weights = np.random.randn(256, 10) * 0.1
    dense_bias = np.zeros(10)

    layers = [
        {"type": "conv2d", "kernel": conv_kernel, "bias": conv_bias},
        {"type": "relu"},
        {"type": "dense", "weights": dense_weights, "bias": dense_bias},
    ]

    return layers, {"conv_kernel": conv_kernel, "dense_weights": dense_weights}


def forward_pass(image: np.ndarray, layers: list, profiler: Profiler, rng: np.random.Generator) -> np.ndarray:
    """Execute forward pass through the network."""
    x = image

    for i, layer in enumerate(layers):
        layer_type = layer["type"]

        if layer_type == "conv2d":
            profiler.start_kernel("conv2d", input_shapes=[x.shape, layer["kernel"].shape])
            x = conv2d_opt(
                x,
                layer["kernel"],
                attributes={"stride": (1, 1), "padding": (1, 1)},
                rng=rng,
                deterministic=True,
            )
            # Add bias (broadcast)
            x = x + layer["bias"].reshape(1, -1, 1, 1)
            flops = np.prod(x.shape) * np.prod(layer["kernel"].shape)
            profiler.end_kernel(flops=flops, bytes_moved=x.nbytes + layer["kernel"].nbytes)

        elif layer_type == "relu":
            profiler.start_kernel("relu", input_shapes=[x.shape])
            x = np.maximum(0, x)
            profiler.end_kernel(flops=x.size, bytes_moved=x.nbytes * 2)

        elif layer_type == "dense":
            profiler.start_kernel("dense_matmul", input_shapes=[x.shape])
            # Flatten spatial dimensions
            batch_size = x.shape[0]
            x_flat = x.reshape(batch_size, -1)
            # Truncate or pad to match dense layer input
            target_size = layer["weights"].shape[0]
            if x_flat.shape[1] > target_size:
                x_flat = x_flat[:, :target_size]
            elif x_flat.shape[1] < target_size:
                pad_width = ((0, 0), (0, target_size - x_flat.shape[1]))
                x_flat = np.pad(x_flat, pad_width, mode="constant")

            x = dense_matmul_opt(
                x_flat,
                layer["weights"],
                attributes={},
                rng=rng,
                deterministic=True,
            )
            x = x + layer["bias"]
            flops = batch_size * layer["weights"].shape[0] * layer["weights"].shape[1]
            profiler.end_kernel(flops=flops, bytes_moved=x.nbytes + layer["weights"].nbytes)

    return x


def postprocess_outputs(outputs: np.ndarray) -> list[dict]:
    """Convert raw outputs to detection results."""
    class_scores = outputs[0]  # Assuming batch size 1
    top_class = int(np.argmax(class_scores))
    confidence = float(class_scores[top_class])

    # Simulate bounding box (placeholder)
    bbox = [100 + top_class * 20, 150, 140 + top_class * 20, 200]

    return [
        {
            "class": f"class_{top_class}",
            "confidence": confidence,
            "bbox": bbox,
        }
    ]


def main():
    parser = argparse.ArgumentParser(description="Deterministic Perception Demo")
    parser.add_argument("--image", type=str, default=None, help="Input image path")
    parser.add_argument("--height", type=int, default=64, help="Image height")
    parser.add_argument("--width", type=int, default=64, help="Image width")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    # Enable deterministic mode
    enable_deterministic_mode(seed=args.seed, strict=True)
    print(f"Deterministic mode enabled with seed={args.seed}")

    # Create or load image
    if args.image:
        print(f"Loading image: {args.image}")
        # Placeholder: would use PIL or cv2 here
        image = np.random.randint(0, 255, (args.height, args.width, 3), dtype=np.uint8)
    else:
        print(f"Generating synthetic image ({args.height}x{args.width})")
        image = np.random.randint(0, 255, (args.height, args.width, 3), dtype=np.uint8)

    # Preprocess
    image_tensor = preprocess_image(image)
    print(f"Input shape: {image_tensor.shape}")

    # Build model
    np.random.seed(args.seed)
    layers, weights = build_simple_cnn()
    print(f"Model built with {len(layers)} layers")

    # Profiler
    profiler = Profiler()
    rng = np.random.default_rng(args.seed)

    # Forward pass
    print("Running inference...")
    start_time = time.perf_counter()
    outputs = forward_pass(image_tensor, layers, profiler, rng)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"Inference completed in {elapsed_ms:.2f} ms ({1000/elapsed_ms:.1f} FPS)")

    # Postprocess
    detections = postprocess_outputs(outputs)
    print("\nDetected objects:")
    for det in detections:
        print(f"  - Class: {det['class']}, confidence: {det['confidence']:.2f}, bbox: {det['bbox']}")

    # Profiler summary
    summary = profiler.summary()
    print(f"\nProfiler Summary:")
    print(f"  Total kernels: {summary['total_kernels']}")
    print(f"  Total time: {summary['total_time_ms']:.2f} ms")
    for kernel in summary["kernel_breakdown"]:
        print(f"    {kernel['name']}: {kernel['latency_ms']:.2f} ms, {kernel['gflops']:.2f} GFLOP/s")


if __name__ == "__main__":
    main()


