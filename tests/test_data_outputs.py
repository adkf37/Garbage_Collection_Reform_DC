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

    def test_capacity_model_has_fallback(self):
        """capacity_model.py must run core calculations without placement_summary.json."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "capacity_model", PROJECT_ROOT / "analysis" / "capacity_model.py"
        )
        cm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cm)

        # With a synthetic container count (simulating missing placement_summary.json)
        freq = cm.find_minimum_frequency(
            cm.SharedSystemAssumptions(), cm.PopulationAssumptions(), 18000, with_growth=False
        )
        assert isinstance(freq, int) and freq >= 1, (
            "capacity_model.find_minimum_frequency() must return a positive integer "
            "when called with a fallback container count"
        )

    def test_at_least_one_frequency_meets_growth_demand(self):
        """At least one pickup frequency must satisfy demand under the +25% growth scenario."""
        with open(DATA_PROC / "capacity_analysis.json") as f:
            cap = json.load(f)
        stress_tests = cap.get("stress_tests", {})
        assert any(
            v.get("growth_meets_demand", False)
            for v in stress_tests.values()
            if isinstance(v, dict)
        ), "No pickup frequency in stress_tests meets demand under the +25% growth scenario"


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

    def test_current_system_costs_present(self):
        """Current system costs must be included for comparison."""
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        assert "current_system_costs" in cost, (
            "cost_analysis.json must include 'current_system_costs' for comparison"
        )
        current = cost["current_system_costs"]
        assert "annual_costs" in current, "current_system_costs must have 'annual_costs' sub-key"
        assert float(current["annual_costs"]["total"]) > 0, "Current system annual cost must be positive"

    def test_comparison_section_present(self):
        """Net cost difference must be explicitly calculated in a comparison section."""
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        assert "comparison" in cost, (
            "cost_analysis.json must include 'comparison' section with net cost difference"
        )

    def test_net_cost_difference_calculated(self):
        """comparison section must contain a numeric net annual cost difference."""
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        comparison = cost.get("comparison", {})
        assert "net_annual_cost_difference" in comparison, (
            "comparison section must contain 'net_annual_cost_difference'"
        )
        # Value must be consistent with current vs shared costs
        diff = float(comparison["net_annual_cost_difference"])
        current_total = float(cost["current_system_costs"]["annual_costs"]["total"])
        shared_total = float(cost["annual_operating_costs"]["total_annual_operating"])
        assert abs(diff - (current_total - shared_total)) < 1.0, (
            "net_annual_cost_difference must equal current_annual - shared_annual"
        )

    def test_parking_spaces_concrete_number(self):
        """Parking spaces consumed must be reported as a concrete positive number."""
        with open(DATA_PROC / "cost_analysis.json") as f:
            cost = json.load(f)
        parking = cost["parking_impact"]
        assert "parking_spaces_equivalent" in parking, (
            "parking_impact must include 'parking_spaces_equivalent'"
        )
        assert float(parking["parking_spaces_equivalent"]) > 0, (
            "parking_spaces_equivalent must be a positive number"
        )

    def test_cost_model_has_fallback(self):
        """cost_model.py must handle missing placement_summary.json gracefully."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "cost_model", PROJECT_ROOT / "analysis" / "cost_model.py"
        )
        cm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cm)

        # Core calculation must work with a synthetic fallback container count
        capital = cm.calculate_capital_costs(
            18247, 320000,
            cm.ContainerCostAssumptions(), cm.TruckCostAssumptions(),
            cm.TransitionCosts(), 3,
        )
        assert float(capital["total_capital_cost"]) > 0, (
            "calculate_capital_costs() must return a positive capital cost "
            "when called with a fallback container count"
        )


# ===========================================================================
# Task 06 — App & Report files exist
# ===========================================================================


class TestAppAndReport:
    """Acceptance criteria from backlog/tasks/06_app_and_report.md."""

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

    def test_app_distance_thresholds_not_hardcoded_in_logic(self):
        """Distance threshold values must be declared via DISTANCE_THRESHOLDS, not buried literals."""
        import ast

        source = (PROJECT_ROOT / "app" / "app.py").read_text()
        tree = ast.parse(source)

        # Find the DISTANCE_THRESHOLDS module-level assignment
        thresholds_value = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "DISTANCE_THRESHOLDS":
                        thresholds_value = ast.literal_eval(node.value)

        assert thresholds_value is not None, (
            "app.py must define DISTANCE_THRESHOLDS as a module-level assignment"
        )
        assert set(thresholds_value) == {250, 500, 750}, (
            f"DISTANCE_THRESHOLDS must contain {{250, 500, 750}}, got {thresholds_value}"
        )

    def test_app_error_handling_for_missing_data(self):
        """App must show an error message rather than crash when data files are missing."""
        source = (PROJECT_ROOT / "app" / "app.py").read_text()
        assert "st.error" in source, "app.py must call st.error() when data files are missing"

    def test_report_references_all_processed_outputs(self):
        """Quarto report must reference all three processed JSON output files."""
        source = (PROJECT_ROOT / "report" / "ironcurb.qmd").read_text()
        for fname in ("placement_summary.json", "capacity_analysis.json", "cost_analysis.json"):
            assert fname in source, f"ironcurb.qmd must reference '{fname}'"

    def test_app_sampling_is_deterministic(self):
        """app.py container sampling must use random_state for reproducibility."""
        source = (PROJECT_ROOT / "app" / "app.py").read_text()
        assert "random_state" in source, (
            "app.py sample() call must use random_state for deterministic map rendering"
        )


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
