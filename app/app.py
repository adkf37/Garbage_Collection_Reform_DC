"""
Task 06: Interactive Map Application

A Streamlit app that allows users to:
1. Enter a DC address and see their nearest shared container
2. Toggle distance threshold visualizations (250/500/750 ft)
3. Explore container locations across the city

Run with: streamlit run app/app.py
"""

import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import json
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
from scipy.spatial import cKDTree

# =============================================================================
# CONFIGURATION
# =============================================================================

# Distance thresholds in feet
DISTANCE_THRESHOLDS = [250, 500, 750]

# Map settings
DEFAULT_CENTER = [38.9072, -77.0369]  # DC center
DEFAULT_ZOOM = 12

# Colors for visualization
THRESHOLD_COLORS = {
    250: "#2ecc71",   # Green
    500: "#f1c40f",   # Yellow
    750: "#e74c3c"    # Red
}

# =============================================================================
# DATA LOADING (cached for performance)
# =============================================================================

@st.cache_data
def load_container_data():
    """Load container locations from processed data."""
    data_path = Path(__file__).parent.parent / "data" / "processed" / "container_locations.parquet"
    
    if not data_path.exists():
        st.error(f"Container data not found at {data_path}. Please run the placement algorithm first.")
        return None
    
    gdf = gpd.read_parquet(data_path)
    
    # Convert to WGS84 for mapping
    gdf_wgs84 = gdf.to_crs("EPSG:4326")
    
    # Extract coordinates
    gdf_wgs84["lat"] = gdf_wgs84.geometry.y
    gdf_wgs84["lon"] = gdf_wgs84.geometry.x
    
    return gdf_wgs84


@st.cache_data
def load_address_data():
    """Load address data for lookup."""
    data_path = Path(__file__).parent.parent / "data" / "raw" / "dc_addresses.parquet"
    
    if not data_path.exists():
        st.error(f"Address data not found at {data_path}. Please run the data fetch script first.")
        return None
    
    gdf = gpd.read_parquet(data_path)
    
    # Convert to WGS84
    gdf_wgs84 = gdf.to_crs("EPSG:4326")
    gdf_wgs84["lat"] = gdf_wgs84.geometry.y
    gdf_wgs84["lon"] = gdf_wgs84.geometry.x
    
    return gdf_wgs84


@st.cache_data
def load_analysis_summary():
    """Load analysis summaries for display."""
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    
    summaries = {}
    
    # Load placement summary
    placement_path = processed_dir / "placement_summary.json"
    if placement_path.exists():
        with open(placement_path) as f:
            summaries["placement"] = json.load(f)
    
    # Load capacity analysis
    capacity_path = processed_dir / "capacity_analysis.json"
    if capacity_path.exists():
        with open(capacity_path) as f:
            summaries["capacity"] = json.load(f)
    
    # Load cost analysis
    cost_path = processed_dir / "cost_analysis.json"
    if cost_path.exists():
        with open(cost_path) as f:
            summaries["cost"] = json.load(f)
    
    return summaries


@st.cache_data
def build_spatial_index(_containers_gdf):
    """Build spatial index for fast nearest-neighbor queries."""
    # Get coordinates in the projected CRS (feet) for accurate distance
    containers_proj = _containers_gdf.to_crs("EPSG:2248")
    coords = np.array([[p.x, p.y] for p in containers_proj.geometry])
    tree = cKDTree(coords)
    return tree, containers_proj


# =============================================================================
# ADDRESS LOOKUP
# =============================================================================

def find_address(addresses_gdf, search_text):
    """
    Find addresses matching the search text.
    
    Returns top 10 matches.
    """
    if addresses_gdf is None or len(search_text) < 3:
        return pd.DataFrame()
    
    # Simple text matching on ADDRESS column
    search_upper = search_text.upper()
    mask = addresses_gdf["ADDRESS"].str.contains(search_upper, na=False)
    
    matches = addresses_gdf[mask].head(10)
    return matches


