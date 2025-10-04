"""
Pydantic models for request/response validation and internal data structures.

Defines schemas for:
- Transit fits and physics checks
- Candidate representation
- Job status and results
- API request/response models
- Biosignature analysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Literal
from datetime import datetime


# ============================================================================
# Transit Physics Models
# ============================================================================

class TransitFit(BaseModel):
    """Result of Modulus transit fit."""
    period_days: float
    t0_bjd: float
    depth_ppm: float
    duration_hours: float
    impact_parameter: float
    limb_darkening: Tuple[float, float]
    snr: float
    log_likelihood: float
    chi2: float
    success: bool
    message: str


class PhysicsChecks(BaseModel):
    """Result of Modulus physics validation checks."""
    odd_even_depth_delta_pct: float
    secondary_eclipse_snr: float
    v_vs_u_shape_score: float
    centroid_shift_proxy: Optional[float] = None
    stellar_density_consistent: bool


# ============================================================================
# Biosignature Models
# ============================================================================

class MolecularFeature(BaseModel):
    """Detected molecular absorption feature."""
    molecule: str
    wavelength_um: float
    depth_ppm: float
    confidence: float


class BiosignatureResult(BaseModel):
    """Result of biosignature analysis."""
    biosignature_score: float = Field(..., ge=0.0, le=1.0, description="Probability of life (0-1)")
    detected_molecules: List[str]
    disequilibrium_score: float
    false_positive_probability: float
    confidence_level: Literal["very_low", "low", "medium", "high"]
    explanation: str
    modulus_analysis: Optional[dict] = None


class SpectrumUploadResponse(BaseModel):
    """Response after uploading spectrum."""
    spectrum_id: str
    filename: str
    num_points: int
    wavelength_range_um: Tuple[float, float]
    message: str


class BiosignatureRequest(BaseModel):
    """Request to analyze spectrum for biosignatures."""
    spectrum_id: str
    planet_radius_earth: float = Field(1.0, description="Planet radius in Earth radii")
    planet_temp_k: float = Field(288.0, description="Equilibrium temperature in Kelvin")
    stellar_uv_flux: float = Field(1.0, description="UV flux relative to Sun")
    planet_age_gyr: float = Field(4.5, description="Planet age in billion years")


# ============================================================================
# Candidate Models
# ============================================================================

class CandidateFlags(BaseModel):
    """Flags from classifier and RL policy."""
    is_planet: bool
    triage: Literal["accept", "reject", "human_review"]
    confidence: float


class CandidatePlotUrls(BaseModel):
    """URLs/paths to diagnostic plots."""
    phase_fold: str
    bls_power: str
    odd_even: str
    secondary: str
    residuals: str


class Candidate(BaseModel):
    """Exoplanet candidate with all properties."""
    candidate_id: str
    period: float
    t0: float
    depth: float
    duration: float
    snr: float
    flags: CandidateFlags
    plots: Optional[CandidatePlotUrls] = None
    fit: Optional[TransitFit] = None
    physics: Optional[PhysicsChecks] = None
    biosignature: Optional[BiosignatureResult] = None  # NEW!


# ============================================================================
# Job Management Models
# ============================================================================

class JobStatus(BaseModel):
    """Status of a detection job."""
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    progress_pct: Optional[float] = None
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class RunParams(BaseModel):
    """Parameters for detection run."""
    dataset_id: str
    min_period: float = Field(default=1.0, ge=0.1, description="Minimum period in days")
    max_period: float = Field(default=20.0, le=100.0, description="Maximum period in days")
    min_snr: float = Field(default=7.0, ge=3.0, description="Minimum SNR threshold")
    max_candidates: int = Field(default=10, ge=1, le=50, description="Max candidates to return")


# ============================================================================
# Dataset Models
# ============================================================================

class Dataset(BaseModel):
    """Available dataset for analysis."""
    dataset_id: str
    name: str
    source: Literal["demo", "upload", "nasa_kepler", "nasa_tess", "nasa_k2"]
    num_points: Optional[int] = None
    time_span_days: Optional[float] = None


class UploadResponse(BaseModel):
    """Response after uploading dataset."""
    dataset_id: str
    filename: str
    message: str


# ============================================================================
# Comparison Models
# ============================================================================

class CompareRequest(BaseModel):
    """Request to compare candidates against baseline."""
    candidate_ids: List[str]
    baseline_id: str


class CompareResult(BaseModel):
    """Result of candidate comparison."""
    candidate_id: str
    baseline_id: str
    period_match: bool
    depth_match: bool
    similarity_score: float
    notes: str


# ============================================================================
# NASA Data Fetch Models
# ============================================================================

class FetchLightCurveRequest(BaseModel):
    """Request to fetch light curve from NASA archives."""
    mission: Literal["Kepler", "K2", "TESS"]
    target_id: str = Field(..., description="KIC ID for Kepler, EPIC for K2, TIC for TESS")
    quarter: Optional[int] = Field(None, description="Specific quarter/sector (optional)")
    save_as_dataset: bool = Field(True, description="Save to datasets for later use")


class ConfirmedPlanet(BaseModel):
    """Information about a confirmed exoplanet."""
    name: str
    host_star: str
    period_days: float
    radius_earth: float
    discovery_method: str
    discovery_year: int


# ============================================================================
# Missing Legacy Schemas (for compatibility)
# ============================================================================

class ResultsResponse(BaseModel):
    """Response with detection results."""
    candidates: List[Candidate]
    job_id: str
    message: str


class DatasetInfo(BaseModel):
    """Legacy name for Dataset."""
    dataset_id: str
    name: str
    source: Literal["demo", "upload", "nasa_kepler", "nasa_tess", "nasa_k2"]
    num_points: Optional[int] = None
    time_span_days: Optional[float] = None


class RunResponse(BaseModel):
    """Legacy name for JobStatus response."""
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    message: Optional[str] = None


class ComparisonRequest(BaseModel):
    """Request to compare methods - legacy name for CompareRequest."""
    candidate_ids: List[str]
    baseline_id: str


class MethodMetrics(BaseModel):
    """Metrics for a detection method."""
    method_name: str
    precision: float
    recall: float
    f1_score: float
    runtime_seconds: float


class ComparisonResponse(BaseModel):
    """Response for comparison - legacy name for CompareResult."""
    candidate_id: str
    baseline_id: str
    period_match: bool
    depth_match: bool
    similarity_score: float
    notes: str
    baseline: Optional[MethodMetrics] = None
    resonant: Optional[MethodMetrics] = None
    improvement_factor: Optional[float] = None