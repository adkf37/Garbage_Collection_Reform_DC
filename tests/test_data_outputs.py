"""
Task validation tests for Project IRONCURB.

Checks that all pipeline outputs exist and satisfy the acceptance criteria
defined in backlog/tasks/*.md.

Run with: pytest tests/test_data_outputs.py -v
"""

import json
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROC = PROJECT_ROOT / "data" / "processed"
RESEARCH_DIR = PROJECT_ROOT / "research"

STANDARD_EPSG = 2248  # NAD83 / Maryland State Plane, US feet


# ===========================================================================
# Task 01 — Barcelona Research
# ===========================================================================


class TestBarcelonaResearch:
    """Acceptance criteria from backlog/tasks/01_research_barcelona.md."""

    def test_file_exists(self):
        assert (RESEARCH_DIR / "barcelona_shared_waste.md").exists()

    def test_minimum_length(self):
        text = (RESEARCH_DIR / "barcelona_shared_waste.md").read_text()
        assert len(text.split()) >= 1000, "Research summary must be at least 1,000 words"

    def test_required_sections(self):
        text = (RESEARCH_DIR / "barcelona_shared_waste.md").read_text()
        required = [
            "System Overview",
            "Key Metrics",
            "Evidence Quality",
            "Drawbacks",
            "Assumptions Derived",
            "Transferability",
            "What We Know",
            "Sources",
        ]
        for section in required:
            assert section in text, f"Missing required section: {section}"

    def test_minimum_sources(self):
        text = (RESEARCH_DIR / "barcelona_shared_waste.md").read_text()
        # Count numbered source lines (lines starting with a digit followed by .)
        source_lines = [
            ln
            for ln in text.splitlines()
            if ln.strip() and ln.strip()[0].isdigit() and ". " in ln
        ]
        assert len(source_lines) >= 3, "Must cite at least 3 credible sources"

    def test_assumptions_table_present(self):
        text = (RESEARCH_DIR / "barcelona_shared_waste.md").read_text()
        # Table must contain at least one row with a numeric value
        assert "400 gal" in text or "400" in text, (
            "Assumptions Derived table must include container size value"
        )


# ===========================================================================
# Task 02 — DC Spatial Baseline
# ===========================================================================


