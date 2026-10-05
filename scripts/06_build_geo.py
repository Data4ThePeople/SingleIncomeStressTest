"""Build the shape of every OEWS area in each geography era.

BLS publishes, for each May estimate, the list of counties (or, in New England before 2024,
towns) that make up every metro and nonmetro area. Those lists are in data/ref/. Here the Census
cartographic boundary polygons of the member counties or towns are merged into one shape per
area, projected (Albers USA with Alaska and Hawaii insets), simplified and delta-encoded.
Output: data/processed/geo.json, data/processed/area_shapes.csv"""
import json
import re

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from albers import project
from common import ERAS, NEW_ENGLAND, PROC, RAW, REF, STATE_INFO

TOL = 250          # simplification tolerance, meters
GRID = 50          # coordinate grid, meters
SAME = 0.005       # two outlines are the same area if less than 0.5% of their combined land differs
MIN_PART = 0.05e6  # drop detached parts under 0.05 km2 after simplification (unless it is the only part)

# county codes in the BLS lists that the 2020 Census file carries under a newer code
COUNTY_FIX = {"02261": ["02063", "02066"], "02270": ["02158"], "46113": ["46102"], "51515": ["51019"], "12025": ["12086"],
              "02201": ["02198"], "02232": ["02230", "02105"], "02280": ["02275", "02195"]}
TOWN_WORDS = r"\b(town|city|borough|plantation|township|unorganized|territory|gore|grant|location|purchase|village|ut)\b"


def key(s):
    return s.astype(str).str.strip().str.lstrip("0")


def norm(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def base(s):
    """Town name without its type word, for the second matching pass."""
    return norm(re.sub(TOWN_WORDS, "", str(s).lower()))


def definitions(fname):
    """One row per county or New England town: area, state, county (5-digit), town code, name."""
    d = pd.read_excel(REF / fname, dtype=str)
    d.columns = [c.strip() for c in d.columns]
    code = next(c for c in d.columns if c.startswith("MSA code (incl") or c.endswith("MSA code") or c == "new_area")
    area = d[code]
    if "MSA code for MSAs with divisions" in d.columns:   # the 2016 list shows divisions; OEWS type 4 rows are the full metro
        area = d["MSA code for MSAs with divisions"].fillna(area)
    st = (d["FIPS code"] if "FIPS code" in d.columns else d["FIPS"]).str.zfill(2)
    name = d[next(c for c in d.columns if c.startswith("County name"))].str.strip()
    twp = d["Township code"].fillna("000").str.zfill(3) if "Township code" in d.columns else "000"
    out = pd.DataFrame({"area": key(area), "state": st, "county": st + d["County code"].str.zfill(3), "twp": twp, "name": name})
    return out[out.state.isin(STATE_INFO)].drop_duplicates()


def prep(geom, st):
    g = shapely.simplify(project(shapely.make_valid(geom), st), TOL, preserve_topology=True)
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty]
    if len(parts) > 1:
        big = [p for p in parts if p.area >= MIN_PART]
        parts = big or [max(parts, key=lambda p: p.area)]
    return parts


def encode(parts):
    """[[ring, ring...], ...] with each ring a flat delta-encoded int list on the GRID."""
    out = []
    for p in parts:
        rings = []
        for ring in [p.exterior, *p.interiors]:
            xy = np.round(np.asarray(ring.coords)[:-1] / GRID).astype(np.int64)
            keep = np.r_[True, np.any(np.diff(xy, axis=0) != 0, axis=1)]
            xy = xy[keep]
            if len(xy) < 3:
                continue
            d = np.vstack([xy[:1], np.diff(xy, axis=0)])
            d[:, 1] *= -1  # screen y points down
            rings.append(d.ravel().tolist())
        if rings:
            out.append(rings)
    return out


