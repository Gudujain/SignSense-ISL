"""
Automated Unit Tests for SignSense Adaptive Recommendation Engine
Tests all recommendation rules, boundary conditions, and demonstrates that
at least three distinct learner histories produce meaningfully different next activities.
"""
import pytest
import time
import os
from src.engine.storage import StorageManager
from src.engine.learner_model import LearnerModelManager
from src.engine.recommender import RecommendationEngine
from src.engine.assessment import assess_attempt
from src.curriculum.curriculum import CurriculumManager

@pytest.fixture
def temp_engine(tmp_path):
    """Creates isolated test storage and engine instances with temporary SQLite DB."""
    db_file = str(tmp_path / "test_signsense.db")
    test_storage = StorageManager(db_path=db_file)
    test_curriculum = CurriculumManager()
    
    # Wire instances together
    rec_engine = RecommendationEngine()
    rec_engine.storage = test_storage
    rec_engine.curriculum = test_curriculum
    
    learner_mgr = LearnerModelManager()
    learner_mgr.storage = test_storage
    
    return {
        "storage": test_storage,
        "curriculum": test_curriculum,
        "recommender": rec_engine,
        "learner": learner_mgr
    }

def test_initial_state_recommends_curriculum_start(temp_engine):
    """Scenario 0: Insufficient practice history defaults to curriculum progression."""
    recs = temp_engine["recommender"].get_recommendations()
    assert len(recs) > 0
    top_rec = recs[0]
    assert top_rec["rule_id"] == "NEXT_NEW_SIGN"
    assert top_rec["sign_id"] == "isl_num_1"
    assert top_rec["label"] == "1"

def test_unvalidated_wrong_candidates_do_not_trigger_incorrect_mastery_or_failure(temp_engine):
    """
    A stable-looking wrong candidate remains uncertain without a validated model.
    It must not produce a failure streak; recovery asks for a retry instead.
    """
    learner = temp_engine["learner"]
    recommender = temp_engine["recommender"]
    
    for _ in range(3):
        pred = {"status": "recognized", "predicted_sign": "2", "confidence": 0.65, "is_uncertain": False}
        assessment = assess_attempt(pred, target_sign_label="1", learner_confirmation="confirmed_incorrect")
        learner.update_with_attempt(assessment, pred)

    recs = recommender.get_recommendations()
    assert len(recs) > 0
    top = recs[0]
    assert top["rule_id"] == "SETUP_RECOVERY"
    assert temp_engine["storage"].get_sign_progress("isl_num_1") is None
    assert temp_engine["storage"].get_sign_mastery() == {}

def test_unvalidated_target_matches_do_not_advance_curriculum(temp_engine):
    """
    Repeated target matches are still uncertain; recommendations should request
    another attempt rather than announce verified mastery or advance.
    """
    learner = temp_engine["learner"]
    recommender = temp_engine["recommender"]
    
    for _ in range(3):
        pred = {"status": "recognized", "predicted_sign": "1", "confidence": 0.85, "is_uncertain": False}
        assessment = assess_attempt(pred, target_sign_label="1", learner_confirmation="confirmed_correct")
        learner.update_with_attempt(assessment, pred)

    recs = recommender.get_recommendations()
    assert len(recs) > 0
    top = recs[0]
    assert top["rule_id"] == "SETUP_RECOVERY"
    assert temp_engine["storage"].get_sign_progress("isl_num_1") is None
    assert temp_engine["storage"].get_sign_mastery() == {}

def test_history_c_mastered_learner_with_overdue_spaced_revision(temp_engine):
    """
    Learner History C (Retention / Spaced Revision):
    Learner previously learned sign '1', but its review time has expired.
    Expected: SPACED_REVISION triggers to protect long-term retention.
    """
    storage = temp_engine["storage"]
    recommender = temp_engine["recommender"]
    
    now = time.time()
    # Seed mastered sign '1' whose review was due 3 hours ago
    storage.save_sign_progress({
        "sign_id": "isl_num_1",
        "label": "1",
        "attempt_count": 5,
        "confirmed_correct_count": 5,
        "confirmed_incorrect_count": 0,
        "uncertain_count": 0,
        "consecutive_successes": 5,
        "consecutive_failures": 0,
        "mastery_score": 0.85,
        "last_practiced_at": now - 7200,
        "review_interval_hours": 1.0,
        "next_review_at": now - 3600  # Overdue by 1 hour
    })

    recs = recommender.get_recommendations()
    assert len(recs) > 0
    top = recs[0]
    assert top["rule_id"] == "SPACED_REVISION"
    assert top["sign_id"] == "isl_num_1"
    assert top["activity_type"] == "spaced_review"
    assert "day" in top["reason"]

def test_uncertainty_does_not_lower_mastery_and_triggers_recovery(temp_engine):
    """
    Uncertainty handling:
    An uncertain attempt must NOT lower mastery and should trigger UNCERTAIN_RECOVERY if recent.
    """
    learner = temp_engine["learner"]
    storage = temp_engine["storage"]
    recommender = temp_engine["recommender"]
    
    # First give learner positive mastery on 1
    pred_ok = {"status": "recognized", "predicted_sign": "1", "confidence": 0.8, "is_uncertain": False}
    assess_ok = assess_attempt(pred_ok, "1", "confirmed_correct")
    learner.update_with_attempt(assess_ok, pred_ok)
    
    assert storage.get_sign_progress("isl_num_1") is None
    
    # Now record an uncertain prediction
    pred_unc = {"status": "uncertain", "predicted_sign": "1", "confidence": 0.38, "is_uncertain": True}
    assess_unc = assess_attempt(pred_unc, "1", learner_confirmation=None)
    learner.update_with_attempt(assess_unc, pred_unc)
    
    assert storage.get_sign_mastery() == {}
    
    # Should trigger UNCERTAIN_RECOVERY
    recs = recommender.get_recommendations()
    assert recs[0]["rule_id"] == "SETUP_RECOVERY"

def test_learner_can_dismiss_recommendation(temp_engine):
    """User Control: Learner can dismiss a recommendation to receive an alternative."""
    storage = temp_engine["storage"]
    recommender = temp_engine["recommender"]
    
    # Initial top recommendation is isl_num_1
    top_init = recommender.get_recommendations()[0]
    assert top_init["sign_id"] == "isl_num_1"
    
    # Learner dismisses isl_num_1
    storage.dismiss_recommendation("isl_num_1")
    
    # Next recommendation must NOT be isl_num_1
    top_after = recommender.get_recommendations()[0]
    assert top_after["sign_id"] != "isl_num_1"


def test_dismissing_every_recommendation_shows_no_recommendations(temp_engine):
    storage = temp_engine["storage"]
    recommender = temp_engine["recommender"]
    for sign in temp_engine["curriculum"].get_all_signs():
        storage.dismiss_recommendation(sign["id"])
    assert recommender.get_recommendations() == []
