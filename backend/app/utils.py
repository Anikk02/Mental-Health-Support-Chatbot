"""
Formatting, crisis detection, and response analysis helpers.
Updated for production backend + final dataset structure.
"""

import re
from typing import Dict
from datetime import datetime

# -------------------------------------------------
# 1. Updated crisis detection dictionary
# -------------------------------------------------

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "self harm", "hurt myself",
    "want to die", "i want to die", "die myself", "give up", "giveup",
    "can't go on", "cant go on", "no point living", "life is pointless",
    "hopeless", "i'm done", "im done", "end it all", "cut myself",
    "slit", "bleed", "my life is over", "wish to die", "kill me"
]

def detect_crisis(text: str) -> bool:
    """Identify suicidal / crisis content based on keyword scanning."""
    t = (text or "").lower().strip()
    for k in CRISIS_KEYWORDS:
        if k in t:
            return True
    return False


# -------------------------------------------------
# 2. Format input text into the EXACT prompt style used in training
# -------------------------------------------------

def format_input_from_features(features: Dict) -> str:
    """
    Formats features into the precise multi-line text block
    used for T5 training.
    Output Length is NOT included (label only).
    """

    return (
        f"User Input: {features.get('user_input','').strip()}\n"
        f"Emotions: {features.get('emotion_labels','none')}\n"
        f"Sentiment: {float(features.get('user_sentiment',0)):.3f}\n"
        f"Trigger Words: {features.get('trigger_word','none')}\n"
        f"Empathy Score: {float(features.get('response_empathy_score',0)):.3f}\n"
        f"Risky Terms: {int(features.get('risky_term_count',0))}\n"
        f"Risk Intensity: {float(features.get('risk_intensity_score',0)):.3f}\n"
        f"Input Length: {int(features.get('input_length',0))}\n"
        f"Safety Flag: {int(features.get('safety_flag',0))}"
    )


# -------------------------------------------------
# 3. Response Analysis (Matches training-phase metrics)
# -------------------------------------------------

def analyze_response_metrics(bot_response: str, user_input: str) -> Dict:
    """
    Computes:
      - word overlap score
      - length ratio
      - phrase match ratio
      - short response flag
    """

    def tokenize(s):
        return re.findall(r"\w+", (s or "").lower())

    b = tokenize(bot_response)
    u = tokenize(user_input)

    if not u:
        return {
            "word_overlap": 0.0,
            "length_ratio": 0.0,
            "phrase_match": 0.0,
            "short_response_flag": 1 if len(b) < 3 else 0
        }

    b_set = set(b)
    u_set = set(u)

    word_overlap = len(b_set & u_set) / max(1, len(u_set))
    phrase_match = sum(1 for w in u if w in b_set) / max(1, len(u))
    length_ratio = len(b) / max(1, len(u))

    return {
        "word_overlap": round(float(word_overlap), 4),
        "length_ratio": round(float(length_ratio), 4),
        "phrase_match": round(float(phrase_match), 4),
        "short_response_flag": 1 if len(b) < 3 else 0
    }


# -------------------------------------------------
# 4. Timestamp helper
# -------------------------------------------------

def utcnow_iso():
    return datetime.utcnow().isoformat() + "Z"
