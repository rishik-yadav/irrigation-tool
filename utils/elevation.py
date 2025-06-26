import requests
import numpy as np
from shapely.geometry import shape, Point
import random

def sample_points_in_polygon(polygon_geojson, n_points=30):
    geom = shape(polygon_geojson['geometry'])
    minx, miny, maxx, maxy = geom.bounds
    points = []

    while len(points) < n_points:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if geom.contains(p):
            points.append((p.y, p.x))
    return points

def get_elevation_profile(polygon_geojson):
    sample_points = sample_points_in_polygon(polygon_geojson, n_points=30)
    elevations = []

    for lat, lon in sample_points:
        try:
            url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
            r = requests.get(url)
            if r.status_code == 200:
                result = r.json()
                elevations.append(result['results'][0]['elevation'])
        except Exception:
            continue

    return float(min(elevations)), float(max(elevations))