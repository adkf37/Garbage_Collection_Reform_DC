# Project IRONCURB - Status

## Current Phase: Closeout

**Current Objective:** Validation phase complete. All 40 tests pass after fixing missing
`pyarrow` dependency. `requirements.txt` created. Project is complete and ready for
stakeholder delivery.

**Squad Template:** data_pipeline

**Squad Status:** Active -- Validation phase complete; all acceptance criteria confirmed.

---

## Phase History

| Phase | Date | Outcome |
|-------|------|---------|
| Planner | 2026-04-03 | `backlog/plan.md` and task files created |
| Squad Init | 2026-04-03 | Squad CLI initialized; team assembled with 6 agents |
| Squad Review | 2026-04-03 | All task files detailed; `backlog/README.md`, `data_sources.md`, `phases.md`, `.squad/sprint.md` created |
| Coder | 2026-04-03 | All 6 tasks implemented. Pipeline, models, app, and report complete. **Done** |
| Tester | 2026-04-03 | 40/40 tests pass. Performance benchmarks met (<42s placement, <1ms lookup). **Done** |
| Reviewer | 2026-04-05 | All 9 success criteria verified against live outputs. `backlog/README.md` checkboxes marked complete. **Done** |
| Validate | 2026-04-21 | 40/40 tests pass after adding `pyarrow` to deps. `requirements.txt` created. **Done** |

---

## Task Checklist

| Task | File | Status | Owner |
|------|------|--------|-------|
| 01 -- Barcelona Research | `research/barcelona_shared_waste.md` | **Done** | Scribe |
| 02 -- DC Spatial Baseline | `src/fetch_dc_data.py`, `data/raw/` | **Done** | Data Engineer |
| 03 -- Container Placement | `analysis/container_placement.py` | **Done** | Geo Developer |
| 04 -- Capacity Model | `analysis/capacity_model.py` | **Done** | Data Engineer |
| 05 -- Cost & Parking Model | `analysis/cost_model.py` | **Done** | Data Engineer |
| 06 -- App & Report | `app/app.py`, `report/ironcurb.qmd` | **Done** | Geo Developer |

---

## Execution Order

Tasks 01 and 02 are independent and can start immediately.
Task 03 depends on Task 02. Tasks 04 and 05 depend on Task 03.
Task 06 depends on Tasks 03, 04, and 05.

See `.squad/sprint.md` for the full execution plan.

---

## Blocking Issues

None — all 40 tests pass. See `.squad/decisions.md` for validation evidence.

---

## Key Constraints (always active)

- All spatial data must use **EPSG:2248** (NAD83 / Maryland State Plane, US feet)
- Walk distance scenarios: **250 / 500 / 750 ft**
- Capacity must match current system + **+25% population growth**
- All model assumptions must be explicit and parameterized (no hard-coded constants)
- Data fetch must be fully scripted -- no manual downloads

---

## Squad Team

See `.squad/team.md` for the full roster and `.squad/routing.md` for routing rules.
