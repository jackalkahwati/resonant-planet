import axios from 'axios';

const API_BASE = '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface ModelStatus {
  is_trained: boolean;
  dataset_type: string | null;
  training_time: number | null;
  metrics: ModelMetrics;
  feature_names: string[];
}

export interface ModelMetrics {
  accuracy: number;
  precision_macro: number;
  recall_macro: number;
  f1_macro: number;
  roc_auc: number | null;
  confusion_matrix: number[][];
  precision_per_class: number[];
  recall_per_class: number[];
  f1_per_class: number[];
  feature_importance: Record<string, number>;
  individual_models: Record<string, { accuracy: number; f1_macro: number }>;
}

export interface PredictionResult {
  predicted_class: number;
  predicted_class_name: string;
  confidence: number;
  class_probabilities: Record<string, number>;
  top_features?: FeatureContribution[];
  model_breakdown?: Record<string, ModelPrediction>;
}

export interface FeatureContribution {
  feature: string;
  shap_value?: number;
  importance?: number;
  feature_value: number;
  direction: string;
}

export interface ModelPrediction {
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface TrainConfig {
  dataset: 'kepler' | 'tess';
  test_size: number;
  balance_method: 'smote' | 'undersample' | 'combined' | 'none';
}

export interface Exoplanet {
  name: string;
  orbital_period_days: number;
  radius_earth: number;
  equilibrium_temp_k: number;
  insolation_flux: number;
  star_temp_k: number;
  potentially_habitable: boolean;
}

export interface DataStatistics {
  dataset: string;
  total_records: number;
  class_distribution: Record<string, number>;
  numeric_columns: number;
  statistics: Record<string, Record<string, number>>;
}

export interface FeatureInfo {
  name: string;
  display_name: string;
  importance: number;
}

// API Functions
export const getModelStatus = async (): Promise<ModelStatus> => {
  const response = await api.get('/model/status');
  return response.data;
};

export const trainModel = async (config: TrainConfig) => {
  const response = await api.post('/model/train', config);
  return response.data;
};

export const predict = async (features: Record<string, number>): Promise<{ prediction: PredictionResult }> => {
  const response = await api.post('/predict', { features });
  return response.data;
};

export const predictBatch = async (data: Record<string, number>[]) => {
  const response = await api.post('/predict/batch', { data });
  return response.data;
};

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/predict/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getMetrics = async (): Promise<{ metrics: ModelMetrics }> => {
  const response = await api.get('/model/metrics');
  return response.data;
};

export const getFeatureImportance = async (): Promise<{ features: FeatureInfo[] }> => {
  const response = await api.get('/model/features');
  return response.data;
};

export const getSampleData = async (dataset: string = 'kepler', n_samples: number = 10) => {
  const response = await api.get(`/data/sample?dataset=${dataset}&n_samples=${n_samples}`);
  return response.data;
};

export const getDataStatistics = async (dataset: string = 'kepler'): Promise<DataStatistics> => {
  const response = await api.get(`/data/statistics?dataset=${dataset}`);
  return response.data;
};

export const getConfirmedExoplanets = async (limit: number = 50): Promise<{ exoplanets: Exoplanet[] }> => {
  const response = await api.get(`/exoplanets/confirmed?limit=${limit}`);
  return response.data;
};

// Confirmed planets from Planetary Systems TAP table
export interface ConfirmedPlanet {
  name: string;
  host_star: string;
  discovery_method: string;
  discovery_year: number;
  discovery_facility: string;
  orbital_period_days: number;
  radius_earth: number;
  mass_earth: number;
  semi_major_axis_au: number;
  eccentricity: number;
  equilibrium_temp_k: number;
  insolation_flux: number;
  star_temp_k: number;
  star_radius_solar: number;
  star_mass_solar: number;
  distance_pc: number;
  ra: number;
  dec: number;
  potentially_habitable: boolean;
  num_planets_in_system: number;
}

export interface PlanetStatistics {
  total_planets: number;
  discovery_methods: Record<string, number>;
  discoveries_by_year: Record<string, number>;
  discovery_facilities: Record<string, number>;
  orbital_period_stats: { min: number; max: number; mean: number; median: number };
  radius_stats: { min: number; max: number; mean: number; median: number };
  mass_stats: { min: number; max: number; mean: number; median: number };
  temperature_stats: { min: number; max: number; mean: number; median: number };
  potentially_habitable: number;
}

export const getConfirmedPlanets = async (limit: number = 100, discoveryMethod?: string): Promise<{
  total_confirmed: number;
  returned: number;
  discovery_methods: Record<string, number>;
  planets: ConfirmedPlanet[];
}> => {
  let url = `/planets/confirmed?limit=${limit}`;
  if (discoveryMethod) {
    url += `&discovery_method=${discoveryMethod}`;
  }
  const response = await api.get(url);
  return response.data;
};

export const getPlanetStatistics = async (): Promise<{ statistics: PlanetStatistics }> => {
  const response = await api.get('/planets/statistics');
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};
