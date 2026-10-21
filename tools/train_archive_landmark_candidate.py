"""Train and compare experimental letter landmark models from Dataset.zip.

The source archive's named splits are not participant-disjoint. This tool
removes byte-identical images across splits (preferring Training, then
Validation, then Testing), evaluates the remaining named splits, and records
that limitation in every report and model artifact. It is not a production
training or validation command.
"""
import argparse
import hashlib
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

import cv2
import joblib
import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ml.landmark_svc import pose_vector, pose_vector_with_layout  # noqa: E402
from src.recognition.pose_analyzer import HandPoseAnalyzer  # noqa: E402

LABELS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SPLIT_PRIORITY = {"Training": 0, "Validation": 1, "Testing": 2}


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_and_deduplicate(archive):
    """Return one exact-content copy per group, preferring the earlier split."""
    groups = {}
    original_counts = Counter()
    with ZipFile(archive) as source:
        for info in source.infolist():
            parts = PurePosixPath(info.filename).parts
            if (info.is_dir() or len(parts) != 3 or parts[0] not in SPLIT_PRIORITY
                    or parts[1] not in LABELS or PurePosixPath(parts[2]).suffix.lower() not in {".jpg", ".jpeg"}):
                continue
            original_counts[parts[0]] += 1
            digest = hashlib.sha256()
            with source.open(info) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            key = digest.hexdigest()
            row = {"path": info.filename, "split": parts[0], "label": parts[1], "sha256": key}
            groups.setdefault(key, []).append(row)

    retained, conflicting_groups = [], 0
    duplicate_groups = 0
    cross_split_groups = 0
    duplicate_by_pair = Counter()
    for copies in groups.values():
        if len(copies) > 1:
            duplicate_groups += 1
            splits = {row["split"] for row in copies}
            if len(splits) > 1:
                cross_split_groups += 1
                for first, second in (("Training", "Validation"), ("Training", "Testing"),
                                      ("Validation", "Testing")):
                    if first in splits and second in splits:
                        duplicate_by_pair[f"{first}-{second}"] += 1
        if len({row["label"] for row in copies}) > 1:
            conflicting_groups += 1
            continue
        retained.append(min(copies, key=lambda row: SPLIT_PRIORITY[row["split"]]))

    return retained, {
        "input_image_counts_by_named_split": dict(sorted(original_counts.items())),
        "input_unique_exact_image_count": len(groups),
        "exact_duplicate_groups": duplicate_groups,
        "exact_duplicate_groups_crossing_named_splits": cross_split_groups,
        "cross_split_duplicate_group_counts": dict(sorted(duplicate_by_pair.items())),
        "conflicting_label_duplicate_groups_excluded": conflicting_groups,
        "retained_image_counts_by_named_split": dict(sorted(Counter(r["split"] for r in retained).items())),
        "deduplication_policy": "one exact SHA-256 content group retained in Training, else Validation, else Testing",
    }


def summarize(y_true, y_pred, labels):
    p, r, f, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(labels), zero_division=0
    )
    per_class = {
        label: {"precision": float(p[i]), "recall": float(r[i]),
                "f1": float(f[i]), "support": int(support[i])}
        for i, label in enumerate(labels)
    }
    matrix = confusion_matrix(y_true, y_pred, labels=list(labels))
    return {
        "accuracy": float(np.mean(np.asarray(y_true) == np.asarray(y_pred))) if len(y_true) else None,
        "macro_precision": float(np.mean(p)) if len(p) else None,
        "macro_recall": float(np.mean(r)) if len(r) else None,
        "macro_f1": float(np.mean(f)) if len(f) else None,
        "per_class": per_class,
        "confusion_matrix_labels": list(labels),
        "confusion_matrix": matrix.tolist(),
    }


