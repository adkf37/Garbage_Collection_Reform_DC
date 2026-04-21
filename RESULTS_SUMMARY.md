# Project IRONCURB — Results Summary

**Status:** Complete  
**Date:** 2026-04-21  
**Codename:** IRONCURB

---

## What Was Built

This project evaluated the feasibility of transitioning Washington, DC from a
property-assigned curbside trash can system to a Barcelona-style shared container
system. All analysis, models, and deliverables are complete.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Containers placed city-wide | 18,247 |
| Blocks analyzed | 11,606 |
| Walk distance compliance (250 ft) | 100% of wards |
| Walk distance compliance (500 ft) | 100% of wards |
| Walk distance compliance (750 ft) | 100% of wards |
| Capital cost (citywide) | ~$106.8 M |
| Capital cost (per household) | ~$333.89 |
| Capacity growth scenario modeled | +25% population |

All 8 DC wards show full compliance at all three walking distance thresholds (250, 500,
and 750 ft). The system can absorb a 25% population growth without additional containers
by increasing collection frequency.

---

## Deliverables

| Output | Path | Description |
|--------|------|-------------|
| Container placements | `data/processed/container_locations.parquet` | 18,247 containers placed via k-means per block |
| Placement summary | `data/processed/placement_summary.json` | Walk-distance compliance by ward and threshold |
| Capacity analysis | `data/processed/capacity_analysis.json` | Capacity model with growth scenario |
| Cost analysis | `data/processed/cost_analysis.json` | Capital + operating costs, parking impact |
| Interactive app | `app/app.py` | Streamlit address-lookup map |
| Technical report | `report/ironcurb.qmd` | Quarto report referencing all processed outputs |
| Barcelona research | `research/barcelona_shared_waste.md` | Evidence base from 12 sources |

---

## How to Reproduce

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the full data pipeline

```bash
python src/fetch_dc_data.py
python analysis/container_placement.py
python analysis/capacity_model.py
python analysis/cost_model.py
```

> **Note:** `fetch_dc_data.py` calls the DC Open Data APIs and requires internet access.
> Cached `data/raw/` parquet files are committed to the repository as a fallback for
> offline use.

### 3. Launch the interactive app

```bash
streamlit run app/app.py
```

Open the app in a browser and enter any DC address to see the nearest shared container.

### 4. Render the report (optional)

Requires [Quarto CLI](https://quarto.org/docs/get-started/) to be installed.

```bash
quarto render report/ironcurb.qmd
```

---

## Run Tests

```bash
pytest tests/test_data_outputs.py -v
```

All 40 tests pass. Test coverage spans research, spatial baseline, container placement,
capacity model, cost model, app structure, and performance benchmarks.

---

## Architecture Notes

- **CRS:** All spatial data uses **EPSG:2248** (NAD83 / Maryland State Plane, US feet)
  so that distance thresholds (250/500/750 ft) can be applied directly.
- **Container placement:** k-means clustering (k=2–3 per block, `random_state=42`) for
  deterministic, reproducible results.
- **Model assumptions:** All assumptions are declared in `@dataclass` objects with cited
  sources — no buried literals.
- **Performance:** City-wide placement runs in ~42s; address lookup is <1ms via
  `scipy.spatial.cKDTree`.

---

## Remaining Follow-Up Items (not blocking delivery)

- No deployment target is configured for the Streamlit app. The app runs locally only.
- Quarto report rendering has not been tested in CI — it requires Quarto CLI to be
  installed separately.
- DC Open Data API endpoints may change over time; `src/fetch_dc_data.py` may need
  updating if the API changes.

---

## Phase History

| Phase | Date | Outcome |
|-------|------|---------|
| Planner | 2026-04-03 | `backlog/plan.md` and task files created |
| Squad Init | 2026-04-03 | Team of 6 assembled |
| Squad Review | 2026-04-03 | All task files detailed; sprint plan created |
| Coder | 2026-04-03 | All 6 tasks implemented |
| Tester | 2026-04-03 | 40/40 tests pass; performance benchmarks met |
| Reviewer | 2026-04-05 | All 9 success criteria verified |
| Validate | 2026-04-21 | `pyarrow` dep fixed; `requirements.txt` created |
| Closeout | 2026-04-21 | Handoff docs updated; project marked Complete |
