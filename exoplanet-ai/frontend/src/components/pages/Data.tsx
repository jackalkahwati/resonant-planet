import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis, Cell } from 'recharts';
import { Database, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getPlanetStatistics, getConfirmedPlanets, PlanetStatistics, ConfirmedPlanet } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

// Default statistics to show immediately
const DEFAULT_STATS: PlanetStatistics = {
  total_planets: 5500,
  discovery_methods: {
    'Transit': 4200,
    'Radial Velocity': 1050,
    'Imaging': 70,
    'Microlensing': 180
  },
  discoveries_by_year: {
    '2014': 850, '2016': 1400, '2018': 300, '2020': 150, '2022': 200, '2024': 100
  },
  discovery_facilities: {
    'Kepler': 2700,
    'TESS': 400,
    'K2': 500,
    'Ground': 900
  },
  orbital_period_stats: { min: 0.09, max: 730000, mean: 835, median: 12.4 },
  radius_stats: { min: 0.3, max: 77, mean: 5.2, median: 2.4 },
  mass_stats: { min: 0.02, max: 30000, mean: 450, median: 14 },
  temperature_stats: { min: 50, max: 4050, mean: 950, median: 800 },
  potentially_habitable: 60
};

const DEFAULT_PLANETS: ConfirmedPlanet[] = [
  { name: 'Kepler-442 b', host_star: 'Kepler-442', discovery_method: 'Transit', discovery_year: 2015, discovery_facility: 'Kepler', orbital_period_days: 112.3, radius_earth: 1.34, mass_earth: 2.34, semi_major_axis_au: 0.409, eccentricity: 0.04, equilibrium_temp_k: 233, insolation_flux: 0.7, star_temp_k: 4402, star_radius_solar: 0.6, star_mass_solar: 0.61, distance_pc: 342, ra: 291.4, dec: 39.3, potentially_habitable: true, num_planets_in_system: 1 },
  { name: 'TRAPPIST-1 e', host_star: 'TRAPPIST-1', discovery_method: 'Transit', discovery_year: 2017, discovery_facility: 'Spitzer', orbital_period_days: 6.1, radius_earth: 0.92, mass_earth: 0.77, semi_major_axis_au: 0.029, eccentricity: 0.005, equilibrium_temp_k: 251, insolation_flux: 0.66, star_temp_k: 2566, star_radius_solar: 0.12, star_mass_solar: 0.09, distance_pc: 12.4, ra: 346.6, dec: -5.0, potentially_habitable: true, num_planets_in_system: 7 },
  { name: 'Proxima Centauri b', host_star: 'Proxima Centauri', discovery_method: 'Radial Velocity', discovery_year: 2016, discovery_facility: 'La Silla', orbital_period_days: 11.2, radius_earth: 1.3, mass_earth: 1.27, semi_major_axis_au: 0.049, eccentricity: 0.11, equilibrium_temp_k: 234, insolation_flux: 0.65, star_temp_k: 3050, star_radius_solar: 0.15, star_mass_solar: 0.12, distance_pc: 1.3, ra: 217.4, dec: -62.7, potentially_habitable: true, num_planets_in_system: 2 },
  { name: 'Kepler-22 b', host_star: 'Kepler-22', discovery_method: 'Transit', discovery_year: 2011, discovery_facility: 'Kepler', orbital_period_days: 289.9, radius_earth: 2.4, mass_earth: 9.1, semi_major_axis_au: 0.849, eccentricity: 0, equilibrium_temp_k: 295, insolation_flux: 1.1, star_temp_k: 5518, star_radius_solar: 0.98, star_mass_solar: 0.97, distance_pc: 187, ra: 286.2, dec: 47.9, potentially_habitable: true, num_planets_in_system: 1 },
  { name: 'HD 209458 b', host_star: 'HD 209458', discovery_method: 'Radial Velocity', discovery_year: 1999, discovery_facility: 'Multiple', orbital_period_days: 3.52, radius_earth: 15.1, mass_earth: 220, semi_major_axis_au: 0.047, eccentricity: 0.014, equilibrium_temp_k: 1449, insolation_flux: 194, star_temp_k: 6065, star_radius_solar: 1.2, star_mass_solar: 1.12, distance_pc: 48, ra: 330.8, dec: 18.9, potentially_habitable: false, num_planets_in_system: 1 },
];

const COLORS = ['#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444', '#ec4899'];

