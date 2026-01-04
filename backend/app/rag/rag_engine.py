from rag.pipeline.rag_stage1_context import build_context
from rag.pipeline.rag_stage2_identity import load_identity, inject_identity
from rag.pipeline.prompt_builder import build_prompt
from rag.memory.memory_engine import update_user_memory
from rag.memory.summarizer import summarize
from rag.retrieval.retriever import retrieve
from rag.retrieval.ranker import rank
from rag.embeddings.vector_store import VectorStore
from rag.utils.intent import is_identity_question   # 👈 ADD THIS

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
USERS_MEM = BASE / "data/users/users_memory.json"
IDENTITY = BASE / "data/identity/lamira_identity.json"

vector_store = VectorStore()


def load_users():
    if USERS_MEM.exists():
        return json.loads(USERS_MEM.read_text())
    return {"users": {}}


def save_users(data):
    USERS_MEM.write_text(json.dumps(data, indent=2))


def run_rag(
    user_id: str,
    user_input: str,
    analysis: dict
) -> str:
    """
    This is the ONLY function your chatbot needs to call.
    """

    # ================== IDENTITY SHORT-CIRCUIT ==================
    if is_identity_question(user_input):
        identity = load_identity(IDENTITY)

        name = identity.get("name", "Lamira")
        role = identity.get("role", "")

        return f"My name is {name}. {role}"

    # ================== NORMAL RAG FLOW ==================

    users = load_users()
    memory = users["users"].setdefault(user_id, {})

    # ---- Update memory ----
    memory = update_user_memory(memory, analysis)
    users["users"][user_id] = memory
    save_users(users)

    # ---- Retrieval ----
    retrieved = retrieve(user_input, vector_store)
    ranked = rank(retrieved)
    context = build_context(ranked)

    # ---- Identity ----
    identity = load_identity(IDENTITY)
    identity_block = inject_identity(identity)

    # ---- Memory summary ----
    memory_summary = summarize(memory)

    # ---- Final prompt ----
    return build_prompt(
        identity_block=identity_block,
        context=context,
        memory_summary=memory_summary,
        user_input=user_input
    )
