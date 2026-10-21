"""
SignSense Web Application Server
Serves the responsive HCI learning interface and local REST API.
Uses local persistence and on-device computer vision; camera frames are processed by the local server and not persisted.
"""
import os
import sys
import time
from flask import Flask, request, jsonify, send_from_directory, send_file

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.curriculum.curriculum import curriculum
from src.recognition.engine import engine
from src.recognition.stability import PredictionStabilizer
from src.recognition.browser_attempt import assess_landmark_window
from src.recognition.local_hand_tracker import close as close_local_hand_tracker, detect_data_url, initialize as initialize_local_hand_tracker
from src.recognition.diagnostics import diagnostics
from src.engine.assessment import assess_attempt
from src.engine.learner_model import learner_manager
from src.engine.recommender import recommender
from src.engine.storage import storage
from src.engine.demo_seed import seed_demo_history
from src.ml.diagnostics import record_inference_diagnostic

app = Flask(__name__, static_folder="../static", static_url_path="/static")
stabilizer = PredictionStabilizer(window_size=8, min_consensus_ratio=0.65, min_frames=5)
# Recognition remains unvalidated until independent participant-held-out results exist.
RECOGNITION_VALIDATED = False

# -------------------------------------------------------------
# Frontend Entry Point
# -------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# -------------------------------------------------------------
# Curriculum Endpoints
# -------------------------------------------------------------
@app.route("/api/curriculum", methods=["GET"])
def get_curriculum():
    return jsonify({
        "summary": curriculum.get_summary(),
        "stages": curriculum.get_stages(),
        "signs": curriculum.get_all_signs()
    })

@app.route("/api/curriculum/<sign_id>", methods=["GET"])
def get_curriculum_sign(sign_id):
    sign = curriculum.get_sign_by_id(sign_id)
    if not sign:
        return jsonify({"error": "Sign not found"}), 404
    return jsonify(sign)

# -------------------------------------------------------------
# Learner Profile & Progress
# -------------------------------------------------------------
@app.route("/api/learner/profile", methods=["GET"])
def get_profile():
    return jsonify(storage.get_profile() or {})

@app.route("/api/learner/profile", methods=["POST"])
def update_profile():
    data = request.json or {}
    curr = storage.get_profile() or {}
    profile = {
        "id": curr.get("id", "default_learner"),
        "goal": data.get("goal", curr.get("goal", "basics")),
        "skill_level": data.get("skill_level", curr.get("skill_level", "beginner")),
        "research_consent": 1 if data.get("research_consent", curr.get("research_consent", 0)) else 0,
        "save_progress": 1 if data.get("save_progress", curr.get("save_progress", 1)) else 0,
        "dominant_hand": data.get("dominant_hand", curr.get("dominant_hand", "right")),
        "text_size": data.get("text_size", curr.get("text_size", "regular")),
        "daily_goal": max(1, min(100, int(data.get("daily_goal", curr.get("daily_goal", 10))))),
        "reduced_motion": int(bool(data.get("reduced_motion", curr.get("reduced_motion", 0)))),
        "high_contrast": int(bool(data.get("high_contrast", curr.get("high_contrast", 0)))),
        "color_blind_palette": int(bool(data.get("color_blind_palette", curr.get("color_blind_palette", 0)))),
        "larger_targets": int(bool(data.get("larger_targets", curr.get("larger_targets", 0)))),
        "caption_cues": int(bool(data.get("caption_cues", curr.get("caption_cues", 1)))),
        "camera_default": str(data.get("camera_default", curr.get("camera_default", "")))[:256],
        "mirror_view": int(bool(data.get("mirror_view", curr.get("mirror_view", 1)))),
        "color_theme": data.get("color_theme", curr.get("color_theme", "system")) if data.get("color_theme", curr.get("color_theme", "system")) in {"system", "light", "dark"} else "system",
        "created_at": curr.get("created_at", time.time()),
        "updated_at": time.time()
    }
    storage.save_profile(profile)
    return jsonify({"status": "success", "profile": profile})

