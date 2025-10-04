# Modulus Integration Plan

## 🔍 What I Found

Your Modulus repo at https://github.com/jackalkahwati/modulus.git contains:

### Core Capabilities
- **Certified Math/Physics Compiler** - Exact computation for integers/rationals
- **Universal Problem Solver** - Multi-domain AI (physics, math, economics, etc.)
- **Multi-Head PAT** - Prime Algebra Transformer for exact arithmetic
- **Qwen Integration** - Multi-head attention acceleration
- **RL Components** - Agent and environment framework

### Current Physics Code
Located in `src/pipeline/modulus/`:
- `kinematics.py` - Constant acceleration motion models (for UAP tracking)
- `corrector.py` - Physics-informed parameter fitting using PyTorch
- Pattern: Differentiable physics + gradient-based optimization

### Purpose
**Primary**: UAP detection and tracking from Sentinel-1 satellite data
**NOT**: Exoplanet transit modeling (yet!)

---

## 🎯 Integration Options

### Option 1: Adapt Modulus Physics Patterns (RECOMMENDED)

**What**: Use Modulus's physics-informed fitting approach for transits

**How**:
1. Keep Modulus math/computation core
2. Create new `exoplanet_physics.py` module
3. Adapt the pattern from `corrector.py` for transit modeling
4. Use PyTorch + autodiff for parameter estimation

**Benefit**: Leverages Modulus's exact computation + physics framework

**Implementation** (2-3 hours):
```python
# physics/modulus_exoplanet/transit_model.py

import torch
from typing import Tuple

class TransitModel(torch.nn.Module):
    """
    Mandel-Agol transit model with PyTorch autodiff.
    Adapted from Modulus physics pattern.
    """
    def __init__(self, limb_darkening: Tuple[float, float] = (0.3, 0.2)):
        super().__init__()
        self.u1, self.u2 = limb_darkening
    
    def forward(self, params: torch.Tensor, time: torch.Tensor) -> torch.Tensor:
        """
        Compute transit light curve.
        
        params: [period, t0, depth, duration, impact_param]
        time: observation times
        """
        period, t0, depth, duration, b = params
        
        # Phase fold
        phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
        
        # Compute z (projected distance)
        z = self._compute_z(phase, period, duration, b)
        
        # Mandel-Agol with quadratic limb darkening
        flux = self._mandel_agol(z, depth, self.u1, self.u2)
        
        return flux
    
    def _compute_z(self, phase, period, duration, b):
        # Simplified - can be made more accurate
        half_dur = duration / 2.0
        z_min = b  # Impact parameter at mid-transit
        
        # Linear approximation for now
        z = torch.abs(phase) / half_dur
        z = torch.where(torch.abs(phase) < half_dur, z_min + z, 100.0)
        
        return z
    
    def _mandel_agol(self, z, depth, u1, u2):
        # Quadratic limb darkening approximation
        # Full implementation would use elliptic integrals
        
        # For now, smooth box model
        r_planet = torch.sqrt(depth)
        ingress = 1.0 - torch.exp(-(z - r_planet).pow(2) / 0.01)
        
        flux = 1.0 - depth * ingress * (1.0 - u1 * (1 - z) - u2 * (1 - z).pow(2))
        
        return flux


def fit_transit_pytorch(time, flux, flux_err, initial_params=None):
    """
    Fit transit using Modulus-style physics-informed optimization.
    
    Similar pattern to corrector.py from Modulus UAP pipeline.
    """
    model = TransitModel()
    
    # Initial guess
    if initial_params is None:
        period_guess = 3.0
        t0_guess = time[torch.argmin(flux)]
        depth_guess = 1.0 - torch.min(flux)
        duration_guess = 0.1
        b_guess = 0.3
        params = torch.tensor([period_guess, t0_guess, depth_guess, duration_guess, b_guess])
    else:
        params = torch.tensor(initial_params)
    
    params = torch.nn.Parameter(params)
    optimizer = torch.optim.Adam([params], lr=0.01)
    
    # Convert inputs to tensors
    time_t = torch.tensor(time, dtype=torch.float32)
    flux_t = torch.tensor(flux, dtype=torch.float32)
    flux_err_t = torch.tensor(flux_err, dtype=torch.float32)
    
    # Optimize
    for step in range(200):
        optimizer.zero_grad()
        
        # Forward pass
        model_flux = model(params, time_t)
        
        # Chi-square loss
        residuals = (flux_t - model_flux) / flux_err_t
        loss = torch.mean(residuals ** 2)
        
        # Add physics constraints
        # e.g., period > 0, depth > 0, impact param < 1
        penalty = torch.relu(-params[0]) + torch.relu(-params[2]) + torch.relu(params[4] - 1.0)
        total_loss = loss + 10.0 * penalty
        
        total_loss.backward()
        optimizer.step()
    
    # Return fitted parameters
    with torch.no_grad():
        final_params = params.cpu().numpy()
        final_flux = model(params, time_t).cpu().numpy()
        residuals = flux - final_flux
        snr = float(final_params[2] / (np.std(residuals) + 1e-10))
    
    return {
        'period_days': float(final_params[0]),
        't0_bjd': float(final_params[1]),
        'depth_ppm': float(final_params[2] * 1e6),
        'duration_hours': float(final_params[3] * 24),
        'impact_parameter': float(final_params[4]),
        'snr': snr,
        'chi2': float(loss.item()),
        'success': True,
        'message': 'Fitted with Modulus-PyTorch'
    }
```

