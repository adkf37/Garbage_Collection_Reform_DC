# Sprint Plan - Project IRONCURB

**Sprint Goal**: Implement the full data pipeline, analysis models, interactive app,
and written report for Project IRONCURB.

**Created**: 2026-04-03
**Phase**: Coder

---

## Definition of Done

A task is DONE when:
1. All outputs listed in the task file exist at the specified paths
2. All acceptance criteria checkboxes in the task file are checked off
3. The relevant analysis script (if any) runs without errors end-to-end
4. Lead has reviewed the output and approved

The sprint is DONE when all 6 tasks are DONE and the full pipeline runs
reproducibly from a fresh checkout.

---

## Execution Order

```
Task 01 (research)  [independent, starts immediately]
Task 02 (spatial)   [independent, starts immediately]
   └→ Task 03 (placement)
         ├→ Task 04 (capacity)
         ├→ Task 05 (cost)
         └→ Task 06 (app+report) [waits for 03+04+05]
```

Tasks 01 and 02 are fully independent and can run in parallel.

---

## Task List (Ordered)

### Wave 1 - Independent (can run in parallel)

| # | Task | File | Agent | Status | Blocked? |
|---|------|------|-------|--------|----------|
| 01 | Barcelona Research | `tasks/01_research_barcelona.md` | Scribe | Pending | No |
| 02 | DC Spatial Baseline | `tasks/02_dc_spatial_baseline.md` | Data Engineer | Pending | No |

**Wave 1 outputs needed before Wave 2:**
- `research/barcelona_shared_waste.md` (from 01)
- `data/raw/dc_addresses.parquet` (from 02)

---

### Wave 2 - Depends on Task 02

| # | Task | File | Agent | Status | Blocked? |
|---|------|------|-------|--------|----------|
| 03 | Container Placement | `tasks/03_container_placement.md` | Geo Developer | Pending | Needs Task 02 |

**Wave 2 outputs needed before Wave 3:**
- `data/processed/container_locations.parquet`
- `data/processed/placement_summary.json`

---

### Wave 3 - Depends on Task 03 (can run in parallel with each other)

| # | Task | File | Agent | Status | Blocked? |
|---|------|------|-------|--------|----------|
| 04 | Capacity Model | `tasks/04_capacity_model.md` | Data Engineer | Pending | Needs Task 03 |
| 05 | Cost & Parking | `tasks/05_cost_and_parking.md` | Data Engineer | Pending | Needs Task 03 |

**Wave 3 outputs needed before Wave 4:**
- `data/processed/capacity_analysis.json`
- `data/processed/cost_analysis.json`

---

### Wave 4 - Depends on Tasks 03 + 04 + 05

| # | Task | File | Agent | Status | Blocked? |
|---|------|------|-------|--------|----------|
| 06 | App & Report | `tasks/06_app_and_report.md` | Geo Developer | Pending | Needs 03+04+05 |

---

## Agent Assignments Summary

| Agent | Tasks | Notes |
|-------|-------|-------|
| Scribe | 01 (Barcelona Research) | Also contributes to report sections in Task 06 |
| Data Engineer | 02 (Spatial Baseline), 04 (Capacity), 05 (Cost) | Core pipeline work |
| Geo Developer | 03 (Placement), 06 (App + Report) | Spatial algorithms + visualization |
| Tester | Validates all tasks after completion | Reviews acceptance criteria |
| Lead | Architecture reviews, approvals | Unblocks decisions |
| Ralph | Memory, cross-task context | Surfaces prior decisions on request |

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| DC Open Data API rate limiting or downtime | Medium | Retry logic in `fetch_dc_data.py`; parquet files already exist in repo as fallback |
| `BLOCKKEY` column missing from address data | Low | Task 02 acceptance criteria check for this column |
| Capacity model needs container count before Task 03 runs | Low | Fallback estimate of 18,000 containers in `capacity_model.py` |
| Quarto not installed for report rendering | Medium | Document install instructions in report README |

---

## Completion Checklist

- [x] Task 01 - Barcelona Research DONE
- [x] Task 02 - DC Spatial Baseline DONE
- [x] Task 03 - Container Placement DONE
- [x] Task 04 - Capacity Model DONE
- [x] Task 05 - Cost & Parking Model DONE
- [x] Task 06 - App & Report DONE
- [x] Full pipeline runs end-to-end on clean machine
- [x] All acceptance criteria across all tasks verified by Tester
- [x] STATUS.md updated to reflect completion
