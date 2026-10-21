"""MediaPipe landmark extraction only; no learner-facing pose checks validated."""
import os
import threading
import numpy as np
import time
from collections import deque
from typing import Dict, Any, Optional, Tuple, List

try:
    import cv2
except ImportError as exc:
    raise ImportError("SignSense camera inference requires OpenCV. Install the project requirements in the active environment.") from exc

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False



class HandPoseAnalyzer:
    def __init__(self, model_path: Optional[str] = None):
        self.available = False
        self.detector = None
        self.initialization_error = None
        self.history_positions: deque = deque(maxlen=10)
        self.last_timestamp: float = 0.0

        if not MEDIAPIPE_AVAILABLE:
            self.initialization_error = "MediaPipe Python package is not installed."
            return

        if model_path is None:
            # Check models directory relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, "models", "hand_landmarker.task")
        self.model_path = model_path

        if not os.path.exists(model_path):
            self._try_download_model(model_path)

        if os.path.exists(model_path):
            try:
                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    num_hands=2,
                    min_hand_detection_confidence=0.4,
                    min_hand_presence_confidence=0.4,
                    min_tracking_confidence=0.4
                )
                self.detector = vision.HandLandmarker.create_from_options(options)
                self.available = True
            except Exception as e:
                self.initialization_error = f"Hand landmarker initialization failed: {e}"
                print(f"[HandPoseAnalyzer] {self.initialization_error}")
                self.available = False
        else:
            self.initialization_error = f"Hand landmarker task file is unavailable: {model_path}"

    def _try_download_model(self, dest_path: str):
        """Attempts to download the official hand landmarker model if missing."""
        import urllib.request
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, dest_path)
        except Exception as e:
            self.initialization_error = f"Could not download hand landmarker model to {dest_path}: {e}"
            print(f"[HandPoseAnalyzer] Could not download landmarker model: {e}")

    def analyze_frame(self, frame_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Runs full 3D hand landmark detection and biomechanical extraction on a BGR frame.
        """
        if not self.available or self.detector is None or frame_bgr is None or frame_bgr.size == 0:
            return {"detected": False, "hands_count": 0}

        try:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            res = self.detector.detect(mp_image)
        except Exception as e:
            return {"detected": False, "hands_count": 0, "error": str(e)}

        hands_count = len(res.hand_landmarks)
        if hands_count == 0:
            return {
                "detected": False,
                "hands_count": 0,
                "steadiness": 0.0,
                "message": "No hand detected in the frame."
            }

        # Analyze primary hand (largest or first)
        primary_lms = res.hand_landmarks[0]
        handedness = "Right"
        if hasattr(res, "handedness") and len(res.handedness) > 0 and len(res.handedness[0]) > 0:
            handedness = res.handedness[0][0].category_name
        hand_info = self._extract_hand_features(primary_lms, handedness=handedness)

        # Update steadiness tracking based on wrist & knuckle stability
        steadiness = self._update_steadiness(primary_lms)
        hand_info["steadiness"] = steadiness

        # If a secondary hand is present (dual-hand ISL alphabet)
        second_hand_info = None
        dual_hand_distance = None
        if hands_count > 1:
            second_lms = res.hand_landmarks[1]
            h2 = "Left" if handedness == "Right" else "Right"
            if len(res.handedness) > 1 and len(res.handedness[1]) > 0:
                h2 = res.handedness[1][0].category_name
            second_hand_info = self._extract_hand_features(second_lms, handedness=h2)
            # Distance between wrists
            w1 = np.array([primary_lms[0].x, primary_lms[0].y, primary_lms[0].z])
            w2 = np.array([second_lms[0].x, second_lms[0].y, second_lms[0].z])
            dual_hand_distance = round(float(np.linalg.norm(w1 - w2)), 3)

        return {
            "detected": True,
            "hands_count": hands_count,
            "primary_hand": hand_info,
            "second_hand": second_hand_info,
            "dual_hand_distance": dual_hand_distance,
            "steadiness": steadiness
        }

    def close(self):
        """Release the native MediaPipe task and its worker threads."""
        detector, self.detector = self.detector, None
        self.available = False
        if detector is not None:
            try:
                detector.close()
            except Exception as exc:
                self.initialization_error = f"Hand landmarker shutdown failed: {exc}"

    def _extract_hand_features(self, landmarks, handedness: str = "Right") -> Dict[str, Any]:
        """Extracts finger extension states, palm orientation, and normalized coordinates."""
        wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z], dtype=np.float32)
        idx_mcp = np.array([landmarks[5].x, landmarks[5].y, landmarks[5].z], dtype=np.float32)
        mid_mcp = np.array([landmarks[9].x, landmarks[9].y, landmarks[9].z], dtype=np.float32)
        pky_mcp = np.array([landmarks[17].x, landmarks[17].y, landmarks[17].z], dtype=np.float32)

        # Hand scale: wrist to middle MCP distance
        hand_scale = float(np.linalg.norm(mid_mcp - wrist))
        if hand_scale < 1e-4:
            hand_scale = 1.0

        # Finger landmark indices: (MCP, PIP, DIP, TIP)
        finger_indices = {
            "index": (5, 6, 7, 8),
            "middle": (9, 10, 11, 12),
            "ring": (13, 14, 15, 16),
            "pinky": (17, 18, 19, 20)
        }

        finger_states = {}
        extended_list = []

        # Non-thumb fingers
        for fname, (mcp_i, pip_i, dip_i, tip_i) in finger_indices.items():
            tip = np.array([landmarks[tip_i].x, landmarks[tip_i].y, landmarks[tip_i].z], dtype=np.float32)
            pip = np.array([landmarks[pip_i].x, landmarks[pip_i].y, landmarks[pip_i].z], dtype=np.float32)
            mcp = np.array([landmarks[mcp_i].x, landmarks[mcp_i].y, landmarks[mcp_i].z], dtype=np.float32)

            d_tip_wrist = np.linalg.norm(tip - wrist)
            d_pip_wrist = np.linalg.norm(pip - wrist)
            d_tip_mcp = np.linalg.norm(tip - mcp)

            # Extended if tip is clearly further from wrist than PIP and MCP
            is_ext = bool((d_tip_wrist > d_pip_wrist * 1.05) and (d_tip_mcp > hand_scale * 0.65))
            finger_states[fname] = is_ext
            if is_ext:
                extended_list.append(fname)

        # Thumb detection
        # Thumb: 1 (CMC), 2 (MCP), 3 (IP), 4 (TIP)
        t_tip = np.array([landmarks[4].x, landmarks[4].y, landmarks[4].z], dtype=np.float32)
        t_ip = np.array([landmarks[3].x, landmarks[3].y, landmarks[3].z], dtype=np.float32)
        t_mcp = np.array([landmarks[2].x, landmarks[2].y, landmarks[2].z], dtype=np.float32)

        d_thumb_pky = np.linalg.norm(t_tip - pky_mcp) / hand_scale
        d_thumb_idx = np.linalg.norm(t_tip - idx_mcp) / hand_scale
        d_thumb_tip_mcp = np.linalg.norm(t_tip - t_mcp) / hand_scale

        # Thumb extended if pointing away from palm and tip is distant from index/pinky bases
        thumb_extended = bool(d_thumb_pky > 1.25 and d_thumb_idx > 0.65 and d_thumb_tip_mcp > 0.75)
        finger_states["thumb"] = thumb_extended
        if thumb_extended:
            extended_list.append("thumb")

        # Specific inter-finger metrics
        idx_tip = np.array([landmarks[8].x, landmarks[8].y, landmarks[8].z], dtype=np.float32)
        mid_tip = np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z], dtype=np.float32)
        pky_tip = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z], dtype=np.float32)

        idx_mid_dist = float(np.linalg.norm(idx_tip - mid_tip) / hand_scale)
        thumb_pky_dist = float(np.linalg.norm(t_tip - pky_tip) / hand_scale)

        # Palm normal vector
        v_idx = idx_mcp - wrist
        v_pky = pky_mcp - wrist
        normal = np.cross(v_idx, v_pky)
        if handedness == "Left":
            normal = -normal
        norm_len = np.linalg.norm(normal)
        if norm_len > 1e-4:
            normal = normal / norm_len

        # Normal z interpretation with handedness correction
        # Relaxed for natural laptop camera angles (screen tilted back 15-30 deg)
        if normal[2] < 0.40:
            palm_facing = "camera"
        elif normal[2] > 0.65:
            palm_facing = "away"
        else:
            palm_facing = "side"

        # Normalized 2D coordinates for canvas overlay [ [x, y], ... ]
        lms_2d = [[round(float(lm.x), 4), round(float(lm.y), 4)] for lm in landmarks]

        # Normalized 3D feature vector (relative to wrist and scaled)
        norm_coords = []
        for lm in landmarks:
            norm_coords.extend([
                float((lm.x - wrist[0]) / hand_scale),
                float((lm.y - wrist[1]) / hand_scale),
                float((lm.z - wrist[2]) / hand_scale)
            ])

        return {
            "finger_states": finger_states,
            "extended_fingers": extended_list,
            "extended_count": len(extended_list),
            "palm_facing": palm_facing,
            "index_middle_distance": round(idx_mid_dist, 3),
            "thumb_pinky_distance": round(thumb_pky_dist, 3),
            "hand_scale": round(hand_scale, 3),
            "landmarks_2d": lms_2d,
            "feature_vector": np.array(norm_coords, dtype=np.float32)
        }

    def _update_steadiness(self, landmarks) -> float:
        """Calculates hand steadiness (0.0 to 1.0) based on jitter over recent frames."""
        wrist = np.array([landmarks[0].x, landmarks[0].y], dtype=np.float32)
        mid_mcp = np.array([landmarks[9].x, landmarks[9].y], dtype=np.float32)
        pos = (wrist + mid_mcp) * 0.5
        self.history_positions.append(pos)

        if len(self.history_positions) < 3:
            return 0.70

        # Measure displacement variances across recent window
        diffs = [
            np.linalg.norm(self.history_positions[i] - self.history_positions[i - 1])
            for i in range(1, len(self.history_positions))
        ]
        avg_jitter = float(np.mean(diffs))
        # Scaled comfortably so natural human hand tremor does not penalize the learner
        steadiness = max(0.0, min(1.0, 1.0 - (avg_jitter / 0.055)))
        return round(float(steadiness), 2)

    def evaluate_sign_form(self, target_sign: str, pose_data: Dict[str, Any], ref_feature_vector=None) -> Dict[str, Any]:
        """Return unavailable until the pose heuristic is independently validated.

        Hand landmarks are still exposed as observations for research, but this
        prototype has no labeled signer-disjoint validation set for its finger
        or palm rules. These observations must not be promoted to pose grades.
        """
        detected = bool(pose_data and pose_data.get("detected"))
        return {
            "match": None,
            "status": "unvalidated_pose_evidence" if detected else "no_hand",
            "accuracy_tier": "UNASSESSED" if detected else "NO_HAND",
            "checks": {},
            "missing_fingers": [],
            "extra_fingers": [],
            "steadiness": pose_data.get("steadiness") if detected else 0.0,
            "advice": "Pose checks are unavailable until independently validated. Compare with the reference demonstration."
        }


# Global singleton
pose_analyzer = HandPoseAnalyzer()

# MediaPipe native task shutdown needs its dispatcher threads alive. CPython's
# threading exit hooks run before executor shutdown; ordinary atexit callbacks
# run too late for this dependency's native close implementation.
if hasattr(threading, "_register_atexit"):
    threading._register_atexit(pose_analyzer.close)
