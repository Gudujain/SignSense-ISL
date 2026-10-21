"""Regression coverage for the conservative attempt assessment contract."""
import unittest

from src.engine.assessment import assess_attempt


def frame(label, status="recognized", hands=1):
    return {"predicted_sign": label, "inference_status": status,
            "hands_detected": hands, "score": 0.8}


def final(label, status="recognized"):
    return {"predicted_sign": label, "status": status, "confidence": 0.8,
            "diagnostics": {"hands_detected": 1, "primary_hand": {
                "landmarks_2d": [[0.5, 0.5]] * 21}}}


class TrustworthyAssessmentTests(unittest.TestCase):
    def test_stable_target_candidate_is_not_graded_correct(self):
        result = assess_attempt(final("1"), "1", observations=[frame("1")] * 4)
        self.assertEqual(result["attempt_assessment"]["status"], "UNCERTAIN")
        self.assertFalse(result["attempt_assessment"]["is_correct"])
        self.assertFalse(result["can_update_mastery"])
        self.assertFalse(result["model_evidence"]["is_calibrated"])
        self.assertIsNone(result["model_evidence"]["calibrated_confidence"])

    def test_stable_different_candidate_is_not_graded_incorrect_without_validation(self):
        result = assess_attempt(final("2"), "1", observations=[frame("2")] * 4)
        self.assertEqual(result["attempt_assessment"]["status"], "UNCERTAIN")
        self.assertEqual(result["attempt_assessment"]["predicted_sign"], "2")

    def test_fluctuating_predictions_are_uncertain(self):
        obs = [frame("1"), frame("2"), frame("1"), frame("2")]
        result = assess_attempt(final("1"), "1", observations=obs)
        self.assertEqual(result["attempt_assessment"]["status"], "UNCERTAIN")

    def test_insufficient_observations_are_uncertain(self):
        result = assess_attempt(final("1"), "1", observations=[frame("1")] * 2)
        self.assertEqual(result["attempt_assessment"]["status"], "UNCERTAIN")

    def test_missing_hand_and_inference_failure_not_assessed(self):
        no_hand = assess_attempt({"status": "no_hand_detected"}, "1", observations=[])
        failed = assess_attempt({"status": "error"}, "1", observations=[])
        self.assertEqual(no_hand["attempt_assessment"]["status"], "NOT_ASSESSED")
        self.assertEqual(failed["attempt_assessment"]["status"], "NOT_ASSESSED")
        self.assertFalse(failed["can_update_mastery"])

    def test_unavailable_pose_is_never_reported_as_a_pass(self):
        result = assess_attempt(final("1"), "1", observations=[frame("1")] * 4)
        self.assertEqual(result["pose_evidence"]["validated_checks"]["palm_orientation"]["status"], "unavailable")
        self.assertFalse(result["pose_evidence"]["all_checks_passed"])


if __name__ == "__main__":
    unittest.main()
