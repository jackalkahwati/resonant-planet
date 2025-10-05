# Frontend-Backend Integration Guide

## Overview

This guide explains how to connect the React frontend to the FastAPI backend for real exoplanet detection.

## Quick Start

### 1. Configure Environment

Create `.env` in the project root:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_REAL_BACKEND=true
VITE_DEMO_MODE=true
```

### 2. Start Backend

```bash
cd backend
source venv/bin/activate  # If using venv
uvicorn api.main:app --reload --port 8000
```

Wait for: `✓ Resonant Worlds Explorer API started`

### 3. Start Frontend

```bash
npm run dev
```

### 4. Test Integration

1. Navigate to http://localhost:5173/detect
2. Click "Run All Samples"
3. Watch real-time progress
4. View detected candidates
5. Download PDF report

## API Client Usage

### Import

```typescript
import api, { formatCandidate } from "@/lib/api";
```

### Common Patterns

**Check Backend Availability**:
```typescript
import { checkBackend } from "@/lib/api";

const isAvailable = await checkBackend();
if (!isAvailable) {
  console.error("Backend not responding");
}
```

**List Datasets**:
```typescript
const datasets = await api.listDatasets();
console.log(`Found ${datasets.length} datasets`);
```

**Upload File**:
```typescript
const file = event.target.files[0];
const response = await api.uploadDataset(file);
console.log(`Uploaded as ${response.dataset_id}`);
```

**Run Detection**:
```typescript
// Start job
const { job_id } = await api.startRun({
  dataset_id: "kepler_tp",
  min_period_days: 0.5,
  max_period_days: 10.0,
  min_snr: 7.0,
  max_candidates: 5,
});

// Poll for completion
const finalStatus = await api.pollStatus(job_id, (status) => {
  console.log(`Progress: ${status.progress}% - ${status.stage}`);
  setProgress(status.progress);
});

// Get results
if (finalStatus.status === "completed") {
  const results = await api.getResults(job_id);
  const formatted = results.candidates.map(formatCandidate);
  setResults(formatted);
}
```

**Download Report**:
```typescript
await api.downloadReportAsFile(job_id, "my_report.pdf");
```

**Get Plot Images**:
```typescript
const plotUrl = api.getPlotUrl(candidate.plots.phase_fold_png);
```

## Updated Detect Component

See `src/pages/DetectWithBackend.tsx` for a complete example that:

- Lists real datasets from backend
- Allows file upload
- Runs detection with progress tracking
- Displays candidates from backend
- Shows real diagnostic plots
- Downloads PDF reports

## Type Definitions

All types are defined in `src/lib/api.ts` and match the backend schemas:

- `DatasetInfo` - Dataset metadata
- `RunParams` - Detection parameters
- `JobStatus` - Job progress tracking
- `Candidate` - Detection result
- `ResultsResponse` - Complete results

## Error Handling

The API client throws `APIError` on failures:

```typescript
import { APIError } from "@/lib/api";

try {
  await api.startRun(params);
} catch (error) {
  if (error instanceof APIError) {
    console.error(`API error ${error.status}: ${error.message}`);
    console.log("Details:", error.details);
  }
}
```

## Mock vs Real Backend

**Development Mode** (no backend):
```typescript
const ENABLE_REAL_BACKEND = import.meta.env.VITE_ENABLE_REAL_BACKEND === "true";

if (!ENABLE_REAL_BACKEND) {
  // Use mock data from sampleCandidates.ts
  setResults(sampleCandidates);
} else {
  // Use real API
  const results = await api.getResults(job_id);
}
```

## Testing the Integration

### Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend (check Network tab)
- [ ] Datasets list loads
- [ ] File upload works
- [ ] Detection job starts
- [ ] Progress updates in real-time
- [ ] Results display correctly
- [ ] Plots render (check URLs in Network tab)
- [ ] PDF downloads successfully
- [ ] Error states show appropriately

### Common Issues

**CORS Error**:
- Backend CORS is set to allow all origins in development
- Check console for specific CORS errors
- Verify backend is running on port 8000

**Connection Refused**:
- Backend not started
- Wrong port in `.env`
- Firewall blocking connection

**404 on Plots**:
- Job artifacts not created
- Check `backend/run_artifacts/` directory exists
- Verify plot paths in candidate data

**Polling Timeout**:
- Detection taking too long (increase timeout)
- Backend crashed (check backend logs)
- Job stuck (restart backend)

## Performance Considerations

**Polling Interval**:
- Default: 1 second
- Adjust for long-running jobs: `api.pollStatus(jobId, onProgress, 2000)`

**Timeout**:
- Default: 5 minutes
- Increase for large datasets: `api.pollStatus(jobId, onProgress, 1000, 600000)`

**Caching**:
Consider caching dataset list:

```typescript
const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
const [datasetsLoaded, setDatasetsLoaded] = useState(false);

useEffect(() => {
  if (!datasetsLoaded) {
    api.listDatasets().then(setDatasets);
    setDatasetsLoaded(true);
  }
}, [datasetsLoaded]);
```

## Production Checklist

Before deploying:

- [ ] Set `VITE_API_URL` to production backend URL
- [ ] Add authentication if required
- [ ] Test on slow network (throttle in DevTools)
- [ ] Add loading skeletons for better UX
- [ ] Implement retry logic for failed requests
- [ ] Add error boundaries
- [ ] Set up analytics/monitoring
- [ ] Test accessibility of plots (alt text)
- [ ] Verify PDF downloads on all browsers

## Next Steps

1. **Enhanced UI**: Add progress bars, better error messages
2. **Batch Processing**: Upload multiple files at once
3. **Result Persistence**: Save results to localStorage
4. **Advanced Filtering**: Filter candidates by flags, SNR, etc.
5. **Comparison View**: Side-by-side baseline vs resonant
6. **Export Options**: Download results as JSON/CSV

## Support

- **API Documentation**: http://localhost:8000/docs
- **Backend README**: `backend/README.md`
- **Architecture**: `backend/ARCHITECTURE.md`

---

**Integration Status**: ✅ Ready for testing

Connect your frontend to the backend and start detecting real exoplanets!
