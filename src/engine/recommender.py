"""Explainable, deterministic teaching recommendations over saved attempt evidence."""
import json
import time
from typing import Any, Dict, List
from src.curriculum.curriculum import curriculum
from src.engine.storage import storage

class RecommendationEngine:
    def __init__(self):
        self.curriculum = curriculum
        self.storage = storage
        self.templates_path = None

    def _templates(self):
        if self.templates_path is None:
            import os
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "data", "signs.json")
            try:
                with open(path, encoding="utf-8") as stream:
                    self.templates_path = json.load(stream).get("signs", [])
            except (OSError, ValueError):
                self.templates_path = []
        return self.templates_path

    def _attempt_outcome(self, row):
        outcome = row.get("outcome")
        if outcome:
            return str(outcome).lower()
        evidence = row.get("assessment") or {}
        return str(evidence.get("outcome") or "uncertain").lower()

    def _suggestion(self, rule_id, title, action, reason, signs=(), **extra):
        sign_ids = list(signs)
        primary = self.curriculum.get_sign_by_id(sign_ids[0]) if sign_ids else None
        dismiss_key = f"{rule_id}:{','.join(sign_ids)}" if sign_ids else rule_id
        activity = {"SPACED_REVISION":"spaced_review", "NEXT_NEW_SIGN":"new_sign",
                    "SETUP_RECOVERY":"setup_check", "REPEATED_DIFFICULTY":"remedial_practice",
                    "CONTRAST_DRILL":"contrast_drill", "STAGE_UNLOCK":"stage_unlock",
                    "RETURN_WARMUP":"warmup", "SESSION_BREAK":"session_break"}.get(rule_id, action)
        return {"title": title, "action": action, "reason": reason, "sign_ids": sign_ids,
                "rule_id": rule_id, "sign_id": sign_ids[0] if sign_ids else None,
                "dismissal_key": dismiss_key,
                "activity_type": activity,
                "label": primary.get("label") if primary else None,
                "reference_image": primary.get("reference_image") if primary else None,
                "stage": primary.get("stage") if primary else None,
                "explanation": reason, **extra}

    def get_recommendations(self, limit: int = 3, demo: bool = False) -> List[Dict[str, Any]]:
        signs = self.curriculum.get_all_signs()
        recent = self.storage.get_recent_attempts(100, demo=demo)
        mastery = self.storage.get_sign_mastery(demo=demo)
        legacy = {} if demo else self.storage.get_all_sign_progress()
        dismissed = set(self.storage.get_dismissed_recommendations())
        now = time.time()
        candidates = []

        def add(item, key=None):
            lookup = key or (("demo:" if demo else "") + item["dismissal_key"])
            if lookup not in dismissed and item.get("sign_id") not in dismissed and not (set(item.get("sign_ids", ())) & dismissed):
                candidates.append(item)

        # Rules are considered in the requested teaching priority order.
        last_two = recent[:2]
        if len(last_two) == 2 and all(self._attempt_outcome(a) == "not_seen" or a.get("failure_source") == "system" for a in last_two):
            add(self._suggestion("SETUP_RECOVERY", "Check your setup", "setup", "We couldn't see your hand clearly."))

        due_ids = [sid for sid, record in mastery.items() if record.get("next_due") and float(record["next_due"]) <= now
                   and f"{'demo:' if demo else ''}SPACED_REVISION:{sid}" not in dismissed]
        due_ids += [sid for sid, record in legacy.items() if record.get("next_review_at") and float(record["next_review_at"]) <= now and sid not in due_ids
                    and f"SPACED_REVISION:{sid}" not in dismissed]
        if due_ids:
            sid = due_ids[0]
            practiced_at = (mastery.get(sid) or {}).get("last_practised") or legacy.get(sid, {}).get("last_practiced_at")
            days = max(1, int((now - float(practiced_at)) / 86400)) if practiced_at else 1
            add(self._suggestion("SPACED_REVISION", f"Revise sign {self.curriculum.get_sign_by_id(sid)['label']}", "practise", f"It has been {days} day{'s' if days != 1 else ''} since you practised it.", [sid]))

        learner_rows = [a for a in recent if a.get("failure_source") != "system"]
        if len(learner_rows) >= 2:
            first, second = learner_rows[0], learner_rows[1]
            misses = {"incorrect", "almost", "try_again", "partial", "incomplete"}
            if first.get("sign_id") == second.get("sign_id") and self._attempt_outcome(first) in misses and self._attempt_outcome(second) in misses:
                sign = self.curriculum.get_sign_by_id(first["sign_id"])
                if sign:
                    add(self._suggestion("REPEATED_DIFFICULTY", "Watch the steps, then try again", "review_steps", f"Sign {sign['label']} has been tricky. Let's slow down.", [sign["id"]]))

        mixed = None
        for template in self._templates():
            for pair in template.get("commonConfusions", []):
                labels = [part.strip() for part in pair.replace("vs", "|").split("|")]
                if len(labels) == 2:
                    a, b = (self.curriculum.get_sign_by_label(label) for label in labels)
                    if not a or not b:
                        continue
                    rows = [item for item in recent if item.get("label") in labels and item.get("model_prediction") in labels]
                    if len(rows) >= 2 and any(item.get("label") != item.get("model_prediction") for item in rows[:4]):
                        mixed = (a, b); break
            if mixed: break
        if mixed:
            add(self._suggestion("CONTRAST_DRILL", "Contrast drill", "contrast", "You often mix these two.", [mixed[0]["id"], mixed[1]["id"]]))

        stages = self.curriculum.get_stages()
        for stage in stages[:-1]:
            stage_signs = [s for s in signs if s.get("stage") == stage.get("stage_id")]
            mastered_count = sum(1 for s in stage_signs if (mastery.get(s["id"]) or {}).get("level") == "mastered")
            if stage_signs and mastered_count / len(stage_signs) >= .8:
                next_stage = next((s for s in stages if s.get("stage_id") == stage["stage_id"] + 1), None)
                if next_stage:
                    next_name=next_stage['name'].split(':',1)[-1].split('(',1)[0].strip()
                    add(self._suggestion("STAGE_UNLOCK", f"Unlock Stage {next_stage['stage_id']}", "unlock_stage", f"You are ready for {next_name}.", extra_stage=next_stage["stage_id"]))
                    break

        last_time = max((float(row.get("timestamp") or 0) for row in recent), default=0)
        if last_time and now - last_time >= 3 * 86400:
            known = [sid for sid, item in mastery.items() if item.get("level") in {"familiar", "mastered"}]
            add(self._suggestion("RETURN_WARMUP", "Warm-up with 2–3 known signs", "warmup", "Welcome back. Warm up first.", known[:3]))

        session_counts = {}
        for row in recent:
            sid = row.get("session_id")
            if sid:
                session_counts[sid] = session_counts.get(sid, 0) + 1
        if session_counts and max(session_counts.values()) >= 10:
            add(self._suggestion("SESSION_BREAK", "Take a break", "pause", "Nice work. Rest your hands."))

        # Default is last so return/wellbeing rules can take precedence.
        next_sign = next((s for s in signs if (mastery.get(s["id"]) or {}).get("level", "new") == "new"
                          and s["id"] not in dismissed
                          and (("demo:" if demo else "") + f"NEXT_NEW_SIGN:{s['id']}") not in dismissed), None)
        if next_sign:
            add(self._suggestion("NEXT_NEW_SIGN", "Learn the next new sign", "practise", "Next in your plan.", [next_sign["id"]]))

        # Keep rule-priority order; remove duplicate actions on one sign.
        unique, seen = [], set()
        for candidate in candidates:
            key = tuple(candidate.get("sign_ids") or (candidate["rule_id"],))
            if key in seen: continue
            seen.add(key); unique.append(candidate)
        return unique[:max(1, min(int(limit), 3))]

recommender = RecommendationEngine()
