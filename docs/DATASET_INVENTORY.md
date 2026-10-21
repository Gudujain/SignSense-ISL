# SignSense data and model inventory

## Current checkout inventory (2026-10-18)

| Asset | Local path | What is present | Provenance and evaluation status |
|---|---|---|---|
| Raw labeled training images | `data/` | **Absent** | README of the upstream project says it created an A–Z, 1–9 dataset with 1,200 images/class, but that dataset is not included in this checkout. The upstream README links a Google Drive download; it has not been downloaded or audited here. |
| Collection manifest | `data_collection/manifest.jsonl` | **Absent** | No consented signer/session samples are available. |
| Curriculum reference images | `src/static/references/` | 35 JPEGs, one named for each label below | These are single UI/reference images, with no image-level labels beyond filename, signer/session metadata, capture provenance, license record, or training eligibility evidence. They are not a dataset and are excluded from training/evaluation. |
| Gesture montage | `all_gestures.jpg` | One montage image | Not a labeled sample dataset. |
| Historical predictions | `submission_svm.csv` | 8,400 label-pair rows | Ledger only: no source image paths, signer/session IDs, model version, split, or scores. Never use as training labels or independent evaluation ground truth. |
| Legacy classifier | `svm_model.sav` | Serialized SVM artifact present | Not loaded in active SignSense inference. Training data, feature order, class mapping, and held-out split cannot be reconstructed from the checkout. Do not unpickle untrusted replacement artifacts. |
| Legacy visual-word model | `mini_kmeans_model.sav` | Serialized MiniBatchKMeans artifact present | Not loaded in active inference. Expected input is SURF descriptor vectors from the legacy preprocessing code. |
| Hand detector | `models/hand_landmarker.task` | MediaPipe task model present | Used for hand landmark extraction, not sign classification. |
| Landmark SVC candidate | `ml_models/landmark_svc.joblib` | **Absent** | Experimental trainer exists; model training is blocked until real consented labels exist. |

## Label inventory

The filename/curriculum vocabulary contains 35 symbols: digits `1`–`9`, then letters `A`–`Z`. This verifies the application's intended label IDs, not the semantic correctness of each reference pose as an ISL example. No qualified signer review or source attribution is attached to the local reference images. Every row therefore remains ineligible for model training and independent evaluation.

Each label ID has one correspondingly named bundled reference JPEG. The file's content has not been verified by an ISL expert; `verified ref?` therefore means no. There are zero verified labeled samples for every ID. Static/dynamic status, required hand count, signers, and sessions are unknown for every class.

| Class ID / label | Bundled reference | Ref verified? | Image count | Verified labeled samples | Signers / sessions | Motion / hands | Quality / eligibility |
|---|---|---:|---:|---:|---:|---|---|
| `1` | `1.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `2` | `2.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `3` | `3.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `4` | `4.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `5` | `5.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `6` | `6.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `7` | `7.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `8` | `8.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `9` | `9.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `A` | `A.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `B` | `B.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `C` | `C.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `D` | `D.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `E` | `E.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `F` | `F.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `G` | `G.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `H` | `H.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `I` | `I.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `J` | `J.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `K` | `K.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `L` | `L.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `M` | `M.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `N` | `N.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `O` | `O.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `P` | `P.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `Q` | `Q.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `R` | `R.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `S` | `S.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `T` | `T.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `U` | `U.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `V` | `V.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `W` | `W.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `X` | `X.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `Y` | `Y.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |
| `Z` | `Z.jpg` | No | 1 | 0 | 0 / 0 | Unknown / unknown | Single reference; ineligible |

Before training, add an expert-reviewed sign-definition record for every symbol, including hand count and whether temporal motion is required. The collector currently supports still-image labels only and cannot establish recognition of movement-based signs.

## Upstream provenance note

The local `README.md` attributes the prototype to Karthikeyu/Karthikeyan's public repository and the local `LICENSE` is MIT, copyright Karthikeyu Busa and ShravaniKatte (2020). The upstream repository README describes its own dataset and its old SURF/BoVW/SVM training procedure, but does not make that dataset available in this working tree. Its claimed 99% result is the upstream authors' historical report, not a result reproduced by SignSense. Local reference JPEGs have no individual provenance metadata, so their origin and license cannot be inferred solely from the repository-level MIT notice.

## Current counts and blocker

- Verified manifest rows: **0**.
- Participants/sessions: **0 / 0**.
- Verified training samples: **0** across all 35 labels.
- Negatives (wrong, incomplete, transition, no-hand, face-only, tracking failure): **0**.
- Evaluator, baseline, and alternative model results: **not available**.

Next data required: consented still images annotated under `research/DATASET_IMAGE_CONSENT_ADDENDUM.md` from at least three distinct pseudonymous participants, with every participant's sessions kept together. For credible signer-held-out comparison, collect substantially more than three participants and reserve several participants for a locked test before tuning. Capture complete examples for all intended labels and target-labeled negatives in each category; include capture-condition diversity and expert-reviewed labels. Do not count adjacent frames as independent samples.
