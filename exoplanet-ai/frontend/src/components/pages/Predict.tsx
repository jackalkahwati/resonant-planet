import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Rocket, Sparkles, AlertCircle, Info, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { predict, getModelStatus, PredictionResult } from '@/lib/api';
import { formatNumber, formatPercent, getClassColor, getClassBgColor, formatFeatureName } from '@/lib/utils';

const FEATURE_DEFAULTS: Record<string, { min: number; max: number; default: number; step: number }> = {
  koi_period: { min: 0.1, max: 1000, default: 10, step: 0.1 },
  koi_duration: { min: 0.1, max: 50, default: 5, step: 0.1 },
  koi_depth: { min: 0, max: 50000, default: 500, step: 10 },
  koi_prad: { min: 0.1, max: 50, default: 2, step: 0.1 },
  koi_teq: { min: 100, max: 3000, default: 300, step: 10 },
  koi_insol: { min: 0.01, max: 10000, default: 1, step: 0.1 },
  koi_model_snr: { min: 0, max: 1000, default: 50, step: 1 },
  koi_steff: { min: 2500, max: 10000, default: 5500, step: 50 },
  koi_srad: { min: 0.1, max: 20, default: 1, step: 0.1 },
  koi_smass: { min: 0.1, max: 5, default: 1, step: 0.1 },
  koi_impact: { min: 0, max: 1.5, default: 0.5, step: 0.05 },
  koi_slogg: { min: 2, max: 6, default: 4.4, step: 0.1 },
};

