"""Explicitly fictional demo history for developer presentations only."""
import json
import time
from contextlib import closing
from datetime import datetime, timedelta
from src.engine.storage import storage
from src.curriculum.curriculum import curriculum

def seed_demo_history(store=None):
    store = store or storage
    store.reset_demo_history()
    now = time.time()
    signs = curriculum.get_all_signs()
    with closing(store._get_connection()) as conn, conn:
        for offset in range(21, -1, -1):
            day = datetime.now() - timedelta(days=offset)
            stamp = day.replace(hour=17, minute=15, second=0, microsecond=0).timestamp()
            session_id = f"demo-{day.strftime('%Y%m%d')}"
            conn.execute("INSERT INTO sessions(id,started_at,ended_at,attempts_count,is_demo) VALUES(?,?,?,?,1)",
                         (session_id, stamp, stamp + 1800, 0))
        conn.commit()

    # Mix recent learner outcomes, a difficult pair, returning after a lapse,
    # and technical no-hand examples. These rows are explicitly tagged demo.
    plan = [
        (20, "1", "correct", "learner", "practise"),
        (17, "2", "correct", "learner", "check"),
        (14, "3", "correct", "learner", "check"),
        (10, "6", "incorrect", "learner", "practise"),
        (9, "9", "incorrect", "learner", "practise"),
        (7, "6", "almost", "learner", "practise"),
        (5, "5", "correct", "learner", "check"),
        (3, "1", "correct", "learner", "practise"),
        (3, "2", "almost", "learner", "practise"),
        (3, "3", "correct", "learner", "practise"),
        (3, "4", "correct", "learner", "practise"),
        (3, "5", "almost", "learner", "practise"),
        (3, "7", "correct", "learner", "practise"),
        (3, "6", "incorrect", "learner", "practise"),
        (3, "6", "incorrect", "learner", "practise"),
        (3, "1", "not_seen", "system", "practise"),
        (3, "2", "not_seen", "system", "practise"),
    ]
    for index, (offset, label, outcome, source, mode) in enumerate(plan):
        sign = curriculum.get_sign_by_label(label)
        stamp = now - offset * 86400 - 1200 + index * 2
        day_key = datetime.fromtimestamp(stamp).strftime("%Y%m%d")
        candidate = ("9" if label == "6" else "6") if label in {"6", "9"} else label
        store.record_attempt({
            "sign_id": sign["id"], "label": label, "model_prediction": candidate,
            "model_confidence": None, "model_status": "demo", "learner_confirmation": None,
            "is_correct": 1 if outcome == "correct" else 0,
            "is_uncertain": 1 if outcome in {"almost", "not_seen"} else 0,
            "discrepancy": int(candidate != label),
            "feedback_message": "Fictional developer-mode example.",
            "assessment_json": json.dumps({"outcome": outcome, "demo_data": True}),
            "model_raw_score": None, "model_score_type": None, "latency_ms": None,
            "timestamp": stamp, "outcome": outcome, "hint_given": "Example feedback",
            "failure_source": source, "mode": mode, "session_id": f"demo-{day_key}", "is_demo": 1,
        })

    # Stage 1 is complete in this scenario. Sign 5 is due; other states illustrate the UI.
    for sign in signs:
        level = "mastered" if sign["stage"] == 1 and sign["label"] in {"1", "2", "3", "4"} else "new"
        if sign["label"] == "5": level = "familiar"
        if sign["label"] == "6": level = "learning"
        stamp = now - (7 * 86400 if sign["label"] == "5" else 4 * 86400)
        store.save_sign_mastery({
            "sign_id": sign["id"], "level": level,
            "streak": 2 if level in {"familiar", "mastered"} else 0,
            "miss_count": 2 if sign["label"] == "6" else 0,
            "last_practised": stamp,
            "next_due": now - 86400 if sign["label"] == "5" else None,
            "last_check_day": None, "updated_at": now,
        }, demo=True)
    return {"demo_data": True, "sessions": 22, "attempts": len(plan)}
