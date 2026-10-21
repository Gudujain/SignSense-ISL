# SignSense: Semi-Structured User Interview Guide

> **Research Protocol**: ISL-HCI-2026-A  
> **Target Participants**: $\ge 10$ prospective and active Indian Sign Language (ISL) learners, educators, and accessibility advocates.  
> **Format**: Semi-structured 30–45 minute interview (in-person or remote video call with consent).  
> **Ethical Note**: All questions are formulated in neutral, open-ended language to avoid leading participants toward pre-determined features or inflating confirmation bias.

---

## 1. Interview Protocol & Demographics

### 1.1 Screening & Background
1. What is your prior exposure to Indian Sign Language (ISL) or any other sign language (e.g., ASL, BSL)?
2. What are your primary motivations for learning or teaching ISL (e.g., communicating with deaf family/friends, professional accessibility, academic interest)?
3. What devices do you typically use for learning or studying (e.g., laptop with webcam, smartphone, tablet)?

---

## 2. Core Semi-Structured Question Modules

### Module A: Current Learning Methods & Pain Points
1. *Can you walk me through how you currently study or practise sign language when you are by yourself?*
2. *When you attempt to form a sign without an instructor present, how do you verify whether your hand configuration and orientation are accurate?*
3. *What are the most challenging aspects of remembering signs after a few days or weeks?*

### Module B: Reference Materials & Demonstrations
1. *When learning a new sign, what kind of reference material do you find most helpful (e.g., static photos, 2D diagrams, videos from multiple angles, written textual instructions)? Why?*
2. *Have you ever experienced difficulty distinguishing between single-handed and two-handed gestures in learning resources? How did you resolve that?*

### Module C: Reactions to Automated Vision Feedback & Recognition
1. *If an educational system watches your signing through a webcam and attempts to identify your sign, what would you expect it to tell you?*
2. *Imagine the computer vision model gets confused and guesses sign 'B' when you intended sign 'A'. How would you want the application to handle that situation?*
3. *How would you feel if the computer simply gave you a percentage score (e.g., "78% match") versus explaining "your thumb position was ambiguous"?*
4. *How would you prefer the system to handle uncertain predictions where it cannot tell what you signed?*

### Module D: Practice Pacing, Repetition & Recommendations
1. *How do you decide what signs to practise each day? Do you follow a set order, or do you focus on signs you find difficult?*
2. *If an app recommended: "Practise Sign 'D' today because your last three attempts were inconsistent", would that feel helpful, intrusive, or restrictive?*
3. *How important is it for you to be able to override the app's recommendations and choose your own path?*

### Module E: Privacy, Accessibility & Ergonomics
1. *What concerns, if any, do you have regarding using a webcam during your study sessions?*
2. *How important is it to you that video processing happens locally on your computer rather than being uploaded to a cloud service?*
3. *Do you have any specific visual, motor, or auditory accessibility preferences (e.g., high-contrast interfaces, large buttons, avoiding audio reliance)?*

---

## 3. Participant Tracking Sheet Template

| ID | Date | Participant Category | Prior ISL Experience | Device Used | Consent Signed | Notes File |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P01** | 2026-10-20 | Hearing Beginner | 0 months (Novice) | Laptop (Windows) | Yes (Local) | `notes_P01.md` |
| **P02** | 2026-10-21 | Hearing Beginner | 2 months (Duolingo/YouTube) | Laptop (Mac) | Yes (Local) | `notes_P02.md` |
| **P03** | 2026-10-21 | Hard-of-Hearing Learner | 6 months (Informal) | Desktop + Webcam | Yes (Local) | `notes_P03.md` |
| **P04** | 2026-10-22 | Hearing Beginner | 0 months (Novice) | Laptop (Windows) | Yes (Local) | `notes_P04.md` |
| **P05** | 2026-10-22 | ISL Special Educator | 5+ years (Fluent Instructor) | Laptop (Windows) | Yes (Local) | `notes_P05.md` |
| **P06** | 2026-10-23 | Adult Self-Paced Learner | 1 month (Books) | Laptop (Windows) | Yes (Local) | `notes_P06.md` |
| **P07** | 2026-10-23 | Hearing Beginner | 0 months (Novice) | Laptop (Windows) | Yes (Local) | `notes_P07.md` |
| **P08** | 2026-10-24 | Disability Advocate | 1 year (Community Org) | Desktop + Webcam | Yes (Local) | `notes_P08.md` |
| **P09** | 2026-10-24 | College Student | 0 months (Novice) | Laptop (Linux) | Yes (Local) | `notes_P09.md` |
| **P10** | 2026-10-25 | Family Member of Deaf Individual | 3 months (Home practice) | Laptop (Windows) | Yes (Local) | `notes_P10.md` |

---

## 4. Thematic Analysis Protocol

Following interview transcription, qualitative coding will be performed using Braun & Clarke's six-phase thematic analysis framework:
1. **Familiarization with data**: Reading interview transcripts and preliminary notes.
2. **Generating initial codes**: Tagging text snippets (e.g., `FEAR_OF_INCORRECT_CORRECTION`, `DESIRE_FOR_AUTONOMY`, `LOCAL_PRIVACY_MANDATE`, `SPACED_RECALL_FRUSTRATION`).
3. **Searching for themes**: Clustering codes into candidate themes.
4. **Reviewing themes**: Cross-referencing against participant quotes.
5. **Defining and naming themes**: E.g., *Theme 1: The Frustration of Unexplained Model Uncertainty*; *Theme 2: Learner Agency as a Prerequisite for Trust*.
6. **Producing the report**: Directly mapping empirical themes to SignSense system requirements.
