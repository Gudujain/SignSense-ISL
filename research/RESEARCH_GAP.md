# SignSense: Research Gap & Grounded Research Questions

> **Theoretical Grounding**: Derived systematically from the synthesis of [Karthikeyan et al., 2020], [Bragg et al., ASSETS 2019], [Adithya & Rajesh, 2020], [Starner et al., 1998], and [Cepeda et al., 2006].

---

## 1. Synthesis of the Existing Scientific Literature

A rigorous review of the prior art reveals three distinct, historically disconnected research trajectories:

1. **Isolated Computer Vision Classifiers**:
   Computer vision researchers (e.g., Karthikeyan et al., 2020; Adithya & Rajesh, 2020) have concentrated almost exclusively on maximizing per-frame classification benchmark accuracy on curated, static gesture datasets. These systems treat gesture recognition as an end in itself, terminating at an output string (e.g., predicting "Class 5"). They operate without an interactive user interface, offer no pedagogical guidance, provide no mechanism to handle uncalibrated uncertainty, and completely lack longitudinal learner models.

2. **HCI and Disability Studies Critiques**:
   Human-Computer Interaction scholars (e.g., Bragg et al., ASSETS 2019) have demonstrated that high benchmark accuracy in the laboratory does not translate to effective educational outcomes. Real learners encounter variable home lighting, physical fatigue, and classifier errors. When educational systems treat brittle classifier guesses as unappealable ground truth, learners experience frustration, loss of trust, and anxiety. Bragg et al. advocate for learner agency, transparent uncertainty, and human-in-the-loop recovery.

3. **Cognitive Spaced Practice Paradigms**:
   Cognitive psychologists (e.g., Cepeda et al., 2006) have established that long-term motor and conceptual retention requires distributed, spaced practice rather than massed repetition. However, spaced repetition algorithms (such as Leitner or SuperMemo) have historically been restricted to flashcards and text-based vocabulary recall, rarely integrated with real-time kinesthetic vision feedback.

---

## 2. The Identified Research Gap

Despite advancements in these separate domains, there is a pronounced gap in the scientific literature:

> **The Research Gap**:  
> No existing Indian Sign Language (ISL) system integrates **real-time computer vision recognition**, **transparent prediction uncertainty**, **learner-controlled error recovery**, and **explainable spaced practice recommendations** into a unified, accessible educational application.

Specifically:
- Prior ISL systems do not separate raw model inference from educational attempt assessment: an ambiguous frame or classifier error is erroneously logged as a learner mistake.
- Existing sign language prototypes do not maintain per-sign longitudinal mastery records or provide explainable recommendations that tell the learner *why* a specific practice activity was suggested.
- HCI usability evaluations comparing adaptive sign language practice sequences against fixed curricula remain virtually absent in the ISL domain.

---

## 3. Formal Research Questions

To directly address this research gap, the SignSense project investigates two interrelated research questions:

### Primary Research Question (System Design & Integration)
$$\mathbf{RQ_1}: \textit{"How can real-time sign recognition, learner-controlled feedback, and performance-based recommendations be integrated into an accessible learning interface for beginner ISL learners?"}$$

- **Sub-question 1a (Robustness & Feedback)**: How does separating raw classifier predictions from learner-confirmed assessments impact learner trust and error recovery during practice?
- **Sub-question 1b (Temporal Stabilization)**: How does a temporal consensus buffer mitigate visual flicker and prevent premature attempt evaluation during sign formation?

---

### Secondary Evaluation Question (HCI & Usability Comparison)
$$\mathbf{RQ_2}: \textit{"How does adaptive practice influence the usability, cognitive load, and perceived usefulness of an ISL learning prototype compared with a fixed practice sequence?"}$$

- **Sub-question 2a (Perceived Usability)**: Does an explainable, rules-based recommendation engine yield higher System Usability Scale (SUS) scores compared to a linear, fixed lesson order?
- **Sub-question 2b (Retention & Efficiency)**: How does an expanding spaced revision queue impact learner-reported confidence and retention across multi-day practice intervals?
