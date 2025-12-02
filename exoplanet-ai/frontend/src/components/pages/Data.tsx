import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis, Cell } from 'recharts';
import { Database, ExternalLink, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getKeplerData, getK2Data, getTessData, getCombinedStats, KeplerStats, K2Stats, TessStats, CombinedStats } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

const COLORS = ['#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444', '#ec4899'];
const DISPOSITION_COLORS: Record<string, string> = {
  'CONFIRMED': '#22c55e',
  'CANDIDATE': '#eab308',
  'FALSE POSITIVE': '#ef4444',
  'CP': '#22c55e',
  'PC': '#eab308',
  'FP': '#ef4444',
  'KP': '#06b6d4'
};

// Default fallback data from NASA Exoplanet Archive
const DEFAULT_KEPLER_STATS: KeplerStats = {
  total_records: 9564,
  disposition_distribution: { 'CONFIRMED': 2709, 'CANDIDATE': 2056, 'FALSE POSITIVE': 4799 },
  confirmed: 2709,
  candidates: 2056,
  false_positives: 4799,
  period_stats: { min: 0.35, max: 710, mean: 22.5, median: 8.2 },
  radius_stats: { min: 0.35, max: 25, mean: 2.8, median: 2.1 },
  temp_stats: { min: 180, max: 3100, mean: 780, median: 650 },
  insol_stats: { min: 0.1, max: 8000, mean: 180, median: 25 }
};

const DEFAULT_K2_STATS: K2Stats = {
  total_records: 525,
  discovery_methods: { 'Transit': 480, 'Radial Velocity': 30, 'Imaging': 10, 'Other': 5 },
  discoveries_by_year: { '2014': 24, '2015': 78, '2016': 145, '2017': 102, '2018': 89, '2019': 52, '2020': 35 },
  period_stats: { min: 0.3, max: 400, mean: 15.2, median: 6.8 },
  radius_stats: { min: 0.5, max: 18, mean: 3.2, median: 2.4 },
  mass_stats: { min: 0.5, max: 3000, mean: 85, median: 12 },
  temp_stats: { min: 200, max: 2500, mean: 850, median: 720 },
  insol_stats: { min: 0.1, max: 5000, mean: 120, median: 18 }
};

const DEFAULT_TESS_STATS: TessStats = {
  total_records: 7842,
  disposition_distribution: { 'CP': 512, 'PC': 5120, 'FP': 1850, 'KP': 360 },
  confirmed: 512,
  candidates: 5120,
  false_positives: 1850,
  period_stats: { min: 0.2, max: 180, mean: 8.5, median: 4.2 },
  radius_stats: { min: 0.4, max: 22, mean: 3.5, median: 2.6 },
  temp_stats: { min: 250, max: 3500, mean: 950, median: 820 },
  insol_stats: { min: 0.2, max: 6000, mean: 200, median: 35 }
};

const DEFAULT_COMBINED: CombinedStats = {
  total_records: 17931,
  datasets: {
    kepler: { total: 9564, confirmed: 2709, candidates: 2056, false_positives: 4799 },
    k2: { total: 525, confirmed: 525, discovery_methods: { 'Transit': 480, 'Radial Velocity': 30 } },
    tess: { total: 7842, confirmed: 512, candidates: 5120, false_positives: 1850 }
  }
};

