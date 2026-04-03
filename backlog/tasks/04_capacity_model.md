# Task 04 - Trash Capacity & Collection Frequency Model

## Goal
Ensure the shared container system can match or exceed the current individual-can
system's waste collection capacity under baseline and +25% growth scenarios.

## Owner
Data Engineer (supporting: Lead)

## Dependencies
- **Task 03 must be complete** -- requires `data/processed/placement_summary.json`
  to obtain the actual container count. Falls back to an estimated 18,000 containers
  if the file is not available.

## Inputs
- `data/processed/placement_summary.json` (from Task 03) -- provides `total_containers`
- All other inputs are parameterized assumptions (no external data needed)

## Outputs
- `analysis/capacity_model.py`           -- capacity model script
- `data/processed/capacity_analysis.json` -- full results with all assumptions
- `data/processed/capacity_comparison.csv` -- human-readable comparison table

## Key Assumption Dataclasses
All parameters live in `@dataclass` classes at the top of the script:

| Class | Key Fields |
|-------|-----------|
| `CurrentSystemAssumptions` | trash_can_size_gal=96, pickups/week=2, utilization=75% |
| `SharedSystemAssumptions` | container_size_gal=400, streams=3, utilization=80% |
| `PopulationAssumptions` | households=320,000, growth_rate=0.25, waste_per_person=8 gal/wk |

## Analyses to Produce
1. **Current system capacity** -- weekly gallons available vs. demand
2. **Shared system capacity** at 2x, 3x, 5x, and 7x/week pickup frequencies
3. **Minimum frequency needed** to meet baseline demand
4. **Minimum frequency needed** with +25% population growth
5. **Comparison table** -- current vs shared at each frequency

## Constraints
- All assumption values must be in `@dataclass` instances -- no hard-coded literals
  elsewhere in the script
- Growth scenario must use `growth_rate` from `PopulationAssumptions`, not a literal
- Script must run standalone (with fallback container count if placement data absent)

## Acceptance Criteria
- [ ] `data/processed/capacity_analysis.json` exists and contains `assumptions`,
      `current_system_capacity`, `shared_system_by_frequency`, `stress_tests`,
      and `minimum_frequencies` keys
- [ ] `data/processed/capacity_comparison.csv` exists and is readable
- [ ] +25% growth scenario is explicitly reported
- [ ] At least one pickup frequency meets demand under the growth scenario
- [ ] All `@dataclass` fields have inline docstring comments explaining their source
- [ ] Script runs without errors with and without `placement_summary.json` present
- [ ] No literal numeric constants outside of the dataclass definitions
