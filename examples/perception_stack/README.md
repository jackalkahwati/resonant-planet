# Example: Deterministic Perception Stack

This example demonstrates a simplified perception pipeline for robotics using Modulus's deterministic execution.

## Overview

A typical robotics perception stack involves:
1. **Image preprocessing** (normalization, resizing)
2. **Feature extraction** (convolution, pooling)
3. **Object detection** (bounding box regression)
4. **Post-processing** (NMS, filtering)

This example shows how to make each stage bit-reproducible using Modulus.

## Architecture

```
Input Image (640x480x3)
    ↓
Conv2D + ReLU (feature extraction)
    ↓
MaxPool (spatial reduction)
    ↓
Dense layers (classification/regression)
    ↓
Output (class scores, bounding boxes)
```

## Key Features

- **Deterministic convolution**: Bit-identical outputs across runs
- **Fixed-seed initialization**: Reproducible model weights
- **Profiled inference**: Per-layer timing and roofline analysis
- **Real-time ready**: Compatible with ROS 2 nodes

## Usage

### Run the Perception Stack

```bash
cd examples/perception_stack
python perception_demo.py --image sample_input.jpg
```

### Expected Output

```
Loading model...
Processing image: sample_input.jpg
  - Conv2D layer: 12.3 ms
  - MaxPool layer: 3.1 ms
  - Dense layer: 5.4 ms
Total inference time: 20.8 ms (48.1 FPS)

Detected objects:
  - Class: car, confidence: 0.95, bbox: [120, 200, 180, 260]
  - Class: person, confidence: 0.87, bbox: [300, 150, 340, 280]
```

## Determinism Verification

Run the same input multiple times:

```bash
for i in {1..10}; do
  python perception_demo.py --image sample_input.jpg --seed 42 > run_$i.log
done

# All outputs should be identical
md5sum run_*.log
```

## ROS 2 Integration

Launch the perception node:

```bash
ros2 run modulus_realtime perception_node.py
```

Subscribe to camera topic:

```bash
ros2 topic echo /modulus/detections
```

## Performance

On a typical workstation (Intel i7, 8 cores):
- Single frame inference: ~20 ms
- Throughput: ~50 FPS
- Memory footprint: ~200 MB

With Resonant hardware (simulated):
- Single frame inference: ~5 ms
- Throughput: ~200 FPS
- Memory footprint: ~150 MB

## Extending

- Add more complex architectures (ResNet, YOLO)
- Integrate with ONNX models via `onnx_to_modulus_graph`
- Deploy to embedded systems with real-time constraints
- Use profiler to identify bottlenecks


