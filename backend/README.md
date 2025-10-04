# Resonant Worlds Explorer - Backend API

Backend API for exoplanet detection using physics-informed methods with local Modulus integration.

## Features

- **Physics-Informed Transit Modeling**: Local Modulus backend for accurate transit fits
- **BLS Period Search**: Box Least Squares algorithm for period detection
- **Qwen Omni Embeddings**: Time series embeddings for classification
- **RL-Based Triage**: Reinforcement learning policy for candidate prioritization
- **Explainability**: Diagnostic plots (phase fold, odd/even, secondary eclipse search)
- **PDF Reports**: One-page reports with plots and method summary
- **Demo Mode**: Bundled light curves for quick testing

## Quick Start

### Local Development

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variables**:
```bash
cp .env.example .env
# Edit .env to configure settings
```

3. **Run the server**:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Test the API**:
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Docker

1. **Build and run**:
```bash
docker-compose up -d
```

2. **View logs**:
```bash
docker-compose logs -f api
```

3. **Stop**:
```bash
docker-compose down
```

## API Endpoints

### Datasets
- `GET /api/datasets/` - List available datasets
- `POST /api/datasets/upload` - Upload light curve CSV
- `GET /api/datasets/{dataset_id}` - Get dataset info

### Detection
- `POST /api/run` - Start detection run
- `GET /api/status/{job_id}` - Check job status
- `GET /api/results/{job_id}` - Get results

### Reports & Comparison
- `GET /api/report/{job_id}` - Generate PDF report
- `POST /api/compare` - Compare baseline vs resonant

## Demo Script

```python
import requests

# List datasets
response = requests.get("http://localhost:8000/api/datasets/")
datasets = response.json()
print(f"Found {len(datasets)} datasets")

# Run detection on demo dataset
response = requests.post(
    "http://localhost:8000/api/run",
    json={
        "dataset_id": "kepler_tp",
        "min_period_days": 0.5,
        "max_period_days": 10.0,
        "min_snr": 7.0,
        "max_candidates": 5
    }
)
job = response.json()
job_id = job["job_id"]
print(f"Started job {job_id}")

# Check status
import time
while True:
    response = requests.get(f"http://localhost:8000/api/status/{job_id}")
    status = response.json()
    print(f"Status: {status['status']} ({status['progress']:.1f}%)")
    
    if status["status"] == "completed":
        break
    
    time.sleep(2)

# Get results
response = requests.get(f"http://localhost:8000/api/results/{job_id}")
results = response.json()
print(f"Found {results['total_candidates']} candidates")

for candidate in results["candidates"]:
    print(f"  P={candidate['period_days']:.3f}d, SNR={candidate['snr']:.1f}, Action={candidate['rl_action']}")

# Download report
response = requests.get(f"http://localhost:8000/api/report/{job_id}")
with open(f"report_{job_id}.pdf", "wb") as f:
    f.write(response.content)
print("Downloaded PDF report")
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LOCAL_MODULUS` | `true` | Use local vendored Modulus code |
| `DEMO_MODE` | `true` | Enable demo datasets |
| `JOB_BACKEND` | `background` | Job backend: `background` or `celery` |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

See `.env.example` for full list.

## Project Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI application
│   └── routes/              # API route handlers
├── core/
│   ├── preprocess.py        # Light curve preprocessing
│   ├── features_bls.py      # BLS period search
│   ├── embeddings_qwen.py   # Qwen embeddings
│   ├── rl_policy.py         # RL triage policy
│   ├── explain.py           # Diagnostic plots
│   ├── report.py            # PDF generation
│   ├── jobs.py              # Job management
│   └── settings.py          # Configuration
├── physics/
│   ├── modulus_adapter.py   # Unified Modulus interface
│   └── local_modulus/       # Vendored Modulus code
│       ├── transit_model.py
│       ├── limb_darkening.py
│       └── fits.py
├── assets/
│   └── demos/               # Demo light curves
├── tests/                   # Test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Modulus Backend

The backend uses a clean adapter pattern for Modulus integration:

- **Local Mode** (`USE_LOCAL_MODULUS=true`): Uses vendored code in `physics/local_modulus/`
- **External Mode** (`USE_LOCAL_MODULUS=false`): Imports from installed `modulus` package
- **Mock Mode**: Fallback if neither available

This allows you to swap backends without touching the API layer.

See [docs/methods.md](docs/methods.md) for implementation details.

## Testing

Run tests:
```bash
pytest tests/ -v
```

Run specific test:
```bash
pytest tests/test_adapter.py -v
```

With coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Development

### Adding a New Modulus Function

1. Add function to `physics/local_modulus/`
2. Update `physics/local_modulus/__init__.py` to call it
3. Add wrapper in `physics/modulus_adapter.py`
4. Write test in `tests/test_adapter.py`

### Adding a New Route

1. Create route file in `api/routes/`
2. Define Pydantic schemas in `core/schemas.py`
3. Include router in `api/main.py`
4. Add tests in `tests/test_api.py`

## Production Deployment

For production:

1. Set `JOB_BACKEND=celery` in environment
2. Use `docker-compose --profile celery up` to start workers
3. Configure proper CORS origins in `api/main.py`
4. Set up reverse proxy (nginx/traefik)
5. Enable HTTPS
6. Use PostgreSQL instead of SQLite for multi-worker setups

## Troubleshooting

**Issue**: "Modulus not found"
- Check `USE_LOCAL_MODULUS` is set to `true`
- Verify `physics/local_modulus/` exists

**Issue**: "Job stuck in running"
- Check logs: `docker-compose logs api`
- Restart: `docker-compose restart api`

**Issue**: "Plots not rendering"
- Ensure `run_artifacts/` directory is writable
- Check plot URLs in candidate results

## License

See LICENSE file in project root.

## Contributing

See CONTRIBUTING.md for development guidelines.
