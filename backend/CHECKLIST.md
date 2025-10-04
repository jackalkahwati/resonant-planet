# Backend Verification Checklist

Use this checklist to verify the backend is correctly set up and working.

## ✅ Installation Checklist

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] All files present (run `ls -la` in backend/)
- [ ] Run installation script: `./install.sh`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] Directories created: `ls uploads/ run_artifacts/ assets/`
- [ ] .env file exists: `cat .env`

## ✅ Server Startup Checklist

- [ ] Server starts: `uvicorn api.main:app --reload --port 8000`
- [ ] No import errors in console
- [ ] Sees log: "Modulus backend: ..."
- [ ] Sees log: "Resonant Worlds Explorer API started"
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] Root endpoint responds: `curl http://localhost:8000/`
- [ ] OpenAPI docs load: Open http://localhost:8000/docs

## ✅ Demo Checklist

- [ ] Demo datasets exist: `ls assets/demos/*.csv`
- [ ] Demo script runs: `python run_demo.py`
- [ ] Server shows datasets: 2 found (kepler_tp, kepler_fp)
- [ ] Job starts: Returns job_id
- [ ] Job progresses: Shows stages (loading, preprocessing, bls_search, ...)
- [ ] Job completes: Status = "completed"
- [ ] Results return: At least 1 candidate
- [ ] PDF generates: demo_report_*.pdf created
- [ ] PDF is valid: Can open with Preview/Adobe

## ✅ API Endpoints Checklist

Test each endpoint:

### Datasets
- [ ] `GET /api/datasets/` - Returns list
- [ ] `POST /api/datasets/upload` - Accepts CSV file
- [ ] `GET /api/datasets/{id}` - Returns dataset info

### Detection
- [ ] `POST /api/run` - Starts job, returns job_id
- [ ] `GET /api/status/{job_id}` - Returns status object
- [ ] `GET /api/results/{job_id}` - Returns candidates array

### Reports
- [ ] `GET /api/report/{job_id}` - Downloads PDF
- [ ] `POST /api/compare` - Returns comparison data

### Static
- [ ] `GET /api/plots/{job}/{cand}/phase.png` - Image loads

## ✅ Modulus Backend Checklist

- [ ] Adapter loads: `python3 -c "from physics import modulus_adapter"`
- [ ] Backend info: `python3 -c "from physics import get_backend_info; print(get_backend_info())"`
- [ ] fit_transit works: Run `pytest tests/test_adapter.py::TestModulusAdapter::test_fit_transit_synthetic -v`
- [ ] run_checks works: Run `pytest tests/test_adapter.py::TestModulusAdapter::test_run_checks -v`
- [ ] Mock fallback works: Logs show "is_mock: True" if no Modulus code

## ✅ Tests Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Adapter tests: `pytest tests/test_adapter.py -v`
- [ ] Preprocess tests: `pytest tests/test_preprocess.py -v`
- [ ] API tests: `pytest tests/test_api.py -v`
- [ ] Coverage >70%: `pytest tests/ --cov=. --cov-report=term`

## ✅ Docker Checklist (Optional)

- [ ] Docker installed: `docker --version`
- [ ] Build succeeds: `docker-compose build`
- [ ] Container starts: `docker-compose up`
- [ ] API responds: `curl http://localhost:8000/health`
- [ ] Logs show startup: `docker-compose logs api`
- [ ] Can stop cleanly: `docker-compose down`

## ✅ Code Quality Checklist

- [ ] No syntax errors: All .py files parse
- [ ] Type hints present: Most functions annotated
- [ ] Docstrings: All public functions documented
- [ ] Error handling: Try/except blocks in API routes
- [ ] Logging: Uses `logging` module, not print()
- [ ] Configuration: Uses settings.py, not hardcoded values

## ✅ Documentation Checklist

- [ ] README.md - Installation, API reference
- [ ] QUICKSTART.md - 5-minute guide
- [ ] docs/methods.md - Algorithm details
- [ ] Inline docstrings - NumPy style
- [ ] .env.example - All config options
- [ ] BACKEND_SUMMARY.md - Architecture overview

## ✅ Production Readiness Checklist

For production deployment:

- [ ] Set specific CORS origins in `api/main.py`
- [ ] Use PostgreSQL instead of SQLite (`DATABASE_URL`)
- [ ] Enable Celery for background jobs (`JOB_BACKEND=celery`)
- [ ] Set up Redis for Celery (`CELERY_BROKER_URL`)
- [ ] Use Gunicorn with multiple workers
- [ ] Set up reverse proxy (nginx/traefik)
- [ ] Enable HTTPS (certbot/Let's Encrypt)
- [ ] Configure proper logging (file rotation)
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Database backups scheduled
- [ ] Rate limiting configured
- [ ] API authentication added

## Common Issues

### Issue: Server won't start
**Check**:
- Python 3.11+ installed
- All dependencies in requirements.txt installed
- No port conflicts on 8000 (`lsof -i :8000`)

### Issue: Import errors
**Fix**: 
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Demo fails with "no datasets"
**Fix**:
```bash
ls assets/demos/  # Should show kepler_tp.csv, kepler_fp.csv
```

### Issue: Plots don't render
**Check**:
- Directory exists: `mkdir -p run_artifacts`
- Permissions: `chmod 755 run_artifacts`

### Issue: PDF generation fails
**Fix**:
```bash
# Install system dependencies for WeasyPrint
# macOS: brew install cairo pango gdk-pixbuf
# Ubuntu: apt-get install libcairo2 libpango-1.0-0
pip install --force-reinstall weasyprint reportlab
```

## Status Dashboard

After completing checklist, you should have:

| Component | Status |
|-----------|--------|
| Installation | ✓ Complete |
| Server Startup | ✓ Running |
| Demo Run | ✓ Success |
| All Endpoints | ✓ Responding |
| Modulus Backend | ✓ Loading |
| Tests | ✓ Passing |
| Documentation | ✓ Complete |

**Overall Status**: 🟢 Ready for Integration

---

*Last Updated: 2025-09-30*
