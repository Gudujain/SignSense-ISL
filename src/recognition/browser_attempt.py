"""Server-side rules and reference-profile comparison for browser landmarks only."""
import json
import math
import os
from collections import Counter
from typing import Any

FINGERS = ('thumb', 'index', 'middle', 'ring', 'pinky')
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'data', 'signs.json')


def _distance(a, b):
    return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))


def _angle(a, b, c):
    u=[a[i]-b[i] for i in range(3)]; v=[c[i]-b[i] for i in range(3)]
    d=math.sqrt(sum(x*x for x in u)*sum(x*x for x in v))
    return math.degrees(math.acos(max(-1.0,min(1.0,sum(u[i]*v[i] for i in range(3))/d)))) if d else 0.0


def _hand_features(raw, handedness='unknown'):
    if not isinstance(raw, list) or len(raw) != 21:
        return None
    try:
        pts=[[float(v) for v in p[:3]] for p in raw]
        if any(len(p) != 3 or not all(math.isfinite(v) for v in p) for p in pts): return None
        if any(not -0.2 <= p[0] <= 1.2 or not -0.2 <= p[1] <= 1.2 or not -2 <= p[2] <= 2 for p in pts): return None
    except (TypeError, ValueError, IndexError): return None
    scale=max(_distance(pts[0],pts[9]),1e-5)
    states={}
    for name,(mcp,pip,tip) in {'index':(5,6,8),'middle':(9,10,12),'ring':(13,14,16),'pinky':(17,18,20)}.items():
        a=_angle(pts[mcp],pts[pip],pts[tip]); states[name]='extended' if a>=155 else 'curled' if a<125 else 'half'
    spread=_distance(pts[4],pts[5])/scale; across=_distance(pts[4],pts[9])/scale
    states['thumb']='out' if spread>.95 else 'across' if across<.48 else 'tucked' if spread<.55 else 'half'
    wrist=pts[0]
    vector=[]
    for p in pts: vector.extend([(p[i]-wrist[i])/scale for i in range(3)])
    return {'landmarks':pts,'handedness':str(handedness),'fingers':states,'scale':scale,'vector':vector}


def assess_landmark_window(target: str, frames: list[dict], reference_profiles: dict | None = None, template_override: dict | None = None) -> dict[str, Any]:
    """Does not persist frames. Candidate is an unvalidated reference similarity, not a probability."""
    templates = json.load(open(TEMPLATES_PATH, encoding='utf-8'))['signs']
    template = template_override if template_override is not None else next((t for t in templates if str(t['label']).upper() == str(target).upper()), None)
    if template is None:
        return {
            'outcome': 'not_seen',
            'gesture_match': 'not_seen',
            'failure_source': 'system',
            'failure_reason': 'target_unavailable',
            'hint': 'This reference is unavailable.',
            'candidate': None,
            'candidate_score': None,
            'candidate_score_type': 'unavailable',
            'perFingerErrors': [],
            'confidence': 0.0,
            'hands_detected': 0,
            'template_verified': False,
            'mastery_eligible': False,
            'verification_warning': None,
            'evidence_status': 'target_unavailable'
        }
    normalized = []
    for frame in frames[-15:]:
        raw_hands = frame.get('hands', []) if isinstance(frame, dict) else []
        hands = [f for f in (_hand_features(h.get('landmarks'), h.get('handedness')) for h in raw_hands[:2]) if f]
        normalized.append(hands)
    visible = [h for h in normalized if h]
    if not visible:
        return {
            'outcome': 'not_seen',
            'gesture_match': 'not_seen',
            'failure_source': 'system',
            'failure_reason': 'no_hand',
            'hint': 'We could not see a hand. Check camera setup and try again.',
            'candidate': None,
            'candidate_score': None,
            'candidate_score_type': 'unavailable',
            'perFingerErrors': [],
            'confidence': 0.0,
            'hands_detected': 0,
            'template_verified': bool(template.get('verified')),
            'mastery_eligible': False,
            'verification_warning': None,
            'evidence_status': 'no_hand_detected'
        }
    hands_count = Counter(len(h) for h in visible).most_common(1)[0][0]
    hands = visible[-1]
    errors = []
    expected = template['handCount']
    if hands_count != expected:
        errors.append({'hand': 'both', 'finger': None, 'reason': 'hand_count', 'expected': expected, 'observed': hands_count})
    required = template.get('hands', [])
    constraints = 0
    for hi, role in enumerate(required[:min(expected, len(hands))]):
        for finger, want in role.get('fingers', {}).items():
            if want == 'unknown':
                continue
            constraints += 1
            got = hands[hi]['fingers'].get(finger)
            match = (want == 'curled' and got in ('curled', 'tucked', 'across')) or (want == 'extended' and got in ('extended', 'out')) or got == want
            if not match:
                errors.append({'hand': role.get('role', str(hi + 1)), 'finger': finger, 'expected': want, 'observed': got})
    # Existing reference descriptors are a secondary, unvalidated signal.
    profile_scores = []
    if reference_profiles and hands:
        user = hands[0]['vector']
        un = math.sqrt(sum(x * x for x in user)) or 1
        for label, profile in reference_profiles.items():
            ref = profile.get('feature_vector')
            if ref is None or len(ref) != len(user):
                continue
            rn = math.sqrt(sum(float(x) * float(x) for x in ref)) or 1
            sim = sum(float(a) * float(b) for a, b in zip(user, ref)) / (un * rn)
            profile_scores.append((str(label).upper(), sim))
    candidate = max(profile_scores, key=lambda x: x[1])[0] if profile_scores else None
    candidate_score = max(profile_scores, key=lambda x: x[1])[1] if profile_scores else None

    if len(errors) == 0 and constraints > 0 and candidate == str(target).upper():
        outcome = 'got_it'
        hint = 'Your hand shape matched the reference cues.'
        failure_source = None
    elif len(errors) == 1 and errors[0].get('finger'):
        outcome = 'almost'
        hint = f"Check your {errors[0]['finger']} against the reference."
        failure_source = 'learner'
    else:
        outcome = 'try_again'
        hint = 'Watch the steps again, then try once more.'
        if errors and errors[0].get('reason') == 'hand_count':
            hint = 'Show both hands inside the guide.' if expected == 2 else 'Keep one hand in view for this reference.'
        failure_source = 'learner'

    template_verified = bool(template.get('verified'))
    mastery_eligible = bool(template_verified and outcome == 'got_it')
    verification_warning = (
        "ISL educator review pending. This result is provisional and does not count toward validated mastery."
        if not template_verified else None
    )

    return {
        'outcome': outcome,
        'gesture_match': outcome,
        'failure_source': failure_source,
        'hint': hint,
        'candidate': candidate,
        'candidate_score': round(candidate_score, 4) if candidate_score is not None else None,
        'candidate_score_type': 'unvalidated_reference_similarity' if candidate_score is not None else 'unavailable',
        'perFingerErrors': errors,
        'confidence': None if candidate_score is None else max(0, min(1, candidate_score)),
        'hands_detected': hands_count,
        'template_verified': template_verified,
        'mastery_eligible': mastery_eligible,
        'verification_warning': verification_warning,
        'verification_note': template.get('verificationNote'),
        'evidence_status': 'unvalidated_rule_and_reference_agreement'
    }