def fit_predict(train, evaluate, feature_key):
    X_train = np.asarray([row[feature_key] for row in train], dtype=np.float32)
    y_train = np.asarray([row["label"] for row in train])
    X_eval = np.asarray([row[feature_key] for row in evaluate], dtype=np.float32)
    y_eval = np.asarray([row["label"] for row in evaluate])
    if set(y_train) != set(LABELS):
        missing = sorted(set(LABELS) - set(y_train))
        raise ValueError(f"Training split is missing classes: {missing}")
    model = make_pipeline(StandardScaler(), SVC(C=1.0, kernel="rbf", decision_function_shape="ovr"))
    start = time.perf_counter()
    model.fit(X_train, y_train)
    fit_ms = (time.perf_counter() - start) * 1000.0
    predictions = model.predict(X_eval)
    return model, y_eval, predictions, fit_ms, X_eval


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-model", type=Path, default=ROOT / "ml_models" / "landmark_svc_letters_experimental.joblib")
    parser.add_argument("--report", type=Path, default=ROOT / "scratch" / "letter_archive_evaluation.json")
    parser.add_argument("--limit-per-split", type=int, default=0,
                        help="Optional deterministic per-class cap for a quick pipeline smoke run; 0 uses all images")
    args = parser.parse_args()
    if not args.archive.is_file():
        parser.error(f"Archive not found: {args.archive}")
    try:
        rows, archive_summary = discover_and_deduplicate(args.archive)
    except BadZipFile as exc:
        parser.error(f"Invalid ZIP archive: {exc}")

    if args.limit_per_split:
        for split in SPLIT_PRIORITY:
            subset = [r for r in rows if r["split"] == split]
            subset.sort(key=lambda row: (row["label"], row["sha256"]))
            kept = []
            counts = Counter()
            for row in subset:
                if counts[row["label"]] < args.limit_per_split:
                    kept.append(row)
                    counts[row["label"]] += 1
            rows = [r for r in rows if r["split"] != split] + kept

    analyzer = HandPoseAnalyzer()
    if not analyzer.available:
        parser.error(f"MediaPipe hand landmark detector unavailable: {analyzer.initialization_error}")

    extracted, extraction_ms = [], []
    try:
        with ZipFile(args.archive) as source:
            for index, row in enumerate(rows, 1):
                started = time.perf_counter()
                encoded = np.frombuffer(source.read(row["path"]), dtype=np.uint8)
                frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
                if frame is None:
                    row["tracking_status"] = "decode_failed"
                    continue
                pose = analyzer.analyze_frame(frame)
                elapsed = (time.perf_counter() - started) * 1000.0
                extraction_ms.append(elapsed)
                if pose.get("detected"):
                    old = pose_vector(pose)
                    layout = pose_vector_with_layout(pose)
                    if old is not None and layout is not None:
                        extracted.append({**row, "pose_vector": old, "layout_vector": layout,
                                          "hands_detected": int(pose.get("hands_count", 0)),
                                          "feature_latency_ms": elapsed})
                if index % 500 == 0:
                    print(f"processed {index}/{len(rows)} archive images; landmarks extracted for {len(extracted)}", flush=True)
    finally:
        analyzer.close()

    split_rows = {name: [r for r in extracted if r["split"] == name] for name in SPLIT_PRIORITY}
    if any(not split_rows[name] for name in ("Training", "Validation", "Testing")):
        raise SystemExit("At least one retained split has no images with usable hand landmarks.")

    train = split_rows["Training"]
    validation = split_rows["Validation"]
    test = split_rows["Testing"]
    candidates = {}
    for key, title in (("pose_vector", "existing_local_hand_features"),
                       ("layout_vector", "local_features_plus_relative_two_hand_layout")):
        model, val_y, val_pred, fit_ms, val_X = fit_predict(train, validation, key)
        test_y = np.asarray([row["label"] for row in test])
        test_X = np.asarray([row[key] for row in test], dtype=np.float32)
        infer_times = []
        test_pred = []
        for vector in test_X:
            t0 = time.perf_counter()
            test_pred.append(model.predict([vector])[0])
            infer_times.append((time.perf_counter() - t0) * 1000.0)
        candidates[title] = {
            "model": model,
            "validation": summarize(val_y, val_pred, LABELS),
            "test": summarize(test_y, test_pred, LABELS),
            "fit_latency_ms": fit_ms,
            "classifier_latency_ms_mean": statistics.mean(infer_times),
            "classifier_latency_ms_p95": float(np.percentile(infer_times, 95)),
            "feature_dimension": int(train[0][key].size),
        }

    selected = max(candidates, key=lambda name: candidates[name]["validation"]["macro_f1"])
    selected_key = "pose_vector" if selected == "existing_local_hand_features" else "layout_vector"
    selected_model = candidates[selected]["model"]
    all_classes_present = {name: sorted({r["label"] for r in split_rows[name]}) for name in split_rows}
    tracking = {
        name: {
            "usable_landmark_images": len(split_rows[name]),
            "retained_images": len([r for r in rows if r["split"] == name]),
            "landmark_detection_coverage": len(split_rows[name]) / max(1, len([r for r in rows if r["split"] == name])),
            "observed_hand_count_distribution": dict(sorted(Counter(str(r["hands_detected"]) for r in split_rows[name]).items())),
            "class_coverage": len(all_classes_present[name]),
        } for name in split_rows
    }
    report = {
        "status": "experimental_archive_evaluation_not_production_validation",
        "dataset_archive": str(args.archive.resolve()),
        "dataset_sha256": file_sha256(args.archive),
        "labels": list(LABELS),
        "archive_summary": archive_summary,
        "split_method": "retained source archive folders after exact SHA-256 deduplication; not participant/session disjoint",
        "participant_metadata": "absent; generalization to unseen people is not measured",
        "negative_examples": "absent; false acceptance, rejection calibration, and unknown-sign handling are not measurable",
        "digits": "absent; this archive contains A-Z only",
        "tracking_summary": tracking,
        "preprocessing": "MediaPipe HandLandmarker, BGR JPEG decode then RGB conversion, up to two hands; inference time includes decode and hand landmark extraction",
        "features": {
            "existing_local_hand_features": "two normalized 21-point local hand vectors, zero padded, plus hand count/presence; current experimental pose_vector",
            "local_features_plus_relative_two_hand_layout": "left-to-right canonical local vectors plus wrist displacement and scale ratio",
        },
        "classifier": "StandardScaler + RBF SVC (C=1.0), no probability calibration, no rejection threshold",
        "candidate_selection": "higher validation macro-F1; test set used only for final reported comparison",
        "candidate_results": {name: {k: v for k, v in result.items() if k != "model"}
                              for name, result in candidates.items()},
        "selected_experimental_candidate": selected,
        "model_approval": "not approved for learner correctness or mastery; archive has no participant metadata or negative examples",
        "latency_note": "classifier timing is measured alone per test vector; feature latency includes local JPEG decode and MediaPipe landmark extraction on the current CPU",
    }
    args.output_model.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"estimator": selected_model, "metadata": {
        "model_version": "archive-letters-landmark-experimental-v1",
        "labels": list(LABELS),
        "feature_name": selected_key,
        "feature_dimension": int(train[0][selected_key].size),
        "archive_sha256": report["dataset_sha256"],
        "validation_macro_f1": candidates[selected]["validation"]["macro_f1"],
        "participant_disjoint_validation": False,
        "negative_validation_available": False,
        "production_approved": False,
    }}, args.output_model)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "archive_summary": archive_summary,
        "tracking_summary": tracking,
        "candidate_validation_macro_f1": {k: v["validation"]["macro_f1"] for k, v in candidates.items()},
        "candidate_test_macro_f1": {k: v["test"]["macro_f1"] for k, v in candidates.items()},
        "selected_experimental_candidate": selected,
        "report": str(args.report),
        "model": str(args.output_model),
    }, indent=2))


if __name__ == "__main__":
    main()
