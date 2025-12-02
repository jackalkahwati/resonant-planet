import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Html } from '@react-three/drei';
import * as THREE from 'three';
import { Search, ThermometerSun, Globe2, Star, Calendar, Rocket } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { ConfirmedPlanet } from '@/lib/api';
import { formatNumber, calculateHabitability } from '@/lib/utils';

// Real K2 exoplanet data from NASA Exoplanet Archive CSV
const K2_EXOPLANETS: ConfirmedPlanet[] = [
  // Confirmed K2 planets with complete data
  { name: 'BD+20 594 b', host_star: 'BD+20 594', discovery_method: 'Transit', discovery_year: 2016, discovery_facility: 'K2', orbital_period_days: 41.69, radius_earth: 2.58, mass_earth: 22.25, semi_major_axis_au: 0.241, eccentricity: 0.0, equilibrium_temp_k: 546, insolation_flux: 1.2, star_temp_k: 5766, star_radius_solar: 0.93, star_mass_solar: 0.96, distance_pc: 179.5, ra: 53.65, dec: 20.60, potentially_habitable: false, num_planets_in_system: 1 },
  { name: 'K2-3 b', host_star: 'K2-3', discovery_method: 'Transit', discovery_year: 2015, discovery_facility: 'K2', orbital_period_days: 10.05, radius_earth: 2.29, mass_earth: 6.6, semi_major_axis_au: 0.077, eccentricity: 0.0, equilibrium_temp_k: 463, insolation_flux: 8.6, star_temp_k: 3896, star_radius_solar: 0.56, star_mass_solar: 0.60, distance_pc: 44.0, ra: 172.33, dec: -1.45, potentially_habitable: false, num_planets_in_system: 3 },
  { name: 'K2-3 c', host_star: 'K2-3', discovery_method: 'Transit', discovery_year: 2015, discovery_facility: 'K2', orbital_period_days: 24.65, radius_earth: 1.77, mass_earth: 2.1, semi_major_axis_au: 0.140, eccentricity: 0.0, equilibrium_temp_k: 344, insolation_flux: 2.6, star_temp_k: 3896, star_radius_solar: 0.56, star_mass_solar: 0.60, distance_pc: 44.0, ra: 172.33, dec: -1.45, potentially_habitable: true, num_planets_in_system: 3 },
  { name: 'K2-3 d', host_star: 'K2-3', discovery_method: 'Transit', discovery_year: 2015, discovery_facility: 'K2', orbital_period_days: 44.56, radius_earth: 1.51, mass_earth: 1.2, semi_major_axis_au: 0.208, eccentricity: 0.0, equilibrium_temp_k: 282, insolation_flux: 1.2, star_temp_k: 3896, star_radius_solar: 0.56, star_mass_solar: 0.60, distance_pc: 44.0, ra: 172.33, dec: -1.45, potentially_habitable: true, num_planets_in_system: 3 },
  { name: 'K2-18 b', host_star: 'K2-18', discovery_method: 'Transit', discovery_year: 2015, discovery_facility: 'K2', orbital_period_days: 32.94, radius_earth: 2.61, mass_earth: 8.63, semi_major_axis_au: 0.143, eccentricity: 0.0, equilibrium_temp_k: 284, insolation_flux: 0.94, star_temp_k: 3457, star_radius_solar: 0.41, star_mass_solar: 0.50, distance_pc: 38.0, ra: 172.56, dec: 7.59, potentially_habitable: true, num_planets_in_system: 2 },
  { name: 'K2-18 c', host_star: 'K2-18', discovery_method: 'Transit', discovery_year: 2017, discovery_facility: 'K2', orbital_period_days: 8.96, radius_earth: 2.36, mass_earth: 5.62, semi_major_axis_au: 0.060, eccentricity: 0.0, equilibrium_temp_k: 437, insolation_flux: 5.4, star_temp_k: 3457, star_radius_solar: 0.41, star_mass_solar: 0.50, distance_pc: 38.0, ra: 172.56, dec: 7.59, potentially_habitable: false, num_planets_in_system: 2 },
  { name: 'K2-141 b', host_star: 'K2-141', discovery_method: 'Transit', discovery_year: 2017, discovery_facility: 'K2', orbital_period_days: 0.28, radius_earth: 1.51, mass_earth: 5.08, semi_major_axis_au: 0.007, eccentricity: 0.0, equilibrium_temp_k: 2050, insolation_flux: 2850, star_temp_k: 4570, star_radius_solar: 0.68, star_mass_solar: 0.71, distance_pc: 61.5, ra: 353.73, dec: -1.18, potentially_habitable: false, num_planets_in_system: 2 },
  { name: 'K2-229 b', host_star: 'K2-229', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 0.58, radius_earth: 1.16, mass_earth: 2.59, semi_major_axis_au: 0.012, eccentricity: 0.0, equilibrium_temp_k: 1960, insolation_flux: 2600, star_temp_k: 5185, star_radius_solar: 0.79, star_mass_solar: 0.84, distance_pc: 103.0, ra: 129.51, dec: 10.78, potentially_habitable: false, num_planets_in_system: 3 },
  { name: 'K2-138 b', host_star: 'K2-138', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 2.35, radius_earth: 1.51, mass_earth: 3.1, semi_major_axis_au: 0.034, eccentricity: 0.0, equilibrium_temp_k: 1150, insolation_flux: 118, star_temp_k: 5378, star_radius_solar: 0.86, star_mass_solar: 0.93, distance_pc: 66.5, ra: 66.79, dec: 24.16, potentially_habitable: false, num_planets_in_system: 6 },
  { name: 'K2-138 c', host_star: 'K2-138', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 3.56, radius_earth: 2.30, mass_earth: 6.3, semi_major_axis_au: 0.045, eccentricity: 0.0, equilibrium_temp_k: 996, insolation_flux: 67, star_temp_k: 5378, star_radius_solar: 0.86, star_mass_solar: 0.93, distance_pc: 66.5, ra: 66.79, dec: 24.16, potentially_habitable: false, num_planets_in_system: 6 },
  { name: 'K2-138 d', host_star: 'K2-138', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 5.40, radius_earth: 2.39, mass_earth: 7.9, semi_major_axis_au: 0.059, eccentricity: 0.0, equilibrium_temp_k: 872, insolation_flux: 39, star_temp_k: 5378, star_radius_solar: 0.86, star_mass_solar: 0.93, distance_pc: 66.5, ra: 66.79, dec: 24.16, potentially_habitable: false, num_planets_in_system: 6 },
  { name: 'K2-138 e', host_star: 'K2-138', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 8.26, radius_earth: 3.39, mass_earth: 13.0, semi_major_axis_au: 0.078, eccentricity: 0.0, equilibrium_temp_k: 760, insolation_flux: 23, star_temp_k: 5378, star_radius_solar: 0.86, star_mass_solar: 0.93, distance_pc: 66.5, ra: 66.79, dec: 24.16, potentially_habitable: false, num_planets_in_system: 6 },
  { name: 'K2-138 f', host_star: 'K2-138', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 12.76, radius_earth: 2.90, mass_earth: 1.6, semi_major_axis_au: 0.104, eccentricity: 0.0, equilibrium_temp_k: 657, insolation_flux: 12.5, star_temp_k: 5378, star_radius_solar: 0.86, star_mass_solar: 0.93, distance_pc: 66.5, ra: 66.79, dec: 24.16, potentially_habitable: false, num_planets_in_system: 6 },
  { name: 'K2-266 b', host_star: 'K2-266', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 0.66, radius_earth: 3.30, mass_earth: 11.3, semi_major_axis_au: 0.013, eccentricity: 0.0, equilibrium_temp_k: 1640, insolation_flux: 1450, star_temp_k: 4285, star_radius_solar: 0.62, star_mass_solar: 0.69, distance_pc: 78.0, ra: 72.18, dec: 14.85, potentially_habitable: false, num_planets_in_system: 4 },
  { name: 'K2-155 d', host_star: 'K2-155', discovery_method: 'Transit', discovery_year: 2018, discovery_facility: 'K2', orbital_period_days: 40.68, radius_earth: 1.64, mass_earth: 4.0, semi_major_axis_au: 0.19, eccentricity: 0.0, equilibrium_temp_k: 287, insolation_flux: 1.05, star_temp_k: 4258, star_radius_solar: 0.58, star_mass_solar: 0.65, distance_pc: 68.2, ra: 55.60, dec: 16.50, potentially_habitable: true, num_planets_in_system: 3 },
  { name: 'EPIC 201170410 b', host_star: 'EPIC 201170410', discovery_method: 'Transit', discovery_year: 2020, discovery_facility: 'K2', orbital_period_days: 6.80, radius_earth: 1.05, mass_earth: 0.9, semi_major_axis_au: 0.035, eccentricity: 0.0, equilibrium_temp_k: 350, insolation_flux: 1.8, star_temp_k: 3648, star_radius_solar: 0.28, star_mass_solar: 0.29, distance_pc: 45.0, ra: 170.14, dec: -4.81, potentially_habitable: true, num_planets_in_system: 1 },
  { name: 'EPIC 201238110 b', host_star: 'EPIC 201238110', discovery_method: 'Transit', discovery_year: 2019, discovery_facility: 'K2', orbital_period_days: 28.17, radius_earth: 1.87, mass_earth: 4.2, semi_major_axis_au: 0.12, eccentricity: 0.0, equilibrium_temp_k: 310, insolation_flux: 1.3, star_temp_k: 3800, star_radius_solar: 0.41, star_mass_solar: 0.41, distance_pc: 159.3, ra: 179.71, dec: -3.39, potentially_habitable: true, num_planets_in_system: 1 },
  { name: 'K2-72 e', host_star: 'K2-72', discovery_method: 'Transit', discovery_year: 2016, discovery_facility: 'K2', orbital_period_days: 24.16, radius_earth: 1.29, mass_earth: 2.21, semi_major_axis_au: 0.106, eccentricity: 0.0, equilibrium_temp_k: 260, insolation_flux: 0.84, star_temp_k: 3360, star_radius_solar: 0.33, star_mass_solar: 0.36, distance_pc: 66.5, ra: 167.39, dec: -3.55, potentially_habitable: true, num_planets_in_system: 4 },
  { name: 'K2-288 B b', host_star: 'K2-288 B', discovery_method: 'Transit', discovery_year: 2019, discovery_facility: 'K2', orbital_period_days: 31.39, radius_earth: 1.91, mass_earth: 4.3, semi_major_axis_au: 0.164, eccentricity: 0.0, equilibrium_temp_k: 226, insolation_flux: 0.51, star_temp_k: 3341, star_radius_solar: 0.32, star_mass_solar: 0.33, distance_pc: 68.0, ra: 118.35, dec: 22.01, potentially_habitable: true, num_planets_in_system: 1 },
];

