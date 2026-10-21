# SignSense limitations

## Current boundaries

- The production teaching flow uses browser hand tracking and rule/template comparisons. This has not been validated as reliable ISL recognition on independent participants.
- Demo mode can force illustrative outcomes. These are fictional and must be labelled as demo results. They are not recognition evidence or learner performance.
- Rules and thresholds can help explain framing or pose differences, but they cannot establish sign correctness without validation by Deaf ISL signers and educators.
- There are 35 curriculum entries: numerals 1–9 and letters A–Z. All bundled images, labels, hand counts, and instructions are unverified. Sign 9 is specifically flagged.
- Some ISL signs require movement, location, facial expression, body posture, or regional context. A still image and hand-only features may not represent these distinctions.
- Camera performance may vary with lighting, skin tone, occlusion, device, distance, and background. No broad-condition robustness claim is supported.
- No study has measured learning gain, accessibility conformance, or long-term retention. The five-person test in `usability-test-plan.md` is planned, not completed.

## Future work

1. Co-design with Deaf ISL learners, Deaf educators, and regional communities.
2. Replace or verify content with consented, provenance-tracked ISL reference material.
3. Collect a participant- and session-diverse labeled dataset with consent and a retention plan.
4. Evaluate recognition and false acceptance on held-out participants and conditions.
5. Add validated two-hand and temporal representation where the sign requires it.
6. Extend to contextual, sentence-level signs only with linguistic expertise and suitable data.
7. Evaluate mobile layouts, cameras, assistive technology, and low-cost devices.

See [`docs/ML_EVALUATION_STATUS.md`](../ML_EVALUATION_STATUS.md), [`docs/content-verification.md`](../content-verification.md), and [`accessibility.md`](accessibility.md).
