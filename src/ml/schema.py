"""Manifest validation and participant-disjoint dataset splitting."""
import hashlib
import json
import random
from pathlib import Path

SIGNS = tuple([str(i) for i in range(1, 10)] + [chr(i) for i in range(ord("A"), ord("Z") + 1)])
CATEGORIES = {"correct_sign", "other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure"}


def read_manifest(path):
    path = Path(path)
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                row = json.loads(line)
                row["_line"] = line_number
                rows.append(row)
    return rows


def validate_manifest(path, verify_files=True):
    path = Path(path).resolve()
    root = path.parent
    if not path.is_file():
        return [], [f"manifest not found: {path}. Collect consented samples with tools/collect_webcam.py first."]
    rows = read_manifest(path)
    errors = []
    ids, hashes, phashes, phash_buckets = set(), {}, [], [dict() for _ in range(5)]
    for row in rows:
        line = row["_line"]
        required = ("sample_id", "image_path", "sha256", "perceptual_hash", "participant_id", "session_id",
                    "target_sign", "actual_sign", "category", "capture_condition", "consent", "consent_scope", "captured_at_utc")
        for key in required:
            if key not in row:
                errors.append(f"line {line}: missing {key}")
        if not all(k in row for k in required):
            continue
        if row["sample_id"] in ids:
            errors.append(f"line {line}: duplicate sample_id")
        ids.add(row["sample_id"])
        if not row["consent"]:
            errors.append(f"line {line}: sample lacks recorded consent")
        if row["consent_scope"] not in {"hand_only_still", "identifiable_still"}:
            errors.append(f"line {line}: invalid consent_scope")
        if row["category"] == "face_only" and row["consent_scope"] != "identifiable_still":
            errors.append(f"line {line}: face_only requires identifiable-still consent")
        if row["category"] not in CATEGORIES:
            errors.append(f"line {line}: unsupported category {row['category']}")
        if row["category"] in {"correct_sign", "other_sign", "incomplete_pose", "transition", "no_hand", "face_only", "tracking_failure"} and row["target_sign"] is None:
            errors.append(f"line {line}: target_sign is required to evaluate a prompted attempt")
        if row["target_sign"] is not None and row["target_sign"] not in SIGNS:
            errors.append(f"line {line}: invalid target_sign")
        actual = row["actual_sign"]
        if actual is not None and actual not in SIGNS:
            errors.append(f"line {line}: invalid actual_sign")
        if row["category"] in {"correct_sign", "other_sign"} and actual is None:
            errors.append(f"line {line}: complete sign category requires actual_sign")
        if row["category"] == "correct_sign" and actual != row["target_sign"]:
            errors.append(f"line {line}: correct_sign must equal target_sign")
        if row["category"] == "other_sign" and actual == row["target_sign"]:
            errors.append(f"line {line}: other_sign must differ from target_sign")
        if not row["participant_id"] or not row["session_id"] or not row["capture_condition"]:
            errors.append(f"line {line}: participant, session, and capture condition are required")
        digest = row["sha256"]
        if digest in hashes:
            errors.append(f"line {line}: exact duplicate image of line {hashes[digest]}")
        hashes[digest] = line
        try:
            encoded = row["perceptual_hash"]
            if len(encoded) != 16:
                raise ValueError("dHash must contain 16 hex digits")
            phash = int(encoded, 16)
            # Five disjoint bit bands guarantee that hashes within Hamming
            # distance four share one entire band. This avoids quadratic scans.
            bands = [(0, 13), (13, 13), (26, 13), (39, 13), (52, 12)]
            possible = set()
            for band_index, (shift, width) in enumerate(bands):
                mask = (1 << width) - 1
                possible.update(phash_buckets[band_index].get((phash >> shift) & mask, ()))
            for old_hash, old_line in (phashes[i] for i in possible):
                if (phash ^ old_hash).bit_count() <= 4:
                    errors.append(f"line {line}: near-duplicate frame of line {old_line} (dHash distance <= 4)")
                    break
            phashes.append((phash, line))
            for band_index, (shift, width) in enumerate(bands):
                mask = (1 << width) - 1
                phash_buckets[band_index].setdefault((phash >> shift) & mask, []).append(len(phashes) - 1)
        except (ValueError, TypeError):
            errors.append(f"line {line}: invalid perceptual_hash")
        if verify_files:
            image = (root / row["image_path"]).resolve()
            if root not in image.parents:
                errors.append(f"line {line}: image_path escapes dataset directory")
            elif not image.is_file():
                errors.append(f"line {line}: image file missing")
            else:
                actual_hash = hashlib.sha256(image.read_bytes()).hexdigest()
                if actual_hash != digest:
                    errors.append(f"line {line}: sha256 does not match image")
    return rows, errors


def participant_split(rows, seed=20261018, train_fraction=0.6, validation_fraction=0.2):
    """Split by participant (therefore also by session), never by frame."""
    participants = sorted({r["participant_id"] for r in rows})
    if len(participants) < 3:
        raise ValueError("At least three distinct participants are required for train/validation/test splits")
    if not (0 < train_fraction < 1 and 0 < validation_fraction < 1 and train_fraction + validation_fraction < 1):
        raise ValueError("Fractions must be positive and leave a non-empty test fraction")
    random.Random(seed).shuffle(participants)
    n_train = max(1, int(len(participants) * train_fraction))
    n_val = max(1, int(len(participants) * validation_fraction))
    if n_train + n_val >= len(participants):
        n_train = len(participants) - 2
        n_val = 1
    groups = {
        "train": set(participants[:n_train]),
        "validation": set(participants[n_train:n_train + n_val]),
        "test": set(participants[n_train + n_val:]),
    }
    result = {name: [r for r in rows if r["participant_id"] in group] for name, group in groups.items()}
    assert not (groups["train"] & groups["validation"] or groups["train"] & groups["test"] or groups["validation"] & groups["test"])
    return result, {k: sorted(v) for k, v in groups.items()}