@app.route("/api/learner/progress", methods=["GET"])
def get_progress():
    summary = learner_manager.get_progress_summary(demo=request.args.get("demo") == "1")
    summary["recent_attempts"] = storage.get_recent_attempts(100000, demo=request.args.get("demo") == "1")
    summary["daily_goal"] = int((storage.get_profile() or {}).get("daily_goal", 10))
    return jsonify(summary)

@app.route("/api/learner/export", methods=["GET"])
def export_learner_data():
    return jsonify({"profile": storage.get_profile() or {},
                    "attempts": storage.get_recent_attempts(100000),
                    "mastery": storage.get_sign_mastery(),
                    "sessions": storage.get_sessions() if hasattr(storage, "get_sessions") else []})

# -------------------------------------------------------------
# Adaptive Recommendations
# -------------------------------------------------------------
@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    demo = request.args.get("demo") == "1"
    return jsonify({"recommendations": recommender.get_recommendations(limit=3, demo=demo), "demo_data": demo})

@app.route("/api/recommendations/dismiss", methods=["POST"])
def dismiss_recommendation():
    data = request.json or {}
    key = data.get("dismissal_key") or data.get("sign_id") or data.get("rule_id")
    action = data.get("choice", "dismiss")
    if key:
        storage.dismiss_recommendation(key, snooze_seconds=6 * 3600 if action == "not_now" else None)
    return jsonify({"status": "dismissed" if action == "dismiss" else "snoozed", "dismissal_key": key})

@app.route("/api/dev/demo-data", methods=["POST"])
def demo_data():
    data = request.get_json(silent=True) or {}
    if data.get("developer_mode") is not True:
        return jsonify({"error": "Developer mode is required."}), 403
    if data.get("action") == "reset":
        storage.reset_demo_history()
        return jsonify({"demo_data": False, "status": "reset"})
    return jsonify({"status": "seeded", **seed_demo_history(storage)})

# -------------------------------------------------------------
# Recognition & Stabilization Endpoints
# -------------------------------------------------------------
@app.route("/api/hand-tracker/ready", methods=["GET"])
def local_hand_tracker_ready():
    """Confirm the bundled local landmark detector can initialize before practice."""
    try:
        initialize_local_hand_tracker()
        return jsonify({"ready": True, "model": "mediapipe-python-local-hand-landmarker"})
    except Exception as exc:
        app.logger.exception("Local hand tracker initialization failed")
        return jsonify({"ready": False, "error": str(exc)}), 503


@app.route("/api/hand-tracker/frame", methods=["POST"])
def local_hand_tracker_frame():
    """Process one transient JPEG frame locally; never write pixels to storage."""
    data = request.get_json(silent=True) or {}
    try:
        hands = detect_data_url(data.get("image"))
        return jsonify({"hands": hands})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        app.logger.exception("Local hand tracking failed")
        return jsonify({"error": "The local hand tracker could not process this frame."}), 503


@app.route("/api/recognize", methods=["POST"])
def recognize():
    diagnostics.record_frame_received()
    data = request.json or {}
    frame_b64 = data.get("frame")
    target_sign = data.get("target_sign")
    roi_box = data.get("roi_box")

    if not frame_b64:
        diagnostics.record_error()
        return jsonify({"status": "error", "message": "Missing frame payload"}), 400

    # Execute inference
    start_time = time.perf_counter()
    # Raw inference must not receive the lesson target. Compare only afterward.
    pred_res = engine.recognize_base64_frame(frame_b64, roi_box=roi_box)
    inf_latency_ms = (time.perf_counter() - start_time) * 1000
    diagnostics.record_inference(inf_latency_ms)
    pred_res["latency_ms"] = round(inf_latency_ms, 2)
    record_inference_diagnostic(pred_res)

    # Ingest into temporal stability buffer
    stab_res = stabilizer.add_prediction(pred_res)

    return jsonify({
        "raw_prediction": pred_res,
        "target_comparison": ({
            "target_sign": str(target_sign).upper(),
            "candidate_matches_target": bool(pred_res.get("predicted_sign") == str(target_sign).upper()),
            "grading_status": "unvalidated_uncertain",
        } if target_sign else None),
        "stability": stab_res,
        "inference_latency_ms": round(inf_latency_ms, 2)
    })

