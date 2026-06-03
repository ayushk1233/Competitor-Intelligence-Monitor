import glob
import json
import sys

TOLERANCE = 0.03


def get_latest_run():
    runs = sorted(glob.glob("evaluation_runs/*.json"))

    if not runs:
        print("⚠️ No evaluation runs found")
        print("Skipping evaluation gate")
        return None

    return runs[-1]


def get_baseline():
    baseline_file = "evaluation_baselines/eval_baseline_v1.json"

    with open(baseline_file, "r") as f:
        return json.load(f)


def main():
    latest_run = get_latest_run()

    if latest_run is None:
        return

    baseline = get_baseline()

    with open(latest_run, "r") as f:
        latest = json.load(f)

    latest_score = latest["overall_score"]
    baseline_score = baseline["overall_score"]

    required_score = baseline_score - TOLERANCE

    print(f"Latest Run     : {latest_run}")
    print(f"Latest Score   : {latest_score:.3f}")
    print(f"Baseline Score : {baseline_score:.3f}")
    print(f"Tolerance      : {TOLERANCE:.3f}")
    print(f"Required Score : {required_score:.3f}")

    if latest_score < required_score:
        print("❌ EVAL GATE FAILED")
        sys.exit(1)

    print("✅ EVAL GATE PASSED")


if __name__ == "__main__":
    main()