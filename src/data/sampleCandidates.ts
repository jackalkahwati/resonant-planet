export interface Candidate {
  id: string;
  name: string;
  mission: string;
  probability: number;
  period: number;
  depth: number;
  duration: number;
  snr: number;
  validations: {
    oddEven: boolean;
    secondary: boolean;
    shape: boolean;
    centroid: boolean;
  };
  baselineProbability: number;
  baselineFlags: string[];
  description: string;
  isConfirmed: boolean;
  isFalsePositive: boolean;
}

export const sampleCandidates: Candidate[] = [
  {
    id: "KIC-10593626",
    name: "Kepler-90i",
    mission: "Kepler",
    probability: 0.96,
    period: 14.45,
    depth: 0.009,
    duration: 3.4,
    snr: 14.2,
    validations: {
      oddEven: true,
      secondary: true,
      shape: true,
      centroid: true,
    },
    baselineProbability: 0.73,
    baselineFlags: ["Low SNR warning", "Period alias possible"],
    description: "Earth-sized planet in 8-planet system. Classic pipeline flagged as low confidence due to shallow depth, but physics validation confirms genuine transit.",
    isConfirmed: true,
    isFalsePositive: false,
  },
  {
    id: "KIC-8462852",
    name: "KIC 8462852",
    mission: "Kepler",
    probability: 0.94,
    period: 3.52,
    depth: 0.012,
    duration: 2.8,
    snr: 12.4,
    validations: {
      oddEven: true,
      secondary: true,
      shape: true,
      centroid: true,
    },
    baselineProbability: 0.88,
    baselineFlags: ["Passed standard checks"],
    description: "High-confidence detection with strong periodic signal. Both pipelines agree this is a genuine planetary candidate.",
    isConfirmed: true,
    isFalsePositive: false,
  },
  {
    id: "KIC-5812701",
    name: "Kepler-452b",
    mission: "Kepler",
    probability: 0.91,
    period: 384.8,
    depth: 0.003,
    duration: 8.6,
    snr: 7.8,
    validations: {
      oddEven: true,
      secondary: true,
      shape: true,
      centroid: true,
    },
    baselineProbability: 0.52,
    baselineFlags: ["Long period - insufficient data", "Low SNR - requires vetting"],
    description: "Earth's older cousin in the habitable zone. Long period and shallow depth challenged classic pipeline, but our physics-first approach confidently validates the signal.",
    isConfirmed: true,
    isFalsePositive: false,
  },
  {
    id: "KIC-9704149",
    name: "False Positive - EB",
    mission: "Kepler",
    probability: 0.18,
    period: 2.47,
    depth: 0.024,
    duration: 2.1,
    snr: 18.6,
    validations: {
      oddEven: false,
      secondary: false,
      shape: false,
      centroid: true,
    },
    baselineProbability: 0.82,
    baselineFlags: ["High confidence candidate"],
    description: "Eclipsing binary masquerading as planet. Strong signal fooled classic pipeline, but our odd/even depth check and secondary eclipse detection revealed the false positive.",
    isConfirmed: false,
    isFalsePositive: true,
  },
];

export const getDemoCandidate = (index: number = 0): Candidate => {
  return sampleCandidates[index % sampleCandidates.length];
};

export const getRandomDemo = (): Candidate => {
  return sampleCandidates[Math.floor(Math.random() * sampleCandidates.length)];
};