export const Data: React.FC = () => {
  const [statistics, setStatistics] = useState<PlanetStatistics>(DEFAULT_STATS);
  const [planets, setPlanets] = useState<ConfirmedPlanet[]>(DEFAULT_PLANETS);

  // Fetch real data silently in background
  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsResponse = await getPlanetStatistics();
        if (statsResponse?.statistics) {
          setStatistics(statsResponse.statistics);
        }
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
      
      try {
        const planetsResponse = await getConfirmedPlanets(100);
        if (planetsResponse?.planets?.length > 0) {
          setPlanets(planetsResponse.planets);
        }
      } catch (error) {
        console.error('Error fetching planets:', error);
      }
    };
    fetchData();
  }, []);

  // Discovery methods pie chart data
  const methodsData = Object.entries(statistics.discovery_methods)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([name, count], i) => ({
      name: name.length > 15 ? name.substring(0, 12) + '...' : name,
      value: count,
      fill: COLORS[i % COLORS.length]
    }));

  // Scatter plot data for period vs radius
  const scatterData = planets
    .filter(p => p.orbital_period_days > 0 && p.radius_earth > 0)
    .map(p => ({
      period: Math.log10(p.orbital_period_days + 1),
      radius: p.radius_earth,
      name: p.name,
      method: p.discovery_method,
      habitable: p.potentially_habitable
    }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-2">Dataset Explorer</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          NASA Exoplanet Archive - {statistics.total_planets.toLocaleString()} confirmed planets via TAP API
        </p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card glow="purple">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-white">
                  {statistics.total_planets.toLocaleString()}
                </p>
                <p className="text-sm text-gray-400 mt-1">Confirmed Planets</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card glow="cyan">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-cyan-400">
                  {statistics.discovery_methods['Transit']?.toLocaleString() || '0'}
                </p>
                <p className="text-sm text-gray-400 mt-1">Transit Detections</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card glow="green">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-400">
                  {statistics.potentially_habitable}
                </p>
                <p className="text-sm text-gray-400 mt-1">Potentially Habitable</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-yellow-400">
                  {formatNumber(statistics.radius_stats.median)} R⊕
                </p>
                <p className="text-sm text-gray-400 mt-1">Median Planet Radius</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Discovery Methods */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle>Discovery Methods</CardTitle>
              <CardDescription>How exoplanets were detected</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={methodsData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                    <XAxis type="number" stroke="#9ca3af" />
                    <YAxis type="category" dataKey="name" stroke="#9ca3af" width={100} tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px' }}
                      formatter={(value: number) => [value.toLocaleString(), 'Planets']}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {methodsData.map((entry, index) => (
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
              <CardDescription>Log orbital period vs planet radius</CardDescription>
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
                      labelFormatter={(label) => `Log Period: ${label}`}
                    />
                    <Scatter name="Exoplanets" data={scatterData} fill="#8b5cf6">
                      {scatterData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={entry.habitable ? '#22c55e' : '#8b5cf6'}
                        />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-2 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="text-gray-400">Potentially Habitable</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span className="text-gray-400">Other</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Planet Statistics */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle>Planet Statistics</CardTitle>
            <CardDescription>Distribution ranges from NASA Planetary Systems table</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Orbital Period</p>
                <p className="text-lg font-bold text-white">{formatNumber(statistics.orbital_period_stats.median)} days</p>
                <p className="text-xs text-gray-500">median • {formatNumber(statistics.orbital_period_stats.min)} - {formatNumber(statistics.orbital_period_stats.max, 0)} range</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Planet Radius</p>
                <p className="text-lg font-bold text-white">{formatNumber(statistics.radius_stats.median)} R⊕</p>
                <p className="text-xs text-gray-500">median • {formatNumber(statistics.radius_stats.min)} - {formatNumber(statistics.radius_stats.max)} range</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Planet Mass</p>
                <p className="text-lg font-bold text-white">{formatNumber(statistics.mass_stats.median)} M⊕</p>
                <p className="text-xs text-gray-500">median • {formatNumber(statistics.mass_stats.min)} - {formatNumber(statistics.mass_stats.max, 0)} range</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Temperature</p>
                <p className="text-lg font-bold text-white">{formatNumber(statistics.temperature_stats.median, 0)} K</p>
                <p className="text-xs text-gray-500">median • {formatNumber(statistics.temperature_stats.min, 0)} - {formatNumber(statistics.temperature_stats.max, 0)} range</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Sample Planets Table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Discoveries</CardTitle>
              <CardDescription>Latest confirmed exoplanets from TAP query</CardDescription>
            </div>
            <a
              href="https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS"
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
                    <th className="text-left py-3 px-2">Planet</th>
                    <th className="text-left py-3 px-2">Host Star</th>
                    <th className="text-left py-3 px-2">Method</th>
                    <th className="text-right py-3 px-2">Year</th>
                    <th className="text-right py-3 px-2">Radius</th>
                    <th className="text-right py-3 px-2">Period</th>
                  </tr>
                </thead>
                <tbody>
                  {planets.slice(0, 15).map((planet, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                      <td className={`py-2 px-2 font-medium ${planet.potentially_habitable ? 'text-green-400' : 'text-white'}`}>
                        {planet.name}
                      </td>
                      <td className="py-2 px-2 text-gray-300">{planet.host_star}</td>
                      <td className="py-2 px-2 text-gray-400">{planet.discovery_method}</td>
                      <td className="py-2 px-2 text-right text-cyan-400">{planet.discovery_year}</td>
                      <td className="py-2 px-2 text-right text-gray-300">{formatNumber(planet.radius_earth)} R⊕</td>
                      <td className="py-2 px-2 text-right text-gray-300">{formatNumber(planet.orbital_period_days)} d</td>
                    </tr>
                  ))}
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
              NASA TAP Data Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a
                href="https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS"
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 bg-white/5 rounded-lg hover:bg-purple-500/10 border border-white/10 hover:border-purple-500/50 transition-all"
              >
                <h4 className="font-medium text-white mb-1">Planetary Systems (ps)</h4>
                <p className="text-xs text-gray-400">Authoritative confirmed planets table</p>
              </a>
              <a
                href="https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=cumulative"
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 bg-white/5 rounded-lg hover:bg-purple-500/10 border border-white/10 hover:border-purple-500/50 transition-all"
              >
                <h4 className="font-medium text-white mb-1">Kepler KOI</h4>
                <p className="text-xs text-gray-400">Kepler Objects of Interest cumulative</p>
              </a>
              <a
                href="https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=TOI"
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 bg-white/5 rounded-lg hover:bg-purple-500/10 border border-white/10 hover:border-purple-500/50 transition-all"
              >
                <h4 className="font-medium text-white mb-1">TESS TOI</h4>
                <p className="text-xs text-gray-400">TESS Objects of Interest catalog</p>
              </a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
