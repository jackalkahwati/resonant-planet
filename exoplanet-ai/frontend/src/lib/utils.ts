import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number, decimals: number = 2): string {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  if (Math.abs(num) < 0.001 && num !== 0) return num.toExponential(decimals);
  return num.toFixed(decimals);
}

export function formatPercent(num: number): string {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return `${(num * 100).toFixed(1)}%`;
}

export function getClassColor(className: string): string {
  switch (className.toLowerCase()) {
    case 'confirmed':
      return 'text-green-400';
    case 'candidate':
      return 'text-yellow-400';
    case 'false positive':
      return 'text-red-400';
    default:
      return 'text-gray-400';
  }
}

export function getClassBgColor(className: string): string {
  switch (className.toLowerCase()) {
    case 'confirmed':
      return 'bg-green-500/20 border-green-500/50';
    case 'candidate':
      return 'bg-yellow-500/20 border-yellow-500/50';
    case 'false positive':
      return 'bg-red-500/20 border-red-500/50';
    default:
      return 'bg-gray-500/20 border-gray-500/50';
  }
}

export function formatFeatureName(feature: string): string {
  const nameMap: Record<string, string> = {
    'koi_period': 'Orbital Period (days)',
    'koi_duration': 'Transit Duration (hours)',
    'koi_depth': 'Transit Depth (ppm)',
    'koi_prad': 'Planet Radius (Earth)',
    'koi_teq': 'Equilibrium Temp (K)',
    'koi_insol': 'Insolation Flux',
    'koi_model_snr': 'Signal-to-Noise',
    'koi_steff': 'Star Temp (K)',
    'koi_srad': 'Star Radius (Solar)',
    'koi_smass': 'Star Mass (Solar)',
    'koi_impact': 'Impact Parameter',
    'koi_slogg': 'Surface Gravity',
    'koi_sage': 'Star Age (Gyr)',
    'koi_smet': 'Stellar Metallicity',
    'radius_ratio': 'Planet/Star Radius',
    'transit_duty_cycle': 'Transit Duty Cycle',
    'in_habitable_zone': 'Habitable Zone',
    'stellar_density': 'Stellar Density',
    'temp_ratio': 'Temperature Ratio',
  };
  return nameMap[feature] || feature.replace(/_/g, ' ').replace(/koi /i, '').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

export function generateStars(count: number): Array<{ x: number; y: number; size: number; delay: number }> {
  return Array.from({ length: count }, () => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 2 + 1,
    delay: Math.random() * 2,
  }));
}

export function calculateHabitability(insol: number): { score: number; label: string } {
  // Earth-like insolation is around 1.0
  // Habitable zone is roughly 0.36 to 1.1
  if (insol >= 0.36 && insol <= 1.1) {
    const score = 1 - Math.abs(1 - insol) / 0.64;
    return { score, label: 'Potentially Habitable' };
  } else if (insol > 1.1 && insol < 2) {
    return { score: 0.3, label: 'Too Hot' };
  } else if (insol > 0.2 && insol < 0.36) {
    return { score: 0.3, label: 'Too Cold' };
  }
  return { score: 0.1, label: 'Uninhabitable' };
}
