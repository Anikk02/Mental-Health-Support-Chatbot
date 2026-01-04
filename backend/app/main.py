"""
Main FastAPI backend for MentalChat.
- Loads T5 chat model
- Loads sentiment/emotion classifier
- Performs crisis detection
- Saves dataset-formatted chat rows
- Returns history, mood analytics, and response metrics
"""

import torch
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
#from app.rag.rag_engine import run_rag
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rag.rag_engine import run_rag
# Local imports
from .config import MODEL_REPO, HF_TOKEN, FRONTEND_BASE
from .db import (
    users_col,
    chat_history_col,
)
from .classifier import extract_features, load_classifier, predict_sentiment_and_emotion
from .helpers import to_str_id, oid
from .utils import detect_crisis, analyze_response_metrics, format_input_from_features

# ---------------------------------------------------
# FastAPI initialization
# ---------------------------------------------------
app = FastAPI(title="MentalChat Backend API")
#from .auth import router as auth_router
#app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:3000",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from .auth import router as auth_router
app.include_router(auth_router)
# ---------------------------------------------------
# ---------------------------------------------------
# Load T5 Chat Model
# ---------------------------------------------------
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

print(f"[startup] Loading chat model from: {MODEL_REPO}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    print(f"[startup] Loading chat model from Hugging Face repo: {MODEL_REPO}")

    # Load directly from Hugging Face (private or public)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_REPO,
        token=HF_TOKEN,
        use_fast=False
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_REPO,
        token=HF_TOKEN
    )

    # Move model to device and set eval mode
    model.to(device)
    model.eval()
    print(f"[startup] Chat model loaded successfully on {device}")

except Exception as e:
    print(f"[startup] ERROR loading model from Hugging Face: {e}")
    tokenizer, model = None, None

# Final check
if not model or not tokenizer:
    print("[startup] Chat model could not be loaded.")
# Warm classifier
try:
    load_classifier()
except Exception as e:
    print("[startup] WARNING: classifier did not initialize:", e)



# ---------------------------------------------------
# Pydantic Models
# ---------------------------------------------------
class ChatRequest(BaseModel):
    userId: Optional[str] = None     # frontend camelCase
    user_id: Optional[str] = None    # fallback snake_case
    user_input: str = Field(..., min_length=1)

    # Optional pre-extracted fields
    emotion_labels: Optional[str] = None
    user_sentiment: Optional[float] = 0.0
    trigger_word: Optional[str] = None
    response_empathy_score: Optional[float] = 0.0
    risky_term_count: Optional[int] = 0
    risk_intensity_score: Optional[float] = 0.0
    input_length: Optional[int] = 0
    output_length: Optional[int] = 0
    safety_flag: Optional[int] = 0


# ---------------------------------------------------
# Chat Endpoint
IDENTITY_QUESTIONS = [
    "what's your name",
    "what is your name",
    "your name",
    "who are you",
    "who am i talking to",
    "tell me about yourself",
    "introduce yourself",
    "are you lamira",
    "what should i call you",
    "who is lamira",
]

