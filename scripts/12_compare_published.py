"""Compare the published Tableau version (May 2024, exported by Eric to data/<n>pct.csv) with this
build: wage at each percentile, the renter threshold, and the result with a $10,000 cushion.
Differences are listed with the Census row each side used. Output: data/processed/published_diff.csv"""
import json

import pandas as pd

from common import PROC, ROOT

FILES = {"10pct": 0, "25pct": 1, "50pct": 2, "75pct": 3, "90pct": 4}
KIND = {"m": "named metro", "s": "state smaller-metro figure", "n": "state nonmetro figure", "x": "none published"}


def money(s):
    return pd.to_numeric(s.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")


def main():
    D = json.loads((PROC / "map_data.json").read_text())
    i = D["years"].index(2024)
    ours = {a["id"]: a for a in D["areas"] if a["w"][i]}
    spm = pd.read_csv(PROC / "spm_thresholds.csv")
    spm = spm[spm.year == 2024]
    by_rent = spm.groupby(spm.rent.round().astype(int)).name.apply(lambda x: " / ".join(x)).to_dict()
    pub = {}
    for f, p in FILES.items():
        d = pd.read_csv(ROOT / "data" / f"{f}.csv", sep="\t", encoding="utf-16", dtype=str)
        d.columns = ["pct", "area", "name", "earn", "earn_plus", "result", "cushion", "spm"]
        for c in ["earn", "earn_plus", "result", "cushion", "spm"]:
            d[c] = money(d[c])
        assert not d.area.duplicated().any(), f"{f}: duplicate area"
        assert (d.cushion == 10000).all()
        bad = d[(d.earn - d.spm - d.cushion - d.result).abs() > 1]
        print(f"{f}: {len(d)} areas; rows where earnings - threshold - cushion is not the published result: {len(bad)}")
        pub[p] = d.set_index("area")
    ids = set(pub[2].index)
    for p in pub:
        assert set(pub[p].index) == ids, "the five files list different areas"
        assert (pub[p].spm == pub[2].spm).all(), "threshold differs between percentile files"
    print(f"\npublished areas: {len(ids)}; in this build for 2024: {len(ours)} "
          f"({sum(a['t'] == 4 for a in ours.values())} metro, {sum(a['t'] == 6 for a in ours.values())} nonmetro)")
    print("published but not in this build:", sorted((k, pub[2].name[k]) for k in ids - set(ours)))
    new = [a for k, a in ours.items() if k not in ids]
    print(f"in this build but not published: {sum(a['t'] == 6 for a in new)} nonmetro areas and these metros: "
          f"{sorted(a['n'] for a in new if a['t'] == 4)}")

    rows = []
    for k in sorted(ids & set(ours)):
        a = ours[k]
        w = [int(pub[p].earn[k]) for p in range(5)]
        wage_diff = [f"{['10th', '25th', '50th', '75th', '90th'][p]}: published {w[p]:,}, source {a['w'][i][p]:,}" for p in range(5) if w[p] != a["w"][i][p]]
        pt = int(pub[2].spm[k])
        ct = a["th"][i][0] if a["th"][i] else None
        et = a["est"][i][0] if a["est"][i] else None
        rows.append({"area": k, "name": a["n"], "wage_diff": "; ".join(wage_diff), "published_thr": pt, "published_row": by_rent.get(pt, "no Census row has this value"),
                     "census_thr": ct, "census_row": a["sp"][i] or "", "kind": KIND[a["k"][i]], "thr_diff": None if ct is None else pt - ct,
                     "our_estimate": et, "median_wage": a["w"][i][2],
                     "published_result_50": int(pub[2].result[k]), "census_result_50": None if ct is None else a["w"][i][2] - ct - 10000,
                     "page_default_result_50": None if (et or ct) is None else a["w"][i][2] - (et or ct) - 10000})
    r = pd.DataFrame(rows)
    r.to_csv(PROC / "published_diff.csv", index=False)
    pd.set_option("display.width", 260, "display.max_colwidth", 60, "display.max_rows", 200)
    print(f"\ncompared: {len(r)} areas x 5 percentiles")
    print(f"wage differences: {(r.wage_diff != '').sum()} areas")
    print(r[r.wage_diff != ""][["name", "wage_diff"]].to_string(index=False))
    same = r[r.thr_diff == 0]
    print(f"\nthreshold equal to the Census figure this build uses: {len(same)} areas\n" + same.groupby("kind").size().to_string())
    diff = r[(r.thr_diff != 0) & r.census_thr.notna()]
    print(f"\nthreshold differs: {len(diff)} areas")
    print(diff[["name", "published_thr", "published_row", "census_thr", "census_row", "thr_diff"]].to_string(index=False))
    none = r[r.census_thr.isna()]
    print(f"\npublished has a threshold, Census publishes none for the area: {len(none)}")
    print(none[["name", "published_thr", "published_row", "our_estimate"]].to_string(index=False))


if __name__ == "__main__":
    main()
