"""
NASA Exoplanet Data Pipeline
Fetches and preprocesses data from NASA Exoplanet Archive
Supports: Kepler KOI, TESS TOI, K2 datasets
"""

import pandas as pd
import numpy as np
from io import StringIO
import requests
from typing import Optional, Tuple, Dict, List
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NASAExoplanetDataPipeline:
    """
    Modern data pipeline for NASA exoplanet datasets
    Implements latest preprocessing techniques for ML
    """
    
    # NASA Exoplanet Archive API endpoints
    BASE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    
    # Key features for exoplanet classification based on latest research
    KEPLER_FEATURES = [
        'koi_period',          # Orbital period (days)
        'koi_time0bk',         # Transit epoch (BJD - 2454833)
        'koi_impact',          # Impact parameter
        'koi_duration',        # Transit duration (hours)
        'koi_depth',           # Transit depth (ppm)
        'koi_prad',            # Planetary radius (Earth radii)
        'koi_teq',             # Equilibrium temperature (K)
        'koi_insol',           # Insolation flux (Earth flux)
        'koi_model_snr',       # Transit signal-to-noise ratio
        'koi_steff',           # Stellar effective temperature (K)
        'koi_slogg',           # Stellar surface gravity (log10(cm/s^2))
        'koi_srad',            # Stellar radius (solar radii)
        'koi_smass',           # Stellar mass (solar masses)
        'koi_sage',            # Stellar age (Gyr)
        'koi_smet',            # Stellar metallicity
    ]
    
    TESS_FEATURES = [
        'pl_orbper',           # Orbital period (days)
        'pl_trandur',          # Transit duration (hours)
        'pl_trandep',          # Transit depth (%)
        'pl_rade',             # Planet radius (Earth radii)
        'pl_eqt',              # Equilibrium temperature (K)
        'pl_insol',            # Insolation flux (Earth flux)
        'st_teff',             # Stellar effective temperature (K)
        'st_logg',             # Stellar surface gravity
        'st_rad',              # Stellar radius (solar radii)
        'st_mass',             # Stellar mass (solar masses)
        'st_met',              # Stellar metallicity
    ]
    
    LABEL_MAPPING = {
        'CONFIRMED': 2,        # Confirmed exoplanet
        'CANDIDATE': 1,        # Planetary candidate
        'FALSE POSITIVE': 0,   # False positive
        'FP': 0,               # False positive (alt)
        'PC': 1,               # Planetary candidate (alt)
        'CP': 2,               # Confirmed planet (alt)
        'KP': 2,               # Known planet (alt)
    }
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.data_cache = {}
    
    def fetch_confirmed_planets(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch confirmed exoplanets from the Planetary Systems (ps) table
        This is the authoritative source for confirmed planets
        """
        if use_cache and 'confirmed' in self.data_cache:
            return self.data_cache['confirmed']
        
        logger.info("Fetching confirmed planets from Planetary Systems table...")
        
        # Query the Planetary Systems table for confirmed planets
        query = """
        SELECT pl_name, hostname, sy_snum, sy_pnum, discoverymethod,
               disc_year, disc_facility, pl_orbper, pl_orbpererr1, pl_orbpererr2,
               pl_rade, pl_radeerr1, pl_radeerr2, pl_bmasse, pl_bmasseerr1, pl_bmasseerr2,
               pl_orbsmax, pl_orbsmaxerr1, pl_orbsmaxerr2, pl_orbeccen,
               pl_eqt, pl_eqterr1, pl_eqterr2, pl_insol, pl_insolerr1, pl_insolerr2,
               st_teff, st_tefferr1, st_tefferr2, st_rad, st_raderr1, st_raderr2,
               st_mass, st_masserr1, st_masserr2, st_met, st_meterr1, st_meterr2,
               st_logg, st_loggerr1, st_loggerr2, ra, dec, sy_dist
        FROM ps
        WHERE default_flag = 1
        ORDER BY disc_year DESC
        """
        
        params = {
            'query': query,
            'format': 'csv'
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=120)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            logger.info(f"Fetched {len(df)} confirmed planets")
            self.data_cache['confirmed'] = df
            return df
        except Exception as e:
            logger.error(f"Error fetching confirmed planets: {e}")
            raise
        
    def fetch_kepler_data(self, use_cache: bool = True) -> pd.DataFrame:
        """Fetch Kepler Objects of Interest (KOI) dataset"""
        if use_cache and 'kepler' in self.data_cache:
            return self.data_cache['kepler']
            
        logger.info("Fetching Kepler KOI dataset from NASA Exoplanet Archive...")
        
        query = """
        SELECT kepid, kepoi_name, koi_disposition, koi_pdisposition,
               koi_period, koi_period_err1, koi_period_err2,
               koi_time0bk, koi_time0bk_err1, koi_time0bk_err2,
               koi_impact, koi_impact_err1, koi_impact_err2,
               koi_duration, koi_duration_err1, koi_duration_err2,
               koi_depth, koi_depth_err1, koi_depth_err2,
               koi_prad, koi_prad_err1, koi_prad_err2,
               koi_teq, koi_teq_err1, koi_teq_err2,
               koi_insol, koi_insol_err1, koi_insol_err2,
               koi_model_snr,
               koi_steff, koi_steff_err1, koi_steff_err2,
               koi_slogg, koi_slogg_err1, koi_slogg_err2,
               koi_srad, koi_srad_err1, koi_srad_err2,
               koi_smass, koi_smass_err1, koi_smass_err2,
               koi_sage, koi_sage_err1, koi_sage_err2,
               koi_smet, koi_smet_err1, koi_smet_err2,
               koi_score
        FROM cumulative
        """
        
        params = {
            'query': query,
            'format': 'csv'
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=120)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            logger.info(f"Fetched {len(df)} Kepler KOI records")
            self.data_cache['kepler'] = df
            return df
        except Exception as e:
            logger.error(f"Error fetching Kepler data: {e}")
            raise
    
    def fetch_tess_data(self, use_cache: bool = True) -> pd.DataFrame:
        """Fetch TESS Objects of Interest (TOI) dataset"""
        if use_cache and 'tess' in self.data_cache:
            return self.data_cache['tess']
            
        logger.info("Fetching TESS TOI dataset from NASA Exoplanet Archive...")
        
        query = """
        SELECT tid, toi, tfopwg_disp,
               pl_orbper, pl_orbpererr1, pl_orbpererr2,
               pl_trandur, pl_trandurerr1, pl_trandurerr2,
               pl_trandep, pl_trandeperr1, pl_trandeperr2,
               pl_rade, pl_radeerr1, pl_radeerr2,
               pl_eqt, pl_eqterr1, pl_eqterr2,
               pl_insol, pl_insolerr1, pl_insolerr2,
               st_teff, st_tefferr1, st_tefferr2,
               st_logg, st_loggerr1, st_loggerr2,
               st_rad, st_raderr1, st_raderr2,
               st_mass, st_masserr1, st_masserr2,
               st_met, st_meterr1, st_meterr2
        FROM toi
        """
        
        params = {
            'query': query,
            'format': 'csv'
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=120)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            logger.info(f"Fetched {len(df)} TESS TOI records")
            self.data_cache['tess'] = df
            return df
        except Exception as e:
            logger.error(f"Error fetching TESS data: {e}")
            raise
    
    def engineer_features(self, df: pd.DataFrame, dataset_type: str = 'kepler') -> pd.DataFrame:
        """
        Apply advanced feature engineering based on latest research
        Creates derived features that improve classification accuracy
        """
        df = df.copy()
        
        if dataset_type == 'kepler':
            # Transit probability features
            if 'koi_prad' in df.columns and 'koi_srad' in df.columns:
                df['radius_ratio'] = df['koi_prad'] / (df['koi_srad'] * 109.076)  # Earth radii / Solar to Earth
                
            if 'koi_period' in df.columns and 'koi_duration' in df.columns:
                df['transit_duty_cycle'] = df['koi_duration'] / (df['koi_period'] * 24)
                
            if 'koi_depth' in df.columns and 'koi_model_snr' in df.columns:
                df['depth_snr_ratio'] = df['koi_depth'] / (df['koi_model_snr'] + 1e-6)
                
            # Habitability zone indicator
            if 'koi_insol' in df.columns:
                df['in_habitable_zone'] = ((df['koi_insol'] >= 0.36) & (df['koi_insol'] <= 1.1)).astype(int)
                
            # Stellar compactness
            if 'koi_smass' in df.columns and 'koi_srad' in df.columns:
                df['stellar_density'] = df['koi_smass'] / (df['koi_srad'] ** 3 + 1e-6)
                
            # Planet-star temperature ratio
            if 'koi_teq' in df.columns and 'koi_steff' in df.columns:
                df['temp_ratio'] = df['koi_teq'] / (df['koi_steff'] + 1e-6)
                
            # Log transformations for skewed features
            for col in ['koi_period', 'koi_depth', 'koi_insol', 'koi_prad']:
                if col in df.columns:
                    df[f'{col}_log'] = np.log1p(df[col].clip(lower=0))
                    
        elif dataset_type == 'tess':
            # Similar engineering for TESS
            if 'pl_rade' in df.columns and 'st_rad' in df.columns:
                df['radius_ratio'] = df['pl_rade'] / (df['st_rad'] * 109.076)
                
            if 'pl_orbper' in df.columns and 'pl_trandur' in df.columns:
                df['transit_duty_cycle'] = df['pl_trandur'] / (df['pl_orbper'] * 24)
                
            if 'pl_insol' in df.columns:
                df['in_habitable_zone'] = ((df['pl_insol'] >= 0.36) & (df['pl_insol'] <= 1.1)).astype(int)
                
            if 'st_mass' in df.columns and 'st_rad' in df.columns:
                df['stellar_density'] = df['st_mass'] / (df['st_rad'] ** 3 + 1e-6)
                
            for col in ['pl_orbper', 'pl_trandep', 'pl_insol', 'pl_rade']:
                if col in df.columns:
                    df[f'{col}_log'] = np.log1p(df[col].clip(lower=0))
                    
        return df
    
    def preprocess_kepler(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Preprocess Kepler data for ML"""
        df = self.engineer_features(df, 'kepler')
        
        # Get target variable
        label_col = 'koi_pdisposition' if 'koi_pdisposition' in df.columns else 'koi_disposition'
        df = df[df[label_col].notna()]
        
        # Map labels
        df['label'] = df[label_col].map(self.LABEL_MAPPING)
        df = df[df['label'].notna()]
        
        # Select features
        feature_cols = self.KEPLER_FEATURES.copy()
        
        # Add engineered features
        engineered = ['radius_ratio', 'transit_duty_cycle', 'depth_snr_ratio', 
                     'in_habitable_zone', 'stellar_density', 'temp_ratio']
        log_features = [f'{col}_log' for col in ['koi_period', 'koi_depth', 'koi_insol', 'koi_prad']]
        
        for col in engineered + log_features:
            if col in df.columns:
                feature_cols.append(col)
        
        # Keep only available features
        available_features = [col for col in feature_cols if col in df.columns]
        self.feature_names = available_features
        
        X = df[available_features].copy()
        y = df['label'].values
        
        # Replace infinities with NaN
        X = X.replace([np.inf, -np.inf], np.nan)
        
        # Drop columns that are entirely NaN
        valid_cols = X.columns[X.notna().any()].tolist()
        X = X[valid_cols]
        available_features = valid_cols
        self.feature_names = available_features
        
        # Use SimpleImputer for robust NaN handling
        imputer = SimpleImputer(strategy='median')
        X_imputed = imputer.fit_transform(X)
        
        # Final check - replace any remaining NaN with 0
        X_imputed = np.nan_to_num(X_imputed, nan=0.0, posinf=0.0, neginf=0.0)
        
        return X_imputed, y, available_features
    
    def preprocess_tess(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Preprocess TESS data for ML"""
        df = self.engineer_features(df, 'tess')
        
        # TESS uses tfopwg_disp for disposition
        label_col = 'tfopwg_disp'
        df = df[df[label_col].notna()]
        
        # Map labels
        df['label'] = df[label_col].map(self.LABEL_MAPPING)
        df = df[df['label'].notna()]
        
        # Select features
        feature_cols = self.TESS_FEATURES.copy()
        
        # Add engineered features
        engineered = ['radius_ratio', 'transit_duty_cycle', 'in_habitable_zone', 'stellar_density']
        log_features = [f'{col}_log' for col in ['pl_orbper', 'pl_trandep', 'pl_insol', 'pl_rade']]
        
        for col in engineered + log_features:
            if col in df.columns:
                feature_cols.append(col)
        
        available_features = [col for col in feature_cols if col in df.columns]
        self.feature_names = available_features
        
        X = df[available_features].copy()
        y = df['label'].values
        
        # Replace infinities with NaN
        X = X.replace([np.inf, -np.inf], np.nan)
        
        # Drop columns that are entirely NaN
        valid_cols = X.columns[X.notna().any()].tolist()
        X = X[valid_cols]
        available_features = valid_cols
        self.feature_names = available_features
        
        # Use SimpleImputer for robust NaN handling
        imputer = SimpleImputer(strategy='median')
        X_imputed = imputer.fit_transform(X)
        
        # Final check - replace any remaining NaN with 0
        X_imputed = np.nan_to_num(X_imputed, nan=0.0, posinf=0.0, neginf=0.0)
        
        return X_imputed, y, available_features
    
    def prepare_training_data(
        self,
        dataset: str = 'kepler',
        test_size: float = 0.2,
        balance_method: str = 'smote',
        random_state: int = 42
    ) -> Dict:
        """
        Prepare complete training dataset with balancing
        
        Args:
            dataset: 'kepler' or 'tess'
            test_size: Fraction for test split
            balance_method: 'smote', 'undersample', 'combined', or None
            random_state: Random seed
        """
        if dataset == 'kepler':
            df = self.fetch_kepler_data()
            X, y, features = self.preprocess_kepler(df)
        else:
            df = self.fetch_tess_data()
            X, y, features = self.preprocess_tess(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Balance training data
        if balance_method == 'smote':
            sampler = SMOTE(random_state=random_state)
            X_train_bal, y_train_bal = sampler.fit_resample(X_train, y_train)
        elif balance_method == 'undersample':
            sampler = RandomUnderSampler(random_state=random_state)
            X_train_bal, y_train_bal = sampler.fit_resample(X_train, y_train)
        elif balance_method == 'combined':
            pipeline = ImbPipeline([
                ('over', SMOTE(sampling_strategy=0.5, random_state=random_state)),
                ('under', RandomUnderSampler(sampling_strategy=0.8, random_state=random_state))
            ])
            X_train_bal, y_train_bal = pipeline.fit_resample(X_train, y_train)
        else:
            X_train_bal, y_train_bal = X_train, y_train
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_bal)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Training samples: {len(X_train_bal)}, Test samples: {len(X_test)}")
        logger.info(f"Class distribution (train): {np.bincount(y_train_bal.astype(int))}")
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train_bal,
            'y_test': y_test,
            'feature_names': features,
            'scaler': self.scaler,
            'n_classes': len(np.unique(y)),
            'class_names': ['False Positive', 'Candidate', 'Confirmed']
        }
    
    def transform_new_data(self, data: pd.DataFrame, dataset_type: str = 'kepler') -> np.ndarray:
        """Transform new data using fitted scaler"""
        if dataset_type == 'kepler':
            data = self.engineer_features(data, 'kepler')
        else:
            data = self.engineer_features(data, 'tess')
        
        # Select features that were used in training
        X = data[self.feature_names].copy()
        
        # Handle missing values
        for col in X.columns:
            if X[col].isna().any():
                X[col] = X[col].fillna(X[col].median())
        
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)
        
        return self.scaler.transform(X.values)


# Singleton instance
data_pipeline = NASAExoplanetDataPipeline()
