# Squad Decisions

## Active Decisions

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
