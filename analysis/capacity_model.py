"""
Task 04: Trash Capacity & Collection Frequency Model

Ensures shared containers can match or exceed current trash capacity.

Key Analyses:
1. Estimate current system capacity (individual cans per household)
2. Model shared container capacity at various pickup frequencies
3. Stress-test with +25% population growth

All assumptions are explicitly documented and parameterized.

Outputs:
- Summary tables comparing current vs shared system
- Capacity analysis under +25% growth scenario
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import json
from dataclasses import dataclass, asdict


# =============================================================================
# EXPLICIT ASSUMPTIONS (all parameterized for sensitivity analysis)
# =============================================================================

@dataclass
class CurrentSystemAssumptions:
    """Assumptions about DC's current garbage collection system."""
    
    # Residential can sizes (gallons)
    trash_can_size_gal: float = 96  # Standard DC SuperCan
    recycling_can_size_gal: float = 65  # Standard recycling cart
    
    # Cans per household
    trash_cans_per_household: float = 1.0
    recycling_cans_per_household: float = 1.0
    
    # Collection frequency (pickups per week)
    trash_pickups_per_week: float = 2.0
    recycling_pickups_per_week: float = 1.0
    
    # Average utilization (how full cans are on pickup day)
    average_can_utilization: float = 0.75  # 75% full on average
    
    # Description for documentation
    source: str = "DC DPW standard residential service"


@dataclass 
class SharedSystemAssumptions:
    """Assumptions about the proposed shared container system."""
    
    # Shared container size (gallons)
    # Standard 4-yard dumpster = ~600 gallons, 2-yard = ~300 gallons
    container_size_gal: float = 400  # Medium-sized shared container
    
    # Separate streams (trash, recycling, compost)
    n_waste_streams: int = 3
    
    # Collection frequency options (pickups per week)
    collection_frequencies: tuple = (2, 3, 5, 7)  # 2x, 3x, 5x, daily
    
    # Expected utilization at pickup
    average_utilization: float = 0.80  # 80% full on average
    
    # Description
    source: str = "Barcelona-style shared container system"


@dataclass
class PopulationAssumptions:
    """Assumptions about DC population and households."""
    
    # Current estimates (2024)
    total_households: int = 320_000  # Approximate DC households
    persons_per_household: float = 2.1
    
    # Growth scenario
    growth_rate: float = 0.25  # +25% stress test
    
    # Waste generation (gallons per person per week)
    waste_per_person_gal_week: float = 8.0  # ~2 gal/person/day trash
    recycling_per_person_gal_week: float = 4.0
    
    source: str = "DC Census estimates, EPA waste generation data"


# =============================================================================
# CAPACITY CALCULATIONS
# =============================================================================

def calculate_current_system_capacity(
    current: CurrentSystemAssumptions,
    population: PopulationAssumptions
) -> Dict:
    """
    Calculate the total capacity of the current individual can system.
    
    Returns:
        Dictionary with capacity metrics
    """
    # Weekly capacity per household
    trash_capacity_per_hh = (
        current.trash_can_size_gal 
        * current.trash_cans_per_household 
        * current.trash_pickups_per_week
    )
    
    recycling_capacity_per_hh = (
        current.recycling_can_size_gal 
        * current.recycling_cans_per_household 
        * current.recycling_pickups_per_week
    )
    
    # City-wide weekly capacity
    total_trash_capacity = trash_capacity_per_hh * population.total_households
    total_recycling_capacity = recycling_capacity_per_hh * population.total_households
    
    # Effective capacity (accounting for utilization)
    effective_trash = total_trash_capacity * current.average_can_utilization
    effective_recycling = total_recycling_capacity * current.average_can_utilization
    
    # Weekly demand
    weekly_trash_demand = (
        population.total_households 
        * population.persons_per_household 
        * population.waste_per_person_gal_week
    )
    
    weekly_recycling_demand = (
        population.total_households 
        * population.persons_per_household 
        * population.recycling_per_person_gal_week
    )
    
    return {
        "system": "current_individual_cans",
        "trash_capacity_per_household_weekly_gal": trash_capacity_per_hh,
        "recycling_capacity_per_household_weekly_gal": recycling_capacity_per_hh,
        "total_trash_capacity_weekly_gal": total_trash_capacity,
        "total_recycling_capacity_weekly_gal": total_recycling_capacity,
        "effective_trash_capacity_weekly_gal": effective_trash,
        "effective_recycling_capacity_weekly_gal": effective_recycling,
        "weekly_trash_demand_gal": weekly_trash_demand,
        "weekly_recycling_demand_gal": weekly_recycling_demand,
        "trash_capacity_headroom_pct": (effective_trash - weekly_trash_demand) / weekly_trash_demand * 100,
        "recycling_capacity_headroom_pct": (effective_recycling - weekly_recycling_demand) / weekly_recycling_demand * 100
    }


