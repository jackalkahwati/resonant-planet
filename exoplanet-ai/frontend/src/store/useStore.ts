import { create } from 'zustand';
import { ModelStatus, ModelMetrics, PredictionResult, Exoplanet, FeatureInfo } from '@/lib/api';

interface AppState {
  // Model state
  modelStatus: ModelStatus | null;
  isTraining: boolean;
  metrics: ModelMetrics | null;
  featureImportance: FeatureInfo[];
  
  // Prediction state
  currentPrediction: PredictionResult | null;
  predictionHistory: PredictionResult[];
  
  // Data state
  confirmedExoplanets: Exoplanet[];
  selectedExoplanet: Exoplanet | null;
  
  // UI state
  activeTab: string;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setModelStatus: (status: ModelStatus) => void;
  setIsTraining: (isTraining: boolean) => void;
  setMetrics: (metrics: ModelMetrics) => void;
  setFeatureImportance: (features: FeatureInfo[]) => void;
  setCurrentPrediction: (prediction: PredictionResult | null) => void;
  addPrediction: (prediction: PredictionResult) => void;
  setConfirmedExoplanets: (exoplanets: Exoplanet[]) => void;
  setSelectedExoplanet: (exoplanet: Exoplanet | null) => void;
  setActiveTab: (tab: string) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  modelStatus: null,
  isTraining: false,
  metrics: null,
  featureImportance: [],
  currentPrediction: null,
  predictionHistory: [],
  confirmedExoplanets: [],
  selectedExoplanet: null,
  activeTab: 'dashboard',
  isLoading: false,
  error: null,
};

export const useStore = create<AppState>((set) => ({
  ...initialState,
  
  setModelStatus: (status) => set({ modelStatus: status }),
  setIsTraining: (isTraining) => set({ isTraining }),
  setMetrics: (metrics) => set({ metrics }),
  setFeatureImportance: (features) => set({ featureImportance: features }),
  setCurrentPrediction: (prediction) => set({ currentPrediction: prediction }),
  addPrediction: (prediction) => set((state) => ({
    predictionHistory: [prediction, ...state.predictionHistory.slice(0, 49)],
  })),
  setConfirmedExoplanets: (exoplanets) => set({ confirmedExoplanets: exoplanets }),
  setSelectedExoplanet: (exoplanet) => set({ selectedExoplanet: exoplanet }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
