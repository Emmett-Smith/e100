# e100 - Flight Path & Parcel Locator

A lightweight, browser-based GIS toolkit designed to cross-reference flight logs with county parcel data. This application allows users to upload drone or aircraft flight paths, establish custom safety/buffer corridors, and query specific land parcel details (including unredacted owner names and parcel IDs) directly from the state's public registry.

---

## Features

* **Flight Path Mapping:** Upload `.kml` or `.kmz` flight logs to instantly visualize tracks on an interactive map.
* **Dynamic Buffer Radiuses:** Input a custom distance in meters to calculate and display a safety corridor polygon wrapping perfectly around the flight track.
* **Live Parcel Lookup:** Input coordinates in either Decimal Degrees (DD) or Degrees, Minutes, Seconds (DMS) to fetch real-time property data.
* **Data Fail-Safes:** Automatically cross-references spatial shapes (Layer 0) with the state tax registry (Layer 1) to recover missing Parcel IDs and unredacted owner names where available.

---

## How to Use the Web App

1. Open `index.html` in any modern web browser (or view via GitHub Pages).
2. **To Plot a Flight Corridor:**
   * Click **Choose File** under the Flight Path section and select your `.kml` or `.kmz` log.
   * Enter your desired safety radius in the **Buffer Radius (Meters)** field.
   * Click **Plot Corridor**. The map will automatically zoom and center on your flight track.
3. **To Look Up a Property Manually:**
   * Select your preferred format (DD or DMS) from the dropdown.
   * Enter the latitude and longitude coordinates.
   * Click **Locate Parcel**. The boundary will highlight in blue, and the sidebar table will populate with the owner's name, county, parcel ID, section, and township.

---

## Technical Details (How It Works)

This application is entirely front-end driven and runs 100% inside the user's browser. It skips the need for a local database or a Python backend by leveraging public web APIs and client-side geospatial libraries:

* **Map Interface:** Powered by **Leaflet.js** using OpenStreetMap tile layers.
* **File Parsing:** **JSZip** extracts compressed KMZ packages in browser memory, and Mapbox's **togeojson** converts raw KML XML trees into standard GeoJSON coordinates.
* **Geospatial Math:** **Turf.js** calculates the mathematically accurate buffer polygons around the line segments instantly.
* **Data Sources:** Real-time property boundaries and tax data are queried directly from the North Dakota GIS Hub Public ArcGIS REST Servers via asynchronous `fetch` requests.

---

## Project Structure

* `index.html` - The main application dashboard containing the user interface, CSS styling, and JavaScript architecture.
* `data/` - (Optional) Local directory for storing reference flight logs and backup datasets.
* `scripts/` - (Optional) Internal Python automation scripts used for bulk data scraping and offline reporting.
