"""In-memory hand landmark detection for the local SignSense server."""
from __future__ import annotations

import base64
import binascii
import os
import threading
from typing import Any

import cv2
import mediapipe as mp
import numpy as np

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "data", "hand_landmarker.task"))
_lock = threading.Lock()
_landmarker = None


def initialize() -> None:
    """Load the bundled hand model once. Frames and landmarks are not persisted."""
    global _landmarker
    if _landmarker is not None:
        return
    with _lock:
        if _landmarker is None:
            if not os.path.isfile(MODEL_PATH):
                raise RuntimeError(f"Bundled hand model is missing: {MODEL_PATH}")
            options = mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.45,
                min_hand_presence_confidence=0.45,
                min_tracking_confidence=0.45,
            )
            _landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)


def close() -> None:
    """Release the native MediaPipe task before interpreter shutdown."""
    global _landmarker
    with _lock:
        if _landmarker is not None:
            _landmarker.close()
            _landmarker = None


def detect_data_url(data_url: Any) -> list[dict[str, Any]]:
    """Decode one bounded JPEG frame and return normalized MediaPipe landmarks."""
    if not isinstance(data_url, str) or not data_url.startswith("data:image/jpeg;base64,"):
        raise ValueError("Expected a JPEG camera frame.")
    encoded = data_url.partition(",")[2]
    if len(encoded) > 1_500_000:
        raise ValueError("Camera frame is too large.")
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Camera frame could not be decoded.") from exc
    if not image_bytes:
        raise ValueError("Camera frame is empty.")
    frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Camera frame is not a valid image.")
    height, width = frame.shape[:2]
    if width < 2 or height < 2:
        raise ValueError("Camera frame is too small.")
    scale = min(640 / width, 480 / height, 1.0)
    if scale < 1.0:
        frame = cv2.resize(frame, (max(2, round(width * scale)), max(2, round(height * scale))))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    initialize()
    with _lock:
        result = _landmarker.detect(image)
    hands = []
    for index, points in enumerate(result.hand_landmarks or []):
        handedness = "unknown"
        if index < len(result.handedness) and result.handedness[index]:
            handedness = result.handedness[index][0].category_name
        hands.append({
            "landmarks": [[float(point.x), float(point.y), float(point.z)] for point in points],
            "handedness": handedness,
        })
    return hands


