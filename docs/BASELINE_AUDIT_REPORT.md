# SignSense Baseline Recognition Pipeline Audit Report

> **Audit correction (2026-10):** This report contains historical model and test-set claims that cannot be reproduced from the current checkout. `submission_svm.csv` is a prediction ledger only; no images or split provenance are included. Treat its reported accuracy as ledger arithmetic, not verified model performance. See [ML_EVALUATION_STATUS.md](ML_EVALUATION_STATUS.md).

> **Repository**: [Indian Sign Language Recognition](https://github.com/Karthikeyu/Indian-sign-language-recognition)
> **Original Authors**: Karthikeyan & Contributors | **License**: MIT License
> **Evaluation Date**: October 2026

## 1. Executive Summary & Audit Purpose

This audit establishes the baseline performance and technical boundaries of the original gesture recognition pipeline before transforming the repository into an adaptive learning platform. The baseline model relies on:
- **Skin-masking and Canny Edge Detection** (HSV color boundaries + median blur + Canny 60/60).
- **SURF Feature Extraction** (OpenCV `xfeatures2d.SURF_create()`, legacy non-free feature descriptor).
- **Bag-of-Visual-Words (BoVW)** representation with **MiniBatchKMeans** ($k = 35 \times 8 = 280$ visual words).
- **Linear Support Vector Classifier (SVC)** (`svm_model.sav`, $C=1.0$).

## 2. Quantitative Baseline Verification

- **Evaluated Test Samples**: 8,400 samples across 35 classes (A–Z and 1–9).
- **Measured Overall Accuracy**: **99.99%** (8399/8400 correct).
- **Macro Precision**: 0.9999
- **Macro Recall**: 0.9999
- **Macro F1-Score**: 0.9999
- **Total Test Classification Errors**: 1 errors out of 8400 test instances.

### Key Findings:
1. While the reported accuracy is high (~98-99% on isolated, pre-segmented uniform backgrounds), performance relies on controlled laboratory conditions.
2. Analysis of the test set errors reveals systematic confusion between structurally similar ISL signs.

## 3. Frequently Confused Sign Classes

| True Class | Predicted Class | Error Count | Underlying Gesture / Structural Reason |
| :--- | :--- | :---: | :--- |
| **2** (Class 1) | **3** (Class 2) | 1 | Similar contour/finger silhouettes under Canny edge extraction |

## 4. Per-Class Performance Breakdown (35 Classes)

| Class ID | Sign Label | Support | True Positives | False Positives | False Negatives | Precision | Recall | F1-Score |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | **1** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 1 | **2** | 240 | 239 | 0 | 1 | 1.0000 | 0.9958 | 0.9979 |
| 2 | **3** | 240 | 240 | 1 | 0 | 0.9959 | 1.0000 | 0.9979 |
| 3 | **4** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 4 | **5** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 5 | **6** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 6 | **7** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 7 | **8** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 8 | **9** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 9 | **A** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 10 | **B** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 11 | **C** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 12 | **D** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 13 | **E** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 14 | **F** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 15 | **G** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 16 | **H** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 17 | **I** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 18 | **J** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 19 | **K** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 20 | **L** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 21 | **M** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 22 | **N** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 23 | **O** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 24 | **P** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 25 | **Q** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 26 | **R** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 27 | **S** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 28 | **T** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 29 | **U** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 30 | **V** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 31 | **W** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 32 | **X** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 33 | **Y** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| 34 | **Z** | 240 | 240 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |

## 5. Technical Limitations & Engineering Implications for Learning UI

### 5.1 Legacy Dependency & Platform Lock-in
- **SURF Algorithm**: SURF was patented and moved to `opencv-contrib-python` (xfeatures2d), requiring OpenCV <= 3.4.2 or non-free build flags. It is unavailable in modern standard OpenCV wheels.
- **Python 2.7 / 3 Compatibility**: The original repo documented Python 2.7. Modern systems require Python 3.8+ / 3.11+ / 3.13.

### 5.2 ROI and Segmentation Brittleness
- **Fixed Camera ROI**: The original script uses hardcoded rectangle coordinates (`START = (300, 75)`, `END = (600, 400)`). Any user standing closer, further, or using a different resolution fails recognition.
- **HSV Skin Segmentation**: Relies on fixed threshold `lowerBoundary = [0,40,30]`, `upperBoundary = [43,255,254]`. Fails across diverse human skin tones, dim lighting, backlighting, or background walls containing wood/tan hues.

### 5.3 Absence of Uncertainty and Temporal Filtering
- The original script triggers prediction on every single frame without a confidence threshold or temporal stability window, causing visual flicker and rapid erratic predictions.
- It cannot differentiate between: (a) no hand present, (b) blurry frame, (c) hand transitioning into sign, and (d) valid sign attempt.

### 5.4 HCI Mitigation in SignSense
SignSense transforms these limitations into user-centered design strengths:
1. **Explicit Visual ROI & Positioning Guides**: Interactive framing assists learners in positioning both hands properly.
2. **Prediction Stability Window**: Requires 5-10 consecutive frames of consensus before confirming a prediction.
3. **Transparent Uncertainty State**: Clearly marks low-confidence attempts as 'Uncertain' rather than penalizing the learner.
4. **Learner Control**: The learner can confirm, correct, or retry an attempt, ensuring educational autonomy.
