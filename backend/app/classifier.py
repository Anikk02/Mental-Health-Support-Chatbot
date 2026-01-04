"""
Advanced feature extractor for MentalChat.

Features:
- Sentiment + emotion (delegates to classifier if available)
- Fuzzy matching for risky/trigger words (typo tolerant)
- Semantic similarity via sentence-transformers (if installed) or TF-IDF fallback
- Weighted risk scoring (0-100)
- Crisis escalation policy that returns recommended action
"""

import math
import numpy as np
import torch
from typing import Dict, List, Tuple, Any
from .config import CLASSIFIER_MODEL, USE_CUDA
import logging

# optional libs — we try to import them but gracefully degrade if absent
try:
    from rapidfuzz import fuzz
    _HAS_RAPIDFUZZ = True
except Exception:
    import difflib
    _HAS_RAPIDFUZZ = False

# semantic embeddings: try sentence-transformers first, else sklearn TF-IDF fallback
try:
    from sentence_transformers import SentenceTransformer, util as st_util
    _HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    _HAS_SENTENCE_TRANSFORMERS = False
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        _HAS_SKLEARN_TFIDF = True
    except Exception:
        _HAS_SKLEARN_TFIDF = False

# classifier fallback (previous code's model)
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---------------------------------------------------
# Logging
# ---------------------------------------------------
logger = logging.getLogger("features")
logger.setLevel(logging.INFO)

# ---------------------------------------------------
# Risk word categories (expanded)
# Keep these lists relatively short in code; consider loading from file if they grow.
# ---------------------------------------------------
# 🔥 High-risk suicide/self-harm phrases
HIGH_RISK_TERMS = [
    "suicide", "kill myself", "end my life", "i want to die",
    "i don’t want to live", "i want to disappear", "self harm",
    "self-harm", "hurt myself", "cut myself", "cutting",
    "taking pills", "overdose", "overdosing", "i will overdose",
    "jump off", "jump from", "jumping off", "hang myself",
    "hanging", "shoot myself", "stab myself", "slit my wrists",
    "kill me", "wish i were dead", "life is pointless",
    "ending it all", "end it all", "drink bleach",
    "poison myself", "drive off a bridge", "drowning myself",
    "hurt myself on purpose", "bleeding out", "i’m done living",
    "nobody would care if i died", "i can’t go on",
    "thinking about dying", "planning to die"
]

# 🟡 Medium-risk emotional breakdown/hopelessness
MEDIUM_RISK_TERMS = [
    "i feel like giving up", "i’m losing control", "i can't handle life",
    "i hate myself", "i feel numb", "i’m not okay", "i feel broken",
    "wish i would vanish", "vanish forever", "i feel unsafe",
    "i'm scared of myself", "dark thoughts", "negative thoughts",
    "intrusive thoughts", "hurting myself", "i don't care anymore",
    "nothing matters", "i feel hopeless", "i feel helpless",
    "everything is collapsing", "life is falling apart",
    "my life is a mess", "i ruin everything", "i feel like i'm drowning",
    "i feel dead inside", "i’m spiraling", "i’m losing hope",
    "i’m exhausted with life", "i don't want to wake up",
    "i wish i didn’t exist", "i shouldn’t be here",
    "i feel like a burden", "everyone hates me",
    "i'm better off gone"
]

# 🟢 Emotional triggers — anxiety, depression, stress etc.
EMOTIONAL_TRIGGER_WORDS = [
    "overwhelmed", "anxious", "anxiety", "panic", "panic attack",
    "stressed", "stress", "scared", "fear", "afraid",
    "depressed", "depression", "lonely", "alone", "hopeless",
    "empty", "lost", "sad", "crying", "crying nonstop",
    "burnout", "fatigue", "tired of everything",
    "mental breakdown", "breakdown", "suffocating",
    "worthless", "useless", "failure", "broken",
    "trauma", "flashbacks", "nightmares", "unloved",
    "unwanted", "no one understands me", "numb",
    "overthinking", "mind racing", "shaking",
    "frustrated", "guilt", "shame", "emotional pain"
]

# 🔥 Optional: Violence toward others
AGGRESSION_TERMS = [
    "hurt someone", "hit someone", "kill someone", "stab someone",
    "violent thoughts", "rage", "attack someone",
    "dangerous thoughts"
]

