"""Experimental SVC over MediaPipe's normalized 3D hand landmarks."""
import numpy as np


def pose_vector(pose):
    if not pose or not pose.get("detected") or not pose.get("primary_hand"):
        return None
    hands = [pose["primary_hand"], pose.get("second_hand")]
    result = []
    for hand in hands:
        if hand is None:
            result.extend([0.0] * 63)
        else:
            values = np.asarray(hand.get("feature_vector"), dtype=np.float32).reshape(-1)
            if values.size != 63 or not np.isfinite(values).all():
                return None
            result.extend(values.tolist())
    result.append(float(pose.get("hands_count", 0)))
    result.append(float(pose.get("second_hand") is not None))
    return np.asarray(result, dtype=np.float32)


def pose_vector_with_layout(pose):
    """Extend local hand shape features with relative two-hand layout.

    The existing vector normalizes each hand around its own wrist, which
    discards where the hands are relative to one another. This candidate
    canonicalizes detected hands left-to-right and adds the normalized wrist
    displacement and hand-scale ratio. It remains an experimental feature,
    not validated pose evidence.
    """
    if not pose or not pose.get("detected") or not pose.get("primary_hand"):
        return None

    hands = [pose["primary_hand"]]
    if pose.get("second_hand") is not None:
        hands.append(pose["second_hand"])

    parsed = []
    for hand in hands:
        values = np.asarray(hand.get("feature_vector"), dtype=np.float32).reshape(-1)
        landmarks = np.asarray(hand.get("landmarks_2d"), dtype=np.float32)
        if values.size != 63 or not np.isfinite(values).all():
            return None
        if landmarks.shape != (21, 2) or not np.isfinite(landmarks).all():
            return None
        scale = float(hand.get("hand_scale", 0.0))
        if not np.isfinite(scale) or scale <= 1e-4:
            return None
        parsed.append((float(landmarks[0, 0]), values, landmarks[0], scale))

    parsed.sort(key=lambda item: item[0])
    result = []
    for index in range(2):
        if index < len(parsed):
            result.extend(parsed[index][1].tolist())
        else:
            result.extend([0.0] * 63)

    layout = [0.0, 0.0, 0.0, 0.0]
    if len(parsed) == 2:
        left, right = parsed
        mean_scale = max((left[3] + right[3]) / 2.0, 1e-4)
        dx = float(right[2][0] - left[2][0])
        dy = float(right[2][1] - left[2][1])
        layout = [dx / mean_scale, dy / mean_scale,
                  float(np.hypot(dx, dy)) / mean_scale,
                  float(np.log(max(left[3], 1e-4) / max(right[3], 1e-4)))]
    result.extend([float(len(parsed)), float(len(parsed) == 2)])
    result.extend(layout)
    vector = np.asarray(result, dtype=np.float32)
    return vector if np.isfinite(vector).all() else None


def predict_candidate(model, vector, score_threshold):
    """Return top label, raw top score, and threshold decision (never probability)."""
    scores = np.asarray(model.decision_function([vector]))[0]
    order = np.argsort(scores)[::-1]
    best = int(order[0])
    margin = float(scores[order[0]] - scores[order[1]]) if len(order) > 1 else float("inf")
    score = float(scores[best])
    label = str(model.classes_[best])
    return {
        "candidate": label,
        "raw_score": score,
        "score_type": "uncalibrated_ovr_decision_score",
        "margin": margin,
        "accepted": score >= score_threshold,
    }
