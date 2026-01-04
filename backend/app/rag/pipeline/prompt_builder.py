def build_prompt(identity_block, context, memory_summary, user_input):
    return f"""
{identity_block}

Relevant past context:
{context}

User patterns:
{memory_summary}

User says:
{user_input}

Respond empathetically.
"""
