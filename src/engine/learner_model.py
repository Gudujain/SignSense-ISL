"""
SignSense Learner Model
Maintains per-sign learner mastery, attempt histories, and spaced repetition schedules.
Ensures uncertainty or technical failures never unfairly penalize the learner.
"""
import time
import json
from typing import Dict, Any, List, Optional
from src.engine.storage import storage
from src.curriculum.curriculum import curriculum

REVIEW_INTERVALS_HOURS = [1.0, 4.0, 24.0, 72.0, 168.0]  # Spaced repetition ladder
REVIEW_INTERVALS_DAYS = [1, 3, 7, 14]

class LearnerModelManager:
    def __init__(self):
        self.storage = storage

    def get_progress_summary(self, demo: bool = False) -> Dict[str, Any]:
        """Calculates global and per-sign progress statistics from actual storage."""
        all_progress = self.storage.get_all_sign_progress()
        all_signs = curriculum.get_all_signs()
        total_curriculum_signs = len(all_signs)

        mastery_records = self.storage.get_sign_mastery(demo=demo)
        attempts_for_stats = self.storage.get_recent_attempts(500, demo=demo)
        attempt_outcomes = self.storage.get_attempt_outcome_counts()
        if demo:
            attempt_outcomes = {"total": len(attempts_for_stats), "correct": sum(a.get("outcome") == "correct" for a in attempts_for_stats),
                "incorrect": sum(a.get("outcome") == "incorrect" for a in attempts_for_stats), "uncertain": sum(a.get("outcome") == "almost" for a in attempts_for_stats),
                "not_assessed": sum(a.get("outcome") == "not_seen" for a in attempts_for_stats), "legacy_unverified": 0}
        total_attempts = attempt_outcomes["total"]
        mastered_signs_count = 0
        learning_signs_count = 0
        signs_needing_revision = []

        now = time.time()
        for sign in all_signs:
            sid = sign["id"]
            p = all_progress.get(sid)
            mastery = mastery_records.get(sid)
            if mastery and mastery.get("level") == "mastered":
                mastered_signs_count += 1
            if mastery and mastery.get("level") in {"learning", "familiar"}:
                learning_signs_count += 1
            due_at = (mastery or {}).get("next_due") or ((p or {}).get("next_review_at") if not demo else 0)
            if due_at and float(due_at) <= now:
                signs_needing_revision.append({"sign_id": sid, "label": sign["label"],
                    "mastery_score": round((p or {}).get("mastery_score", 0), 2),
                    "due_hours_ago": round((now - float(due_at)) / 3600.0, 1), "next_due": due_at})
            if p:
                score = p["mastery_score"]
                # The current vision heuristics have not been validated on
                # held-out learners, so their score cannot establish mastery.
                if not mastery and (score > 0.0 or p["attempt_count"] > 0):
                    learning_signs_count += 1

                # Check if revision is due
        recent_attempts = attempts_for_stats[:10]
        progress_by_sign = {}
        signs_awaiting_validated_evidence = 0
        for sign in all_signs:
            record = all_progress.get(sign["id"])
            state = mastery_records.get(sign["id"])
            attempt_count = int(record.get("attempt_count", 0)) if record else 0
            attempt_count = sum(a.get("sign_id") == sign["id"] for a in recent_attempts) if demo else attempt_count
            next_review_at = float((state or {}).get("next_due") or (record or {}).get("next_review_at", 0.0))
            review_due = bool(attempt_count and next_review_at and now >= next_review_at)
            if attempt_count:
                signs_awaiting_validated_evidence += 1
            progress_by_sign[sign["id"]] = {
                "attempt_count": attempt_count,
                "status": "due" if review_due else ((state or {}).get("level") or ("practised" if attempt_count else "not_started")),
                "review_due": review_due,
                "mastered": bool(state and state.get("level") == "mastered"),
                "level": (state or {}).get("level", "new"),
            }

        return {
            "total_curriculum_signs": total_curriculum_signs,
            "mastered_signs_count": mastered_signs_count,
            "learning_signs_count": learning_signs_count,
            "unstarted_signs_count": total_curriculum_signs - (mastered_signs_count + learning_signs_count),
            "total_attempts": total_attempts,
            "assessed_correct_attempts": attempt_outcomes["correct"],
            "assessed_incorrect_attempts": attempt_outcomes["incorrect"],
            "uncertain_attempts": attempt_outcomes["uncertain"],
            "not_assessed_attempts": attempt_outcomes["not_assessed"],
            "legacy_unverified_attempts": attempt_outcomes["legacy_unverified"],
            "signs_awaiting_validated_evidence": signs_awaiting_validated_evidence,
            "progress_by_sign": progress_by_sign,
            "signs_needing_revision": signs_needing_revision,
            "mastery_by_sign": mastery_records,
            "streak_days": self._current_streak_days(attempts_for_stats, now),
            "weekly_attempts": sum(1 for a in attempts_for_stats if a.get("timestamp", 0) >= now - 7 * 86400),
            "today_attempts": sum(1 for a in attempts_for_stats if time.localtime(a.get("timestamp", 0)).tm_yday == time.localtime(now).tm_yday and time.localtime(a.get("timestamp", 0)).tm_year == time.localtime(now).tm_year),
            "demo_data": demo,
            "recent_attempts": recent_attempts
        }

    @staticmethod
    def _current_streak_days(attempts, now):
        from datetime import date, timedelta
        days={time.strftime("%Y-%m-%d",time.localtime(a["timestamp"])) for a in attempts
              if a.get("timestamp") and a.get("failure_source") != "system"}
        cursor=date.today()
        if cursor.isoformat() not in days:
            cursor-=timedelta(days=1)
        streak=0
        while cursor.isoformat() in days:
            streak+=1;cursor-=timedelta(days=1)
        return streak

    def update_with_attempt(self, assessment: Dict[str, Any], raw_prediction: Dict[str, Any], mode: str = "practise", demo: bool = False) -> Dict[str, Any]:
        """
        Updates learner model based on the assessed attempt.
        Strict rule: Uncertain predictions or system errors DO NOT lower mastery score!
        """
        target_label = assessment["target_sign"]
        sign_info = curriculum.get_sign_by_label(target_label)
        if not sign_info:
            return {"status": "error", "message": f"Unknown curriculum sign '{target_label}'"}

        sign_id = sign_info["id"]
        now = time.time()

        outcome = assessment.get("outcome") or ("uncertain" if assessment.get("is_uncertain") else
                  "correct" if assessment.get("is_correct") else "incorrect")
        mode = assessment.get("mode", mode)
        failure_source = assessment.get("failure_source", "learner")
        if failure_source == "system" or outcome in {"not_assessed", "system_failure"}:
            # System-side loss of evidence may be logged, but cannot affect learner mastery.
            attempt_log = self._attempt_log(sign_id, target_label, assessment, raw_prediction, now,
                                            outcome, "system", mode, demo)
            attempt_id = self.storage.record_attempt(attempt_log)
            return {"attempt_id": attempt_id, "sign_id": sign_id, "label": target_label,
                    "saved": True, "mastery_unchanged": True, "outcome": outcome,
                    "consecutive_successes": 0, "assessment": assessment}

        # Load or initialize sign progress record
        progress = self.storage.get_sign_progress(sign_id)
        if not progress:
            progress = {
                "sign_id": sign_id,
                "label": target_label,
                "attempt_count": 0,
                "confirmed_correct_count": 0,
                "confirmed_incorrect_count": 0,
                "uncertain_count": 0,
                "consecutive_successes": 0,
                "consecutive_failures": 0,
                "mastery_score": 0.0,
                "last_practiced_at": 0.0,
                "review_interval_hours": 1.0,
                "next_review_at": 0.0
            }

        progress["attempt_count"] += 1
        progress["last_practiced_at"] = now

        is_uncertain = assessment.get("is_uncertain", False)
        is_correct = assessment.get("is_correct", False)
        can_update = assessment.get("can_update_mastery", False)

        if is_uncertain:
            progress["uncertain_count"] += 1
            # Uncertainty does not alter consecutive streaks or degrade mastery
        elif can_update:
            if is_correct:
                progress["confirmed_correct_count"] += 1
                progress["consecutive_successes"] += 1
                progress["consecutive_failures"] = 0

                # Increase mastery (capped at 1.0)
                # Gain is proportional to distance from 1.0
                progress["mastery_score"] = min(1.0, progress["mastery_score"] + (1.0 - progress["mastery_score"]) * 0.35)

                # Advance spaced repetition ladder
                curr_interval = progress["review_interval_hours"]
                try:
                    curr_idx = REVIEW_INTERVALS_HOURS.index(curr_interval)
                    next_idx = min(len(REVIEW_INTERVALS_HOURS) - 1, curr_idx + 1)
                except ValueError:
                    next_idx = 1
                new_interval = REVIEW_INTERVALS_HOURS[next_idx]
                progress["review_interval_hours"] = new_interval
                progress["next_review_at"] = now + (new_interval * 3600.0)

            else:
                progress["confirmed_incorrect_count"] += 1
                progress["consecutive_failures"] += 1
                progress["consecutive_successes"] = 0

                # Moderate penalty (floor at 0.0)
                progress["mastery_score"] = max(0.0, progress["mastery_score"] - 0.20)

                # Reset spaced interval back to lowest rung
                progress["review_interval_hours"] = REVIEW_INTERVALS_HOURS[0]
                progress["next_review_at"] = now + (REVIEW_INTERVALS_HOURS[0] * 3600.0)

        # Determine transparent mastery status
        # Single correct attempt is 'learning'; requires at least 3 verified successes for 'mastered'
        succ = progress["confirmed_correct_count"]
        score = progress["mastery_score"]
        # Prototype heuristic progress only. Without validated recognition
        # evidence, no number of classifier agreements should claim mastery.
        if succ >= 3 and score >= 0.75:
            mastery_status = "practice_in_progress"
            display_progress = "Several consistent predictions; learner mastery not validated"
            is_mastered = False
        elif succ == 2:
            mastery_status = "practicing"
            display_progress = "2 of 3 verified attempts to master"
            is_mastered = False
        elif succ == 1:
            mastery_status = "learning"
            display_progress = "1 of 3 verified attempts to master"
            is_mastered = False
        elif progress.get("consecutive_failures", 0) >= 2:
            mastery_status = "struggling"
            display_progress = "Needs review"
            is_mastered = False
        else:
            mastery_status = "unstarted"
            display_progress = "0 of 3 verified attempts"
            is_mastered = False

        progress["mastery_status"] = mastery_status

        # The explicit four-level state follows only an authoritative assessment.
        # Browser recognition is currently gated as unvalidated, so it cannot advance this state.
        mastery = self.storage.get_sign_mastery(demo=demo).get(sign_id) or {
            "sign_id": sign_id, "level": "new", "streak": 0, "miss_count": 0,
            "last_practised": None, "next_due": None, "last_check_day": None
        }
        first_attempt = mastery["level"] == "new"
        if first_attempt:
            # First learner-originated attempt moves the sign into practice, even
            # when the recognizer is uncertain; uncertainty never means mastery.
            mastery["level"] = "learning"
            mastery["last_practised"] = now
            mastery["updated_at"] = now
        if outcome in {"correct", "incorrect", "almost", "try_again"} and assessment.get("can_update_mastery"):
            previous_level = mastery["level"]
            mastery["last_practised"] = now
            if previous_level == "new":
                mastery["level"] = "learning"
            if outcome == "correct" and assessment.get("is_correct"):
                mastery["streak"] += 1
                if mastery["level"] == "learning" and mastery["streak"] >= 2:
                    mastery["level"] = "familiar"
                elif mastery["level"] == "familiar" and mode == "check":
                    day = time.strftime("%Y-%m-%d", time.localtime(now))
                    if mastery.get("last_check_day") != day:
                        mastery["miss_count"] = 0
                        if mastery.get("check_streak", 0) + 1 >= 2:
                            mastery["level"] = "mastered"
                            mastery["check_streak"] = 0
                        else:
                            mastery["check_streak"] = mastery.get("check_streak", 0) + 1
                        mastery["last_check_day"] = day
                rung = min(max(mastery["streak"] - 1, 0), len(REVIEW_INTERVALS_DAYS) - 1)
                mastery["next_due"] = now + REVIEW_INTERVALS_DAYS[rung] * 86400
            else:
                mastery["streak"] = 0
                mastery["miss_count"] += 1
                mastery["check_streak"] = 0
                order = ["new", "learning", "familiar", "mastered"]
                current = order.index(mastery["level"])
                mastery["level"] = "learning" if first_attempt else order[max(0, current - 1)]
                mastery["next_due"] = now + 86400
            mastery["updated_at"] = now
        self.storage.save_sign_mastery(mastery, demo=demo)

        # Persist updated legacy-compatible progress
        if not demo:
            self.storage.save_sign_progress(progress)

        # Log complete attempt
        attempt_log = {
            "sign_id": sign_id,
            "label": target_label,
            "model_prediction": raw_prediction.get("predicted_sign"),
            # Only persist a probability when the predictor explicitly
            # supplies one. Uncalibrated raw scores remain in assessment
            # evidence and are not relabeled as confidence.
            "model_confidence": raw_prediction.get("confidence"),
            "model_status": raw_prediction.get("status", "unknown"),
            "learner_confirmation": assessment.get("learner_confirmation"),
            "is_correct": 1 if is_correct else 0,
            "is_uncertain": 1 if is_uncertain else 0,
            "discrepancy": 1 if assessment.get("discrepancy", False) else 0,
            "feedback_message": assessment.get("feedback_message", ""),
            "assessment_json": json.dumps(assessment, separators=(",", ":")),
            "model_raw_score": assessment.get("model_evidence", {}).get("raw_score"),
            "model_score_type": assessment.get("model_evidence", {}).get("score_type"),
            "latency_ms": raw_prediction.get("latency_ms", 0.0),
            "outcome": outcome,
            "hint_given": assessment.get("feedback_message", ""),
            "failure_source": failure_source,
            "mode": mode,
            "is_demo": 1 if demo else 0,
            "timestamp": now
        }
        attempt_id = self.storage.record_attempt(attempt_log)

        return {
            "attempt_id": attempt_id,
            "sign_id": sign_id,
            "label": target_label,
            "mastery_score": round(progress["mastery_score"], 2),
            "mastery_status": mastery_status,
            "is_mastered": is_mastered,
            "display_progress": display_progress,
            "consecutive_successes": progress["consecutive_successes"],
            "consecutive_failures": progress["consecutive_failures"],
            "next_review_in_hours": progress["review_interval_hours"],
            "assessment": assessment
        }

    @staticmethod
    def _attempt_log(sign_id, label, assessment, raw_prediction, now, outcome, failure_source, mode, demo=False):
        return {
            "sign_id": sign_id, "label": label,
            "model_prediction": raw_prediction.get("predicted_sign"),
            "model_confidence": raw_prediction.get("confidence"),
            "model_status": raw_prediction.get("status", "unknown"),
            "learner_confirmation": assessment.get("learner_confirmation"),
            "is_correct": 1 if assessment.get("is_correct") else 0,
            "is_uncertain": 1 if assessment.get("is_uncertain") else 0,
            "discrepancy": 1 if assessment.get("discrepancy") else 0,
            "feedback_message": assessment.get("feedback_message", ""),
            "assessment_json": json.dumps(assessment, separators=(",", ":")),
            "model_raw_score": (assessment.get("model_evidence") or {}).get("raw_score"),
            "model_score_type": (assessment.get("model_evidence") or {}).get("score_type"),
            "latency_ms": raw_prediction.get("latency_ms"), "timestamp": now,
            "outcome": outcome, "hint_given": assessment.get("feedback_message", ""),
            "failure_source": failure_source, "mode": mode,
            "is_demo": 1 if demo else 0,
        }

# Singleton
learner_manager = LearnerModelManager()
