# SignSense: Low-Fidelity Wireframes & Interaction Schematics

> **Design Objective**: Clear, low-clutter spatial hierarchy mapping Nielsen usability heuristics and WCAG 2.1 AA accessibility guidelines to the 8 core application screens.

---

## Screen A: Onboarding View (`#screenOnboarding`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense [ISL Adaptive]                [HUD: Off]  [Contrast]            |
+-------------------------------------------------------------------------------+
|                                                                               |
|                            Welcome to SignSense                               |
|        Adaptive Indian Sign Language Learning with Real-Time Feedback         |
|                                                                               |
|  +------------------------------+     +-----------------------------------+  |
|  | 1. Learning Goal & Level     |     | 2. Privacy & Camera Permissions   |  |
|  |                              |     |                                   |  |
|  | Target Goal:                 |     | 🔒 Local-First Privacy Notice:    |  |
|  | [ Stage 1: Numerals (1-5) v] |     | All frames analyzed on device.    |  |
|  |                              |     | Zero video uploaded to cloud.     |  |
|  | Skill Level:                 |     |                                   |  |
|  | [ Beginner (Novice)       v] |     | [ ] Optional research analytics   |  |
|  +------------------------------+     +-----------------------------------+  |
|                                                                               |
|              [ Enable Camera & Begin ]   [ Proceed Without Camera ]           |
|                                                                               |
+-------------------------------------------------------------------------------+
```

---

## Screen B: Learning Dashboard (`#screenDashboard`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense   [Dashboard*] [Curriculum] [Practice] [Recs] [History] [Settings]|
+-------------------------------------------------------------------------------+
|  +--------------+  +--------------+  +-----------------+  +-----------------+ |
|  |  MASTERED    |  |  IN PRACTICE |  | CONSISTENCY     |  | TOTAL ATTEMPTS  | |
|  |      8       |  |      4       |  |      87%        |  |       42        | |
|  +--------------+  +--------------+  +-----------------+  +-----------------+ |
|                                                                               |
|  +----------------------------------------------------+  +------------------+ |
|  | ✨ RECOMMENDED NEXT ACTIVITY: Advance to Sign '2'  |  | 📅 REVISION DUE  | |
|  | "Try new sign '2' because you achieved consistent  |  | [Sign 1 (Due)]   | |
|  |  mastery (85%) on Sign '1'."                       |  | [Sign 4 (Due)]   | |
|  |                                                    |  |                  | |
|  | [ Start Practising Now ]    [ Dismiss Suggestion ] |  | 🕒 RECENT SIGNS  | |
|  +----------------------------------------------------+  | [Sign 1] [Sign B]| |
|                                                          +------------------+ |
+-------------------------------------------------------------------------------+
```

---

## Screen C: Curriculum Catalogue & Reference Modal (`#screenCurriculum`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense   [Dashboard] [Curriculum*] [Practice] [Recs] [History] [Settings]|
+-------------------------------------------------------------------------------+
|  ISL Curriculum Catalogue                         [ Filter: All | 123 | ABC ] |
|                                                                               |
|  STAGE 1: Basic Numerals (1–5) [5 Signs]                                      |
|  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+    |
|  | [Thumb 1] |  | [Thumb 2] |  | [Thumb 3] |  | [Thumb 4] |  | [Thumb 5] |    |
|  |  Sign 1   |  |  Sign 2   |  |  Sign 3   |  |  Sign 4   |  |  Sign 5   |    |
|  | 1-handed  |  | 1-handed  |  | 1-handed  |  | 1-handed  |  | 1-handed  |    |
|  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+    |
|                                                                               |
|  STAGE 3: Foundational ISL Vowels (A, E, I, O, U) [5 Signs]                   |
|  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+    |
|  | [Thumb A] |  | [Thumb E] |  | [Thumb I] |  | [Thumb O] |  | [Thumb U] |    |
|  |  Sign A   |  |  Sign E   |  |  Sign I   |  |  Sign O   |  |  Sign U   |    |
|  | 2-handed  |  | 2-handed  |  | 2-handed  |  | 2-handed  |  | 2-handed  |    |
|  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+    |
+-------------------------------------------------------------------------------+