def find_nearest_container(address_point, containers_tree, containers_proj, containers_wgs84):
    """
    Find the nearest container to an address point.
    
    Args:
        address_point: Shapely Point in WGS84
        containers_tree: cKDTree spatial index
        containers_proj: Containers GeoDataFrame in projected CRS
        containers_wgs84: Containers GeoDataFrame in WGS84
        
    Returns:
        Tuple of (nearest_container_row, distance_in_feet)
    """
    # Project the address point
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2248", always_xy=True)
    x, y = transformer.transform(address_point.x, address_point.y)
    
    # Query nearest neighbor
    distance, idx = containers_tree.query([x, y])
    
    nearest_container = containers_wgs84.iloc[idx]
    
    return nearest_container, distance


# =============================================================================
# MAP CREATION
# =============================================================================

def create_map(containers_gdf, center=None, zoom=None, selected_address=None, 
               nearest_container=None, distance_ft=None, show_threshold=500):
    """Create an interactive Folium map."""
    
    if center is None:
        center = DEFAULT_CENTER
    if zoom is None:
        zoom = DEFAULT_ZOOM
    
    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="cartodbpositron"
    )
    
    # Add container markers (clustered for performance)
    from folium.plugins import MarkerCluster
    
    container_cluster = MarkerCluster(name="Containers")
    
    # Only show a sample if too many containers
    sample_size = min(1000, len(containers_gdf))
    sample = containers_gdf.sample(sample_size, random_state=42) if len(containers_gdf) > sample_size else containers_gdf
    
    for _, row in sample.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            color="#3498db",
            fill=True,
            fillColor="#3498db",
            fillOpacity=0.7,
            popup=f"Container: {row['container_id']}<br>Ward: {row.get('ward', 'N/A')}<br>Addresses served: {row.get('addresses_served', 'N/A')}"
        ).add_to(container_cluster)
    
    container_cluster.add_to(m)
    
    # Add selected address marker
    if selected_address is not None:
        folium.Marker(
            location=[selected_address["lat"], selected_address["lon"]],
            popup=f"Your address: {selected_address['ADDRESS']}",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)
        
        # Draw distance circle
        if show_threshold:
            # Convert feet to meters for folium
            radius_m = show_threshold * 0.3048
            folium.Circle(
                location=[selected_address["lat"], selected_address["lon"]],
                radius=radius_m,
                color=THRESHOLD_COLORS.get(show_threshold, "#3498db"),
                fill=True,
                fillOpacity=0.2,
                popup=f"{show_threshold} ft radius"
            ).add_to(m)
    
    # Add nearest container marker
    if nearest_container is not None:
        folium.Marker(
            location=[nearest_container["lat"], nearest_container["lon"]],
            popup=f"Nearest container<br>Distance: {distance_ft:.0f} ft",
            icon=folium.Icon(color="green", icon="trash")
        ).add_to(m)
        
        # Draw line between address and container
        if selected_address is not None:
            folium.PolyLine(
                locations=[
                    [selected_address["lat"], selected_address["lon"]],
                    [nearest_container["lat"], nearest_container["lon"]]
                ],
                color="#2ecc71",
                weight=3,
                opacity=0.8
            ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m


# =============================================================================
# STREAMLIT APP
# =============================================================================

def main():
    st.set_page_config(
        page_title="DC Shared Container Finder",
        page_icon="🗑️",
        layout="wide"
    )
    
    st.title("🗑️ DC Shared Container System")
    st.markdown("Find your nearest shared waste container under the proposed Barcelona-style collection system.")
    
    # Load data
    with st.spinner("Loading data..."):
        containers = load_container_data()
        addresses = load_address_data()
        summaries = load_analysis_summary()
    
    if containers is None:
        st.error("Could not load container data. Please ensure the analysis scripts have been run.")
        return
    
    # Build spatial index
    containers_tree, containers_proj = build_spatial_index(containers)
    
    # Sidebar with summary stats
    with st.sidebar:
        st.header("📊 System Summary")
        
        if "placement" in summaries:
            placement = summaries["placement"]["overall"]
            st.metric("Total Containers", f"{int(placement['total_containers']):,}")
            st.metric("Addresses Covered", f"{int(placement['total_addresses_covered']):,}")
            st.metric("Avg Walking Distance", f"{placement['avg_max_distance_ft']:.0f} ft")
        
        if "cost" in summaries:
            cost = summaries["cost"]
            st.metric("Capital Cost", f"${cost['capital_costs']['total_capital_cost']/1e6:.1f}M")
            st.metric("Annual Savings", f"${(cost['current_system_costs']['annual_costs']['total'] - cost['annual_operating_costs']['total_annual_operating'])/1e6:.1f}M")
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        show_threshold = st.selectbox(
            "Distance Threshold",
            options=[250, 500, 750],
            index=1,
            format_func=lambda x: f"{x} ft"
        )
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔍 Find Your Container")
        
        # Address search
        search_text = st.text_input(
            "Enter your DC address",
            placeholder="e.g., 1600 Pennsylvania Ave NW"
        )
        
        selected_address = None
        nearest_container = None
        distance_ft = None
        
        if search_text and len(search_text) >= 3:
            matches = find_address(addresses, search_text)
            
            if len(matches) > 0:
                # Let user select from matches
                address_options = matches["ADDRESS"].tolist()
                selected_addr_text = st.selectbox(
                    "Select your address",
                    options=address_options
                )
                
                if selected_addr_text:
                    selected_address = matches[matches["ADDRESS"] == selected_addr_text].iloc[0]
                    
                    # Find nearest container
                    address_point = Point(selected_address["lon"], selected_address["lat"])
                    nearest_container, distance_ft = find_nearest_container(
                        address_point, containers_tree, containers_proj, containers
                    )
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📍 Results")
                    
                    # Distance indicator
                    if distance_ft <= 250:
                        distance_color = "🟢"
                        distance_status = "Excellent"
                    elif distance_ft <= 500:
                        distance_color = "🟡"
                        distance_status = "Good"
                    elif distance_ft <= 750:
                        distance_color = "🟠"
                        distance_status = "Acceptable"
                    else:
                        distance_color = "🔴"
                        distance_status = "Over threshold"
                    
                    st.metric(
                        "Distance to Nearest Container",
                        f"{distance_ft:.0f} ft",
                        delta=distance_status,
                        delta_color="normal" if distance_ft <= show_threshold else "inverse"
                    )
                    
                    st.write(f"{distance_color} **Status:** {distance_status}")
                    st.write(f"**Container ID:** {nearest_container['container_id']}")
                    st.write(f"**Ward:** {nearest_container.get('ward', 'N/A')}")
                    
                    # Walking time estimate (assuming 3 mph = 264 ft/min)
                    walk_time = distance_ft / 264
                    st.write(f"**Est. Walking Time:** {walk_time:.1f} min")
            else:
                st.warning("No matching addresses found. Try a different search.")
    
    with col2:
        st.subheader("🗺️ Map")
        
        # Determine map center
        if selected_address is not None:
            center = [selected_address["lat"], selected_address["lon"]]
            zoom = 16
        else:
            center = DEFAULT_CENTER
            zoom = DEFAULT_ZOOM
        
        # Create and display map
        m = create_map(
            containers,
            center=center,
            zoom=zoom,
            selected_address=selected_address,
            nearest_container=nearest_container,
            distance_ft=distance_ft,
            show_threshold=show_threshold
        )
        
        st_folium(m, width=None, height=500)
    
    # Additional info section
    st.markdown("---")
    st.subheader("ℹ️ About This System")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("""
        **How It Works**
        - Shared containers replace individual cans
        - 2-3 containers per block for trash, recycling, and compost
        - Automated trucks with single driver
        """)
    
    with col_b:
        st.markdown("""
        **Benefits**
        - Cleaner streets (no scattered cans)
        - Better recycling with separate streams
        - Flexible capacity (increase pickup frequency)
        """)
    
    with col_c:
        st.markdown("""
        **Distance Thresholds**
        - 🟢 250 ft - Excellent access
        - 🟡 500 ft - Good access
        - 🟠 750 ft - Acceptable access
        """)
    
    # Footer
    st.markdown("---")
    st.caption("DC Garbage Collection Reform Analysis | Data from DC Open Data")


if __name__ == "__main__":
    main()
