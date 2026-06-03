import json
from pathlib import Path

EVAL_RUNS_DIR = Path("evaluation_runs")


def load_all_evaluations():
    evaluations = []

    for file in sorted(
        EVAL_RUNS_DIR.glob("evaluation_*.json")
    ):
        with open(file, "r") as f:
            evaluations.append(json.load(f))

    return evaluations