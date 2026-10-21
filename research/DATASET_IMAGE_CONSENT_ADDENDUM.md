# Optional SignSense Dataset Still-Image Consent Addendum

This is a separate, optional consent for collecting a labeled image dataset. It
is **not** covered by the existing usability-study consent, which promises that
webcam stills are not stored. Do not collect images under that existing
consent alone.

The dataset collector stores only still frames explicitly selected by the
operator. It does not write video. Images remain in the local ignored
`data_collection/` directory; do not upload, publish, or share them without
separate permission. A frame may still contain a face or other identifying
content. Hand-only capture should frame out faces and personal background
details. A face-only negative is valuable for testing false detections and
requires the additional identifiable-still consent below.

Participants can decline or stop at any time. Record only a pseudonymous
participant ID and session ID. Deletion by pseudonym removes the participant's
manifest rows and image files. Retention period, access controls, and any
publication or sharing plan must be set by the study owner before recruitment.

## Consent items

- [ ] I understand that selected still images containing my hands may be saved locally for model development and evaluation. The live video stream is not recorded.
- [ ] I understand that images may be used to evaluate wrong-sign, incomplete, transitional, and tracking/no-hand cases, and that participation is voluntary.
- [ ] I understand how my images will be stored, who can access them, the planned retention period, and how to request deletion.
- [ ] I agree to collection of the still images described above.

**Optional face-only images (additional consent):**

- [ ] I separately agree that selected still images containing my face may be saved locally as a no-hand/face-only negative example for false-detection evaluation.

Participant pseudonym: ____________________  Date: __________

Participant signature: ____________________  Researcher initials: ________

Do not use the `--consent-identifiable-stills` option unless this additional
face-only consent was obtained and documented according to the study protocol.
