def summarize(memory):
    summaries = []
    for b, data in memory.get("beliefs", {}).items():
        if data["count"] > 1:
            summaries.append(b)
    return summaries
