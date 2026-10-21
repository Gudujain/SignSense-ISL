"""Stdlib-only tests for dataset validation and target-isolated raw inference."""
import ast
import hashlib
import json
import tempfile
import unittest
import os
from pathlib import Path

from src.ml.schema import participant_split, validate_manifest
from src.ml.diagnostics import record_inference_diagnostic
from src.ml.landmark_svc import pose_vector_with_layout
from src.engine.storage import StorageManager
from tools.evaluate_recognizer import class_metrics, wilson_interval

ROOT = Path(__file__).resolve().parents[1]


class DatasetPipelineTests(unittest.TestCase):
    @staticmethod
    def make_hand(wrist_x, wrist_y, hand_scale, marker):
        landmarks = [[wrist_x, wrist_y] for _ in range(21)]
        return {"feature_vector": [marker] * 63,
                "landmarks_2d": landmarks,
                "hand_scale": hand_scale}

    def test_layout_features_are_canonical_to_detector_hand_order(self):
        left = self.make_hand(0.2, 0.3, 0.1, 1.0)
        right = self.make_hand(0.8, 0.5, 0.2, 2.0)
        first = pose_vector_with_layout({"detected": True, "primary_hand": left,
                                         "second_hand": right, "hands_count": 2})
        swapped = pose_vector_with_layout({"detected": True, "primary_hand": right,
                                           "second_hand": left, "hands_count": 2})
        self.assertEqual(first.shape, (132,))
        self.assertTrue((first == swapped).all())
        self.assertGreater(first[-4], 0.0)
        self.assertGreater(first[-3], 0.0)

    def test_layout_features_change_when_relative_hand_position_changes(self):
        left = self.make_hand(0.2, 0.3, 0.1, 1.0)
        right = self.make_hand(0.8, 0.5, 0.2, 2.0)
        apart = pose_vector_with_layout({"detected": True, "primary_hand": left,
                                         "second_hand": right, "hands_count": 2})
        right_up = self.make_hand(0.8, 0.1, 0.2, 2.0)
        moved = pose_vector_with_layout({"detected": True, "primary_hand": left,
                                         "second_hand": right_up, "hands_count": 2})
        self.assertTrue((apart[:126] == moved[:126]).all())
        self.assertFalse((apart[-4:] == moved[-4:]).all())

    def test_layout_features_reject_invalid_landmarks_and_missing_pose(self):
        self.assertIsNone(pose_vector_with_layout(None))
        broken = self.make_hand(0.2, 0.3, 0.1, 1.0)
        broken["landmarks_2d"] = [[0.2, 0.3]]
        self.assertIsNone(pose_vector_with_layout({"detected": True,
                                                   "primary_hand": broken,
                                                   "second_hand": None}))

    def test_confusion_matrix_includes_abstention_and_uses_documented_label_order(self):
        per_class, sparse, dense, columns, summary = class_metrics(
            [{"actual_sign": "1", "candidate": "1"},
             {"actual_sign": "1", "candidate": None},
             {"actual_sign": "2", "candidate": "1"}], ("1", "2"))
        self.assertEqual(columns, ["1", "2", "ABSTAIN"])
        self.assertEqual(dense, [[1, 0, 1], [1, 0, 0]])
        self.assertEqual(per_class["1"]["support"], 2)
        self.assertEqual(summary["balanced_accuracy"], summary["macro_recall"])
        self.assertTrue(sparse)

    def test_wilson_interval_reports_uncertainty_and_undefined_empty_data(self):
        self.assertIsNone(wilson_interval(0, 0))
        low, high = wilson_interval(0, 20)
        self.assertEqual(low, 0.0)
        self.assertGreater(high, 0.0)
        self.assertLess(high, 0.2)

    def test_group_split_keeps_all_sessions_from_participant_together(self):
        rows = [{"participant_id": f"p{i}", "session_id": f"s{j}", "sample_id": f"{i}-{j}"}
                for i in range(8) for j in range(3)]
        split, groups = participant_split(rows, seed=42)
        sets = [{r["participant_id"] for r in split[k]} for k in ("train", "validation", "test")]
        self.assertFalse(sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])
        for participant in {r["participant_id"] for r in rows}:
            self.assertEqual(sum(participant in group for group in groups.values()), 1)

    def test_split_requires_three_participants(self):
        with self.assertRaises(ValueError):
            participant_split([{"participant_id": "p1"}, {"participant_id": "p2"}])

    def test_manifest_hash_and_category_contract(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            root = Path(temp)
            payload = b"not-identifiable-test-bytes"
            (root / "frame.jpg").write_bytes(payload)
            row = {"schema_version": 1, "sample_id": "x1", "image_path": "frame.jpg",
                   "sha256": hashlib.sha256(payload).hexdigest(), "perceptual_hash": "0000000000000000",
                   "participant_id": "p1", "session_id": "s1", "target_sign": "1", "actual_sign": "1",
                   "category": "correct_sign", "capture_condition": "test", "consent": True,
                   "consent_scope": "hand_only_still",
                   "captured_at_utc": "2026-01-01T00:00:00+00:00"}
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps(row) + "\n", encoding="utf-8")
            _, errors = validate_manifest(manifest)
            self.assertEqual(errors, [])
            row["actual_sign"] = "2"
            manifest.write_text(json.dumps(row) + "\n", encoding="utf-8")
            _, errors = validate_manifest(manifest, verify_files=False)
            self.assertTrue(any("correct_sign must equal target_sign" in e for e in errors))

    def test_raw_recognizer_body_does_not_read_target_argument(self):
        source = (ROOT / "src" / "recognition" / "engine.py").read_text(encoding="utf-8")
        module = ast.parse(source)
        engine_class = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == "RecognitionEngine")
        method = next(n for n in engine_class.body if isinstance(n, ast.FunctionDef) and n.name == "recognize_frame")
        names = {n.id for n in ast.walk(method) if isinstance(n, ast.Name)}
        self.assertNotIn("target_sign", names)

    def test_http_route_does_not_pass_target_to_raw_engine(self):
        tree = ast.parse((ROOT / "src" / "server" / "app.py").read_text(encoding="utf-8"))
        recognize = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "recognize")
        call = next(n for n in ast.walk(recognize) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "recognize_base64_frame")
        self.assertNotIn("target_sign", {kw.arg for kw in call.keywords})

    def test_diagnostics_are_opt_in_and_contain_no_image_or_landmarks(self):
        old = os.environ.get("SIGNSENSE_DIAGNOSTICS")
        try:
            os.environ["SIGNSENSE_DIAGNOSTICS"] = "1"
            with tempfile.TemporaryDirectory(dir=ROOT) as temp:
                path = Path(temp) / "diag.jsonl"
                record_inference_diagnostic({"model_version": "test", "prediction": "1",
                                             "frame": "secret", "diagnostics": {"landmarks": [1]}}, path)
                row = json.loads(path.read_text(encoding="utf-8"))
                self.assertNotIn("frame", row)
                self.assertNotIn("landmarks", row)
                self.assertEqual(row["model_version"], "test")
        finally:
            if old is None:
                os.environ.pop("SIGNSENSE_DIAGNOSTICS", None)
            else:
                os.environ["SIGNSENSE_DIAGNOSTICS"] = old

    def test_authoritative_assessment_and_raw_score_persist_without_confidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            storage = StorageManager(str(Path(temp) / "learner.db"))
            assessment = {"outcome": "uncertain", "is_correct": False,
                          "model_evidence": {"raw_score": 0.42,
                                             "score_type": "unvalidated_template_similarity",
                                             "calibrated_confidence": None}}
            storage.record_attempt({
                "sign_id": "sign_1", "label": "1", "model_prediction": "2",
                "model_confidence": None, "model_status": "uncertain",
                "learner_confirmation": None, "is_correct": 0, "is_uncertain": 1,
                "discrepancy": 1, "feedback_message": "Uncertain",
                "assessment_json": json.dumps(assessment), "model_raw_score": 0.42,
                "model_score_type": "unvalidated_template_similarity",
                "latency_ms": 4.0, "timestamp": 1.0,
            })
            saved = storage.get_recent_attempts(1)[0]
            self.assertEqual(saved["assessment"], assessment)
            self.assertIsNone(saved["model_confidence"])
            self.assertEqual(saved["model_raw_score"], 0.42)


if __name__ == "__main__":
    unittest.main()