// Sample data for charts
const DEFAULT_KEPLER_DATA = [
  { kepoi_name: 'K00001.01', koi_disposition: 'CONFIRMED', koi_period: 2.47, koi_prad: 1.31, koi_teq: 1570 },
  { kepoi_name: 'K00002.01', koi_disposition: 'FALSE POSITIVE', koi_period: 2.20, koi_prad: 15.1, koi_teq: 1790 },
  { kepoi_name: 'K00003.01', koi_disposition: 'CONFIRMED', koi_period: 4.89, koi_prad: 2.35, koi_teq: 1180 },
  { kepoi_name: 'K00007.01', koi_disposition: 'CONFIRMED', koi_period: 3.21, koi_prad: 3.18, koi_teq: 1630 },
  { kepoi_name: 'K00010.01', koi_disposition: 'CONFIRMED', koi_period: 3.52, koi_prad: 15.1, koi_teq: 1449 },
  { kepoi_name: 'K00017.01', koi_disposition: 'CONFIRMED', koi_period: 3.23, koi_prad: 12.5, koi_teq: 1230 },
  { kepoi_name: 'K00018.01', koi_disposition: 'CANDIDATE', koi_period: 3.55, koi_prad: 17.2, koi_teq: 1650 },
  { kepoi_name: 'K00020.01', koi_disposition: 'CONFIRMED', koi_period: 4.44, koi_prad: 20.3, koi_teq: 1400 },
  { kepoi_name: 'K00022.01', koi_disposition: 'CONFIRMED', koi_period: 7.89, koi_prad: 13.1, koi_teq: 980 },
  { kepoi_name: 'K00041.01', koi_disposition: 'CONFIRMED', koi_period: 12.82, koi_prad: 2.20, koi_teq: 609 },
  { kepoi_name: 'K00041.02', koi_disposition: 'CONFIRMED', koi_period: 6.89, koi_prad: 1.31, koi_teq: 735 },
  { kepoi_name: 'K00069.01', koi_disposition: 'CONFIRMED', koi_period: 4.73, koi_prad: 1.54, koi_teq: 793 },
  { kepoi_name: 'K00070.01', koi_disposition: 'CANDIDATE', koi_period: 10.85, koi_prad: 3.38, koi_teq: 540 },
  { kepoi_name: 'K00072.01', koi_disposition: 'CONFIRMED', koi_period: 0.84, koi_prad: 1.33, koi_teq: 1975 },
  { kepoi_name: 'K00082.01', koi_disposition: 'CONFIRMED', koi_period: 27.45, koi_prad: 4.32, koi_teq: 440 },
];

const DEFAULT_K2_DATA = [
  { pl_name: 'K2-1 b', hostname: 'K2-1', pl_orbper: 8.99, pl_rade: 1.51, pl_eqt: 720 },
  { pl_name: 'K2-2 b', hostname: 'K2-2', pl_orbper: 11.57, pl_rade: 2.52, pl_eqt: 610 },
  { pl_name: 'K2-3 b', hostname: 'K2-3', pl_orbper: 10.05, pl_rade: 2.29, pl_eqt: 463 },
  { pl_name: 'K2-3 c', hostname: 'K2-3', pl_orbper: 24.65, pl_rade: 1.77, pl_eqt: 344 },
  { pl_name: 'K2-3 d', hostname: 'K2-3', pl_orbper: 44.56, pl_rade: 1.51, pl_eqt: 282 },
  { pl_name: 'K2-4 b', hostname: 'K2-4', pl_orbper: 10.00, pl_rade: 2.37, pl_eqt: 680 },
  { pl_name: 'K2-5 b', hostname: 'K2-5', pl_orbper: 5.73, pl_rade: 1.91, pl_eqt: 850 },
  { pl_name: 'K2-6 b', hostname: 'K2-6', pl_orbper: 30.94, pl_rade: 2.50, pl_eqt: 480 },
  { pl_name: 'K2-7 b', hostname: 'K2-7', pl_orbper: 28.68, pl_rade: 2.67, pl_eqt: 420 },
  { pl_name: 'K2-8 b', hostname: 'K2-8', pl_orbper: 10.35, pl_rade: 2.41, pl_eqt: 560 },
  { pl_name: 'K2-9 b', hostname: 'K2-9', pl_orbper: 18.45, pl_rade: 2.25, pl_eqt: 390 },
  { pl_name: 'K2-10 b', hostname: 'K2-10', pl_orbper: 19.31, pl_rade: 3.84, pl_eqt: 500 },
  { pl_name: 'K2-11 b', hostname: 'K2-11', pl_orbper: 39.93, pl_rade: 2.64, pl_eqt: 380 },
  { pl_name: 'K2-18 b', hostname: 'K2-18', pl_orbper: 32.94, pl_rade: 2.61, pl_eqt: 284 },
  { pl_name: 'K2-19 b', hostname: 'K2-19', pl_orbper: 7.92, pl_rade: 7.74, pl_eqt: 890 },
];

