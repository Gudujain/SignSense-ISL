# SignSense recognition model card

**Status: no sign classifier approved for learner grading.**

## Scope

The intended initial vocabulary is 35 isolated symbols (`1`–`9`, `A`–`Z`). No continuous signing, sentence recognition, dynamic signs, or arbitrary two-handed vocabulary is claimed. The current webcam path is an unvalidated prototype candidate generator followed by a fail-closed assessment layer; it is not an ML model validated for ISL recognition.

## Active and candidate systems

- The active browser request reaches `src/recognition/engine.py`. When MediaPipe is available, `src/recognition/pose_analyzer.py` extracts landmarks and the engine ranks one-reference-per-class landmark templates, with legacy finger-count rules for some numerals. If MediaPipe is unavailable, a skin-mask/Canny/Hu-moment reference fallback is used. These candidate mechanisms are heuristic and unvalidated; they are not calibrated and do not authorize a correct/incorrect result.
- `svm_model.sav` and `mini_kmeans_model.sav` are legacy artifacts from the SURF/Bag-of-Visual-Words/SVM project, not active SignSense inference. The historical training script used a per-class ordered image-count split, descriptor extraction, KMeans, and an SVM. Its source data is absent, so the artifact's fitted classes and test protocol cannot be independently checked.
- `src/ml/landmark_svc.py` and `tools/train_landmark_candidate.py` define a separate experimental candidate: up to two wrist-relative, hand-scale-normalized MediaPipe landmark vectors, StandardScaler, and RBF SVC. It is not wired to practice inference and has not been trained because there are no consented labeled samples.

## Data and evaluation

See [dataset inventory](DATASET_INVENTORY.md). The checkout has 35 reference JPEGs (one per label), no source manifest, no consented image set, and no independent signer-held-out test data. Reference images are not used as a validation set. The 8,400-row prediction CSV is historical label-pair output, not reproducible ground truth.

No precision, recall, F1, false-acceptance rate, rejection/coverage trade-off, calibration measure, independent latency, or model-selection result is available. There is no selected production classifier. The evaluator and trainer commands are documented in [ML evaluation status](ML_EVALUATION_STATUS.md); both require a valid participant-grouped manifest.

## Use and limitations

The learner assessment remains uncertain/not-assessed and does not award mastery from these model candidates. Do not interpret similarity or SVM decision scores as probabilities. The collection workflow stores selected stills only after separate consent confirmation. Face-only examples need additional identifiable-still consent. No images should be added to a training or test split without provenance, label review, hash validation, and signer/session grouping.

## Acceptance gate

Do not select or deploy a trained recognizer until the baseline and landmark candidate have been evaluated on the same untouched participant-disjoint test set, with a validation-only threshold, target false-acceptance analysis (including incomplete and non-signing examples), per-class and per-category results, grouped results, uncertainty intervals, and preprocessing-inclusive latency. The webcam absence and empty dataset currently prevent this gate from being run.