export const Predict: React.FC = () => {
  const [features, setFeatures] = useState<Record<string, number>>({});
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelTrained, setModelTrained] = useState(false);

  useEffect(() => {
    const checkModel = async () => {
      try {
        const status = await getModelStatus();
        setModelTrained(status.is_trained);
        if (status.feature_names?.length) {
          setAvailableFeatures(status.feature_names);
          const defaultFeatures: Record<string, number> = {};
          status.feature_names.forEach((f) => {
            defaultFeatures[f] = FEATURE_DEFAULTS[f]?.default || 0;
          });
          setFeatures(defaultFeatures);
        }
      } catch (err) {
        console.error('Error checking model status:', err);
      }
    };
    checkModel();
  }, []);

  const handlePredict = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await predict(features);
      setPrediction(result.prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
    } finally {
      setIsLoading(false);
    }
  };

  const updateFeature = (name: string, value: number) => {
    setFeatures((prev) => ({ ...prev, [name]: value }));
  };

  // Preset configurations
  const presets: Array<{ name: string; description: string; values: Record<string, number> }> = [
    {
      name: 'Earth-like',
      description: 'Similar to Earth parameters',
      values: { koi_period: 365, koi_prad: 1, koi_teq: 288, koi_insol: 1, koi_steff: 5778, koi_depth: 100 }
    },
    {
      name: 'Hot Jupiter',
      description: 'Large planet, close orbit',
      values: { koi_period: 3, koi_prad: 11, koi_teq: 1500, koi_insol: 1000, koi_depth: 10000, koi_steff: 6000 }
    },
    {
      name: 'Super Earth',
      description: 'Larger rocky planet',
      values: { koi_period: 50, koi_prad: 2.5, koi_teq: 400, koi_insol: 2, koi_steff: 5000, koi_depth: 300 }
    },
  ];

  const applyPreset = (preset: { name: string; description: string; values: Record<string, number> }) => {
    setFeatures((prev) => ({ ...prev, ...preset.values }));
  };

  if (!modelTrained) {
    return (
      <div className="flex items-center justify-center h-96">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-yellow-400" />
            <h3 className="text-xl font-bold text-white mb-2">Model Not Trained</h3>
            <p className="text-gray-400 mb-4">
              Please train the model first before making predictions.
            </p>
            <Button variant="cyan">Go to Training</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-2">Predict Exoplanet</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Enter transit and stellar parameters to classify a potential exoplanet candidate
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Feature Input */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Input Features</CardTitle>
              <CardDescription>Adjust the parameters or use a preset</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Presets */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">Quick Presets</label>
                <div className="flex gap-2 flex-wrap">
                  {presets.map((preset) => (
                    <button
                      key={preset.name}
                      onClick={() => applyPreset(preset)}
                      className="px-3 py-2 bg-white/5 hover:bg-purple-500/20 border border-white/10 hover:border-purple-500/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all"
                    >
                      {preset.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Feature Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableFeatures.slice(0, 12).map((feature) => {
                  const config = FEATURE_DEFAULTS[feature] || { min: 0, max: 1000, default: 0, step: 1 };
                  return (
                    <div key={feature} className="bg-white/5 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <label className="text-sm font-medium text-gray-300">
                          {formatFeatureName(feature)}
                        </label>
                        <span className="text-sm text-purple-300">{formatNumber(features[feature] || 0)}</span>
                      </div>
                      <input
                        type="range"
                        min={config.min}
                        max={config.max}
                        step={config.step}
                        value={features[feature] || config.default}
                        onChange={(e) => updateFeature(feature, parseFloat(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>{config.min}</span>
                        <span>{config.max}</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Predict Button */}
              <div className="mt-6">
                <Button onClick={handlePredict} isLoading={isLoading} size="lg" className="w-full">
                  <Rocket className="w-5 h-5 mr-2" />
                  Classify Exoplanet
                </Button>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                  {error}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Prediction Result */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <Card glow={prediction ? (prediction.predicted_class === 2 ? 'green' : prediction.predicted_class === 1 ? 'purple' : undefined) : undefined}>
            <CardHeader>
              <CardTitle>Prediction Result</CardTitle>
              <CardDescription>AI classification with confidence</CardDescription>
            </CardHeader>
            <CardContent>
              {!prediction ? (
                <div className="text-center py-12 text-gray-400">
                  <Sparkles className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>Enter features and click "Classify" to see the prediction</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Main Prediction */}
                  <div className={`p-6 rounded-xl border ${getClassBgColor(prediction.predicted_class_name)}`}>
                    <div className="text-center">
                      <p className={`text-3xl font-bold ${getClassColor(prediction.predicted_class_name)}`}>
                        {prediction.predicted_class_name}
                      </p>
                      <p className="text-gray-400 mt-2">
                        Confidence: <span className="text-white font-medium">{formatPercent(prediction.confidence)}</span>
                      </p>
                    </div>
                  </div>

                  {/* Class Probabilities */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-3">Class Probabilities</h4>
                    <div className="space-y-3">
                      {Object.entries(prediction.class_probabilities).map(([className, prob]) => (
                        <div key={className}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className={getClassColor(className)}>{className}</span>
                            <span className="text-white">{formatPercent(prob)}</span>
                          </div>
                          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all duration-500 ${
                                className.toLowerCase().includes('confirmed') ? 'bg-green-500' :
                                className.toLowerCase().includes('candidate') ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${prob * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Model Breakdown */}
                  {prediction.model_breakdown && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-3">Model Consensus</h4>
                      <div className="space-y-2">
                        {Object.entries(prediction.model_breakdown).map(([model, data]) => (
                          <div key={model} className="flex items-center justify-between text-sm bg-white/5 rounded-lg px-3 py-2">
                            <span className="text-gray-400 uppercase">{model}</span>
                            <span className={getClassColor(data.predicted_class)}>
                              {data.predicted_class}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Top Features */}
                  {prediction.top_features && prediction.top_features.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-3">Key Factors</h4>
                      <div className="space-y-2">
                        {prediction.top_features.slice(0, 5).map((feat, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm">
                            <ArrowRight className={`w-4 h-4 ${feat.direction === 'positive' ? 'text-green-400' : 'text-red-400'}`} />
                            <span className="text-gray-300">{formatFeatureName(feat.feature)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Info Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card>
          <CardContent className="py-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-gray-400">
                <strong className="text-gray-300">How it works:</strong> The ensemble model analyzes transit properties 
                (orbital period, depth, duration) and stellar characteristics (temperature, radius, mass) to classify 
                the observation as a confirmed exoplanet, candidate, or false positive. Each prediction includes 
                confidence scores and model consensus.
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
