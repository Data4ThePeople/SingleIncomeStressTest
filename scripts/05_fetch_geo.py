"""Download Census cartographic boundary files (1:500k) used to draw OEWS areas.

Counties, 2020 vintage: for May 2015 to May 2023 areas (Connecticut still has its eight counties).
Counties, 2024 vintage: for May 2024 and May 2025 areas (Connecticut planning regions).
County subdivisions, 2020, six New England states: OEWS areas there were built from towns before 2024.
States, 2024: outlines.
Output: data/raw/cb/"""
from common import NEW_ENGLAND, RAW, fetch

BASE = "https://www2.census.gov/geo/tiger/GENZ{y}/shp/{name}"
FILES = [(2020, "cb_2020_us_county_500k.zip"), (2024, "cb_2024_us_county_500k.zip"), (2024, "cb_2024_us_state_500k.zip")]
FILES += [(2020, f"cb_2020_{s}_cousub_500k.zip") for s in NEW_ENGLAND]

for y, name in FILES:
    print(name, "ok" if fetch(BASE.format(y=y, name=name), RAW / "cb" / name) else "NOT FOUND")
