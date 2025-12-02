import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, Check, HelpCircle, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { getModelStatus, getDataStatistics, ModelStatus, DataStatistics } from '@/lib/api';
import { formatPercent, formatNumber } from '@/lib/utils';

const COLORS = ['#ef4444', '#eab308', '#22c55e'];

// Default data to show immediately - no loading state
const DEFAULT_CLASS_DIST = {
  'FALSE POSITIVE': 4567,
  'CANDIDATE': 2341,
  'CONFIRMED': 2656
};

export const Dashboard: React.FC = () => {
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [dataStats, setDataStats] = useState<DataStatistics | null>({
    status: 'success',
    dataset: 'kepler',
    total_records: 9564,
    class_distribution: DEFAULT_CLASS_DIST,
    numeric_columns: 0,
    statistics: {}
  });

  // Fetch real data silently in background
  useEffect(() => {
    const fetchData = async () => {
      try {
        const status = await getModelStatus();
        setModelStatus(status);
      } catch (error) {
        console.error('Error fetching model status:', error);
      }
      
      try {
        const stats = await getDataStatistics('kepler');
        if (stats?.class_distribution) {
          setDataStats(stats);
        }
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    };
    fetchData();
  }, []);

  const classDistData = dataStats ? Object.entries(dataStats.class_distribution).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
    color: name.includes('FALSE') ? COLORS[0] : name.includes('CANDIDATE') ? COLORS[1] : COLORS[2]
  })) : [];

  const metricsData = modelStatus?.metrics ? [
    { metric: 'Accuracy', value: modelStatus.metrics.accuracy * 100 },
    { metric: 'Precision', value: modelStatus.metrics.precision_macro * 100 },
    { metric: 'Recall', value: modelStatus.metrics.recall_macro * 100 },
    { metric: 'F1 Score', value: modelStatus.metrics.f1_macro * 100 },
  ] : [
    { metric: 'Accuracy', value: 0 },
    { metric: 'Precision', value: 0 },
    { metric: 'Recall', value: 0 },
    { metric: 'F1 Score', value: 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card glow="purple">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Model Status</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {modelStatus?.is_trained ? 'Trained' : 'Not Trained'}
                  </p>
                </div>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${modelStatus?.is_trained ? 'bg-green-500/20' : 'bg-yellow-500/20'}`}>
                  {modelStatus?.is_trained ? (
                    <Check className="w-6 h-6 text-green-400" />
                  ) : (
                    <HelpCircle className="w-6 h-6 text-yellow-400" />
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card glow="cyan">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Records</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {dataStats?.total_records?.toLocaleString() || '0'}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-cyan-500/20 flex items-center justify-center">
                  <Activity className="w-6 h-6 text-cyan-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card glow="green">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Accuracy</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {modelStatus?.metrics?.accuracy ? formatPercent(modelStatus.metrics.accuracy) : 'N/A'}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Target className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">ROC AUC</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {modelStatus?.metrics?.roc_auc ? formatNumber(modelStatus.metrics.roc_auc, 3) : 'N/A'}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Class Distribution */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader>
              <CardTitle>Class Distribution</CardTitle>
              <CardDescription>Distribution of exoplanet classifications in dataset</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={classDistData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {classDistData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px' }}
                      labelStyle={{ color: '#fff' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-sm text-gray-400">False Positive</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <span className="text-sm text-gray-400">Candidate</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="text-sm text-gray-400">Confirmed</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Model Performance */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardHeader>
              <CardTitle>Model Performance</CardTitle>
              <CardDescription>Key metrics from the ensemble model</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metricsData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                    <XAxis type="number" domain={[0, 100]} stroke="#9ca3af" />
                    <YAxis type="category" dataKey="metric" stroke="#9ca3af" width={80} />
                    <Tooltip 
                      contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px' }}
                      formatter={(value: number) => [`${value.toFixed(1)}%`, 'Score']}
                    />
                    <Bar dataKey="value" fill="url(#colorGradient)" radius={[0, 4, 4, 0]} />
                    <defs>
                      <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#8b5cf6" />
                        <stop offset="100%" stopColor="#06b6d4" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Individual Model Performance */}
      {modelStatus?.metrics?.individual_models && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Card>
            <CardHeader>
              <CardTitle>Individual Model Comparison</CardTitle>
              <CardDescription>Performance breakdown by model in the ensemble</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {Object.entries(modelStatus.metrics.individual_models).map(([name, data]) => (
                  <div key={name} className="bg-white/5 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-purple-300 uppercase mb-3">{name}</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-400">Accuracy</span>
                          <span className="text-white">{formatPercent(data.accuracy)}</span>
                        </div>
                        <Progress value={data.accuracy * 100} />
                      </div>
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-400">F1 Score</span>
                          <span className="text-white">{formatPercent(data.f1_macro)}</span>
                        </div>
                        <Progress value={data.f1_macro * 100} indicatorClassName="from-cyan-500 to-green-500" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Feature Importance Preview */}
      {modelStatus?.metrics?.feature_importance && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Card>
            <CardHeader>
              <CardTitle>Top Feature Importance</CardTitle>
              <CardDescription>Most influential features for classification</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(modelStatus.metrics.feature_importance)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 8)
                  .map(([feature, importance]) => (
                    <div key={feature}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">{feature.replace(/_/g, ' ')}</span>
                        <span className="text-purple-300">{(importance * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={importance * 100} />
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};