// 3D Planet Component
function Planet({ planet, position, onClick, isSelected }: { 
  planet: ConfirmedPlanet; 
  position: [number, number, number];
  onClick: () => void;
  isSelected: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  
  // Calculate planet color based on temperature
  const getColor = () => {
    const temp = planet.equilibrium_temp_k;
    if (temp < 200) return '#3b82f6'; // Cold - blue
    if (temp < 300) return '#22c55e'; // Habitable - green
    if (temp < 500) return '#eab308'; // Warm - yellow
    if (temp < 1000) return '#f97316'; // Hot - orange
    return '#ef4444'; // Very hot - red
  };

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005;
      if (isSelected) {
        meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.1);
      }
    }
    if (glowRef.current && isSelected && glowRef.current.material) {
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = 0.3 + Math.sin(state.clock.elapsedTime * 3) * 0.2;
    }
  });

  const size = Math.min(Math.max(planet.radius_earth * 0.3, 0.2), 2);
  const color = getColor();

  return (
    <group position={position}>
      {/* Glow effect */}
      {isSelected && (
        <mesh ref={glowRef}>
          <sphereGeometry args={[size * 1.5, 32, 32]} />
          <meshBasicMaterial color={color} transparent opacity={0.3} />
        </mesh>
      )}
      
      {/* Planet */}
      <mesh ref={meshRef} onClick={onClick}>
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial 
          color={color}
          roughness={0.7}
          metalness={0.3}
        />
      </mesh>
      
      {/* Label */}
      <Html position={[0, size + 0.5, 0]} center>
        <div className={`text-xs whitespace-nowrap px-2 py-1 rounded ${isSelected ? 'bg-purple-500 text-white' : 'bg-black/50 text-gray-300'}`}>
          {planet.name}
        </div>
      </Html>
    </group>
  );
}

