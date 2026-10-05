"""Give every OEWS area and year the SPM threshold row that applies to it.

Order: (1) the SPM file names the metro under the same code; (2) the hand table in
data/ref/spm_oews_hand.csv (renumbered metros, and New England before 2024, where OEWS areas are
built from towns and the SPM file uses county-based metros); (3) the state's "Metro" row, which is
Census's figure for the smaller metros it does not name; (4) for nonmetro areas, the state's
"Nonmetro" row. An area with no published row is kept with kind "none"; nothing is guessed.
Output: data/processed/area_thresholds.csv"""
import pandas as pd

from common import PROC, REF

TEN = ["own_mort", "own_free", "rent"]


def main():
    o = pd.read_csv(PROC / "oews_areas.csv", dtype={"area": str, "state": str})
    s = pd.read_csv(PROC / "spm_thresholds.csv", dtype={"state": str})
    hand = pd.read_csv(REF / "spm_oews_hand.csv", dtype={"oews_area": str})
    rows = []
    for y, oy in o.groupby("year"):
        sy = s[s.year == y]
        named = sy[sy.kind == "metro"].set_index("code")
        st = {k: g.set_index("state") for k, g in sy[sy.kind != "metro"].groupby("kind")}
        h = hand[(hand.first_year <= y) & (hand.last_year >= y)].set_index("oews_area").spm_code
        used = set()
        for r in oy.itertuples():
            code, kind, how = None, "none", ""
            if r.area_type == 4:
                if int(r.area) in named.index:
                    code, kind, how = int(r.area), "metro", "code"
                elif r.area in h.index:
                    code, kind, how = int(h[r.area]), "metro", "hand"
                    assert code in named.index, f"{y}: hand table points at {code}, not in the SPM file"
                elif r.state in st["state_metro"].index:
                    code, kind, how = int(st["state_metro"].code[r.state]), "state_metro", "state"
            elif r.state in st["state_nonmetro"].index:
                code, kind, how = int(st["state_nonmetro"].code[r.state]), "state_nonmetro", "state"
            if kind == "metro":
                assert code not in used, f"{y}: SPM metro {code} assigned twice"
                used.add(code)
            src = sy.set_index("code").loc[code] if code is not None else None
            rows.append({"year": y, "area": r.area, "kind": kind, "how": how, "spm_code": code,
                         "spm_name": src["name"] if src is not None else "",
                         **{t: (int(round(src[t])) if src is not None else None) for t in TEN}})
        left = named[~named.index.isin(used)]
        if len(left):
            print(f"{y}: named SPM metros with no OEWS metro: {left.name.tolist()}")
    d = pd.DataFrame(rows)
    d["spm_code"] = d.spm_code.astype("Int64")
    for t in TEN:
        d[t] = d[t].astype("Int64")
    d.to_csv(PROC / "area_thresholds.csv", index=False)
    m = d.merge(o[["year", "area", "area_type", "title", "tot_emp"]], on=["year", "area"])
    print(m.groupby(["year", "kind"]).size().unstack(fill_value=0).to_string())
    none = m[m.kind == "none"]
    print("\nno published threshold row:")
    for t, g in none.groupby("title"):
        print(f"  {t}: {g.year.min()}-{g.year.max()} ({len(g)} yrs)")


if __name__ == "__main__":
    main()
