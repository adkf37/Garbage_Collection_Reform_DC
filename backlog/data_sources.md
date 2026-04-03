# Data Sources

All data for Project IRONCURB is fetched programmatically from public APIs.
No manual downloads are required or permitted.

## DC Open Data Sources

### Address Points
- **Layer**: DC Address Points
- **URL**: `https://opendata.arcgis.com/api/v3/datasets/aa514416aaf74fdc94748f1e56e7cc8a_0/downloads/data?format=geojson&spatialRefId=4326`
- **Type**: GeoJSON direct download
- **Output**: `data/raw/dc_addresses.parquet`
- **Key Columns**: `BLOCKKEY` (block grouping), `WARD` (ward 1-8), geometry (Point)
- **CRS**: Fetched as EPSG:4326 (WGS84), reprojected to EPSG:2248
- **Expected Size**: ~170,000 address points

### Street Centerlines
- **Layer**: DC Street Centerlines (Transportation)
- **URL**: `https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/57/query`
- **Type**: ArcGIS REST API (paginated, 2,000 records/page)
- **Output**: `data/raw/dc_streets.parquet`
- **CRS**: Fetched in WebMercator, reprojected to EPSG:2248

### Planning Blocks
- **Layer**: DC Square/Blocks (Planning)
- **URL**: `https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Planning_Landuse_WebMercator/MapServer/46/query`
- **Type**: ArcGIS REST API (paginated, 2,000 records/page)
- **Output**: `data/raw/dc_blocks.parquet`
- **CRS**: Fetched in WebMercator, reprojected to EPSG:2248

## Fetch Script

All three layers are downloaded by running:

```bash
python src/fetch_dc_data.py
```

The script handles:
- Pagination for large ArcGIS datasets
- Geometry validation and repair
- CRS reprojection to EPSG:2248
- Saving as GeoParquet

## Research Sources

### Barcelona Shared Waste PDF
- **File**: `research/Shared Containerized Waste Collection_ Lessons from Barcelona and Beyond.pdf`
- **Status**: Already present in repository
- **Use**: Primary source for Task 01 research synthesis

### Additional Research (to be found by Scribe)
- Barcelona city waste management reports (ajuntament.barcelona.cat)
- Academic papers on shared waste collection systems
- Comparative city studies (Vienna, Zurich, other European cities)

## Processed Data (outputs of analysis scripts)

| File | Produced by | Description |
|------|-------------|-------------|
| `data/processed/container_locations.parquet` | Task 03 | Container placement GeoDataFrame |
| `data/processed/block_stats.parquet` | Task 03 | Per-block distance statistics |
| `data/processed/placement_summary.json` | Task 03 | Aggregate stats by ward/threshold |
| `data/processed/capacity_analysis.json` | Task 04 | Capacity model results |
| `data/processed/capacity_comparison.csv` | Task 04 | Human-readable capacity table |
| `data/processed/cost_analysis.json` | Task 05 | Cost model results |
| `data/processed/cost_comparison.csv` | Task 05 | Human-readable cost table |

## Notes on Data Freshness

- DC GIS data is updated periodically; fetch dates should be logged in `data/README.md`
- The analysis does not require real-time data; a point-in-time snapshot is sufficient
- All APIs are public and require no authentication
