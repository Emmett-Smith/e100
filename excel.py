import pandas as pd

def save(parcels, output_file):
    print("Formatting parcel records and cleaning columns...")
    
    cleaned_records = []
    
    for parcel in parcels:
        # Check Layer 1 OwnerName first, fallback to Layer 0 fields if necessary
        owner_name = parcel.get("OwnerName") or parcel.get("Ownership") or parcel.get("OWNER_NAME") or "UNKNOWN"
        if str(owner_name).strip().upper() == "NONE":
            owner_name = "UNKNOWN"
            
        # Extract standard structural identifiers
        gis_id = parcel.get("GISID") or parcel.get("UniqueGISID") or "N/A"
        unique_gis_id = parcel.get("UniqueGISID") or "N/A"
        county = parcel.get("CountyName") or "N/A"
        section = parcel.get("Section") or parcel.get("SectionNumber") or "N/A"
        township = parcel.get("Township") or parcel.get("TownshipNumber") or "N/A"
        range_num = parcel.get("Range") or parcel.get("RangeNumber") or "N/A"
        twp_name = parcel.get("TownshipName") or "N/A"
        
        # Handle acreage gracefully
        acres = parcel.get("CalculatedAcres") or parcel.get("Acres") or 0.0
        try:
            acres = round(float(acres), 2)
        except (ValueError, TypeError):
            acres = "N/A"

        cleaned_records.append({
            "County": county,
            "Owner Name": str(owner_name).strip(),
            "Parcel ID / GISID": gis_id,
            "Unique GISID": unique_gis_id,
            "Section": section,
            "Township": township,
            "Range": range_num,
            "Township Name": twp_name,
            "Calculated Acres": acres
        })
        
    df = pd.DataFrame(cleaned_records)
    
    if not df.empty and "County" in df.columns:
        df = df.sort_values(by=["County", "Township Name", "Section"]).reset_index(drop=True)
    
    try:
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Flight Corridor Owners')
        
        workbook = writer.book
        worksheet = writer.sheets['Flight Corridor Owners']
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
        writer.close()
        print(f"📊 Spreadsheet saved cleanly with unified owner tracking format.")
    except Exception as e:
        print(f"❌ Error compiling Excel formatting engines: {e}")
        fallback_csv = output_file.replace(".xlsx", ".csv")
        df.to_csv(fallback_csv, index=False)
        print(f"⚠️ Saved clean backup format to: {fallback_csv}")