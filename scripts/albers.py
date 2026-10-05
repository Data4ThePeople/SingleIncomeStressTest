"""Albers USA composite projection (lower 48 + Alaska and Hawaii insets), like d3.geoAlbersUsa.
Output units are meters in the lower-48 Albers plane; the insets are moved into the lower left."""
import shapely
from pyproj import Transformer

_L48 = Transformer.from_crs("EPSG:4269", "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +datum=NAD83", always_xy=True)
_AK = Transformer.from_crs("EPSG:4269", "+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 +lon_0=-154 +datum=NAD83", always_xy=True)
_HI = Transformer.from_crs("EPSG:4269", "+proj=aea +lat_1=8 +lat_2=18 +lat_0=13 +lon_0=-157 +datum=NAD83", always_xy=True)
# scale and offset (meters) for each inset, tuned so the insets sit below the Southwest
_INSET = {"02": (_AK, 0.28, (-1_900_000, -2_250_000)), "15": (_HI, 1.0, (-700_000, -2_100_000))}


def project(geom, statefp):
    """Project a lon/lat shapely geometry into the composite plane."""
    tr, k, (dx, dy) = _INSET.get(statefp, (_L48, 1.0, (0, 0)))

    def f(coords):
        x, y = tr.transform(coords[:, 0], coords[:, 1])
        coords[:, 0] = x * k + dx
        coords[:, 1] = y * k + dy
        return coords

    return shapely.transform(geom, f)
