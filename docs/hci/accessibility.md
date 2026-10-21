# Accessibility audit checklist

**Status: incomplete.** This checklist separates source-level checks from browser, assistive-technology, and user checks. Do not present this as WCAG conformance. The required axe-core and Lighthouse runs are pending because neither package nor a usable browser executable is available in this workspace.

## Source checks completed

- [x] All application views use the shared responsive page shell.
- [x] Main navigation has five labelled destinations.
- [x] Added a keyboard skip link to the main content.
- [x] Focus-visible styles use a 3px outline.
- [x] Default buttons and controls are styled for at least 44px height; checkboxes are 24px.
- [x] Common live status and result regions have text and live-region semantics.
- [x] Camera capture requests video only (`audio: false`); no audio cue or speech synthesis was found.
- [x] The user interface uses text alongside icons and state colors.
- [x] Reduced-motion CSS covers OS preference and the in-app setting.
- [x] Sign reference content is marked unverified; sign 9 is flagged.
- [x] Copy no longer tells learners that hand landmarks or frames are being processed.
- [x] Added the audience phrase “Deaf, hard of hearing or non-speaking”.

## Required checks still pending

- [ ] Run axe-core on Home, Learn, Practice, Progress, Settings, onboarding, sign dialog, help drawer, recovery panel, and developer demo states.
- [ ] Run Lighthouse accessibility for all primary screen states at mobile and desktop sizes. The app is a single-page interface, so save the tested state and route for every report.
- [ ] Fix all serious and critical axe findings; attach reports and record remaining violations.
- [ ] Verify Lighthouse accessibility score of at least 95 for each state.
- [ ] Keyboard-only walkthrough: onboarding, curriculum search/details, camera attempt, retry, progress filters, settings, export/delete confirmation.
- [ ] Screen-reader walkthrough of status changes, dynamically rendered history, dialogs, setup checks, and recommendation reasons.
- [ ] Contrast sampling for all text and state combinations in dark, light, and high-contrast themes. The source-token spot check is not a complete contrast audit.
- [ ] Confirm layout at 360px, 390px, 768px, and 1440px, including dialogs, developer tools, and result actions.
- [ ] Confirm target size and focus order in a real browser; check controls smaller than 44px against WCAG 2.2 AA exceptions and spacing rules.
- [ ] Review wording, instructions, and camera framing with Deaf and non-speaking participants.

## Environment evidence

- JavaScript syntax check: `node --check src/static/js/app.js` — passed during this change.
- A contrast calculation checked core text pairs and the added color-blind outcome colors against their card backgrounds. Tested pairs were above 4.5:1: core dark/light/high-contrast text was 9.94:1, 8.71:1, and 20.38:1; color-blind status colors were at least 6.92:1 in dark, 6.89:1 in light, and 10.04:1 in high contrast. These calculations do not cover every computed style, state, opacity, border, focus, or photo background.
- `axe-core`, `lighthouse`, `playwright`, and `puppeteer` are not installed in the project/global Node environment. No browser executable was found on PATH. No package was installed for this audit.
- Therefore, “axe has no serious or critical issues” and “Lighthouse ≥95” are **not established**.

## Audit record

| Tool / method | Version | Screens/states | Result | Date |
|---|---|---|---|---|
| Static source review | N/A | HTML, JS, CSS | Partial; see checks above | 2026-10-20 |
| axe-core | Not installed | Pending | Not run | Pending |
| Lighthouse | Not installed | Pending | Not run | Pending |
| Keyboard only | Browser unavailable | Pending | Not run | Pending |
| Screen reader | Not available | Pending | Not run | Pending |

See [`heuristic-reeval.md`](heuristic-reeval.md), [`before-after.md`](before-after.md), and [`usability-test-plan.md`](usability-test-plan.md).

### Commands for a workstation with browser tooling

Start the app in one PowerShell window:

```powershell
.\.venv\Scripts\python.exe -m src.server.app
```

In a second window, run the tools in the evaluation environment:

```powershell
npx --yes @axe-core/cli http://127.0.0.1:5000
npx --yes lighthouse http://127.0.0.1:5000 --only-categories=accessibility --output=json --output-path=docs/hci/lighthouse-home.json
```

These commands audit the initial Home state only. Navigate to each screen, repeat axe, and save a separate Lighthouse report for each state. The app uses client-side screens, so a single URL report does not cover hidden views or dialogs. Record the browser and tool versions in the audit table.