@app.route("/api/recognize/reset_stability", methods=["POST"])
def reset_stability():
    stabilizer.reset()
    return jsonify({"status": "reset"})


@app.route("/api/attempt", methods=["POST"])
def browser_attempt():
    """Accept compact landmark vectors only; raw camera frames are never accepted here."""
    start = time.perf_counter()
    data = request.get_json(silent=True) or {}
    frames = data.get("frames")
    target = str(data.get("target_sign", "")).upper()
    mode = data.get("mode", "practise")
    if not isinstance(frames, list) or len(frames) > 30 or mode not in {"practise", "check"}:
        return jsonify({"error": "Expected a short landmark window and a supported practice mode."}), 400
    # Reference comparison is a secondary, one-reference-per-class signal and is not a probability.
    result = assess_landmark_window(target, frames, getattr(engine, "landmark_profiles", {}))
    result["mode"] = mode
    result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
    result["model_version"] = engine.model_version
    result["frames_received"] = len(frames)
    result["recognition_validated"] = RECOGNITION_VALIDATED
    if result["outcome"] == "not_seen":
        result["failure_source"] = "system"
    mastery_eligible = bool(result.get("template_verified") and RECOGNITION_VALIDATED and result.get("outcome") == "got_it")
    result["mastery_eligible"] = mastery_eligible
    if result.get("outcome") == "got_it" and not RECOGNITION_VALIDATED:
        result["validation_note"] = "Recognition needs independent validation before progress can be confirmed."

    # Keep the authoritative learner assessment separate from the raw candidate and pose result.
    target_info = curriculum.get_sign_by_label(target)
    if (target_info and result["outcome"] == "not_seen" and data.get("save_progress", True)):
        update = learner_manager.update_with_attempt({
            "target_sign": target, "outcome": "not_seen", "is_correct": False,
            "is_uncertain": True, "can_update_mastery": False,
            "failure_source": "system", "mode": mode,
            "feedback_message": result.get("hint", "The camera could not see a hand.")
        }, {"status": "error", "predicted_sign": None}, mode=mode)
        update["saved"] = True
        result["learner_update"] = update
    elif (target_info and mode == "check" and result["outcome"] != "not_seen"
            and result.get("template_verified") and RECOGNITION_VALIDATED and data.get("save_progress", True)):
        got_it = result["outcome"] == "got_it"
        assessment = {
            "target_sign": target, "is_correct": got_it, "is_uncertain": not got_it,
            "can_update_mastery": got_it, "failure_source": result["failure_source"],
            "outcome": "correct" if got_it else "uncertain", "mode": mode,
            "attempt_assessment": {"status": "CORRECT" if got_it else "UNCERTAIN",
              "explanation": result["hint"], "can_update_mastery": got_it,
              "verified_template": result["template_verified"]},
            "outcome": "correct" if got_it else "uncertain",
            "model_evidence": {"predicted_class": result.get("candidate"),
              "raw_score": result.get("candidate_score"), "score_type": result.get("candidate_score_type"),
              "is_calibrated": False},
            "pose_evidence": {"per_finger_errors": result["perFingerErrors"],
              "template_verified": result["template_verified"]}
        }
        update = learner_manager.update_with_attempt(assessment, {
            "status": "recognized" if result.get("candidate") else "uncertain",
            "predicted_sign": result.get("candidate"), "raw_score": result.get("candidate_score"),
            "score_type": result.get("candidate_score_type")}, mode=mode)
        update["saved"] = True
        result["learner_update"] = update
    else:
        reason = ("Recognition needs independent validation before progress can be recorded."
                  if not RECOGNITION_VALIDATED else
                  "Sign template needs ISL educator review before progress can be recorded."
                  if not result.get("template_verified") else
                  "Learn and Practise feedback does not change Check-mode progress.")
        result["learner_update"] = {"saved": False, "reason": reason}
    result["next_recommendations"] = recommender.get_recommendations(limit=3) if result.get("learner_update", {}).get("saved") else []
    return jsonify(result)

processed_attempt_ids = set()

