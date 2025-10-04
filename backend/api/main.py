"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from core.settings import settings
from physics import get_backend_info

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Import routes
from api.routes import datasets, run, status, results, report, compare, nasa, biosignatures

# Create app
app = FastAPI(
    title="Resonant Worlds Explorer API",
    description="Backend API for exoplanet detection using physics-informed methods",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasets.router)
app.include_router(run.router)
app.include_router(status.router)
app.include_router(results.router)
app.include_router(report.router)
app.include_router(compare.router)
app.include_router(nasa.router)  # NASA archive access
app.include_router(biosignatures.router)  # Biosignature detection

# Serve plot images
plots_dir = settings.base_dir / settings.artifacts_dir
if plots_dir.exists():
    app.mount("/api/plots", StaticFiles(directory=str(plots_dir)), name="plots")


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    # Ensure directories exist
    settings.ensure_directories()

    # Log backend info
    backend_info = get_backend_info()
    logger.info(f"Modulus backend: {backend_info}")

    logger.info("Resonant Worlds Explorer API started")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Resonant Worlds Explorer API",
        "version": "0.1.0",
        "status": "running",
        "modulus_backend": get_backend_info(),
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
