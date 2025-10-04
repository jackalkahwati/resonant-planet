/**
 * React hook for managing datasets from backend
 */
import { useState, useEffect } from "react";
import api, { type DatasetInfo } from "@/lib/api";

export interface UseDatasetsResult {
  datasets: DatasetInfo[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  uploadFile: (file: File) => Promise<string>;
}

export function useDatasets(): UseDatasetsResult {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDatasets = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await api.listDatasets();
      setDatasets(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load datasets";
      setError(message);
      console.error("Failed to fetch datasets:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadFile = async (file: File): Promise<string> => {
    try {
      const response = await api.uploadDataset(file);
      // Refresh datasets after upload
      await fetchDatasets();
      return response.dataset_id;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to upload file";
      throw new Error(message);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  return {
    datasets,
    isLoading,
    error,
    refetch: fetchDatasets,
    uploadFile,
  };
}

export default useDatasets;
