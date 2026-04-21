"""
Task 05: Cost & Parking Impact Model

Estimates startup and operating costs for the shared container system,
along with parking/curb space impacts.

Analyses:
1. Capital/Startup costs: new trucks, containers, old bin removal
2. Operating costs: labor, maintenance, fuel
3. Parking space impact
4. Comparison to current system costs

All assumptions are explicitly documented and adjustable.

Outputs:
- Summary tables with per-household and citywide figures
- Clear comparison to current system
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict
import json
from dataclasses import dataclass, asdict, field


# =============================================================================
# EXPLICIT ASSUMPTIONS - All adjustable for sensitivity analysis
# =============================================================================

@dataclass
class ContainerCostAssumptions:
    """Costs related to shared containers."""
    
    # Container purchase cost
    container_unit_cost: float = 2_500  # $ per container (400-gal underground/semi-underground)
    container_installation_cost: float = 1_500  # $ per container (site prep, installation)
    
    # Container specifications
    container_footprint_sqft: float = 25  # Square feet per container (5x5 ft typical)
    container_lifespan_years: int = 15  # Expected useful life
    
    # Maintenance
    container_annual_maintenance: float = 150  # $ per container per year
    
    source: str = "Industry estimates for underground/semi-underground waste containers"


@dataclass
class TruckCostAssumptions:
    """Costs related to collection trucks."""
    
    # New automated side-loader trucks
    truck_unit_cost: float = 350_000  # $ per truck
    truck_lifespan_years: int = 10
    
    # Fleet sizing (containers per truck per day)
    containers_per_truck_per_day: int = 150  # Automated collection is faster
    collection_days_per_week: int = 6  # Mon-Sat
    
    # Operating costs per truck
    annual_fuel_cost: float = 25_000  # $ per truck per year
    annual_maintenance_cost: float = 15_000  # $ per truck per year
    annual_insurance_cost: float = 8_000  # $ per truck per year
    
    source: str = "Industry estimates for automated side-loader trucks"


@dataclass
class LaborCostAssumptions:
    """Labor costs for collection operations."""
    
    # Current system (traditional rear-loader)
    current_crew_size: int = 3  # Driver + 2 collectors
    current_hourly_wage_driver: float = 28  # $ per hour
    current_hourly_wage_collector: float = 22  # $ per hour
    current_hours_per_shift: float = 8
    current_shifts_per_week: int = 10  # 2 shifts/day, 5 days
    
    # Shared system (automated)
    shared_crew_size: int = 1  # Driver only (automated arm)
    shared_hourly_wage_driver: float = 30  # $ per hour (slightly higher for skilled operator)
    shared_hours_per_shift: float = 8
    
    # Benefits multiplier (health, retirement, etc.)
    benefits_multiplier: float = 1.35  # 35% on top of wages
    
    source: str = "DC DPW wage estimates, BLS data"


@dataclass
class CurrentSystemCosts:
    """Current system cost estimates for comparison."""
    
    # Individual cans
    trash_can_cost: float = 65  # $ per 96-gal SuperCan
    recycling_can_cost: float = 50  # $ per recycling cart
    can_lifespan_years: int = 10
    
    # Trucks (traditional rear-loader)
    truck_cost: float = 280_000  # $ per truck
    trucks_in_fleet: int = 100  # Approximate DC DPW fleet for residential
    
    # Annual operating budget (estimate)
    annual_collection_budget: float = 45_000_000  # $ per year (DC DPW solid waste division)
    
    source: str = "DC DPW budget documents, industry estimates"


@dataclass
class TransitionCosts:
    """One-time costs for transitioning to the new system."""
    
    # Old bin collection and disposal
    bin_collection_cost_per_unit: float = 15  # $ to collect each old can
    bin_disposal_recycling_value: float = -5  # $ credit per can (plastic recycling)
    
    # Public outreach and education
    outreach_campaign_cost: float = 2_000_000  # $ total
    
    # Signage and wayfinding
    signage_per_container: float = 100  # $ per container location
    
    source: str = "Comparable city transition programs"


@dataclass
class ParkingAssumptions:
    """Assumptions for parking/curb space impact."""
    
    # Standard parking space dimensions
    parking_space_length_ft: float = 20  # feet
    parking_space_width_ft: float = 8  # feet
    parking_space_sqft: float = 160  # square feet
    
    # Container placement
    containers_per_location: int = 3  # One each: trash, recycling, compost
    location_footprint_sqft: float = 100  # Total footprint for 3 containers + access
    
    # Value of parking
    annual_parking_revenue_per_space: float = 2_500  # $ (metered areas)
    pct_locations_in_metered_areas: float = 0.15  # 15% of locations affect paid parking
    
    source: str = "DC DDOT parking standards"


# =============================================================================
# COST CALCULATIONS
# =============================================================================

def calculate_capital_costs(
    n_containers: int,
    n_households: int,
    container_costs: ContainerCostAssumptions,
    truck_costs: TruckCostAssumptions,
    transition_costs: TransitionCosts,
    pickup_frequency: int
) -> Dict:
    """
    Calculate one-time capital/startup costs.
    
    Args:
        n_containers: Total number of containers needed
        n_households: Number of households served
        container_costs: Container cost assumptions
        truck_costs: Truck cost assumptions
        transition_costs: Transition cost assumptions
        pickup_frequency: Pickups per week
        
    Returns:
        Dictionary with capital cost breakdown
    """
    # Container costs
    container_purchase = n_containers * container_costs.container_unit_cost
    container_installation = n_containers * container_costs.container_installation_cost
    total_container_costs = container_purchase + container_installation
    
    # Calculate truck fleet size needed
    # Total container pickups per week = n_containers * pickup_frequency
    weekly_pickups = n_containers * pickup_frequency
    daily_pickups = weekly_pickups / truck_costs.collection_days_per_week
    trucks_needed = int(np.ceil(daily_pickups / truck_costs.containers_per_truck_per_day))
    
    # Add 15% reserve fleet
    trucks_needed = int(np.ceil(trucks_needed * 1.15))
    
    truck_purchase = trucks_needed * truck_costs.truck_unit_cost
    
    # Transition costs
    # Assume 2 cans per household (trash + recycling)
    old_cans = n_households * 2
    bin_collection = old_cans * transition_costs.bin_collection_cost_per_unit
    bin_disposal_credit = old_cans * transition_costs.bin_disposal_recycling_value
    
    outreach = transition_costs.outreach_campaign_cost
    signage = (n_containers / 3) * transition_costs.signage_per_container  # Per location, not per container
    
    total_transition = bin_collection + bin_disposal_credit + outreach + signage
    
    # Total capital costs
    total_capital = total_container_costs + truck_purchase + total_transition
    
    return {
        "containers": {
            "n_containers": n_containers,
            "purchase_cost": container_purchase,
            "installation_cost": container_installation,
            "total": total_container_costs
        },
        "trucks": {
            "n_trucks_needed": trucks_needed,
            "purchase_cost": truck_purchase
        },
        "transition": {
            "old_bins_to_collect": old_cans,
            "bin_collection_cost": bin_collection,
            "bin_disposal_credit": bin_disposal_credit,
            "outreach_campaign": outreach,
            "signage": signage,
            "total": total_transition
        },
        "total_capital_cost": total_capital,
        "capital_cost_per_household": total_capital / n_households
    }


def calculate_annual_operating_costs(
    n_containers: int,
    n_trucks: int,
    n_households: int,
    pickup_frequency: int,
    container_costs: ContainerCostAssumptions,
    truck_costs: TruckCostAssumptions,
    labor_costs: LaborCostAssumptions
) -> Dict:
    """
    Calculate annual operating costs for the shared system.
    
    Returns:
        Dictionary with operating cost breakdown
    """
    # Container maintenance
    container_maintenance = n_containers * container_costs.container_annual_maintenance
    
    # Truck operating costs
    truck_fuel = n_trucks * truck_costs.annual_fuel_cost
    truck_maintenance = n_trucks * truck_costs.annual_maintenance_cost
    truck_insurance = n_trucks * truck_costs.annual_insurance_cost
    total_truck_operating = truck_fuel + truck_maintenance + truck_insurance
    
    # Labor costs
    # Calculate shifts needed per week
    shifts_per_week = n_trucks * truck_costs.collection_days_per_week
    
    # Annual labor cost
    hourly_cost = labor_costs.shared_hourly_wage_driver * labor_costs.benefits_multiplier
    weekly_labor = shifts_per_week * labor_costs.shared_hours_per_shift * hourly_cost
    annual_labor = weekly_labor * 52
    
    # Total operating
    total_operating = container_maintenance + total_truck_operating + annual_labor
    
    return {
        "container_maintenance": container_maintenance,
        "truck_operations": {
            "fuel": truck_fuel,
            "maintenance": truck_maintenance,
            "insurance": truck_insurance,
            "total": total_truck_operating
        },
        "labor": {
            "shifts_per_week": shifts_per_week,
            "hourly_cost_with_benefits": hourly_cost,
            "annual_total": annual_labor
        },
        "total_annual_operating": total_operating,
        "operating_cost_per_household": total_operating / n_households
    }


def calculate_current_system_costs(
    n_households: int,
    current_costs: CurrentSystemCosts,
    labor_costs: LaborCostAssumptions
) -> Dict:
    """
    Estimate current system costs for comparison.
    
    Returns:
        Dictionary with current system cost breakdown
    """
    # Capital invested in current cans
    cans_per_household = 2  # trash + recycling
    total_cans = n_households * cans_per_household
    avg_can_cost = (current_costs.trash_can_cost + current_costs.recycling_can_cost) / 2
    can_investment = total_cans * avg_can_cost
    
    # Truck fleet investment
    truck_investment = current_costs.trucks_in_fleet * current_costs.truck_cost
    
    # Annual operating (using DC budget as baseline)
    annual_operating = current_costs.annual_collection_budget
    
    # Annualized capital (simple straight-line)
    annualized_can_cost = can_investment / current_costs.can_lifespan_years
    annualized_truck_cost = truck_investment / 10  # 10-year truck life
    
    total_annual_cost = annual_operating + annualized_can_cost + annualized_truck_cost
    
    return {
        "capital_invested": {
            "cans": can_investment,
            "trucks": truck_investment,
            "total": can_investment + truck_investment
        },
        "annual_costs": {
            "operating_budget": annual_operating,
            "annualized_can_replacement": annualized_can_cost,
            "annualized_truck_replacement": annualized_truck_cost,
            "total": total_annual_cost
        },
        "cost_per_household": total_annual_cost / n_households
    }


def calculate_parking_impact(
    n_containers: int,
    parking: ParkingAssumptions
) -> Dict:
    """
    Calculate parking and curb space impact.
    
    Returns:
        Dictionary with parking impact metrics
    """
    # Number of container locations (3 containers per location)
    n_locations = n_containers / parking.containers_per_location
    
    # Total footprint
    total_footprint_sqft = n_locations * parking.location_footprint_sqft
    
    # Parking spaces equivalent
    parking_spaces_equivalent = total_footprint_sqft / parking.parking_space_sqft
    
    # Revenue impact (only for metered areas)
    spaces_in_metered = parking_spaces_equivalent * parking.pct_locations_in_metered_areas
    annual_revenue_impact = spaces_in_metered * parking.annual_parking_revenue_per_space
    
    return {
        "n_container_locations": int(n_locations),
        "total_footprint_sqft": total_footprint_sqft,
        "parking_spaces_equivalent": parking_spaces_equivalent,
        "spaces_in_metered_areas": spaces_in_metered,
        "annual_parking_revenue_impact": annual_revenue_impact,
        "pct_of_dc_street_parking": parking_spaces_equivalent / 17000 * 100  # DC has ~17k metered spaces
    }


def generate_cost_comparison(
    shared_capital: Dict,
    shared_operating: Dict,
    current: Dict,
    n_households: int,
    container_lifespan: int
) -> pd.DataFrame:
    """Generate comparison table of current vs shared system costs."""
    
    # Calculate 10-year total cost of ownership
    shared_10yr = (
        shared_capital["total_capital_cost"] + 
        shared_operating["total_annual_operating"] * 10
    )
    
    current_10yr = current["annual_costs"]["total"] * 10
    
    rows = [
        {
            "Category": "Upfront Capital Cost",
            "Current System": f"${current['capital_invested']['total']:,.0f}",
            "Shared System": f"${shared_capital['total_capital_cost']:,.0f}",
            "Difference": f"${shared_capital['total_capital_cost'] - current['capital_invested']['total']:+,.0f}"
        },
        {
            "Category": "Annual Operating Cost",
            "Current System": f"${current['annual_costs']['total']:,.0f}",
            "Shared System": f"${shared_operating['total_annual_operating']:,.0f}",
            "Difference": f"${shared_operating['total_annual_operating'] - current['annual_costs']['total']:+,.0f}"
        },
        {
            "Category": "Cost per Household (Annual)",
            "Current System": f"${current['cost_per_household']:,.0f}",
            "Shared System": f"${shared_operating['operating_cost_per_household']:,.0f}",
            "Difference": f"${shared_operating['operating_cost_per_household'] - current['cost_per_household']:+,.0f}"
        },
        {
            "Category": "10-Year Total Cost",
            "Current System": f"${current_10yr:,.0f}",
            "Shared System": f"${shared_10yr:,.0f}",
            "Difference": f"${shared_10yr - current_10yr:+,.0f}"
        },
        {
            "Category": "10-Year Savings",
            "Current System": "-",
            "Shared System": "-",
            "Difference": f"${current_10yr - shared_10yr:,.0f}" if current_10yr > shared_10yr else f"(${shared_10yr - current_10yr:,.0f})"
        }
    ]
    
    return pd.DataFrame(rows)


def print_cost_analysis(
    n_containers: int,
    n_households: int,
    pickup_frequency: int
):
    """Print comprehensive cost analysis."""
    
    # Initialize assumptions
    container_costs = ContainerCostAssumptions()
    truck_costs = TruckCostAssumptions()
    labor_costs = LaborCostAssumptions()
    current_costs = CurrentSystemCosts()
    transition_costs = TransitionCosts()
    parking = ParkingAssumptions()
    
    print("\n" + "=" * 80)
    print("COST & PARKING IMPACT MODEL")
    print("=" * 80)
    
    # Print assumptions
    print("\n" + "-" * 80)
    print("KEY ASSUMPTIONS")
    print("-" * 80)
    
    print(f"\nContainers:")
    print(f"  Unit cost: ${container_costs.container_unit_cost:,}")
    print(f"  Installation: ${container_costs.container_installation_cost:,}")
    print(f"  Annual maintenance: ${container_costs.container_annual_maintenance:,}")
    print(f"  Lifespan: {container_costs.container_lifespan_years} years")
    
    print(f"\nTrucks (Automated Side-Loader):")
    print(f"  Unit cost: ${truck_costs.truck_unit_cost:,}")
    print(f"  Containers per truck per day: {truck_costs.containers_per_truck_per_day}")
    print(f"  Annual fuel: ${truck_costs.annual_fuel_cost:,}")
    print(f"  Annual maintenance: ${truck_costs.annual_maintenance_cost:,}")
    
    print(f"\nLabor:")
    print(f"  Current system: {labor_costs.current_crew_size} workers per truck")
    print(f"  Shared system: {labor_costs.shared_crew_size} worker per truck (automated)")
    print(f"  Benefits multiplier: {labor_costs.benefits_multiplier}x")
    
    # Calculate costs
    capital = calculate_capital_costs(
        n_containers, n_households, container_costs, 
        truck_costs, transition_costs, pickup_frequency
    )
    
    operating = calculate_annual_operating_costs(
        n_containers, capital["trucks"]["n_trucks_needed"], n_households,
        pickup_frequency, container_costs, truck_costs, labor_costs
    )
    
    current = calculate_current_system_costs(n_households, current_costs, labor_costs)
    
    parking_impact = calculate_parking_impact(n_containers, parking)
    
    # Print capital costs
    print("\n" + "-" * 80)
    print("CAPITAL / STARTUP COSTS")
    print("-" * 80)
    
    print(f"\nContainers ({n_containers:,} units):")
    print(f"  Purchase: ${capital['containers']['purchase_cost']:,.0f}")
    print(f"  Installation: ${capital['containers']['installation_cost']:,.0f}")
    print(f"  Subtotal: ${capital['containers']['total']:,.0f}")
    
    print(f"\nTruck Fleet ({capital['trucks']['n_trucks_needed']} trucks):")
    print(f"  Purchase: ${capital['trucks']['purchase_cost']:,.0f}")
    
    print(f"\nTransition Costs:")
    print(f"  Old bin collection ({capital['transition']['old_bins_to_collect']:,} cans): ${capital['transition']['bin_collection_cost']:,.0f}")
    print(f"  Bin recycling credit: ${capital['transition']['bin_disposal_credit']:,.0f}")
    print(f"  Public outreach: ${capital['transition']['outreach_campaign']:,.0f}")
    print(f"  Signage: ${capital['transition']['signage']:,.0f}")
    print(f"  Subtotal: ${capital['transition']['total']:,.0f}")
    
    print(f"\n{'='*40}")
    print(f"TOTAL CAPITAL COST: ${capital['total_capital_cost']:,.0f}")
    print(f"Per Household: ${capital['capital_cost_per_household']:,.0f}")
    print(f"{'='*40}")
    
    # Print operating costs
    print("\n" + "-" * 80)
    print(f"ANNUAL OPERATING COSTS (at {pickup_frequency}x/week pickup)")
    print("-" * 80)
    
    print(f"\nContainer Maintenance: ${operating['container_maintenance']:,.0f}")
    
    print(f"\nTruck Operations:")
    print(f"  Fuel: ${operating['truck_operations']['fuel']:,.0f}")
    print(f"  Maintenance: ${operating['truck_operations']['maintenance']:,.0f}")
    print(f"  Insurance: ${operating['truck_operations']['insurance']:,.0f}")
    print(f"  Subtotal: ${operating['truck_operations']['total']:,.0f}")
    
    print(f"\nLabor:")
    print(f"  Shifts per week: {operating['labor']['shifts_per_week']}")
    print(f"  Hourly cost (w/ benefits): ${operating['labor']['hourly_cost_with_benefits']:.2f}")
    print(f"  Annual total: ${operating['labor']['annual_total']:,.0f}")
    
    print(f"\n{'='*40}")
    print(f"TOTAL ANNUAL OPERATING: ${operating['total_annual_operating']:,.0f}")
    print(f"Per Household: ${operating['operating_cost_per_household']:,.0f}")
    print(f"{'='*40}")
    
    # Print parking impact
    print("\n" + "-" * 80)
    print("PARKING / CURB SPACE IMPACT")
    print("-" * 80)
    
    print(f"\nContainer Locations: {parking_impact['n_container_locations']:,}")
    print(f"Total Footprint: {parking_impact['total_footprint_sqft']:,.0f} sq ft")
    print(f"Parking Spaces Equivalent: {parking_impact['parking_spaces_equivalent']:,.0f}")
    print(f"  In metered areas: {parking_impact['spaces_in_metered_areas']:,.0f}")
    print(f"  % of DC metered spaces: {parking_impact['pct_of_dc_street_parking']:.1f}%")
    print(f"Annual Parking Revenue Impact: ${parking_impact['annual_parking_revenue_impact']:,.0f}")
    
    # Print comparison
    print("\n" + "-" * 80)
    print("COMPARISON: CURRENT VS SHARED SYSTEM")
    print("-" * 80)
    
    comparison = generate_cost_comparison(
        capital, operating, current, n_households,
        container_costs.container_lifespan_years
    )
    print("\n" + comparison.to_string(index=False))
    
    # Key findings
    print("\n" + "-" * 80)
    print("KEY FINDINGS")
    print("-" * 80)
    
    annual_savings = current["annual_costs"]["total"] - operating["total_annual_operating"]
    payback_years = capital["total_capital_cost"] / annual_savings if annual_savings > 0 else float('inf')
    
    print(f"\n1. CAPITAL INVESTMENT:")
    print(f"   Total upfront cost: ${capital['total_capital_cost']:,.0f}")
    print(f"   Per household: ${capital['capital_cost_per_household']:,.0f}")
    
    print(f"\n2. OPERATING SAVINGS:")
    if annual_savings > 0:
        print(f"   Annual savings: ${annual_savings:,.0f}")
        print(f"   Savings per household: ${annual_savings/n_households:,.0f}")
    else:
        print(f"   Annual additional cost: ${-annual_savings:,.0f}")
    
    print(f"\n3. PAYBACK PERIOD:")
    if payback_years < 100:
        print(f"   Capital payback: {payback_years:.1f} years")
    else:
        print(f"   No payback (operating costs higher)")
    
    print(f"\n4. LABOR REDUCTION:")
    current_workers = labor_costs.current_crew_size * current_costs.trucks_in_fleet
    new_workers = labor_costs.shared_crew_size * capital['trucks']['n_trucks_needed']
    print(f"   Current system: ~{current_workers} collection workers")
    print(f"   Shared system: ~{new_workers} collection workers")
    print(f"   Reduction: {current_workers - new_workers} positions ({(current_workers-new_workers)/current_workers*100:.0f}%)")
    
    return capital, operating, current, parking_impact


def main():
    """Main entry point for cost model."""
    
    # Load data from previous tasks
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    processed_dir = project_root / "data" / "processed"
    
    # Load container count and assumptions
    try:
        with open(processed_dir / "placement_summary.json") as f:
            placement = json.load(f)
        n_containers = int(placement["overall"]["total_containers"])
        
        with open(processed_dir / "capacity_analysis.json") as f:
            capacity = json.load(f)
        n_households = capacity["assumptions"]["population"]["total_households"]
        pickup_frequency = capacity["minimum_frequencies"]["baseline"]
        
        print(f"Loaded from previous analyses:")
        print(f"  Containers: {n_containers:,}")
        print(f"  Households: {n_households:,}")
        print(f"  Pickup frequency: {pickup_frequency}x/week")
        
    except (FileNotFoundError, KeyError) as e:
        print(f"Warning: Could not load previous data ({e}), using defaults")
        n_containers = 18247
        n_households = 320000
        pickup_frequency = 3
    
    # Run analysis
    capital, operating, current, parking = print_cost_analysis(
        n_containers, n_households, pickup_frequency
    )
    
    # Build comparison summary with net cost difference and payback period
    annual_savings = current["annual_costs"]["total"] - operating["total_annual_operating"]
    payback_years = (
        capital["total_capital_cost"] / annual_savings
        if annual_savings > 0
        else float("inf")
    )
    comparison_summary = {
        "current_annual_operating_cost": current["annual_costs"]["total"],
        "shared_annual_operating_cost": operating["total_annual_operating"],
        "net_annual_cost_difference": annual_savings,
        "net_annual_cost_direction": "savings" if annual_savings > 0 else "increase",
        "net_cost_per_household": annual_savings / n_households,
        "shared_capital_cost": capital["total_capital_cost"],
        "payback_period_years": payback_years,
        "ten_year_shared_total": capital["total_capital_cost"] + operating["total_annual_operating"] * 10,
        "ten_year_current_total": current["annual_costs"]["total"] * 10,
        "ten_year_net_savings": current["annual_costs"]["total"] * 10 - (capital["total_capital_cost"] + operating["total_annual_operating"] * 10),
    }

    # Save results
    results = {
        "inputs": {
            "n_containers": n_containers,
            "n_households": n_households,
            "pickup_frequency": pickup_frequency
        },
        "assumptions": {
            "container": asdict(ContainerCostAssumptions()),
            "truck": asdict(TruckCostAssumptions()),
            "labor": asdict(LaborCostAssumptions()),
            "current_system": asdict(CurrentSystemCosts()),
            "transition": asdict(TransitionCosts()),
            "parking": asdict(ParkingAssumptions())
        },
        "capital_costs": capital,
        "annual_operating_costs": operating,
        "current_system_costs": current,
        "parking_impact": parking,
        "comparison": comparison_summary,
    }
    
    output_path = processed_dir / "cost_analysis.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n\nResults saved to: {output_path}")
    
    # Save comparison table
    comparison = generate_cost_comparison(
        capital, operating, current, n_households,
        ContainerCostAssumptions().container_lifespan_years
    )
    csv_path = processed_dir / "cost_comparison.csv"
    comparison.to_csv(csv_path, index=False)
    print(f"Comparison table saved to: {csv_path}")
    
    return results


if __name__ == "__main__":
    main()
