"""Tie-out: recompute every number the page shows from the source files and compare.

1. Every wage in map_data.json against the OEWS annual files.
2. Every threshold against the Census workbooks, read again here without the parser in 03.
3. Spot rows, headline counts per year, and the published 2024 Tableau range."""
import json

import pandas as pd

from common import PCTS, PROC, RAW, ROOT, YEARS

TEN = ["rent", "own_mort", "own_free"]
COL = {"rent": 5, "own_mort": 3, "own_free": 4}


def main():
    D = json.loads((PROC / "map_data.json").read_text())
    areas = {a["id"]: a for a in D["areas"]}
    bad = n_w = n_t = 0
    for i, y in enumerate(YEARS):
        o = pd.read_parquet(ROOT.parent / "WageLorenzCurve" / "data" / "interim" / f"oews_{y}.parquet")
        o = o[(o.occ_code == "00-0000") & o.area_type.isin([4, 6])]
        src = {a.lstrip("0"): r for a, r in zip(o.area, o[PCTS].itertuples(index=False))}
        raw = pd.read_excel(RAW / "spm" / f"spm_{y}.xlsx", sheet_name=f"Thresholds {y}", header=None)
        spm = {str(r[1]).strip(): r for r in raw.itertuples(index=False)}
        for a in areas.values():
            if a["w"][i] is None:
                continue
            n_w += 5
            bad += sum(int(s) != v for s, v in zip(src[a["id"]], a["w"][i]))
            if a["th"][i]:
                n_t += 3
                row = spm[a["sp"][i]]
                bad += sum(int(round(float(row[COL[t]]))) != v for t, v in zip(TEN, a["th"][i]))
    print(f"wages compared: {n_w:,}; thresholds compared: {n_t:,}; differences: {bad}")
    assert bad == 0

    def test(a, i, p=2, ten=0, cush=10000):
        return a["w"][i][p] - a["th"][i][ten] - cush

    print("\nspot rows (income, threshold, cushion, result)")
    for aid, y, p, ten, cush in [("22380", 2024, 2, 0, 10000), ("35620", 2025, 2, 0, 10000), ("26420", 2015, 1, 0, 5000),
                                 ("41860", 2019, 3, 1, 10000), ("2800006", 2025, 2, 0, 10000), ("71650", 2020, 2, 2, 0), ("11260", 2022, 0, 0, 10000)]:
        a, i = areas[aid], YEARS.index(y)
        print(f"  {a['n']}, {y}, {PCTS[p]}, {TEN[ten]}: {a['w'][i][p]:,} - {a['th'][i][ten]:,} - {cush:,} = {test(a, i, p, ten, cush):,}  [{a['sp'][i]}]")

    print("\nheadline, 50th percentile, renters, $10,000 cushion")
    for i, y in enumerate(YEARS):
        rows = [(test(a, i), a["e"][i] or 0) for a in areas.values() if a["w"][i] and a["th"][i]]
        short = [r for r in rows if r[0] < 0]
        tot = sum(1 for a in areas.values() if a["w"][i])
        print(f"  {y}: short in {len(short)} of {len(rows)} areas with a threshold ({tot} areas in all), "
              f"{100 * sum(e for _, e in short) / sum(e for _, e in rows):.0f}% of jobs; national renter threshold {D['nat'][i][0]:,}")

    i = YEARS.index(2024)
    m = [(test(a, i), a["n"]) for a in areas.values() if a["t"] == 4 and a["w"][i] and a["th"][i] and a["s"] not in ("02", "15")]
    print(f"\n2024 lower-48 metros with a threshold: {len(m)}; min {min(m)}, max {max(m)}")
    print("published Tableau legend, 2024: -12,628 to 14,053")


if __name__ == "__main__":
    main()
