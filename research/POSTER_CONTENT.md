# SignSense: Adaptive Indian Sign Language Learning System
## Poster Presentation & Executive Research Summary

---

### [PANEL 1] Problem Statement & Target Learners
- **The Core Problem**: Most automated sign language projects are designed as brittle "sign-to-text translators" rather than pedagogical learning tools. When computer vision models encounter lighting changes or hand occlusion, they fail silently or guess wrong classes with deceptive 99% confidence, demoralizing beginners.
- **Target Learners**:
  1. *Hearing Novices*: Family members, friends, or coworkers of deaf individuals seeking structured fingerspelling practice.
  2. *Independent Adult Learners*: Practice in short daily intervals with privacy constraints.
  3. *Special Education Instructors*: Require authentic Indian Sign Language (ISL) two-handed conventions and explainable recommendations.

---

### [PANEL 2] Research Gap & Core Research Questions
- **The Research Gap**: Prior art either focuses on raw classifier accuracy (e.g., Karthikeyan et al., 2020) or theoretical interface critique (Bragg et al., ASSETS 2019). No existing ISL system combines real-time vision feedback, transparent uncertainty handling, learner-controlled error recovery, and explainable spaced revision into an end-to-end self-paced learning tool.
- **Primary Research Question ($\text{RQ}_1$)**:  
  *How can real-time sign recognition, learner-controlled feedback, and performance-based recommendations be integrated into an accessible learning interface for beginner ISL learners?*
- **Evaluation Question ($\text{RQ}_2$)**:  
  *How does adaptive practice influence usability, cognitive load, and perceived usefulness compared to a fixed practice sequence?*

---

### [PANEL 3] System Architecture & Data Flow
```
[Learner Web UI] <--- (HTTP/JSON API) ---> [Flask Modular Server]
       |                                          |
  Webcam Preview                         Recognition Engine
  (Canvas ROI Guide)                   (Edge/Contour/Moments + SIFT)
       |                                          |
   Video Frame ---------------------------> Raw Prediction
                                                  |
                                        Temporal Stability Buffer
                                         (8-frame sliding window)
                                                  |
[Feedback & Assessment UI] <---------- Stable Consensus Outcome
       |
Learner Confirmation / Override
       |
[Learner Model & Storage] (SQLite) ---> [Explainable Recommender]
 (Per-sign mastery, decay ladder)       (Deterministic Pedagogical Rules)
                                                  |
                                        Next Personalized Lesson
```

---

### [PANEL 4] Core Pedagogical Rules of the Adaptive Engine
1. **Repeated Difficulty (`REPEATED_DIFFICULTY`)**: If consecutive failures $\ge 2$, prioritize remedial practice with step-by-step reference guidance.
2. **Spaced Revision (`SPACED_REVISION`)**: Dynamically schedules mastered signs across an expanding retention ladder ($1\text{h} \rightarrow 4\text{h} \rightarrow 24\text{h} \rightarrow 72\text{h} \rightarrow 168\text{h}$) to combat forgetting curves.
3. **Uncertainty Recovery (`UNCERTAIN_RECOVERY`)**: If a recent prediction was ambiguous, guides the learner to adjust posture and lighting rather than punishing their score.
4. **Consistent Success Advance (`CONSISTENT_SUCCESS_ADVANCE`)**: When a learner achieves $\ge 3$ consecutive successes and mastery $\ge 70\%$, advances them to the next unlearned curriculum sign.
5. **Educational Autonomy**: Every suggestion is fully dismissible, allowing learners to freely override the system.

---

### [PANEL 5] Key HCI & Accessibility Principles Implemented
- **Visibility of System Status**: Real-time camera indicator, FPS/latency HUD, and a progressive steadiness meter showing pose consensus.
- **Error Prevention & Recovery**: Visual ROI bounding box assists hand positioning; constructive feedback explains *what* to adjust rather than displaying negative alerts.
- **Transparent Uncertainty**: Replaces misleading percentage scores with honest "Uncertain" states when classification margins are narrow.
- **Learner Agency**: Learner confirmation/override ensures classifier glitches never damage educational records.
- **Inclusive Accessibility**: WCAG 2.1 AA contrast, keyboard navigation, high-contrast toggle, zero reliance on audio, and local camera processing.

---

### [PANEL 6] Evaluation & Measured Engineering Benchmarks
- **Quantitative Engine Benchmarks** (Measured on Test Harness):
  - Model Inference Latency: $\mathbf{2.6\text{--}5.8\text{ ms}}$ (Target: $<20\text{ ms}$).
  - Real-Time Camera Preview: $\mathbf{28\text{--}30\text{ FPS}}$ (Target: $24\text{--}30\text{ FPS}$).
  - Prediction Frequency: $\mathbf{11.2\text{ Hz}}$ (Target: $10\text{--}20\text{ Hz}$).
  - Recommendation Generation Latency: $\mathbf{1.2\text{ ms}}$ (Target: $<500\text{ ms}$).
- **Automated Validation**: 20/20 automated pytest tests passing across recognition robustness, stability consensus, adaptive rules, and REST API flows.
- **Usability Study Protocol**: 9 realistic user tasks prepared with pre/post SUS questionnaires and within-subjects A/B comparison plan.

---

### [PANEL 7] Limitations & Future Work
- **Documented Limitations**:
  - The starting vocabulary is restricted to 35 verified baseline classes (1–9, A–Z). It does not encompass continuous signing, facial grammar, or full ISL sentence discourse.
  - Skin-masking remains sensitive to extreme lighting shifts; future work should incorporate full 3D hand mesh transformers as client-side WebGPU models mature.
- **Future Directions**: Integration with dynamic continuous video gestures and expanded vocabulary co-designed with Deaf Indian Sign Language native signers.
