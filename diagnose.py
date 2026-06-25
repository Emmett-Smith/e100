# import requests
# import json

# def run_diagnostic():
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
#     }
    
#     base_url = "https://services1.arcgis.com/GOcSXpzwBHyk2nog/arcgis/rest/services/NDGISHUB_Parcels/FeatureServer"
    
#     print("=== DIAGNOSTIC 1: Checking Server Limits & Schema ===")
#     try:
#         # Check metadata for Layer 0 and Layer 1
#         for layer_id in [0, 1]:
#             meta_resp = requests.get(f"{base_url}/{layer_id}?f=json", headers=headers, timeout=15)
#             meta_data = meta_resp.json()
#             name = meta_data.get("name", "Unknown")
#             max_records = meta_data.get("maxRecordCount", "Unknown")
#             print(f"Layer {layer_id} ('{name}'): Max Record Count Allowed = {max_records}")
#     except Exception as e:
#         print(f"Failed to fetch layer metadata: {e}")

#     print("\n=== DIAGNOSTIC 2: Fetching Sample Parcels from Layer 0 ===")
#     # Let's pull 3 sample features specifically from Pembina County to inspect the raw field names
#     params_l0 = {
#         "where": "CountyName = 'Pembina'",
#         "resultRecordCount": 3,
#         "outFields": "*",
#         "f": "json"
#     }
    
#     sample_unique_id = None
#     try:
#         resp_l0 = requests.post(f"{base_url}/0/query", data=params_l0, headers=headers, timeout=15)
#         data_l0 = resp_l0.json()
#         features = data_l0.get("features", [])
        
#         print(f"Successfully grabbed {len(features)} sample records from Layer 0.")
#         if features:
#             attrs = features[0].get("attributes", {})
#             print("\nAvailable attributes in Layer 0 (Sample 1):")
#             for k, v in attrs.items():
#                 print(f"  {k}: {v}")
#                 if k == "UniqueGISID" and v:
#                     sample_unique_id = v
#     except Exception as e:
#         print(f"Failed to query Layer 0: {e}")

#     print("\n=== DIAGNOSTIC 3: Testing Layer 1 Cross-Reference ===")
#     if not sample_unique_id:
#         # Hardcoded fallback sample from your previous network logs if the query failed
#         sample_unique_id = "38067-23-0480000"
        
#     print(f"Attempting to look up Owner data for UniqueGISID: '{sample_unique_id}' inside Layer 1...")
    
#     params_l1 = {
#         "where": f"UniqueGISID = '{sample_unique_id}'",
#         "outFields": "*",
#         "f": "json"
#     }
    
#     try:
#         resp_l1 = requests.post(f"{base_url}/1/query", data=params_l1, headers=headers, timeout=15)
#         data_l1 = resp_l1.json()
#         features_l1 = data_l1.get("features", [])
        
#         print(f"Layer 1 returned {len(features_l1)} matching rows.")
#         if features_l1:
#             print("\nAvailable attributes found inside Layer 1:")
#             attrs_l1 = features_l1[0].get("attributes", {})
#             for k, v in attrs_l1.items():
#                 print(f"  {k}: {v}")
#         else:
#             print("⚠️ Layer 1 returned NO records. The string index match failed.")
#             print("Let's try a wildcard search instead...")
            
#             params_l1_wildcard = {
#                 "where": f"UniqueGISID LIKE '{sample_unique_id}%'",
#                 "outFields": "*",
#                 "f": "json"
#             }
#             resp_l1_w = requests.post(f"{base_url}/1/query", data=params_l1_wildcard, headers=headers, timeout=15)
#             features_w = resp_l1_w.json().get("features", [])
#             print(f"Wildcard search returned {len(features_w)} rows.")
#             if features_w:
#                 for k, v in features_w[0].get("attributes", {}).items():
#                     print(f"  [Wildcard Match] {k}: {v}")
                    
#     except Exception as e:
#         print(f"Failed to query Layer 1: {e}")

# if __name__ == "__main__":
#     run_diagnostic()





import requests
import json

def check_cavalier_county():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    # Let's count how many total parcels exist in the database for ACTUAL Cavalier County
    url = "https://services1.arcgis.com/GOcSXpzwBHyk2nog/arcgis/rest/services/NDGISHUB_Parcels/FeatureServer/0/query"
    
    params = {
        "where": "CountyName = 'Cavalier'",
        "returnCountOnly": "true",
        "f": "json"
    }
    
    try:
        resp = requests.post(url, data=params, headers=headers, timeout=15)
        count = resp.json().get("count", 0)
        print(f"Database check: There are {count} total parcels belonging to 'Cavalier' County in the state database.")
        
        # Let's see if the server uses a different name variation like "Cavalier County"
        params["where"] = "CountyName LIKE 'Cavalier%'"
        resp2 = requests.post(url, data=params, headers=headers, timeout=15)
        print(f"Wildcard check ('Cavalier%'): Found {resp2.json().get('count', 0)} parcels.")
        
    except Exception as e:
        print(f"Error checking county records: {e}")

if __name__ == "__main__":
    check_cavalier_county()