# combine
RISKY_TERMS = list(dict.fromkeys(HIGH_RISK_TERMS + MEDIUM_RISK_TERMS + AGGRESSION_TERMS))
TRIGGER_WORDS = EMOTIONAL_TRIGGER_WORDS


# ---------------------------------------------
# RISK SCORING WEIGHTS
# ---------------------------------------------
WEIGHTS = {
    "high_risk_match": 50.0,
    "medium_risk_match": 25.0,
    "aggression_match": 30.0,
    "fuzzy_match_bonus": 8.0,
    "semantic_match_bonus": 12.0,
    "sentiment_negative_bonus": 10.0,
}

ESCALATION_THRESHOLDS = {
    "call_emergency": 85,
    "notify_admin": 60,
    "monitor": 30,
    "none": 0
}

FUZZY_RATIO_THRESHOLD = 85
FUZZY_RATIO_THRESHOLD_LOW = 70

SEMANTIC_SIM_HIGH = 0.70
SEMANTIC_SIM_MED = 0.55


# ---------------------------------------------
# CACHES
# ---------------------------------------------
_classifier_cache = {"model": None, "tokenizer": None, "labels": None, "device": None}

_embedding_model = None
_embedding_method = None
_st_embeddings = None
_tfidf_vectorizer = None
_tfidf_matrix = None


# ---------------------------------------------
# DEVICE
# ---------------------------------------------
def _get_device():
    if str(USE_CUDA).lower() == "true":
        return torch.device("cuda")
    if str(USE_CUDA).lower() == "false":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ---------------------------------------------
# EMBEDDING INITIALIZATION
# ---------------------------------------------
def init_embeddings():
    global _embedding_model, _embedding_method, _st_embeddings
    global _tfidf_vectorizer, _tfidf_matrix

    if _embedding_method is not None:
        return

    if _HAS_SENTENCE_TRANSFORMERS:
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            _embedding_model = model
            _embedding_method = "sentence-transformers"
            _st_embeddings = model.encode(RISKY_TERMS, convert_to_tensor=True)
            logger.info("[features] Using sentence-transformers")
            return
        except Exception:
            pass

    if _HAS_SKLEARN_TFIDF:
        try:
            vec = TfidfVectorizer()
            _tfidf_vectorizer = vec
            _tfidf_matrix = vec.fit_transform(RISKY_TERMS)
            _embedding_method = "tfidf"
            logger.info("[features] Using TF-IDF fallback")
            return
        except Exception:
            pass

    _embedding_method = None
    logger.info("[features] No embeddings available.")


# ---------------------------------------------
# CLASSIFIER (sentiment/emotion)
# ---------------------------------------------
def load_classifier(model_name=CLASSIFIER_MODEL):
    if _classifier_cache["model"]:
        return (
            _classifier_cache["model"],
            _classifier_cache["tokenizer"],
            _classifier_cache["labels"],
            _classifier_cache["device"],
        )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    device = _get_device()
    model.to(device).eval()

    labels = model.config.id2label.values() if hasattr(model.config, "id2label") else None

    _classifier_cache.update({
        "model": model,
        "tokenizer": tokenizer,
        "labels": list(labels) if labels else None,
        "device": device,
    })

    logger.info(f"[features] Loaded classifier {model_name} on {device}")
    return model, tokenizer, _classifier_cache["labels"], device


# ---------------------------------------------
# SENTIMENT + EMOTION
# ---------------------------------------------
# ==========================================================
# IMPROVED SENTIMENT + EMOTION CLASSIFIER
# ==========================================================

POSITIVE_WORDS = [
    # Happiness / Joy
    "joy", "happy", "delight", "pleasure", "cheerful", "glad",
    "delighted", "joyful", "ecstatic", "content", "satisfied",
    "peaceful", "uplifted", "buoyant", "radiant",

    # Hope / Optimism
    "optimistic", "hopeful", "encouraged", "confident", "reassured",
    "inspired", "motivated", "positive",

    # Love / Affection
    "love", "caring", "affection", "warm", "warmth",
    "valued", "supported", "connected",

    # Calm / Relaxation
    "calm", "relaxed", "peace", "serene", "tranquil",
    "centered", "grounded",

    # Gratitude
    "grateful", "thankful", "appreciative",

    # Achievement / Pride
    "proud", "accomplished", "successful", "productive"
]


