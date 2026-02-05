"""
Task 03: Shared Container Placement Algorithm

Generates candidate container locations that satisfy walking-distance constraints.

Algorithm:
1. Group addresses by block (using BLOCKKEY from address data)
2. For each block, use k-means clustering to find 2-3 optimal container locations
3. Evaluate coverage at 250/500/750 ft distance thresholds
4. Flag blocks where any address exceeds the threshold

Outputs:
- data/processed/container_locations.parquet
- Summary statistics by ward
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from shapely.geometry import Point
from typing import Tuple, Dict, List
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# =============================================================================
# PARAMETERS (all configurable, no hard-coded DC-specific constants)
# =============================================================================

# Distance thresholds to evaluate (in feet - matching CRS EPSG:2248)
DISTANCE_THRESHOLDS_FT = [250, 500, 750]

# Number of containers per block range
MIN_CONTAINERS_PER_BLOCK = 2
MAX_CONTAINERS_PER_BLOCK = 3

# Minimum addresses in a block to place containers
MIN_ADDRESSES_FOR_CONTAINERS = 5


def load_address_data(data_path: Path) -> gpd.GeoDataFrame:
    """
    Load address data from parquet file.
    
    Args:
        data_path: Path to dc_addresses.parquet
        
    Returns:
        GeoDataFrame with address points
    """
    gdf = gpd.read_parquet(data_path)
    print(f"Loaded {len(gdf)} addresses")
    print(f"CRS: {gdf.crs}")
    return gdf


def determine_containers_per_block(n_addresses: int) -> int:
    """
    Determine optimal number of containers based on block size.
    
    Uses a simple heuristic: more addresses = more containers (up to max).
    
    Args:
        n_addresses: Number of addresses in the block
        
    Returns:
        Number of containers to place (2 or 3)
    """
    if n_addresses < 20:
        return MIN_CONTAINERS_PER_BLOCK
    elif n_addresses < 50:
        return MIN_CONTAINERS_PER_BLOCK + 1 if MAX_CONTAINERS_PER_BLOCK > MIN_CONTAINERS_PER_BLOCK else MIN_CONTAINERS_PER_BLOCK
    else:
        return MAX_CONTAINERS_PER_BLOCK


def place_containers_on_block(
    addresses: gpd.GeoDataFrame,
    block_id: str
) -> Tuple[gpd.GeoDataFrame, Dict]:
    """
    Place containers optimally on a single block using k-means clustering.
    
    Args:
        addresses: GeoDataFrame of addresses on this block
        block_id: Block identifier
        
    Returns:
        Tuple of (container_gdf, stats_dict)
    """
    n_addresses = len(addresses)
    
    # Skip blocks with too few addresses
    if n_addresses < MIN_ADDRESSES_FOR_CONTAINERS:
        return None, {
            "block_id": block_id,
            "n_addresses": n_addresses,
            "n_containers": 0,
            "skipped": True,
            "skip_reason": "insufficient_addresses"
        }
    
    # Extract coordinates for clustering
    coords = np.array([[p.x, p.y] for p in addresses.geometry])
    
    # Determine number of containers
    n_containers = determine_containers_per_block(n_addresses)
    
    # Can't have more clusters than points
    n_containers = min(n_containers, n_addresses)
    
    # Run k-means clustering
    kmeans = KMeans(n_clusters=n_containers, random_state=42, n_init=10)
    kmeans.fit(coords)
    
    # Get container locations (cluster centers)
    container_coords = kmeans.cluster_centers_
    
    # Calculate distances from each address to nearest container
    distances = []
    for coord in coords:
        dist_to_containers = np.sqrt(np.sum((container_coords - coord) ** 2, axis=1))
        distances.append(np.min(dist_to_containers))
    
    max_distance = np.max(distances)
    mean_distance = np.mean(distances)
    
    # Create container GeoDataFrame
    container_points = [Point(x, y) for x, y in container_coords]
    container_gdf = gpd.GeoDataFrame({
        "block_id": [block_id] * n_containers,
        "container_id": [f"{block_id}_{i}" for i in range(n_containers)],
        "addresses_served": [np.sum(kmeans.labels_ == i) for i in range(n_containers)]
    }, geometry=container_points, crs=addresses.crs)
    
    # Calculate violation flags for each threshold
    stats = {
        "block_id": block_id,
        "n_addresses": n_addresses,
        "n_containers": n_containers,
        "max_distance_ft": max_distance,
        "mean_distance_ft": mean_distance,
        "skipped": False
    }
    
    for threshold in DISTANCE_THRESHOLDS_FT:
        violations = np.sum(np.array(distances) > threshold)
        stats[f"violations_{threshold}ft"] = violations
        stats[f"compliant_{threshold}ft"] = violations == 0
    
    return container_gdf, stats


def run_placement_algorithm(
    addresses: gpd.GeoDataFrame
) -> Tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Run container placement algorithm on all blocks.
    
    Args:
        addresses: Full address GeoDataFrame with BLOCKKEY column
        
    Returns:
        Tuple of (all_containers_gdf, block_stats_df)
    """
    # Ensure we have block keys
    if "BLOCKKEY" not in addresses.columns:
        raise ValueError("Address data must have BLOCKKEY column")
    
    # Get unique blocks
    blocks = addresses["BLOCKKEY"].dropna().unique()
    print(f"Processing {len(blocks)} blocks...")
    
    all_containers = []
    all_stats = []
    
    for i, block_id in enumerate(blocks):
        if i % 500 == 0:
            print(f"  Processing block {i}/{len(blocks)}...")
        
        block_addresses = addresses[addresses["BLOCKKEY"] == block_id]
        containers, stats = place_containers_on_block(block_addresses, block_id)
        
        if containers is not None:
            all_containers.append(containers)
        all_stats.append(stats)
    
    # Combine results
    if all_containers:
        containers_gdf = gpd.GeoDataFrame(
            pd.concat(all_containers, ignore_index=True),
            crs=addresses.crs
        )
    else:
        containers_gdf = gpd.GeoDataFrame(columns=["block_id", "container_id", "addresses_served", "geometry"])
    
    stats_df = pd.DataFrame(all_stats)
    
    return containers_gdf, stats_df


