# Task 06 - Interactive Map & Write-Up

## Goal
Produce a public-facing interactive Streamlit map and a Quarto technical report
that communicate the analysis results to non-technical stakeholders.

## Owner
Geo Developer (supporting: Scribe)

## Dependencies
- **Task 03 must be complete** -- app requires `data/processed/container_locations.parquet`
- **Task 04 must be complete** -- report needs capacity analysis results
- **Task 05 must be complete** -- report needs cost analysis results
- Task 01 useful but not blocking -- report can reference research summary

## Inputs
- `data/processed/container_locations.parquet` (from Task 03)
- `data/processed/placement_summary.json` (from Task 03)
- `data/processed/capacity_analysis.json` (from Task 04)
- `data/processed/cost_analysis.json` (from Task 05)
- `data/raw/dc_addresses.parquet` (from Task 02, for address lookup)

## Outputs
- `app/app.py`         -- Streamlit interactive map application
- `report/ironcurb.qmd` -- Quarto report with embedded figures and tables

## App Features (app/app.py)
- **Address search**: user types a DC address, app finds the nearest container
  using `scipy.spatial.cKDTree` spatial index (response <1 second)
- **Distance threshold toggle**: radio buttons or select box to switch between
  250 / 500 / 750 ft thresholds -- map updates dynamically
- **Container map**: Folium map rendered via `streamlit-folium` showing container
  locations color-coded by threshold compliance
- **Summary statistics**: sidebar or panel showing ward-level compliance stats
- **Data loaded once**: all GeoDataFrames cached with `@st.cache_data`

## Technology Stack
| Component | Library |
|-----------|---------|
| App framework | `streamlit` |
| Map rendering | `folium` + `streamlit-folium` |
| Spatial index | `scipy.spatial.cKDTree` |
| Spatial data | `geopandas` |
| Map CRS | EPSG:4326 (WGS84, for Folium) -- convert from EPSG:2248 at load time |

## Report Sections (report/ironcurb.qmd)
1. Executive Summary
2. Problem Statement (current DC system)
3. Barcelona System Overview (reference Task 01 research)
4. Methodology (container placement algorithm)
5. Results: Walking Distance Compliance by Ward
6. Results: Capacity Analysis
7. Results: Cost & Parking Impact
8. Limitations & Assumptions
9. Conclusion

## Constraints
- App must run with `streamlit run app/app.py` -- no other setup required
- App must handle missing data files gracefully (show error, not crash)
- Report must render with `quarto render report/ironcurb.qmd` -- no manual steps
- No hidden state or magic global variables in the app

## Acceptance Criteria
- [x] `streamlit run app/app.py` starts without errors
- [x] Address lookup returns nearest container in <1 second
- [x] Distance threshold toggle updates the map display
- [x] Container map renders correctly in the browser
- [x] `report/ironcurb.qmd` renders end-to-end with `quarto render`
- [x] Report includes all 9 required sections
- [x] All figures/tables in report are generated from `data/processed/` files
- [x] App shows meaningful error message if processed data is missing
- [x] Distance threshold values readable from config -- not hard-coded in logic
