# Example: 2D Heat Equation with 5-Point Stencil

This example demonstrates solving the 2D heat equation using Modulus's deterministic stencil operators.

## Problem

We solve the 2D heat equation:

```
∂u/∂t = α (∂²u/∂x² + ∂²u/∂y²)
```

where:
- `u(x,y,t)` is temperature
- `α` is thermal diffusivity
- Boundary conditions: fixed temperature on edges

## Method

1. **Discretize** the domain into a 2D grid
2. **Apply 5-point stencil** for Laplacian approximation
3. **Time-step** using explicit Euler method
4. **Validate** conservation of energy

## Usage

```bash
cd examples/pde_stencil
python heat_equation_2d.py
```

### Expected Output

```
Time step 0: max_temp=100.0, energy=2500.0
Time step 10: max_temp=95.3, energy=2498.1
Time step 20: max_temp=91.2, energy=2496.5
...
Final state saved to heat_output.npy
```

## Key Features

- **Exact stencil operations**: No floating-point drift
- **Deterministic time-stepping**: Bit-identical results across runs
- **Energy conservation**: Validated at each step
- **Profiled execution**: Per-kernel timing available

## Validation

Run with different seeds to verify determinism:

```bash
python heat_equation_2d.py --seed 42
python heat_equation_2d.py --seed 123
diff output_42.npy output_123.npy  # Should be identical
```

## Performance

On a typical workstation:
- Grid: 256x256
- Time steps: 1000
- Total time: ~2.5s
- Stencil throughput: ~100 GFLOP/s

## Next Steps

- Try different boundary conditions (Neumann, periodic)
- Experiment with implicit time-stepping
- Visualize results with `plot_heat.py`


