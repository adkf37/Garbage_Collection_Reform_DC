# Project IRONCURB — Execution Plan

## Objective
Evaluate the feasibility, cost, and spatial impacts of transitioning DC from curbside,
property-assigned trash/recycling bins to a shared, block-level container system.

## Hypothesis
A shared container model can:
- reduce labor and operating costs
- improve cleanliness and recycling outcomes
- scale better with population growth
while keeping resident walk distances within acceptable bounds.

## Key Constraints
- Maximum walk distance scenarios: 250 / 500 / 750 ft
- Capacity must match current service and +25% population growth
- Must account for DC street geometry, alleys, and tree cover

## Outputs
- Reproducible analysis
- Interactive map with address lookup
- Cost, capacity, and parking impact estimates
- Markdown / Quarto write-up

## Success Criteria
- All assumptions explicit and parameterized
- End-to-end reproducibility via Makefile
- Address → nearest bin lookup works
- Clear comparison: current vs shared system
