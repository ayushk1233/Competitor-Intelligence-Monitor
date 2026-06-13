import json
from datetime import datetime
from pathlib import Path

from backend.eval.snapshot import EvaluationSnapshot

EVAL_RUNS_DIR = Path("evaluation_runs")

EVAL_RUNS_DIR.mkdir(exist_ok=True)


def save_evaluation_snapshot(
    snapshot: EvaluationSnapshot
):

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"evaluation_{timestamp}.json"
    )

    filepath = EVAL_RUNS_DIR / filename

    with open(filepath, "w") as f:

        json.dump(
            snapshot.model_dump(),
            f,
            indent=2
        )

    return filepath
