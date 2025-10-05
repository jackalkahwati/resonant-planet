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
from core.cache import get_cache_stats, clear_all_caches

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

from api.routes import datasets, run, status, results, report, compare, nasa, biosignatures

app = FastAPI(
    title="Resonant Worlds Explorer API",
    description="Backend API for exoplanet detection using physics-informed methods",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(run.router)
app.include_router(status.router)
app.include_router(results.router)
app.include_router(report.router)
app.include_router(compare.router)
app.include_router(nasa.router)
app.include_router(biosignatures.router)

plots_dir = settings.base_dir / settings.artifacts_dir
if plots_dir.exists():
    app.mount("/api/plots", StaticFiles(directory=str(plots_dir)), name="plots")


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    settings.ensure_directories()

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


@app.get("/api/cache/stats")
async def cache_stats():
    """
    Get cache statistics.
    
    Returns hit rates, sizes, and usage for preprocessing and BLS caches.
    """
    stats = get_cache_stats()
    return {
        "status": "ok",
        "caches": stats,
        "description": {
            "preprocess": "Light curve preprocessing (normalization, detrending, outlier removal)",
            "bls": "Box Least Squares period search results"
        }
    }


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear all caches and reset statistics."""
    clear_all_caches()
    return {
        "status": "ok",
        "message": "All caches cleared"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
