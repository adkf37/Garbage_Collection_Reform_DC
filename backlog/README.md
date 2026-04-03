# Project IRONCURB - Backlog

## Project Goal

Evaluate the feasibility of transitioning Washington, DC from a property-assigned
curbside trash can system to a Barcelona-style shared container system.

## Hypothesis

A shared container model can reduce labor and operating costs, improve cleanliness
and recycling outcomes, and scale better with population growth -- while keeping
resident walking distances within acceptable bounds.

## Success Criteria

- [ ] Container placement algorithm produces a deterministic city-wide placement
- [ ] Walking distance compliance reported for 250 / 500 / 750 ft thresholds by ward
- [ ] Capacity model demonstrates parity with current system under a +25% growth scenario
- [ ] Cost model produces per-household and citywide figures (capital + operating)
- [ ] Parking/curb impact quantified
- [ ] Interactive Streamlit app with address lookup runs locally
- [ ] Quarto report renders end-to-end from `data/processed/` files
- [ ] All model assumptions are explicit, parameterized, and source-cited
- [ ] Full pipeline is reproducible via `python src/fetch_dc_data.py &&
      python analysis/container_placement.py &&
      python analysis/capacity_model.py &&
      python analysis/cost_model.py`

## Key Constraints

- All spatial data uses **EPSG:2248** (NAD83 / Maryland State Plane, US feet)
- Walking distance scenarios: **250 / 500 / 750 ft**
- Capacity must cover current system + **+25% population growth**
- All assumption values must be in `@dataclass` objects -- no buried literals
- Data fetching must be fully scripted (no manual downloads)

## Backlog Files

| File | Description |
|------|-------------|
| `plan.md` | Overall execution plan and hypothesis |
| `README.md` | This file -- goals and success criteria |
| `data_sources.md` | Data source inventory and API documentation |
| `phases.md` | Phase-by-phase breakdown |
| `tasks/01_research_barcelona.md` | Barcelona research synthesis |
| `tasks/02_dc_spatial_baseline.md` | DC GIS data pipeline |
| `tasks/03_container_placement.md` | Container placement algorithm |
| `tasks/04_capacity_model.md` | Waste capacity analysis |
| `tasks/05_cost_and_parking.md` | Cost and parking impact model |
| `tasks/06_app_and_report.md` | Streamlit app and Quarto report |
