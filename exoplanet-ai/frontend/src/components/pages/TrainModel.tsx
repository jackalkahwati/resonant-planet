import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Play, Settings, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';
import { trainModel, TrainConfig } from '@/lib/api';
import { formatPercent, formatNumber } from '@/lib/utils';

interface TrainingResult {
  accuracy: number;
  f1_macro: number;
  roc_auc: number | null;
  training_time_seconds: number;
  individual_models: Record<string, { accuracy: number; f1_macro: number }>;
}

export const TrainModel: React.FC = () => {
  const [config, setConfig] = useState<TrainConfig>({
    dataset: 'kepler',
    test_size: 0.2,
    balance_method: 'smote',
  });
  const [isTraining, setIsTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'idle' | 'training' | 'success' | 'error'>('idle');
  const [result, setResult] = useState<TrainingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrain = async () => {
    setIsTraining(true);
    setStatus('training');
    setProgress(0);
    setError(null);

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + Math.random() * 15, 90));
    }, 1000);

    try {
      const response = await trainModel(config);
      clearInterval(progressInterval);
      setProgress(100);
      setResult(response.metrics);
      setStatus('success');
    } catch (err) {
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : 'Training failed');
      setStatus('error');
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-3xl font-bold gradient-text mb-2">Train AI Model</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Train the ensemble model on NASA exoplanet datasets. The model combines XGBoost, LightGBM, 
          CatBoost, Random Forest, and a Neural Network with attention mechanism.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-purple-400" />
                Training Configuration
              </CardTitle>
              <CardDescription>Configure the training parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Dataset Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Dataset</label>
                <div className="grid grid-cols-2 gap-3">
                  {['kepler', 'tess'].map((dataset) => (
                    <button
                      key={dataset}
                      onClick={() => setConfig({ ...config, dataset: dataset as 'kepler' | 'tess' })}
                      disabled={isTraining}
                      className={`p-4 rounded-lg border transition-all ${
                        config.dataset === dataset
                          ? 'bg-purple-500/20 border-purple-500 text-white'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:border-purple-500/50'
                      } ${isTraining ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <div className="font-medium">{dataset.toUpperCase()}</div>
                      <div className="text-xs mt-1 opacity-70">
                        {dataset === 'kepler' ? 'Kepler Mission KOI' : 'TESS TOI Catalog'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Test Size */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Test Split: {(config.test_size * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="10"
                  max="40"
                  value={config.test_size * 100}
                  onChange={(e) => setConfig({ ...config, test_size: parseInt(e.target.value) / 100 })}
                  disabled={isTraining}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>10%</span>
                  <span>40%</span>
                </div>
              </div>

              {/* Balance Method */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Data Balancing</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'smote', label: 'SMOTE', desc: 'Synthetic oversampling' },
                    { value: 'undersample', label: 'Undersample', desc: 'Random undersampling' },
                    { value: 'combined', label: 'Combined', desc: 'SMOTE + Undersample' },
                    { value: 'none', label: 'None', desc: 'No balancing' },
                  ].map((method) => (
                    <button
                      key={method.value}
                      onClick={() => setConfig({ ...config, balance_method: method.value as TrainConfig['balance_method'] })}
                      disabled={isTraining}
                      className={`p-3 rounded-lg border text-left transition-all ${
                        config.balance_method === method.value
                          ? 'bg-purple-500/20 border-purple-500 text-white'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:border-purple-500/50'
                      } ${isTraining ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <div className="text-sm font-medium">{method.label}</div>
                      <div className="text-xs opacity-70">{method.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Train Button */}
              <Button
                onClick={handleTrain}
                disabled={isTraining}
                isLoading={isTraining}
                size="lg"
                className="w-full"
              >
                {isTraining ? (
                  <>Training Model...</>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Start Training
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Training Progress & Results */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-cyan-400" />
                Training Status
              </CardTitle>
              <CardDescription>Monitor training progress and results</CardDescription>
            </CardHeader>
            <CardContent>
              {status === 'idle' && (
                <div className="text-center py-12 text-gray-400">
                  <Brain className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>Configure settings and click "Start Training" to begin</p>
                </div>
              )}

              {status === 'training' && (
                <div className="space-y-6">
                  <div className="text-center">
                    <Loader2 className="w-16 h-16 mx-auto mb-4 text-purple-400 animate-spin" />
                    <p className="text-lg font-medium text-white">Training in Progress</p>
                    <p className="text-sm text-gray-400 mt-1">This may take a few minutes...</p>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Progress</span>
                      <span className="text-white">{progress.toFixed(0)}%</span>
                    </div>
                    <Progress value={progress} />
                  </div>
                  <div className="bg-white/5 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">Training Steps:</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2">
                        <CheckCircle className={`w-4 h-4 ${progress > 10 ? 'text-green-400' : 'text-gray-500'}`} />
                        <span className={progress > 10 ? 'text-white' : 'text-gray-500'}>Fetching data from NASA Archive</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className={`w-4 h-4 ${progress > 25 ? 'text-green-400' : 'text-gray-500'}`} />
                        <span className={progress > 25 ? 'text-white' : 'text-gray-500'}>Preprocessing & feature engineering</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className={`w-4 h-4 ${progress > 50 ? 'text-green-400' : 'text-gray-500'}`} />
                        <span className={progress > 50 ? 'text-white' : 'text-gray-500'}>Training ensemble models</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className={`w-4 h-4 ${progress > 80 ? 'text-green-400' : 'text-gray-500'}`} />
                        <span className={progress > 80 ? 'text-white' : 'text-gray-500'}>Evaluating performance</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {status === 'success' && result && (
                <div className="space-y-6">
                  <div className="text-center">
                    <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
                    <p className="text-lg font-medium text-white">Training Complete!</p>
                    <p className="text-sm text-gray-400 mt-1">
                      Completed in {formatNumber(result.training_time_seconds, 1)}s
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-green-400">{formatPercent(result.accuracy)}</p>
                      <p className="text-xs text-gray-400 mt-1">Accuracy</p>
                    </div>
                    <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-cyan-400">{formatPercent(result.f1_macro)}</p>
                      <p className="text-xs text-gray-400 mt-1">F1 Score</p>
                    </div>
                    <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-purple-400">
                        {result.roc_auc ? formatNumber(result.roc_auc, 3) : 'N/A'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">ROC AUC</p>
                    </div>
                  </div>

                  {result.individual_models && (
                    <div className="bg-white/5 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-300 mb-3">Model Performance:</h4>
                      <div className="space-y-2">
                        {Object.entries(result.individual_models).map(([name, data]) => (
                          <div key={name} className="flex items-center justify-between">
                            <span className="text-sm text-gray-400 uppercase">{name}</span>
                            <span className="text-sm text-white">{formatPercent(data.accuracy)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {status === 'error' && (
                <div className="text-center py-8">
                  <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
                  <p className="text-lg font-medium text-white">Training Failed</p>
                  <p className="text-sm text-red-400 mt-2">{error}</p>
                  <Button onClick={handleTrain} className="mt-4">
                    Retry Training
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Model Architecture Info */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card>
          <CardHeader>
            <CardTitle>Ensemble Architecture</CardTitle>
            <CardDescription>The model combines multiple state-of-the-art algorithms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {[
                { name: 'XGBoost', weight: '25%', desc: 'Gradient boosting with regularization' },
                { name: 'LightGBM', weight: '25%', desc: 'Fast gradient boosting framework' },
                { name: 'CatBoost', weight: '20%', desc: 'Gradient boosting with categorical support' },
                { name: 'Random Forest', weight: '15%', desc: 'Bagging ensemble of decision trees' },
                { name: 'Neural Net', weight: '15%', desc: 'Deep network with attention mechanism' },
              ].map((model) => (
                <div key={model.name} className="bg-white/5 rounded-lg p-4 text-center">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 mx-auto mb-3 flex items-center justify-center">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="font-medium text-white">{model.name}</h4>
                  <p className="text-xs text-purple-300 mt-1">Weight: {model.weight}</p>
                  <p className="text-xs text-gray-400 mt-2">{model.desc}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
