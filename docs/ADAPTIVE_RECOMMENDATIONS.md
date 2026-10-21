# SignSense: Adaptive Learning & Recommendation Engine

> **Module**: `src/engine/recommender.py`, `src/engine/learner_model.py`, `src/engine/assessment.py`  
> **Status**: Verified with Automated Unit Tests Across Multiple Synthetic Learner Histories

---

## 1. Core Educational Philosophy

SignSense does not treat machine learning output as an authoritative judge of human proficiency. The core differentiator of SignSense is its **human-in-the-loop adaptive pedagogical engine**:
1. **Decoupling Inference from Assessment**: A computer vision prediction is merely evidence; educational assessment requires learner confirmation and context.
2. **Deterministic Explainability**: Every recommendation displays the explicit rule name and the underlying historical evidence that triggered it (e.g., *"Practise because your last 2 attempts were inconsistent"*).
3. **Learner Autonomy**: The learner is never locked into a path. All suggestions are dismissible, and any sign across all 6 stages can be practiced at will.
4. **Protection Against System Errors**: Classifier uncertainty or technical glitches **never** lower a learner's mastery score.

---

## 2. Decoupled Learning Loop

```
       [Video Frame] 
             │
             ▼
     recognize_sign()               <-- Pure computer vision inference
             │
             ▼
    stabilize_prediction()          <-- Temporal noise reduction (N=8 frames)
             │
             ▼
       assess_attempt()             <-- Incorporates learner confirmation & discrepancy
             │
             ▼
    update_learner_model()          <-- Updates mastery score & spaced repetition ladder
             │
             ▼
recommend_next_activity()           <-- Evaluates explainable pedagogical rules
```

---

## 3. Prioritized Recommendation Rules

When computing next activities, `RecommendationEngine.get_recommendations()` evaluates candidates in strict priority order:

| Rule ID | Pedagogical Purpose | Trigger Condition | System Explanation Presented to Learner |
| :--- | :--- | :--- | :--- |
| **`REPEATED_DIFFICULTY`** *(Priority: 100+)* | Remedial intervention for struggling gestures | Learner has $\ge 2$ consecutive confirmed failures on Sign $X$ | *"Practise this sign again because your last $N$ attempts were inconsistent. Replay the reference demonstration and hold the pose steady."* |
| **`SPACED_REVISION`** *(Priority: 80+)* | Long-term memory consolidation (Ebbinghaus decay) | Mastered sign ($\text{mastery} \ge 0.40$) has $\text{now} \ge \text{next\_review\_at}$ | *"Review sign '$X$' because it is due for scheduled spaced revision to strengthen your long-term memory."* |
| **`UNCERTAIN_RECOVERY`** *(Priority: 70)* | Camera and environmental positioning assistance | Most recent attempt on Sign $X$ had status `"uncertain"` | *"The last attempt for sign '$X$' was uncertain. Adjust your distance from camera and retry inside the guide rectangle."* |
| **`CONSISTENT_SUCCESS_ADVANCE`** *(Priority: 60)* | Curriculum advancement upon demonstrated mastery | Current sign has $\ge 3$ consecutive successes and $\text{mastery} \ge 0.70$ | *"Try new sign '$Y$' because you have achieved consistent mastery ($M\%$) on '$X$'."* |
| **`NEGLECTED_SIGN`** *(Priority: 40+)* | Preventing skill atrophy in active stages | Previously attempted sign has not been practiced in $> 48\text{ hours}$ | *"Revisit '$X$' because you have not practiced it in $D$ days."* |
| **`CURRICULUM_PROGRESSION`** *(Priority: 20)* | Baseline structured learning path | Default when no remedial, revision, or advancement rules are active | *"Start learning sign '$X$' in Stage $S$ to build your core ISL vocabulary."* |

---

## 4. Spaced Repetition Interval Ladder

To maintain retention without causing learner burnout, SignSense implements an expanding review interval ladder:
$$\text{Ladder} = [1.0\text{h},\; 4.0\text{h},\; 24.0\text{h},\; 72.0\text{h},\; 168.0\text{h}\; (7\text{ days})]$$

- **On Confirmed Success**:
  - Mastery score increments: $\text{mastery} = \text{mastery} + (1.0 - \text{mastery}) \times 0.35$.
  - Interval advances to the next step on the ladder (e.g., from 4 hours to 24 hours).
  - Next review scheduled: $\text{next\_review\_at} = \text{now} + (\text{interval} \times 3600)$.
- **On Confirmed Failure**:
  - Mastery score decreases moderately: $\text{mastery} = \max(0.0, \text{mastery} - 0.20)$.
  - Review interval resets to the baseline rung ($1.0\text{ hour}$).
- **On Uncertainty / Technical Glitch**:
  - Mastery score and review intervals remain **strictly unchanged**.

---

## 5. Verification Across Three Distinct Learner Histories

In `tests/test_recommender.py`, automated tests demonstrate that the recommendation engine produces meaningfully different next activities across diverse learning trajectories:

### History A: Struggling Learner
- **Behavior**: Learner repeatedly fails Sign '1' three consecutive times.
- **Resulting Recommendation**: `REPEATED_DIFFICULTY` triggered on Sign '1', prioritizing remedial reference review.

### History B: Proficient Learner
- **Behavior**: Learner completes 3 consecutive successful attempts on Sign '1' ($\text{mastery} \ge 70\%$).
- **Resulting Recommendation**: `CONSISTENT_SUCCESS_ADVANCE` triggered, advancing the learner to Sign '2'.

### History C: Spaced Revision Learner
- **Behavior**: Learner previously mastered Sign '1', but 3 hours have passed since review expiration.
- **Resulting Recommendation**: `SPACED_REVISION` triggered on Sign '1', prioritizing memory consolidation.
