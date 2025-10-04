"""
Tests for preprocessing module.
"""
import pytest
import numpy as np
from core.preprocess import (
    normalize_flux,
    remove_outliers,
    detrend_light_curve,
    fold_light_curve,
    preprocess_pipeline,
    estimate_noise,
)


class TestPreprocess:
    """Test suite for preprocessing functions."""

    def test_normalize_flux_median(self):
        """Test median normalization."""
        flux = np.array([100, 101, 99, 100, 102])

        normalized = normalize_flux(flux, method="median")

        assert np.median(normalized) == pytest.approx(1.0, abs=0.01)

    def test_normalize_flux_polyfit(self):
        """Test polynomial detrending."""
        flux = np.array([100, 101, 102, 103, 104])

        normalized = normalize_flux(flux, method="polyfit")

        # Should remove trend
        assert len(normalized) == len(flux)

    def test_remove_outliers(self):
        """Test outlier removal."""
        time = np.arange(100)
        flux = np.random.normal(1.0, 0.01, 100)

        # Add outliers
        flux[10] = 2.0
        flux[50] = 0.5

        time_clean, flux_clean = remove_outliers(time, flux, sigma_clip=3.0)

        # Should remove outliers
        assert len(time_clean) < len(time)

    def test_detrend_light_curve(self):
        """Test detrending."""
        time = np.linspace(0, 10, 1000)

        # Flux with linear trend
        flux = 1.0 + 0.01 * time + np.random.normal(0, 0.001, 1000)

        detrended = detrend_light_curve(time, flux, window_hours=24)

        # Should be centered around 1.0
        assert np.abs(np.median(detrended) - 1.0) < 0.01

    def test_fold_light_curve(self):
        """Test phase folding."""
        time = np.linspace(0, 10, 100)
        flux = np.sin(2 * np.pi * time / 3.0) + 1.0  # Period = 3.0

        phase, flux_folded = fold_light_curve(time, flux, period=3.0, t0=0.0)

        # Check phase range
        assert np.all(phase >= -0.5)
        assert np.all(phase <= 0.5)

        # Check sorted
        assert np.all(np.diff(phase) >= 0)

    def test_estimate_noise_mad(self):
        """Test MAD noise estimation."""
        flux = np.random.normal(1.0, 0.01, 1000)

        noise = estimate_noise(flux, method="mad")

        assert noise == pytest.approx(0.01, abs=0.003)

    def test_estimate_noise_std(self):
        """Test std noise estimation."""
        flux = np.random.normal(1.0, 0.01, 1000)

        noise = estimate_noise(flux, method="std")

        assert noise == pytest.approx(0.01, abs=0.003)

    def test_preprocess_pipeline(self):
        """Test full preprocessing pipeline."""
        # Generate test data
        time = np.linspace(0, 10, 1000)
        flux = 100.0 * (1.0 + 0.01 * np.sin(2 * np.pi * time / 5.0))

        # Add noise
        flux += np.random.normal(0, 1.0, 1000)

        # Add outliers
        flux[100] = 200.0

        # Preprocess
        time_clean, flux_clean, flux_err_clean = preprocess_pipeline(
            time, flux, flux_err=None, sigma_clip=5.0
        )

        # Check results
        assert len(time_clean) < len(time)  # Outlier removed
        assert np.abs(np.median(flux_clean) - 1.0) < 0.1  # Normalized
        assert len(flux_err_clean) == len(flux_clean)  # Uncertainties provided


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
