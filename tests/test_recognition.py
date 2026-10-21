"""
Automated Unit Tests for Recognition Engine & Stability Buffer
Tests runtime robustness, error handling, invalid inputs, and temporal stabilization.
"""
import pytest
import numpy as np
import cv2
import os
from src.recognition.engine import RecognitionEngine
from src.recognition.stability import PredictionStabilizer
from src.recognition.diagnostics import PerformanceDiagnostics

@pytest.fixture
def test_engine():
    ref_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "static", "references")
    return RecognitionEngine(references_dir=ref_dir)

def test_empty_or_none_frame_handling(test_engine):
    """Engine must return structured error instead of crashing on empty frame."""
    res_none = test_engine.recognize_frame(None)
    assert res_none["status"] == "error"
    assert res_none["is_uncertain"] is True

    res_empty = test_engine.recognize_frame(np.array([]))
    assert res_empty["status"] == "error"

    res_wrong_shape = test_engine.recognize_frame(np.zeros((20, 20), dtype=np.uint8))
    assert res_wrong_shape["status"] == "error"
    assert res_wrong_shape["input_validity"] == "invalid_frame_shape"
    assert res_wrong_shape["predicted_sign"] is None

def test_no_hand_detected_on_blank_image(test_engine):
    """Blank/black image must return no_hand_detected status."""
    blank = np.zeros((200, 200, 3), dtype=np.uint8)
    res = test_engine.recognize_frame(blank, target_sign="1")
    assert res["status"] == "no_hand_detected"
    assert "visible" in res["message"].lower()

def test_reference_sign_1_recognition(test_engine):
    """Engine recognizes sign '1' from extracted reference demonstration image."""
    ref_1 = os.path.join("src", "static", "references", "1.jpg")
    assert os.path.exists(ref_1)
    img = cv2.imread(ref_1)
    res = test_engine.recognize_frame(img, target_sign="1")
    changed_target = test_engine.recognize_frame(img, target_sign="2")
    assert res["status"] == "uncertain"
    assert res["confidence"] is None
    assert "target_match" not in res
    assert res["predicted_sign"] == changed_target["predicted_sign"]
    assert res["raw_score"] == changed_target["raw_score"]
    assert res["latency_ms"] < 250.0  # Informational only; not an approved benchmark.

def test_stability_buffer_requires_consensus():
    """Stabilizer must require multiple consistent frames before confirming stable state."""
    stabilizer = PredictionStabilizer(window_size=6, min_consensus_ratio=0.65, min_frames=4)
    
    # 2 frames of 'A' -> accumulating (not enough frames)
    pred_a = {"status": "recognized", "predicted_sign": "A", "confidence": 0.8}
    r1 = stabilizer.add_prediction(pred_a)
    assert r1["is_stable"] is False
    assert r1["status"] == "accumulating"
    
    r2 = stabilizer.add_prediction(pred_a)
    assert r2["is_stable"] is False
    
    # 3rd frame is 'B' (fluctuation)
    pred_b = {"status": "recognized", "predicted_sign": "B", "confidence": 0.7}
    r3 = stabilizer.add_prediction(pred_b)
    assert r3["is_stable"] is False
    
    # 4th and 5th frames are 'A' -> total 5 frames: 4 'A's and 1 'B' = 80% consensus
    stabilizer.add_prediction(pred_a)
    r5 = stabilizer.add_prediction(pred_a)
    assert r5["is_stable"] is True
    assert r5["stable_sign"] == "A"
    assert r5["consensus_ratio"] >= 0.65

def test_diagnostics_metrics_calculation():
    """Diagnostics must compute FPS, prediction Hz, and latency stats."""
    diag = PerformanceDiagnostics(window_size=10)
    for i in range(5):
        diag.record_frame_received()
        diag.record_inference(latency_ms=10.0 + i)
        diag.record_assessment(latency_ms=2.0)
        diag.record_recommendation(latency_ms=1.5)
        
    metrics = diag.get_metrics()
    assert metrics["total_frames_received"] == 5
    assert metrics["total_predictions_made"] == 5
    assert metrics["avg_inference_latency_ms"] > 0
    assert metrics["avg_assessment_latency_ms"] == 2.0
    assert metrics["avg_recommendation_latency_ms"] == 1.5

def test_unvalidated_biomechanics_are_not_reported_as_assessment():
    """Pose rules have no independent validation and must be marked unavailable."""
    from src.recognition.pose_analyzer import pose_analyzer
    ref_1 = os.path.join("src", "static", "references", "1.jpg")
    ref_2 = os.path.join("src", "static", "references", "2.jpg")

    img_1 = cv2.imread(ref_1)
    img_2 = cv2.imread(ref_2)

    # Even reference images do not establish validation on held-out learners.
    pose_1 = pose_analyzer.analyze_frame(img_1)
    eval_1 = pose_analyzer.evaluate_sign_form("1", pose_1)
    assert eval_1["accuracy_tier"] in ("UNASSESSED", "NO_HAND")
    assert "confidence" not in eval_1

def test_stable_target_candidate_never_auto_verifies():
    """Temporal agreement is not validation and must never auto-grade."""
    stabilizer = PredictionStabilizer(window_size=8, hold_threshold_frames=5)
    pred_match = {
        "status": "recognized",
        "predicted_sign": "1",
        "target_match": True,
        "confidence": 0.95
    }

    # Agreement may stabilize the candidate, but the learner must submit and
    # the assessment remains uncertain until the model is independently validated.
    for i in range(8):
        res = stabilizer.add_prediction(pred_match)
        assert res["auto_verified"] is False
        assert res["hold_progress"] == 0.0
