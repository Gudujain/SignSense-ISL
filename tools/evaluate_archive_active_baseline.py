"""Compare the active reference heuristic and archive SVC on deduplicated test images.

This comparison uses only the archive's Testing folder after exact-content
deduplication. It is not participant-disjoint and has no negative examples.
"""
import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import cv2
import joblib
import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.train_archive_landmark_candidate import LABELS, discover_and_deduplicate  # noqa: E402
from src.ml.landmark_svc import pose_vector, pose_vector_with_layout  # noqa: E402
from src.recognition.engine import RecognitionEngine  # noqa: E402


def discrete_numeral_guess(extended):
    non_thumb = [finger for finger in extended if finger != "thumb"]
    if len(non_thumb) == 1 and non_thumb[0] == "index":
        return "1"
    if len(non_thumb) == 2 and set(non_thumb) == {"index", "middle"}:
        return "2"
    if len(non_thumb) == 3 and set(non_thumb) == {"index", "middle", "ring"}:
        return "3"
    if len(non_thumb) == 4:
        return "4"
    if len(extended) == 5:
        return "5"
    return None


def active_template_candidate(engine, pose):
    if not pose or not pose.get("detected"):
        return None
    primary = pose["primary_hand"]
    feature = primary["feature_vector"]
    scores = []
    for label, profile in engine.landmark_profiles.items():
        ref = profile["feature_vector"]
        norm_u, norm_r = np.linalg.norm(feature), np.linalg.norm(ref)
        similarity = float(np.dot(feature, ref) / (norm_u * norm_r)) if norm_u > 1e-4 and norm_r > 1e-4 else 0.0
        ref_extended = profile["extended_fingers"]
        current_extended = primary["extended_fingers"]
        if set(ref_extended) == set(current_extended):
            similarity += 0.25
        elif len(ref_extended) == len(current_extended):
            similarity += 0.10
        scores.append((label, max(0.0, min(1.0, similarity))))
    scores.sort(key=lambda value: value[1], reverse=True)
    top = scores[0][0] if scores else None
    return discrete_numeral_guess(primary["extended_fingers"]) or top


def metrics(y_true, y_pred):
    all_labels = list(LABELS) + ["ABSTAIN_OR_OUTSIDE_LETTER_LABELS"]
    pred = [value if value in LABELS else all_labels[-1] for value in y_pred]
    p, r, f, support = precision_recall_fscore_support(
        y_true, pred, labels=list(LABELS), zero_division=0
    )
    matrix = confusion_matrix(y_true, pred, labels=all_labels)
    return {
        "accuracy_including_abstention": float(np.mean(np.asarray(y_true) == np.asarray(y_pred))),
        "macro_precision": float(np.mean(p)),
        "macro_recall": float(np.mean(r)),
        "macro_f1": float(np.mean(f)),
        "per_class": {
            label: {"precision": float(p[i]), "recall": float(r[i]),
                    "f1": float(f[i]), "support": int(support[i])}
            for i, label in enumerate(LABELS)
        },
        "confusion_matrix_labels": all_labels,
        "confusion_matrix": matrix.tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=ROOT / "ml_models" / "landmark_svc_letters_experimental.joblib")
    parser.add_argument("--report", type=Path, default=ROOT / "scratch" / "letter_archive_evaluation.json")
    args = parser.parse_args()
    model_data = joblib.load(args.model)
    estimator = model_data["estimator"]
    feature_name = model_data["metadata"]["feature_name"]
    feature_fn = pose_vector_with_layout if feature_name == "layout_vector" else pose_vector
    deduped, summary = discover_and_deduplicate(args.archive)
    tests = [row for row in deduped if row["split"] == "Testing"]
    if not tests:
        parser.error("No retained Testing rows in archive")

    engine = RecognitionEngine()
    active_true, active_pred, svc_pred = [], [], []
    active_ms, svc_ms, svc_end_to_end, extraction_ms = [], [], [], []
    detector_failures = 0
    try:
        with ZipFile(args.archive) as source:
            for index, row in enumerate(tests, 1):
                started = time.perf_counter()
                frame = cv2.imdecode(np.frombuffer(source.read(row["path"]), np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    pose = None
                else:
                    pose = engine.pose_analyzer.analyze_frame(frame)
                extraction_ms.append((time.perf_counter() - started) * 1000.0)
                active_candidate = active_template_candidate(engine, pose)
                if active_candidate is None:
                    detector_failures += 1
                active_true.append(row["label"])
                active_pred.append(active_candidate)
                active_ms.append((time.perf_counter() - started) * 1000.0)

                if not pose or not pose.get("detected"):
                    svc_pred.append(None)
                    svc_end_to_end.append((time.perf_counter() - started) * 1000.0)
                else:
                    vector = feature_fn(pose)
                    if vector is None:
                        svc_pred.append(None)
                        svc_end_to_end.append((time.perf_counter() - started) * 1000.0)
                    else:
                        pred_start = time.perf_counter()
                        svc_pred.append(str(estimator.predict([vector])[0]))
                        svc_ms.append((time.perf_counter() - pred_start) * 1000.0)
                        svc_end_to_end.append((time.perf_counter() - started) * 1000.0)
                if index % 500 == 0:
                    print(f"evaluated {index}/{len(tests)} held-out archive images", flush=True)
    finally:
        engine.pose_analyzer.close()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    report["active_reference_heuristic_comparison"] = {
        "same_exact_deduplicated_test_rows": len(tests),
        "same_split_policy": summary["deduplication_policy"],
        "active_model_version": engine.model_version,
        "permitted_interpretation": "image-disjoint letter candidate comparison only; not person-disjoint validation or assessment reliability",
        "candidate_coverage": {
            "active_reference_heuristic": 1.0 - detector_failures / len(tests),
            "archive_svc": sum(pred is not None for pred in svc_pred) / len(svc_pred),
        },
        "active_reference_heuristic_test_metrics": metrics(active_true, active_pred),
        "archive_svc_test_metrics": metrics(active_true, svc_pred),
        "inference_latency_ms": {
            "shared_image_decode_plus_mediapipe_mean": statistics.mean(extraction_ms),
            "shared_image_decode_plus_mediapipe_p95": float(np.percentile(extraction_ms, 95)),
            "svc_classifier_only_mean": statistics.mean(svc_ms) if svc_ms else None,
            "svc_classifier_only_p95": float(np.percentile(svc_ms, 95)) if svc_ms else None,
            "active_heuristic_end_to_end_mean": statistics.mean(active_ms),
            "active_heuristic_end_to_end_p95": float(np.percentile(active_ms, 95)),
            "svc_end_to_end_mean": statistics.mean(svc_end_to_end),
            "svc_end_to_end_p95": float(np.percentile(svc_end_to_end, 95)),
        },
        "false_acceptance": "not measurable: the archive has no labeled negative target examples",
        "rejection_calibration": "not measurable: the archive has no no-hand, incomplete, transition, or unknown-sign examples",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "active_macro_f1": report["active_reference_heuristic_comparison"]["active_reference_heuristic_test_metrics"]["macro_f1"],
        "archive_svc_macro_f1": report["active_reference_heuristic_comparison"]["archive_svc_test_metrics"]["macro_f1"],
        "active_accuracy": report["active_reference_heuristic_comparison"]["active_reference_heuristic_test_metrics"]["accuracy_including_abstention"],
        "archive_svc_accuracy": report["active_reference_heuristic_comparison"]["archive_svc_test_metrics"]["accuracy_including_abstention"],
        "report": str(args.report),
    }, indent=2))


if __name__ == "__main__":
    main()
