from datetime import datetime, timedelta

def decay_memories(memory, days=30):
    now = datetime.utcnow()

    memory["long_term_memory"] = [
        m for m in memory.get("long_term_memory", [])
        if (now - datetime.fromisoformat(m["last_seen"])) < timedelta(days=days)
    ]
    return memory
