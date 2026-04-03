# Squad Decisions

## Active Decisions

### 2026-04-03 — Task 01 Complete: Barcelona Research Summary

**Decision:** `research/barcelona_shared_waste.md` created synthesizing the primary source PDF plus 11 additional sources covering Barcelona, Amsterdam, Vienna, Seoul, and San Francisco.

**Rationale:** Task 01 was the only outstanding Coder-phase task. The research summary documents the system overview, key metrics, evidence quality, drawbacks, assumption values used in Tasks 04 and 05, DC transferability, and knowledge gaps. All assumption values in the "Assumptions Derived" table in the research summary are traceable to named sources.

**Key assumptions confirmed:**
- Shared container size: 400 gal (surface model)
- Walking distance target: ≤500 ft baseline (250/500/750 ft thresholds)
- Underground containers can achieve ~36% operating-cost savings vs. door-to-door (ACR+ study)
- Smart containers cost ~€1,400 vs. ~€1,000 standard

**Applies to:** `research/barcelona_shared_waste.md`, Tasks 04 and 05 assumption dataclasses.

---

### 2026-04-03 — CRS: EPSG:2248

**Decision:** All spatial data uses EPSG:2248 (NAD83 / Maryland State Plane, US feet).

**Rationale:** Distance thresholds (250/500/750 ft) are in feet. EPSG:2248 native unit is feet, enabling direct distance calculations without unit conversion. Deviating from this CRS would break distance-based acceptance criteria.

**Applies to:** All GeoPandas operations, parquet outputs, distance calculations.

---

### 2026-04-03 — Data Sources: DC Open Data APIs

**Decision:** All DC spatial data (addresses, blocks, streets) is fetched programmatically from DC Open Data APIs via `src/fetch_dc_data.py`. No manual downloads allowed.

**Rationale:** Reproducibility requirement. The pipeline must be fully scripted.

**Applies to:** `data/raw/` directory, fetch scripts.

---

### 2026-04-03 — Container Placement: k-means per block

**Decision:** Use k-means clustering (k=2–3) within each block to determine container placement locations.

**Rationale:** Produces deterministic, parameterized placements. Consistent with backlog Task 03 acceptance criteria requiring deterministic output.

**Applies to:** `analysis/container_placement.py`

---

### 2026-04-03 — Walk Distance Scenarios: 250 / 500 / 750 ft

**Decision:** Evaluate three walking distance thresholds: 250 ft, 500 ft, and 750 ft.

**Rationale:** Defined in `backlog/plan.md` and used consistently across placement, capacity, and app.

**Applies to:** All analysis scripts, app UI, report.

---

### 2026-04-03 — Squad Team Initialized

**Decision:** Squad team initialized with: Lead, Data Engineer, Geo Developer, Tester, Scribe, Ralph.

**Rationale:** Project type is `data_pipeline` with geospatial components. Data Engineer handles pipeline + modeling. Geo Developer handles spatial analysis + app. Tester validates acceptance criteria from backlog.

**Applies to:** `.squad/team.md`, `.squad/routing.md`

## Governance

- All meaningful architectural changes require Lead approval
- Document spatial/algorithm decisions here before implementation
- Keep history focused on work, decisions focused on direction
