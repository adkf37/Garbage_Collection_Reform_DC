# Task 03 - Shared Container Placement Algorithm

## Goal
Generate candidate shared container locations that satisfy walking-distance
constraints for all three threshold scenarios (250 / 500 / 750 ft).

## Owner
Geo Developer (supporting: Data Engineer)

## Dependencies
- **Task 02 must be complete** -- requires `data/raw/dc_addresses.parquet`
  with `BLOCKKEY` and `WARD` columns in EPSG:2248

## Inputs
- `data/raw/dc_addresses.parquet` (from Task 02)

## Outputs
- `analysis/container_placement.py`   -- placement algorithm script
- `data/processed/container_locations.parquet` -- one row per container, with
  columns: `block_id`, `container_id`, `addresses_served`, `ward`, geometry (Point)
- `data/processed/block_stats.parquet` -- one row per block, with distance stats
  and per-threshold violation flags
- `data/processed/placement_summary.json` -- aggregate stats by ward and threshold

## Algorithm Design
1. Group address points by `BLOCKKEY`
2. Skip blocks with fewer than `MIN_ADDRESSES_FOR_CONTAINERS` (default: 5) addresses
3. For each eligible block, run **k-means clustering** (k=2 for <20 addresses,
   k=3 for >=20 addresses) with `random_state=42` for determinism
4. Use cluster centroids as container locations
5. Calculate Euclidean distance from each address to its nearest container
6. Record per-block: max distance, mean distance, violation counts per threshold

## Key Parameters (all configurable at top of script)
| Parameter | Default | Notes |
|-----------|---------|-------|
| `DISTANCE_THRESHOLDS_FT` | [250, 500, 750] | Thresholds to evaluate |
| `MIN_CONTAINERS_PER_BLOCK` | 2 | Minimum containers per block |
| `MAX_CONTAINERS_PER_BLOCK` | 3 | Maximum containers per block |
| `MIN_ADDRESSES_FOR_CONTAINERS` | 5 | Skip blocks below this |

## Constraints
- Output must be **deterministic** (same input always produces same output)
- No hard-coded DC-specific constants -- all thresholds are parameters
- CRS of output containers must be EPSG:2248 (inherited from addresses)
- Script must complete in <60 seconds on a modern laptop

## Acceptance Criteria
- [x] `data/processed/container_locations.parquet` exists and loads cleanly
- [x] `data/processed/placement_summary.json` exists with `overall`, `by_threshold`,
      and `by_ward` keys
- [x] Summary reports compliance rate for each of the three thresholds
- [x] Violating blocks (at 500 ft default) are identifiable from `block_stats.parquet`
- [x] Container CRS is EPSG:2248
- [x] Script runs in <60 seconds end-to-end (groupby optimisation verified by test)
- [x] Re-running the script produces identical output (determinism via `random_state=42`)
- [x] Ward-level breakdown present in summary JSON
