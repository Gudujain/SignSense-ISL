"""
SignSense Prediction Stabilizer
Prevents visual flicker and ensures predictions are stable before
attempt assessment, filtering erratic frame-to-frame fluctuations.
"""
from collections import deque, Counter
from typing import Optional, Dict, Any, List
import time

class PredictionStabilizer:
    def __init__(self, window_size: int = 8, min_consensus_ratio: float = 0.65, min_frames: int = 5, hold_threshold_frames: int = 5):
        self.window_size = window_size
        self.min_consensus_ratio = min_consensus_ratio
        self.min_frames = min_frames
        self.hold_threshold_frames = hold_threshold_frames
        self.history: deque = deque(maxlen=window_size)
        self.last_stable_sign: Optional[str] = None
        self.last_stable_time: float = 0.0
        self.consecutive_target_matches: int = 0
        self.consecutive_partial_matches: int = 0

    def reset(self):
        """Clears buffer (e.g. when starting a new practice attempt)."""
        self.history.clear()
        self.last_stable_sign = None
        self.last_stable_time = 0.0
        self.consecutive_target_matches = 0
        self.consecutive_partial_matches = 0

    def add_prediction(self, prediction_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests a frame prediction result, computes temporal consensus,
        and reports temporal candidate stability. Stability is not correctness.
        """
        now = time.time()
        status = prediction_dict.get("status")
        pred_sign = prediction_dict.get("predicted_sign")
        # This buffer can measure agreement only; it has no authority to grade.
        hold_progress = 0.0
        auto_verified = False
        stable_partial = False

        # Buffer predictions for consensus
        if status in ("recognized", "uncertain") and pred_sign:
            self.history.append((pred_sign, status, now))
        elif status in ("no_hand_detected", "hand_outside_region"):
            if self.history:
                self.history.popleft()

        total_frames = len(self.history)
        if total_frames < self.min_frames:
            return {
                "is_stable": False,
                "stable_sign": None,
                "status": "accumulating",
                "consensus_ratio": 0.0,
                "hold_progress": round(hold_progress, 2),
                "auto_verified": auto_verified,
                "stable_partial": stable_partial,
                "frames_buffered": total_frames,
                "target_frames": self.min_frames,
                "message": f"Hold sign steady ({total_frames}/{self.min_frames} frames)..."
            }

        signs = [s for s, st, t in self.history]
        counts = Counter(signs)
        most_common_sign, top_count = counts.most_common(1)[0]
        consensus_ratio = top_count / total_frames

        if consensus_ratio >= self.min_consensus_ratio:
            self.last_stable_sign = most_common_sign
            self.last_stable_time = now
            return {
                "is_stable": True,
                "stable_sign": most_common_sign,
                "status": "stable",
                "consensus_ratio": round(consensus_ratio, 2),
                "hold_progress": round(hold_progress, 2),
                "auto_verified": auto_verified,
                "stable_partial": stable_partial,
                "frames_buffered": total_frames,
                "target_frames": self.min_frames,
                "message": f"Stable sign '{most_common_sign}' detected ({int(consensus_ratio * 100)}% consensus)."
            }
        else:
            return {
                "is_stable": False,
                "stable_sign": None,
                "status": "fluctuating",
                "consensus_ratio": round(consensus_ratio, 2),
                "hold_progress": round(hold_progress, 2),
                "auto_verified": auto_verified,
                "stable_partial": stable_partial,
                "frames_buffered": total_frames,
                "target_frames": self.min_frames,
                "message": "Sign is fluctuating. Hold hand position still."
            }
