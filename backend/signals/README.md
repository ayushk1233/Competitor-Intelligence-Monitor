# Strategic Signal Extraction Layer

## Purpose
This bounded context represents the intelligence persistence layer of the CIM.
The `TemporalEngine` outputs reasoning (`TemporalAnalysis`).
The `StrategicSignalExtractor` turns that reasoning into deterministic, reusable intelligence artifacts (`StrategicSignal`).

## Architecture
Memory -> Temporal -> **Signals** -> Strategic -> Prediction

Signals are deliberately separated from Temporal reasoning. Temporal reasoning is ephemeral and prompt-dependent. Signals are the canonical "facts" that CIM remembers.

## Determinism
Signal generation is deterministic:
- `signal_id` is a UUIDv5 generated from the company, category, direction, latest run id, and summary. It uniquely identifies an observation.
- `signal_fingerprint` is a SHA-256 hash of the company, normalized category, normalized direction, and business impact. It uniquely identifies the semantic intent, allowing us to track the same fundamental strategic change across multiple observations over time.
