# Before screenshots — manual capture checklist

The browser available for this documentation task can display a page screenshot but does not expose a way to save the image bytes into the repository. This folder is ready for the screenshots; none are included yet. Please capture them locally before any redesign if a persistent baseline is required.

## Capture steps

1. Start the app from the repository root: `\.venv\Scripts\python.exe -m src.server.app`.
2. Open `http://127.0.0.1:5000/` in Edge or Chrome. Use one consistent browser window size and zoom (recommended 1440×900 at 100%).
3. For each page, open DevTools (`F12`), press `Ctrl+Shift+P`, choose **Capture full size screenshot**, then save the PNG into this folder using the filenames below. If the command is unavailable, use `Win+Shift+S` and capture the full app viewport; note that the capture is viewport-only.
4. Capture Practice in the camera-off state. If documenting a camera state, do not grant camera access unless you intend to test it; do not submit, dismiss, or clear any learner data for screenshots.
5. For Curriculum, keep the top stage visible in the full-page capture. For Recommendations and History, capture the full scrollable page.
6. Onboarding may be included if you can reach it with a clean browser profile. Do not clear the project's `signsense.db` just to reset the screen.

## Expected filenames

- `home.png`
- `curriculum.png`
- `practice.png`
- `recommendations.png`
- `history.png`
- `settings.png`
- Optional: `onboarding.png`

After capturing, confirm these PNGs are present here. Keep this folder's screenshot files unmodified as the “before” record; future phases can place annotated copies elsewhere.
