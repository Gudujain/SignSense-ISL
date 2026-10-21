# Experimental letter-recognition result from `Dataset.zip`

## Scope

This is a local experiment on the user-provided archive at
`C:\Users\admin\Downloads\Dataset.zip`. It covers the 26 letter-folder
labels A–Z only. It does not cover digits 1–9, incorrect target signs,
incomplete poses, transitions, no-hand frames, face-only frames, or unknown
signs. It does not establish ISL label correctness, participant-independent
generalization, webcam reliability, or learner-assessment accuracy. The
archive contained no provenance, consent, or license document; confirm its
terms before redistributing the model or data.

The existing user-supplied archive is not copied into this repository. The
trained candidate is written to the ignored local `ml_models/` directory.

## Data audit

The ZIP contained 18,198 Training, 2,579 Validation, and 5,200 Testing images
across 26 letter folders. Exact SHA-256 comparison found 25,086 unique image
contents among those 25,977 images. There were 787 exact duplicate groups;
648 crossed the archive's named split boundaries, including 599 groups shared
by Training and Testing. One exact-content group had conflicting folder labels
and was excluded.

The experiment retained one copy of each image, preferring Training, then
Validation, then Testing. This leaves 18,054 / 2,470 / 4,561 images in the
three named splits. It removes exact duplicates across the evaluated splits,
but the archive has no participant/session metadata, so these are **not
participant-disjoint splits**. Near-duplicates may also remain.

## Model and comparison

MediaPipe HandLandmarker extracted up to two hands from each image. The two
candidates were `StandardScaler + RBF SVC (C=1)` using (1) the existing
128-value pair of independently normalized hand vectors plus hand count, and
(2) that feature plus left-to-right wrist displacement and relative hand
scale. Both candidates were fitted on Training; validation macro-F1 selected
the existing local-hand feature candidate (0.8593 versus 0.8586 for the added
layout feature). The independent-from-fitting Testing folder was used once
after exact duplicate removal.

| Test result | Active reference heuristic | Selected landmark SVC |
|---|---:|---:|
| Top-class accuracy across all 4,561 test images, counting no-landmark cases as abstentions | 5.77% | 82.96% |
| Macro-F1 across all test images, counting no-landmark cases as abstentions | 0.0610 | 0.8698 |
| Accuracy among 4,135 images with detected landmarks | — | 91.51% |
| Macro-F1 among images with detected landmarks | — | 0.9121 |
| Landmark candidate coverage | 90.66% | 90.66% |

The selected model's lower-scoring test classes included Z (F1 0.620), S
(0.658), Q (0.662), B (0.752), W (0.758), and N (0.762). The complete per-class
precision/recall/F1, supports, and confusion matrices for both the active
heuristic and SVC are in
[`scratch/letter_archive_evaluation.json`](../scratch/letter_archive_evaluation.json).

On this machine, shared image decode plus MediaPipe extraction measured
62.36 ms mean / 81.38 ms p95. SVC classification alone measured 2.06 ms mean /
2.39 ms p95; decode, extraction, and classifier together measured 64.96 ms
mean / 84.40 ms p95. These are offline archive-image timings, not live browser
end-to-end latency.

## Interpretation and decision

The SVC is a much stronger **letter candidate on this archive's image split**
than the current one-reference-per-label heuristic. This is useful evidence
that the project should move beyond its heuristic letter matcher. It is not
evidence that the SVC can grade a learner correctly: the archive has neither
negative examples nor participant metadata, and exact-deduplicated folder
splits may still share signers, capture sessions, and near-duplicate images.
The 9.34% of test images without usable landmarks also abstain; the SVC has no
validated rejection threshold or probability calibration.

The relative two-hand feature did not improve validation macro-F1, so it was
not selected. This result does not prove two-hand geometry is unnecessary;
capture variation and labels in this archive are not independently verified.

The SVC remains an experimental artifact and is **not wired into production**.
No false-acceptance rate, incomplete-pose rejection rate, unknown-sign
performance, digits performance, or held-out-person performance can be
reported from this archive.

## Reproduction

From the repository root in PowerShell, with the project `.venv` active or by
using its Python directly:

```powershell
.\.venv\Scripts\python.exe tools\train_archive_landmark_candidate.py `
  --archive C:\Users\admin\Downloads\Dataset.zip `
  --output-model ml_models\landmark_svc_letters_experimental.joblib `
  --report scratch\letter_archive_evaluation.json

.\.venv\Scripts\python.exe tools\evaluate_archive_active_baseline.py `
  --archive C:\Users\admin\Downloads\Dataset.zip `
  --model ml_models\landmark_svc_letters_experimental.joblib `
  --report scratch\letter_archive_evaluation.json
```

The first command removes exact duplicates, extracts landmarks, fits both
feature variants, selects by validation macro-F1, evaluates both on the
remaining Testing images, and writes the experimental model and report. The
second command runs the active heuristic and selected SVC on the same
deduplicated Testing images and adds their side-by-side confusion matrices and
timings. Both commands require the user-provided archive and MediaPipe model
asset already present in `models/hand_landmarker.task`.

## Next data required

To consider production integration, first review all 35 curriculum references
and meanings with an ISL expert. Then collect participant/session-labeled
examples for all reviewed signs, including wrong signs, incomplete attempts,
transitions, no-hand and tracking failures. Reserve unseen participants for
test and include target-labeled negatives for threshold selection and false
acceptance measurement. Dynamic signs require clips, not still images.
