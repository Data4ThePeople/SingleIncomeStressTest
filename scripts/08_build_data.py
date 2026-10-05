"""Build the map data file: wages, thresholds and shapes for every OEWS area and year.
Output: data/processed/map_data.json"""
import json

import pandas as pd

from common import ERAS, PCTS, PROC, STATE_INFO, YEARS

TEN = ["rent", "own_mort", "own_free"]
KIND = {"metro": "m", "state_metro": "s", "state_nonmetro": "n", "none": "x"}


def main():
    o = pd.read_csv(PROC / "oews_areas.csv", dtype={"area": str, "state": str})
    t = pd.read_csv(PROC / "area_thresholds.csv", dtype={"area": str})
    d = o.merge(t, on=["year", "area"], validate="one_to_one")
    # our rent-based estimate, kept only for metros with no Census figure of their own
    est = pd.read_csv(PROC / "acs_thresholds.csv", dtype={"area": str})[["year", "area", "rent2br"] + ["est_" + c for c in TEN]]
    d = d.merge(est, on=["year", "area"], how="left", validate="one_to_one")
    d["id"] = d.area.str.lstrip("0")
    assert not d.duplicated(["year", "id"]).any(), "duplicate (year, area)"
    shapes = pd.read_csv(PROC / "area_shapes.csv", dtype={"area": str})
    shape = {(y, r.area): r.shape_id for r in shapes.itertuples() for y in range(r.era_from, r.era_to + 1)}
    geo = json.loads((PROC / "geo.json").read_text())
    nat = pd.read_csv(PROC / "spm_national.csv").set_index("year")
    yi = {y: i for i, y in enumerate(YEARS)}
    n = len(YEARS)

    areas = []
    for aid, g in d.groupby("id"):
        g = g.sort_values("year")
        last = g.iloc[-1]
        a = {"id": aid, "n": last.title, "t": int(last.area_type), "s": last.state,
             "w": [None] * n, "e": [None] * n, "th": [None] * n, "k": [None] * n, "sp": [None] * n, "sh": [None] * n, "est": [None] * n, "r2": [None] * n}
        assert g.state.nunique() == 1, f"{aid}: principal state changes"
        for r in g.itertuples():
            i = yi[r.year]
            a["w"][i] = [int(getattr(r, p)) for p in PCTS]
            a["e"][i] = None if pd.isna(r.tot_emp) else int(r.tot_emp)
            a["k"][i] = KIND[r.kind]
            if r.kind != "none":
                a["th"][i] = [int(getattr(r, c)) for c in TEN]
                a["sp"][i] = r.spm_name
            if r.kind in ("state_metro", "none") and pd.notna(r.rent2br):
                a["est"][i] = [int(getattr(r, "est_" + c)) for c in TEN]
                a["r2"][i] = int(r.rent2br)
            a["sh"][i] = int(shape[(r.year, aid)])
        areas.append(a)

    out = {"years": YEARS, "grid": geo["grid"], "states": STATE_INFO,
           "nat": [[int(nat.loc[y, c]) for c in TEN] for y in YEARS],
           "acs": [f"{max(y - 1, 2015) - 4} to {max(y - 1, 2015)}" for y in YEARS],
           "eras": [{"from": e["from"], "to": e["to"], "geo": e["geo"]} for e in geo["eras"]],
           "borders": geo["borders"], "areas": areas}
    for e in out["eras"]:      # every area with data in an era has a shape, and the reverse
        need = {a["id"] for a in areas if any(a["w"][yi[y]] for y in range(e["from"], e["to"] + 1))}
        assert need == set(e["geo"]), f"{e['from']}: data and shapes differ"
    dest = PROC / "map_data.json"
    dest.write_text(json.dumps(out, separators=(",", ":")))
    full = sum(1 for a in areas if all(a["w"]) and len(set(a["sh"])) == 1)
    print(f"wrote {dest.name}: {dest.stat().st_size / 1e6:.1f} MB; {len(areas)} areas ever, {len(ERAS)} shape sets; "
          f"{full} areas have all {n} years on one unchanged outline")


if __name__ == "__main__":
    main()
