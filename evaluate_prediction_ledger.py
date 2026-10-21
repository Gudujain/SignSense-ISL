"""Score the stored prediction CSV; this does not run or validate a model."""
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "submission_svm.csv"
OUTPUT_PATH = ROOT / "docs" / "ml_prediction_ledger_metrics.json"


def evaluate(path=CSV_PATH):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    required = {"ImageId", "PredictedLabel", "TrueLabel"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"CSV must contain columns {sorted(required)}")

    truth = [int(row["TrueLabel"]) for row in rows]
    predicted = [int(row["PredictedLabel"]) for row in rows]
    labels = sorted(set(truth) | set(predicted))
    if len(set(row["ImageId"] for row in rows)) != len(rows):
        raise ValueError("ImageId values are not unique")
    confusion = Counter(zip(truth, predicted))
    per_class = {}
    for label in labels:
        tp = confusion[label, label]
        fp = sum(confusion[t, label] for t in labels if t != label)
        fn = sum(confusion[label, p] for p in labels if p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[str(label)] = {
            "support": sum(1 for t in truth if t == label),
            "precision": round(precision, 6), "recall": round(recall, 6),
            "f1": round(f1, 6),
        }
    n = len(rows)
    return {
        "evidence_type": "stored_prediction_ledger_only",
        "model_rerun": False,
        "independent_split_verified": False,
        "rows": n,
        "classes": len(labels),
        "unique_image_ids": len(set(row["ImageId"] for row in rows)),
        "image_ids_sequential_1_to_n": all(int(row["ImageId"]) == i + 1 for i, row in enumerate(rows)),
        "accuracy": round(sum(t == p for t, p in zip(truth, predicted)) / n, 8),
        "macro_precision": round(sum(x["precision"] for x in per_class.values()) / len(labels), 8),
        "macro_recall": round(sum(x["recall"] for x in per_class.values()) / len(labels), 8),
        "macro_f1": round(sum(x["f1"] for x in per_class.values()) / len(labels), 8),
        "per_class": per_class,
        "confusion_nonzero": [
            {"true_id": t, "predicted_id": p, "count": count}
            for (t, p), count in sorted(confusion.items())
        ],
        "inference_latency_ms": None,
        "false_acceptance_rate": None,
        "calibration_metrics": None,
    }


if __name__ == "__main__":
    result = evaluate()
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "evidence_type", "rows", "classes", "accuracy", "macro_precision",
        "macro_recall", "macro_f1", "confusion_nonzero",
        "inference_latency_ms", "false_acceptance_rate")}, indent=2))
