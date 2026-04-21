# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository analyzes the feasibility of transitioning DC from individual curbside trash cans to a Barcelona-style shared container system. The analysis evaluates walking distances, capacity, costs, and parking impacts.

## Commands

### Data Pipeline
```bash
# Fetch DC spatial data (addresses, blocks, streets) from DC Open Data
python src/fetch_dc_data.py

# Run container placement algorithm
python analysis/container_placement.py

# Run capacity analysis
python analysis/capacity_model.py

# Run cost/parking analysis
python analysis/cost_model.py
```

### Interactive App
```bash
# Launch the Streamlit address lookup app
streamlit run app/app.py
```

### Dependencies
The project uses: `geopandas`, `pandas`, `numpy`, `pyarrow`, `scikit-learn`, `streamlit`, `streamlit-folium`, `folium`, `pyproj`, `requests`, `scipy`

Install all dependencies with: `pip install -r requirements.txt`

## Architecture

### Coordinate Reference System
**All spatial data must use EPSG:2248** (NAD83 / Maryland State Plane, US feet). This CRS is critical because:
- Distance thresholds (250/500/750 ft) are in feet
- The CRS native unit is feet, enabling direct distance calculations without conversion

### Data Flow
```
DC Open Data APIs → src/fetch_dc_data.py → data/raw/*.parquet
                                                 ↓
                              analysis/container_placement.py
                                                 ↓
                              data/processed/container_locations.parquet
                                                 ↓
                    analysis/capacity_model.py + analysis/cost_model.py
                                                 ↓
                              data/processed/*.json (summaries)
                                                 ↓
                                    app/app.py (Streamlit)
```

### Key Design Patterns

1. **Parameterized Assumptions**: All models use `@dataclass` classes to define assumptions (e.g., `CurrentSystemAssumptions`, `SharedSystemAssumptions`). This enables sensitivity analysis and makes assumptions explicit.

2. **Block-Based Analysis**: Addresses are grouped by `BLOCKKEY` field. Container placement uses k-means clustering within each block to find 2-3 optimal locations.

3. **Distance Thresholds**: The system evaluates three walking distance scenarios: 250 ft, 500 ft, and 750 ft. Compliance is tracked per block.

4. **Spatial Indexing**: The app uses `scipy.spatial.cKDTree` for fast nearest-neighbor queries when looking up addresses.

### Output Files
- `data/processed/container_locations.parquet` - Container placement GeoDataFrame
- `data/processed/placement_summary.json` - Stats by ward and threshold
- `data/processed/capacity_analysis.json` - Capacity model results with assumptions
- `data/processed/cost_analysis.json` - Cost breakdown with all assumptions

## Task Backlog

Planned tasks are in `backlog/tasks/`. Each task file specifies goal, outputs, scope, constraints, and acceptance criteria.
