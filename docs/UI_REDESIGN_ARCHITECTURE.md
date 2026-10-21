# SignSense interface redesign: architecture and retained modules

Reviewed 2026-10-20 before interface changes.

## Existing architecture

SignSense is a Flask-served, vanilla HTML/CSS/JavaScript single-page application. `src/server/app.py` serves `src/static/index.html` and the static assets, plus JSON APIs for curriculum, learner profile/progress, recommendations, recognition, attempt assessment, diagnostics, and history reset. There is no frontend framework or build step.

The browser app in `src/static/js/app.js` owns screen navigation, camera stream acquisition, canvas overlays, explicit attempt lifecycle, and rendering. Camera frames are posted to the same-origin `/api/recognize` endpoint. The server calls `src/recognition/engine.py`; MediaPipe landmarks and the legacy reference/heuristic candidate path live in `src/recognition/pose_analyzer.py` and `engine.py`. `src/engine/assessment.py` returns an uncertain/not-assessed result because this recognition evidence is not independently validated.

Curriculum records are loaded from `src/curriculum/curriculum_data.json` through `src/curriculum/curriculum.py`. Learner outcomes and recommendation dismissals are persisted in SQLite by `src/engine/storage.py`. `src/engine/learner_model.py` updates attempt counts and revision schedules; `src/engine/recommender.py` applies deterministic rules to stored history. The evaluation status and model-card docs document the recognition limits.

## Modules and contracts retained

- Keep Flask route names and response contracts in `src/server/app.py`.
- Keep the explicit attempt lifecycle and authoritative server assessment; remove any UI shortcut that fabricates observations or claims correctness.
- Keep `curriculum.py`, the existing curriculum IDs/labels, reference image paths, stage grouping, SQLite persistence, learner history, recommendation engine, and recommendation dismissal endpoint.
- Keep the MediaPipe camera path and recognition candidate output unchanged during a UI redesign. UI work must not raise confidence or alter recognition thresholds.
- Keep the existing local SQLite data file; no migrations that discard learner history and no demo-data seeding.
- Keep the consent-gated image collector and ML evaluation workflow; do not turn learner research preferences into a claim that research uploads occur when there is no such export path.

## Verified findings that constrain presentation

- The current repository bundles one reference image per label, but lacks individual expert verification records for those images or the written pose instructions. The curriculum's inherited provenance and `recognition_supported` fields overstate what has been verified. The UI must make the reference-only/unverified status clear and must not present finger-level descriptions as validated instruction.
- Current recognition is not validated. An attempt matching a target remains uncertain; no correct/incorrect outcome or mastery credit can be claimed.
- Camera frames are posted from the browser to the local Flask server for recognition. The application does not persist these request frames as learner history. Learner assessment records are persisted in the local SQLite database. User-facing privacy text must describe this concrete flow.
- Existing dashboard steadiness and success UI contained synthetic values/text, and manual override controls submitted fabricated observations. These are not legitimate learner evidence and must be removed.

## Change boundary

The redesign will stay within the existing SPA and APIs: semantic markup, shared theme/accessibility tokens, real-history summaries, curriculum search/status filters, learner-facing recommendation copy, attempt-state feedback, actual settings persistence, and camera device/overlay preferences. No new UI dependency or replacement backend is required.
