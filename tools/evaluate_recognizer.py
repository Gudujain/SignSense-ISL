"""Evaluate the active candidate generator on a participant-disjoint manifest."""
import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ml.schema import validate_manifest, participant_split, SIGNS  # noqa: E402
from src.recognition.engine import RecognitionEngine  # noqa: E402
from src.ml.landmark_svc import pose_vector, predict_candidate  # noqa: E402


def class_metrics(rows, labels):
    result, matrix = {}, Counter()
    prediction_labels = list(labels) + ["ABSTAIN"]
    for row in rows:
        truth, prediction = row.get("actual_sign"), row.get("candidate") or "ABSTAIN"
        if truth in labels:
            matrix[truth, prediction] += 1
    for label in labels:
        tp = matrix[label, label]
        fp = sum(matrix[other, label] for other in labels if other != label)
        fn = sum(matrix[label, pred] for pred in prediction_labels if pred != label)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        support = sum(matrix[label, pred] for pred in prediction_labels)
        result[label] = {"support": support,
                         "precision": p if support else None,
                         "recall": r if support else None,
                         "f1": 2*p*r/(p+r) if support and p+r else (0.0 if support else None)}
    sparse = [{"actual": t, "candidate": p, "count": n} for (t, p), n in sorted(matrix.items())]
    dense = [[matrix[truth, predicted] for predicted in prediction_labels]
             for truth in labels]
    observed = [m for m in result.values() if m["support"]]
    summary = {
        "accuracy": (sum(matrix[t, t] for t in labels) / sum(m["support"] for m in observed)) if observed else None,
        "macro_precision": statistics.mean(m["precision"] for m in observed) if observed else None,
        "macro_recall": statistics.mean(m["recall"] for m in observed) if observed else None,
        "macro_f1": statistics.mean(m["f1"] for m in observed) if observed else None,
        "observed_class_count": len(observed),
        "balanced_accuracy": statistics.mean(m["recall"] for m in observed) if observed else None,
    }
    return result, sparse, dense, prediction_labels, summary


def wilson_interval(successes, trials, z=1.959963984540054):
    """Two-sided 95% Wilson interval for a binomial rate; None if undefined."""
    if trials <= 0:
        return None
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    radius = z * ((p * (1 - p) / trials + z * z / (4 * trials * trials)) ** 0.5) / denominator
    return [max(0.0, center - radius), min(1.0, center + radius)]


