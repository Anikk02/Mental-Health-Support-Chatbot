"""
Optional background tasks module. Placeholder for sending notifications, heavy enrichment, or logging.
"""

from .db import get_db

async def enqueue_heavy_enrichment(db, chat_id):
    # placeholder: run heavy tasks like running an external classifier, analytics
    pass
