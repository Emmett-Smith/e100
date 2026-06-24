import matplotlib.pyplot as plt
from shapely.geometry import shape, mapping
from modules.kmz_reader import read_kmz
from modules.geometry import make_flight_line
from config import KMZ_FILE

def visualize_plan():
    print("Reading flight path coordinates from KMZ...")
    points = read_kmz(KMZ_FILE)
    
    # Generate the base line geometry
    flight_line = make_flight_line(points)
    
    # Isolate the hollow perimeter ring if it's a closed loop
    base_line = flight_line.boundary if hasattr(flight_line, "boundary") else flight_line
    
    # Calculate a half-mile buffer zone (1 half mile = ~804 meters)
    # 804 meters * 0.000009 degrees per meter = ~0.00723 degrees
    buffer_distance_degrees = 804 * 0.000009
    corridor_footprint = base_line.buffer(buffer_distance_degrees)
    
    # Setup the plot window
    fig, ax = plt.subplots(figsize=(10, 8))
    
    print("Plotting geometry layers...")
    
    # 1. Plot the solid corridor footprint (The half-mile wide belt)
    if hasattr(corridor_footprint, "exterior"):
        # Single polygon loop
        x, y = corridor_footprint.exterior.xy
        ax.fill(x, y, alpha=0.3, fc='skyblue', ec='blue', label='Half-Mile Flight Corridor Swath')
        # Plot internal hole boundary if it exists (the area skipped in the center)
        for interior in corridor_footprint.interiors:
            xi, yi = interior.xy
            ax.fill(xi, yi, alpha=1.0, fc='white', ec='blue')
    elif hasattr(corridor_footprint, "geoms"):
        # Multi-polygon fallback
        for geom in corridor_footprint.geoms:
            x, y = geom.exterior.xy
            ax.fill(x, y, alpha=0.3, fc='skyblue', ec='blue')
            
    # 2. 🌟 FIX: Extract coordinates safely using Shapely mapping to handle LinearRings
    geojson_line = mapping(base_line)
    if geojson_line['type'] in ['LineString', 'LinearRing']:
        coords = geojson_line['coordinates']
        x = [c[0] for c in coords]
        y = [c[1] for c in coords]
        ax.plot(x, y, color='red', linewidth=2.5, label='Actual Flight Track Perimeter')
    elif geojson_line['type'] == 'MultiLineString':
        for line_coords in geojson_line['coordinates']:
            x = [c[0] for c in line_coords]
            y = [c[1] for c in line_coords]
            ax.plot(x, y, color='red', linewidth=2.5)

    # 3. Plot the raw KMZ waypoint markers
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    ax.scatter(lons, lats, color='darkred', zorder=5, s=25, label='KMZ Key Waypoints')
    
    # Formatting the visual grid map
    ax.set_title("Visual Verification: Flight Track & Half-Mile Buffer Ribbon", fontsize=14, fontweight='bold')
    ax.set_xlabel("Longitude (Degrees Decimal)", fontsize=11)
    ax.set_ylabel("Latitude (Degrees Decimal)", fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    ax.set_aspect('equal', adjustable='box')
    
    print("\nDisplaying interactive flight map window...")
    print("💡 The white space in the dead center of the ring is being intentionally skipped!")
    plt.show()

if __name__ == "__main__":
    visualize_plan()