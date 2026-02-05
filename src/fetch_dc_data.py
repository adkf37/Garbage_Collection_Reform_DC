"""
Task 02: DC Spatial Baseline Construction

Fetches authoritative DC GIS data:
- Street centerlines
- Census blocks (2020)
- Address points

All data standardized to EPSG:2248 (Maryland State Plane, feet) for distance calculations.

Data Sources:
- DC Open Data Portal (https://opendata.dc.gov)
- ArcGIS REST Services
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import requests
import json
from typing import Optional
import warnings

# Suppress pandas warnings about fragmentation
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

# Standard CRS for all DC data (Maryland State Plane, US feet)
# Good for distance calculations in feet
STANDARD_CRS = "EPSG:2248"

# DC Open Data URLs - using direct ArcGIS FeatureServer endpoints
DC_DATA_SOURCES = {
    "streets": {
        "url": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/57/query",
        "type": "arcgis_query",
        "description": "DC Street Centerlines",
        "output": "dc_streets.parquet"
    },
    "blocks": {
        "url": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Planning_Landuse_WebMercator/MapServer/46/query",
        "type": "arcgis_query",
        "description": "DC Square/Blocks (Planning)",
        "output": "dc_blocks.parquet"
    },
    "addresses": {
        "url": "https://opendata.arcgis.com/api/v3/datasets/aa514416aaf74fdc94748f1e56e7cc8a_0/downloads/data?format=geojson&spatialRefId=4326",
        "type": "geojson_download",  
        "description": "DC Address Points",
        "output": "dc_addresses.parquet"
    }
}


def fetch_geojson_download(url: str) -> gpd.GeoDataFrame:
    """
    Fetch GeoJSON from a direct download URL.
    
    Args:
        url: Direct GeoJSON download URL
    
    Returns:
        GeoDataFrame with all features
    """
    print(f"  Downloading GeoJSON (this may take a while for large datasets)...")
    response = requests.get(url, timeout=300)
    response.raise_for_status()
    
    print(f"  Parsing GeoJSON...")
    gdf = gpd.read_file(response.text, driver='GeoJSON')
    
    return gdf


def fetch_arcgis_features(url: str, max_records: int = 2000) -> gpd.GeoDataFrame:
    """
    Fetch all features from an ArcGIS REST API endpoint.
    
    Handles pagination for large datasets.
    
    Args:
        url: ArcGIS REST API query endpoint
        max_records: Records per request (server may limit)
    
    Returns:
        GeoDataFrame with all features
    """
    all_features = []
    offset = 0
    
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": max_records
        }
        
        print(f"  Fetching records {offset} to {offset + max_records}...")
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        features = data.get("features", [])
        
        if not features:
            break
            
        all_features.extend(features)
        
        # Check if we got fewer records than requested (last page)
        if len(features) < max_records:
            break
            
        offset += max_records
    
    if not all_features:
        raise ValueError(f"No features returned from {url}")
    
    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }
    
    return gpd.GeoDataFrame.from_features(geojson)


def validate_and_fix_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Validate geometries and fix common issues.
    
    Args:
        gdf: Input GeoDataFrame
        
    Returns:
        GeoDataFrame with valid geometries
    """
    # Check for invalid geometries
    invalid_count = (~gdf.geometry.is_valid).sum()
    if invalid_count > 0:
        print(f"  Fixing {invalid_count} invalid geometries...")
        gdf.geometry = gdf.geometry.buffer(0)
    
    # Remove null geometries
    null_count = gdf.geometry.isna().sum()
    if null_count > 0:
        print(f"  Removing {null_count} null geometries...")
        gdf = gdf[gdf.geometry.notna()].copy()
    
    # Remove empty geometries
    empty_count = gdf.geometry.is_empty.sum()
    if empty_count > 0:
        print(f"  Removing {empty_count} empty geometries...")
        gdf = gdf[~gdf.geometry.is_empty].copy()
    
    return gdf


def standardize_crs(gdf: gpd.GeoDataFrame, target_crs: str = STANDARD_CRS) -> gpd.GeoDataFrame:
    """
    Standardize CRS to target projection.
    
    Args:
        gdf: Input GeoDataFrame
        target_crs: Target CRS (default: Maryland State Plane)
        
    Returns:
        Reprojected GeoDataFrame
    """
    if gdf.crs is None:
        print(f"  Warning: No CRS defined, assuming WGS84 (EPSG:4326)")
        gdf = gdf.set_crs("EPSG:4326")
    
    if gdf.crs.to_string() != target_crs:
        print(f"  Reprojecting from {gdf.crs} to {target_crs}...")
        gdf = gdf.to_crs(target_crs)
    
    return gdf


def fetch_and_process_dataset(
    name: str,
    url: str,
    output_path: Path,
    description: str,
    data_type: str = "arcgis_query"
) -> Optional[gpd.GeoDataFrame]:
    """
    Fetch, validate, standardize, and save a dataset.
    
    Args:
        name: Dataset identifier
        url: Data URL
        output_path: Path to save parquet file
        description: Human-readable description
        data_type: "geojson_download" or "arcgis_query"
        
    Returns:
        Processed GeoDataFrame or None on error
    """
    print(f"\n{'='*60}")
    print(f"Processing: {description}")
    print(f"{'='*60}")
    
    try:
        # Fetch data
        print("Fetching data from DC Open Data...")
        if data_type == "geojson_download":
            gdf = fetch_geojson_download(url)
        else:
            gdf = fetch_arcgis_features(url)
        print(f"  Retrieved {len(gdf)} features")
        
        # Validate and fix geometries
        print("Validating geometries...")
        gdf = validate_and_fix_geometry(gdf)
        print(f"  {len(gdf)} valid features remaining")
        
        # Standardize CRS
        print("Standardizing CRS...")
        gdf = standardize_crs(gdf)
        
        # Save to parquet
        print(f"Saving to {output_path}...")
        gdf.to_parquet(output_path)
        print(f"  Saved successfully")
        
        # Print summary
        print(f"\nSummary for {name}:")
        print(f"  Features: {len(gdf)}")
        print(f"  CRS: {gdf.crs}")
        print(f"  Bounds: {gdf.total_bounds}")
        print(f"  Columns: {list(gdf.columns)}")
        
        return gdf
        
    except Exception as e:
        print(f"ERROR processing {name}: {e}")
        return None


def main():
    """Main entry point for data fetching."""
    print("DC Spatial Baseline Construction")
    print("=" * 60)
    print(f"Standard CRS: {STANDARD_CRS} (Maryland State Plane, feet)")
    
    # Set up output directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Fetch each dataset
    for name, config in DC_DATA_SOURCES.items():
        output_path = output_dir / config["output"]
        gdf = fetch_and_process_dataset(
            name=name,
            url=config["url"],
            output_path=output_path,
            description=config["description"],
            data_type=config.get("type", "arcgis_query")
        )
        results[name] = gdf
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for gdf in results.values() if gdf is not None)
    print(f"Successfully processed: {success_count}/{len(DC_DATA_SOURCES)} datasets")
    
    for name, gdf in results.items():
        if gdf is not None:
            print(f"  ✓ {name}: {len(gdf)} features")
        else:
            print(f"  ✗ {name}: FAILED")
    
    print(f"\nOutput directory: {output_dir}")
    print("All data uses CRS:", STANDARD_CRS)
    
    return results


if __name__ == "__main__":
    main()
