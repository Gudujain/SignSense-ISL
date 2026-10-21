# SignSense User Personas

> **Methodological Note**: These personas are constructed from preliminary user group requirements and domain analysis. Per project guidelines, they are explicitly designated as **[Provisional Hypotheses]** pending final aggregation of the 10 formal user interviews.

---

## Persona 1: Aanya — The Self-Paced Hearing Beginner
*Status: [Provisional Hypothesis]*

- **Demographics**: 21 years old, Undergraduate Computer Science Student, New Delhi.
- **Prior Experience**: Zero prior sign language experience.
- **Primary Goal**: Learn the 35 core ISL fingerspelling alphabets and numerals so she can communicate with a deaf peer in her university project team.
- **Context of Use**: Practices in her dormitory room in the evening under modest ambient lamp lighting using a budget laptop with an integrated 720p webcam.

### Pain Points & Frustrations:
1. **Uncertain Self-Correction**: When practicing alone using static textbook illustrations, she cannot tell if her thumb placement on two-handed vowels (e.g., A, E) is correct.
2. **Classifier Anxiety**: Previous apps she tried penalized her with an "Incorrect!" alert when she hesitated or moved her hand into frame, causing discouragement.
3. **Retention Drop-off**: Forgets signs learned on Monday by Thursday if she doesn't actively review them.

### Representative Scenario:
Aanya opens SignSense after dinner. The dashboard immediately suggests: *"Learn Sign '1' in Stage 1"*. She views the verified reference demonstration, noting the instruction: *"Extend index finger vertically upwards while keeping thumb folded"*. She clicks *Practise*, positions her hand inside the cyan guide box, and watches the steadiness progress bar fill up as she holds the pose. The system recognizes the sign, and she confirms the outcome. The next day, SignSense surfaces a spaced revision reminder for Sign '1' while advancing her to Sign '2'.

### Design Implications for SignSense:
- **Interactive ROI Box**: Visual cyan alignment guides reassure Aanya that both hands are correctly framed.
- **Temporal Stability Buffer**: Prevents counting preparatory hand movements as failed attempts.
- **Spaced Revision Queue**: Automatically schedules previous signs before memory decays.

---

## Persona 2: Rajesh — The Independent Adult Learner with Low-Light & Privacy Constraints
*Status: [Provisional Hypothesis]*

- **Demographics**: 34 years old, Banking Officer, Bengaluru.
- **Prior Experience**: Completed an informal 2-hour online workshop 6 months ago.
- **Primary Goal**: Build practical fluency in ISL numerals and high-frequency fingerspelling during 15-minute evening intervals.
- **Context of Use**: Home study area with variable warm incandescent lighting. Highly sensitive to data privacy and corporate webcam surveillance policies.

### Pain Points & Frustrations:
1. **Webcam Privacy Skepticism**: Refuses to use educational tools that upload video feeds to cloud servers or foreign AI APIs.
2. **Misleading Model Confidence**: Has experienced computer vision systems that report "99% confident" on blurry, wrong predictions.
3. **Lack of Educational Freedom**: Frustrated by rigid apps that lock future lessons until a score threshold is met.

### Representative Scenario:
Rajesh begins a practice session on sign 'C'. Because of warm evening lighting, the skin-masking produces lower contour separation. Rather than guessing an arbitrary class with false confidence, SignSense honestly reports: *"Prediction is uncertain. Check your hand position and lighting, then try again."* Rajesh repositions his lamp, holds the sign steadily, and the model recognizes 'C'. He overrides one ambiguous result using the *"Confirm Correct"* button, appreciating that his educational judgment is respected.

### Design Implications for SignSense:
- **Local-Only Privacy Guarantees**: Prominent assurance in onboarding and settings that zero video frames leave the device.
- **Transparent Uncertainty State**: Honest "Uncertain" status whenever confidence margin is low, eliminating deceptive percentage claims.
- **Learner Override Control**: Ability to manually confirm or correct model output so a classifier glitch never lowers learner mastery.

---

## Persona 3: Meera — The Inclusive Education Instructor
*Status: [Provisional Hypothesis]*

- **Demographics**: 42 years old, Special Needs Educator & Accessibility Coordinator, Pune.
- **Prior Experience**: 10+ years fluent ISL signer and certified trainer.
- **Primary Goal**: Recommend a trustworthy, self-paced practice tool for her hearing students that accurately mirrors authentic Indian Sign Language conventions.
- **Context of Use**: Recommends software to students practicing on home PCs with varied hardware capabilities.

### Pain Points & Frustrations:
1. **ASL Contamination in Online Tools**: Many apps falsely market American Sign Language (ASL) materials as Indian Sign Language (ISL), confusing students who need two-handed ISL fingerspelling.
2. **Black-Box AI Recommendations**: Black-box algorithmic schedulers that cannot explain *why* a student is being forced to repeat a sign.
3. **Accessibility Neglect**: Apps that depend on subtle color distinctions or sound effects that are unusable for deaf or low-vision students.

### Representative Scenario:
Meera reviews SignSense to verify its curriculum integrity. She checks the Stage 3 Vowels and confirms that signs A, E, I, O, U utilize authentic ISL two-handed fingertip touching rather than one-handed ASL shapes. She tests the recommendation engine by intentionally failing sign 'B' twice; SignSense immediately flags: *"Practise this sign again because your last 2 attempts were inconsistent"*, clearly citing the underlying pedagogical rule. She is satisfied that the system is explainable, authentic, and accessible.

### Design Implications for SignSense:
- **Verified ISL Provenance**: Explicit documentation of two-handed ISL rules and data provenance.
- **Explainable Pedagogical Rules**: Every recommendation displays its exact rule rationale (`REPEATED_DIFFICULTY`, `SPACED_REVISION`, `CONSISTENT_SUCCESS_ADVANCE`).
- **WCAG 2.1 AA Compliance**: High-contrast mode, legible typography (`Outfit`/`Inter`), and zero reliance on audio cues.
