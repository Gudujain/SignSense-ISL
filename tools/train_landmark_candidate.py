"""Train an experimental landmark SVC; fit=train only, reject threshold=validation."""
import argparse
import json
import sys
from pathlib import Path

import cv2
import joblib
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ml.schema import validate_manifest, participant_split, SIGNS  # noqa: E402
from src.ml.landmark_svc import pose_vector, predict_candidate  # noqa: E402
from src.recognition.pose_analyzer import HandPoseAnalyzer  # noqa: E402


def extract(rows, root, analyzer):
    X, y, kept = [], [], []
    for row in rows:
        image = cv2.imread(str(root / row["image_path"]))
        if image is None:
            continue
        vector = pose_vector(analyzer.analyze_frame(image))
        if vector is not None:
            X.append(vector)
            y.append(row["actual_sign"])
            kept.append(row)
    return np.asarray(X, dtype=np.float32), np.asarray(y), kept


def choose_threshold(model, X, rows, max_false_accept_rate):
    if not len(X):
        raise ValueError("Validation contains no tracked landmark examples")
    scored = [predict_candidate(model, x, float("-inf")) for x in X]
    negatives = [(p, r) for p, r in zip(scored, rows)
                 if r["category"] != "correct_sign" and r.get("target_sign")]
    positives = [(p, r) for p, r in zip(scored, rows) if r["category"] == "correct_sign"]
    if not negatives or not positives:
        raise ValueError("Validation requires both correct_sign and target-labeled negative examples")
    values = sorted({p["raw_score"] for p, _ in scored})
    candidates = values + [values[-1] + 1e-9]
    for threshold in candidates:
        fa = sum(p["candidate"] == r["target_sign"] and p["raw_score"] >= threshold for p, r in negatives) / len(negatives)
        if fa <= max_false_accept_rate:
            positive_coverage = sum(p["candidate"] == r["target_sign"] and p["raw_score"] >= threshold for p, r in positives) / len(positives)
            return threshold, fa, positive_coverage, len(negatives), len(positives)
    raise ValueError("Could not select a threshold meeting the validation false-accept constraint")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261018)
    parser.add_argument("--max-validation-false-accept-rate", type=float, default=0.05)
    parser.add_argument("--output", type=Path, default=Path("ml_models/landmark_svc.joblib"))
    args = parser.parse_args()
    rows, errors = validate_manifest(args.manifest, verify_files=True)
    if errors:
        parser.error("Manifest invalid: " + "; ".join(errors[:8]))
    split, groups = participant_split(rows, args.seed)
    root = args.manifest.resolve().parent
    analyzer = HandPoseAnalyzer()
    if not analyzer.available:
        parser.error("MediaPipe hand-landmarker is unavailable; cannot extract landmark features")
    train_rows = [r for r in split["train"] if r["category"] == "correct_sign" and r.get("actual_sign")]
    val_rows = split["validation"]
    X_train, y_train, _ = extract(train_rows, root, analyzer)
    X_val, y_val, val_kept = extract(val_rows, root, analyzer)
    if len(set(y_train.tolist())) < 2:
        parser.error("Training split needs at least two observed sign classes")
    missing_classes = sorted(set(SIGNS) - set(y_train.tolist()))
    if missing_classes:
        parser.error("Training split lacks tracked correct examples for: " + ", ".join(missing_classes))
    model = make_pipeline(StandardScaler(), SVC(C=1.0, kernel="rbf", decision_function_shape="ovr"))
    model.fit(X_train, y_train)
    threshold, val_far, val_positive_coverage, n_negative, n_positive = choose_threshold(
        model, X_val, val_kept, args.max_validation_false_accept_rate)
    metadata = {
        "model_version": "landmark-svc-experimental-v1",
        "feature": "MediaPipe 21-point normalized XYZ per detected hand, padded to two hands, plus hand count",
        "classifier": "StandardScaler + RBF SVC (C=1); no calibrated probabilities",
        "score": "uncalibrated one-vs-rest decision score",
        "score_threshold": threshold,
        "validation_false_accept_rate": val_far,
        "validation_positive_target_coverage": val_positive_coverage,
        "validation_negative_count": n_negative,
        "validation_positive_count": n_positive,
        "max_validation_false_accept_rate": args.max_validation_false_accept_rate,
        "split_seed": args.seed,
        "split_participants": groups,
        "training_samples": len(X_train),
        "training_classes": sorted(set(y_train.tolist())),
        "validation_samples_with_landmarks": len(X_val),
        "probability_calibration": None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"estimator": model, "metadata": metadata}, args.output)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
