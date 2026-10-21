# SignSense personas and task scenarios

These are **provisional design personas**, not research participants or validated findings. They are grounded in the two audiences specified for the project. Validate assumptions with Deaf ISL learners, Deaf educators and families before treating them as representative.

## Persona 1 — A Deaf teenager learning ISL

**Name:** Riya (pseudonym) · **Age:** 16 · **Communication:** Deaf; uses ISL and text; prefers visual information.

- **Goals:** Learn and remember useful ISL signs; practise independently; understand what to adjust when a pose is unclear; see progress without being judged by a fallible recognizer.
- **Pain points:** Instructions that assume hearing; audio-only cues; tiny hand demonstrations; feedback that says only “wrong” or exposes ML jargon; a process that requires operating controls while both hands are signing.
- **Context:** Uses a laptop webcam in a bedroom or shared family room, at variable distances and lighting. May practise in short sessions and wants to choose the sign and repeat it at their own pace.
- **Design implications:** Text, icon and visible state change together; camera setup guidance remains visible; learner controls are reachable before/after signing; uncertainty is framed as a system limitation with a useful next step.

## Persona 2 — A hearing parent of a Deaf child

**Name:** Arjun (pseudonym) · **Age:** 38 · **Role:** Parent learning ISL to communicate with his 9-year-old child.

- **Goals:** Learn practical signs accurately, practise between lessons, support his child without making them responsible for teaching, and know which references need confirmation from an ISL educator.
- **Pain points:** Unclear or questionable reference images; not knowing whether a sign was performed correctly; recommendations that feel random; technical setup that interrupts family time; progress summaries that imply mastery without reliable evidence.
- **Context:** Uses a shared family laptop/tablet, sometimes with the child nearby. Sessions may be brief, interrupted and occur under household lighting. He is a novice and benefits from clear, short written directions.
- **Design implications:** Explain evidence and limits plainly; make review/practice choices useful without asserting certainty; keep the learner in control; distinguish “practised” from “verified learned.”

## Journey map — one practice session

| Stage | Learner action | Questions / friction today | Desired support | Observable success signal |
|---|---|---|---|---|
| Choose | Pick a sign from Home, Curriculum or Recommendations. | “What should I learn next, and why?” Repeated recommendation surfaces can compete. | One clear suggested action plus an easy browse/choose path and brief rationale. | Learner identifies the target and can change it without losing progress. |
| Learn | Inspect reference and instructions. | Is the image large enough? Is the sign label correct? What should each hand do? | Large reviewed demo, concise written cues, orientation/hand-count details and provenance. | Learner can describe or imitate the cue before activating camera. |
| Set up | Position camera and hands. | Is the webcam ready? Are hands in frame? Is face detection being mistaken for a sign? | Clear camera state, one/two-hand framing guide and non-camera option. | Learner sees a visible ready state and understands how to reposition. |
| Practise | Hold or move through the sign. | When do I start/finish if both hands are occupied? Does “frames” mean success? | Explicit attempt lifecycle with low-effort/hands-free finish option; no grading during preparation. | Learner can complete or cancel without awkward hand-to-mouse switching. |
| Feedback | Read result and decide what to do. | Did the app judge my sign or lose tracking? What can I change? | Three-level visual/text feedback: supportive success only when justified, actionable retry, or transparent uncertainty/system issue. | Learner can state the result and choose retry, review or continue. |
| Continue | Review history or next suggestion. | Does history show practice or actual mastery? Why this next activity? | Separate activity from verified learning; explain recommendation and allow dismissal. | Learner chooses an appropriate next step and recognizes progress honestly. |

## Task scenarios and planned measures

The thresholds below are **proposed acceptance targets for a future usability study**, not measured results. Collect task completion, elapsed time, observed errors/help requests, and a post-session SUS score. SUS is a session-level measure; associate the same post-session score with all completed task scenarios for analysis rather than pretending it is a per-task score.

| Scenario | Task prompt | Success criteria / target | Measures |
|---|---|---|---|
| T1 — Learn and practise a numeral | “Find sign 3, study its reference, start a practice attempt, complete it, then choose whether to retry or continue.” | ≥85% complete without facilitator intervention; learner can identify the current target and feedback state; no accidental history entry on cancel. Target median ≤3 minutes. | Completion (yes/no), time on task, wrong navigation/actions, recovery/help requests, post-session SUS. |
| T2 — Practise a two-hand letter with hands occupied | “Open a two-hand reference, position both hands, practise, and finish the attempt without using a mouse while signing.” | ≥80% complete without switching to a mouse during sign production; no clipped controls or lost attempt; target median ≤4 minutes. | Completion, time on task, hand-to-mouse interruptions, missed/duplicate finish actions, help requests, post-session SUS. |
| T3 — Recover from no-hand/tracking loss and use a recommendation | “Begin an attempt, move hands out of frame, recover from the tracking message, cancel or retry, then explain why the suggested activity appears.” | ≥85% recover without facilitator help; understands that no-hand is a tracking state, not a wrong sign; can state recommendation reason. Target median ≤3 minutes. | Completion, time to recovery, incorrect interpretation count, retry/cancel errors, help requests, post-session SUS. |

### Study notes

- Recruit participants in each audience group and include Deaf ISL users/educators in content review; do not ask a child to act as the sole authority on sign correctness.
- Obtain consent/assent appropriate to age and institutional review requirements. Camera video should not be retained unless a separate, explicit study protocol requires it.
- Record device, viewport, camera, lighting description and assistive technology use so outcomes can be interpreted.
- Define task success before sessions. Report sample size and missing observations; do not infer effectiveness from these planned targets.
