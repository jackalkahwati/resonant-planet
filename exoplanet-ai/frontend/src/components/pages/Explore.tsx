import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Html } from '@react-three/drei';
import * as THREE from 'three';
import { Search, ThermometerSun, Globe2, Star, Calendar, Rocket } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { getConfirmedPlanets, ConfirmedPlanet } from '@/lib/api';
import { formatNumber, calculateHabitability } from '@/lib/utils';

// Default planets data for instant loading
const DEFAULT_PLANETS: ConfirmedPlanet[] = [
  { name: 'Kepler-442 b', host_star: 'Kepler-442', discovery_method: 'Transit', discovery_year: 2015, discovery_facility: 'Kepler', orbital_period_days: 112.3, radius_earth: 1.34, mass_earth: 2.34, semi_major_axis_au: 0.409, eccentricity: 0.04, equilibrium_temp_k: 233, insolation_flux: 0.7, star_temp_k: 4402, star_radius_solar: 0.6, star_mass_solar: 0.61, distance_pc: 342, ra: 291.4, dec: 39.3, potentially_habitable: true, num_planets_in_system: 1 },
  { name: 'TRAPPIST-1 e', host_star: 'TRAPPIST-1', discovery_method: 'Transit', discovery_year: 2017, discovery_facility: 'Spitzer', orbital_period_days: 6.1, radius_earth: 0.92, mass_earth: 0.77, semi_major_axis_au: 0.029, eccentricity: 0.005, equilibrium_temp_k: 251, insolation_flux: 0.66, star_temp_k: 2566, star_radius_solar: 0.12, star_mass_solar: 0.09, distance_pc: 12.4, ra: 346.6, dec: -5.0, potentially_habitable: true, num_planets_in_system: 7 },
  { name: 'Proxima Centauri b', host_star: 'Proxima Centauri', discovery_method: 'Radial Velocity', discovery_year: 2016, discovery_facility: 'La Silla', orbital_period_days: 11.2, radius_earth: 1.3, mass_earth: 1.27, semi_major_axis_au: 0.049, eccentricity: 0.11, equilibrium_temp_k: 234, insolation_flux: 0.65, star_temp_k: 3050, star_radius_solar: 0.15, star_mass_solar: 0.12, distance_pc: 1.3, ra: 217.4, dec: -62.7, potentially_habitable: true, num_planets_in_system: 2 },
  { name: 'Kepler-22 b', host_star: 'Kepler-22', discovery_method: 'Transit', discovery_year: 2011, discovery_facility: 'Kepler', orbital_period_days: 289.9, radius_earth: 2.4, mass_earth: 9.1, semi_major_axis_au: 0.849, eccentricity: 0, equilibrium_temp_k: 295, insolation_flux: 1.1, star_temp_k: 5518, star_radius_solar: 0.98, star_mass_solar: 0.97, distance_pc: 187, ra: 286.2, dec: 47.9, potentially_habitable: true, num_planets_in_system: 1 },
  { name: 'HD 209458 b', host_star: 'HD 209458', discovery_method: 'Radial Velocity', discovery_year: 1999, discovery_facility: 'Multiple', orbital_period_days: 3.52, radius_earth: 15.1, mass_earth: 220, semi_major_axis_au: 0.047, eccentricity: 0.014, equilibrium_temp_k: 1449, insolation_flux: 194, star_temp_k: 6065, star_radius_solar: 1.2, star_mass_solar: 1.12, distance_pc: 48, ra: 330.8, dec: 18.9, potentially_habitable: false, num_planets_in_system: 1 },
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
  const [exoplanets, setExoplanets] = useState<ConfirmedPlanet[]>(DEFAULT_PLANETS);
  const [selectedPlanet, setSelectedPlanet] = useState<ConfirmedPlanet | null>(null);
  const [totalPlanets, setTotalPlanets] = useState(5500);

  // Fetch real data silently in background
  useEffect(() => {
    const fetchExoplanets = async () => {
      try {
        const response = await getConfirmedPlanets(50);
        if (response.planets?.length > 0) {
          setExoplanets(response.planets);
          setTotalPlanets(response.total_confirmed);
        }
      } catch (error) {
        console.error('Error fetching exoplanets:', error);
      }
    };
    fetchExoplanets();
  }, []);

  const habitability = selectedPlanet ? calculateHabitability(selectedPlanet.insolation_flux) : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-2">Explore Exoplanets</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Interactive 3D visualization of {totalPlanets.toLocaleString()}+ confirmed exoplanets from NASA TAP Archive
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
            <CardTitle>Confirmed Exoplanets Catalog</CardTitle>
            <CardDescription>Data from NASA Exoplanet Archive Planetary Systems TAP table</CardDescription>
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
