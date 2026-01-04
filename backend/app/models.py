"""
Pydantic models for API schemas (auth, chat, analytics).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# -----------------------------
# Authentication Schemas
# -----------------------------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)
    email: EmailStr


class UserOut(BaseModel):
    id: Optional[str]
    username: str
    email: EmailStr
    is_email_verified: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


# -----------------------------
# 2FA Schemas
# -----------------------------

class TwoFASetupResponse(BaseModel):
    otp_auth_url: str
    secret: str


class TwoFAVerifyRequest(BaseModel):
    username: str
    otp_code: str
    otp_code_secret: Optional[str]=None


class TwoFAToggleRequest(BaseModel):
    enable: bool


# -----------------------------
# Chat / Dataset Schemas
# -----------------------------

class ChatRequest(BaseModel):
    """
    Updated schema matching the production backend:
    - Accepts both camelCase (userId) and snake_case (user_id)
    - Optional dataset fields because backend fills missing values
    """

    user_id: Optional[str] = None
    userId: Optional[str] = None     # NEW → support frontend camelCase

    user_input: str = Field(..., min_length=1)

    # Optional dataset enrichment fields
    emotion_labels: Optional[str] = None
    user_sentiment: Optional[float] = None
    trigger_word: Optional[str] = None
    response_empathy_score: Optional[float] = None
    risky_term_count: Optional[int] = None
    risk_intensity_score: Optional[float] = None
    input_length: Optional[int] = None
    output_length: Optional[int] = None
    safety_flag: Optional[int] = None

    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    bot_response: str
    crisis: bool = False
    saved_id: Optional[str] = None


# -----------------------------
# History Schemas
# -----------------------------

class HistoryItem(BaseModel):
    id: str
    user_id: Optional[str]
    user_input: str

    chatbot_output: Optional[str] = None   # NEW (dataset field)
    model_response: Optional[str] = None   # for backward compatibility

    emotion_labels: Optional[str] = None
    user_sentiment: Optional[float] = None
    response_empathy_score: Optional[float] = None
    risky_term_count: Optional[int] = None
    risk_intensity_score: Optional[float] = None
    safety_flag: Optional[int] = None

    analysis_metrics: Optional[Dict[str, Any]] = None
    crisis_flag: bool
    created_at: datetime


# -----------------------------
# Mood & Analysis Schemas
# -----------------------------

class MoodStats(BaseModel):
    count: int
    avg_sentiment: float
    avg_empathy: float
    emotion_counts: Dict[str, int]
    risk_count: int


class ResponseAnalysis(BaseModel):
    count: int
    avg_word_overlap: float
    avg_length_ratio: float
    short_responses: List[Dict[str, Any]]
