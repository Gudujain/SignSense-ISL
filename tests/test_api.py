"""
Automated Integration Tests for SignSense REST API
Validates all endpoints, payload schemas, error handling, and assessment flows.
"""
import pytest
import json
import base64
import numpy as np
import cv2
from src.server.app import app
from src.engine.storage import storage
from src.engine.storage import StorageManager

@pytest.fixture
def client(tmp_path, monkeypatch):
    # Never let integration tests clear or modify a learner's real signsense.db.
    test_db = tmp_path / "signsense-test.db"
    StorageManager(str(test_db))
    monkeypatch.setattr(storage, "db_path", str(test_db))
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Root route must serve the web application."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"SignSense" in res.data

def test_curriculum_endpoint(client):
    """Curriculum API exposes prototype labels without claiming verification."""
    res = client.get("/api/curriculum")
    assert res.status_code == 200
    data = res.get_json()
    assert "signs" in data
    assert "stages" in data
    assert len(data["signs"]) == 35
    assert len(data["stages"]) == 6
    assert all(sign["recognition_supported"] is False for sign in data["signs"])
    assert all(sign["instruction_status"] == "not_independently_reviewed" for sign in data["signs"])

def test_curriculum_single_sign_endpoint(client):
    """Legacy instruction data is explicitly marked unverified."""
    res = client.get("/api/curriculum/isl_num_1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["label"] == "1"
    assert data["instruction_status"] == "not_independently_reviewed"

def test_learner_progress_endpoint(client):
    """Progress endpoint returns real calculated statistics."""
    res = client.get("/api/learner/progress")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_curriculum_signs"] == 35
    assert "assessed_correct_attempts" in data
    assert "consistency_rate" not in data

def test_recommendations_endpoint(client):
    """Recommendations API returns prioritized, explainable activities."""
    res = client.get("/api/recommendations")
    assert res.status_code == 200
    data = res.get_json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    top = data["recommendations"][0]
    assert "rule_id" in top
    assert "explanation" in top

def test_recognize_endpoint_with_blank_image(client):
    """Recognize endpoint safely handles blank frame with no_hand_detected."""
    blank = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", blank)
    b64_str = base64.b64encode(buffer).decode("utf-8")

    res = client.post("/api/recognize", json={
        "frame": b64_str,
        "target_sign": "1"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["raw_prediction"]["status"] == "no_hand_detected"
    assert "stability" in data

def test_assess_and_feedback_flow(client):
    """An unevaluated camera prediction remains uncertain through the API."""
    raw_pred = {
        "status": "recognized",
        "predicted_sign": "1",
        "confidence": 0.88,
        "is_uncertain": False,
        "latency_ms": 5.2
    }
    res = client.post("/api/assess", json={
        "prediction": raw_pred,
        "target_sign": "1",
        "learner_confirmation": "confirmed_correct"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["assessment"]["outcome"] == "not_assessed"
    assert data["assessment"]["is_correct"] is False
    assert data["learner_update"]["consecutive_successes"] == 0
    assert data["learner_update"]["assessment"] == data["assessment"]
    assert "next_recommendations" in data

def test_diagnostics_endpoint(client):
    """Diagnostics endpoint returns real-time latency and FPS targets."""
    res = client.get("/api/diagnostics")
    assert res.status_code == 200
    data = res.get_json()
    assert "camera_fps" in data
    assert "avg_inference_latency_ms" in data
    assert "targets" in data

def test_history_clear_endpoint(client):
    """Clear history endpoint resets attempts and mastery state."""
    res = client.post("/api/history/clear")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "cleared"
