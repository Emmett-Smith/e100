import requests
import json
from shapely.geometry import shape, mapping

class ArcGISClient:
    def __init__(self):
        self.base_url = "https://services1.arcgis.com/GOcSXpzwBHyk2nog/arcgis/rest/services/NDGISHUB_Parcels/FeatureServer"
        self.geom_url = f"{self.base_url}/0/query"
        self.owner_table_url = f"{self.base_url}/1/query"

    def get_intersections(self, flight_line, buffer_meters=100):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Isolate the hollow track line
        base_line = flight_line.boundary if hasattr(flight_line, "boundary") else flight_line
        
        print(f"Generating local {buffer_meters}m corridor footprint...")
        degree_buffer = buffer_meters * 0.000009
        corridor_footprint = base_line.buffer(degree_buffer)

        # Unpack the raw track coordinates to chunk the requests spatially
        geojson_line = mapping(base_line)
        coords = []
        if geojson_line['type'] in ['LineString', 'LinearRing']:
            coords = geojson_line['coordinates']
        elif geojson_line['type'] == 'MultiLineString':
            for sub_line in geojson_line['coordinates']:
                coords.extend(sub_line)

        all_downloaded_features = []
        seen_object_ids = set()

        print(f"Scanning flight track in localized segments to prevent server truncation...")
        
        # Step through the track coordinates 3 waypoints at a time to create small, micro-envelopes
        step_size = 3
        for i in range(0, len(coords), step_size):
            segment_coords = coords[i:i + step_size + 1]
            if len(segment_coords) < 2:
                continue
                
            lons = [c[0] for c in segment_coords]
            lats = [c[1] for c in segment_coords]
            
            # Create a tight, small box around just this tiny piece of the flight path
            sub_envelope = {
                "xmin": min(lons) - degree_buffer - 0.001,
                "ymin": min(lats) - degree_buffer - 0.001,
                "xmax": max(lons) + degree_buffer + 0.001,
                "ymax": max(lats) + degree_buffer + 0.001,
                "spatialReference": {"wkid": 4326}
            }

            params = {
                "where": "1=1",
                "geometry": json.dumps(sub_envelope),
                "geometryType": "esriGeometryEnvelope",
                "spatialRel": "esriSpatialRelIntersects",
                "inSR": 4326,
                "outSR": 4326,
                "outFields": "*", 
                "returnGeometry": "true",
                "f": "json"
            }

            try:
                response = requests.post(self.geom_url, data=params, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    for feat in features:
                        obj_id = feat.get("attributes", {}).get("OBJECTID")
                        if obj_id and obj_id not in seen_object_ids:
                            seen_object_ids.add(obj_id)
                            all_downloaded_features.append(feat)
            except Exception:
                continue

        print(f"Successfully gathered {len(all_downloaded_features)} unique candidate parcels across all segments.")
        print("Applying precision corridor intersection filter locally...")
        
        intersecting_parcels = []
        unique_gis_ids = []

        for feature in all_downloaded_features:
            geometry_data = feature.get("geometry")
            attributes_data = feature.get("attributes", {})
            
            if geometry_data:
                try:
                    geo_json_format = {
                        "type": "Polygon",
                        "coordinates": geometry_data.get("rings", [])
                    }
                    parcel_shape = shape(geo_json_format)
                    
                    if corridor_footprint.intersects(parcel_shape):
                        intersecting_parcels.append(attributes_data)
                        ugisid = attributes_data.get("UniqueGISID")
                        if ugisid:
                            unique_gis_ids.append(str(ugisid).strip())
                except Exception:
                    continue

        total_found = len(intersecting_parcels)
        print(f"Identified {total_found} verified intersecting parcels. Syncing unredacted owner profiles from Layer 1...")
        
        if not unique_gis_ids:
            return []

        owner_lookup = {}
        id_chunk_size = 50
        
        for i in range(0, len(unique_gis_ids), id_chunk_size):
            chunk = unique_gis_ids[i:i + id_chunk_size]
            id_list_str = ",".join(f"'{uid}'" for uid in chunk)
            where_clause = f"UniqueGISID IN ({id_list_str})"
            
            table_payload = {
                "where": where_clause,
                "outFields": "UniqueGISID,OwnerName",
                "f": "json"
            }
            
            try:
                table_resp = requests.post(self.owner_table_url, data=table_payload, headers=headers, timeout=30)
                if table_resp.status_code == 200:
                    table_data = table_resp.json()
                    for feature in table_data.get("features", []):
                        attrs = feature.get("attributes", {})
                        ugisid = attrs.get("UniqueGISID")
                        if ugisid:
                            owner_lookup[str(ugisid).strip()] = attrs.get("OwnerName")
            except Exception:
                pass

        final_records = []
        for parcel in intersecting_parcels:
            ugisid = parcel.get("UniqueGISID")
            if ugisid:
                clean_id = str(ugisid).strip()
                if clean_id in owner_lookup:
                    parcel["OwnerName"] = owner_lookup[clean_id]
            final_records.append(parcel)

        print(f"Data sync complete! Exporting {len(final_records)} records.")
        return final_records
    
    def lookup_point(self, lat, lon):
        """
        Takes a single latitude and longitude coordinate and returns 
        the exact parcel attributes and owner information.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        # Structure the coordinate into an Esri Point object
        point_geom = {
            "x": float(lon), # Longitude is always X
            "y": float(lat), # Latitude is always Y
            "spatialReference": {"wkid": 4326}
        }

        params = {
            "where": "1=1",
            "geometry": json.dumps(point_geom),
            "geometryType": "esriGeometryPoint",
            "spatialRel": "esriSpatialRelIntersects", # Find what contains this point
            "inSR": 4326,
            "outSR": 4326,
            "outFields": "*",
            "returnGeometry": "true",
            "f": "json"
        }

        try:
            # 1. Find the parcel geometry and attributes
            resp = requests.post(self.geom_url, data=params, headers=headers, timeout=15)
            data = resp.json()
            features = data.get("features", [])
            
            if not features:
                return {"error": "Coordinates do not intersect any known parcel in North Dakota."}
                
            parcel_attr = features[0].get("attributes", {})
            parcel_geom = features[0].get("geometry", {})
            ugisid = parcel_attr.get("UniqueGISID")
            
            # 2. Go grab the unredacted owner name from Layer 1
            owner_name = "UNKNOWN"
            if ugisid:
                table_payload = {
                    "where": f"UniqueGISID = '{str(ugisid).strip()}'",
                    "outFields": "OwnerName",
                    "f": "json"
                }
                table_resp = requests.post(self.owner_table_url, data=table_payload, headers=headers, timeout=15)
                table_features = table_resp.json().get("features", [])
                if table_features:
                    owner_name = table_features[0].get("attributes", {}).get("OwnerName", "UNKNOWN")

            # Return a clean summary of the specific property
            return {
                "County": parcel_attr.get("CountyName"),
                "OwnerName": owner_name,
                "ParcelID": parcel_attr.get("ParcelID"),
                "UniqueGISID": ugisid,
                "Section": parcel_attr.get("Section"),
                "TownshipName": parcel_attr.get("TownshipName"),
                "Geometry": parcel_geom # We will need this later for the map!
            }
            
        except Exception as e:
            return {"error": f"API Search failed: {e}"}