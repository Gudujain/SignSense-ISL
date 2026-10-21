# SignSense design rationale

This table describes implemented design intent. It is not evidence of usability or accessibility outcomes. Recognition and curriculum content remain experimental.

| Change | Problem addressed | Principle | Evidence / limitation |
|---|---|---|---|
| Live camera state text, guide, and hold/countdown ring | Learners need to know whether the camera sees hands and when an attempt is being captured. | Nielsen: visibility of system status; WCAG status messages | `src/static/index.html`, `src/static/js/app.js`; dynamic browser validation remains pending. |
| Automatic hold, countdown, and capture after the learner steadies hands | Pointer actions are awkward while signing with two hands. | Match with real world; Fitts's law; flexible interaction | `processPracticeFrame()` and `finishHandsFreeAttempt()` in `src/static/js/app.js`. It has not been observed in a live user session. |
| Pause, skip, retry, cancel, and dismiss controls | Learners need safe ways to stop or change course. | User control and freedom | Camera pause, onboarding skip, retry, attempt cancel, and recommendation dismissal controls. |
| Camera setup check, hand guide, and recovery panel | Poor framing or tracking should be diagnosed as a system condition. | Error prevention and recovery | Setup checks and `showRecovery()` in `src/static/js/app.js`; heuristic thresholds are not independently validated. |
| Persistent sign reference beside the practice view | Learners should not have to remember an image while signing. | Recognition rather than recall | `#targetSignThumb`, `#targetSignInstructions` in `src/static/index.html`. Reference accuracy remains unverified. |
| At least 44px default controls; larger-target option | Small targets are difficult to reach and activate. | Fitts's law; WCAG 2.2 target size | `src/static/css/components.css`; actual geometry at every viewport still needs browser review. |
| Five main navigation items and one top recommendation | Too many competing choices increase selection effort. | Hick's law; aesthetic and minimalist design | Header navigation and Home suggestion in `src/static/index.html`. |
| Learner-centered progress; hidden diagnostics | Technical measurements do not explain learning progress. | Aesthetic and minimalist design; match with real world | `screenDashboard`, `screenHistory`, developer-only diagnostics in `src/static/index.html`. |
| Three visible outcome labels and actionable hints | Feedback needs to be understandable and guide the next action. | Feedback and reward; visibility of system status | `showHandsFreeResult()` in `src/static/js/app.js`. Labels describe prototype outcomes, not validated correctness. |
| “Why this?” for suggestions | Recommendations should be explainable and dismissible. | Explainability; user control | `loadRecommendations()` and `recommendationWhy()` in `src/static/js/app.js`. Rules are not proven pedagogically effective. |
| Text, icon, state, and color together; keyboard focus and reduced motion | Visual state should not depend on color or motion alone. | WCAG 2.2 AA; universal design | `src/static/css/tokens.css`, `src/static/css/components.css`; axe and assistive-technology checks remain pending. |
| Deaf-led content review and no sound cues | Learning should not depend on hearing, and sign examples need community review. | Deaf-centered and universal design | `docs/content-verification.md`; no educator review has been completed. Camera capture requests video only (`audio: false`). |
| Local camera processing and explicit progress saving | Learners should understand what is stored and control local progress. | Privacy by design; user control | Camera video is processed in the browser; hand-position data is sent to the local app. It is not uploaded to a remote service by this application. |

## Known evidence limits

- The project's prediction and assessment logic is not independently validated on participants.
- The 35 reference labels and images have not been verified by an ISL educator.
- No axe-core report, Lighthouse report, screen-reader run, or measured WCAG conformance is available for this revision.
- See [`accessibility.md`](accessibility.md), [`heuristic-reeval.md`](heuristic-reeval.md), and [`limitations.md`](limitations.md).