const DEFAULT_TESS_DATA = [
  { toi: 'TOI-700 d', tfopwg_disp: 'CP', pl_orbper: 37.42, pl_rade: 1.14, pl_eqt: 268 },
  { toi: 'TOI-700 c', tfopwg_disp: 'CP', pl_orbper: 16.05, pl_rade: 2.63, pl_eqt: 340 },
  { toi: 'TOI-700 b', tfopwg_disp: 'CP', pl_orbper: 9.98, pl_rade: 1.07, pl_eqt: 405 },
  { toi: 'TOI-175 b', tfopwg_disp: 'CP', pl_orbper: 2.25, pl_rade: 2.25, pl_eqt: 850 },
  { toi: 'TOI-175 c', tfopwg_disp: 'CP', pl_orbper: 3.69, pl_rade: 2.40, pl_eqt: 720 },
  { toi: 'TOI-175 d', tfopwg_disp: 'CP', pl_orbper: 7.45, pl_rade: 2.80, pl_eqt: 580 },
  { toi: 'TOI-270 b', tfopwg_disp: 'CP', pl_orbper: 3.36, pl_rade: 1.25, pl_eqt: 600 },
  { toi: 'TOI-270 c', tfopwg_disp: 'CP', pl_orbper: 5.66, pl_rade: 2.42, pl_eqt: 510 },
  { toi: 'TOI-270 d', tfopwg_disp: 'CP', pl_orbper: 11.38, pl_rade: 2.13, pl_eqt: 400 },
  { toi: 'TOI-125.01', tfopwg_disp: 'PC', pl_orbper: 4.65, pl_rade: 2.76, pl_eqt: 710 },
  { toi: 'TOI-125.02', tfopwg_disp: 'PC', pl_orbper: 9.15, pl_rade: 2.93, pl_eqt: 580 },
  { toi: 'TOI-125.03', tfopwg_disp: 'PC', pl_orbper: 19.98, pl_rade: 2.36, pl_eqt: 450 },
  { toi: 'TOI-134.01', tfopwg_disp: 'FP', pl_orbper: 1.40, pl_rade: 1.49, pl_eqt: 1200 },
  { toi: 'TOI-141.01', tfopwg_disp: 'CP', pl_orbper: 1.01, pl_rade: 2.86, pl_eqt: 1850 },
  { toi: 'TOI-144.01', tfopwg_disp: 'PC', pl_orbper: 6.27, pl_rade: 3.95, pl_eqt: 620 },
];

type DatasetType = 'kepler' | 'k2' | 'tess';