NEGATIVE_WORDS = [
    # Sadness / Low mood
    "sad", "down", "unhappy", "heartbroken", "depressed",
    "lonely", "grief", "mourning", "hurt", "sorrow",
    "melancholy", "hopeless", "despair", "empty",

    # Anger / Irritation
    "anger", "angry", "furious", "irritated", "frustrated",
    "annoyed", "resentful", "outraged", "hostile",

    # Fear / Anxiety
    "fear", "afraid", "scared", "terrified", "petrified",
    "anxiety", "anxious", "worried", "panic", "panicking",
    "nervous", "tense", "uneasy", "insecure",

    # Stress / Overwhelm
    "stress", "stressed", "distress", "overwhelmed",
    "pressured", "burdened", "exhausted", "burnout",

    # Shame / Guilt
    "ashamed", "guilty", "embarrassed", "regretful",

    # Confusion / Disorientation
    "lost", "conflicted", "troubled", "uncertain"
]


NEUTRAL_WORDS = [
    # Neutral
    "neutral", "fine", "ok", "okay", "ordinary", "normal",
    "average", "typical", "steady", "stable",

    # Mixed feelings
    "uncertain", "mixed", "meh", "indifferent",
    "unsure", "confused", "ambivalent",

    # Flat / Numb
    "blank", "numb", "apathetic", "detached"
]



def classify_sentiment(label: str, conf: float):
    """
    Convert emotion label → numeric sentiment score.
    Positive emotions return +conf
    Negative emotions return -conf
    Neutral returns 0
    """
    lname = label.lower()

    if any(w in lname for w in POSITIVE_WORDS):
        return conf

    if any(w in lname for w in NEGATIVE_WORDS):
        return -conf

    if any(w in lname for w in NEUTRAL_WORDS):
        return 0.0

    # Unknown: treat as neutral
    return 0.0


def predict_sentiment_and_emotion(text: str) -> Dict:
    try:
        model, tokenizer, labels, device = load_classifier()
    except Exception:
        return {"user_sentiment": 0.0, "emotion_labels": "unknown(0.00)"}

    # tokenize
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)

    # model inference
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]

    # ===========================
    # CASE 1 — BINARY CLASSIFIER
    # ===========================
    if labels and len(labels) == 2:
        pos_prob = float(probs[1])
        sentiment = (pos_prob - 0.5) * 2   # -1 to +1 scale

        return {
            "user_sentiment": round(sentiment, 4),
            "emotion_labels": f"{labels[1]}({pos_prob:.3f})",
        }

    # ===========================
    # CASE 2 — MULTICLASS CLASSIFIER
    # ===========================
    if labels:
        idx = int(probs.argmax())       # index of strongest emotion
        label = labels[idx]             # emotion label string
        conf = float(probs[idx])        # confidence score

        # improved sentiment logic
        sentiment = classify_sentiment(label, conf)

        # this format works with Emotion Distribution
        emotion_str = f"{label}({conf:.3f})"

        return {
            "user_sentiment": round(sentiment, 4),
            "emotion_labels": emotion_str,
        }

    # fallback
    return {"user_sentiment": 0.0, "emotion_labels": "unknown(0.00)"}


# ---------------------------------------------
# FUZZY MATCHING
# ---------------------------------------------
def fuzzy_match_score(term: str, text: str) -> float:
    t = term.lower()
    s = text.lower()

    if _HAS_RAPIDFUZZ:
        return fuzz.token_set_ratio(t, s) / 100.0

    # difflib fallback
    best = 0.0
    words = s.split()
    for L in range(1, min(6, len(words) + 1)):
        for i in range(0, len(words) - L + 1):
            chunk = " ".join(words[i:i+L])
            score = difflib.SequenceMatcher(None, t, chunk).ratio()
            best = max(best, score)
    return best


