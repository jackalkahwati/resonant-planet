/**
 * React hook for running detection jobs with the backend
 */
import { useState, useCallback } from "react";
import api, { formatCandidate, type RunParams, type JobStatus } from "@/lib/api";
import { toast } from "sonner";
import type { Candidate } from "@/data/sampleCandidates";

export interface UseDetectionResult {
  isProcessing: boolean;
  progress: number;
  stage: string;
  results: Candidate[];
  jobId: string | null;
  error: string | null;
  runDetection: (params: RunParams) => Promise<void>;
  reset: () => void;
}

export function useDetection(): UseDetectionResult {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [results, setResults] = useState<Candidate[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runDetection = useCallback(async (params: RunParams) => {
    try {
      setIsProcessing(true);
      setProgress(0);
      setStage("Starting...");
      setError(null);
      setResults([]);

      toast.info("Starting detection on backend...");

      // Start job
      const { job_id } = await api.startRun(params);
      setJobId(job_id);

      toast.success(`Job started: ${job_id.substring(0, 8)}...`);

      // Poll for completion
      const finalStatus = await api.pollStatus(
        job_id,
        (status: JobStatus) => {
          setProgress(status.progress);
          setStage(status.stage || "Processing");

          // Show toast on stage changes
          if (status.stage && status.stage !== stage) {
            toast.info(`${status.stage}: ${status.message || ""}`);
          }
        },
        1000, // Poll every second
        300000 // 5 minute timeout
      );

      // Handle completion
      if (finalStatus.status === "completed") {
        // Fetch results
        const resultsData = await api.getResults(job_id);

        // Convert backend candidates to frontend format
        const formattedCandidates = resultsData.candidates.map(formatCandidate);

        setResults(formattedCandidates);
        setProgress(100);
        setStage("Complete");

        toast.success(
          `Analysis complete! Found ${resultsData.total_candidates} candidates ` +
            `(${resultsData.accepted_count} accepted, ${resultsData.rejected_count} rejected, ` +
            `${resultsData.human_review_count} need review).`
        );
      } else if (finalStatus.status === "failed") {
        throw new Error(finalStatus.message || "Job failed");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Detection failed";
      setError(message);
      toast.error(`Detection failed: ${message}`);
      console.error("Detection error:", err);
    } finally {
      setIsProcessing(false);
    }
  }, [stage]);

  const reset = useCallback(() => {
    setIsProcessing(false);
    setProgress(0);
    setStage("");
    setResults([]);
    setJobId(null);
    setError(null);
  }, []);

  return {
    isProcessing,
    progress,
    stage,
    results,
    jobId,
    error,
    runDetection,
    reset,
  };
}

export default useDetection;
