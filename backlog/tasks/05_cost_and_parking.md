# Task 05 - Cost & Parking Impact Model

## Goal
Estimate startup and operating costs of the shared container system and
quantify curb/parking space consumed, compared to the current system.

## Owner
Data Engineer (supporting: Lead)

## Dependencies
- **Task 03 must be complete** -- requires total container count from
  `data/processed/placement_summary.json`
- Task 04 useful but not blocking -- cost model uses its own assumptions

## Inputs
- `data/processed/placement_summary.json` (from Task 03) -- container count
- All cost parameters are dataclass assumptions (no external pricing data needed)

## Outputs
- `analysis/cost_model.py`           -- cost model script
- `data/processed/cost_analysis.json` -- full cost breakdown with all assumptions
- `data/processed/cost_comparison.csv` -- per-household and citywide comparison table

## Cost Components to Model

### Capital / Startup Costs
| Item | Assumption Class | Notes |
|------|-----------------|-------|
| Container purchase | `ContainerCostAssumptions` | $2,500/container |
| Container installation | `ContainerCostAssumptions` | $1,500/container |
| New automated trucks | `TruckCostAssumptions` | $350,000/truck |
| Old bin removal/disposal | `BinRemovalAssumptions` | cost per household |

### Operating Costs (annual)
| Item | Assumption Class | Notes |
|------|-----------------|-------|
| Labor (drivers + crew) | `LaborCostAssumptions` | crew size varies by system |
| Fuel | `TruckCostAssumptions` | per truck per year |
| Container maintenance | `ContainerCostAssumptions` | per container per year |
| Truck maintenance | `TruckCostAssumptions` | per truck per year |

### Parking / Curb Impact
- Square feet per container footprint
- Equivalent parking spaces consumed (1 space = 162 sq ft)
- Total curb frontage impact citywide

## Key Metrics to Report
- **Per-household** capital cost
- **Per-household** annual operating cost
- **Citywide** capital cost (total)
- **Citywide** annual operating cost
- **Net annual cost change** vs current system (savings or increase)
- **Parking spaces** consumed citywide
- **Payback period** if shared system is cheaper to operate

## Constraints
- Separate capital vs operating costs clearly
- All dollar figures must trace to a named `@dataclass` field
- Operating cost comparison must use same household count as capacity model
- Parking calculation must use `container_footprint_sqft` parameter, not a literal

## Acceptance Criteria
- [ ] `data/processed/cost_analysis.json` exists with `capital_costs`,
      `operating_costs`, `parking_impact`, and `comparison` keys
- [ ] `data/processed/cost_comparison.csv` includes per-household and citywide rows
- [ ] Current system costs included for comparison
- [ ] Net cost difference (savings or increase) explicitly calculated
- [ ] Parking spaces consumed reported as a concrete number
- [ ] All assumption values in `@dataclass` instances with source comments
- [ ] Script runs without errors with fallback container count
