import json
from unittest import mock

import pytest

from core.biosignature_modulus_workflow import (
    AtmosphericSnapshot,
    ModulusBiosignatureWorkflow,
)


@pytest.fixture
def mocked_workflow():
    workflow = ModulusBiosignatureWorkflow(base_url="http://dummy")
    with mock.patch.object(workflow.session, "post") as mock_post:
        yield workflow, mock_post


def _build_response(status: int, payload: dict):
    response = mock.Mock()
    response.status_code = status
    response.json.return_value = payload
    response.text = json.dumps(payload)
    return response


def test_compute_gas_disequilibrium_success(mocked_workflow):
    workflow, mock_post = mocked_workflow

    mock_post.return_value = _build_response(
        200,
        {
            "answer": "2.0",
            "confidence": 0.9,
            "trace_id": "123",
            "router": {"explanation": "log10 ratio"},
        },
    )

    result = workflow.compute_gas_disequilibrium({"CO2": 410, "CH4": 1.9})

    assert result.metric_name == "log10_CO2_CH4"
    assert pytest.approx(result.value) == 2.0
    assert result.confidence == 0.9
    assert result.trace_id == "123"
    assert "log10" in result.explanation


def test_compute_greenhouse_offset(mocked_workflow):
    workflow, mock_post = mocked_workflow

    mock_post.return_value = _build_response(
        200,
        {"answer": "33", "confidence": 1.0, "trace_id": "abc"},
    )

    snapshot = AtmosphericSnapshot(
        planet_name="Kepler-186f",
        stellar_flux_rel_solar=0.3,
        equilibrium_temperature_k=230.0,
        greenhouse_temperature_k=263.0,
    )

    result = workflow.compute_greenhouse_offset(snapshot)

    assert result.metric_name == "greenhouse_temperature_offset"
    assert pytest.approx(result.value) == 33.0
    assert result.confidence == 1.0


def test_run_composite_analysis_handles_missing_gases(mocked_workflow):
    workflow, mock_post = mocked_workflow

    mock_post.return_value = _build_response(200, {"answer": "10", "confidence": 0.5})

    snapshot = AtmosphericSnapshot(
        planet_name="PlanetX",
        stellar_flux_rel_solar=1.0,
        equilibrium_temperature_k=250.0,
        greenhouse_temperature_k=260.0,
        gas_mixing_ratios_ppm={"CO2": 100},
    )

    computations = workflow.run_composite_analysis(snapshot)

    assert len(computations) == 1
    assert computations[0].metric_name == "greenhouse_temperature_offset"


def test_compute_gas_disequilibrium_requires_gases(mocked_workflow):
    workflow, _ = mocked_workflow

    with pytest.raises(ValueError):
        workflow.compute_gas_disequilibrium({"CO2": 100})


