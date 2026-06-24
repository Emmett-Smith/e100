
# Flight Corridor Parcel Matcher

A Python utility and web interface to map flight paths against local parcel data. The system reads flight track waypoints, applies a buffer zone, and queries public state GIS registries to pull down ownership details for properties along the flight corridor.

After downloading files, run main.py for it all to work

## Project Structure

```text
├── config.py             # Global configurations (File paths, distances)
├── main.py               # Main pipeline execution script
├── diagnose_api.py       # API connection test script
├── requirements.txt      # Python dependencies
├── modules/
│   ├── kmz_reader.py     # Parses KMZ files for waypoints
│   ├── geometry.py       # Builds spatial tracks using Shapely
│   ├── arcgis.py         # Handles paginated queries to ArcGIS endpoints
│   └── excel.py          # Exports data to Excel spreadsheets
└── website/
    └── index.html        # Interactive map interface (HTML/JS)
```
