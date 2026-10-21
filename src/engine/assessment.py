"""Conservative attempt assessment from observed model predictions.

The active candidate generator emits only an uncalibrated raw score; it cannot
by itself verify a learner's sign.
"""
from collections import Counter
from typing import Any, Dict, List, Optional


def assess_attempt(prediction_result: Dict[str, Any], target_sign_label: str,
                   learner_confirmation: Optional[str] = None,
                   observations: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    target = str(target_sign_label).upper()
    obs = observations or []
    valid = [o for o in obs if o.get("inference_status") in ("recognized", "uncertain", "partially_correct")
             and o.get("predicted_sign") and o.get("hands_detected", 0) > 0]
    preds = [str(o["predicted_sign"]).upper() for o in valid]
    counts = Counter(preds)
    winner, count = counts.most_common(1)[0] if counts else (None, 0)
    stability = count / len(preds) if preds else 0.0
    min_observations = 3
    raw_score = prediction_result.get("raw_score", prediction_result.get("confidence"))
    try:
        raw_score = float(raw_score) if raw_score is not None else None
    except (TypeError, ValueError):
        raw_score = None
    diagnostics = prediction_result.get("diagnostics") or {}
    primary = diagnostics.get("primary_hand") or {}
    landmarks_ok = len(primary.get("landmarks_2d") or []) >= 21
    has_pose = bool(valid) and landmarks_ok
    checks = {
        "hand_visible": {"status": "passed" if valid else "unavailable"},
        "landmarks": {"status": "passed" if has_pose else "unavailable"},
        "finger_configuration": {"status": "unavailable"},
        "palm_orientation": {"status": "unavailable"},
    }
    status_code = str(prediction_result.get("status", "error"))
    final_status = "UNCERTAIN"
    reason = "I couldn't confidently distinguish the sign. Review the reference and try again."
    action = "review_reference"

    if status_code == "error" or not valid:
        final_status = "NOT_ASSESSED"
        reason = "I couldn't assess this attempt because hand tracking or model inference was unavailable. Reposition your hand and retry."
        action = "reposition_hand"
    elif len(valid) < min_observations:
        reason = f"Only {len(valid)} valid observations were available; at least {min_observations} are needed for a stable assessment. Please retry."
    elif stability < 0.8:
        reason = f"Predictions varied across the attempt ({stability:.0%} agreement). Hold the sign steady and try again."
        action = "hold_steady"
    elif not has_pose:
        reason = "The prediction was stable, but pose evidence was unavailable, so this attempt has not been marked correct or incorrect."
    else:
        # There is no labeled participant/session-held-out evaluation for this
        # pipeline, and no pose check has independent validation. A stable
        # candidate therefore cannot be promoted to a learner outcome.
        relation = "matches" if winner == target else f"differs from {target} (candidate: {winner})"
        reason = (f"The model's candidate {relation}, but this prototype has not been validated "
                  "to assess correctness. Compare with the reference; this attempt is not graded.")
        action = "review_reference"

    model_evidence = {
        "predicted_class": winner,
        "raw_score": round(raw_score, 3) if raw_score is not None else None,
        "score_type": prediction_result.get("score_type", "unavailable") if raw_score is not None else "unavailable",
        "is_calibrated": False,
        "calibrated_confidence": None,
        "prediction_stability": round(stability, 2),
        "supported_class": winner is not None,
        "inference_failed": status_code == "error",
        "observation_count": len(valid),
        "minimum_observations": min_observations,
    }
    pose_evidence = {
        "hand_visible": bool(valid), "sufficient_landmarks": has_pose,
        "finger_states": primary.get("finger_states", {}),
        "palm_orientation": None, "validated_checks": checks,
        "all_checks_passed": False,
    }
    is_correct = False
    uncertain = final_status in ("UNCERTAIN", "NOT_ASSESSED")
    assessment = {
        "target_sign": target, "predicted_sign": winner,
        "sufficient_evidence": not uncertain, "is_stable": stability >= 0.8,
        "status": final_status, "explanation": reason,
        "suggested_action": action, "can_update_mastery": not uncertain,
        "is_correct": is_correct, "is_uncertain": uncertain,
        "discrepancy": bool(winner and winner != target),
        "feedback_message": reason,
        "failure_source": "system" if final_status == "NOT_ASSESSED" else "learner",
    }
    outcome = {"CORRECT": "correct", "INCORRECT": "incorrect",
               "UNCERTAIN": "uncertain", "NOT_ASSESSED": "not_assessed"}[final_status]
    return {
        "model_evidence": model_evidence, "pose_evidence": pose_evidence,
        "attempt_assessment": assessment, "outcome": outcome,
        "target_sign": target, "predicted_sign": winner,
        "learner_confirmation": learner_confirmation,
        "is_correct": is_correct, "is_uncertain": uncertain,
        "discrepancy": assessment["discrepancy"],
        "can_update_mastery": assessment["can_update_mastery"],
        "feedback_message": reason,
    }
