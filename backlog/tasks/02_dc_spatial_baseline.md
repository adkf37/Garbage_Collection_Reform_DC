# Task 02 — DC Spatial Baseline Construction

## Goal
Create a clean, reproducible spatial baseline of DC streets, blocks, and addresses.

## Outputs
- data/raw/dc_streets.*
- data/raw/dc_blocks.*
- data/raw/dc_addresses.*

## Scope
- Fetch authoritative DC GIS sources
- Standardize CRS
- Ensure geometries are valid
- Prepare blocks suitable for distance calculations

## Constraints
- Scripted fetch only (no manual downloads)
- One documented CRS used everywhere

## Acceptance Criteria
- All layers load cleanly in GeoPandas
- Script can be rerun without modification
- README notes data provenance
