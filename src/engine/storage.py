"""
SignSense Local Persistent Storage
Uses SQLite for robust, offline, transactional persistence of learner profiles,
attempt logs, per-sign mastery records, and privacy preferences.
"""
import sqlite3
import os
import json
import time
from contextlib import closing
from typing import Dict, Any, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "signsense.db")

class StorageManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.cursor()
            # Learner profile
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learner_profile (
                    id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    skill_level TEXT NOT NULL,
                    research_consent INTEGER DEFAULT 0,
                    save_progress INTEGER DEFAULT 1,
                    dominant_hand TEXT DEFAULT 'right',
                    text_size TEXT DEFAULT 'regular',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            # Per-sign progress
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sign_progress (
                    sign_id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    attempt_count INTEGER DEFAULT 0,
                    confirmed_correct_count INTEGER DEFAULT 0,
                    confirmed_incorrect_count INTEGER DEFAULT 0,
                    uncertain_count INTEGER DEFAULT 0,
                    consecutive_successes INTEGER DEFAULT 0,
                    consecutive_failures INTEGER DEFAULT 0,
                    mastery_score REAL DEFAULT 0.0,
                    last_practiced_at REAL DEFAULT 0.0,
                    review_interval_hours REAL DEFAULT 1.0,
                    next_review_at REAL DEFAULT 0.0
                )
            """)
            profile_columns = {row[1] for row in cursor.execute("PRAGMA table_info(learner_profile)").fetchall()}
            # Additive preference columns preserve existing learner profiles during upgrades.
            for name, sql_type in (("save_progress", "INTEGER DEFAULT 1"),
                                   ("dominant_hand", "TEXT DEFAULT 'right'"),
                                   ("text_size", "TEXT DEFAULT 'regular'"),
                                   ("daily_goal", "INTEGER DEFAULT 10"),
                                   ("reduced_motion", "INTEGER DEFAULT 0"),
                                   ("high_contrast", "INTEGER DEFAULT 0"),
                                   ("color_blind_palette", "INTEGER DEFAULT 0"),
                                   ("larger_targets", "INTEGER DEFAULT 0"),
                                   ("caption_cues", "INTEGER DEFAULT 1"),
                                   ("camera_default", "TEXT DEFAULT ''"),
                                   ("mirror_view", "INTEGER DEFAULT 1"),
                                   ("color_theme", "TEXT DEFAULT 'system'")):
                if name not in profile_columns:
                    cursor.execute(f"ALTER TABLE learner_profile ADD COLUMN {name} {sql_type}")
            # Practice attempts history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS practice_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sign_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    model_prediction TEXT,
                    model_confidence REAL,
                    model_status TEXT,
                    learner_confirmation TEXT,
                    is_correct INTEGER,
                    is_uncertain INTEGER,
                    discrepancy INTEGER,
                    feedback_message TEXT,
                    assessment_json TEXT,
                    model_raw_score REAL,
                    model_score_type TEXT,
                    latency_ms REAL,
                timestamp REAL NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0
                )
            """)
            # Additive learning-state tables: existing attempt rows are retained.
            cursor.execute("""CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, started_at REAL NOT NULL, ended_at REAL,
                attempts_count INTEGER NOT NULL DEFAULT 0, is_demo INTEGER NOT NULL DEFAULT 0)""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS sign_mastery (
                sign_id TEXT PRIMARY KEY, level TEXT NOT NULL DEFAULT 'new'
                  CHECK(level IN ('new','learning','familiar','mastered')),
                streak INTEGER NOT NULL DEFAULT 0, miss_count INTEGER NOT NULL DEFAULT 0,
                last_practised REAL, next_due REAL, last_check_day TEXT,
                check_streak INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL DEFAULT 0)""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS demo_sign_mastery (
                sign_id TEXT PRIMARY KEY, level TEXT NOT NULL DEFAULT 'new',
                streak INTEGER NOT NULL DEFAULT 0, miss_count INTEGER NOT NULL DEFAULT 0,
                last_practised REAL, next_due REAL, last_check_day TEXT,
                check_streak INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL DEFAULT 0)""")
            mastery_columns = {row[1] for row in cursor.execute("PRAGMA table_info(sign_mastery)").fetchall()}
            if "check_streak" not in mastery_columns:
                cursor.execute("ALTER TABLE sign_mastery ADD COLUMN check_streak INTEGER NOT NULL DEFAULT 0")
            # Add audit/evidence columns to databases created by older builds.
            existing = {row[1] for row in cursor.execute("PRAGMA table_info(practice_attempts)").fetchall()}
            for name, sql_type in (("assessment_json", "TEXT"), ("model_raw_score", "REAL"),
                                   ("model_score_type", "TEXT"), ("outcome", "TEXT"),
                                   ("hint_given", "TEXT"), ("failure_source", "TEXT"),
                                   ("mode", "TEXT"), ("session_id", "TEXT"), ("is_demo", "INTEGER NOT NULL DEFAULT 0")):
                if name not in existing:
                    cursor.execute(f"ALTER TABLE practice_attempts ADD COLUMN {name} {sql_type}")
            # Dismissed recommendations (user control)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dismissed_recommendations (
                    sign_id TEXT PRIMARY KEY,
                    dismissed_at REAL NOT NULL,
                    snoozed_until REAL
                )
            """)
            dismissed_columns = {row[1] for row in cursor.execute("PRAGMA table_info(dismissed_recommendations)").fetchall()}
            if "snoozed_until" not in dismissed_columns:
                cursor.execute("ALTER TABLE dismissed_recommendations ADD COLUMN snoozed_until REAL")
            conn.commit()

        # Seed default profile if missing
        if not self.get_profile():
            self.save_profile({
                "id": "default_learner",
                "goal": "basics",
                "skill_level": "beginner",
                "research_consent": 0,
                "created_at": time.time(),
                "updated_at": time.time()
            })

    def get_profile(self) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            row = conn.cursor().execute("SELECT * FROM learner_profile LIMIT 1").fetchone()
            if row:
                return dict(row)
        return None

    def save_profile(self, profile: Dict[str, Any]):
        profile = {
            "save_progress": 1,
            "dominant_hand": "right",
            "text_size": "regular",
            "daily_goal": 10,
            "reduced_motion": 0,
            "high_contrast": 0,
            "color_blind_palette": 0,
            "larger_targets": 0,
            "caption_cues": 1,
            "camera_default": "",
            "mirror_view": 1,
            "color_theme": "system",
            **profile,
        }
        with closing(self._get_connection()) as conn, conn:
            conn.cursor().execute("""
                INSERT INTO learner_profile (id, goal, skill_level, research_consent, save_progress, dominant_hand, text_size,
                    daily_goal, reduced_motion, high_contrast, color_blind_palette, larger_targets, caption_cues,
                    camera_default, mirror_view, color_theme, created_at, updated_at)
                VALUES (:id, :goal, :skill_level, :research_consent, :save_progress, :dominant_hand, :text_size,
                    :daily_goal, :reduced_motion, :high_contrast, :color_blind_palette, :larger_targets, :caption_cues,
                    :camera_default, :mirror_view, :color_theme, :created_at, :updated_at)
                ON CONFLICT(id) DO UPDATE SET
                    goal=excluded.goal,
                    skill_level=excluded.skill_level,
                    research_consent=excluded.research_consent,
                    save_progress=excluded.save_progress,
                    dominant_hand=excluded.dominant_hand,
                    text_size=excluded.text_size,
                    daily_goal=excluded.daily_goal,
                    reduced_motion=excluded.reduced_motion,
                    high_contrast=excluded.high_contrast,
                    color_blind_palette=excluded.color_blind_palette,
                    larger_targets=excluded.larger_targets,
                    caption_cues=excluded.caption_cues,
                    camera_default=excluded.camera_default,
                    mirror_view=excluded.mirror_view,
                    color_theme=excluded.color_theme,
                    updated_at=excluded.updated_at
            """, profile)
            conn.commit()

    def get_all_sign_progress(self) -> Dict[str, Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            rows = conn.cursor().execute("SELECT * FROM sign_progress").fetchall()
            return {r["sign_id"]: dict(r) for r in rows}

    def get_sign_progress(self, sign_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            row = conn.cursor().execute("SELECT * FROM sign_progress WHERE sign_id = ?", (sign_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def save_sign_progress(self, progress: Dict[str, Any]):
        with closing(self._get_connection()) as conn, conn:
            conn.cursor().execute("""
                INSERT INTO sign_progress (
                    sign_id, label, attempt_count, confirmed_correct_count, confirmed_incorrect_count,
                    uncertain_count, consecutive_successes, consecutive_failures, mastery_score,
                    last_practiced_at, review_interval_hours, next_review_at
                ) VALUES (
                    :sign_id, :label, :attempt_count, :confirmed_correct_count, :confirmed_incorrect_count,
                    :uncertain_count, :consecutive_successes, :consecutive_failures, :mastery_score,
                    :last_practiced_at, :review_interval_hours, :next_review_at
                )
                ON CONFLICT(sign_id) DO UPDATE SET
                    attempt_count=excluded.attempt_count,
                    confirmed_correct_count=excluded.confirmed_correct_count,
                    confirmed_incorrect_count=excluded.confirmed_incorrect_count,
                    uncertain_count=excluded.uncertain_count,
                    consecutive_successes=excluded.consecutive_successes,
                    consecutive_failures=excluded.consecutive_failures,
                    mastery_score=excluded.mastery_score,
                    last_practiced_at=excluded.last_practiced_at,
                    review_interval_hours=excluded.review_interval_hours,
                    next_review_at=excluded.next_review_at
            """, progress)
            conn.commit()

    def record_attempt(self, attempt: Dict[str, Any]) -> int:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.cursor()
            attempt = {"model_prediction":None,"model_confidence":None,"model_status":None,
                       "learner_confirmation":None,"is_correct":0,"is_uncertain":0,"discrepancy":0,
                       "feedback_message":"","assessment_json":None,"model_raw_score":None,
                       "model_score_type":None,"latency_ms":None,"outcome":None,
                       "hint_given":None,"failure_source":None,"is_demo":0,
                       "mode":"practise",**attempt}
            attempt.setdefault("timestamp", time.time())
            session_id = attempt.get("session_id") or self.ensure_session(cursor=cursor, is_demo=bool(attempt.get("is_demo")))
            attempt["session_id"] = session_id
            cursor.execute("""
                INSERT INTO practice_attempts (
                    sign_id, label, model_prediction, model_confidence, model_status,
                    learner_confirmation, is_correct, is_uncertain, discrepancy,
                    feedback_message, assessment_json, model_raw_score,
                    model_score_type, latency_ms, timestamp, outcome, hint_given,
                    failure_source, mode, session_id, is_demo
                ) VALUES (
                    :sign_id, :label, :model_prediction, :model_confidence, :model_status,
                    :learner_confirmation, :is_correct, :is_uncertain, :discrepancy,
                    :feedback_message, :assessment_json, :model_raw_score,
                    :model_score_type, :latency_ms, :timestamp, :outcome, :hint_given,
                    :failure_source, :mode, :session_id, :is_demo
                )
            """, attempt)
            cursor.execute("UPDATE sessions SET attempts_count=attempts_count+1 WHERE id=?", (session_id,))
            conn.commit()
            return cursor.lastrowid

    def ensure_session(self, cursor=None, is_demo=False) -> str:
        """Create a practice session lazily when an attempt is first recorded."""
        import uuid
        conn = None
        if cursor is None:
            conn = self._get_connection()
            cursor = conn.cursor()
        row = cursor.execute("SELECT id,started_at FROM sessions WHERE ended_at IS NULL AND is_demo=? ORDER BY started_at DESC LIMIT 1", (1 if is_demo else 0,)).fetchone()
        if row and time.time() - float(row[1]) > 3600:
            cursor.execute("UPDATE sessions SET ended_at=? WHERE id=?", (time.time(), row[0]))
            row = None
        if row:
            session_id = row[0]
        else:
            session_id = uuid.uuid4().hex
            cursor.execute("INSERT INTO sessions(id, started_at, is_demo) VALUES (?, ?, ?)", (session_id, time.time(), 1 if is_demo else 0))
        if conn:
            conn.commit()
            conn.close()
        return session_id

    def get_sign_mastery(self, demo=False) -> Dict[str, Dict[str, Any]]:
        table = "demo_sign_mastery" if demo else "sign_mastery"
        with closing(self._get_connection()) as conn, conn:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            return {row["sign_id"]: dict(row) for row in rows}

    def get_sessions(self) -> List[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            rows=conn.execute("SELECT * FROM sessions WHERE is_demo=0 ORDER BY started_at DESC").fetchall()
            return [dict(row) for row in rows]

    def save_sign_mastery(self, record: Dict[str, Any], demo=False):
        table = "demo_sign_mastery" if demo else "sign_mastery"
        payload = {"level":"new", "streak":0, "miss_count":0, "last_practised":None,
                   "next_due":None, "last_check_day":None, "check_streak":0,
                   "updated_at":time.time(), **record}
        with closing(self._get_connection()) as conn, conn:
            conn.execute(f"""INSERT INTO {table}
                (sign_id,level,streak,miss_count,last_practised,next_due,last_check_day,check_streak,updated_at)
                VALUES(:sign_id,:level,:streak,:miss_count,:last_practised,:next_due,:last_check_day,:check_streak,:updated_at)
                ON CONFLICT(sign_id) DO UPDATE SET level=excluded.level,streak=excluded.streak,
                miss_count=excluded.miss_count,last_practised=excluded.last_practised,
                next_due=excluded.next_due,last_check_day=excluded.last_check_day,
                check_streak=excluded.check_streak,updated_at=excluded.updated_at""", payload)

    def get_recent_attempts(self, limit: int = 50, demo=False) -> List[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            rows = conn.cursor().execute("""
                SELECT * FROM practice_attempts WHERE is_demo=? ORDER BY timestamp DESC LIMIT ?
            """, (1 if demo else 0, limit)).fetchall()
            attempts = [dict(r) for r in rows]
            for attempt in attempts:
                serialized = attempt.pop("assessment_json", None)
                if serialized:
                    try:
                        attempt["assessment"] = json.loads(serialized)
                    except (TypeError, json.JSONDecodeError):
                        attempt["assessment"] = None
                else:
                    attempt["assessment"] = None
            return attempts

    def get_attempt_outcome_counts(self) -> Dict[str, int]:
        """Count stored assessment outcomes without treating legacy predictions as grades."""
        counts = {"total": 0, "correct": 0, "incorrect": 0, "uncertain": 0,
                  "not_assessed": 0, "legacy_unverified": 0}
        with closing(self._get_connection()) as conn, conn:
            rows = conn.cursor().execute(
                "SELECT is_correct, is_uncertain, assessment_json FROM practice_attempts WHERE is_demo=0"
            ).fetchall()
        counts["total"] = len(rows)
        for row in rows:
            outcome = None
            if row["assessment_json"]:
                try:
                    record = json.loads(row["assessment_json"])
                    outcome = record.get("outcome")
                    if outcome is None:
                        outcome = (record.get("attempt_assessment") or {}).get("status")
                    if isinstance(outcome, str):
                        outcome = outcome.lower()
                except (TypeError, json.JSONDecodeError):
                    outcome = None
            if outcome in {"correct", "incorrect", "uncertain", "not_assessed"}:
                counts[outcome] += 1
            else:
                # Old rows have no authoritative assessment object; a historical
                # boolean must not be presented as validated evidence.
                counts["legacy_unverified"] += 1
        return counts

    def dismiss_recommendation(self, sign_id: str, snooze_seconds: Optional[int] = None):
        with closing(self._get_connection()) as conn, conn:
            conn.cursor().execute("""
                INSERT OR REPLACE INTO dismissed_recommendations (sign_id, dismissed_at, snoozed_until)
                VALUES (?, ?, ?)
            """, (sign_id, time.time(), time.time() + snooze_seconds if snooze_seconds else None))
            conn.commit()

    def get_dismissed_recommendations(self) -> List[str]:
        with closing(self._get_connection()) as conn, conn:
            rows = conn.cursor().execute("SELECT sign_id FROM dismissed_recommendations WHERE snoozed_until IS NULL OR snoozed_until > ?", (time.time(),)).fetchall()
            return [r["sign_id"] for r in rows]

    def clear_dismissed_recommendations(self):
        with closing(self._get_connection()) as conn, conn:
            conn.cursor().execute("DELETE FROM dismissed_recommendations")
            conn.commit()

    def reset_learning_history(self):
        """Safely resets all practice attempts, per-sign mastery, and dismissed recommendations."""
        with closing(self._get_connection()) as conn, conn:
            conn.cursor().execute("DELETE FROM practice_attempts")
            conn.cursor().execute("DELETE FROM sign_progress")
            conn.cursor().execute("DELETE FROM dismissed_recommendations")
            conn.cursor().execute("DELETE FROM sign_mastery")
            conn.cursor().execute("DELETE FROM sessions")
            conn.cursor().execute("DELETE FROM demo_sign_mastery")
            conn.commit()

    def reset_demo_history(self):
        with closing(self._get_connection()) as conn, conn:
            conn.execute("DELETE FROM practice_attempts WHERE is_demo=1")
            conn.execute("DELETE FROM sessions WHERE is_demo=1")
            conn.execute("DELETE FROM demo_sign_mastery")
            conn.commit()

# Singleton
storage = StorageManager()
