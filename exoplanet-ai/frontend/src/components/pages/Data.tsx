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

type DatasetType = 'kepler' | 'k2' | 'tess';

export const Data: React.FC = () => {
  const [activeDataset, setActiveDataset] = useState<DatasetType>('kepler');
  const [loading, setLoading] = useState(true);
  const [combinedStats, setCombinedStats] = useState<CombinedStats | null>(null);
  const [keplerStats, setKeplerStats] = useState<KeplerStats | null>(null);
  const [k2Stats, setK2Stats] = useState<K2Stats | null>(null);
  const [tessStats, setTessStats] = useState<TessStats | null>(null);
  const [keplerData, setKeplerData] = useState<Record<string, unknown>[]>([]);
  const [k2Data, setK2Data] = useState<Record<string, unknown>[]>([]);
  const [tessData, setTessData] = useState<Record<string, unknown>[]>([]);

  // Fetch all data on mount
  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        // Fetch combined stats
        const combined = await getCombinedStats();
        setCombinedStats(combined);
        
        // Fetch Kepler data
        const kepler = await getKeplerData(50);
        setKeplerStats(kepler.statistics);
        setKeplerData(kepler.data);
        
        // Fetch K2 data
        const k2 = await getK2Data(50);
        setK2Stats(k2.statistics);
        setK2Data(k2.data);
        
        // Fetch TESS data
        const tess = await getTessData(50);
        setTessStats(tess.statistics);
        setTessData(tess.data);
      } catch (error) {
        console.error('Error fetching data:', error);
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