def calculate_shared_system_capacity(
    shared: SharedSystemAssumptions,
    population: PopulationAssumptions,
    n_containers: int,
    pickup_frequency: int
) -> Dict:
    """
    Calculate capacity of shared container system at given configuration.
    
    Args:
        shared: Shared system assumptions
        population: Population assumptions
        n_containers: Total number of containers (from placement algorithm)
        pickup_frequency: Pickups per week
        
    Returns:
        Dictionary with capacity metrics
    """
    # Total weekly capacity (all containers combined)
    # Divide by n_waste_streams since containers are split by type
    containers_per_stream = n_containers / shared.n_waste_streams
    
    total_capacity_per_stream = (
        containers_per_stream 
        * shared.container_size_gal 
        * pickup_frequency
    )
    
    effective_capacity = total_capacity_per_stream * shared.average_utilization
    
    # Weekly demand
    weekly_trash_demand = (
        population.total_households 
        * population.persons_per_household 
        * population.waste_per_person_gal_week
    )
    
    weekly_recycling_demand = (
        population.total_households 
        * population.persons_per_household 
        * population.recycling_per_person_gal_week
    )
    
    # Capacity per household
    capacity_per_hh = total_capacity_per_stream / population.total_households
    
    return {
        "system": f"shared_containers_{pickup_frequency}x_week",
        "n_containers_total": n_containers,
        "n_containers_per_stream": int(containers_per_stream),
        "container_size_gal": shared.container_size_gal,
        "pickup_frequency_per_week": pickup_frequency,
        "total_capacity_per_stream_weekly_gal": total_capacity_per_stream,
        "effective_capacity_per_stream_weekly_gal": effective_capacity,
        "capacity_per_household_weekly_gal": capacity_per_hh,
        "weekly_trash_demand_gal": weekly_trash_demand,
        "weekly_recycling_demand_gal": weekly_recycling_demand,
        "trash_capacity_headroom_pct": (effective_capacity - weekly_trash_demand) / weekly_trash_demand * 100,
        "recycling_capacity_headroom_pct": (effective_capacity - weekly_recycling_demand) / weekly_recycling_demand * 100,
        "meets_trash_demand": effective_capacity >= weekly_trash_demand,
        "meets_recycling_demand": effective_capacity >= weekly_recycling_demand
    }


def stress_test_growth(
    shared: SharedSystemAssumptions,
    population: PopulationAssumptions,
    n_containers: int,
    pickup_frequency: int
) -> Dict:
    """
    Test shared system capacity with population growth.
    
    Args:
        shared: Shared system assumptions
        population: Population assumptions
        n_containers: Total containers
        pickup_frequency: Pickups per week
        
    Returns:
        Dictionary comparing baseline vs growth scenario
    """
    # Baseline
    baseline = calculate_shared_system_capacity(
        shared, population, n_containers, pickup_frequency
    )
    
    # Growth scenario
    grown_pop = PopulationAssumptions(
        total_households=int(population.total_households * (1 + population.growth_rate)),
        persons_per_household=population.persons_per_household,
        growth_rate=population.growth_rate,
        waste_per_person_gal_week=population.waste_per_person_gal_week,
        recycling_per_person_gal_week=population.recycling_per_person_gal_week,
        source=f"{population.source} + {population.growth_rate*100:.0f}% growth"
    )
    
    growth = calculate_shared_system_capacity(
        shared, grown_pop, n_containers, pickup_frequency
    )
    
    return {
        "scenario": f"+{population.growth_rate*100:.0f}% population growth",
        "baseline_households": population.total_households,
        "growth_households": grown_pop.total_households,
        "pickup_frequency": pickup_frequency,
        "baseline_trash_headroom_pct": baseline["trash_capacity_headroom_pct"],
        "growth_trash_headroom_pct": growth["trash_capacity_headroom_pct"],
        "baseline_meets_demand": baseline["meets_trash_demand"],
        "growth_meets_demand": growth["meets_trash_demand"],
        "additional_pickups_needed": not growth["meets_trash_demand"]
    }