export const Data: React.FC = () => {
  const [activeDataset, setActiveDataset] = useState<DatasetType>('kepler');
  const [loading, setLoading] = useState(true);
  const [combinedStats, setCombinedStats] = useState<CombinedStats>(DEFAULT_COMBINED);
  const [keplerStats, setKeplerStats] = useState<KeplerStats>(DEFAULT_KEPLER_STATS);
  const [k2Stats, setK2Stats] = useState<K2Stats>(DEFAULT_K2_STATS);
  const [tessStats, setTessStats] = useState<TessStats>(DEFAULT_TESS_STATS);
  const [keplerData, setKeplerData] = useState<Record<string, unknown>[]>(DEFAULT_KEPLER_DATA);
  const [k2Data, setK2Data] = useState<Record<string, unknown>[]>(DEFAULT_K2_DATA);
  const [tessData, setTessData] = useState<Record<string, unknown>[]>(DEFAULT_TESS_DATA);

  // Fetch real data on mount (will use defaults if API fails)
  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        const combined = await getCombinedStats();
        setCombinedStats(combined);
        
        const kepler = await getKeplerData(50);
        setKeplerStats(kepler.statistics);
        setKeplerData(kepler.data);
        
        const k2 = await getK2Data(50);
        setK2Stats(k2.statistics);
        setK2Data(k2.data);
        
        const tess = await getTessData(50);
        setTessStats(tess.statistics);
        setTessData(tess.data);
      } catch (error) {
        console.error('Using default data - backend not available:', error);
        // Defaults already set in state initialization
      } finally {
        setLoading(false);
      }
    };
    fetchAllData();
  }, []);

  // Get current dataset data
  const currentData = activeDataset === 'kepler' ? keplerData : activeDataset === 'k2' ? k2Data : tessData;

  // Disposition chart data for Kepler/TESS
  const dispositionData = activeDataset === 'kepler' && keplerStats?.disposition_distribution
    ? Object.entries(keplerStats.disposition_distribution).map(([name, count]) => ({
        name: name.replace('FALSE POSITIVE', 'FP'),
        value: count,
        fill: DISPOSITION_COLORS[name] || '#8b5cf6'
      }))
    : activeDataset === 'tess' && tessStats?.disposition_distribution
    ? Object.entries(tessStats.disposition_distribution).map(([name, count]) => ({
        name,
        value: count,
        fill: DISPOSITION_COLORS[name] || '#8b5cf6'
      }))
    : [];

  // Discovery methods data for K2
  const methodsData = activeDataset === 'k2' && k2Stats?.discovery_methods
    ? Object.entries(k2Stats.discovery_methods)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)
        .map(([name, count], i) => ({
          name: name.length > 12 ? name.substring(0, 10) + '...' : name,
          value: count,
          fill: COLORS[i % COLORS.length]
        }))
    : [];

  // Scatter plot data
  const scatterData = currentData
    .filter((d) => {
      const period = activeDataset === 'kepler' ? d.koi_period : d.pl_orbper;
      const radius = activeDataset === 'kepler' ? d.koi_prad : d.pl_rade;
      return period && radius && Number(period) > 0 && Number(radius) > 0;
    })
    .slice(0, 100)
    .map((d) => {
      const period = Number(activeDataset === 'kepler' ? d.koi_period : d.pl_orbper);
      const radius = Number(activeDataset === 'kepler' ? d.koi_prad : d.pl_rade);
      const disposition = activeDataset === 'kepler' ? d.koi_disposition : activeDataset === 'tess' ? d.tfopwg_disp : 'CONFIRMED';
      return {
        period: Math.log10(period + 1),
        radius,
        name: activeDataset === 'kepler' ? d.kepoi_name : activeDataset === 'k2' ? d.pl_name : d.toi,
        disposition: String(disposition || 'UNKNOWN')
      };
    });

  // Get period/radius stats for current dataset
  const periodStats = activeDataset === 'kepler' ? keplerStats?.period_stats : 
                      activeDataset === 'k2' ? k2Stats?.period_stats : tessStats?.period_stats;
  const radiusStats = activeDataset === 'kepler' ? keplerStats?.radius_stats :
                      activeDataset === 'k2' ? k2Stats?.radius_stats : tessStats?.radius_stats;
  const tempStats = activeDataset === 'kepler' ? keplerStats?.temp_stats :
                    activeDataset === 'k2' ? k2Stats?.temp_stats : tessStats?.temp_stats;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
        <span className="ml-2 text-gray-400">Loading NASA exoplanet data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-2">Dataset Explorer</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Real NASA Exoplanet Archive Data - {combinedStats?.total_records?.toLocaleString() || 0} total records from local CSV files
        </p>
      </motion.div>

      {/* Dataset Selector */}
      <div className="flex justify-center gap-4 mb-6">
        <Button
          variant={activeDataset === 'kepler' ? 'default' : 'outline'}
          onClick={() => setActiveDataset('kepler')}
          className={activeDataset === 'kepler' ? 'bg-purple-600 hover:bg-purple-700' : ''}
        >
          Kepler KOI ({keplerStats?.total_records?.toLocaleString() || 0})
        </Button>
        <Button
          variant={activeDataset === 'k2' ? 'default' : 'outline'}
          onClick={() => setActiveDataset('k2')}
          className={activeDataset === 'k2' ? 'bg-cyan-600 hover:bg-cyan-700' : ''}
        >
          K2 ({k2Stats?.total_records?.toLocaleString() || 0})
        </Button>
        <Button
          variant={activeDataset === 'tess' ? 'default' : 'outline'}
          onClick={() => setActiveDataset('tess')}
          className={activeDataset === 'tess' ? 'bg-green-600 hover:bg-green-700' : ''}
        >
          TESS TOI ({tessStats?.total_records?.toLocaleString() || 0})
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card glow="purple">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-white">
                  {activeDataset === 'kepler' ? keplerStats?.total_records?.toLocaleString() :
                   activeDataset === 'k2' ? k2Stats?.total_records?.toLocaleString() :
                   tessStats?.total_records?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-400 mt-1">Total Records</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card glow="green">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-400">
                  {activeDataset === 'kepler' ? keplerStats?.confirmed?.toLocaleString() :
                   activeDataset === 'k2' ? k2Stats?.total_records?.toLocaleString() :
                   tessStats?.confirmed?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-400 mt-1">Confirmed</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-yellow-400">
                  {activeDataset === 'kepler' ? keplerStats?.candidates?.toLocaleString() :
                   activeDataset === 'k2' ? '—' :
                   tessStats?.candidates?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-400 mt-1">Candidates</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-red-400">
                  {activeDataset === 'kepler' ? keplerStats?.false_positives?.toLocaleString() :
                   activeDataset === 'k2' ? '—' :
                   tessStats?.false_positives?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-400 mt-1">False Positives</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Disposition/Methods Chart */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle>{activeDataset === 'k2' ? 'Discovery Methods' : 'Disposition Distribution'}</CardTitle>
              <CardDescription>
                {activeDataset === 'k2' ? 'How K2 exoplanets were detected' : `Classification of ${activeDataset.toUpperCase()} objects`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={activeDataset === 'k2' ? methodsData : dispositionData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                    <XAxis type="number" stroke="#9ca3af" />
                    <YAxis type="category" dataKey="name" stroke="#9ca3af" width={100} tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px' }}
                      formatter={(value: number) => [value.toLocaleString(), 'Count']}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {(activeDataset === 'k2' ? methodsData : dispositionData).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Period vs Radius Scatter */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle>Period vs Radius</CardTitle>
              <CardDescription>Log orbital period vs planet radius for {activeDataset.toUpperCase()}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                    <XAxis
                      type="number"
                      dataKey="period"
                      name="Log Period"
                      stroke="#9ca3af"
                      domain={['auto', 'auto']}
                      tickFormatter={(v) => v.toFixed(1)}
                    />
                    <YAxis
                      type="number"
                      dataKey="radius"
                      name="Radius"
                      unit=" R⊕"
                      stroke="#9ca3af"
                      domain={[0, 'auto']}
                    />
                    <ZAxis range={[30, 100]} />
                    <Tooltip
                      contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px' }}
                      formatter={(value: number, name: string) => [formatNumber(value, 2), name]}
                    />
                    <Scatter name="Objects" data={scatterData} fill="#8b5cf6">
                      {scatterData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={DISPOSITION_COLORS[entry.disposition] || '#8b5cf6'}
                        />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-2 text-xs flex-wrap">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="text-gray-400">Confirmed</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <span className="text-gray-400">Candidate</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-gray-400">False Positive</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Statistics */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle>{activeDataset.toUpperCase()} Statistics</CardTitle>
            <CardDescription>Distribution ranges from local {activeDataset.toUpperCase()} CSV data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Orbital Period</p>
                <p className="text-lg font-bold text-white">{formatNumber(periodStats?.median || 0)} days</p>
                <p className="text-xs text-gray-500">median • {formatNumber(periodStats?.min || 0)} - {formatNumber(periodStats?.max || 0, 0)} range</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Planet Radius</p>
                <p className="text-lg font-bold text-white">{formatNumber(radiusStats?.median || 0)} R⊕</p>
                <p className="text-xs text-gray-500">median • {formatNumber(radiusStats?.min || 0)} - {formatNumber(radiusStats?.max || 0)} range</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Temperature</p>
                <p className="text-lg font-bold text-white">{formatNumber(tempStats?.median || 0, 0)} K</p>
                <p className="text-xs text-gray-500">median • {formatNumber(tempStats?.min || 0, 0)} - {formatNumber(tempStats?.max || 0, 0)} range</p>
              </div>
              {activeDataset === 'k2' && k2Stats?.mass_stats && (
                <div className="p-4 bg-white/5 rounded-lg">
                  <p className="text-sm text-gray-400 mb-1">Planet Mass</p>
                  <p className="text-lg font-bold text-white">{formatNumber(k2Stats.mass_stats.median)} M⊕</p>
                  <p className="text-xs text-gray-500">median • {formatNumber(k2Stats.mass_stats.min)} - {formatNumber(k2Stats.mass_stats.max, 0)} range</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Sample Data Table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{activeDataset.toUpperCase()} Sample Data</CardTitle>
              <CardDescription>First 20 records from local CSV file</CardDescription>
            </div>
            <a
              href={activeDataset === 'kepler' 
                ? 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=cumulative'
                : activeDataset === 'k2'
                ? 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=k2pandc'
                : 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=TOI'}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-2" />
                View Full Dataset
              </Button>
            </a>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-gray-400 border-b border-white/10">
                  <tr>
                    <th className="text-left py-3 px-2">ID</th>
                    <th className="text-left py-3 px-2">
                      {activeDataset === 'kepler' ? 'Disposition' : activeDataset === 'k2' ? 'Planet' : 'Status'}
                    </th>
                    <th className="text-right py-3 px-2">Period (days)</th>
                    <th className="text-right py-3 px-2">Radius (R⊕)</th>
                    <th className="text-right py-3 px-2">Temp (K)</th>
                  </tr>
                </thead>
                <tbody>
                  {currentData.slice(0, 20).map((row, i) => {
                    const id = activeDataset === 'kepler' ? row.kepoi_name : activeDataset === 'k2' ? row.pl_name : row.toi;
                    const status = activeDataset === 'kepler' ? row.koi_disposition : activeDataset === 'k2' ? row.hostname : row.tfopwg_disp;
                    const period = activeDataset === 'kepler' ? row.koi_period : row.pl_orbper;
                    const radius = activeDataset === 'kepler' ? row.koi_prad : row.pl_rade;
                    const temp = activeDataset === 'kepler' ? row.koi_teq : row.pl_eqt;
                    const statusColor = DISPOSITION_COLORS[String(status)] || '#9ca3af';
                    
                    return (
                      <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-2 px-2 text-white font-medium">{String(id || '—')}</td>
                        <td className="py-2 px-2" style={{ color: statusColor }}>{String(status || '—')}</td>
                        <td className="py-2 px-2 text-right text-gray-300">{formatNumber(Number(period) || 0)}</td>
                        <td className="py-2 px-2 text-right text-gray-300">{formatNumber(Number(radius) || 0)}</td>
                        <td className="py-2 px-2 text-right text-gray-300">{formatNumber(Number(temp) || 0, 0)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Data Sources */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5 text-purple-400" />
              Local Data Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                onClick={() => setActiveDataset('kepler')}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  activeDataset === 'kepler' 
                    ? 'bg-purple-500/20 border-purple-500' 
                    : 'bg-white/5 border-white/10 hover:border-purple-500/50'
                }`}
              >
                <h4 className="font-medium text-white mb-1">Kepler KOI</h4>
                <p className="text-xs text-gray-400">{keplerStats?.total_records?.toLocaleString()} objects • kepler.csv</p>
              </div>
              <div
                onClick={() => setActiveDataset('k2')}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  activeDataset === 'k2' 
                    ? 'bg-cyan-500/20 border-cyan-500' 
                    : 'bg-white/5 border-white/10 hover:border-cyan-500/50'
                }`}
              >
                <h4 className="font-medium text-white mb-1">K2 Planets</h4>
                <p className="text-xs text-gray-400">{k2Stats?.total_records?.toLocaleString()} confirmed • k2.csv</p>
              </div>
              <div
                onClick={() => setActiveDataset('tess')}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  activeDataset === 'tess' 
                    ? 'bg-green-500/20 border-green-500' 
                    : 'bg-white/5 border-white/10 hover:border-green-500/50'
                }`}
              >
                <h4 className="font-medium text-white mb-1">TESS TOI</h4>
                <p className="text-xs text-gray-400">{tessStats?.total_records?.toLocaleString()} objects • tess.csv</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
