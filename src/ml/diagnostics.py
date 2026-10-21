"""Opt-in JSONL diagnostics; never records frames, landmarks, or identifiers."""
import json
import os
from pathlib import Path
from datetime import datetime, timezone


def record_inference_diagnostic(result, path=None):
    if os.environ.get("SIGNSENSE_DIAGNOSTICS", "").lower() not in {"1", "true", "yes"}:
        return False
    path = Path(path or os.environ.get("SIGNSENSE_DIAGNOSTICS_PATH", "diagnostics/recognition.jsonl"))
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_version": result.get("model_version"),
        "preprocessing_path": result.get("preprocessing_path"),
        "input_validity": result.get("input_validity"),
        "prediction": result.get("predicted_sign"),
        "status": result.get("status"),
        "raw_score": result.get("raw_score"),
        "score_type": result.get("score_type"),
        "latency_ms": result.get("latency_ms"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    return True
