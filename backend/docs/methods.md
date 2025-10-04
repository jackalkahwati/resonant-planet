# Resonant Worlds Explorer - Methods Documentation

## Overview

The Resonant Worlds Explorer backend implements a multi-stage pipeline for exoplanet transit detection that combines classical signal processing, physics-informed modeling, and machine learning.

## Pipeline Architecture

### 1. Preprocessing (`core/preprocess.py`)

**Goal**: Clean and normalize light curves for downstream analysis.

**Steps**:
1. **Normalization**: Center flux to unity baseline using median or polynomial detrending
2. **Outlier Removal**: Sigma clipping to remove cosmic rays and instrumental artifacts
3. **Detrending**: Median filtering to remove stellar variability (window: 24 hours default)
4. **Gap Handling**: Identify and mark data gaps for proper folding
5. **Uncertainty Estimation**: Compute flux uncertainties from MAD if not provided

**Key Functions**:
- `preprocess_pipeline()`: Full pipeline
- `detrend_light_curve()`: Remove long-term trends
- `fold_light_curve()`: Phase fold at given period

### 2. BLS Period Search (`core/features_bls.py`)

**Goal**: Identify periodic transit-like signals.

**Algorithm**: Box Least Squares (Kovács et al. 2002)

**Implementation**:
1. **Grid Search**: Logarithmic period grid from `min_period` to `max_period`
2. **Duration Grid**: Test multiple transit durations (1% to 10% of period)
3. **Phase Grid**: Sample phases to find best epoch
4. **Power Metric**: Signal Detection Efficiency (SDE)
   ```
   SDE = (depth² × n_in × n_out) / (n_in + n_out)
   ```
5. **Peak Finding**: Identify top N peaks with minimum separation
6. **Refinement**: Fine grid search around each peak

**Output**: List of BLS candidates with period, epoch, duration, depth, SNR

### 3. Physics-Informed Transit Modeling (`physics/`)

**Goal**: Fit detailed transit models and perform validation checks.

#### Modulus Adapter Pattern

The adapter provides a stable interface that can switch between:
- **Local Modulus**: Vendored code in `physics/local_modulus/`
- **External Modulus**: Installed package
- **Mock Backend**: Fallback for testing

**Adapter Interface**:
```python
def fit_transit(time, flux, flux_err) -> TransitFit:
    """Fit physics-based transit model."""
    ...

def run_checks(time, flux, period, t0) -> PhysicsChecks:
    """Run validation checks."""
    ...
```

#### Transit Model (`physics/local_modulus/transit_model.py`)

**Model**: Mandel-Agol formalism (simplified implementation)

**Parameters**:
- Period (P)
- Epoch (t₀)
- Depth (δ)
- Duration (T)
- Impact parameter (b)

**Fitting**:
- Optimizer: L-BFGS-B
- Objective: χ² minimization
- Bounds: Physical constraints on all parameters

**Output**: Best-fit parameters, SNR, χ², log-likelihood

#### Limb Darkening (`physics/local_modulus/limb_darkening.py`)

**Model**: Quadratic limb darkening law
```
I(μ) / I(1) = 1 - u₁(1 - μ) - u₂(1 - μ)²
```

**Coefficients**: Lookup table by stellar T_eff (Claret & Bloemen 2011)

#### Validation Checks (`physics/local_modulus/fits.py`)

**1. Odd-Even Test**
- Separates odd and even numbered transits
- Computes depth difference
- **Flag**: Fail if difference > 10%
- **Purpose**: Rule out eclipsing binaries

**2. Secondary Eclipse Search**
- Searches phase 0.5 (expected secondary for EB)
- Computes SNR of secondary
- **Flag**: Fail if secondary SNR > 3
- **Purpose**: Rule out stellar eclipses

**3. V-shape vs U-shape Discrimination**
- Fits quadratic to transit bottom
- Measures curvature
- **Score**: 0 (V-shaped) to 1 (U-shaped)
- **Flag**: Fail if score < 0.6
- **Purpose**: Planetary transits are U-shaped, grazing EBs are V-shaped

**4. Stellar Density Check**
- Uses Kepler's third law
- Checks if implied density is main-sequence consistent
- **Flag**: Fail if density unrealistic
- **Purpose**: Rule out contamination

### 4. Time Series Embeddings (`core/embeddings_qwen.py`)

**Goal**: Extract learned representations for classification.

**Model**: Qwen Omni-inspired time series encoder

**Architecture** (simplified):
1. **Input**: Interpolated light curve (512 points)
2. **Encoder**: 1D convolutions (7→5→3 kernel sizes)
3. **Pooling**: Global average pooling
4. **Output**: 128-dimensional embedding

**Fallback**: If Qwen weights unavailable, use statistical features:
- Moments (mean, std, skewness, kurtosis)
- Quantiles (25%, 50%, 75%)
- Autocorrelation
- Power spectrum features

### 5. Classifier (Stub Implementation)

**Goal**: Compute probability that candidate is a true planet.

**Current**: Simple heuristic based on SNR
```python
probability = min(0.99, max(0.01, snr / 20.0))
```

**Production**: Should use trained XGBoost or neural network on:
- BLS features (power, SNR, shape)
- Physics fit metrics (χ², log-likelihood)
- Qwen embeddings (128-dim)
- Validation flags (4 binary)

