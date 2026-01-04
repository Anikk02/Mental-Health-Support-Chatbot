from rag.memory.belief_updater import update_beliefs
from rag.memory.decay import decay_memories
from rag.utils.time_utils import now_iso

def update_user_memory(user_memory, analysis):
    user_memory.setdefault("long_term_memory", [])
    user_memory.setdefault("beliefs", {})

    # ---- SAFE GETS ----
    extracted_beliefs = analysis.get("extracted_beliefs", [])
    emotion = analysis.get("emotion", "neutral")
    risk_score = analysis.get(
        "risk_score",
        analysis.get("risk_intensity", 0.0)
    )

    if extracted_beliefs:
        user_memory = update_beliefs(
            user_memory, extracted_beliefs
        )

    user_memory["long_term_memory"].append({
        "emotion": emotion,
        "risk_score": risk_score,
        "last_seen": now_iso()
    })

    return decay_memories(user_memory)
