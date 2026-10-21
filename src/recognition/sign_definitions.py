"""
SignSense Class-Specific Sign Definitions & Validated Check Specifications
Defines required biomechanical constraints, validated checks, and limitations
for each of the 35 Indian Sign Language (ISL) curriculum classes (1-9, A-Z).
"""
from typing import Dict, Any, List, Optional


class SignDefinitionCatalog:
    """Catalog of verified biomechanical requirements for ISL curriculum signs."""

    DEFINITIONS: Dict[str, Dict[str, Any]] = {
        # ---------------- Stage 1: Single-Handed Numerals (1-5) ----------------
        "1": {
            "label": "1",
            "name": "Numeral 1",
            "category": "single_handed_numeral",
            "required_hands": 1,
            "required_fingers": ["index"],
            "forbidden_fingers": ["middle", "ring", "pinky"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Hold dominant index finger extended upright; keep thumb and other 3 fingers folded into palm."
        },
        "2": {
            "label": "2",
            "name": "Numeral 2",
            "category": "single_handed_numeral",
            "required_hands": 1,
            "required_fingers": ["index", "middle"],
            "forbidden_fingers": ["ring", "pinky"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Extend index and middle fingers upwards in a V-shape; fold ring and pinky fingers."
        },
        "3": {
            "label": "3",
            "name": "Numeral 3",
            "category": "single_handed_numeral",
            "required_hands": 1,
            "required_fingers": ["index", "middle", "ring"],
            "forbidden_fingers": ["pinky"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Extend index, middle, and ring fingers upright; thumb holds pinky folded against palm."
        },
        "4": {
            "label": "4",
            "name": "Numeral 4",
            "category": "single_handed_numeral",
            "required_hands": 1,
            "required_fingers": ["index", "middle", "ring", "pinky"],
            "forbidden_fingers": [],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Extend all four fingers (index, middle, ring, pinky) upright; thumb folded flat across palm."
        },
        "5": {
            "label": "5",
            "name": "Numeral 5",
            "category": "single_handed_numeral",
            "required_hands": 1,
            "required_fingers": ["thumb", "index", "middle", "ring", "pinky"],
            "forbidden_fingers": [],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Open hand fully with all five digits extended and naturally spread."
        },

        # ---------------- Stage 2: Two-Handed Numerals (6-9) ----------------
        "6": {
            "label": "6",
            "name": "Numeral 6",
            "category": "two_handed_numeral",
            "required_hands": 2,
            "dominant_counting_fingers": 1,
            "dominant_required_fingers": ["index"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand holds flat open palm (5); dominant index finger touches palm (5 + 1 = 6)."
        },
        "7": {
            "label": "7",
            "name": "Numeral 7",
            "category": "two_handed_numeral",
            "required_hands": 2,
            "dominant_counting_fingers": 2,
            "dominant_required_fingers": ["index", "middle"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand holds flat open palm (5); dominant index & middle fingers placed across it (5 + 2 = 7)."
        },
        "8": {
            "label": "8",
            "name": "Numeral 8",
            "category": "two_handed_numeral",
            "required_hands": 2,
            "dominant_counting_fingers": 3,
            "dominant_required_fingers": ["index", "middle", "ring"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand holds flat open palm (5); dominant 3 fingers placed across it (5 + 3 = 8)."
        },
        "9": {
            "label": "9",
            "name": "Numeral 9",
            "category": "two_handed_numeral",
            "required_hands": 2,
            "dominant_counting_fingers": 4,
            "dominant_required_fingers": ["index", "middle", "ring", "pinky"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand holds flat open palm (5); dominant 4 fingers placed across it (5 + 4 = 9)."
        },

        # ---------------- Stage 3: Two-Handed Vowels (A, E, I, O, U) ----------------
        "A": {
            "label": "A",
            "name": "Letter A",
            "category": "two_handed_vowel",
            "required_hands": 2,
            "vowel_target_finger": "thumb",
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand open with palm forward; dominant index finger touches the non-dominant thumb tip."
        },
        "E": {
            "label": "E",
            "name": "Letter E",
            "category": "two_handed_vowel",
            "required_hands": 2,
            "vowel_target_finger": "index",
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand open with palm forward; dominant index finger touches the non-dominant index fingertip."
        },
        "I": {
            "label": "I",
            "name": "Letter I",
            "category": "two_handed_vowel",
            "required_hands": 2,
            "vowel_target_finger": "middle",
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand open with palm forward; dominant index finger touches the non-dominant middle fingertip."
        },
        "O": {
            "label": "O",
            "name": "Letter O",
            "category": "two_handed_vowel",
            "required_hands": 2,
            "vowel_target_finger": "ring",
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand open with palm forward; dominant index finger touches the non-dominant ring fingertip."
        },
        "U": {
            "label": "U",
            "name": "Letter U",
            "category": "two_handed_vowel",
            "required_hands": 2,
            "vowel_target_finger": "pinky",
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant hand open with palm forward; dominant index finger touches the non-dominant pinky fingertip."
        },

        # ---------------- Stage 4-6: Consonants (B-Z) ----------------
        "B": {
            "label": "B",
            "name": "Letter B",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Both hands touch thumb-to-thumb and index-to-index, forming two circular loops resembling 'B'."
        },
        "C": {
            "label": "C",
            "name": "Letter C",
            "category": "single_handed_consonant",
            "required_hands": 1,
            "required_palm_facing": "side",
            "has_validated_checks": True,
            "description": "One hand: Curve hand into a 'C' silhouette with thumb and curved fingers opposing each other."
        },
        "D": {
            "label": "D",
            "name": "Letter D",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant index points vertically; dominant index and thumb form curved loop touching stem."
        },
        "F": {
            "label": "F",
            "name": "Letter F",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Place two extended dominant fingers across two extended non-dominant fingers."
        },
        "G": {
            "label": "G",
            "name": "Letter G",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Both fists placed together horizontally with knuckles aligned."
        },
        "H": {
            "label": "H",
            "name": "Letter H",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant palm held horizontally; dominant flat palm sweeps across it."
        },
        "J": {
            "label": "J",
            "name": "Letter J",
            "category": "single_handed_consonant",
            "required_hands": 1,
            "required_fingers": ["index"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "One hand: Trace a 'J' curve in the air with dominant index finger."
        },
        "K": {
            "label": "K",
            "name": "Letter K",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Dominant index finger hooks over non-dominant upright index finger."
        },
        "L": {
            "label": "L",
            "name": "Letter L",
            "category": "single_handed_consonant",
            "required_hands": 1,
            "required_fingers": ["thumb", "index"],
            "forbidden_fingers": ["middle", "ring", "pinky"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "One hand: Form an 'L' shape with thumb and index finger at 90 degrees; fold other fingers."
        },
        "M": {
            "label": "M",
            "name": "Letter M",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "dominant_counting_fingers": 3,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Lay dominant 3 fingers (index, middle, ring) across non-dominant open palm (3 legs of 'M')."
        },
        "N": {
            "label": "N",
            "name": "Letter N",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "dominant_counting_fingers": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Lay dominant 2 fingers (index, middle) across non-dominant open palm (2 legs of 'N')."
        },
        "P": {
            "label": "P",
            "name": "Letter P",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant index points vertically; dominant index and thumb form loop touching top."
        },
        "Q": {
            "label": "Q",
            "name": "Letter Q",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant thumb and index form a circle; dominant index hooks into bottom."
        },
        "R": {
            "label": "R",
            "name": "Letter R",
            "category": "single_handed_consonant",
            "required_hands": 1,
            "required_fingers": ["index", "middle"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "One hand: Cross middle finger over index finger with other fingers folded."
        },
        "S": {
            "label": "S",
            "name": "Letter S",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Hook both pinky fingers together while other fingers form loose fists."
        },
        "T": {
            "label": "T",
            "name": "Letter T",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Touch dominant index finger to the side edge of non-dominant flat palm."
        },
        "V": {
            "label": "V",
            "name": "Letter V",
            "category": "single_handed_consonant",
            "required_hands": 1,
            "required_fingers": ["index", "middle"],
            "forbidden_fingers": ["ring", "pinky"],
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "One hand: Extend index and middle fingers in a clear, spread 'V' shape."
        },
        "W": {
            "label": "W",
            "name": "Letter W",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Interlock fingers of both hands upright with palms facing each other."
        },
        "X": {
            "label": "X",
            "name": "Letter X",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Cross both extended index fingers over each other to form an 'X'."
        },
        "Y": {
            "label": "Y",
            "name": "Letter Y",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Non-dominant thumb and index form 'V'; dominant index rests between them."
        },
        "Z": {
            "label": "Z",
            "name": "Letter Z",
            "category": "two_handed_consonant",
            "required_hands": 2,
            "required_palm_facing": "camera",
            "has_validated_checks": True,
            "description": "Two hands: Hold non-dominant palm flat; dominant index finger traces a 'Z' across it."
        }
    }

    @classmethod
    def get_definition(cls, sign_label: str) -> Optional[Dict[str, Any]]:
        return cls.DEFINITIONS.get(str(sign_label).upper())

    @classmethod
    def get_all_definitions(cls) -> Dict[str, Dict[str, Any]]:
        return cls.DEFINITIONS
