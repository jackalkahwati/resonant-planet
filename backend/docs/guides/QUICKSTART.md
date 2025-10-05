# Quickstart Guide - Resonant Worlds Explorer Backend

Get the backend running in under 5 minutes.

## Prerequisites

- Python 3.11+
- pip

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: Installation may take 2-3 minutes due to PyTorch and scientific packages.

## Step 2: Configure Environment

```bash
# Create .env file with defaults
cat > .env << EOF
USE_LOCAL_MODULUS=true
DEMO_MODE=true
JOB_BACKEND=background
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
EOF
```

## Step 3: Start Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Modulus backend: {'backend': 'local', ...}
INFO:     Resonant Worlds Explorer API started
```

## Step 4: Test the API

Open a new terminal and run:

```bash
# Check health
curl http://localhost:8000/health

# List datasets
curl http://localhost:8000/api/datasets/

# Or use the demo script
python run_demo.py
```

## Step 5: Run Demo Detection

The `run_demo.py` script will:
1. Check server status
2. List available datasets
3. Run detection on demo data
4. Show results and generate PDF report

Expected output:
```
======================================================================
Resonant Worlds Explorer - Demo Script
======================================================================

1. Checking server status...
   ✓ Server is running

2. Listing available datasets...
   Found 2 datasets:
   - kepler_tp: 96 points, 2.0 days
   - kepler_fp: 85 points, 2.1 days

3. Running detection on dataset: kepler_tp...
   ✓ Started job: abc123...

4. Monitoring progress...
   [  5.0%] loading: Loading data
   [ 15.0%] preprocessing: Preprocessing light curve
   [ 30.0%] bls_search: Running BLS period search
   [ 90.0%] candidate_analysis: Analyzing candidate 1/1
   [100.0%] completed: Found 1 candidates
   ✓ Job completed!

5. Retrieving results...
   Total candidates: 1
   - Accepted: 1
   - Rejected: 0
   - Human review: 0

6. Candidate summary:

   ID          | Period (d) | Depth (ppm) | SNR  | Action
   --------------------------------------------------------------
   abc123_1    |     1.2600 |      2180.0 |  9.2 | accept

7. Physics flags for first candidate:
   ✓ odd_even_ok
   ✓ secondary_low
   ✓ shape_u_like
   ✓ density_consistent

8. Downloading PDF report...
   ✓ Saved to: demo_report_abc123.pdf
   File size: 234.5 KB

======================================================================
Demo completed successfully!
======================================================================
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`, ensure you're in the backend directory and dependencies are installed:

```bash
cd backend
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is busy, use a different port:

```bash
uvicorn api.main:app --port 8001
```

And update the demo script:
```python
API_URL = "http://localhost:8001"
```

### No Demo Datasets

If `run_demo.py` reports no datasets, ensure demo files exist:

```bash
ls -la assets/demos/
```

You should see:
```
kepler_tp.csv
kepler_fp.csv
```

### Modulus Backend Not Found

The backend will automatically use a mock implementation if local Modulus is unavailable. Check the logs:

```
INFO:     Modulus backend: {'backend': 'local', 'is_mock': True, ...}
```

This is expected for the initial demo. The mock backend provides the same API but uses simplified physics models.

## Next Steps

### Run Tests

```bash
pytest tests/ -v
```

### Try Docker

```bash
docker-compose up
```

### Connect Frontend

The frontend (Vite+React) should connect to `http://localhost:8000` automatically.

### Add Real Data

Upload your own light curve:

```python
import requests

files = {"file": ("my_lightcurve.csv", open("my_lightcurve.csv", "rb"), "text/csv")}
response = requests.post("http://localhost:8000/api/datasets/upload", files=files)
dataset_id = response.json()["dataset_id"]

# Run detection
response = requests.post(
    "http://localhost:8000/api/run",
    json={"dataset_id": dataset_id, "min_period_days": 1.0, "max_period_days": 20.0}
)
```

CSV format:
```csv
time,flux,flux_err
0.0,1.0000,0.001
0.02,0.9998,0.001
0.04,1.0001,0.001
...
```

## API Documentation

Once the server is running, view interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development Workflow

### Hot Reload

The `--reload` flag enables automatic server restart on code changes.

### Debug Logging

Set `LOG_LEVEL=DEBUG` in `.env` for verbose output.

### Add New Routes

1. Create `api/routes/my_route.py`
2. Add router to `api/main.py`
3. Test with `pytest tests/test_api.py`

### Modify Modulus Backend

1. Edit `physics/local_modulus/transit_model.py`
2. Test with `pytest tests/test_adapter.py`
3. No API changes needed (adapter isolates physics from API)

## Production Deployment

For production use:

```bash
# Use Gunicorn with multiple workers
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use Docker
docker-compose up -d
```

See `README.md` for full production setup.

## Support

- **Documentation**: `docs/methods.md`
- **Issues**: Check logs in terminal for errors
- **Tests**: `pytest tests/ -v` to verify installation

Happy planet hunting! 🪐
