def compare_scores(
    old_score: float,
    new_score: float
):
    delta = round(
        new_score - old_score,
        3
    )

    return {
        "old_score": old_score,
        "new_score": new_score,
        "delta": delta,
        "improved": delta > 0,
        "regressed": delta < 0,
    }