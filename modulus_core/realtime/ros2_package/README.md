# Modulus ROS 2 Package

Real-time deterministic computation bridge for ROS 2 robotics applications.

## Overview

This package provides a ROS 2 node that integrates Modulus's exact computation engine into robotics control loops, enabling deterministic and reproducible real-time processing.

## Features

- **Deterministic execution**: All computations are bit-reproducible
- **Real-time performance**: Low-latency processing suitable for control loops
- **ROS 2 integration**: Standard message types and node interfaces
- **Thread affinity**: Pin computations to specific CPU cores
- **Priority scheduling**: Support for real-time scheduling policies

## Installation

### Prerequisites

- ROS 2 (Humble or later)
- Python 3.8+
- Modulus core library

### Build from Source

```bash
cd /path/to/ros2_ws/src
ln -s /path/to/modulus_core/realtime/ros2_package modulus_realtime
cd /path/to/ros2_ws
colcon build --packages-select modulus_realtime
source install/setup.bash
```

## Usage

### Basic Node

```bash
ros2 run modulus_realtime modulus_node.py
```

### Topics

**Subscribed:**
- `/modulus/input` (Float64MultiArray): Input data for computation

**Published:**
- `/modulus/result` (Float64MultiArray): Computation results
- `/modulus/status` (String): Node status and error messages

### Example: Send Input Data

```bash
ros2 topic pub /modulus/input std_msgs/msg/Float64MultiArray "{data: [1.0, 2.0, 3.0]}"
```

### Example: Monitor Results

```bash
ros2 topic echo /modulus/result
```

## Configuration

### Thread Affinity

Set CPU affinity in your launch file:

```python
from modulus_core.realtime import set_thread_affinity
set_thread_affinity([0, 1])  # Pin to cores 0 and 1
```

### Deterministic Mode

Enable deterministic execution:

```python
from modulus_core.realtime import enable_deterministic_mode
enable_deterministic_mode(seed=42, strict=True)
```

## Integration with Modulus

Replace the placeholder `compute()` method in `modulus_node.py` with your Modulus pipeline:

```python
from modulus_core import solve, ProblemSpec

def compute(self, input_data: np.ndarray) -> np.ndarray:
    spec = ProblemSpec(...)  # Build from input_data
    result = solve(spec)
    return result.solution.values
```

## Testing

```bash
colcon test --packages-select modulus_realtime
```

## License

MIT License - See LICENSE file for details.

## Contact

Jack Al-Kahwati - jack@resonantcomputer.com


