"""
Create TTL indexes for token and rate-limit collections (auth_temp, rate_limits).
Run once:
    python -m backend.app.indexes_setup
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from .config import (
    MONGO_URI,
    MONGO_DB,
    AUTH_TEMP_COLLECTION,
    RATE_LIMIT_COLLECTION
)

async def create_indexes():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]

    # TTL index for tokens stored in auth_temp
    await db[AUTH_TEMP_COLLECTION].create_index(
        "expireAt",
        expireAfterSeconds=0
    )

    # TTL index for rate limiting docs
    await db[RATE_LIMIT_COLLECTION].create_index(
        "expireAt",
        expireAfterSeconds=0
    )

    print("TTL indexes created successfully.")

if __name__ == "__main__":
    asyncio.run(create_indexes())