# ---------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest, background_tasks: BackgroundTasks):
    if model is None or tokenizer is None:
        raise HTTPException(503, "Chat model not loaded on server")

    user_input = payload.user_input.strip()
    if not user_input:
        raise HTTPException(400, "Message cannot be empty")

    # Pick userId/user_id
    uid_raw = payload.userId or payload.user_id or None
    # ------------------ Resolve user (EARLY for RAG) ------------------
    resolved_uid = None
    if uid_raw:
        obj = oid(uid_raw)
        if obj:
            resolved_uid = obj
        else:
            doc = await users_col.find_one({"username": uid_raw})
            if doc:
                resolved_uid = doc["_id"]
            else:
                doc2 = await users_col.find_one({"email": uid_raw})
                if doc2:
                    resolved_uid = doc2["_id"]

    # Extract missing features
    enriched = {}
    needs_extract = (
        not payload.emotion_labels
        or str(payload.emotion_labels).lower() == "none"
        or payload.user_sentiment in (None, 0.0)
    )

    if needs_extract:
        try:
            enriched = extract_features(user_input)
        except Exception as e:
            print("[chat] classifier error:", e)
            enriched = {}

    # Merge fields
    doc_fields = {
        "emotion_labels": payload.emotion_labels or enriched.get("emotion_labels", "none"),
        "user_sentiment": float(
            payload.user_sentiment if payload.user_sentiment is not None
            else enriched.get("user_sentiment", 0.0)
        ),
        "trigger_word": payload.trigger_word or enriched.get("trigger_word", "none"),
        "response_empathy_score": float(
            payload.response_empathy_score or enriched.get("response_empathy_score", 0.0)
        ),
        "risky_term_count": int(payload.risky_term_count or enriched.get("risky_term_count", 0)),
        "risk_intensity_score": float(
            payload.risk_intensity_score or enriched.get("risk_intensity_score", 0.0)
        ),
        "input_length": int(payload.input_length or len(user_input.split())),
        "safety_flag": int(payload.safety_flag or enriched.get("safety_flag", 0)),
    }
    
    # Updated classifier on user text
    sentiment_result = predict_sentiment_and_emotion(user_input)
    
    #crisis detection
    try:
        crisis_flag = detect_crisis(user_input)
    except:
        crisis_flag = False

    # Format input for T5
    # Resolve user id for RAG memory (fallback to guest)
    # ------------------ RAG USER ID ------------------
    # ------------------ RAG USER ID ------------------
    rag_user_id = (
        str(resolved_uid)
        if resolved_uid
        else f"guest_{abs(hash(user_input))}"
        )

    rag_analysis = {
    "emotion": sentiment_result["emotion_labels"],
    "sentiment": sentiment_result["user_sentiment"],
    "risk_intensity": doc_fields["risk_intensity_score"],
    "risk_count": doc_fields["risky_term_count"],
    "input_length": doc_fields["input_length"],
    "safety_flag": doc_fields["safety_flag"],
    }

    rag_analysis.setdefault("extracted_beliefs", [])
    rag_analysis.setdefault("risk_score", rag_analysis["risk_intensity"])

    # ------------------ IDENTITY QUESTION OVERRIDE ------------------
    is_identity_question = any(
        q in user_input.lower() for q in IDENTITY_QUESTIONS
        )

    # ------------------ RAG AUGMENTATION ------------------
    if is_identity_question:
        try:
            from rag.pipeline.rag_stage2_identity import load_identity
            from rag.pipeline.identity_prompt import identity_prompt

            IDENTITY_PATH = Path(__file__).resolve().parent / "rag/data/identity/lamira_identity.json"
            identity = load_identity(IDENTITY_PATH)

            formatted = identity_prompt(identity, user_input)

        except Exception as e:
            print("[IDENTITY ERROR]", e)
            formatted = "My name is Lamira. I’m here to support you."

    elif not crisis_flag:
        try:
            formatted = run_rag(
                user_id = rag_user_id,
                user_input = user_input,
                analysis = rag_analysis
            )
        except Exception as e:
            print("[RAG ERROR] Falling back to basic prompt:", e)
            formatted = f"User Input: {user_input}\nEmotion: {rag_analysis['emotion']}"
    
    else:
        #Crisis-safe fallback(NO MEMORY, NO MEMORY OVERRIDE)
        formatted = f"User Input: {user_input}\nEmotion: {rag_analysis['emotion']}"
 
    # Generate long response (up to 512 output tokens)
    try:
        encoded = tokenizer(formatted, return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            output_ids = model.generate(
                encoded.input_ids,
                attention_mask=encoded.attention_mask,
                max_new_tokens=512,             # <<< LONG RESPONSES
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
                temperature=0.8,
                do_sample=True
            )

        reply = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    except Exception as e:
        print("[generation ERROR]", e)
        reply = "Sorry, I couldn't process that right now."

    # Compute output length
    output_length = len(reply.split())

    # Crisis detection
    try:
        crisis_flag = detect_crisis(user_input)
    except:
        crisis_flag = False

    # Analysis metrics
    try:
        metrics = analyze_response_metrics(reply, user_input)
    except:
        metrics = {}

    # Final row for DB
    db_row = {
        "user_id": resolved_uid,
        "user_input": user_input,

        # dataset fields
        "emotion_labels": sentiment_result["emotion_labels"],
        "user_sentiment": sentiment_result["user_sentiment"],
        "trigger_word": doc_fields["trigger_word"],
        "response_empathy_score": doc_fields["response_empathy_score"],
        "risky_term_count": doc_fields["risky_term_count"],
        "risk_intensity_score": doc_fields["risk_intensity_score"],
        "input_length": doc_fields["input_length"],
        "output_length": output_length,
        "safety_flag": doc_fields["safety_flag"],

        # model output
        "chatbot_output": reply,
        "model_response": reply,

        # flags + metadata
        "crisis_flag": crisis_flag,
        "analysis_metrics": metrics,
        "created_at": datetime.utcnow(),
    }

    # Async DB save
    async def _save(row):
        try:
            await chat_history_col.insert_one(row)
        except Exception as e:
            print("[DB ERROR] Failed to save chat:", e)

    background_tasks.add_task(_save, db_row)

    return {"bot_response": reply, "crisis": crisis_flag}


# ---------------------------------------------------
# History Endpoint
# ---------------------------------------------------
@app.get("/api/history")
async def get_history(user_id: Optional[str] = Query(None), limit: int = 50):
    query = {}
    if user_id:
        obj = oid(user_id)
        if obj:
            query = {"user_id": obj}
        else:
            doc = await users_col.find_one({"username": user_id})
            if doc:
                query = {"user_id": doc["_id"]}
            else:
                return []

    cursor = chat_history_col.find(query).sort("created_at", -1).limit(limit)
    results = [to_str_id(d) async for d in cursor]
    return results


# ---------------------------------------------------
# Mood Endpoint
# ---------------------------------------------------
# ---------------------------------------------------
# Enhanced Mood Endpoint (Upgraded)
# ---------------------------------------------------
@app.get("/api/mood")
async def get_mood(user_id: Optional[str] = Query(None), limit: int = 200):
    match = {}

    # User resolution
    if user_id:
        obj = oid(user_id)
        if obj:
            match["user_id"] = obj
        else:
            doc = await users_col.find_one({"username": user_id})
            if doc:
                match["user_id"] = doc["_id"]
            else:
                return {
                    "count": 0,
                    "avg_sentiment": 0.0,
                    "avg_empathy": 0.0,
                    "emotion_counts": {},
                    "risk_count": 0,
                    "avg_risk_intensity": 0.0,
                    "trigger_counts": {},
                    "escalation_counts": {},
                    "avg_input_length": 0
                }

    pipeline = [
        {"$match": match},
        {"$sort": {"created_at": -1}},
        {"$limit": limit},
        {"$project": {
            "user_sentiment": 1,
            "emotion_labels": 1,
            "response_empathy_score": 1,
            "risky_term_count": 1,
            "risk_intensity_score": 1,
            "input_length": 1,
            "assessment_raw": 1
        }}
    ]

    cursor = chat_history_col.aggregate(pipeline)
    rows = [r async for r in cursor]

    if not rows:
        return {
            "count": 0,
            "avg_sentiment": 0.0,
            "avg_empathy": 0.0,
            "emotion_counts": {},
            "risk_count": 0,
            "avg_risk_intensity": 0.0,
            "trigger_counts": {},
            "escalation_counts": {},
            "avg_input_length": 0
        }

    # Aggregation buckets
    total_sentiment = 0.0
    total_empathy = 0.0
    total_risk_intensity = 0.0
    total_input_len = 0

    import collections
    emotion_counter = collections.Counter()
    trigger_counter = collections.Counter()
    escalation_counter = collections.Counter()

    risk_total = 0

    # Process each record
    for r in rows:
        total_sentiment += float(r.get("user_sentiment", 0.0))
        total_empathy += float(r.get("response_empathy_score", 0.0))
        risk_total += int(r.get("risky_term_count", 0))
        total_risk_intensity += float(r.get("risk_intensity_score", 0.0))
        total_input_len += int(r.get("input_length", 0))

        # emotion parsing
        labs = r.get("emotion_labels", "none")
        for part in str(labs).split(","):
            lab = (part.split("(")[0] if "(" in part else part).strip()
            if lab:
                emotion_counter[lab] += 1

        # trigger
        trigger = r.get("assessment_raw", {}).get("trigger_word", "none")
        if trigger:
            trigger_counter[trigger] += 1

        # escalation
        esc = r.get("assessment_raw", {}).get("escalation", "none")
        escalation_counter[esc] += 1

    n = len(rows)

    return {
        "count": n,
        "avg_sentiment": round(total_sentiment / n, 4),
        "avg_empathy": round(total_empathy / n, 4),
        "emotion_counts": dict(emotion_counter),
        "risk_count": risk_total,
        "avg_risk_intensity": round(total_risk_intensity / n, 4),
        "trigger_counts": dict(trigger_counter),
        "escalation_counts": dict(escalation_counter),
        "avg_input_length": round(total_input_len / n, 2),
    }


# ---------------------------------------------------
# Response Analysis Endpoint
# ---------------------------------------------------
@app.get("/api/response-analysis")
async def get_response_analysis(user_id: Optional[str] = Query(None), limit: int = 200):
    query = {}

    if user_id:
        obj = oid(user_id)
        if obj:
            query = {"user_id": obj}
        else:
            doc = await users_col.find_one({"username": user_id})
            if doc:
                query = {"user_id": doc["_id"]}

    cursor = chat_history_col.find(query).sort("created_at", -1).limit(limit)

    total_overlap = 0.0
    total_len_ratio = 0.0
    count = 0
    short = []

    async for d in cursor:
        m = d.get("analysis_metrics", {})
        total_overlap += float(m.get("word_overlap", 0.0))
        total_len_ratio += float(m.get("length_ratio", 0.0))
        count += 1

        bot = d.get("model_response", "")
        if len(str(bot).split()) < 3:
            short.append({"id": str(d["_id"]), "response": bot})

    if count == 0:
        return {"count": 0, "avg_word_overlap": 0.0,
                "avg_length_ratio": 0.0, "short_responses": []}

    return {
        "count": count,
        "avg_word_overlap": round(total_overlap / count, 4),
        "avg_length_ratio": round(total_len_ratio / count, 4),
        "short_responses": short,
    }
