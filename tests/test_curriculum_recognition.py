"""Unvalidated pose heuristics must remain unavailable to learner grading."""
from src.recognition.pose_analyzer import HandPoseAnalyzer


def analyzer_without_native_runtime():
    """The pure form-evaluation method needs no native MediaPipe task."""
    return object.__new__(HandPoseAnalyzer)


def test_even_matching_single_hand_pose_is_not_graded():
    analyzer = analyzer_without_native_runtime()
    pose = {
        "detected": True,
        "hands_count": 1,
        "primary_hand": {
            "finger_states": {"index": True, "middle": False, "ring": False, "pinky": False},
            "extended_fingers": ["index"], "palm_facing": "camera",
        },
        "steadiness": 0.9,
    }
    result = analyzer.evaluate_sign_form("1", pose)
    assert result["match"] is None
    assert result["accuracy_tier"] == "UNASSESSED"
    assert "confidence" not in result


def test_wrong_or_incomplete_pose_is_not_misrepresented_as_validated_feedback():
    analyzer = analyzer_without_native_runtime()
    pose = {"detected": True, "hands_count": 1, "primary_hand": {}, "steadiness": 0.4}
    result = analyzer.evaluate_sign_form("7", pose)
    assert result["accuracy_tier"] == "UNASSESSED"
    assert result["checks"] == {}
    assert "unavailable" in result["advice"].lower()


def test_no_hand_remains_a_tracking_result():
    analyzer = analyzer_without_native_runtime()
    result = analyzer.evaluate_sign_form("1", {"detected": False})
    assert result["accuracy_tier"] == "NO_HAND"
    assert result["match"] is None