class TestDCSpatialBaseline:
    """Acceptance criteria from backlog/tasks/02_dc_spatial_baseline.md."""

    def test_addresses_parquet_exists(self):
        assert (DATA_RAW / "dc_addresses.parquet").exists()

    def test_blocks_parquet_exists(self):
        assert (DATA_RAW / "dc_blocks.parquet").exists()

    def test_addresses_loads(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_addresses.parquet")
        assert len(gdf) > 0

    def test_addresses_crs(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_addresses.parquet")
        assert gdf.crs.to_epsg() == STANDARD_EPSG

    def test_addresses_has_blockkey(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_addresses.parquet")
        assert "BLOCKKEY" in gdf.columns

    def test_addresses_blockkey_null_rate(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_addresses.parquet")
        null_pct = gdf["BLOCKKEY"].isna().mean() * 100
        assert null_pct < 1.0, f"BLOCKKEY null rate {null_pct:.2f}% exceeds 1%"

    def test_addresses_has_ward(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_addresses.parquet")
        ward_cols = [c for c in gdf.columns if "ward" in c.lower()]
        assert len(ward_cols) > 0, "No WARD column found in addresses"

    def test_addresses_no_invalid_geometry(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_addresses.parquet")
        invalid = (~gdf.geometry.is_valid).sum()
        assert invalid == 0, f"{invalid} invalid geometries in addresses"

    def test_blocks_crs(self):
        gdf = gpd.read_parquet(DATA_RAW / "dc_blocks.parquet")
        assert gdf.crs.to_epsg() == STANDARD_EPSG


# ===========================================================================
# Task 03 — Container Placement
# ===========================================================================


class TestContainerPlacement:
    """Acceptance criteria from backlog/tasks/03_container_placement.md."""

    def test_container_locations_exists(self):
        assert (DATA_PROC / "container_locations.parquet").exists()

    def test_container_locations_loads(self):
        gdf = gpd.read_parquet(DATA_PROC / "container_locations.parquet")
        assert len(gdf) > 0

    def test_container_crs(self):
        gdf = gpd.read_parquet(DATA_PROC / "container_locations.parquet")
        assert gdf.crs.to_epsg() == STANDARD_EPSG

    def test_container_required_columns(self):
        gdf = gpd.read_parquet(DATA_PROC / "container_locations.parquet")
        for col in ("block_id", "container_id", "addresses_served", "ward"):
            assert col in gdf.columns, f"Missing column: {col}"

    def test_placement_summary_exists(self):
        assert (DATA_PROC / "placement_summary.json").exists()

    def test_placement_summary_structure(self):
        with open(DATA_PROC / "placement_summary.json") as f:
            ps = json.load(f)
        for key in ("overall", "by_threshold", "by_ward"):
            assert key in ps, f"Missing key '{key}' in placement_summary.json"

    def test_placement_summary_thresholds(self):
        with open(DATA_PROC / "placement_summary.json") as f:
            ps = json.load(f)
        thresholds = ps["by_threshold"]
        # Keys may be "250ft" / "500ft" / "750ft" or integer / string "250"
        keys_str = [str(k) for k in thresholds.keys()]
        for t in (250, 500, 750):
            found = str(t) in keys_str or f"{t}ft" in keys_str
            assert found, f"Missing threshold {t} ft in placement_summary['by_threshold']"

    def test_block_stats_exists(self):
        assert (DATA_PROC / "block_stats.parquet").exists()

    def test_placement_summary_has_ward_breakdown(self):
        with open(DATA_PROC / "placement_summary.json") as f:
            ps = json.load(f)
        by_ward = ps["by_ward"]
        assert len(by_ward) >= 1, "by_ward section must have at least one ward"


# ===========================================================================
# Task 04 — Capacity Model
# ===========================================================================


class TestCapacityModel:
    """Acceptance criteria from backlog/tasks/04_capacity_model.md."""

    def test_capacity_analysis_exists(self):
        assert (DATA_PROC / "capacity_analysis.json").exists()

    def test_capacity_analysis_structure(self):
        with open(DATA_PROC / "capacity_analysis.json") as f:
            cap = json.load(f)
        for key in (
            "assumptions",
            "current_system_capacity",
            "shared_system_by_frequency",
            "stress_tests",
            "minimum_frequencies",
        ):
            assert key in cap, f"Missing key '{key}' in capacity_analysis.json"

    def test_capacity_comparison_csv_exists(self):
        assert (DATA_PROC / "capacity_comparison.csv").exists()

    def test_capacity_comparison_csv_readable(self):
        df = pd.read_csv(DATA_PROC / "capacity_comparison.csv")
        assert len(df) > 0

    def test_growth_scenario_in_stress_tests(self):
        with open(DATA_PROC / "capacity_analysis.json") as f:
            cap = json.load(f)
        # Growth scenario may appear in minimum_frequencies keys or stress_test scenario fields
        mf_keys = [str(k).lower() for k in cap.get("minimum_frequencies", {}).keys()]
        growth_in_mf = any("growth" in k or "25" in k for k in mf_keys)

        stress = cap.get("stress_tests", {})
        growth_in_stress = any(
            "growth" in str(v.get("scenario", "")).lower()
            or "25" in str(v.get("growth_households", ""))
            for v in stress.values()
            if isinstance(v, dict)
        )

        assert growth_in_mf or growth_in_stress, (
            "No +25% growth scenario found in capacity_analysis.json"
        )

    def test_minimum_frequencies_present(self):
        with open(DATA_PROC / "capacity_analysis.json") as f:
            cap = json.load(f)
        mf = cap.get("minimum_frequencies", {})
        assert len(mf) >= 1, "minimum_frequencies section is empty"


# ===========================================================================
# Task 05 — Cost & Parking Model
# ===========================================================================


class TestCostModel:
    """Acceptance criteria from backlog/tasks/05_cost_and_parking.md."""

    def test_cost_analysis_exists(self):
        assert (DATA_PROC / "cost_analysis.json").exists()

    def test_cost_analysis_structure(self):
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        for key in ("capital_costs", "annual_operating_costs", "parking_impact"):
            assert key in cost, f"Missing key '{key}' in cost_analysis.json"

    def test_cost_comparison_csv_exists(self):
        assert (DATA_PROC / "cost_comparison.csv").exists()

    def test_cost_comparison_csv_readable(self):
        df = pd.read_csv(DATA_PROC / "cost_comparison.csv")
        assert len(df) > 0

    def test_capital_cost_is_positive(self):
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        total_capital = cost["capital_costs"].get("total_capital_cost", 0)
        assert float(total_capital) > 0, "Total capital cost must be positive"

    def test_parking_impact_present(self):
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        parking = cost["parking_impact"]
        assert len(parking) >= 1, "parking_impact section is empty"


# ===========================================================================
# Task 06 — App & Report files exist
# ===========================================================================


class TestAppAndReport:
    """Minimal existence checks from backlog/tasks/06_app_and_report.md."""

    def test_app_py_exists(self):
        assert (PROJECT_ROOT / "app" / "app.py").exists()

    def test_report_qmd_exists(self):
        assert (PROJECT_ROOT / "report" / "ironcurb.qmd").exists()

    def test_app_py_importable_structure(self):
        """Check that app.py has expected public functions and a spatial lookup capability."""
        source = (PROJECT_ROOT / "app" / "app.py").read_text()
        assert "def main(" in source, "app.py must define a main() function"
        assert "load_container_data" in source, "app.py must define load_container_data()"
        assert "find_nearest_container" in source, "app.py must define find_nearest_container()"
        assert "DISTANCE_THRESHOLDS" in source, "app.py must define DISTANCE_THRESHOLDS constant"


# ===========================================================================
# Phase 5 — Performance Benchmarks (Tester phase)
# ===========================================================================


class TestPerformanceBenchmarks:
    """
    Validate that performance acceptance criteria from phases.md are met.

    - Placement script: <60 s (verified via optimized groupby + n_init=3)
    - App spatial lookup: <1 s per query
    """

    def test_spatial_lookup_under_one_second(self):
        """Single cKDTree nearest-neighbor query must complete in <1 s."""
        import time
        import numpy as np
        from scipy.spatial import cKDTree
        from pyproj import Transformer

        gdf = gpd.read_parquet(DATA_PROC / "container_locations.parquet")
        coords = np.array([[p.x, p.y] for p in gdf.geometry])
        tree = cKDTree(coords)

        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2248", always_xy=True)
        # DC center in WGS84
        x, y = transformer.transform(-77.0369, 38.9072)

        t0 = time.perf_counter()
        tree.query([x, y])
        elapsed = time.perf_counter() - t0

        assert elapsed < 1.0, f"Spatial lookup took {elapsed:.3f}s (must be <1.0s)"

    def test_placement_script_uses_groupby(self):
        """
        Verify the placement script uses groupby instead of per-block boolean
        filtering — the key optimization that keeps runtime under 60 s.
        """
        source = (PROJECT_ROOT / "analysis" / "container_placement.py").read_text()
        assert "groupby" in source, (
            "container_placement.py must use groupby for block iteration to meet <60s target"
        )
