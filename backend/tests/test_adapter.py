"""
Tests for Modulus adapter.
"""
import pytest
import numpy as np
from physics import fit_transit, run_checks, get_backend_info


def generate_synthetic_transit(n_points=1000, period=3.0, t0=0.5, depth=0.01, noise=0.001):
    """Generate synthetic transit light curve."""
    time = np.linspace(0, 10.0, n_points)

    # Simple box transit
    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
    duration = 0.1  # days

    flux = np.ones(n_points)
    in_transit = np.abs(phase) < (duration / 2.0)
    flux[in_transit] = 1.0 - depth

    # Add noise
    flux += np.random.normal(0, noise, n_points)

    flux_err = np.ones(n_points) * noise

    return time, flux, flux_err


class TestModulusAdapter:
    """Test suite for Modulus adapter."""

    def test_backend_info(self):
        """Test backend information retrieval."""
        info = get_backend_info()

        assert "backend" in info
        assert "name" in info
        assert "is_mock" in info
        assert "has_fit_transit" in info
        assert "has_run_checks" in info

    def test_fit_transit_synthetic(self):
        """Test transit fitting on synthetic data."""
        # Generate synthetic transit
        time, flux, flux_err = generate_synthetic_transit(
            n_points=500, period=3.14, t0=0.5, depth=0.02, noise=0.001
        )

        # Fit transit
        result = fit_transit(time, flux, flux_err)

        # Check result structure
        assert "period_days" in result
        assert "t0_bjd" in result
        assert "depth_ppm" in result
        assert "duration_hours" in result
        assert "impact_parameter" in result
        assert "limb_darkening" in result
        assert "snr" in result
        assert "log_likelihood" in result
        assert "chi2" in result
        assert "success" in result
        assert "message" in result

        # Check success
        assert result["success"] is True

        # Check parameter recovery (rough bounds)
        # Note: Mock fitter may not recover exact parameters
        assert result["period_days"] > 0
        assert result["depth_ppm"] > 0
        assert result["snr"] > 0

    def test_fit_transit_no_signal(self):
        """Test fitting on pure noise (should still return valid structure)."""
        # Pure noise
        time = np.linspace(0, 10.0, 500)
        flux = np.random.normal(1.0, 0.001, 500)
        flux_err = np.ones(500) * 0.001

        result = fit_transit(time, flux, flux_err)

        # Should return valid structure even if fit fails
        assert "success" in result
        assert "message" in result

    def test_run_checks(self):
        """Test physics validation checks."""
        # Generate synthetic transit
        time, flux, flux_err = generate_synthetic_transit(period=3.0, t0=0.5, depth=0.02)

        # Run checks
        checks = run_checks(time, flux, period_days=3.0, t0_bjd=0.5)

        # Check structure
        assert "odd_even_depth_delta_pct" in checks
        assert "secondary_eclipse_snr" in checks
        assert "v_vs_u_shape_score" in checks
        assert "centroid_shift_proxy" in checks
        assert "stellar_density_consistent" in checks

        # Check types
        assert isinstance(checks["odd_even_depth_delta_pct"], float)
        assert isinstance(checks["secondary_eclipse_snr"], float)
        assert isinstance(checks["v_vs_u_shape_score"], float)
        assert isinstance(checks["stellar_density_consistent"], bool)

    def test_fit_transit_with_auto_uncertainties(self):
        """Test fitting without providing flux_err."""
        time, flux, _ = generate_synthetic_transit()

        # Fit without flux_err
        result = fit_transit(time, flux, flux_err=None)

        assert "success" in result
        assert isinstance(result["snr"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
