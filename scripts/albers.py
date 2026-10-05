"""Albers USA composite projection (lower 48 + Alaska and Hawaii insets), like d3.geoAlbersUsa.
Output units are meters in the lower-48 Albers plane; the insets are moved into the lower left."""
import shapely
from pyproj import Transformer

_L48 = Transformer.from_crs("EPSG:4269", "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +datum=NAD83", always_xy=True)
_AK = Transformer.from_crs("EPSG:4269", "+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 +lon_0=-154 +datum=NAD83", always_xy=True)
_HI = Transformer.from_crs("EPSG:4269", "+proj=aea +lat_1=8 +lat_2=18 +lat_0=13 +lon_0=-157 +datum=NAD83", always_xy=True)
# scale and offset (meters) for each inset. Both sit in the open space south of Arizona and New Mexico,
# inside the lower 48's own bounding box, so the insets do not make the map any taller or wider.
_INSET = {"02": (_AK, 0.28, (-1_718_000, -1_386_000)), "15": (_HI, 1.0, (-700_000, -1_980_000))}
# Hawaii is drawn from Niihau to the Big Island. The uninhabited Northwestern Hawaiian Islands, which
# belong to Honolulu County and stretch 2,000 km west, are left off.
_HI_BOX = shapely.box(-161.0, 18.0, -154.0, 23.0)


def project(geom, statefp):
    """Project a lon/lat shapely geometry into the composite plane."""
    tr, k, (dx, dy) = _INSET.get(statefp, (_L48, 1.0, (0, 0)))
    if statefp == "15":
        geom = shapely.intersection(geom, _HI_BOX)

    def f(coords):
        x, y = tr.transform(coords[:, 0], coords[:, 1])
        coords[:, 0] = x * k + dx
        coords[:, 1] = y * k + dy
        return coords

    return shapely.transform(geom, f)
