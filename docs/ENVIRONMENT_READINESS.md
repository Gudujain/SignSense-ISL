# SignSense Environment and Camera Readiness

Last checked: 2026-10-18. See [dataset inventory](DATASET_INVENTORY.md) and [model card](MODEL_CARD.md) for the model and data status.

## Environment used for this check

- Windows 11 x64, CPython 3.12.14.
- Repository-local `.venv`; no dependency installation into the Codex shared
  Python runtime.
- `numpy==1.26.4`, `opencv-contrib-python==4.11.0.86`,
  `mediapipe==0.10.32`, `scikit-learn==1.5.2`, `scipy==1.15.3`,
  `pytest==8.3.5`, Flask 3.1.3.
- Only `opencv-contrib-python` is installed. The `opencv-python` duplicate was
  removed because the OpenCV wheel variants share the `cv2` package namespace.
- `python -m pip check`: **No broken requirements found**.
- The MediaPipe Tasks API imported and `models/hand_landmarker.task` initialized
  successfully. Initialization failures are surfaced by
  `tools/environment_report.py` with the task path and error.

The exact PyPI wheels are available for Windows x64 and the selected Python
version. `requirements.txt` pins the core numeric/vision stack, and
`requirements-win-py312.lock.txt` captures the complete resolved dependency
set for this interpreter/platform. Recreate this environment with
`python -m pip install -r requirements-win-py312.lock.txt`.

## Camera probe

`tools/camera_smoke_test.py` tried camera indices 0, 1, and 2, requesting two
frames per index with a one-second warm-up. OpenCV reported that all three
devices could not be opened; none returned frames and no frames were saved.
The camera collector therefore could not be exercised through a real capture
session. The script releases every successfully opened handle in `finally`
and reports likely Windows privacy/device causes for failures.

No pilot images were collected. There is no participant consent record or
camera device in this environment, and no `data_collection/manifest.jsonl`
exists. Dataset coverage is **zero recorded samples**. Do not use the bundled
reference images or the historical CSV ledger as a substitute for the consented
pilot or independent test set.

## Tests

Run the current suite from the repository root (see the task completion note
for the measured result):

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --tb=short --basetemp=.pytest-tmp
```

The explicit `--basetemp` keeps pytest temporary data inside the project
workspace. Tests cover API and assessment invariants, target independence,
invalid/no-hand handling, participant grouping, manifest validation,
persistence, report metrics, and recommender behavior. They do not substitute
for participant-held-out model evaluation or real-camera testing.

To collect the pilot after separate still-image consent and with a working
camera:

```powershell
.\.venv\Scripts\python.exe tools/camera_smoke_test.py
.\.venv\Scripts\python.exe tools/environment_report.py
.\.venv\Scripts\python.exe tools/collect_webcam.py --consent --participant P001 --session S001
```

For each additional participant use a new pseudonym; for each separate session
use a new session token. The collector requires typed confirmation of the
consent described in `research/DATASET_IMAGE_CONSENT_ADDENDUM.md`. Face-only
examples additionally require the separately documented identifiable-still
consent.

Model baseline and candidate training/evaluation remain pending dataset
collection. See `ML_EVALUATION_STATUS.md` for the split protocol and commands.
