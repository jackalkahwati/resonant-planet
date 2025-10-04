"""
Biosignature detection using Modulus Universal Problem Solver.

This module analyzes exoplanet atmospheres for signs of life by:
1. Detecting chemical disequilibrium (e.g., O2 + CH4)
2. Modeling atmospheric spectroscopy
3. Ruling out abiotic (non-biological) sources
4. Computing biosignature confidence scores
"""
import math
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
import requests
from dataclasses import dataclass
from core.biosignature_modulus_workflow import (
    ModulusBiosignatureWorkflow,
    AtmosphericSnapshot,
)

logger = logging.getLogger(__name__)


@dataclass
class MolecularFeature:
    """Detected molecular absorption feature."""
    molecule: str
    wavelength_um: float
    depth_ppm: float
    confidence: float
    
    
@dataclass
class BiosignatureResult:
    """Result of biosignature analysis."""
    biosignature_score: float  # 0-1 probability of life
    detected_molecules: List[str]
    disequilibrium_score: float
    false_positive_probability: float
    confidence_level: str  # "low", "medium", "high", "definitive"
    explanation: str
    modulus_analysis: Optional[Dict] = None


class ModulusChemistryAnalyzer:
    """
    Uses Modulus API to perform exact chemistry calculations for biosignatures.
    """
    
    def __init__(self, api_url: str = "https://modulus-865475771210.europe-west1.run.app", api_key: str = "demo-key"):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})
        
    def check_chemical_equilibrium(
        self,
        molecules: Dict[str, float],
        temperature_k: float = 288.0,
        pressure_bar: float = 1.0
    ) -> Dict:
        """
        Check if detected atmospheric composition is in chemical equilibrium.
        
        Parameters
        ----------
        molecules : dict
            Molecule concentrations, e.g., {'O2': 0.21, 'CH4': 1.8e-6, 'N2': 0.78}
        temperature_k : float
            Atmospheric temperature in Kelvin
        pressure_bar : float
            Atmospheric pressure in bar
        
        Returns
        -------
        dict
            Analysis including equilibrium state, timescales, disequilibrium score
        """
        # Format molecules for Modulus
        mol_str = "\n".join([f"   - {mol}: {conc*100:.6g}%" for mol, conc in molecules.items()])
        
        problem = f"""
        An exoplanet atmosphere contains:
{mol_str}
        
        Atmospheric conditions:
        - Temperature: {temperature_k} K
        - Pressure: {pressure_bar} bar
        
        Questions:
        1. Is this composition in thermodynamic equilibrium?
        2. For any disequilibrium, calculate reaction timescale (how fast should gases react?)
        3. Calculate Gibbs free energy change for key reactions
        4. What continuous source is needed to maintain this composition?
        
        Focus on reactions like: CH4 + 2O2 → CO2 + 2H2O
        """
        
        # Legacy path retained for compatibility but compute_gas_disequilibrium is preferred.
        logger.warning("check_chemical_equilibrium is deprecated; use ModulusBiosignatureWorkflow instead")
        return {'success': False, 'is_disequilibrium': None}
    
    def calculate_spectroscopic_depth(
        self,
        molecule: str,
        concentration: float,
        planet_radius_earth: float = 1.0,
        scale_height_km: float = 8.0
    ) -> Dict:
        """
        Calculate expected absorption depth for a molecule in transmission spectrum.
        
        Parameters
        ----------
        molecule : str
            Molecule name (e.g., 'O2', 'H2O', 'CH4')
        concentration : float
            Volume mixing ratio (e.g., 0.21 for 21% O2)
        planet_radius_earth : float
            Planet radius in Earth radii
        scale_height_km : float
            Atmospheric scale height in km
        
        Returns
        -------
        dict
            Expected absorption depth, wavelengths, detectability
        """
        problem = f"""
        Calculate transmission spectroscopy signal for exoplanet:
        
        Planet properties:
        - Radius: {planet_radius_earth} Earth radii
        - Atmospheric scale height: {scale_height_km} km
        
        Molecule: {molecule}
        - Concentration: {concentration*100}% by volume
        
        Questions:
        1. Calculate atmospheric annulus area during transit
        2. For primary absorption band of {molecule}, calculate optical depth
        3. Compute absorption depth in ppm (parts per million)
        4. Compare to photon noise limit for JWST (assume 100 ppm precision)
        
        Is this molecule detectable with current telescopes?
        """
        
        try:
            response = self.session.post(
                f"{self.api_url}/v2/solve",
                json={"problem": problem},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'explanation': result.get('explanation', ''),
                    'expected_depth_ppm': self._parse_depth(result),
                    'detectable': True  # Parse from explanation
                }
            else:
                return {'success': False}
                
        except Exception as e:
            logger.error(f"Spectroscopy calculation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_false_positives(
        self,
        molecule: str,
        concentration: float,
        stellar_uv_flux: float = 1.0,
        planet_age_gyr: float = 4.5
    ) -> Dict:
        """
        Analyze whether detected molecules could be from abiotic (non-biological) sources.
        
        Parameters
        ----------
        molecule : str
            Detected molecule (e.g., 'O2')
        concentration : float
            Observed concentration
        stellar_uv_flux : float
            UV flux relative to Sun (1.0 = solar)
        planet_age_gyr : float
            Planet age in billion years
        
        Returns
        -------
        dict
            Analysis of abiotic production mechanisms and likelihood
        """
        problem = f"""
        Detected: {concentration*100}% {molecule} on an exoplanet
        
        Planet/Star properties:
        - Stellar UV flux: {stellar_uv_flux}× Solar
        - Planet age: {planet_age_gyr} billion years
        
        Analyze abiotic (non-biological) sources:
        
        For O2:
        1. Water photolysis: H2O + UV → H + OH → O2 (hydrogen escapes)
        2. Calculate O2 production rate from photolysis
        3. Calculate O2 loss rate from surface oxidation (rocks, iron)
        4. Time to build up observed {concentration*100}% O2 abiotically?
        
        For CH4:
        1. Serpentinization: olivine + water → serpentine + H2 → CH4
        2. Outgassing from interior
        3. Cometary delivery
        
        Can abiotic processes explain the observed concentration?
        What is the probability this is biological vs. abiotic?
        """
        
        try:
            response = self.session.post(
                f"{self.api_url}/v2/solve",
                json={"problem": problem},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'explanation': result.get('explanation', ''),
                    'abiotic_likely': self._parse_abiotic_likelihood(result),
                    'biological_probability': 0.5  # Parse from explanation
                }
            else:
                return {'success': False}
                
        except Exception as e:
            logger.error(f"False positive analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_disequilibrium(self, result: Dict) -> bool:
        """Parse Modulus result to determine if disequilibrium exists."""
        explanation = result.get('explanation', '').lower()
        # Look for keywords indicating disequilibrium
        if any(word in explanation for word in ['disequilibrium', 'not equilibrium', 'unstable']):
            return True
        if any(word in explanation for word in ['equilibrium', 'stable', 'balanced']):
            return False
        return None
    
    def _parse_depth(self, result: Dict) -> Optional[float]:
        """Parse expected absorption depth from Modulus result."""
        # Try to extract ppm value from numerical answer or explanation
        if result.get('numerical_answer'):
            try:
                return float(result['numerical_answer'])
            except:
                pass
        return None
    
    def _parse_abiotic_likelihood(self, result: Dict) -> bool:
        """Parse whether abiotic sources are likely."""
        explanation = result.get('explanation', '').lower()
        if any(word in explanation for word in ['unlikely', 'cannot', 'insufficient']):
            return False
        if any(word in explanation for word in ['likely', 'can explain', 'sufficient']):
            return True
        return None


class BiosignatureDetector:
    """
    Main biosignature detection pipeline using spectroscopy + Modulus.
    """
    
    def __init__(self, modulus_api_url: str = "http://localhost:8000"):
        self.chemistry = ModulusChemistryAnalyzer(modulus_api_url)
        self.modulus_workflow = ModulusBiosignatureWorkflow(base_url=modulus_api_url)
        
        # Known biosignature molecules and their significance
        self.biosignature_molecules = {
            # Classic strong biosignatures
            'O2': {'weight': 0.8, 'primary_wavelength_um': 0.76, 'biosignature_strength': 'strong'},
            'O3': {'weight': 0.7, 'primary_wavelength_um': 9.6, 'biosignature_strength': 'strong'},
            'CH4': {'weight': 0.6, 'primary_wavelength_um': 3.3, 'biosignature_strength': 'strong'},
            
            # Moderate biosignatures
            'N2O': {'weight': 0.5, 'primary_wavelength_um': 7.8, 'biosignature_strength': 'moderate'},
            'NH3': {'weight': 0.5, 'primary_wavelength_um': 10.5, 'biosignature_strength': 'moderate'},
            
            # Controversial/emerging biosignatures
            'PH3': {'weight': 0.4, 'primary_wavelength_um': 4.3, 'biosignature_strength': 'controversial'},
            'DMS': {'weight': 0.9, 'primary_wavelength_um': 3.4, 'biosignature_strength': 'controversial'},
            'CH3Cl': {'weight': 0.6, 'primary_wavelength_um': 13.7, 'biosignature_strength': 'controversial'},
            'CH3Br': {'weight': 0.6, 'primary_wavelength_um': 7.1, 'biosignature_strength': 'controversial'},
            
            # Secondary indicators
            'SO2': {'weight': 0.3, 'primary_wavelength_um': 7.3, 'biosignature_strength': 'weak'},
            'NO2': {'weight': 0.3, 'primary_wavelength_um': 6.2, 'biosignature_strength': 'weak'},
        }
        
        # Extended disequilibrium pairs (beyond classic O2+CH4)
        self.disequilibrium_pairs = {
            # Classic pairs
            ('O2', 'CH4'): {
                'score': 0.85, 
                'explanation': 'Classic Earth-like biosignature - O2+CH4 react rapidly without replenishment',
                'timescale_years': 10,
                'precedent': 'Earth atmosphere'
            },
            ('O2', 'O3'): {
                'score': 0.80, 
                'explanation': 'Photochemical disequilibrium - O3 from O2 photolysis',
                'timescale_years': 1,
                'precedent': 'Earth stratosphere'
            },
            
            # Agricultural/microbial biosignatures
            ('N2O', 'CH4'): {
                'score': 0.75, 
                'explanation': 'Agricultural/microbial biosignature - both produced by microbial metabolism',
                'timescale_years': 100,
                'precedent': 'Agricultural Earth'
            },
            ('NH3', 'CH4'): {
                'score': 0.65, 
                'explanation': 'Early Earth analog - methanogenesis + nitrogen fixation',
                'timescale_years': 50,
                'precedent': 'Archean Earth (3 Gya)'
            },
            
            # Marine/aquatic biosignatures
            ('DMS', 'O2'): {
                'score': 0.80, 
                'explanation': 'Marine biosphere indicator - DMS from phytoplankton',
                'timescale_years': 5,
                'precedent': 'Marine phytoplankton blooms'
            },
            ('DMS', 'CH4'): {
                'score': 0.70,
                'explanation': 'Aquatic biosignature - both from anaerobic + aerobic marine life',
                'timescale_years': 20,
                'precedent': 'Ocean ecosystems'
            },
            
            # Controversial pairs
            ('PH3', 'O2'): {
                'score': 0.70, 
                'explanation': 'Controversial but strong disequilibrium - PH3 oxidizes rapidly in O2',
                'timescale_years': 1,
                'precedent': 'Debated (Venus clouds?)'
            },
            ('PH3', 'CH4'): {
                'score': 0.60,
                'explanation': 'Anaerobic biosignature pair - both from reducing environments',
                'timescale_years': 30,
                'precedent': 'Speculative'
            },
            
            # Biological halogens
            ('CH3Cl', 'CH3Br'): {
                'score': 0.60, 
                'explanation': 'Biological halogen production - marine algae and fungi',
                'timescale_years': 10,
                'precedent': 'Tropical marine ecosystems'
            },
            ('CH3Cl', 'O2'): {
                'score': 0.65,
                'explanation': 'Halogenated compound with oxidizer - biological origin likely',
                'timescale_years': 15,
                'precedent': 'Forest ecosystems'
            },
            
            # Industrial/pollution biosignatures (technologically advanced life)
            ('NO2', 'SO2'): {
                'score': 0.55,
                'explanation': 'Industrial pollution signature - combustion byproducts',
                'timescale_years': 5,
                'precedent': 'Industrial Earth (post-1800)'
            },
        }
    
    def analyze_spectrum(
        self,
        wavelengths_um: np.ndarray,
        absorption_depths_ppm: np.ndarray,
        planet_params: Dict
    ) -> BiosignatureResult:
        """
        Analyze transmission spectrum for biosignatures.
        
        Parameters
        ----------
        wavelengths_um : array
            Wavelengths in microns
        absorption_depths_ppm : array
            Absorption depths in ppm
        planet_params : dict
            Planet properties (radius, temperature, etc.)
        
        Returns
        -------
        BiosignatureResult
            Complete biosignature analysis
        """
        logger.info("Starting biosignature analysis...")
        
        # Step 1: Identify molecules from spectrum
        detected_molecules = self._identify_molecules(wavelengths_um, absorption_depths_ppm)
        
        if not detected_molecules:
            return BiosignatureResult(
                biosignature_score=0.0,
                detected_molecules=[],
                disequilibrium_score=0.0,
                false_positive_probability=1.0,
                confidence_level="low",
                explanation="No biosignature molecules detected in spectrum"
            )
        
        logger.info(f"Detected molecules: {[m.molecule for m in detected_molecules]}")
        
        # Step 2: Check for chemical disequilibrium using Modulus
        molecule_dict = {m.molecule: 0.01 for m in detected_molecules}
        
        # Check for ALL known disequilibrium pairs (extended detection)
        molecule_names = [m.molecule for m in detected_molecules]
        
        # Find the strongest disequilibrium pair
        max_disequilibrium_score = 0.3  # Default for no pairs
        detected_pair = None
        pair_explanation = ""
        
        for (mol1, mol2), props in self.disequilibrium_pairs.items():
            if mol1 in molecule_names and mol2 in molecule_names:
                if props['score'] > max_disequilibrium_score:
                    max_disequilibrium_score = props['score']
                    detected_pair = (mol1, mol2)
                    pair_explanation = props['explanation']
                    
                    logger.info(f"✓ Disequilibrium pair detected: {mol1}+{mol2} (score: {props['score']:.2f})")
                    logger.info(f"  {props['explanation']}")
                    logger.info(f"  Reaction timescale: {props['timescale_years']} years")
                    logger.info(f"  Precedent: {props['precedent']}")
        
        disequilibrium_score = max_disequilibrium_score
        
        if detected_pair:
            logger.info(f"⭐ STRONGEST PAIR: {detected_pair[0]}+{detected_pair[1]} (score: {disequilibrium_score:.2f})")
        else:
            logger.info("No known disequilibrium pairs detected")

        # Try to get exact Modulus calculation for refinement
        workflow_results = []
        try:
            gas_ppm = {
                mol: max(conc * 1e6, 1.0)
                for mol, conc in molecule_dict.items()
            }

            snapshot = AtmosphericSnapshot(
                planet_name=planet_params.get('name', 'unknown'),
                stellar_flux_rel_solar=planet_params.get('stellar_uv_flux', 1.0),
                equilibrium_temperature_k=planet_params.get('temperature_k', 288.0),
                greenhouse_temperature_k=planet_params.get('greenhouse_temperature_k'),
                gas_mixing_ratios_ppm=gas_ppm,
            )

            workflow_results = self.modulus_workflow.run_composite_analysis(snapshot)

            # If Modulus provides better calculation, use it
            log_ratio = next((c for c in workflow_results if c.metric_name == "log10_CO2_CH4"), None)
            if log_ratio and not math.isnan(log_ratio.value):
                modulus_score = 0.9 if log_ratio.value >= 2.0 else (0.6 if log_ratio.value >= 1.0 else 0.3)
                # Take maximum of pair-based and Modulus calculation
                disequilibrium_score = max(disequilibrium_score, modulus_score)
                logger.info(f"Modulus refinement: log10_CO2_CH4 = {log_ratio.value:.2f}")

            greenhouse = next((c for c in workflow_results if c.metric_name == "greenhouse_temperature_offset"), None)
            if greenhouse and not math.isnan(greenhouse.value) and greenhouse.value >= 20:
                disequilibrium_score = min(1.0, disequilibrium_score + 0.1)

        except Exception as exc:
            logger.warning("Modulus biosignature workflow failed: %s", exc)
        
        # Create equilibrium result summary
        equilibrium_result = {
            'is_disequilibrium': disequilibrium_score > 0.5,
            'score': disequilibrium_score,
            'explanation': f"Disequilibrium score: {disequilibrium_score:.2f}"
        }
        
        # Step 3: Analyze false positives for each molecule
        false_positive_scores = []
        
        for mol_feature in detected_molecules:
            if mol_feature.molecule in ['O2', 'CH4', 'O3']:
                fp_result = self.chemistry.analyze_false_positives(
                    mol_feature.molecule,
                    0.01,  # Rough concentration
                    stellar_uv_flux=planet_params.get('stellar_uv_flux', 1.0),
                    planet_age_gyr=planet_params.get('age_gyr', 4.5)
                )
                
                if fp_result.get('success'):
                    abiotic_likely = fp_result.get('abiotic_likely', True)
                    false_positive_scores.append(0.8 if abiotic_likely else 0.2)
        
        false_positive_prob = np.mean(false_positive_scores) if false_positive_scores else 0.5
        
        # Step 4: Calculate overall biosignature score (with temperature filtering)
        temperature_k = planet_params.get('temperature_k', 288.0)
        biosignature_score = self._calculate_biosignature_score(
            detected_molecules,
            disequilibrium_score,
            false_positive_prob,
            temperature_k
        )
        
        # Step 5: Determine confidence level
        confidence = self._determine_confidence(biosignature_score, detected_molecules)
        
        # Step 6: Generate explanation
        explanation = self._generate_explanation(
            detected_molecules,
            equilibrium_result,
            biosignature_score,
            false_positive_prob,
            temperature_k
        )
        
        return BiosignatureResult(
            biosignature_score=biosignature_score,
            detected_molecules=[m.molecule for m in detected_molecules],
            disequilibrium_score=disequilibrium_score,
            false_positive_probability=false_positive_prob,
            confidence_level=confidence,
            explanation=explanation,
            modulus_analysis=equilibrium_result
        )
    
    def _identify_molecules(
        self,
        wavelengths: np.ndarray,
        depths: np.ndarray
    ) -> List[MolecularFeature]:
        """Identify molecules from absorption features in transmission spectrum."""
        detected = []
        
        # Convert transmission flux (0-1) to depth if needed
        if np.all(depths <= 1.0) and np.all(depths >= 0.0):
            # This is transmission flux, convert to absorption depth
            # Lower transmission = more absorption
            baseline = np.median(depths)
            absorption_depth = (baseline - depths) * 1e6  # Convert to ppm
            logger.info(f"Converted transmission to absorption depth (baseline: {baseline:.3f})")
        else:
            # Already in ppm
            absorption_depth = depths
        
        for molecule, props in self.biosignature_molecules.items():
            primary_wl = props['primary_wavelength_um']
            
            # Look for absorption near this wavelength
            mask = np.abs(wavelengths - primary_wl) < 0.15  # Broader search window
            
            if np.any(mask):
                max_depth = float(np.max(absorption_depth[mask]))
                
                # Lower thresholds for realistic detection (Earth-like signals are 100-500 ppm)
                # Strong biosignatures: O2, O3, CH4 at 200+ ppm
                # Moderate biosignatures: N2O at 150+ ppm  
                # Controversial: PH3, DMS at 100+ ppm (need careful validation)
                if props['biosignature_strength'] == 'strong':
                    threshold = 200  # Lowered from 1000
                elif props['biosignature_strength'] == 'moderate':
                    threshold = 150  # Lowered from 500
                else:  # controversial
                    threshold = 100  # Lowered from 1000
                
                if max_depth > threshold:
                    detected.append(MolecularFeature(
                        molecule=molecule,
                        wavelength_um=primary_wl,
                        depth_ppm=max_depth,
                        confidence=0.9 if max_depth > 2000 else 0.7
                    ))
                    logger.info(f"Detected {molecule} at {primary_wl:.2f}μm (depth: {max_depth:.0f} ppm)")
        
        return detected
    
    def _calculate_biosignature_score(
        self,
        molecules: List[MolecularFeature],
        disequilibrium: float,
        false_positive_prob: float,
        temperature_k: float = 288.0
    ) -> float:
        """
        Calculate overall biosignature probability.
        
        Temperature filtering:
        - Hot Jupiters (>1000K): Automatically very low score (<0.1)
        - Warm planets (600-1000K): Strong penalty
        - Temperate planets (200-600K): Normal scoring
        - Cold planets (<200K): Moderate penalty (life unlikely)
        """
        if not molecules:
            return 0.0
        
        # Temperature-based habitability penalty
        if temperature_k > 1000:
            # Hot Jupiter - biosignatures extremely unlikely
            temperature_factor = 0.05  # Maximum 5% score
            logger.info(f"Hot Jupiter penalty applied (T={temperature_k:.0f}K)")
        elif temperature_k > 600:
            # Very warm - strong penalty
            temperature_factor = 0.3
            logger.info(f"Warm planet penalty applied (T={temperature_k:.0f}K)")
        elif temperature_k > 200:
            # Habitable zone - no penalty
            temperature_factor = 1.0
        else:
            # Too cold - moderate penalty
            temperature_factor = 0.5
            logger.info(f"Cold planet penalty applied (T={temperature_k:.0f}K)")
        
        # Weighted sum of molecule detections
        molecule_score = sum(
            self.biosignature_molecules[m.molecule]['weight'] * m.confidence
            for m in molecules if m.molecule in self.biosignature_molecules
        ) / len(molecules)
        
        # Combine with disequilibrium and false positive analysis
        base_score = (
            0.4 * molecule_score +
            0.3 * disequilibrium +
            0.3 * (1 - false_positive_prob)
        )
        
        # Apply temperature penalty
        score = base_score * temperature_factor
        
        return min(1.0, max(0.0, score))
    
    def _determine_confidence(self, score: float, molecules: List) -> str:
        """Determine confidence level."""
        if score > 0.8 and len(molecules) >= 2:
            return "high"
        elif score > 0.6:
            return "medium"
        elif score > 0.4:
            return "low"
        else:
            return "very_low"
    
    def _generate_explanation(
        self,
        molecules: List[MolecularFeature],
        equilibrium_result: Dict,
        score: float,
        fp_prob: float,
        temperature_k: float = 288.0
    ) -> str:
        """Generate human-readable explanation."""
        mol_str = ", ".join([m.molecule for m in molecules])
        
        explanation = f"Biosignature Analysis (Score: {score:.2f}/1.00)\n\n"
        explanation += f"Planet Temperature: {temperature_k:.0f} K\n"
        
        # Temperature context
        if temperature_k > 1000:
            explanation += "⚠️  HOT JUPITER - Biosignatures highly unlikely due to extreme temperature\n\n"
        elif temperature_k > 600:
            explanation += "⚠️  Very warm planet - Life unlikely at this temperature\n\n"
        elif 200 <= temperature_k <= 600:
            explanation += "✓ Temperate planet - Within potential habitable range\n\n"
        else:
            explanation += "⚠️  Cold planet - Life unlikely at this temperature\n\n"
        
        explanation += f"Detected molecules: {mol_str}\n\n"
        
        if equilibrium_result.get('is_disequilibrium'):
            explanation += "✅ Chemical disequilibrium detected - requires active replenishment\n"
        else:
            explanation += "⚠️  Atmospheric composition appears in equilibrium\n"
        
        explanation += f"\nFalse positive probability: {fp_prob:.1%}\n"
        
        if score > 0.7:
            explanation += "\n🌟 STRONG biosignature candidate - warrants follow-up!"
        elif score > 0.5:
            explanation += "\n🔍 Moderate biosignature - needs more data"
        else:
            explanation += "\n⚠️  Weak biosignature - likely abiotic"
        
        if equilibrium_result.get('explanation'):
            explanation += f"\n\nModulus Analysis:\n{equilibrium_result['explanation'][:300]}..."
        
        return explanation

