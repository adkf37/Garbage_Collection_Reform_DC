# Task 03 — Shared Container Placement Algorithm

## Goal
Generate candidate shared container locations that satisfy walking-distance constraints.

## Outputs
- analysis/container_placement.py
- data/processed/container_locations.parquet

## Scope
- Place 2–3 containers per block baseline
- Evaluate 250 / 500 / 750 ft distance thresholds
- Flag blocks violating constraints

## Constraints
- Deterministic output
- Parameterized distances
- No hard-coded DC-specific constants

## Acceptance Criteria
- Summary stats by ward/neighborhood
- Violating blocks clearly identified
- Script runs in <60s locally
