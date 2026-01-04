"""
MongoDB connection and FastAPI dependency (Motor).
Provides shared client, db, and named collections.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from .config import (
    MONGO_URI,
    MONGO_DB,
    USERS_COLLECTION,
    CHAT_HISTORY_COLLECTION,
    MOOD_STATS_COLLECTION,
    RESPONSE_ANALYSIS_COLLECTION,
    AUTH_TEMP_COLLECTION,
    RATE_LIMIT_COLLECTION,
)

# Create one shared client for entire application
_client = AsyncIOMotorClient(MONGO_URI, maxPoolSize=20, minPoolSize=5)
_db = _client[MONGO_DB]

# Expose collections with correct names
users_col = _db[USERS_COLLECTION]
chat_history_col = _db[CHAT_HISTORY_COLLECTION]
mood_stats_col = _db[MOOD_STATS_COLLECTION]
response_analysis_col = _db[RESPONSE_ANALYSIS_COLLECTION]
auth_temp_col = _db[AUTH_TEMP_COLLECTION]
rate_limit_col = _db[RATE_LIMIT_COLLECTION]

async def get_db():
    """
    FastAPI dependency to inject database instance.
    Keeping this in case you need raw DB access.
    """
    return _db
