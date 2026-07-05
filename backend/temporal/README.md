# Temporal Intelligence Engine

## Purpose
The Temporal Intelligence Engine is Phase 2 of the Competitor Intelligence Monitor. Its responsibility is to reason about history—specifically, interpreting changes across chronological timeline events for a given company. It detects trends in messaging, pricing, product, and more by comparing past intelligence snapshots with the current state.

## Architecture
This subsystem is completely decoupled from both the initial `AnalysisService` and the `Memory` storage/retrieval subsystems. 

The domain vocabulary is defined here using strictly typed Pydantic models and Enums (`backend/temporal/models.py`). 

## Dependency Graph Rule
**CRITICAL RULE:** 
1. `Temporal` must **never** import `AnalysisService`.
2. `Temporal` consumes only `CompanyTimeline` objects produced by `MemoryService`.

The architectural flow is strictly:
`Memory` (stores history) -> `Temporal` (reasons about history) -> `Strategic` -> `Prediction`.

Nothing in Phase 2 should invent its own data structures; everything must consume and return the domain models defined in `models.py`.
