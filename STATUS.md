# Project IRONCURB — Status

## Current Phase: Coder

**Current Objective:** Implement the six backlog tasks — data pipeline, container placement, capacity/cost models, and interactive app.

**Squad Template:** data_pipeline

**Squad Status:** ✅ Initialized — team is active and routing is configured.

---

## Phase History

| Phase | Date | Outcome |
|-------|------|---------|
| Planner | 2026-04-03 | `backlog/plan.md` and task files created |
| Squad Init | 2026-04-03 | Squad CLI initialized; team assembled with 6 agents |
| Coder | 2026-04-03 | **← Current** |

---

## Task Checklist

| Task | File | Status | Owner |
|------|------|--------|-------|
| 01 — Barcelona Research | `research/barcelona_shared_waste.md` | ⬜ Pending | Scribe |
| 02 — DC Spatial Baseline | `src/fetch_dc_data.py`, `data/raw/` | ⬜ Pending | Data Engineer |
| 03 — Container Placement | `analysis/container_placement.py` | ⬜ Pending | Geo Developer |
| 04 — Capacity Model | `analysis/capacity_model.py` | ⬜ Pending | Data Engineer |
| 05 — Cost & Parking Model | `analysis/cost_model.py` | ⬜ Pending | Data Engineer |
| 06 — App & Report | `app/app.py`, `report/ironcurb.qmd` | ⬜ Pending | Geo Developer |

---

## Blocking Issues

None.

---

## Key Constraints (always active)

- All spatial data must use **EPSG:2248** (NAD83 / Maryland State Plane, US feet)
- Walk distance scenarios: **250 / 500 / 750 ft**
- Capacity must match current system + **+25% population growth**
- All model assumptions must be explicit and parameterized (no hard-coded constants)
- Data fetch must be fully scripted — no manual downloads

---

## Squad Team

See `.squad/team.md` for the full roster and `.squad/routing.md` for routing rules.
