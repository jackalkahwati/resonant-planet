# Vercel Environment Variable Setup

## Backend API URL

Your backend is now live at:
```
https://backend-api-production-6a91.up.railway.app
```

## Steps to Connect Frontend to Backend

### Option 1: Via Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/jackalkahwatis-projects/resonant-planet)
2. Click on your **resonant-planet** project
3. Go to **Settings** → **Environment Variables**
4. Add a new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://backend-api-production-6a91.up.railway.app`
   - **Environment**: Select **Production**, **Preview**, and **Development**
5. Click **Save**
6. Go to **Deployments** and click **Redeploy** on the latest deployment

### Option 2: Via Vercel CLI

If you want to use the CLI instead:

```bash
# Link the project first
vercel link

# Add the environment variable
echo "https://backend-api-production-6a91.up.railway.app" | vercel env add VITE_API_URL production

# Trigger a new deployment
vercel --prod
```

## Test the Connection

After redeploying, your frontend at `https://resonant-planet.vercel.app` will be able to communicate with the backend API.

You can verify the connection by:
1. Opening the browser console
2. Checking that API requests go to the Railway URL
3. Testing the detection workflow

## Current Status

✅ Backend deployed on Railway: https://backend-api-production-6a91.up.railway.app
✅ Frontend deployed on Vercel: https://resonant-planet.vercel.app
⏳ Environment variable needs to be added (follow steps above)
⏳ Frontend needs to be redeployed after adding the variable

## API Endpoints Available

- `GET /` - API info and status
- `POST /api/run` - Start a detection run
- `GET /api/status/{job_id}` - Check run status
- `GET /api/results/{job_id}` - Get detection results
- `POST /api/upload` - Upload custom light curve data
