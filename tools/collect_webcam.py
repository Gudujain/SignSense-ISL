"""Consent-gated still-frame collector; never records a video stream."""
import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import cv2
except ImportError as exc:
    raise SystemExit("OpenCV is missing. Activate the project .venv and run `python -m pip install -r requirements.txt`.") from exc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ml.schema import CATEGORIES, SIGNS  # noqa: E402


def dhash(image):
    gray = cv2.cvtColor(cv2.resize(image, (9, 8)), cv2.COLOR_BGR2GRAY)
    bits = (gray[:, 1:] > gray[:, :-1]).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def safe_id(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,48}", value):
        raise ValueError("Use a non-identifying pseudonym/session token: 2-48 letters, digits, _ or -")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consent", action="store_true", help="Confirm hand-only still-image consent from the separate addendum")
    parser.add_argument("--consent-identifiable-stills", action="store_true", help="Additional consent for face/identifiable stills (required for face_only examples)")
    parser.add_argument("--participant", required=True, help="Non-identifying participant pseudonym")
    parser.add_argument("--session", required=True, help="Recording session token")
    parser.add_argument("--output", type=Path, default=ROOT / "data_collection")
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    if not args.consent:
        parser.error("No capture without --consent after reading research/DATASET_IMAGE_CONSENT_ADDENDUM.md")
    participant, session = safe_id(args.participant), safe_id(args.session)
    if input("Confirm separate hand-only still-image consent was obtained (type YES): ").strip() != "YES":
        raise SystemExit("Consent not confirmed; no camera opened or data saved.")
    if args.consent_identifiable_stills and input("Confirm additional identifiable-still consent was obtained (type YES): ").strip() != "YES":
        raise SystemExit("Identifiable-still consent not confirmed; no camera opened or data saved.")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "manifest.jsonl"
    destination = output / "frames" / participant / session
    destination.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        cap.release()
        raise SystemExit(f"Could not open camera {args.camera}. Check that it is connected, not in use, and allowed by Windows camera privacy settings.")
    previous_hash = None
    consecutive_read_failures = 0
    print("Preview is not recorded. Press c to capture one still, q to quit.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                consecutive_read_failures += 1
                if consecutive_read_failures >= 30:
                    raise SystemExit("Camera stopped returning frames (30 consecutive failures); collection stopped without saving a new sample.")
                continue
            consecutive_read_failures = 0
            cv2.imshow("Consent-gated still collection (C=capture, Q=quit)", frame)
            key = cv2.waitKey(1) & 0xff
            if key == ord("q"):
                break
            if key != ord("c"):
                continue

            category = input(f"Category {sorted(CATEGORIES)}: ").strip()
            if category not in CATEGORIES:
                print("Unknown category; frame not saved.")
                continue
            if category == "face_only" and not args.consent_identifiable_stills:
                print("face_only requires --consent-identifiable-stills and separate signed consent.")
                continue
            target = input("Prompted target sign (1-9,A-Z; blank if none): ").strip().upper() or None
            actual = input("Actual complete sign label (blank if incomplete/no-hand/unknown): ").strip().upper() or None
            condition = input("Capture condition (e.g. lighting/background/distance): ").strip()
            identifiable = input("Does this still contain a face or identifying material? (y/N): ").strip().lower() == "y"
            if identifiable and not args.consent_identifiable_stills:
                print("Identifiable still skipped; obtain the separate additional consent first.")
                continue
            if category == "face_only" and not identifiable:
                print("A face_only example must actually contain a face; frame not saved.")
                continue
            if target not in SIGNS and target is not None or actual not in SIGNS and actual is not None or not condition:
                print("Invalid sign or missing capture condition; frame not saved.")
                continue
            if target is None:
                print("A prompted target sign is required for false-acceptance evaluation.")
                continue
            if category == "correct_sign" and target != actual:
                print("For correct_sign, actual label must equal target; frame not saved.")
                continue
            if category == "other_sign" and (actual is None or actual == target):
                print("For other_sign, actual label must differ from target; frame not saved.")
                continue
            image_hash = dhash(frame)
            if previous_hash is not None and (int(image_hash, 16) ^ int(previous_hash, 16)).bit_count() <= 4:
                print("Near-identical adjacent frame skipped (dHash distance <= 4).")
                continue
            previous_hash = image_hash

            sample_id = str(uuid.uuid4())
            relative = Path("frames") / participant / session / f"{sample_id}.jpg"
            saved_path = output / relative
            if not cv2.imwrite(str(saved_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95]):
                print("Image write failed; sample not recorded.")
                continue
            row = {
                "schema_version": 1,
                "sample_id": sample_id,
                "image_path": relative.as_posix(),
                "sha256": hashlib.sha256(saved_path.read_bytes()).hexdigest(),
                "perceptual_hash": image_hash,
                "participant_id": participant,
                "session_id": session,
                "target_sign": target,
                "actual_sign": actual,
                "category": category,
                "capture_condition": condition,
                "consent": True,
                "consent_scope": "identifiable_still" if identifiable else "hand_only_still",
                "consent_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            with manifest.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"Saved selected still: {sample_id}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
