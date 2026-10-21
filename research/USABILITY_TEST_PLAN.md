# SignSense Usability Testing Protocol & Evaluation Plan

> **Study Type**: Within-Subjects Usability Evaluation & Comparative A/B Trial  
> **Target Cohort**: $N = 10\text{--}12$ participants across novice and intermediate ISL learners  
> **Evaluation Framework**: Mixed-Methods (Task Completion Metrics + SUS Usability + Cognitive Load + Thematic Debrief)

---

## 1. Evaluation Objectives
1. Assess the usability, accessibility, and navigation efficiency of the SignSense interface.
2. Evaluate learner comprehension of the real-time feedback box, stability meter, and transparent uncertainty states.
3. Compare user experience, perceived usefulness, and cognitive load between:
   - **Condition A (Baseline)**: Fixed, linear curriculum progression (Signs 1 $\rightarrow$ 2 $\rightarrow$ 3 ... without adaptation).
   - **Condition B (SignSense)**: Explainable adaptive recommendation engine with spaced revision and remedial practice rules.

---

## 2. Standardized Usability Task Protocol

Each participant will complete the following 9 realistic learner tasks in sequential order:

| Task ID | Task Description | Acceptance / Success Criterion | Expected Max Duration |
| :---: | :--- | :--- | :---: |
| **T01** | **Curriculum Discovery**: Navigate to the curriculum catalogue, locate Stage 1, and open the detailed reference demonstration for Sign '1'. | Modal opens displaying large reference image, handshape instructions, and provenance. | 45 sec |
| **T02** | **Reference Comprehension**: Read the verified instruction for Sign '1' and identify whether it is a one-handed or two-handed sign. | Participant correctly states: "One-handed, index finger pointing up". | 30 sec |
| **T03** | **Practice Initialization**: Launch the practice screen and activate the webcam. Align hand within the cyan practice guide box. | Live camera preview active; hand positioned within guide box; status dot turns green. | 45 sec |
| **T04** | **Hold Pose & Stabilization**: Form Sign '1' and hold it steady until the stability meter reaches 100% and a stable prediction triggers. | Stability bar fills smoothly; system displays recognized prediction without flickering. | 30 sec |
| **T05** | **Recover from Uncertain State**: Intentionally create an ambiguous pose (e.g., partial hand occlusion or dimming light) to trigger an "Uncertain" status, then follow feedback instructions to recover. | Participant reads constructive message, repositions hand inside guide, and retries. | 60 sec |
| **T06** | **Handle Different Prediction**: Form Sign '2' while target is '1', observe the constructive feedback message, and decide whether to confirm, correct, or retry. | Participant reads "System recognized 2 instead of 1" and successfully uses retry or confirmation. | 45 sec |
| **T07** | **Recommendation Discovery & Explanation**: Navigate to the Dashboard or Recommendations tab, identify the suggested next sign, and explain *why* it was recommended. | Participant reads the explanation string (e.g., citing consecutive errors or spaced revision). | 45 sec |
| **T08** | **Progress Review & Discrepancy Inspection**: Navigate to History tab, locate their recent practice attempt, and distinguish between model prediction and learner confirmation. | Participant successfully identifies their attempt row and explains whether it was confirmed correct. | 45 sec |
| **T09** | **Privacy & History Control**: Navigate to Settings, locate the data retention section, and trigger a history reset with confirmation. | Participant executes history reset; confirms prompt; dashboard resets cleanly to zero. | 45 sec |

---

## 3. Quantitative & Qualitative Metrics

### 3.1 Quantitative Measures
- **Task Completion Rate (TCR)**: Percentage of tasks completed without experimenter intervention.
- **Time on Task (ToT)**: Duration (seconds) recorded per task.
- **Error Frequency**: Count of unassisted recovery slips or misclicks per task.
- **System Usability Scale (SUS)**: Standardized 10-item questionnaire score (target $> 80/100$, Grade A).
- **Inference & Feedback Latency**: Background system logs measuring frame rate (FPS), model inference (ms), and visible feedback latency (ms).

### 3.2 Qualitative Measures
- **Think-Aloud Protocol**: Participants verbalize their thought process during practice.
- **Trust & Calibrated Confidence**: Semi-structured debrief exploring whether learners felt supported or patronized by AI feedback.
- **Perceived Autonomy**: Participant rating of freedom to override suggestions versus being coerced by an algorithm.

---

## 4. Fixed vs. Adaptive Comparative Protocol

To fairly evaluate **Research Question 2** ($\text{RQ}_2$):
1. **Counterbalanced Grouping**: Half the participants ($N=6$) experience Condition A (Fixed) followed by Condition B (Adaptive); the other half experience Condition B followed by Condition A.
2. **Standardized Content**: Both conditions cover the same set of 5 signs (Numerals 1–5).
3. **Practice Constraints**: Equal total practice time (10 minutes per condition).
4. **Post-Condition Assessment**: Immediately following each condition, participants complete the SUS questionnaire and rate perceived cognitive load on a 1–7 scale.