# -------------------------------------------------------------
# Attempt Assessment & Learner Model Update
# -------------------------------------------------------------
@app.route("/api/assess", methods=["POST"])
def assess():
    start = time.perf_counter()
    data = request.json or {}
    raw_prediction = data.get("prediction", {})
    target_sign = data.get("target_sign", "1")
    learner_confirmation = data.get("learner_confirmation")
    observations = data.get("observations", [])
    attempt_uuid = data.get("attempt_id") or data.get("attempt_uuid")

    # Idempotent attempt submission (Priority 2 & 10)
    if attempt_uuid and attempt_uuid in processed_attempt_ids:
        return jsonify({
            "status": "duplicate_ignored",
            "message": "Attempt already evaluated and recorded."
        })

    if attempt_uuid:
        if len(processed_attempt_ids) > 1000:
            processed_attempt_ids.clear()
        processed_attempt_ids.add(attempt_uuid)

    # Browser observations are the attempt's evidence. Never assess an empty
    # prediction object or allow a preparation-frame prediction to leak in.
    if not raw_prediction and observations:
        usable = [o for o in observations if o.get("predicted_sign")]
        if usable:
            last = usable[-1]
            raw_prediction = {
                "status": last.get("inference_status", "recognized"),
                "predicted_sign": last.get("predicted_sign"),
                "raw_score": last.get("raw_score"),
                "score_type": last.get("score_type", "unavailable"),
                "diagnostics": last.get("diagnostics", {}),
            }

    assessment = assess_attempt(
        prediction_result=raw_prediction,
        target_sign_label=target_sign,
        learner_confirmation=learner_confirmation,
        observations=observations
    )
    assessment["mode"] = str(data.get("mode", "practise"))

    profile = storage.get_profile() or {}
    save_progress = bool(profile.get("save_progress", 1)) and bool(data.get("save_progress", True))
    if save_progress:
        update_result = learner_manager.update_with_attempt(assessment, raw_prediction)
        fresh_recs = recommender.get_recommendations(limit=3)
    else:
        # Respect the learner's local-storage choice: calculate feedback in memory
        # but do not write attempts, mastery, or recommendations derived from them.
        update_result = {"saved": False, "message": "Progress saving is off; this attempt was not stored."}
        fresh_recs = []
    assess_latency_ms = (time.perf_counter() - start) * 1000
    diagnostics.record_assessment(assess_latency_ms)

    return jsonify({
        "status": "success",
        "assessment": assessment,
        "learner_update": update_result,
        "next_recommendations": fresh_recs,
        "assessment_latency_ms": round(assess_latency_ms, 2)
    })

# -------------------------------------------------------------
# Diagnostics & System Health
# -------------------------------------------------------------
@app.route("/api/diagnostics", methods=["GET"])
def get_diagnostics():
    metrics = diagnostics.get_metrics()
    metrics["recognition"] = {
        "model_version": getattr(engine, "model_version", "unknown"),
        "preprocessing_path": getattr(engine, "preprocessing_path", "unknown"),
        "hand_landmarker_available": bool(getattr(engine.pose_analyzer, "available", False)),
        "initialization_error": getattr(engine.pose_analyzer, "initialization_error", None),
    }
    return jsonify(metrics)

# -------------------------------------------------------------
# History Reset & Privacy Controls
# -------------------------------------------------------------
@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    storage.reset_learning_history()
    stabilizer.reset()
    return jsonify({"status": "cleared", "message": "Practice history and learner progress have been reset."})

@app.route("/api/learner/data/delete", methods=["POST"])
def delete_learner_data():
    storage.reset_learning_history()
    profile = storage.get_profile() or {}
    profile.update({"goal":"basics", "skill_level":"beginner", "research_consent":0,
                    "save_progress":0, "dominant_hand":"right", "text_size":"regular", "daily_goal":10,
                    "reduced_motion":0, "high_contrast":0, "color_blind_palette":0, "larger_targets":0,
                    "caption_cues":1, "camera_default":"", "mirror_view":1, "color_theme":"system",
                    "updated_at":time.time()})
    storage.save_profile(profile)
    stabilizer.reset()
    return jsonify({"status":"deleted"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting SignSense server on http://127.0.0.1:{port}")
    try:
        app.run(host="127.0.0.1", port=port, debug=False)
    finally:
        close_local_hand_tracker()
