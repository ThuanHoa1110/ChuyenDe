"""
Comprehensive Test Suite for FastAPI Weather Inference Service (Phase 4, Step 4.1).
Covers:
1. GET /health status 200 and diagnostic payload.
2. GET /metadata schema, stations, lookback/horizon, and metrics.
3. POST /predict with valid payload returning 6 finite station temperatures.
4. Numerical equivalence test: Compares API output directly with raw model forward pass.
5. Rejection (HTTP 422) for at least 5 invalid payloads:
   - Wrong timestep count (e.g. 50 instead of 72)
   - Invalid / incomplete / wrong-order station IDs
   - Non-monotonic timestamps / irregular interval
   - Missing required feature column in dict data
   - Invalid 2D matrix shape
   - end_timestamp mismatch with series final timestamp
"""

import os
import json
import copy
import datetime
import pytest
import numpy as np
import torch
from fastapi.testclient import TestClient

from src.weather.api.app import app, state, CANONICAL_STATIONS, LOOKBACK_STEPS
from src.weather.data.image import window_to_3channel_matrix, resize_matrix_bilinear

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_PATH = os.path.join(BASE_DIR, "docs", "api_example.json")


@pytest.fixture(scope="module")
def client():
    """Initializes FastAPI TestClient within lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def valid_payload():
    """Loads canonical valid sample payload from docs/api_example.json."""
    assert os.path.exists(EXAMPLE_PATH), f"Missing docs/api_example.json at {EXAMPLE_PATH}"
    with open(EXAMPLE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# ---------------------------------------------------------
# 1. Health & Metadata Endpoints
# ---------------------------------------------------------

def test_health_endpoint(client):
    """Checks GET /health returns 200 OK and valid health indicators."""
    response = client.get("/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"
    body = response.json()
    assert body["status"] in ("healthy", "degraded")
    assert body["model_loaded"] is True
    assert body["scaler_loaded"] is True
    assert body["uptime_seconds"] >= 0.0
    assert "device" in body
    assert "timestamp" in body


def test_metadata_endpoint(client):
    """Checks GET /metadata returns correct station list, lookback, horizon, and metrics."""
    response = client.get("/metadata")
    assert response.status_code == 200, f"Metadata query failed: {response.text}"
    body = response.json()
    assert body["model_name"] == "DINOv3Forecaster"
    assert body["model_version"] == "v1.0.0"
    assert body["lookback_steps"] == 72
    assert body["lookback_hours"] == 6
    assert body["horizon_steps"] == 12
    assert body["horizon_minutes"] == 60
    assert body["num_features"] == 66
    assert len(body["stations"]) == 6
    assert len(body["feature_order"]) == 66

    station_ids = [s["id"] for s in body["stations"]]
    assert station_ids == CANONICAL_STATIONS

    # Check metrics present
    metrics = body["metrics_summary"]
    assert "dinov3_macro_mae" in metrics
    assert "persistence_macro_mae" in metrics
    assert "ridge_macro_mae" in metrics


# ---------------------------------------------------------
# 2. Valid Prediction & Equivalence with Direct Model Call
# ---------------------------------------------------------

def test_valid_prediction_dict_payload(client, valid_payload):
    """Verifies that a valid 72-step dictionary payload returns 200 and 6 finite forecasts."""
    response = client.post("/predict", json=valid_payload)
    assert response.status_code == 200, f"Prediction failed: {response.text}"
    res = response.json()

    assert res["status"] == "success"
    assert res["horizon_steps"] == 12
    assert res["horizon_minutes"] == 60
    assert res["units"] == "°C"
    assert res["latency_ms"] > 0

    preds = res["predictions"]
    assert len(preds) == 6
    for st, temp_val in preds.items():
        assert isinstance(temp_val, (int, float)), f"Non-numeric forecast for {st}: {temp_val}"
        assert np.isfinite(temp_val), f"Non-finite forecast for {st}: {temp_val}"
        # Reasonable physical range for Hanoi: 0°C to 50°C
        assert -5.0 <= temp_val <= 60.0, f"Unreasonable physical temperature for {st}: {temp_val}°C"


def test_valid_prediction_matrix_payload(client, valid_payload):
    """Verifies that 2D matrix format (72 rows x 66 columns) is accepted and outputs 6 finite forecasts."""
    matrix_payload = copy.deepcopy(valid_payload)
    features = state.canonical_features

    # Convert dict to 2D matrix: 72 rows x 66 cols
    raw_matrix = []
    for t_idx in range(LOOKBACK_STEPS):
        row = [matrix_payload["data"][col][t_idx] for col in features]
        raw_matrix.append(row)
    matrix_payload["data"] = raw_matrix

    response = client.post("/predict", json=matrix_payload)
    assert response.status_code == 200, f"Matrix prediction failed: {response.text}"
    res = response.json()
    assert res["status"] == "success"
    assert len(res["predictions"]) == 6
    for st, val in res["predictions"].items():
        assert np.isfinite(val)


def test_api_prediction_matches_direct_model_inference(client, valid_payload):
    """
    Direct Model Equivalence Test:
    Ensures that calling the REST API produces results numerically equivalent
    to calling the model directly in Python with the same normalized input.
    """
    # 1. Direct Model Inference
    features = state.canonical_features
    raw_matrix = np.empty((LOOKBACK_STEPS, len(features)), dtype=np.float32)
    for c_idx, col in enumerate(features):
        raw_matrix[:, c_idx] = valid_payload["data"][col]

    scaled_matrix = state.scaler.transform(raw_matrix).astype(np.float32)
    mat_3ch = window_to_3channel_matrix(scaled_matrix, features)
    img_np = resize_matrix_bilinear(mat_3ch, target_size=(224, 224))
    img_tensor = torch.from_numpy(img_np).unsqueeze(0).to(state.device)

    state.model.eval()
    with torch.no_grad():
        direct_preds = state.model(img_tensor).cpu().numpy().squeeze(0)  # Shape (6,)

    # 2. REST API Call
    response = client.post("/predict", json=valid_payload)
    assert response.status_code == 200
    api_preds = np.array(list(response.json()["predictions"].values()))

    # Round direct_preds to 2 decimals as API does
    direct_preds_rounded = np.round(direct_preds, 2)

    # 3. Assert Equivalence
    np.testing.assert_allclose(
        api_preds,
        direct_preds_rounded,
        atol=1e-2,
        err_msg="API predictions do not match direct model inference output!"
    )


# ---------------------------------------------------------
# 3. Rejection of Invalid Payloads (HTTP 422)
# ---------------------------------------------------------

def test_invalid_payload_wrong_timesteps_count(client, valid_payload):
    """Rejects payload with 50 timesteps instead of required 72."""
    bad_payload = copy.deepcopy(valid_payload)
    bad_payload["timestamps"] = bad_payload["timestamps"][:50]
    for col in bad_payload["data"]:
        bad_payload["data"][col] = bad_payload["data"][col][:50]
    bad_payload["end_timestamp"] = bad_payload["timestamps"][-1]

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    assert "72 timesteps" in response.json()["detail"]


def test_invalid_payload_wrong_station_ids(client, valid_payload):
    """Rejects payload with only 5 stations or wrong station order."""
    bad_payload = copy.deepcopy(valid_payload)
    # Remove station 6
    bad_payload["station_ids"] = ["st01", "st02", "st03", "st04", "st05"]

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    assert "station_ids must contain exactly 6 stations" in response.json()["detail"]

    # Wrong order
    bad_payload["station_ids"] = ["st06", "st05", "st04", "st03", "st02", "st01"]
    response2 = client.post("/predict", json=bad_payload)
    assert response2.status_code == 422
    assert "station_ids at index 0 must be 'st01'" in response2.json()["detail"]


def test_invalid_payload_non_monotonic_timestamps(client, valid_payload):
    """Rejects payload where timestamps are reversed or not strictly monotonic."""
    bad_payload = copy.deepcopy(valid_payload)
    # Reverse timestamps
    bad_payload["timestamps"] = list(reversed(bad_payload["timestamps"]))
    bad_payload["end_timestamp"] = bad_payload["timestamps"][-1]

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    assert "strictly monotonically increasing" in response.json()["detail"]


def test_invalid_payload_missing_required_column(client, valid_payload):
    """Rejects payload missing a required meteorological feature column."""
    bad_payload = copy.deepcopy(valid_payload)
    # Remove st01_temperature
    del bad_payload["data"]["st01_temperature"]

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    assert "Missing required meteorological feature column: 'st01_temperature'" in response.json()["detail"]


def test_invalid_payload_matrix_dimension_mismatch(client, valid_payload):
    """Rejects 2D matrix payload with incorrect column dimension (e.g. 50 instead of 66)."""
    bad_payload = copy.deepcopy(valid_payload)
    # Matrix of 72 rows x 50 columns
    bad_payload["data"] = [[20.0] * 50 for _ in range(LOOKBACK_STEPS)]

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    assert "must have exactly 66 columns" in response.json()["detail"]


def test_invalid_payload_end_timestamp_mismatch(client, valid_payload):
    """Rejects payload where end_timestamp does not equal timestamps[-1]."""
    bad_payload = copy.deepcopy(valid_payload)
    bad_payload["end_timestamp"] = "2026-11-06T12:00:00Z"  # Different from timestamps[-1]

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    assert "end_timestamp" in response.json()["detail"]
    assert "does not match the final timestamp" in response.json()["detail"]
