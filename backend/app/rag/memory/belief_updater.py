def update_beliefs(memory, new_beliefs):
    beliefs = memory.setdefault("beliefs", {})

    for belief in new_beliefs:
        beliefs.setdefault(belief, {"count": 0})
        beliefs[belief]["count"] += 1

    return memory
