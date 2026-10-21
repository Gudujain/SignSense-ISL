# SignSense usability test plan

## Purpose

Learn whether people can set up the app, practise with both hands, understand its feedback, and find a useful next step. This is an HCI usability study, not an ML accuracy study.

## Participants and consent

- Recruit five adults: prioritize Deaf ISL users and Deaf educators; include hard-of-hearing, non-speaking, and hearing family learners where feasible.
- Do not treat five participants as representative of all Deaf people or ISL users.
- Ask about communication and access preferences before the session. Provide written instructions and interpreters or other access support requested by participants.
- Obtain informed consent before recording notes or screen activity. Explain purpose, duration, voluntary participation, stopping at any time, storage, deletion date, and contact person.
- Do not retain webcam video by default. If research video is genuinely needed, obtain separate explicit consent and an approved data-handling plan.
- For minors, obtain guardian consent and participant assent under the institution's ethics process. Do not ask a child to validate sign correctness.

### Short consent form

> I understand that this session evaluates the SignSense interface, not my signing ability. Taking part is optional. I may pause or stop at any time. Camera video will not be saved unless I give separate permission. My notes will use a participant code. I can ask how to withdraw my data.

Participant code: ______  Date: ______  Consent: Yes / No  Separate video consent: Yes / No

## Procedure

1. Explain think-aloud: say what you expect, notice, and find confusing. There are no right answers.
2. Ask permission before helping. Record the help request and point of failure.
3. Give each task once, without coaching. Counterbalance tasks if time permits.
4. Record completion, time, errors, help requests, and access barriers.
5. After tasks, administer the standard 10-item System Usability Scale (SUS). Use the standard wording and scoring procedure; do not edit item text.
6. Debrief and offer data withdrawal contact details.

## Tasks and measures

| Task | Prompt | Completion criterion | Measures |
|---|---|---|---|
| 1. First setup and sign | “Set up SignSense, find sign 3, and begin practising it.” | Reaches a sign practice state and explains the visible next action. | Completion, time, errors, setup recovery, help requests. |
| 2. Two-handed hands-free practice | “Practise the two-handed sign shown. Keep using your hands until feedback appears.” | Feedback appears without mouse or keyboard use during signing. | Completion, time, hand-to-device interruptions, tracking loss, errors. |
| 3. Find what to do next | “From Home, choose a next step. Tell me why it was suggested, then find your progress.” | Starts or dismisses a suggestion, explains “Why this?”, opens Progress. | Completion, time, navigation errors, explanation comprehension. |

## Results template

| Participant code | Access needs (optional) | Task | Completed? | Time (seconds) | Errors | Help requests | Notes / quotes with consent |
|---|---|---|---:|---:|---:|---:|---|
| | | | | | | | |

Record SUS item responses separately. Compute SUS only after all ten responses. Report participant count, missing tasks, device/viewport, camera conditions, facilitator assistance, and any deviations. Do not publish identifiable notes without consent.

## Summary template

- Participants completed: __ / 5
- Task completion rates: T1 __%; T2 __%; T3 __%
- Median times: T1 __s; T2 __s; T3 __s
- Common errors/help requests: __
- SUS scores (individual and median): __
- Access barriers and design changes: __
- Limitations and next study: __

No participants have been recruited or tested for this plan yet.

## SUS questionnaire

Use a five-point scale: **1 Strongly disagree, 2 Disagree, 3 Neither, 4 Agree, 5 Strongly agree.**

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

See [`design-rationale.md`](design-rationale.md), [`heuristic-reeval.md`](heuristic-reeval.md), and [`limitations.md`](limitations.md).