# ---------------------------------------------
# SEMANTIC SIMILARITY
# ---------------------------------------------
def semantic_similarity_best(text: str) -> Tuple[float, int]:
    init_embeddings()

    if _embedding_method == "sentence-transformers":
        q_emb = _embedding_model.encode(text, convert_to_tensor=True)
        sims = st_util.cos_sim(q_emb, _st_embeddings).cpu().numpy()[0]
        idx = int(np.argmax(sims))
        return float(sims[idx]), idx

    if _embedding_method == "tfidf":
        q = _tfidf_vectorizer.transform([text])
        sims = cosine_similarity(q, _tfidf_matrix).flatten()
        idx = int(np.argmax(sims))
        return float(sims[idx]), idx

    return 0.0, -1


# ---------------------------------------------
# RISK ASSESSMENT
# ---------------------------------------------
def assess_risk(text: str) -> Dict[str, Any]:
    text_l = text.lower()
    matched = []
    score = 0.0
    components = []

    # direct matches
    for t in HIGH_RISK_TERMS:
        if t in text_l:
            matched.append(t)
            components.append(("high_direct", t, WEIGHTS["high_risk_match"]))
            score += WEIGHTS["high_risk_match"]

    for t in MEDIUM_RISK_TERMS:
        if t in text_l:
            matched.append(t)
            components.append(("medium_direct", t, WEIGHTS["medium_risk_match"]))
            score += WEIGHTS["medium_risk_match"]

    for t in AGGRESSION_TERMS:
        if t in text_l:
            matched.append(t)
            components.append(("aggression_direct", t, WEIGHTS["aggression_match"]))
            score += WEIGHTS["aggression_match"]

    # fuzzy matches
    for t in RISKY_TERMS:
        f = fuzzy_match_score(t, text_l)
        if f >= FUZZY_RATIO_THRESHOLD / 100:
            bonus = WEIGHTS["fuzzy_match_bonus"] * f
            score += bonus
        elif f >= FUZZY_RATIO_THRESHOLD_LOW / 100:
            bonus = WEIGHTS["fuzzy_match_bonus"] * 0.4 * f
            score += bonus

    # semantic similarity
    sim, idx = semantic_similarity_best(text)
    if idx != -1:
        if sim >= SEMANTIC_SIM_HIGH:
            score += WEIGHTS["semantic_match_bonus"] * sim
        elif sim >= SEMANTIC_SIM_MED:
            score += WEIGHTS["semantic_match_bonus"] * 0.5 * sim

    # trigger detection
    trigger = "none"
    for t in TRIGGER_WORDS:
        if t in text_l:
            trigger = t
            break

    # sentiment contribution
    se = predict_sentiment_and_emotion(text)
    sentiment = float(se.get("user_sentiment", 0.0))
    if sentiment < -0.4:
        score += WEIGHTS["sentiment_negative_bonus"] * abs(sentiment)

    score = min(100.0, max(0.0, score))

    # escalation
    if score >= ESCALATION_THRESHOLDS["call_emergency"]:
        escalation = "call_emergency"
    elif score >= ESCALATION_THRESHOLDS["notify_admin"]:
        escalation = "notify_admin"
    elif score >= ESCALATION_THRESHOLDS["monitor"]:
        escalation = "monitor"
    else:
        escalation = "none"

    return {
        "risk_score": round(score, 2),
        "matched_terms": matched,
        "trigger_word": trigger,
        "emotion_labels": se["emotion_labels"],
        "sentiment": sentiment,
        "escalation": escalation,
    }


# ---------------------------------------------
# FINAL FEATURE PACKAGE (for DB)
# ---------------------------------------------
def extract_features(text: str) -> Dict:
    assessment = assess_risk(text)
    sentiment = assessment["sentiment"]
    risk = assessment["risk_score"]

    return {
        "emotion_labels": assessment["emotion_labels"],
        "user_sentiment": float(sentiment),
        "trigger_word": assessment["trigger_word"],
        "response_empathy_score": 0.0,
        "risky_term_count": len(assessment["matched_terms"]),
        "risk_intensity_score": round(risk / 100.0, 4),
        "input_length": len(text.split()),
        "output_length": 0,
        "safety_flag": 1 if risk >= ESCALATION_THRESHOLDS["monitor"] else 0,
        "escalation_action": assessment["escalation"],
        "assessment_raw": assessment,
    }