def evaluate(manifest, seed=20261018, model=None):
    rows, errors = validate_manifest(manifest, verify_files=True)
    if errors:
        raise ValueError("Manifest validation failed:\n" + "\n".join(errors[:30]))
    split, groups = participant_split(rows, seed=seed)
    engine = RecognitionEngine()
    dataset_root = Path(manifest).resolve().parent
    outputs, latencies, alt_outputs, alt_latencies = [], [], [], []
    for sample in split["test"]:
        image = cv2.imread(str(dataset_root / sample["image_path"]))
        if image is None:
            raise ValueError(f"Could not read {sample['image_path']}")
        start = time.perf_counter()
        prediction = engine.recognize_frame(image)
        latencies.append((time.perf_counter() - start) * 1000.0)
        candidate = prediction.get("predicted_sign")
        outputs.append({**sample, "candidate": candidate,
                        "accepted": prediction.get("status") == "recognized",
                        "prediction_status": prediction.get("status"),
                        "input_validity": prediction.get("input_validity"),
                        "raw_score": prediction.get("raw_score"),
                        "score_type": prediction.get("score_type"),
                        "latency_ms": latencies[-1]})
        if model is not None:
            start = time.perf_counter()
            pose = engine.pose_analyzer.analyze_frame(image) if engine.pose_analyzer.available else None
            vector = pose_vector(pose)
            if vector is None:
                alt = {"candidate": None, "accepted": False, "raw_score": None,
                       "score_type": "unavailable_no_landmarks"}
            else:
                alt = predict_candidate(model["estimator"], vector, model["metadata"]["score_threshold"])
                alt["accepted"] = bool(alt["accepted"])
            alt_latencies.append((time.perf_counter() - start) * 1000.0)
            alt_outputs.append({**sample, "candidate": alt.get("candidate") if alt.get("accepted") else None,
                                "top_candidate": alt.get("candidate"), "accepted": alt.get("accepted", False),
                                "prediction_status": "recognized" if alt.get("accepted") else "uncertain",
                                "raw_score": alt.get("raw_score"), "score_type": alt.get("score_type"),
                                "latency_ms": alt_latencies[-1]})

    complete = [r for r in outputs if r["category"] in ("correct_sign", "other_sign")]
    per_class, confusion, confusion_dense, confusion_labels, metric_summary = class_metrics(complete, SIGNS)
    accepted = [r for r in outputs if r["accepted"]]
    negatives = [r for r in outputs if r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and r["target_sign"]]
    fa_candidates = sum(r["candidate"] == r["target_sign"] for r in negatives)
    fa_accepted = sum(r["accepted"] and r["candidate"] == r["target_sign"] for r in negatives)
    categories = {}
    for category in sorted({r["category"] for r in outputs}):
        bucket = [r for r in outputs if r["category"] == category]
        categories[category] = {
            "count": len(bucket),
            "candidate_coverage": sum(r["candidate"] is not None for r in bucket) / len(bucket),
            "rejection_rate": sum(not r["accepted"] for r in bucket) / len(bucket),
            "target_candidate_matches": sum(r["candidate"] == r["target_sign"] for r in bucket if r["target_sign"]),
            "accepted_target_false_accepts": sum(r["accepted"] and r["candidate"] == r["target_sign"] for r in bucket if r["target_sign"]),
        }
    return {
        "model_version": engine.model_version,
        "preprocessing_path": engine.preprocessing_path,
        "split_seed": seed,
        "split_unit": "participant (all sessions remain grouped)",
        "split_participants": groups,
        "test_samples": len(outputs),
        "complete_sign_candidate_metrics": per_class,
        "complete_sign_candidate_summary": metric_summary,
        "complete_sign_candidate_confusion_sparse": confusion,
        "complete_sign_confusion_matrix_labels": confusion_labels,
        "complete_sign_confusion_matrix": confusion_dense,
        "complete_sign_candidate_accuracy": (sum(r["candidate"] == r["actual_sign"] for r in complete) / len(complete)) if complete else None,
        "rejection_rate": sum(not r["accepted"] for r in outputs) / len(outputs) if outputs else None,
        "negative_target_examples": len(negatives),
        "candidate_target_false_accept_rate_on_negatives": fa_candidates / len(negatives) if negatives else None,
        "accepted_target_false_accept_rate_on_negatives": fa_accepted / len(negatives) if negatives else None,
        "accepted_target_false_accept_rate_95pct_wilson": wilson_interval(fa_accepted, len(negatives)),
        "candidate_target_match_rate_on_negatives": fa_candidates / len(negatives) if negatives else None,
        "accepted_count": len(accepted),
        "latency_ms_mean": statistics.mean(latencies) if latencies else None,
        "latency_ms_p95": sorted(latencies)[min(len(latencies)-1, int(0.95*len(latencies)))] if latencies else None,
        "by_category": categories,
        "probability_calibration": "not used; scores are uncalibrated similarities",
        "alternative_model": None if model is None else {
            "metadata": model["metadata"],
            "same_test_participants": groups["test"],
            "test_metrics_including_rejections": class_metrics(
                [r for r in alt_outputs if r["category"] in ("correct_sign", "other_sign")], SIGNS)[0],
            "test_summary_including_rejections": class_metrics(
                [r for r in alt_outputs if r["category"] in ("correct_sign", "other_sign")], SIGNS)[4],
            "test_confusion_sparse": class_metrics(
                [r for r in alt_outputs if r["category"] in ("correct_sign", "other_sign")], SIGNS)[1],
            "test_confusion_matrix_labels": class_metrics(
                [r for r in alt_outputs if r["category"] in ("correct_sign", "other_sign")], SIGNS)[3],
            "test_confusion_matrix": class_metrics(
                [r for r in alt_outputs if r["category"] in ("correct_sign", "other_sign")], SIGNS)[2],
            "accepted_candidate_accuracy": (sum(r["candidate"] == r["actual_sign"] for r in alt_outputs if r["candidate"] and r["category"] in ("correct_sign", "other_sign")) /
                                            sum(r["candidate"] is not None for r in alt_outputs if r["category"] in ("correct_sign", "other_sign")))
                                           if any(r["candidate"] and r["category"] in ("correct_sign", "other_sign") for r in alt_outputs) else None,
            "rejection_rate": sum(not r["accepted"] for r in alt_outputs) / len(alt_outputs) if alt_outputs else None,
            "negative_target_example_count": sum(r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and bool(r["target_sign"]) for r in alt_outputs),
            "false_accepts_on_negative_target_examples": sum(r["accepted"] and r.get("top_candidate") == r.get("target_sign") for r in alt_outputs if r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and r["target_sign"]),
            "accepted_false_accept_rate_on_negative_targets": (
                sum(r["accepted"] and r.get("top_candidate") == r.get("target_sign") for r in alt_outputs if r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and r["target_sign"]) /
                sum(r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and bool(r["target_sign"]) for r in alt_outputs)
            ) if any(r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and r["target_sign"] for r in alt_outputs) else None,
            "accepted_false_accept_rate_95pct_wilson_on_negative_targets": wilson_interval(
                sum(r["accepted"] and r.get("top_candidate") == r.get("target_sign") for r in alt_outputs if r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and r["target_sign"]),
                sum(r["category"] in ("other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure") and bool(r["target_sign"]) for r in alt_outputs)),
            "latency_ms_mean": statistics.mean(alt_latencies) if alt_latencies else None,
            "latency_ms_p95": sorted(alt_latencies)[min(len(alt_latencies)-1, int(0.95*len(alt_latencies)))] if alt_latencies else None,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261018)
    parser.add_argument("--landmark-model", type=Path, help="Optional trained experimental SVC artifact")
    parser.add_argument("--output", type=Path, default=Path("ml_baseline_report.json"))
    args = parser.parse_args()
    model = None
    if args.landmark_model:
        import joblib
        model = joblib.load(args.landmark_model)
    try:
        report = evaluate(args.manifest, seed=args.seed, model=model)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}; test samples={report['test_samples']}; accuracy={report['complete_sign_candidate_accuracy']}")