def add_ward_info(
    containers: gpd.GeoDataFrame,
    stats: pd.DataFrame,
    addresses: gpd.GeoDataFrame
) -> Tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Add ward information to containers and stats.
    
    Args:
        containers: Container locations GeoDataFrame
        stats: Block statistics DataFrame
        addresses: Original address data with WARD column
        
    Returns:
        Updated containers and stats with ward info
    """
    # Create block-to-ward mapping (most common ward per block)
    block_ward = addresses.groupby("BLOCKKEY")["WARD"].agg(
        lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None
    ).to_dict()
    
    # Add to stats
    stats["ward"] = stats["block_id"].map(block_ward)
    
    # Add to containers
    containers["ward"] = containers["block_id"].map(block_ward)
    
    return containers, stats


def generate_summary_stats(stats: pd.DataFrame) -> Dict:
    """
    Generate summary statistics by ward and overall.
    
    Args:
        stats: Block statistics DataFrame
        
    Returns:
        Dictionary of summary statistics
    """
    summary = {
        "overall": {},
        "by_ward": {},
        "by_threshold": {}
    }
    
    # Filter to non-skipped blocks
    active = stats[~stats["skipped"]]
    
    # Overall stats
    summary["overall"] = {
        "total_blocks": len(stats),
        "active_blocks": len(active),
        "skipped_blocks": len(stats) - len(active),
        "total_containers": active["n_containers"].sum(),
        "total_addresses_covered": active["n_addresses"].sum(),
        "avg_containers_per_block": active["n_containers"].mean(),
        "avg_max_distance_ft": active["max_distance_ft"].mean(),
        "max_max_distance_ft": active["max_distance_ft"].max()
    }
    
    # Stats by threshold
    for threshold in DISTANCE_THRESHOLDS_FT:
        compliant_col = f"compliant_{threshold}ft"
        violations_col = f"violations_{threshold}ft"
        
        compliant_blocks = active[compliant_col].sum()
        total_violations = active[violations_col].sum()
        
        summary["by_threshold"][f"{threshold}ft"] = {
            "compliant_blocks": int(compliant_blocks),
            "non_compliant_blocks": int(len(active) - compliant_blocks),
            "compliance_rate": compliant_blocks / len(active) if len(active) > 0 else 0,
            "total_address_violations": int(total_violations)
        }
    
    # Stats by ward
    if "ward" in active.columns:
        for ward in active["ward"].dropna().unique():
            ward_data = active[active["ward"] == ward]
            ward_summary = {
                "blocks": len(ward_data),
                "containers": int(ward_data["n_containers"].sum()),
                "addresses": int(ward_data["n_addresses"].sum())
            }
            
            for threshold in DISTANCE_THRESHOLDS_FT:
                compliant_col = f"compliant_{threshold}ft"
                ward_summary[f"compliant_{threshold}ft"] = int(ward_data[compliant_col].sum())
            
            summary["by_ward"][str(ward)] = ward_summary
    
    return summary


def print_summary(summary: Dict):
    """Print formatted summary statistics."""
    print("\n" + "=" * 70)
    print("CONTAINER PLACEMENT SUMMARY")
    print("=" * 70)
    
    overall = summary["overall"]
    print(f"\nOverall Statistics:")
    print(f"  Total blocks analyzed: {overall['total_blocks']}")
    print(f"  Active blocks (with containers): {overall['active_blocks']}")
    print(f"  Skipped blocks (insufficient addresses): {overall['skipped_blocks']}")
    print(f"  Total containers placed: {overall['total_containers']:.0f}")
    print(f"  Total addresses covered: {overall['total_addresses_covered']:.0f}")
    print(f"  Avg containers per block: {overall['avg_containers_per_block']:.1f}")
    print(f"  Avg max walking distance: {overall['avg_max_distance_ft']:.0f} ft")
    print(f"  Worst case walking distance: {overall['max_max_distance_ft']:.0f} ft")
    
    print(f"\nCompliance by Distance Threshold:")
    for threshold, data in summary["by_threshold"].items():
        print(f"\n  {threshold}:")
        print(f"    Compliant blocks: {data['compliant_blocks']} ({data['compliance_rate']*100:.1f}%)")
        print(f"    Non-compliant blocks: {data['non_compliant_blocks']}")
        print(f"    Address violations: {data['total_address_violations']}")
    
    print(f"\nSummary by Ward:")
    print(f"  {'Ward':<6} {'Blocks':<8} {'Containers':<12} {'Addresses':<12} {'250ft OK':<10} {'500ft OK':<10} {'750ft OK':<10}")
    print(f"  {'-'*6} {'-'*8} {'-'*12} {'-'*12} {'-'*10} {'-'*10} {'-'*10}")
    
    for ward, data in sorted(summary["by_ward"].items()):
        print(f"  {ward:<6} {data['blocks']:<8} {data['containers']:<12} {data['addresses']:<12} "
              f"{data['compliant_250ft']:<10} {data['compliant_500ft']:<10} {data['compliant_750ft']:<10}")


def identify_violating_blocks(stats: pd.DataFrame, threshold_ft: int = 500) -> pd.DataFrame:
    """
    Identify blocks that violate the given distance threshold.
    
    Args:
        stats: Block statistics DataFrame
        threshold_ft: Distance threshold in feet
        
    Returns:
        DataFrame of violating blocks sorted by severity
    """
    compliant_col = f"compliant_{threshold_ft}ft"
    violations_col = f"violations_{threshold_ft}ft"
    
    # Filter to non-skipped blocks first, then find violations
    active = stats[~stats["skipped"]].copy()
    violating = active[active[compliant_col] == False].copy()
    violating = violating.sort_values(violations_col, ascending=False)
    
    return violating[["block_id", "ward", "n_addresses", "n_containers", 
                      "max_distance_ft", violations_col]]


def main():
    """Main entry point for container placement algorithm."""
    print("Shared Container Placement Algorithm")
    print("=" * 70)
    print(f"Parameters:")
    print(f"  Distance thresholds: {DISTANCE_THRESHOLDS_FT} ft")
    print(f"  Containers per block: {MIN_CONTAINERS_PER_BLOCK}-{MAX_CONTAINERS_PER_BLOCK}")
    print(f"  Min addresses for containers: {MIN_ADDRESSES_FOR_CONTAINERS}")
    
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    raw_data_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Load address data
    print("\nLoading address data...")
    addresses = load_address_data(raw_data_dir / "dc_addresses.parquet")
    
    # Run placement algorithm
    print("\nRunning container placement algorithm...")
    containers, stats = run_placement_algorithm(addresses)
    
    # Add ward information
    print("\nAdding ward information...")
    containers, stats = add_ward_info(containers, stats, addresses)
    
    # Generate and print summary
    summary = generate_summary_stats(stats)
    print_summary(summary)
    
    # Identify violating blocks (at 500ft threshold as default)
    print("\n" + "=" * 70)
    print("BLOCKS VIOLATING 500ft THRESHOLD (Top 20)")
    print("=" * 70)
    violating = identify_violating_blocks(stats, 500)
    if len(violating) > 0:
        print(violating.head(20).to_string(index=False))
    else:
        print("All blocks comply with 500ft threshold!")
    
    # Save outputs
    print("\nSaving outputs...")
    
    # Save container locations
    container_output = processed_dir / "container_locations.parquet"
    containers.to_parquet(container_output)
    print(f"  Saved containers to: {container_output}")
    
    # Save block statistics
    stats_output = processed_dir / "block_stats.parquet"
    stats.to_parquet(stats_output)
    print(f"  Saved block stats to: {stats_output}")
    
    # Save summary as JSON
    import json
    summary_output = processed_dir / "placement_summary.json"
    with open(summary_output, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Saved summary to: {summary_output}")
    
    print("\nContainer placement complete!")
    
    return containers, stats, summary


if __name__ == "__main__":
    main()
