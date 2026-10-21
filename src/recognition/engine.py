"""
SignSense Recognition Engine
Provides candidate generation for the current, unvalidated prototype.
No model probability or verified classification is produced.
"""
import os
import cv2
import numpy as np
import base64
import time
from typing import Dict, Any, Optional, Tuple, List
from src.recognition.pose_analyzer import pose_analyzer

CLASS_LABELS_35 = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
    'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

class RecognitionEngine:
    def __init__(self, references_dir: Optional[str] = None):
        if references_dir is None:
            references_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "references")
        self.references_dir = references_dir
        self.reference_features: Dict[str, Dict[str, Any]] = {}
        self.landmark_profiles: Dict[str, Dict[str, Any]] = {}
        self.labels = CLASS_LABELS_35
        self.pose_analyzer = pose_analyzer
        self.model_version = "template-candidate-v2"
        self.preprocessing_path = "mediapipe_landmarks" if self.pose_analyzer.available else "hsv_canny_hu_reference"
        self._load_reference_profiles()

    def _load_reference_profiles(self):
        """Precomputes unvalidated one-reference-per-class templates."""
        if not os.path.exists(self.references_dir):
            return

        for label in self.labels:
            img_path = os.path.join(self.references_dir, f"{label}.jpg")
            if not os.path.exists(img_path):
                continue
            img = cv2.imread(img_path)
            if img is None:
                continue

            canny, skin = self._preprocess_roi(img)
            moments = self._extract_shape_descriptors(canny, skin)
            self.reference_features[label] = {
                "moments": moments
            }

            # Precompute landmark profile if analyzer is available
            if self.pose_analyzer and self.pose_analyzer.available:
                try:
                    pose = self.pose_analyzer.analyze_frame(img)
                    if pose.get("detected"):
                        self.landmark_profiles[label] = {
                            "hands_count": pose["hands_count"],
                            "extended_fingers": pose["primary_hand"]["extended_fingers"],
                            "feature_vector": pose["primary_hand"]["feature_vector"]
                        }
                except Exception:
                    pass

    def _preprocess_roi(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extracts skin mask and Canny edges.
        Adheres faithfully to the baseline repository's imagePreprocessingUtils.py parameters.
        """
        resized = cv2.resize(image, (128, 128))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

        # Baseline HSV boundaries from original repo
        lower_boundary = np.array([0, 40, 30], dtype="uint8")
        upper_boundary = np.array([43, 255, 254], dtype="uint8")
        skin_mask = cv2.inRange(hsv, lower_boundary, upper_boundary)

        skin_mask = cv2.addWeighted(skin_mask, 0.5, skin_mask, 0.5, 0.0)
        skin_mask = cv2.medianBlur(skin_mask, 5)
        skin = cv2.bitwise_and(gray, gray, mask=skin_mask)

        # Baseline Canny parameters from original repo (60, 60)
        canny = cv2.Canny(skin, 60, 60)
        return canny, skin

    def _extract_shape_descriptors(self, canny: np.ndarray, skin: np.ndarray) -> np.ndarray:
        """Computes scale/rotation invariant log-transformed Hu moments + spatial area ratios."""
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        skin_pixels = np.count_nonzero(skin) / (skin.shape[0] * skin.shape[1])
        edge_pixels = np.count_nonzero(canny) / (canny.shape[0] * canny.shape[1])

        if contours:
            largest_c = max(contours, key=cv2.contourArea)
            m = cv2.moments(largest_c)
            hu = cv2.HuMoments(m).flatten()
            log_hu = []
            for h in hu:
                if abs(h) > 1e-12:
                    log_hu.append(-1.0 * np.sign(h) * np.log10(abs(h)))
                else:
                    log_hu.append(0.0)
            log_hu = np.array(log_hu, dtype=np.float32)
        else:
            log_hu = np.zeros(7, dtype=np.float32)

        features = np.concatenate([log_hu, [skin_pixels, edge_pixels]])
        return features

    def recognize_frame(
        self,
        frame: np.ndarray,
        target_sign: Optional[str] = None,
        roi_box: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Executes real-time sign recognition on a video frame or cropped ROI.
        Generates an unvalidated candidate. `target_sign` is accepted for
        backwards compatibility but is deliberately not read here.
        """
        start_time = time.perf_counter()

        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return {
                "status": "error",
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "invalid_or_empty_frame",
                "predicted_sign": None,
                "confidence": None,
                "is_uncertain": True,
                "latency_ms": 0.0,
                "message": "Invalid or empty camera frame."
            }

        # Reject malformed arrays before OpenCV/MediaPipe see them. This is
        # input validation only; it does not certify that a valid image has a
        # hand or a supported sign.
        if (frame.ndim != 3 or frame.shape[2] != 3 or
                frame.shape[0] < 10 or frame.shape[1] < 10):
            return {
                "status": "error",
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "invalid_frame_shape",
                "predicted_sign": None,
                "confidence": None,
                "is_uncertain": True,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "message": "Expected a non-empty color image with at least 10x10 pixels."
            }

        # Crop to ROI if specified
        h, w = frame.shape[:2]
        if roi_box:
            x1, y1, x2, y2 = roi_box
            x1 = max(0, min(x1, w - 10))
            y1 = max(0, min(y1, h - 10))
            x2 = max(x1 + 10, min(x2, w))
            y2 = max(y1 + 10, min(y2, h))
            roi = frame[y1:y2, x1:x2]
        else:
            # Use center region
            cx1, cy1 = int(w * 0.15), int(h * 0.10)
            cx2, cy2 = int(w * 0.85), int(h * 0.90)
            roi = frame[cy1:cy2, cx1:cx2]

        # -------------------------------------------------------------
        # STEP 1: Biomechanical Extraction on Full Camera Frame
        # -------------------------------------------------------------
        pose_data = None
        if self.pose_analyzer and self.pose_analyzer.available:
            try:
                # Pass full frame so hands anywhere in camera view are detected
                pose_data = self.pose_analyzer.analyze_frame(frame)
            except Exception:
                pose_data = None

        if pose_data and pose_data.get("detected"):
            # Hand landmark detected!
            primary = pose_data["primary_hand"]
            user_feat = primary["feature_vector"]
            ext_fingers = primary["extended_fingers"]
            steadiness = pose_data.get("steadiness", 0.5)

            # Compare user feature vector with precomputed landmark profiles
            best_label = None
            best_sim = -1.0
            scores: List[Tuple[str, float]] = []

            for label, prof in self.landmark_profiles.items():
                ref_feat = prof["feature_vector"]
                norm_u = np.linalg.norm(user_feat)
                norm_r = np.linalg.norm(ref_feat)
                if norm_u > 1e-4 and norm_r > 1e-4:
                    cos_sim = float(np.dot(user_feat, ref_feat) / (norm_u * norm_r))
                else:
                    cos_sim = 0.0

                # Finger count agreement heuristic bonus
                ref_ext = prof["extended_fingers"]
                if set(ref_ext) == set(ext_fingers):
                    cos_sim += 0.25
                elif len(ref_ext) == len(ext_fingers):
                    cos_sim += 0.10

                scores.append((label, max(0.0, min(1.0, cos_sim))))

            # Discrete Finger Classification Rules for Numerals (1 to 5)
            # Provides instant, rock-solid deterministic recognition
            non_thumb = [f for f in ext_fingers if f != "thumb"]
            if len(non_thumb) == 1 and non_thumb[0] == "index":
                discrete_guess = "1"
            elif len(non_thumb) == 2 and set(non_thumb) == {"index", "middle"}:
                discrete_guess = "2"
            elif len(non_thumb) == 3 and set(non_thumb) == {"index", "middle", "ring"}:
                discrete_guess = "3"
            elif len(non_thumb) == 4:
                discrete_guess = "4"
            elif len(ext_fingers) == 5:
                discrete_guess = "5"
            else:
                discrete_guess = None

            if scores:
                scores.sort(key=lambda x: x[1], reverse=True)
                top_landmark_label = scores[0][0]
                top_landmark_score = scores[0][1]
            else:
                top_landmark_label = discrete_guess
                top_landmark_score = None

            if discrete_guess and top_landmark_score is not None:
                top_landmark_label = discrete_guess

            # Prediction must be independent of the requested target. The
            # previous target-conditioned form evaluator could return the
            # target itself as the prediction, making a match tautological.
            form_eval = None
            accuracy_tier = "UNASSESSED"
            final_label = discrete_guess or top_landmark_label
            raw_similarity = round(top_landmark_score, 3) if top_landmark_score is not None else None
            is_uncertain = True
            status = "uncertain"
            message = (f"Possible candidate: '{final_label}'. This unvalidated template similarity "
                       "is not a probability or verified recognition.") if final_label else "No supported class candidate."

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Direct 2D coordinates across full camera frame
            full_lms_2d = [
                [
                    round(float(pt[0]), 4),
                    round(float(pt[1]), 4)
                ]
                for pt in primary["landmarks_2d"]
            ]

            diagnostics_payload = {
                "hands_detected": pose_data.get("hands_count", 1),
                "primary_hand": {
                    "finger_states": primary["finger_states"],
                    "extended_fingers": primary["extended_fingers"],
                    "extended_count": primary["extended_count"],
                    "palm_facing": primary["palm_facing"],
                    "landmarks_2d": full_lms_2d
                },
                "accuracy_tier": accuracy_tier,
                "missing_fingers": form_eval.get("missing_fingers", []) if form_eval else [],
                "extra_fingers": form_eval.get("extra_fingers", []) if form_eval else [],
                "steadiness": steadiness,
                "form_status": form_eval.get("status", status) if form_eval else status,
                "advice": form_eval.get("advice", message) if form_eval else message
            }

            return {
                "status": status,
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "hand_landmarks_detected",
                "predicted_sign": final_label,
                "confidence": None,
                "raw_score": raw_similarity,
                "score_type": "unvalidated_template_similarity" if raw_similarity is not None else "unavailable",
                "accuracy_tier": accuracy_tier,
                "margin": None,
                "is_uncertain": is_uncertain,
                "top_candidates": [{"label": l, "raw_score": round(float(s), 3),
                                    "score_type": "unvalidated_template_similarity"} for l, s in scores[:4]],
                "latency_ms": round(latency_ms, 2),
                "message": message,
                "diagnostics": diagnostics_payload
            }

        # If MediaPipe analyzer is available and found no hand, DO NOT guess on face or background!
        if self.pose_analyzer and self.pose_analyzer.available:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "status": "no_hand_detected",
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "no_hand_detected",
                "predicted_sign": None,
                "confidence": None,
                "accuracy_tier": "NO_HAND",
                "margin": 0.0,
                "is_uncertain": False,
                "top_candidates": [],
                "latency_ms": round(latency_ms, 2),
                "message": "Hand not visible. Raise your hand in front of the camera when you're ready.",
                "diagnostics": {
                    "hands_detected": 0,
                    "primary_hand": None,
                    "accuracy_tier": "NO_HAND",
                    "missing_fingers": [],
                    "extra_fingers": [],
                    "steadiness": 0.0,
                    "form_status": "no_hand",
                    "advice": "Hand not visible. Raise your hand in front of the camera when you're ready."
                }
            }

        # -------------------------------------------------------------
        # STEP 2: Legacy Fallback (ONLY used if MediaPipe model is completely unavailable)
        # -------------------------------------------------------------
        canny, skin = self._preprocess_roi(roi)
        skin_coverage = np.count_nonzero(skin) / (skin.shape[0] * skin.shape[1])
        edge_coverage = np.count_nonzero(canny) / (canny.shape[0] * canny.shape[1])

        if skin_coverage < 0.025 and edge_coverage < 0.005:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "status": "no_hand_detected",
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "skin_mask_below_candidate_floor",
                "predicted_sign": None,
                "confidence": None,
                "accuracy_tier": "NO_HAND",
                "is_uncertain": False,
                "latency_ms": round(latency_ms, 2),
                "message": "No hand detected. Raise your hand in front of the camera to begin."
            }

        # Check border cut-off
        top_cut = np.count_nonzero(skin[0, :]) > (skin.shape[1] * 0.85)
        bottom_cut = np.count_nonzero(skin[-1, :]) > (skin.shape[1] * 0.85)
        left_cut = np.count_nonzero(skin[:, 0]) > (skin.shape[0] * 0.85)
        right_cut = np.count_nonzero(skin[:, -1]) > (skin.shape[0] * 0.85)
        if (top_cut and bottom_cut and left_cut and right_cut):
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "status": "hand_outside_region",
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "roi_border_truncation_suspected",
                "predicted_sign": None,
                "confidence": None,
                "is_uncertain": True,
                "latency_ms": round(latency_ms, 2),
                "message": "Hand is partially outside the practice boundary. Center both hands inside the frame."
            }

        sample_moments = self._extract_shape_descriptors(canny, skin)
        scores = []
        for label, ref in self.reference_features.items():
            ref_moments = ref["moments"]
            diff = np.abs(sample_moments - ref_moments)
            weights = np.array([1.2, 1.2, 1.0, 1.0, 0.8, 0.8, 0.8, 2.5, 2.5], dtype=np.float32)
            dist = np.sum(diff * weights)
            similarity = 1.0 / (1.0 + float(dist) * 0.15)
            scores.append((label, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_label, top_score = scores[0]
        second_label, second_score = scores[1] if len(scores) > 1 else ("", 0.0)
        margin = top_score - second_score
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Historical thresholds are retained for comparison only, not acceptance.

        # These acceptance thresholds have not been tuned on an independent
        # validation set. Return a candidate only and abstain from accepting it.
        status = "uncertain"
        is_uncertain = True
        message = f"Possible candidate: '{top_label}'. Similarity is unvalidated; this is not a probability or verified recognition."

        return {
            "status": status,
            "model_version": self.model_version,
            "preprocessing_path": self.preprocessing_path,
            "input_validity": "skin_mask_candidate_present",
            "predicted_sign": top_label,
            "confidence": None,
            "raw_score": round(float(top_score), 3),
            "score_type": "unvalidated_template_similarity",
            "margin": round(float(margin), 3),
            "is_uncertain": is_uncertain,
            "top_candidates": [{"label": l, "raw_score": round(float(s), 3),
                                "score_type": "unvalidated_template_similarity"} for l, s in scores[:4]],
            "latency_ms": round(latency_ms, 2),
            "message": message
        }

    def recognize_base64_frame(
        self,
        base64_str: str,
        target_sign: Optional[str] = None,
        roi_box: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """Decodes a base64 JPEG/PNG string and executes recognition."""
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            img_bytes = base64.b64decode(base64_str)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Do not forward the requested target into raw inference.
            return self.recognize_frame(frame, roi_box=roi_box)
        except Exception as e:
            return {
                "status": "error",
                "model_version": self.model_version,
                "preprocessing_path": self.preprocessing_path,
                "input_validity": "frame_decode_failed",
                "predicted_sign": None,
                "confidence": None,
                "is_uncertain": True,
                "latency_ms": 0.0,
                "message": f"Frame decode failure: {str(e)}"
            }

# Singleton
engine = RecognitionEngine()
