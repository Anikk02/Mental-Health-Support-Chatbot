def rank(chunks):
    # Simple heuristic ranking
    return sorted(chunks, key=lambda x: len(x), reverse=True)
