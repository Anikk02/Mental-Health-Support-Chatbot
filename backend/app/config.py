"""
Application configuration. Reads environment variables and provides safe defaults.
"""
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env only for local development
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    load_dotenv()

# ===============================
# Hugging Face Model Config
# ===============================
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_REPO = os.getenv(
    "MODEL_REPO",
    "anikk/trained-mentalchat-model"
)

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is missing from environment variables")

# Optional: Hugging Face cache directory
HF_HOME = os.getenv("HF_HOME", "/tmp/huggingface")

# ===============================
# Auxiliary Models
# ===============================
CLASSIFIER_MODEL = os.getenv(
    "CLASSIFIER_MODEL",
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# ===============================
# Frontend / CORS
# ===============================
FRONTEND_URL = os.getenv("FRONTEND_URL")
FRONTEND_BASE = os.getenv("FRONTEND_BASE")

# ===============================
# MongoDB
# ===============================
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://")
MONGO_DB = os.getenv("MONGO_DB", "mentalchat")

# Collections
USERS_COLLECTION = "users"
CHAT_HISTORY_COLLECTION = "chat_history"
MOOD_STATS_COLLECTION = "mood_stats"
RESPONSE_ANALYSIS_COLLECTION = "response_analysis"
AUTH_TEMP_COLLECTION = "auth_temp"
RATE_LIMIT_COLLECTION = "rate_limits"

# ===============================
# JWT / Auth
# ===============================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from environment variables")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

# ===============================
# 2FA Email / Verification
# ===============================
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # should be your verified email

# ===============================
# Device config (for ML model)
# ===============================
USE_CUDA = os.getenv("USE_CUDA", "auto")

# ===============================
# Debug / Temporary prints
# ===============================
print("DEBUG MONGO_URI:", MONGO_URI)
print("DEBUG MONGO_DB:", MONGO_DB)
print("DEBUG MODEL_REPO:", MODEL_REPO)
print("DEBUG FRONTEND_BASE:", FRONTEND_BASE)
print("DEBUG SMTP_HOST:", SMTP_HOST)
print("DEBUG SMTP_USER:", SMTP_USER)
print("DEBUG SMTP_PASS SET:", bool(SMTP_PASS))
