# Connect to Modulus Cloud Run API

Your backend now connects to an external Modulus Cloud Run instance instead of running it locally.

## Configuration

Set these environment variables:

### Local Development
Create `backend/.env`:
```bash
# Modulus API Configuration
USE_MODULUS_API=true
MODULUS_API_URL=https://your-modulus-service-xxx.run.app
MODULUS_API_KEY=your-api-key-if-needed  # Optional
```

### Railway Deployment

Go to Railway Dashboard → resonant-worlds-backend → backend-api → Variables:

Add:
- `USE_MODULUS_API` = `true`
- `MODULUS_API_URL` = `https://your-modulus-service-xxx.run.app`
- `MODULUS_API_KEY` = `your-api-key` (if your service requires authentication)

### Vercel Frontend

No changes needed! The frontend talks to Railway, which talks to Modulus.

## Architecture

```
┌────────────────────────────────────────┐
│  Frontend (Vercel)                     │
│  https://resonant-planet.vercel.app    │
└───────────────┬────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────────────┐
│  Backend (Railway)                                │
│  https://backend-api-production-6a91.up.railway   │
│  • Fetch NASA data                                 │
│  • Run BLS detection                               │
│  • Call Modulus API →                             │
└───────────────┬───────────────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────┐
│  Modulus Cloud Run (Your Separate Repo)  │
│  https://your-modulus-xxx.run.app         │
│  • PAT (Prime Algebra Transformer)        │
│  • Exact computation                       │
│  • Transit fitting                         │
│  • Physics validation                      │
└───────────────────────────────────────────┘
```

## API Endpoints

Your Modulus service should expose:

- `GET /health` - Health check
- `POST /fit_transit` - Fit transit model
  ```json
  {
    "time": [0, 1, 2, ...],
    "flux": [1.0, 0.99, 1.0, ...],
    "flux_err": [0.001, 0.001, ...] // optional
  }
  ```
- `POST /run_checks` - Physics validation
  ```json
  {
    "time": [0, 1, 2, ...],
    "flux": [1.0, 0.99, 1.0, ...],
    "period_days": 3.14,
    "t0_bjd": 2456789.0
  }
  ```

## Testing

Test the connection:
```bash
cd backend
python -c "from physics import get_backend_info; print(get_backend_info())"
```

Should show:
```
{'backend': 'api', 'url': 'https://...', 'status': 'connected'}
```

## Fallback

If Modulus API is unreachable, the system will:
1. Log warnings
2. Use local physics models (`backend/physics/local_modulus/`)
3. Continue operating (with slightly lower accuracy)

This ensures your system stays online even if Modulus has issues!

## Clean Codebase

The embedded `modulus_real/` directory (32MB) has been removed since you're using the external service. This keeps your repo lean and maintains proper separation of concerns.
