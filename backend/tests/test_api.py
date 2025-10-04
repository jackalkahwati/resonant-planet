"""
API endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app
from core.settings import settings

client = TestClient(app)


class TestAPI:
    """Test suite for API endpoints."""

    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "status" in data

    def test_health(self):
        """Test health check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"

    def test_list_datasets_empty(self):
        """Test listing datasets when none exist."""
        response = client.get("/api/datasets/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_list_datasets_with_demos(self):
        """Test listing demo datasets."""
        # Ensure demo datasets exist
        demo_dir = settings.base_dir / settings.demo_datasets_path
        demo_dir.mkdir(parents=True, exist_ok=True)

        # Create a test demo file
        test_demo = demo_dir / "test_demo.csv"
        df = pd.DataFrame({"time": [0, 1, 2], "flux": [1.0, 0.99, 1.0], "flux_err": [0.01, 0.01, 0.01]})
        df.to_csv(test_demo, index=False)

        response = client.get("/api/datasets/")

        assert response.status_code == 200
        data = response.json()

        # Clean up
        test_demo.unlink(missing_ok=True)

    def test_upload_dataset(self):
        """Test uploading a dataset."""
        # Create test CSV
        test_data = "time,flux,flux_err\n0.0,1.0,0.01\n1.0,0.99,0.01\n2.0,1.0,0.01\n"

        files = {"file": ("test.csv", test_data, "text/csv")}

        response = client.post("/api/datasets/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        assert "dataset_id" in data
        assert "message" in data

    def test_upload_invalid_file(self):
        """Test uploading non-CSV file."""
        files = {"file": ("test.txt", "not a csv", "text/plain")}

        response = client.post("/api/datasets/upload", files=files)

        assert response.status_code == 400

    def test_get_status_not_found(self):
        """Test getting status for non-existent job."""
        response = client.get("/api/status/nonexistent")

        assert response.status_code == 404

    def test_get_results_not_found(self):
        """Test getting results for non-existent job."""
        response = client.get("/api/results/nonexistent")

        assert response.status_code == 404

    def test_compare_methods(self):
        """Test method comparison endpoint."""
        response = client.post(
            "/api/compare/",
            json={
                "candidate_ids": ["test_1", "test_2"],
                "baseline_id": "baseline_ref",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        # Check structure
        for comparison in data:
            assert "candidate_id" in comparison
            assert "baseline" in comparison
            assert "resonant" in comparison
            assert "improvement_factor" in comparison


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
