"""Learner attempt lifecycle invariants under unvalidated recognition."""
import uuid

import pytest

from src.engine.assessment import assess_attempt
from src.engine.learner_model import learner_manager
from src.engine.storage import storage, StorageManager
from src.curriculum.curriculum import curriculum
from src.server.app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "signsense-test.db"
    StorageManager(str(test_db))
    monkeypatch.setattr(storage, "db_path", str(test_db))
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def isolate_storage_for_every_test(tmp_path, monkeypatch):
    # Several lifecycle tests write directly through the shared manager.
    test_db = tmp_path / "signsense-lifecycle-test.db"
    StorageManager(str(test_db))
    monkeypatch.setattr(storage, "db_path", str(test_db))


def prediction(label="1", status="uncertain"):
    return {
        "status": status,
        "predicted_sign": label,
        "raw_score": 0.88,
        "score_type": "unvalidated_template_similarity",
        "confidence": None,
        "diagnostics": {
            "hands_detected": 1,
            "primary_hand": {"landmarks_2d": [[0.5, 0.5]] * 21},
        },
    }


def observations(label="1", count=5):
    return [{"predicted_sign": label, "raw_score": 0.88,
             "score_type": "unvalidated_template_similarity",
             "inference_status": "uncertain", "hands_detected": 1}
            for _ in range(count)]


def test_target_match_stays_uncertain_and_never_awards_mastery():
    result = assess_attempt(prediction("1"), "1", observations=observations("1"))
    assert result["attempt_assessment"]["status"] == "UNCERTAIN"
    assert result["is_correct"] is False
    assert result["can_update_mastery"] is False
    assert result["model_evidence"]["calibrated_confidence"] is None


def test_wrong_candidate_is_reported_as_discrepancy_not_graded_incorrect():
    result = assess_attempt(prediction("2"), "1", observations=observations("2"))
    assert result["attempt_assessment"]["status"] == "UNCERTAIN"
    assert result["discrepancy"] is True
    assert result["is_correct"] is False
    assert result["can_update_mastery"] is False


def test_unvalidated_pose_heuristics_cannot_upgrade_candidate():
    pred = prediction("1")
    pred["diagnostics"]["accuracy_tier"] = "CORRECT"
    pred["diagnostics"]["primary_hand"]["palm_facing"] = "camera"
    result = assess_attempt(pred, "1", observations=observations("1"))
    assert result["attempt_assessment"]["status"] == "UNCERTAIN"
    assert result["pose_evidence"]["all_checks_passed"] is False


def test_insufficient_pose_and_no_hand_are_not_assessed():
    no_pose = prediction("1")
    no_pose["diagnostics"] = {"hands_detected": 1, "primary_hand": {}}
    result = assess_attempt(no_pose, "1", observations=observations("1"))
    assert result["attempt_assessment"]["status"] == "UNCERTAIN"
    no_hand = assess_attempt({"status": "no_hand_detected", "predicted_sign": None}, "1")
    assert no_hand["attempt_assessment"]["status"] == "NOT_ASSESSED"
    assert no_hand["can_update_mastery"] is False


def test_conflicting_candidates_remain_uncertain():
    mixed = observations("1", 2) + observations("2", 2)
    result = assess_attempt(prediction("1"), "1", observations=mixed)
    assert result["attempt_assessment"]["status"] == "UNCERTAIN"
    assert result["can_update_mastery"] is False


def test_inference_failure_does_not_reduce_mastery():
    storage.reset_learning_history()
    first = assess_attempt(prediction("1"), "1", observations=observations("1"))
    learner_manager.update_with_attempt(first, prediction("1"))
    sign_id = curriculum.get_sign_by_label("1")["id"]
    progress = storage.get_sign_progress(sign_id)
    progress["mastery_score"] = 0.4
    storage.save_sign_progress(progress)
    before = storage.get_sign_progress(sign_id)["mastery_score"]
    failed = {"status": "error", "predicted_sign": None, "confidence": None}
    assessment = assess_attempt(failed, "1")
    learner_manager.update_with_attempt(assessment, failed)
    assert storage.get_sign_progress(sign_id)["mastery_score"] == before


def test_retry_resets_temporal_stability(client):
    response = client.post("/api/recognize/reset_stability")
    assert response.status_code == 200
    assert response.get_json()["status"] == "reset"


def test_repeated_stable_target_candidates_never_create_verified_successes():
    storage.reset_learning_history()
    pred = prediction("1")
    result = assess_attempt(pred, "1", observations=observations("1"))
    for _ in range(3):
        update = learner_manager.update_with_attempt(result, pred)
    assert update["is_mastered"] is False
    assert update["consecutive_successes"] == 0
    progress = storage.get_sign_progress(curriculum.get_sign_by_label("1")["id"])
    assert progress["mastery_score"] == 0.0
    assert progress["confirmed_correct_count"] == 0


def test_duplicate_attempt_submission_is_idempotent(client):
    attempt_id = f"test_{uuid.uuid4().hex}"
    payload = {"attempt_id": attempt_id, "target_sign": "1",
               "prediction": prediction("1"), "observations": observations("1")}
    first = client.post("/api/assess", json=payload)
    second = client.post("/api/assess", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.get_json()["assessment"]["outcome"] == "uncertain"
    assert second.get_json()["status"] == "duplicate_ignored"
    assert len(storage.get_recent_attempts(10)) == 1


def test_prep_preview_does_not_create_attempt_records(client):
    before = len(storage.get_recent_attempts())
    assert client.get("/api/diagnostics").status_code == 200
    assert len(storage.get_recent_attempts()) == before


def test_api_feedback_persisted_assessment_and_learner_update_agree(client):
    response = client.post("/api/assess", json={
        "attempt_id": f"contract_{uuid.uuid4().hex}", "target_sign": "1",
        "prediction": prediction("1"), "observations": observations("1"),
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["assessment"]["attempt_assessment"]["status"] == "UNCERTAIN"
    assert data["assessment"]["is_correct"] is False
    assert data["learner_update"]["assessment"] == data["assessment"]
    saved = storage.get_recent_attempts(1)[0]
    assert saved["assessment"] == data["assessment"]
    assert saved["model_confidence"] is None
    assert saved["model_raw_score"] == 0.88
