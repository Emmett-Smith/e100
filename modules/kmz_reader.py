import zipfile
import xml.etree.ElementTree as ET


def read_kmz(filename):
    """Extract waypoint coordinates from a KMZ file."""

    coords = []

    with zipfile.ZipFile(filename, "r") as kmz:

        # Find the KML file inside the KMZ
        kml_name = None
        for name in kmz.namelist():
            if name.endswith(".kml"):
                kml_name = name
                break

        if kml_name is None:
            raise RuntimeError("No KML file found inside KMZ.")

        kml_data = kmz.read(kml_name)

    root = ET.fromstring(kml_data)

    ns = {
        "kml": "http://www.opengis.net/kml/2.2"
    }

    for point in root.findall(".//kml:Point", ns):

        coord = point.find("kml:coordinates", ns)

        if coord is None or coord.text is None:
            continue

        text = coord.text.strip()
        lon, lat, *_ = text.split(",")

        coords.append((float(lon), float(lat)))

    return coords