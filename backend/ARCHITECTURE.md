# Resonant Worlds Explorer - Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client (React Frontend)                     │
│                    http://localhost:3000                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      FastAPI Backend                                │
│                   http://localhost:8000                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Routes                                │  │
│  │                                                              │  │
│  │  /api/datasets/  /api/run  /api/status  /api/results       │  │
│  │  /api/report    /api/compare    /api/plots                 │  │
│  └────────┬────────────────────────────────────┬────────────────┘  │
│           │                                    │                    │
│  ┌────────▼────────┐                  ┌────────▼─────────┐         │
│  │  Job Manager    │                  │  Static Files    │         │
│  │  (SQLite)       │                  │  (Plots/PDFs)    │         │
│  └────────┬────────┘                  └──────────────────┘         │
│           │                                                         │
│  ┌────────▼──────────────────────────────────────────────────────┐ │
│  │              Detection Pipeline (Background Task)            │ │
│  │                                                              │ │
│  │  1. Load Data ──► 2. Preprocess ──► 3. BLS Search          │ │
│  │       │                  │                  │                │ │
│  │       │                  ▼                  ▼                │ │
│  │       │           Normalize, Detrend    Period Grid          │ │
│  │       │           Remove Outliers       Find Peaks           │ │
│  │       │                  │                  │                │ │
│  │       │                  └──────┬───────────┘                │ │
│  │       │                         │                            │ │
│  │       │                  ┌──────▼──────┐                     │ │
│  │       │                  │  Candidates  │                     │ │
│  │       │                  └──────┬──────┘                     │ │
│  │       │                         │                            │ │
│  │       │          For each candidate:                         │ │
│  │       │                         │                            │ │
│  │       ├──────────►  4. Physics Fit (Modulus Adapter)        │ │
│  │       │                    │                                 │ │
│  │       │                    ├──► Transit Parameters           │ │
│  │       │                    ├──► Odd/Even Test                │ │
│  │       │                    ├──► Secondary Search             │ │
│  │       │                    └──► Shape Score                  │ │
│  │       │                         │                            │ │
│  │       ├──────────►  5. Qwen Embeddings                       │ │
│  │       │                    │                                 │ │
│  │       │                    └──► 128-dim vector               │ │
│  │       │                         │                            │ │
│  │       ├──────────►  6. Classifier                            │ │
│  │       │                    │                                 │ │
│  │       │                    └──► Probability (0-1)            │ │
│  │       │                         │                            │ │
│  │       ├──────────►  7. RL Policy                             │ │
│  │       │                    │                                 │ │
│  │       │                    └──► accept/reject/human_review   │ │
│  │       │                         │                            │ │
│  │       └──────────►  8. Explainability Plots                  │ │
│  │                            │                                 │ │
│  │                            └──► phase.png, bls.png, etc      │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  9. Report Generator (ReportLab)                            │  │
│  │      ├─► Assemble metadata                                  │  │
│  │      ├─► Embed plots                                        │  │
│  │      └─► Generate PDF                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                   Modulus Backend (Adapter Pattern)                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  modulus_adapter.py (Unified Interface)                     │  │
│  │                                                              │  │
│  │  fit_transit(time, flux, flux_err) -> TransitFit           │  │
│  │  run_checks(time, flux, period, t0) -> PhysicsChecks       │  │
│  └────────┬─────────────────────────────────┬──────────────────┘  │
│           │                                 │                      │
│  ┌────────▼────────┐              ┌─────────▼──────────┐          │
│  │ Local Modulus   │              │ External Modulus   │          │
│  │ (Vendored)      │      OR      │ (pip install)      │          │
│  │                 │              │                    │          │
│  │ transit_model   │              │ (production GPU    │          │
│  │ limb_darkening  │              │  accelerated)      │          │
│  │ fits/checks     │              │                    │          │
│  └─────────────────┘              └────────────────────┘          │
│                                                                     │
│  USE_LOCAL_MODULUS=true          USE_LOCAL_MODULUS=false          │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (`api/`)

