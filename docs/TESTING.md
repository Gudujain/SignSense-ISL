# SignSense: Testing & Verification Guide

> **Audit correction (2026-10):** Previous pass-rate and manual-camera claims are not reproducible from this checkout. The ML evaluation is blocked on missing labeled images and split metadata; see [ML_EVALUATION_STATUS.md](ML_EVALUATION_STATUS.md). Do not treat the legacy test suite as evidence of recognition accuracy.

---

## 1. Quick Execution Commands

### 1.1 Run Complete Automated Test Suite
```bash
python -m pytest tests/ -v
```

### 1.2 Run Specific Test Suites
```bash
# Recognition Engine, Stability Buffer & Diagnostics
python -m pytest tests/test_recognition.py -v

# Adaptive Recommendation Rules & Multi-Scenario Histories
python -m pytest tests/test_recommender.py -v

# REST API & Assessment Integration Endpoints
python -m pytest tests/test_api.py -v
```

### 1.3 Reproduce Baseline Recognition Audit
```bash
python baseline_evaluator.py
```
*Outputs quantitative accuracy, per-class F1, and confusion matrix from `submission_svm.csv` to `docs/BASELINE_AUDIT_REPORT.md`.*

### 1.4 Launch Application Server
```bash
python src/server/app.py
```
*Accessible at `http://127.0.0.1:5000`.*

---

## 2. Automated Test Suite Breakdown

### 2.1 Recognition & Robustness Tests (`tests/test_recognition.py`)
- `test_empty_or_none_frame_handling`: Verifies engine returns structured error status rather than crashing on empty image buffers.
- `test_no_hand_detected_on_blank_image`: Verifies blank/black frame emits `no_hand_detected` with actionable message.
- `test_reference_sign_1_recognition`: Verifies model recognizes ground-truth reference sign '1' within latency bounds ($<50\text{ ms}$).
- `test_stability_buffer_requires_consensus`: Proves that temporal noise and fluctuating frames are filtered until $\ge 65\%$ consensus is achieved across $N=8$ frames.
- `test_diagnostics_metrics_calculation`: Verifies calculation of camera FPS, inference rate, and latency averages.

### 2.2 Adaptive Recommendation Tests (`tests/test_recommender.py`)
- `test_initial_state_recommends_curriculum_start`: Proves that insufficient history defaults to curriculum start (Sign '1').
- `test_history_a_struggling_learner_triggers_repeated_difficulty`: Verifies that a learner who fails 3 consecutive attempts on Sign '1' triggers `REPEATED_DIFFICULTY` recommending remedial practice on Sign '1'.
- `test_history_b_proficient_learner_triggers_consistent_success_advance`: Verifies that 3 consecutive successes ($\text{mastery} \ge 70\%$) on Sign '1' triggers `CONSISTENT_SUCCESS_ADVANCE` advancing the learner to Sign '2'.
- `test_history_c_mastered_learner_with_overdue_spaced_revision`: Verifies that an expired spaced review interval triggers `SPACED_REVISION` to consolidate memory.
- `test_uncertainty_does_not_lower_mastery_and_triggers_recovery`: Proves that an uncertain prediction does not decrease learner mastery score and triggers `UNCERTAIN_RECOVERY`.
- `test_learner_can_dismiss_recommendation`: Proves that learner can dismiss suggestions to exercise educational autonomy.

### 2.3 API Integration Tests (`tests/test_api.py`)
- `test_index_route`: Validates static HTML delivery.
- `test_curriculum_endpoint`: Validates retrieval of 35 signs and 6 stages.
- `test_curriculum_single_sign_endpoint`: Validates detailed instructions for individual signs.
- `test_learner_progress_endpoint`: Validates calculation of real-time progress metrics.
- `test_recommendations_endpoint`: Validates prioritized, explainable recommendation payloads.
- `test_recognize_endpoint_with_blank_image`: Validates base64 frame ingestion and error response.
- `test_assess_and_feedback_flow`: Validates end-to-end assessment, mastery update, and immediate fresh recommendation delivery ($<0.5\text{ s}$).
- `test_diagnostics_endpoint`: Validates performance HUD metrics endpoint.
- `test_history_clear_endpoint`: Validates database reset on user confirmation.

---

## 3. End-to-End Browser Subagent Verification Summary

On October 17, 2026, a comprehensive automated browser subagent audited all 8 core application screens on `http://127.0.0.1:5000`:
- **Screen A (Onboarding)**: Interactive goal selection and privacy guarantee verified.
- **Screen B (Dashboard)**: Real stats cards, recommendation hero, and revision queue verified.
- **Screen C (Curriculum)**: All 6 stages rendered; clicking Sign '1' successfully opens the detailed reference demonstration modal with full ISL instructions.
- **Screen D & E (Practice & Feedback)**: Live webcam preview layout, cyan ROI guide overlay, steadiness progress bar, and confirmation override buttons verified.
- **Screen F (Recommendations)**: Explainable recommendation cards with rule rationale verified.
- **Screen G (History)**: Practice analytics and attempt log table verified.
- **Screen H (Settings)**: Privacy disclosure, research consent toggle, and high-contrast accessibility verified.
- **Diagnostics HUD**: Dev HUD toggle confirmed functional, displaying live camera FPS, inference rate, and latency.
