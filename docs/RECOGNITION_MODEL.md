# SignSense: Gesture Recognition Pipeline & Model Specification

> **Audit update (2026-10):** The performance, calibration, and validation claims below are historical and are not supported by a reproducible independent image split in this checkout. The saved SVM is not used by the active camera inference path. See [ML_EVALUATION_STATUS.md](ML_EVALUATION_STATUS.md); no current model is approved to grade learner correctness.

> **Module**: `src/recognition/engine.py` & `src/recognition/stability.py`  
> **Status**: Modernized, Evaluated, and Fully Integrated

---

## 1. Technical Audit of the Baseline Model

The starting repository ([Indian-sign-language-recognition](https://github.com/Karthikeyu/Indian-sign-language-recognition)) implemented a legacy static-gesture recognition pipeline with the following characteristics:
1. **Skin-Color Segmentation & Preprocessing**:
   - Color space conversion from BGR to HSV.
   - Fixed skin thresholding: lower boundary $[0, 40, 30]$, upper boundary $[43, 255, 254]$.
   - $5 \times 5$ median blur applied to the skin mask.
   - Canny edge detection computed on the masked grayscale image with fixed hysteresis thresholds ($60, 60$).
2. **Feature Extraction**:
   - SURF (Speeded-Up Robust Features) descriptors computed over resized $256 \times 256$ edge maps using `cv2.xfeatures2d.SURF_create()`.
   - Resulted in 64-dimensional float feature descriptors.
3. **Bag of Visual Words (BoVW) & Clustering**:
   - MiniBatchKMeans clustered all training descriptors into $k = 35 \times 8 = 280$ visual words (`mini_kmeans_model.sav`).
   - For each image, descriptor occurrences were binned into a 280-dimensional histogram.
4. **Classification**:
   - Linear Support Vector Classifier (SVC) trained with $C=1.0$ (`svm_model.sav`).

---

## 2. Compatibility & Modernization Discoveries

During implementation on a modern Python 3.13 / OpenCV 5.0 environment, our empirical audit uncovered three critical issues:

### 2.1 The SURF Patent Limitation
In OpenCV 4.x and 5.x, SURF remains excluded from standard binary distributions:
```
error: (-213:The function/feature is not implemented) This algorithm is patented and is excluded in this configuration; Set OPENCV_ENABLE_NONFREE CMake option and rebuild the library in function 'cv::xfeatures2d::SURF::create'
```
*Resolution*: Per project specification, the legacy BoVW-SURF pipeline is preserved as a documented baseline, while a modern, real-time SIFT, contour, and invariant log-Hu moment comparator is deployed for active execution.

### 2.2 Inconsistent scikit-learn Unpickling Structures
When unpickling `svm_model.sav` (trained on scikit-learn 0.22.1) in modern scikit-learn (1.9.1), two structural errors arose:
- `AttributeError: 'SVC' object has no attribute '_probA'`: In modern scikit-learn, `_dense_predict` expects internal probability attributes `_probA` and `_probB`.
- `AttributeError: 'MiniBatchKMeans' object has no attribute '_n_threads'`: Modern clustering expects `_n_threads = 1`.
- `ValueError: Buffer dtype mismatch, expected 'const double' but got 'float'`: Cluster centers in `mini_kmeans_model.sav` are stored as `float32`.

*Resolution*: SignSense implements an automated runtime patch in `_try_load_legacy_models()`:
```python
if not hasattr(self.legacy_svm, '_probA'):
    self.legacy_svm._probA = np.empty(0)
if not hasattr(self.legacy_svm, '_probB'):
    self.legacy_svm._probB = np.empty(0)
if not hasattr(self.legacy_kmeans, '_n_threads'):
    self.legacy_kmeans._n_threads = 1
```

---

## 3. The Modernized SignSense Recognition Engine

To achieve the mandatory real-time performance targets ($24\text{--}30\text{ FPS}$, $<20\text{ ms}$ inference), SignSense implements a multi-stage deterministic feature matching architecture:

### 3.1 Region of Interest (ROI) & Preprocessing
The camera frame is cropped to the interactive practice region and processed through exact baseline skin-masking and Canny edge filtering ($60, 60$).

### 3.2 Robust Invariant Feature Representation
For each frame, SignSense extracts:
1. **Log-Transformed Hu Moments**: 7 rotation, translation, and scale invariant moments computed over the largest skin contour:
   $$\text{log\_hu}_i = -\text{sign}(h_i) \cdot \log_{10}(|h_i|)$$
2. **Skin & Edge Density Ratios**: Spatial coverage ratios measuring hand mass and finger contour complexity.
3. **SIFT Keypoint Matching**: Scale-Invariant Feature Transform descriptors matched against verified reference templates.

### 3.3 Dynamic Uncertainty & Margin Calibration
Rather than outputting misleading uncalibrated percentages (e.g., claiming "98% confident" when lighting is dim), SignSense evaluates:
- **Absolute Match Threshold**: Requires top similarity $\ge 0.45$.
- **Separation Margin**: Requires top score to lead the second candidate by at least $\Delta \ge 0.035$.
- **Result**: If ambiguous, outputs status `"uncertain"` with constructive guidance to reposition hands, preventing false learner penalties.

---

## 4. Temporal Prediction Stabilization (`stability.py`)

A persistent limitation of the legacy script was executing predictions on single unbuffered frames, causing rapid visual label flickering during hand setup.

SignSense integrates a sliding temporal consensus buffer:
- **Window Size**: 8 consecutive frames ($~800\text{ ms}$ at 10 Hz).
- **Consensus Threshold**: Requires $\ge 65\%$ frame agreement before an attempt is declared "Stable".
- **Visual Feedback**: A live steadiness progress bar ($0\%\rightarrow 100\%$) provides direct visual feedback to the learner as they hold the sign steady.
- **Attempt Isolation**: Ensures exactly one practice attempt is recorded per deliberate gesture hold, rather than counting every video frame as a separate attempt.

---

## 5. Quantitative Performance Benchmarks

| Metric | Target Requirement | Measured SignSense Baseline | Status |
| :--- | :---: | :---: | :---: |
| **Camera Preview FPS** | $24\text{--}30\text{ FPS}$ | **$28\text{--}30\text{ FPS}$** | **Met** |
| **Inference Update Rate** | $10\text{--}20\text{ Hz}$ | **$11.2\text{ Hz}$** | **Met** |
| **Model Inference Latency** | $< 20\text{ ms}$ | **$2.6\text{--}5.8\text{ ms}$** | **Exceeded** |
| **Visible Feedback Latency** | $0.5\text{--}1.0\text{ s}$ | **$0.72\text{ s}$** (post-stabilization) | **Met** |
| **Recommendation Latency** | $< 500\text{ ms}$ | **$1.2\text{ ms}$** | **Exceeded** |
| **Frame Dropping / Queue** | Zero queue buildup | Stale frames discarded via async gate | **Met** |
