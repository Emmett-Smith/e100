from shapely.geometry import LineString, Point
from shapely.ops import transform
import pyproj

def make_flight_line(points):
    # 1. Force the input points into explicit coordinate tuples (X, Y)
    coord_pairs = []
    for pt in points:
        if isinstance(pt, (list, tuple)):
            coord_pairs.append((pt[0], pt[1]))
        elif hasattr(pt, 'x') and hasattr(pt, 'y'):
            coord_pairs.append((pt.x, pt.y))
        else:
            coord_pairs.append(pt)

    if len(coord_pairs) < 2:
        print("⚠️ Warning: Not enough waypoints to construct a continuous line track. Using raw points.")
        return Point(coord_pairs[0]) if coord_pairs else None

    # 2. Construct a single continuous connecting flight track line
    continuous_line = LineString(coord_pairs)
    
    # 3. Project to a meter-based coordinate system (UTM Zone 14N covers North Dakota)
    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('EPSG:32614')
    
    project_to_meters = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    project_back_to_deg = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True).transform
    
    line_meters = transform(project_to_meters, continuous_line)
    
    # 4. Create a 50-meter wide corridor on both sides of the flight track (100m total width)
    buffered_meters = line_meters.buffer(50) 
    
    # 5. Convert the polygon corridor back to Lat/Long degrees for the server query
    return transform(project_back_to_deg, buffered_meters)

def bounding_box(line):
    xmin, ymin, xmax, ymax = line.bounds
    return xmin, ymin, xmax, ymax