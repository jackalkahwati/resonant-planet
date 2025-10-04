# Getting Started - Resonant Worlds Explorer

Complete guide to running the full-stack exoplanet detection system.

## Overview

This project consists of:
- **Frontend**: React + Vite + TypeScript + shadcn/ui
- **Backend**: FastAPI + Python 3.11 + Local Modulus physics

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Modern browser** (Chrome, Firefox, Safari, Edge)

## Quick Start (5 Minutes)

### Terminal 1: Backend

```bash
# Navigate to backend
cd backend

# Install dependencies (first time only)
./install.sh

# Start server
source venv/bin/activate  # If using venv
uvicorn api.main:app --reload --port 8000
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ Using local Modulus backend
✓ Resonant Worlds Explorer API started
```

### Terminal 2: Frontend

```bash
# In project root
npm install  # First time only

# Start dev server
npm run dev
```

Visit: **http://localhost:5173**

### Terminal 3: Test

```bash
./test_integration.sh
```

## Detailed Setup

### Backend Setup

1. **Install Python 3.11+**
   ```bash
   python3 --version  # Should be 3.11 or higher
   ```

2. **Create virtual environment** (recommended)
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or use the installation script:
   ```bash
   ./install.sh
   ```

4. **Configure environment**
   
   The backend comes with sensible defaults. To customize, create `backend/.env`:
   ```bash
   USE_LOCAL_MODULUS=true
   DEMO_MODE=true
   JOB_BACKEND=background
   LOG_LEVEL=INFO
   ```

5. **Start backend**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Test backend**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   
   python run_demo.py
   # Runs full demo with PDF report
   ```

### Frontend Setup

1. **Install Node.js 18+**
   ```bash
   node --version  # Should be 18 or higher
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API connection**
   
   Create `.env` in project root:
   ```bash
   VITE_API_URL=http://localhost:8000
   VITE_ENABLE_REAL_BACKEND=true
   VITE_DEMO_MODE=true
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open browser**
   
   Navigate to http://localhost:5173

## Using the System

### Option 1: Demo with Sample Data

1. Click **"Try Demo Detection"** on home page
2. Navigate to **Detect** page
3. Click **"Run All Samples"**
4. Watch progress bar
5. View detected candidates
6. Click **"Compare"** to see baseline vs resonant metrics
7. Click candidate to view diagnostic plots
8. Download PDF report

### Option 2: Upload Your Own Data

1. Navigate to **Detect** page
2. Click **"Upload"** tab
3. Upload CSV file with columns:
   ```
   time,flux,flux_err
   0.0,1.0000,0.001
   0.02,0.9998,0.001
   ...
   ```
4. Click **"Run Detection"**
5. Results appear in ~10-30 seconds

### Option 3: Use API Directly

**List datasets**:
```bash
curl http://localhost:8000/api/datasets/
```

**Start detection**:
```bash
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"kepler_tp","min_period_days":0.5,"max_period_days":10.0}'
```

**Check status**:
```bash
curl http://localhost:8000/api/status/{job_id}
```

**Get results**:
```bash
curl http://localhost:8000/api/results/{job_id}
```

**Download report**:
```bash
curl http://localhost:8000/api/report/{job_id} --output report.pdf
```

## File Structure

```
resonant-worlds-explorer/
├── backend/                      # FastAPI backend
│   ├── api/                      # Routes
│   ├── core/                     # Pipeline components
│   ├── physics/                  # Modulus adapter
│   ├── tests/                    # Test suite
│   ├── assets/demos/             # Sample data
│   └── README.md                 # Backend docs
│
├── src/                          # React frontend
│   ├── pages/                    # Page components
│   ├── components/               # UI components
│   ├── lib/api.ts                # API client
│   └── hooks/                    # React hooks
│
├── GETTING_STARTED.md            # This file
├── FRONTEND_INTEGRATION.md       # API integration guide
├── BACKEND_SUMMARY.md            # Backend architecture
└── test_integration.sh           # Full-stack test
```

## Common Workflows

### Developing Backend

```bash
cd backend

# Make changes to code
vim api/routes/run.py

# Server auto-reloads (--reload flag)

# Test changes
pytest tests/ -v