// Star/Sun Component
function StarSun({ position }: { position: [number, number, number] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshBasicMaterial color="#fcd34d" />
      <pointLight color="#fcd34d" intensity={2} distance={50} />
    </mesh>
  );
}

// 3D Scene
function ExoplanetScene({ exoplanets, selectedPlanet, onSelectPlanet }: {
  exoplanets: ConfirmedPlanet[];
  selectedPlanet: ConfirmedPlanet | null;
  onSelectPlanet: (planet: ConfirmedPlanet) => void;
}) {
  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      
      <StarSun position={[0, 0, 0]} />
      
      {exoplanets.slice(0, 20).map((planet, i) => {
        const angle = (i / 20) * Math.PI * 2;
        const radius = 5 + (i % 5) * 3;
        const position: [number, number, number] = [
          Math.cos(angle) * radius,
          (Math.random() - 0.5) * 4,
          Math.sin(angle) * radius
        ];
        
        return (
          <Planet
            key={planet.name}
            planet={planet}
            position={position}
            onClick={() => onSelectPlanet(planet)}
            isSelected={selectedPlanet?.name === planet.name}
          />
        );
      })}
      
      <OrbitControls 
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        autoRotate={true}
        autoRotateSpeed={0.5}
      />
    </>
  );
}

export const Explore: React.FC = () => {
  const [exoplanets] = useState<ConfirmedPlanet[]>(K2_EXOPLANETS);
  const [selectedPlanet, setSelectedPlanet] = useState<ConfirmedPlanet | null>(null);

  const habitability = selectedPlanet ? calculateHabitability(selectedPlanet.insolation_flux) : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-2">Explore K2 Exoplanets</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Interactive 3D visualization of {exoplanets.length} confirmed K2 exoplanets from NASA Exoplanet Archive
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Viewer */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="lg:col-span-2">
          <Card className="overflow-hidden">
            <div className="h-[500px] bg-black relative">
              <Canvas camera={{ position: [0, 10, 20], fov: 60 }}>
                <ExoplanetScene
                  exoplanets={exoplanets}
                  selectedPlanet={selectedPlanet}
                  onSelectPlanet={setSelectedPlanet}
                />
              </Canvas>
              
              {/* Controls hint */}
              <div className="absolute bottom-4 left-4 text-xs text-gray-400 bg-black/50 px-3 py-2 rounded">
                Drag to rotate • Scroll to zoom • Click planet to select
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Planet Details */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle>Planet Details</CardTitle>
              <CardDescription>
                {selectedPlanet ? selectedPlanet.name : 'Click a planet to view details'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedPlanet ? (
                <div className="text-center py-12 text-gray-400">
                  <Search className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>Select a planet to view its properties</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Habitability Indicator */}
                  {habitability && (
                    <div className={`p-4 rounded-lg border ${
                      habitability.score > 0.5 ? 'bg-green-500/10 border-green-500/30' : 'bg-yellow-500/10 border-yellow-500/30'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Globe2 className={`w-5 h-5 ${habitability.score > 0.5 ? 'text-green-400' : 'text-yellow-400'}`} />
                        <span className="font-medium text-white">{habitability.label}</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${habitability.score > 0.5 ? 'bg-green-500' : 'bg-yellow-500'}`}
                          style={{ width: `${habitability.score * 100}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Discovery Info */}
                  <div className="p-3 bg-white/5 rounded-lg mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Rocket className="w-4 h-4 text-cyan-400" />
                      <span className="text-sm text-gray-400">Discovery</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="text-gray-500 text-xs">Method</p>
                        <p className="text-white">{selectedPlanet.discovery_method}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 text-xs">Year</p>
                        <p className="text-white">{selectedPlanet.discovery_year}</p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-gray-500 text-xs">Facility</p>
                        <p className="text-white">{selectedPlanet.discovery_facility}</p>
                      </div>
                    </div>
                  </div>

                  {/* Properties */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                      <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <Globe2 className="w-5 h-5 text-purple-400" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-400">Radius / Mass</p>
                        <p className="text-white font-medium">{formatNumber(selectedPlanet.radius_earth)} R⊕ • {formatNumber(selectedPlanet.mass_earth)} M⊕</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                      <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
                        <Calendar className="w-5 h-5 text-cyan-400" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-400">Orbital Period</p>
                        <p className="text-white font-medium">{formatNumber(selectedPlanet.orbital_period_days)} days</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                      <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                        <ThermometerSun className="w-5 h-5 text-orange-400" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-400">Temperature</p>
                        <p className="text-white font-medium">{formatNumber(selectedPlanet.equilibrium_temp_k, 0)} K</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                      <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                        <Star className="w-5 h-5 text-yellow-400" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-400">Host Star</p>
                        <p className="text-white font-medium">{selectedPlanet.host_star}</p>
                        <p className="text-xs text-gray-500">{formatNumber(selectedPlanet.distance_pc)} pc away</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Planet List */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Card>
          <CardHeader>
            <CardTitle>K2 Confirmed Exoplanets</CardTitle>
            <CardDescription>Real data from NASA K2 mission - including potentially habitable worlds</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {exoplanets.map((planet) => (
                <button
                  key={planet.name}
                  onClick={() => setSelectedPlanet(planet)}
                  className={`p-4 rounded-lg border text-left transition-all ${
                    selectedPlanet?.name === planet.name
                      ? 'bg-purple-500/20 border-purple-500'
                      : 'bg-white/5 border-white/10 hover:border-purple-500/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full ${
                      planet.potentially_habitable ? 'bg-green-500' : 'bg-purple-500'
                    } flex items-center justify-center`}>
                      <Globe2 className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-white text-sm truncate">{planet.name}</p>
                      <p className="text-xs text-gray-400">
                        {formatNumber(planet.radius_earth)}R⊕ • {planet.discovery_year}
                      </p>
                      <p className="text-xs text-gray-500 truncate">{planet.discovery_method}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
