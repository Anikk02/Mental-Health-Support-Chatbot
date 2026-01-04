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

def is_identity_question(text: str) -> bool:
    text = text.lower().strip()
    return any(q in text for q in IDENTITY_QUESTIONS)