# Check API docs
open http://localhost:8000/docs
```

### Developing Frontend

```bash
# Make changes to code
vim src/pages/Detect.tsx

# Vite auto-reloads

# Test in browser
open http://localhost:5173
```

### Adding a New Feature

**Backend**:
1. Add route in `backend/api/routes/`
2. Update schemas in `backend/core/schemas.py`
3. Add tests in `backend/tests/`
4. Document in `backend/README.md`

**Frontend**:
1. Add API method in `src/lib/api.ts`
2. Create hook if needed in `src/hooks/`
3. Update UI in `src/pages/` or `src/components/`
4. Test integration

## Troubleshooting

### Backend Won't Start

**Issue**: `ModuleNotFoundError`
```bash
cd backend
pip install -r requirements.txt
```

**Issue**: Port 8000 in use
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn api.main:app --port 8001
```

**Issue**: Import errors
```bash
# Ensure you're in backend/ directory
cd backend

# Activate venv if using
source venv/bin/activate
```

### Frontend Won't Connect

**Issue**: CORS errors
- Backend CORS is set to allow all origins in dev
- Check backend is running on port 8000
- Check `.env` has correct `VITE_API_URL`

**Issue**: 404 on API calls
- Verify backend URL in browser: http://localhost:8000
- Check Network tab in DevTools
- Verify `.env` file exists and is loaded

**Issue**: Plots not showing
- Check backend logs for plot generation errors
- Verify `backend/run_artifacts/` directory exists
- Check plot URLs in candidate data

### Performance Issues

**Backend slow**:
- Reduce `max_candidates` in detection params
- Reduce BLS grid size (edit `core/features_bls.py`)
- Use faster preset

**Frontend lag**:
- Check Network tab for slow requests
- Reduce polling interval
- Clear browser cache

## Production Deployment

### Backend

```bash
# Install production dependencies
pip install gunicorn

# Run with multiple workers
gunicorn api.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

Or use Docker:
```bash
cd backend
docker-compose up -d
```

### Frontend

```bash
# Build for production
npm run build

# Dist folder can be served by nginx, Apache, or CDN
```

## Testing

### Unit Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
npm test
```

### Integration Test

```bash
./test_integration.sh
```

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Datasets list loads
- [ ] File upload works
- [ ] Detection runs successfully
- [ ] Progress updates in real-time
- [ ] Results display correctly
- [ ] Plots render
- [ ] PDF downloads
- [ ] Error states work

## Next Steps

### Learn More

- **Backend Architecture**: `backend/ARCHITECTURE.md`
- **Methods Documentation**: `backend/docs/methods.md`
- **API Integration**: `FRONTEND_INTEGRATION.md`
- **API Reference**: http://localhost:8000/docs

### Extend the System

1. **Add New Detection Method**
   - Implement in `backend/core/`
   - Update pipeline in `backend/api/routes/run.py`
   - Add tests

2. **Customize UI**
   - Modify components in `src/components/`
   - Add new pages in `src/pages/`
   - Update routing in `src/App.tsx`

3. **Integrate External Data**
   - Add data source in `backend/api/routes/datasets.py`
   - Create data adapter
   - Update frontend to show new sources

4. **Deploy to Cloud**
   - Set up PostgreSQL for production database
   - Configure Redis for Celery
   - Deploy backend to Heroku/AWS/GCP
   - Deploy frontend to Vercel/Netlify
   - Set environment variables

## Support

- **Issues**: Check console logs in browser and terminal
- **Debugging**: Enable DEBUG log level in backend `.env`
- **Questions**: Review documentation in `backend/` and root
- **Updates**: Pull latest changes and reinstall dependencies

## Success Checklist

After setup, you should be able to:

- [x] Start backend (port 8000)
- [x] Start frontend (port 5173)
- [x] See API docs at http://localhost:8000/docs
- [x] Load demo datasets
- [x] Run detection on sample data
- [x] See progress in real-time
- [x] View candidate results
- [x] Download PDF report
- [x] Upload custom light curve
- [x] See diagnostic plots
- [x] Compare baseline vs resonant

---

**Status**: ✅ Ready to discover exoplanets!

Happy planet hunting! 🪐🔭
