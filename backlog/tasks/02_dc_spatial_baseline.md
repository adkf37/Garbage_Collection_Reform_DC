# Task 02 - DC Spatial Baseline Construction

## Goal
Create a clean, reproducible spatial baseline of DC addresses and blocks
by fetching data from authoritative DC GIS sources via scripted API calls.

## Owner
Data Engineer (supporting: Geo Developer)

## Dependencies
None -- this task can start immediately.

## Inputs
- DC Open Data / ArcGIS REST endpoints (defined in `src/fetch_dc_data.py`):
  - **Streets**: `https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/57/query`
  - **Blocks**: `https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Planning_Landuse_WebMercator/MapServer/46/query`
  - **Addresses**: `https://opendata.arcgis.com/api/v3/datasets/aa514416aaf74fdc94748f1e56e7cc8a_0/downloads/data?format=geojson&spatialRefId=4326`

## Outputs
- `data/raw/dc_streets.parquet`   -- street centerlines
- `data/raw/dc_blocks.parquet`    -- planning blocks
- `data/raw/dc_addresses.parquet` -- address points with BLOCKKEY and WARD columns
- `data/README.md` (update) -- document data provenance and column definitions

## Implementation Steps
1. Run `python src/fetch_dc_data.py` to download all three layers
2. Each layer is fetched with paginated ArcGIS REST queries (2,000 records/page)
   or direct GeoJSON download
3. Invalid/null/empty geometries are automatically repaired or dropped
4. All layers are reprojected to **EPSG:2248** (NAD83 / Maryland State Plane, US feet)
5. Results are saved as GeoParquet files in `data/raw/`

## Key Columns Required
- `dc_addresses.parquet` must include: `BLOCKKEY`, `WARD`, geometry (Point)
- `dc_blocks.parquet` must include: block identifier, geometry (Polygon)

## Constraints
- Scripted fetch only -- no manual downloads or local file copies
- CRS must be EPSG:2248 for all output files
- Script must be idempotent (safe to re-run)

## Acceptance Criteria
- [x] All three parquet files exist in `data/raw/` (`dc_addresses.parquet`, `dc_blocks.parquet` committed; `dc_streets.parquet` must be regenerated via `python src/fetch_dc_data.py` — not committed as it is not consumed by any current analysis script)
- [x] `gpd.read_parquet("data/raw/dc_addresses.parquet")` loads without error
- [x] `gpd.read_parquet("data/raw/dc_blocks.parquet")` loads without error
- [x] CRS of all outputs is EPSG:2248 (`gdf.crs.to_epsg() == 2248`)
- [x] `BLOCKKEY` column present in addresses with <1% null rate
- [x] `WARD` column present in addresses
- [x] Zero invalid geometries in any layer
- [x] Script runs end-to-end without manual intervention
- [x] `data/README.md` notes data sources and column definitions
