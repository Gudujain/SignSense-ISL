"""
SignSense Real-Time Performance & Diagnostics Instrumentation
Tracks FPS, inference latency, prediction frequency, dropped frames,
and latency breakdowns as required by system performance specifications.
"""
import time
from collections import deque
from typing import Dict, Any, List

class PerformanceDiagnostics:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.inference_latencies: deque = deque(maxlen=window_size)
        self.frame_timestamps: deque = deque(maxlen=window_size)
        self.prediction_timestamps: deque = deque(maxlen=window_size)
        self.assessment_latencies: deque = deque(maxlen=window_size)
        self.recommendation_latencies: deque = deque(maxlen=window_size)
        self.dropped_frames: int = 0
        self.total_frames_received: int = 0
        self.total_predictions_made: int = 0
        self.total_errors: int = 0

    def record_frame_received(self):
        now = time.perf_counter()
        self.total_frames_received += 1
        self.frame_timestamps.append(now)

    def record_dropped_frame(self):
        self.dropped_frames += 1

    def record_inference(self, latency_ms: float):
        now = time.perf_counter()
        self.total_predictions_made += 1
        self.inference_latencies.append(latency_ms)
        self.prediction_timestamps.append(now)

    def record_assessment(self, latency_ms: float):
        self.assessment_latencies.append(latency_ms)

    def record_recommendation(self, latency_ms: float):
        self.recommendation_latencies.append(latency_ms)

    def record_error(self):
        self.total_errors += 1

    def get_metrics(self) -> Dict[str, Any]:
        now = time.perf_counter()

        # Calculate Camera / Ingestion FPS over recent window
        camera_fps = 0.0
        if len(self.frame_timestamps) > 1:
            duration = self.frame_timestamps[-1] - self.frame_timestamps[0]
            if duration > 0:
                camera_fps = (len(self.frame_timestamps) - 1) / duration

        # Calculate Recognition update frequency (predictions per sec)
        prediction_hz = 0.0
        if len(self.prediction_timestamps) > 1:
            p_dur = self.prediction_timestamps[-1] - self.prediction_timestamps[0]
            if p_dur > 0:
                prediction_hz = (len(self.prediction_timestamps) - 1) / p_dur

        # Latency statistics
        inf_list = list(self.inference_latencies)
        avg_inference_ms = sum(inf_list) / len(inf_list) if inf_list else 0.0
        p95_inference_ms = 0.0
        if inf_list:
            s_inf = sorted(inf_list)
            idx95 = int(len(s_inf) * 0.95)
            p95_inference_ms = s_inf[min(idx95, len(s_inf) - 1)]

        assess_list = list(self.assessment_latencies)
        avg_assess_ms = sum(assess_list) / len(assess_list) if assess_list else 0.0

        rec_list = list(self.recommendation_latencies)
        avg_rec_ms = sum(rec_list) / len(rec_list) if rec_list else 0.0

        return {
            "camera_fps": round(camera_fps, 1),
            "prediction_frequency_hz": round(prediction_hz, 1),
            "avg_inference_latency_ms": round(avg_inference_ms, 2),
            "p95_inference_latency_ms": round(p95_inference_ms, 2),
            "avg_assessment_latency_ms": round(avg_assess_ms, 2),
            "avg_recommendation_latency_ms": round(avg_rec_ms, 2),
            "total_frames_received": self.total_frames_received,
            "total_predictions_made": self.total_predictions_made,
            "dropped_frames": self.dropped_frames,
            "total_errors": self.total_errors,
            "targets": {
                "camera_fps_target": "24–30 FPS",
                "prediction_frequency_target": "10–20 Hz",
                "feedback_latency_target": "0.5–1.0 s",
                "recommendation_latency_target": "<0.5 s"
            }
        }

# Singleton
diagnostics = PerformanceDiagnostics()
