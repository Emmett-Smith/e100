from modules.kmz_reader import read_kmz
from modules.geometry import make_flight_line
from modules.arcgis import ArcGISClient
from modules.excel import save

from config import KMZ_FILE
from config import OUTPUT_FILE

# 🌟 ADJUST YOUR RADIUS HERE (in meters)
BUFFER_RADIUS = 804 #half mile

def main():
    print("Reading KMZ...")
    points = read_kmz(KMZ_FILE)
    print(f"{len(points)} waypoints loaded.")

    flight_line = make_flight_line(points)

    client = ArcGISClient()
    
    print(f"Querying parcel server for intersections using a {BUFFER_RADIUS}m corridor...")
    # 🌟 PASS THE BUFFER VARIABLE STRAIGHT TO THE CLIENT HERE:
    parcels = client.get_intersections(flight_line, buffer_meters=BUFFER_RADIUS)
    
    # 🔍 DEBUG PRINTS ADDED HERE:
    print(f"Parcels found intersecting flight line: {len(parcels)}")
    print(f"Attempting to save to destination: {OUTPUT_FILE}")

    if len(parcels) > 0:
        save(parcels, OUTPUT_FILE)
        print("Finished saving successfully.")
    else:
        print("Skipping save because 0 parcels were returned.")


if __name__ == "__main__":
    main()