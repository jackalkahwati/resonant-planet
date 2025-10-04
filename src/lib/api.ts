/**
 * API client for Resonant Worlds Explorer backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ============================================================================
// Types (matching backend schemas)
// ============================================================================

export interface DatasetInfo {
  dataset_id: string;
  name: string;
  description: string;
  source: "kepler" | "k2" | "tess" | "upload" | "demo";
  num_points?: number;
  time_span_days?: number;
}

export interface RunParams {
  dataset_id?: string;
  upload_ref?: string;
  min_period_days?: number;
  max_period_days?: number;
  min_snr?: number;
  max_candidates?: number;
}

export interface JobStatus {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  progress: number;
  stage?: string;
  message?: string;
}

export interface CandidateFlags {
  odd_even_ok: boolean;
  secondary_low: boolean;
  shape_u_like: boolean;
  density_consistent: boolean;
}

export interface PlotUrls {
  phase_fold_png: string;
  bls_png: string;
  oddeven_png: string;
  secondary_png?: string;
}

export interface Candidate {
  candidate_id: string;
  probability: number;
  period_days: number;
  t0_bjd: number;
  depth_ppm: number;
  duration_hours: number;
  snr: number;
  flags: CandidateFlags;
  plots: PlotUrls;
  rl_action: "accept" | "reject" | "human_review";
}

export interface ResultsResponse {
  job_id: string;
  candidates: Candidate[];
  total_candidates: number;
  accepted_count: number;
  rejected_count: number;
  human_review_count: number;
}

export interface MethodMetrics {
  method: "baseline" | "resonant";
  detection_probability: number;
  snr: number;
  false_alarm_rate: number;
  compute_time_seconds: number;
}

export interface ComparisonResponse {
  candidate_id: string;
  baseline: MethodMetrics;
  resonant: MethodMetrics;
  improvement_factor: number;
}

// ============================================================================
// API Client
// ============================================================================

class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    let details;
    try {
      details = JSON.parse(text);
    } catch {
      details = text;
    }
    throw new APIError(response.status, `API error: ${response.statusText}`, details);
  }

  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return response.json();
  }

  return response as any;
}

export const api = {
  /**
   * Check backend health
   */
  async health(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  },

  /**
   * Get backend info
   */
  async getInfo(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/`);
    return handleResponse(response);
  },

  // ========== Datasets ==========

  /**
   * List available datasets
   */
  async listDatasets(): Promise<DatasetInfo[]> {
    const response = await fetch(`${API_BASE_URL}/api/datasets/`);
    return handleResponse(response);
  },

  /**
   * Upload a light curve CSV file
   */
  async uploadDataset(file: File): Promise<{ dataset_id: string; message: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/datasets/upload`, {
      method: "POST",
      body: formData,
    });
    return handleResponse(response);
  },

  /**
   * Get dataset info
   */
  async getDataset(datasetId: string): Promise<DatasetInfo> {
    const response = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}`);
    return handleResponse(response);
  },

  // ========== Detection ==========

  /**
   * Start a detection run
   */
  async startRun(params: RunParams): Promise<{ job_id: string; status: string }> {
    const response = await fetch(`${API_BASE_URL}/api/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return handleResponse(response);
  },

  /**
   * Get job status
   */
  async getStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
    return handleResponse(response);
  },

  /**
   * Poll job status until completion
   */
  async pollStatus(
    jobId: string,
    onProgress?: (status: JobStatus) => void,
    interval: number = 1000,
    timeout: number = 300000 // 5 minutes
  ): Promise<JobStatus> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const status = await this.getStatus(jobId);

      if (onProgress) {
        onProgress(status);
      }

      if (status.status === "completed" || status.status === "failed") {
        return status;
      }

      await new Promise((resolve) => setTimeout(resolve, interval));
    }

    throw new Error("Job polling timed out");
  },

  /**
   * Get detection results
   */
  async getResults(jobId: string): Promise<ResultsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/results/${jobId}`);
    return handleResponse(response);
  },

  // ========== Reports ==========

  /**
   * Download PDF report
   */
  async downloadReport(jobId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/report/${jobId}`);

    if (!response.ok) {
      throw new APIError(response.status, `Failed to download report: ${response.statusText}`);
    }

    return response.blob();
  },

  /**
   * Download report as file
   */
  async downloadReportAsFile(jobId: string, filename?: string): Promise<void> {
    const blob = await this.downloadReport(jobId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || `resonant_report_${jobId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  // ========== Comparison ==========

  /**
   * Compare methods for candidates
   */
  async compareMethod(candidateIds: string[]): Promise<ComparisonResponse[]> {
    const response = await fetch(`${API_BASE_URL}/api/compare/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_ids: candidateIds }),
    });
    return handleResponse(response);
  },

  /**
   * Get plot URL
   */
  getPlotUrl(plotPath: string): string {
    if (plotPath.startsWith("http")) {
      return plotPath;
    }
    return `${API_BASE_URL}${plotPath}`;
  },
};

// ============================================================================
// Utility functions
// ============================================================================

/**
 * Format candidate for display (convert from backend to frontend format)
 */
export function formatCandidate(backendCandidate: Candidate) {
  return {
    id: backendCandidate.candidate_id,
    name: backendCandidate.candidate_id,
    mission: "Kepler", // Could be extracted from dataset info
    probability: backendCandidate.probability,
    period: backendCandidate.period_days,
    depth: backendCandidate.depth_ppm / 1e6, // Convert ppm to fractional
    duration: backendCandidate.duration_hours,
    snr: backendCandidate.snr,
    validations: {
      oddEven: backendCandidate.flags.odd_even_ok,
      secondary: backendCandidate.flags.secondary_low,
      shape: backendCandidate.flags.shape_u_like,
      centroid: backendCandidate.flags.density_consistent,
    },
    baselineProbability: 0.7, // Placeholder - would come from comparison API
    baselineFlags: [] as string[],
    description: `Detected by Resonant Worlds Explorer (${backendCandidate.rl_action})`,
    isConfirmed: backendCandidate.rl_action === "accept",
    isFalsePositive: backendCandidate.rl_action === "reject",
    plots: backendCandidate.plots,
  };
}

/**
 * Check if backend is available
 */
export async function checkBackend(): Promise<boolean> {
  try {
    await api.health();
    return true;
  } catch {
    return false;
  }
}

export default api;
