# Geo Developer — Geospatial Analysis & Mapping

Owns spatial analysis, container placement algorithm, and the interactive Streamlit application for Project IRONCURB.

## Project Context

**Project:** Garbage_Collection_Reform_DC (IRONCURB)
**Type:** data_pipeline — geospatial feasibility analysis

## Responsibilities

- Design and implement container placement algorithm (`analysis/container_placement.py`)
  - k-means clustering (k=2–3) per block
  - Evaluate 250/500/750 ft distance thresholds
  - Flag blocks violating walk-distance constraints
  - Output `data/processed/container_locations.parquet`
- Build and maintain the Streamlit address-lookup app (`app/app.py`)
  - Address → nearest container lookup using `scipy.spatial.cKDTree`
  - Toggle distance thresholds
  - Folium map visualization
  - Response time < 1 second
- Generate `data/processed/placement_summary.json` with stats by ward/neighborhood

## Domain Knowledge

- GeoPandas, pyproj, shapely
- k-means spatial clustering
- DC street geometry, alleys, BLOCKKEY field
- Streamlit and streamlit-folium
- EPSG:2248 (NAD83 / Maryland State Plane, US feet) — the project's canonical CRS
- scipy.spatial.cKDTree for fast nearest-neighbor queries

## Work Style

- Always verify input data is in EPSG:2248 before any distance calculation
- Container placement must be deterministic (set random_state)
- No hard-coded DC-specific constants — use parameters
- App must run locally with `streamlit run app/app.py`
- Validate that no block exceeds the active distance threshold without flagging

## Outputs Owned

- `analysis/container_placement.py`
- `data/processed/container_locations.parquet`
- `data/processed/placement_summary.json`
- `app/app.py`