def town_areas(d, towns):
    """Area for every Census town in New England, from the BLS town list.
    Pass 1: same county and full name. Pass 2: same county and name without the type word
    (BLS says "Bridgeport city", Census "Bridgeport town"). Pass 3: the county has only one area.
    Pass 4: the area of the matched town it shares the longest border with (BLS lists Maine's
    unorganized territories under older names). Passes 3 and 4 place land for drawing only."""
    t = d[d.twp != "000"]
    full = {r.county + norm(r.name): r.area for r in t.itertuples()}
    short = {}
    for r in t.itertuples():
        short.setdefault(r.county + base(r.name), set()).add(r.area)
    one = t.groupby("county").area.agg(lambda x: x.iloc[0] if x.nunique() == 1 else None).dropna()
    out, tier = {}, {1: 0, 2: 0, 3: 0, 4: 0}
    for r in towns.itertuples():
        c = r.STATEFP + r.COUNTYFP
        if r.k in full:
            out[r.Index], n = full[r.k], 1
        elif len(short.get(c + base(r.NAME), ())) == 1:
            out[r.Index], n = next(iter(short[c + base(r.NAME)])), 2
        elif c in one.index:
            out[r.Index], n = one[c], 3
        else:
            continue
        tier[n] += 1
    todo = [i for i in towns.index if i not in out]
    while todo:
        done = pd.Series(out)
        tree = shapely.STRtree(towns.geometry[done.index].values)
        left = []
        for i in todo:
            g = towns.geometry[i]
            best = {}
            for j in tree.query(g, predicate="intersects"):
                best[done.iloc[j]] = best.get(done.iloc[j], 0) + shapely.intersection(g, tree.geometries[j]).length
            if best:
                out[i] = max(best, key=best.get)
                tier[4] += 1
            else:
                left.append(i)
        if len(left) == len(todo):                    # islands: take the nearest matched town
            for i in left:
                out[i] = done.iloc[tree.nearest(towns.geometry[i])]
                tier[4] += 1
            left = []
        todo = left
    return out, tier


def main():
    oews = pd.read_csv(PROC / "oews_areas.csv", dtype={"area": str})
    oews["key"] = key(oews.area)
    cty = {v: gpd.read_file(f"zip://{RAW / 'cb' / f'cb_{v}_us_county_500k.zip'}").set_index("GEOID").geometry for v in (2020, 2024)}
    towns = pd.concat([gpd.read_file(f"zip://{RAW / 'cb' / f'cb_2020_{s}_cousub_500k.zip'}") for s in NEW_ENGLAND], ignore_index=True)
    towns["k"] = towns.STATEFP + towns.COUNTYFP + towns.NAMELSAD.map(norm)
    assert not towns.k.duplicated().any()

    eras, shape_rows, prev, next_id = [], [], {}, 0
    for a, b, fname, patch in ERAS:
        d = definitions(fname)
        d["area"] = d.county.map(patch).fillna(d.area)
        counties = cty[2024] if a >= 2024 else cty[2020]
        pieces, miss = {}, []
        st_of = d.groupby("area").state.first()
        for r in d[d.twp == "000"].itertuples():
            ids = COUNTY_FIX.get(r.county, [r.county]) if a < 2024 else [r.county]
            if all(i in counties.index for i in ids):
                pieces.setdefault(r.area, []).extend(counties[i] for i in ids)
            else:
                miss.append((r.area, r.county, r.name))
        tier = {}
        if (d.twp != "000").any():
            ta, tier = town_areas(d, towns)
            for i, area in ta.items():
                pieces.setdefault(area, []).append(towns.geometry[i])
        print(f"{a}-{b} {fname}: {d.area.nunique()} areas; counties not found: {miss}; towns matched by pass: {tier}")
        whole = {k: shapely.make_valid(shapely.union_all(v)) for k, v in pieces.items()}
        geo = {k: encode(prep(g, st_of[k])) for k, g in whole.items()}
        # shape id: an area keeps its id across eras only while its outline stays the same (under SAME of its area differs)
        cur = {}
        for k, g in whole.items():
            old = prev.get(k)
            if old is not None and shapely.symmetric_difference(g, old[1]).area <= SAME * shapely.union(g, old[1]).area:
                cur[k] = (old[0], g)
            else:
                cur[k] = (next_id, g)
                next_id += 1
            shape_rows.append({"era_from": a, "era_to": b, "area": k, "shape_id": cur[k][0]})
        prev = cur
        need = set(oews[(oews.year >= a) & (oews.year <= b)].key)
        nogeo = sorted(need - set(geo))
        assert not nogeo, f"OEWS areas without a shape: {nogeo}"
        print(f"  OEWS areas with data {len(need)}, all have a shape; shapes with no data: {sorted(set(geo) - need)}")
        eras.append({"from": a, "to": b, "geo": {k: geo[k] for k in sorted(need)}})

    st = gpd.read_file(f"zip://{RAW / 'cb' / 'cb_2024_us_state_500k.zip'}")
    st = st[st.STATEFP.isin(STATE_INFO)]
    borders = [encode(prep(g, s)) for g, s in zip(st.geometry, st.STATEFP)]
    pd.DataFrame(shape_rows).to_csv(PROC / "area_shapes.csv", index=False)
    dest = PROC / "geo.json"
    dest.write_text(json.dumps({"grid": GRID, "eras": eras, "borders": borders}, separators=(",", ":")))
    print(f"wrote {dest.name}: {dest.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