def find_minimum_frequency(
    shared: SharedSystemAssumptions,
    population: PopulationAssumptions,
    n_containers: int,
    with_growth: bool = False
) -> int:
    """
    Find the minimum pickup frequency needed to meet demand.
    
    Args:
        shared: Shared system assumptions
        population: Population assumptions  
        n_containers: Total containers
        with_growth: Whether to include growth scenario
        
    Returns:
        Minimum pickups per week needed
    """
    if with_growth:
        pop = PopulationAssumptions(
            total_households=int(population.total_households * (1 + population.growth_rate)),
            persons_per_household=population.persons_per_household,
            growth_rate=population.growth_rate,
            waste_per_person_gal_week=population.waste_per_person_gal_week,
            recycling_per_person_gal_week=population.recycling_per_person_gal_week,
            source=population.source
        )
    else:
        pop = population
    
    for freq in range(1, 15):  # Up to twice daily
        result = calculate_shared_system_capacity(shared, pop, n_containers, freq)
        if result["meets_trash_demand"] and result["meets_recycling_demand"]:
            return freq
    
    return -1  # Cannot meet demand


def generate_comparison_table(
    current: CurrentSystemAssumptions,
    shared: SharedSystemAssumptions,
    population: PopulationAssumptions,
    n_containers: int
) -> pd.DataFrame:
    """
    Generate comparison table of current vs shared system at various frequencies.
    
    Returns:
        DataFrame with comparison metrics
    """
    rows = []
    
    # Current system
    current_cap = calculate_current_system_capacity(current, population)
    rows.append({
        "System": "Current (Individual Cans)",
        "Pickup Frequency": f"{current.trash_pickups_per_week:.0f}x/week",
        "Trash Capacity (M gal/week)": current_cap["effective_trash_capacity_weekly_gal"] / 1e6,
        "Trash Demand (M gal/week)": current_cap["weekly_trash_demand_gal"] / 1e6,
        "Headroom (%)": current_cap["trash_capacity_headroom_pct"],
        "Meets Demand": "Yes" if current_cap["trash_capacity_headroom_pct"] > 0 else "No"
    })
    
    # Shared system at various frequencies
    for freq in shared.collection_frequencies:
        shared_cap = calculate_shared_system_capacity(
            shared, population, n_containers, freq
        )
        rows.append({
            "System": "Shared Containers",
            "Pickup Frequency": f"{freq}x/week",
            "Trash Capacity (M gal/week)": shared_cap["effective_capacity_per_stream_weekly_gal"] / 1e6,
            "Trash Demand (M gal/week)": shared_cap["weekly_trash_demand_gal"] / 1e6,
            "Headroom (%)": shared_cap["trash_capacity_headroom_pct"],
            "Meets Demand": "Yes" if shared_cap["meets_trash_demand"] else "No"
        })
    
    return pd.DataFrame(rows)