### Option 2: Use Modulus Universal Solver

**What**: Use Modulus's Universal Problem Solver for physics problems

**Example**:
```python
from universal_problem_solver import UniversalProblemSolver

solver = UniversalProblemSolver()

# Ask Modulus to solve transit physics
result = solver.solve(
    "A planet with radius 0.1 R_sun transits a star. "
    "The star has radius 1 R_sun and limb darkening (u1=0.3, u2=0.2). "
    "What is the transit depth?"
)

print(result.numerical_answer)  # Exact answer via PAT
print(result.explanation)       # Step-by-step derivation
```

**Benefit**: Leverages Modulus's exact computation
**Drawback**: May need fine-tuning for astronomy domain

### Option 3: Keep Current Mock + Add NASA Data (FASTEST)

**What**: Don't integrate Modulus physics yet, just add data sources

**Benefit**: Get to real discovery quickly
**Time**: 30 minutes

**Implementation**: See next section

---

## 🚀 Recommended Path

I suggest a **hybrid approach**:

### Phase 1: Add NASA Data NOW (30 min)
- Install `lightkurve`
- Add data fetching routes
- Test on real Kepler planets
- **Outcome**: Can search real exoplanet data

### Phase 2: Adapt Modulus Patterns (2-3 hours)
- Create `physics/modulus_exoplanet/`
- Implement PyTorch-based transit fitting (like corrector.py)
- Use Modulus's math core for exact computation
- **Outcome**: Better physics, still fast

### Phase 3: Full Integration (1-2 days)
- Connect to Modulus Universal Solver
- Train Qwen on astronomy domain
- Use PAT for numerical stability
- **Outcome**: State-of-the-art system

---

## 📋 Next Steps

**Immediate** (I'll do this now):
1. ✅ Clone Modulus repo (done)
2. ⏳ Add NASA data integration (lightkurve)
3. ⏳ Create adapter for Modulus math core
4. ⏳ Test on real Kepler data

**Your Decision Needed**:
- **Option A**: Quick win - Just add NASA data, keep current physics (30 min)
- **Option B**: Adapt Modulus - Use physics patterns, improve fitting (2-3 hours)
- **Option C**: Full integration - Modulus math core + astronomy training (1-2 days)

**My Recommendation**: Start with **Option A** (NASA data), then upgrade to **Option B** (Modulus patterns).

---

## 🎯 What I'll Do Now

I'm going to proceed with:
1. **NASA Data Integration** - Add lightkurve, enable real data fetching
2. **Modulus Math Adapter** - Connect to Modulus computation core
3. **Test on Real Data** - Verify everything works

Then you can decide if you want the full Modulus physics integration.

Sound good? Should I proceed?