**main.py**: FastAPI application with CORS, OpenAPI docs
**routes/**: RESTful endpoints for each resource

```python
datasets.py  -> List, upload, get datasets
run.py       -> Start detection jobs
status.py    -> Poll job status
results.py   -> Retrieve candidates
report.py    -> Generate PDFs
compare.py   -> Baseline vs Resonant metrics
```

### 2. Core Pipeline (`core/`)

**Preprocessing** (`preprocess.py`):
- Input: Raw CSV (time, flux, flux_err)
- Output: Clean, normalized, detrended light curve
- Methods: Median filter, sigma clipping, gap handling

**BLS Search** (`features_bls.py`):
- Input: Preprocessed light curve
- Output: Candidate periods, epochs, depths
- Algorithm: Box Least Squares with grid search

**Embeddings** (`embeddings_qwen.py`):
- Input: Light curve
- Output: 128-dim feature vector
- Model: 1D CNN encoder (Qwen-inspired)

**RL Policy** (`rl_policy.py`):
- Input: Probability, SNR, physics flags
- Output: Action (accept/reject/human_review)
- Policy: Threshold-based (upgradeable to bandits)

**Explainability** (`explain.py`):
- Input: Candidate parameters
- Output: Diagnostic PNG plots
- Plots: Phase fold, BLS, odd/even, secondary

**Report** (`report.py`):
- Input: Job results
- Output: One-page PDF
- Library: ReportLab

### 3. Physics Backend (`physics/`)

**Adapter Pattern**: Allows swapping implementations

```python
# Adapter provides stable interface
from physics import fit_transit, run_checks

# Backend selected at runtime
if USE_LOCAL_MODULUS:
    from physics.local_modulus import ...
else:
    import modulus
```

**Local Modulus** (`local_modulus/`):
- `transit_model.py`: Mandel-Agol fitting with scipy optimize
- `limb_darkening.py`: Quadratic LD coefficient lookup
- `fits.py`: Validation checks (odd/even, secondary, shape, density)

**Benefits**:
- Zero API changes to swap backends
- Easy A/B testing of physics models
- Mock mode for testing without dependencies

### 4. Data Flow

**Request Flow**:
```
POST /api/run
  ↓
Create job in DB (status: queued)
  ↓
Start background task
  ↓
Update status to "running"
  ↓
Pipeline stages (update progress each stage)
  ↓
Save candidates to DB
  ↓
Update status to "completed"
  ↓
GET /api/results/{job_id} → Return candidates
```

**Status Polling**:
```javascript
// Frontend polls for updates
const poll = async () => {
  const response = await fetch(`/api/status/${jobId}`);
  const status = await response.json();
  
  if (status.status === 'completed') {
    // Fetch results
  } else if (status.status === 'running') {
    // Update progress bar
    setTimeout(poll, 1000);
  }
};
```

### 5. Database Schema

**Jobs Table**:
```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    dataset_id TEXT,
    status TEXT,           -- queued, running, completed, failed
    progress REAL,         -- 0-100
    stage TEXT,           -- loading, bls_search, etc
    message TEXT,
    created_at TEXT,
    updated_at TEXT,
    params TEXT           -- JSON
);
```

**Candidates Table**:
```sql
CREATE TABLE candidates (
    candidate_id TEXT PRIMARY KEY,
    job_id TEXT,
    probability REAL,
    period_days REAL,
    t0_bjd REAL,
    depth_ppm REAL,
    duration_hours REAL,
    snr REAL,
    rl_action TEXT,       -- accept, reject, human_review
    flags TEXT,           -- JSON
    plots TEXT,           -- JSON (URLs)
    created_at TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
);
```

### 6. Configuration (`core/settings.py`)

**Pydantic Settings**: Type-safe environment variables

```python
class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Modulus
    use_local_modulus: bool = True
    
    # Data
    demo_mode: bool = True
    
    # Jobs
    job_backend: Literal["background", "celery"] = "background"
    
    # Paths
    upload_dir: str = "uploads"
    artifacts_dir: str = "run_artifacts"
```

**Loading**: Reads from `.env` file or environment

### 7. Background Tasks

**Default**: FastAPI BackgroundTasks
```python
@router.post("/")
async def start_run(params: RunParams, background_tasks: BackgroundTasks):
    job_id = create_job()
    background_tasks.add_task(run_pipeline, job_id)
    return {"job_id": job_id}
```

**Optional**: Celery workers (for scale)
```bash
JOB_BACKEND=celery docker-compose --profile celery up
```

### 8. Deployment Options

**Development**:
```bash
uvicorn api.main:app --reload --port 8000
```

**Production (Single Server)**:
```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Production (Multi-Worker)**:
```bash
docker-compose --profile celery up
# API server + Redis + Celery workers
```

**Scaling**:
- Horizontal: Multiple API containers behind load balancer
- Vertical: Increase Celery workers
- Database: Migrate SQLite → PostgreSQL

## Security Considerations

**Current (Development)**:
- CORS: Allow all origins
- No authentication
- No rate limiting

**Production TODO**:
- [ ] Add API key authentication
- [ ] Restrict CORS to specific domains
- [ ] Rate limit endpoints (slowapi)
- [ ] Input validation (Pydantic already helps)
- [ ] File upload size limits
- [ ] SQL injection protection (SQLite parameterized queries ✓)

## Performance Characteristics

**Throughput**: ~1-3 candidates/second (single core)
**Latency**: ~10-30 seconds per job (100 points, 5 candidates)
**Memory**: ~500 MB per worker (including NumPy/PyTorch)

**Bottlenecks**:
1. BLS grid search (O(n_periods × n_durations × n_phases))
2. Transit fitting (scipy.optimize, 100-500ms)
3. Plot rendering (matplotlib, 200ms)

**Optimizations**:
- Coarse-then-fine BLS grid
- Parallel candidate processing (Celery)
- GPU transit fitting (PyTorch)
- Plot caching

## Error Handling

**Levels**:
1. **API**: HTTPException with status codes
2. **Pipeline**: Try/except, update job status to "failed"
3. **Physics**: Return `success: False` with message

**Example**:
```python
try:
    fit = fit_transit(time, flux)
except Exception as e:
    logger.error(f"Fit failed: {e}")
    return TransitFit(success=False, message=str(e), ...)
```

## Logging

**Configuration**:
```python
logging.basicConfig(
    level=LOG_LEVEL,  # INFO (default), DEBUG, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

**Usage**:
```python
logger.info(f"[Job {job_id}] Starting BLS search")
logger.warning(f"Transit fit failed for candidate {i}")
logger.error(f"Pipeline failed: {e}", exc_info=True)
```

## Testing Strategy

**Unit Tests**: Individual functions (preprocess, BLS, adapter)
**Integration Tests**: Full API endpoints
**Synthetic Data**: Parameter recovery on known planets

**Coverage Goal**: >80% for critical paths

## Future Architecture

**Short Term**:
- Add Redis caching for periodograms
- WebSocket for real-time progress
- Batch upload API

**Medium Term**:
- GPU-accelerated transit fitting
- Distributed BLS search (Dask)
- Multi-planet search

**Long Term**:
- Kubernetes deployment
- Streaming data (Kafka)
- ML model serving (TensorFlow Serving)

---

*Architecture Version: 1.0*
*Last Updated: 2025-09-30*