def print_analysis(
    current: CurrentSystemAssumptions,
    shared: SharedSystemAssumptions,
    population: PopulationAssumptions,
    n_containers: int
):
    """Print comprehensive capacity analysis."""
    
    print("\n" + "=" * 80)
    print("TRASH CAPACITY & COLLECTION FREQUENCY MODEL")
    print("=" * 80)
    
    # Print assumptions
    print("\n" + "-" * 80)
    print("EXPLICIT ASSUMPTIONS")
    print("-" * 80)
    
    print("\nCurrent System (Individual Cans):")
    print(f"  Trash can size: {current.trash_can_size_gal} gallons")
    print(f"  Cans per household: {current.trash_cans_per_household}")
    print(f"  Pickup frequency: {current.trash_pickups_per_week}x per week")
    print(f"  Average utilization: {current.average_can_utilization*100:.0f}%")
    print(f"  Source: {current.source}")
    
    print("\nShared System (Community Containers):")
    print(f"  Container size: {shared.container_size_gal} gallons")
    print(f"  Waste streams: {shared.n_waste_streams} (trash, recycling, compost)")
    print(f"  Average utilization: {shared.average_utilization*100:.0f}%")
    print(f"  Total containers: {n_containers:,}")
    print(f"  Source: {shared.source}")
    
    print("\nPopulation/Demand:")
    print(f"  Total households: {population.total_households:,}")
    print(f"  Persons per household: {population.persons_per_household}")
    print(f"  Waste generation: {population.waste_per_person_gal_week} gal/person/week")
    print(f"  Source: {population.source}")
    
    # Comparison table
    print("\n" + "-" * 80)
    print("CAPACITY COMPARISON: CURRENT VS SHARED SYSTEM")
    print("-" * 80)
    
    comparison = generate_comparison_table(current, shared, population, n_containers)
    print(comparison.to_string(index=False))
    
    # Find minimum frequencies
    min_freq_baseline = find_minimum_frequency(shared, population, n_containers, False)
    min_freq_growth = find_minimum_frequency(shared, population, n_containers, True)
    
    print("\n" + "-" * 80)
    print("MINIMUM PICKUP FREQUENCY ANALYSIS")
    print("-" * 80)
    print(f"\nTo meet current demand:")
    print(f"  Minimum pickup frequency: {min_freq_baseline}x per week")
    
    print(f"\nTo meet demand with +{population.growth_rate*100:.0f}% population growth:")
    print(f"  Minimum pickup frequency: {min_freq_growth}x per week")
    
    # Stress test results
    print("\n" + "-" * 80)
    print(f"STRESS TEST: +{population.growth_rate*100:.0f}% POPULATION GROWTH")
    print("-" * 80)
    
    for freq in shared.collection_frequencies:
        stress = stress_test_growth(shared, population, n_containers, freq)
        status = "✓ MEETS DEMAND" if stress["growth_meets_demand"] else "✗ INSUFFICIENT"
        print(f"\n  {freq}x/week pickup:")
        print(f"    Baseline headroom: {stress['baseline_trash_headroom_pct']:+.1f}%")
        print(f"    +25% growth headroom: {stress['growth_trash_headroom_pct']:+.1f}%")
        print(f"    Status: {status}")
    
    # Key findings
    print("\n" + "-" * 80)
    print("KEY FINDINGS")
    print("-" * 80)
    
    current_cap = calculate_current_system_capacity(current, population)
    
    print(f"\n1. CAPACITY PARITY:")
    if min_freq_baseline <= current.trash_pickups_per_week:
        print(f"   ✓ Shared system can match current capacity at same pickup frequency")
        print(f"     ({min_freq_baseline}x/week vs current {current.trash_pickups_per_week:.0f}x/week)")
    else:
        print(f"   ✗ Shared system requires more frequent pickup")
        print(f"     ({min_freq_baseline}x/week vs current {current.trash_pickups_per_week:.0f}x/week)")
    
    print(f"\n2. GROWTH RESILIENCE:")
    if min_freq_growth <= 7:
        print(f"   ✓ System can handle +25% growth with {min_freq_growth}x/week pickup")
    else:
        print(f"   ✗ System may struggle with +25% growth")
    
    print(f"\n3. FLEXIBILITY:")
    print(f"   Shared system can scale capacity by increasing pickup frequency")
    print(f"   without adding infrastructure (unlike individual cans)")


def main():
    """Main entry point for capacity model."""
    
    # Initialize assumptions
    current = CurrentSystemAssumptions()
    shared = SharedSystemAssumptions()
    population = PopulationAssumptions()
    
    # Load container count from placement algorithm
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    processed_dir = project_root / "data" / "processed"
    
    # Try to load actual container count
    try:
        summary_path = processed_dir / "placement_summary.json"
        with open(summary_path) as f:
            placement_summary = json.load(f)
        n_containers = int(placement_summary["overall"]["total_containers"])
        print(f"Loaded container count from placement algorithm: {n_containers:,}")
    except (FileNotFoundError, KeyError):
        # Fallback estimate
        n_containers = 18000
        print(f"Using estimated container count: {n_containers:,}")
    
    # Run analysis
    print_analysis(current, shared, population, n_containers)
    
    # Save results
    results = {
        "assumptions": {
            "current_system": asdict(current),
            "shared_system": asdict(shared),
            "population": asdict(population)
        },
        "n_containers": n_containers,
        "current_system_capacity": calculate_current_system_capacity(current, population),
        "shared_system_by_frequency": {},
        "stress_tests": {},
        "minimum_frequencies": {
            "baseline": find_minimum_frequency(shared, population, n_containers, False),
            "with_25pct_growth": find_minimum_frequency(shared, population, n_containers, True)
        }
    }
    
    # Add shared system results for each frequency
    for freq in shared.collection_frequencies:
        results["shared_system_by_frequency"][f"{freq}x_week"] = calculate_shared_system_capacity(
            shared, population, n_containers, freq
        )
        results["stress_tests"][f"{freq}x_week"] = stress_test_growth(
            shared, population, n_containers, freq
        )
    
    # Save to JSON
    output_path = processed_dir / "capacity_analysis.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n\nResults saved to: {output_path}")
    
    # Save comparison table to CSV
    comparison = generate_comparison_table(current, shared, population, n_containers)
    csv_path = processed_dir / "capacity_comparison.csv"
    comparison.to_csv(csv_path, index=False)
    print(f"Comparison table saved to: {csv_path}")
    
    return results


if __name__ == "__main__":
    main()
