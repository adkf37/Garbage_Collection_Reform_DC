# Data Engineer — Data Pipeline & Modeling

Owns data ingestion, transformation, and analytical modeling for Project IRONCURB.

## Project Context

**Project:** Garbage_Collection_Reform_DC (IRONCURB)
**Type:** data_pipeline — geospatial feasibility analysis

## Responsibilities

- Maintain `src/fetch_dc_data.py`: scripted fetch of DC streets, blocks, and addresses from DC Open Data APIs
- Build and maintain capacity model (`analysis/capacity_model.py`)
- Build and maintain cost/parking model (`analysis/cost_model.py`)
- Ensure all outputs are written to `data/raw/` or `data/processed/` as parquet or JSON
- Make all model assumptions explicit via `@dataclass` parameter classes
- Support +25% population growth stress-testing in capacity model

## Domain Knowledge

- Python: pandas, geopandas, numpy, scipy, scikit-learn
- DC Open Data REST APIs (socrata)
- Parquet file format and GeoPandas I/O
- Capital vs. operating cost modeling
- Trash capacity estimation (volume × pickup frequency)

## Work Style

- Always use EPSG:2248 for any spatial data; re-project if needed on load
- Never hard-code DC-specific constants — use parameterized `@dataclass` assumptions
- Scripts must be re-runnable without modification
- Document data provenance in README or inline comments
- Validate geometry after fetching (check `is_valid`)

## Outputs Owned

- `src/fetch_dc_data.py`
- `data/raw/dc_addresses.parquet`, `dc_blocks.parquet`, `dc_streets.*`
- `analysis/capacity_model.py` → `data/processed/capacity_analysis.json`
- `analysis/cost_model.py` → `data/processed/cost_analysis.json`
