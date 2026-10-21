# SignSense HCI demo script

**Purpose:** demonstrate the intended visual teaching flow, not model accuracy. Clearly identify forced results and seeded history as demo data.

## Before the demo

1. Start the local Flask app and open it in a supported browser.
2. Use a clean learner profile only if onboarding needs to be shown. Otherwise keep existing learner data.
3. Check the camera and lighting before presenting. Do not record the participant or screen without consent.
4. Use **Ctrl+Shift+D** to open the developer demo controls. Turn demo mode on. This makes the forced result label visible.

## Walkthrough

1. **Onboarding:** show Welcome, profile choices, camera setup checks, and privacy summary. Explain that app recognition is experimental and curriculum content needs educator review.
2. **Learn a sign:** open Learn and select a two-handed sign entry, such as sign 6. Show its reference and steps. Do not claim its ISL content has been verified.
3. **Prepare practice:** open Practice, choose Practise mode, and start the camera. Position both hands inside the guide. Wait until the visible status says to hold the sign.
4. **Hands-free signing:** before beginning, set the developer controls to force **Almost** and enter a clearly labelled demo hint, such as “Check your finger position against the example.” Put both hands up and sign. Keep hands on screen through the steady-pose countdown and capture. The app should show feedback without a mouse click. Do not touch the mouse or keyboard while signing.
5. **Explain the feedback:** point out the text outcome, hint, and demo label. Say that the result was forced for this demonstration, not inferred by a validated recognizer.
6. **Recommendation:** return to Home. Load demo history if a populated Home recommendation is needed. Expand **Why this?** and show the reason. Identify the history as fictional demo data.
7. **Progress:** open Progress and show the activity strip, trends, and outcome filters.
8. **Settings and privacy:** show accessibility options, progress saving, export/delete controls, and About/Beta disclosure. Do not export real learner data during a public presentation.

## Recovery plan

- If camera access is unavailable, open developer controls and select a camera recovery example. Show the non-blaming recovery message and its retry/skip actions.
- Forced Almost results still require a tracked pose to start the hands-free countdown. If tracking cannot see a hand, demonstrate the tracking recovery instead. Do not imply the forced result came from the camera.
- If demo history is absent, seed it from developer controls. Reset only demo data after the presentation if needed; never reset the learner's real history without consent.

## Success checklist

- [ ] Onboarding, camera guide, and privacy are shown.
- [ ] Learner sees a two-hand target and its reference.
- [ ] No pointer or keyboard action occurs during signing.
- [ ] Forced result is labelled demo and explained honestly.
- [ ] Recommendation reason and Progress are shown.
- [ ] Settings and data controls are explained.

See [`docs/hci/accessibility.md`](hci/accessibility.md), [`docs/hci/limitations.md`](hci/limitations.md), and [`docs/content-verification.md`](content-verification.md).