[ MODAL DIALOG ON SIGN CLICK ]
+-----------------------------------------------------------------------+
|  Sign Reference: Sign 'A'                                         [X] |
|  +-----------------------+  Stage 3: Intermediate level • Alphabet    |
|  |                       |                                            |
|  |  [Large High-Res      |  Pose Instructions:                        |
|  |   Reference Image]    |  "Hold non-dominant hand open with palm    |
|  |                       |   facing outward. With dominant index,     |
|  |                       |   touch the tip of the non-dominant thumb" |
|  +-----------------------+                                            |
|                             Provenance: Karthikeyan et al. ISL Dataset|
|                             [ Practise This Sign with Camera ]        |
+-----------------------------------------------------------------------+
```

---

## Screen D & E: Real-Time Practice & Feedback (`#screenPractice`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense   [Dashboard] [Curriculum] [Practice*] [Recs] [History] [Settings]|
+-------------------------------------------------------------------------------+
|  +----------------------------------+  +------------------------------------+ |
|  | [● Camera Active (30 FPS)]       |  | TARGET SIGN: Sign 1     [MiniThumb]| |
|  |                                  |  | Stage 1 • Numerals                 | |
|  |       +------------------+       |  +------------------------------------+ |
|  |       |                  |       |  Pose Instructions:                     | |
|  |       |   [CYAN ROI      |       |  "Extend index finger vertically up;   | |
|  |       |    GUIDE BOX]    |       |   keep thumb and 3 fingers folded."    | |
|  |       |                  |       |  +------------------------------------+ |
|  |       +------------------+       |  | SYSTEM RECOGNITION      CONFIDENCE | |
|  |     "Place hands inside box"     |  |       Sign 1               86%     | |
|  |                                  |  |                                    | |
|  | [Pause Camera]  [Switch Device]  |  | Hold Pose: [===========>    ] 75%  | |
|  +----------------------------------+  |                                    | |
|                                        | "Sign '1' detected! Hold steady..."| |
|                                        |                                    | |
|                                        | Educational Confirmation:          | |
|                                        | [ Confirm Correct ] [ Mark Wrong ] | |
|                                        | [ Retry Attempt   ] [ Next Sign ->]| |
|                                        +------------------------------------+ |
+-------------------------------------------------------------------------------+
```

---

## Screen F: Personalized Recommendations (`#screenRecommendations`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense   [Dashboard] [Curriculum] [Practice] [Recs*] [History] [Settings]|
+-------------------------------------------------------------------------------+
|  Personalized Practice Recommendations                                        |
|  Every activity is generated by transparent pedagogical rules.                |
|                                                                               |
|  +--------------------------------------------------------------------------+ |
|  | [Thumb]  [REPEATED_DIFFICULTY]                                           | |
|  |          Review Sign 'B' with Guided Demonstration                       | |
|  |          "Practise this sign again because your last 2 attempts were     | |
|  |           inconsistent. Replay the reference demonstration and retry."   | |
|  |                                                 [ Practise ] [ Dismiss ] | |
|  +--------------------------------------------------------------------------+ |
|                                                                               |
|  +--------------------------------------------------------------------------+ |
|  | [Thumb]  [SPACED_REVISION]                                               | |
|  |          Spaced Memory Review: Sign '1'                                  | |
|  |          "Review sign '1' because it is due for scheduled spaced         | |
|  |           revision to maintain long-term retention."                     | |
|  |                                                 [ Practise ] [ Dismiss ] | |
|  +--------------------------------------------------------------------------+ |
+-------------------------------------------------------------------------------+
```

---

## Screen G: Progress & History View (`#screenHistory`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense   [Dashboard] [Curriculum] [Practice] [Recs] [History*] [Settings]|
+-------------------------------------------------------------------------------+
|  Practice History & Analytics Log                                             |
|                                                                               |
|  +--------------------------------------------------------------------------+ |
|  | TIME     | TARGET | PREDICTED | CONFIDENCE | CONFIRMATION | STATUS | LATENCY |
|  |----------+--------+-----------+------------+--------------+--------+---------|
|  | 21:14:02 | Sign 1 | Sign 1    |    88%     | Confirmed    | Correct| 4.2 ms  |
|  | 21:12:15 | Sign 1 | Sign 2    |    62%     | Overridden   | Correct| 3.8 ms  |
|  | 21:10:40 | Sign B | Sign D    |    48%     | Reported     | Incorr | 5.1 ms  |
|  +--------------------------------------------------------------------------+ |
+-------------------------------------------------------------------------------+
```

---

## Screen H: Settings & Privacy View (`#screenSettings`)
```
+-------------------------------------------------------------------------------+
|  🤟 SignSense   [Dashboard] [Curriculum] [Practice] [Recs] [History] [Settings*]|
+-------------------------------------------------------------------------------+
|  Settings & Privacy Controls                                                  |
|                                                                               |
|  +--------------------------------------------------------------------------+ |
|  | 🔒 Camera Privacy Architecture                                           | |
|  | All video processing executes 100% locally on your machine. Zero webcam  | |
|  | frames are ever uploaded, recorded, or transmitted to cloud services.   | |
|  |                                                                          | |
|  | [X] Contribute anonymized latency metrics to academic research study     | |
|  +--------------------------------------------------------------------------+ |
|                                                                               |
|  +--------------------------------------------------------------------------+ |
|  | ♿ Accessibility Preferences                                              | |
|  | [ ] High Contrast Color Mode (WCAG 2.1 AAA Compliant)                     | |
|  | [ ] Reduced Motion & Interface Animations                                | |
|  +--------------------------------------------------------------------------+ |
|                                                                               |
|  +--------------------------------------------------------------------------+ |
|  | ⚠️ Danger Zone: Reset Learning History                                    | |
|  | Permanently clear all stored practice attempts and per-sign mastery.      | |
|  | [ Reset All Progress ]                                                   | |
|  +--------------------------------------------------------------------------+ |
+-------------------------------------------------------------------------------+
```