### 6. RL Triage Policy (`core/rl_policy.py`)

**Goal**: Decide action for each candidate to meet false alarm rate target.

**Actions**:
- **Accept**: High confidence, passes all checks → automated confirmation
- **Reject**: Low confidence or fails physics → discard
- **Human Review**: Uncertain → send to expert

**Current Policy**: Threshold-based
```python
score = w₁·P + w₂·SNR + w₃·physics_score

if score ≥ 0.9 and passes_checks:
    action = "accept"
elif score ≤ 0.3:
    action = "reject"
else:
    action = "human_review"
```

**Weights**: Configurable (default: w₁=1.0, w₂=0.3, w₃=0.2)

**Adaptive Thresholds**: Can adjust based on observed false alarm rate

**Future**: Upgrade to contextual bandits (Thompson sampling) to learn from human feedback

### 7. Explainability (`core/explain.py`)

**Goal**: Generate diagnostic plots for human interpretation.

**Plots**:

1. **Phase Fold**: Light curve folded at best period
   - Scatter: all data points
   - Binned: median in phase bins
   - Shows transit shape

2. **BLS Periodogram**: Power vs period
   - Marks best period
   - Shows aliases and harmonics

3. **Odd/Even Overlay**: Separate odd and even transits
   - Blue: odd transits
   - Red: even transits
   - Should overlap for true planets

4. **Secondary Search**: Full phase with secondary window highlighted
   - Shows phase 0.5 region
   - Significant signal indicates EB

**Style**: 
- Monotone-friendly (uses red/blue with distinct markers)
- Grid and labels for accessibility
- 150 DPI for crisp PDF embedding

### 8. Report Generation (`core/report.py`)

**Goal**: One-page PDF summary with plots and rationale.

**Sections**:
1. **Header**: Job ID, dataset, timestamp
2. **Methods**: Brief pipeline description
3. **Summary**: Counts by RL action
4. **Top Candidates**: Table and plots for best 5
5. **Plots**: Phase fold embedded for each

**Library**: ReportLab (pure Python, no external dependencies)

**Output**: 8.5×11" PDF, ~500KB typical size

## Data Flow

```
Input CSV
    ↓
Preprocessing (normalize, detrend, clip outliers)
    ↓
BLS Search (period grid, find peaks)
    ↓
For each candidate:
    ├─ Modulus Transit Fit (parameters, SNR)
    ├─ Physics Checks (odd/even, secondary, shape)
    ├─ Qwen Embedding (128-dim vector)
    └─ Classifier (probability)
    ↓
RL Policy (accept, reject, human_review)
    ↓
Explainability Plots (phase, BLS, odd/even)
    ↓
PDF Report
```

## Switching Modulus Backends

The adapter pattern allows seamless backend switching:

### Using Local Modulus (Default)

```bash
export USE_LOCAL_MODULUS=true
```

The adapter imports from `physics.local_modulus` and logs:
```
✓ Using local Modulus backend
```

### Using External Modulus

```bash
export USE_LOCAL_MODULUS=false
pip install modulus  # hypothetical external package
```

The adapter imports `modulus` and logs:
```
✓ Using external Modulus package
```

### Implementing a New Backend

1. Create module (e.g., `physics/gpu_modulus/`)
2. Implement `fit_transit()` and `run_checks()` matching adapter signatures
3. Update `modulus_adapter._get_modulus_backend()` to detect and load it
4. No changes needed in API or pipeline code

## Performance Characteristics

**Typical Processing Times** (1000-point light curve, single candidate):

| Stage | Time | Notes |
|-------|------|-------|
| Preprocessing | 50 ms | Vectorized NumPy |
| BLS Search | 2-10 s | Period grid size dependent |
| Transit Fit | 100-500 ms | Optimization convergence |
| Physics Checks | 50 ms | Phase folding and stats |
| Qwen Embedding | 10 ms | Single forward pass, CPU |
| Plots | 200 ms | Matplotlib rendering |
| **Total** | **3-12 s** | Per candidate |

**Scaling**: 
- Linear in number of candidates
- Quadratic in BLS period grid size (use coarse then refine)
- Parallelizable across candidates (future Celery implementation)

## Validation Strategy

### Unit Tests
- `test_adapter.py`: Synthetic transit parameter recovery
- `test_preprocess.py`: Normalization, detrending, folding
- `test_api.py`: Endpoint responses, error handling

### Integration Tests
- End-to-end demo run on bundled datasets
- Compare results to known planets (Kepler-10b, etc.)

### Injection/Recovery
- Inject synthetic transits at various SNRs and periods
- Measure detection efficiency vs SNR
- Target: >95% recovery at SNR > 10

## References

- Kovács et al. 2002: "A box-fitting algorithm in the search for periodic transits"
- Mandel & Agol 2002: "Analytic Light Curves for Planetary Transit Searches"
- Claret & Bloemen 2011: "Gravity and limb-darkening coefficients for the Kepler mission"

## Future Improvements

1. **GPU Acceleration**: Move transit fitting to PyTorch for batch processing
2. **Bayesian Inference**: Replace χ² fit with nested sampling (dynesty)
3. **Active Learning**: Use human review labels to retrain classifier
4. **Multi-planet Search**: Iterative BLS with residuals
5. **Stellar Variability Modeling**: GP regression for better detrending
