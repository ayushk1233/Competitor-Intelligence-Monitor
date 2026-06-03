import json
from pathlib import Path


BASELINE_FILE = Path(
    "evaluation_baselines/eval_baseline_v1.json"
)


def load_baseline_score() -> float:
    with open(BASELINE_FILE, "r") as f:
        baseline = json.load(f)

    return baseline["overall_score"]


def calculate_regression(
    latest_score: float,
    baseline_score: float,
) -> dict:

    delta = latest_score - baseline_score

    return {
        "latest_score": latest_score,
        "baseline_score": baseline_score,
        "delta": round(delta, 3),
        "improved": delta > 0,
        "regressed": delta < 0,
    }