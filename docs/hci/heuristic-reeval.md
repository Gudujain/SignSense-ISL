# Heuristic re-evaluation after Phases 1–7

Severity uses Nielsen's 0–4 scale. This is a source-based re-review, not a participant study. Findings that need a live browser are marked pending rather than assumed fixed.

| Baseline finding | Baseline severity | Current assessment | Current severity | Evidence / open check |
|---|---:|---|---:|---|
| H1 Pointer-only attempt completion | 4 | The `Practise` and `Check` flow can count down and finish after a steady pose without clicking. | 1 | `processPracticeFrame()`; verify camera flow and actual two-hand signing in browser. |
| H2 Conflicting active/no-hand/frame-count state | 3 | Learner-facing state text names setup or hand positioning; frame counter is no longer in the current template. | 1 | `updateRecognitionUI()`; run no-hand and loss-of-tracking cases. |
| H3 Tiny reference | 3 | Practice uses the existing larger responsive thumbnail style. | 1 | `target-thumb-mini`; actual dimensions are viewport-dependent and need screenshot review. |
| H4 Face-centered guide | 3 | Guide geometry is proportional and hand-based; two-hand position checks exist. | 2 | `drawRoiGuide()` and `processPracticeFrame()`; camera-dependent visual validation remains. |
| H5 Squeezed camera placeholder | 2 | Placeholder uses a vertical, centered flex layout. | 1 | `.camera-placeholder`; verify at 360px and 390px widths. |
| H6 Native controls and low-contrast helper text | 3 | Shared control styling and token-level contrast values exist. | 2 | `tokens.css`, `components.css`; no full rendered contrast audit has run. |
| H7 Cut-off Submit and Cancel | 4 | Hands-free flow avoids the submit control; controls are responsive in CSS. | 1 | `components.css`; visual clipping check pending. |
| H8 Disclaimer instead of pose cues | 3 | Curriculum instructions appear beside the reference; About explains the beta boundary. | 2 | Curriculum content remains unverified and cannot be treated as authoritative. |
| H9 ML jargon | 3 | Learner copy removes several diagnostic terms; technical labels remain in the hidden developer panel. | 1 | Static text review; dynamic copy and screen-reader announcements not fully audited. |
| H10 Demotivating stats and suggestion | 3 | Home uses practice activity and next-step suggestions; system failures are separated from learner misses. | 2 | Runtime outcomes and demo-mode consistency need browser verification. |
| H11 Curriculum overlap and no progression | 2 | Grid cards, stage progress, lock and preview states are implemented. | 1 | `renderCurriculum()`; seeded visual states need screenshot verification. |
| H12 Plain history table | 2 | Replaced by weekly activity, trends, and session cards with filters. | 1 | `screenHistory`, `loadHistory()`; interaction check pending. |
| H13 Learning controls grouped as Accessibility | 2 | Learning and accessibility settings are separate sections. | 1 | `screenSettings`; persisted behavior needs app/API smoke test. |
| H14 Header clutter | 2 | User navigation is simplified; accessibility controls are grouped. | 1 | `index.html`; verify keyboard disclosure and focus return. |
| H15 Repeated educator disclaimer | 2 | About/Beta and first-run notice carry the main disclosure. | 1 | Search all generated UI messages before release. |
| H16 Recommendations duplicate Home | 2 | Recommendations redirect to Home. | 1 | Route in `switchScreen()` and Flask route. |
| H17 No onboarding/help/recovery | 3 | Onboarding, tips, and recovery messages exist. | 1 | Full keyboard and assistive technology path remains untested. |
| H18 Sign 9 may be wrong | 4 | Still explicitly flagged. | 4 | Requires Deaf ISL educator review; see `docs/content-verification.md`. |

## Remaining high-priority work

1. Run axe-core on each visible screen state and fix serious/critical findings.
2. Run Lighthouse at representative desktop and mobile sizes.
3. Complete keyboard-only and screen-reader walkthroughs, including camera recovery.
4. Capture matched before/after screenshots.
5. Have Deaf ISL educators review all 35 entries.

Severity reductions above are provisional implementation judgments. They do not prove that users can complete tasks or that visual layouts are defect-free.

See the original [`00-baseline.md`](00-baseline.md), [`design-rationale.md`](design-rationale.md), [`accessibility.md`](accessibility.md), and [`before-after.md`](before-after.md).
