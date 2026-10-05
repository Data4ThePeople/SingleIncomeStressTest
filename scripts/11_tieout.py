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

    # our rent-based estimates, recomputed from the cached ACS responses and the national rows of the workbooks
    n_e = bad = 0
    for i, y in enumerate(YEARS):
        v = max(y - 1, 2015)
        rent = {}
        for geo in ("cbsa", "necta"):
            j = json.loads((RAW / "acs" / f"b25031_{v}_{geo}.json").read_text())
            rent.update({r[-1]: float(r[1]) for r in j[1:] if r[1] and float(r[1]) > 0 and r[-1] not in rent})
        us = float(json.loads((RAW / "acs" / f"b25031_{v}_us.json").read_text())[1][1])
        raw = pd.read_excel(RAW / "spm" / f"spm_{y}.xlsx", sheet_name=f"Thresholds {y}", header=None)
        num = raw.apply(pd.to_numeric, errors="coerce")
        natrow = num[num[0].isna() & num[2].isna() & num[5].notna()].iloc[0]
        far = num[num[0].notna() & ((num[2] - 1).abs() > 0.05)]
        for a in areas.values():
            if not a["est"][i]:
                continue
            assert a["k"][i] in "sx" and a["r2"][i] == rent[a["id"]]
            for t, got in zip(TEN, a["est"][i]):
                share = round(((far[COL[t]] / natrow[COL[t]] - 1) / (far[2] - 1)).median(), 4)
                n_e += 1
                bad += abs(natrow[COL[t]] * (share * rent[a["id"]] / us + 1 - share) - got) > 0.51
    print(f"rent-based estimates recomputed: {n_e:,}; differences: {bad}")
    assert bad == 0

    # family-size scale: every cell of each workbook's "Matrix" sheet (thresholds by family size and
    # number of children for one sample area) against the scale the page uses
    def equiv(ad, kids):
        if kids == 0:
            return 1 if ad == 1 else 1.41 if ad == 2 else ad ** 0.7
        return (1.8 + 0.5 * (kids - 1)) ** 0.7 if ad == 1 else (ad + 0.5 * kids) ** 0.7

    n_f, worst = 0, 0.0
    for y in YEARS:
        m = pd.read_excel(RAW / "spm" / f"spm_{y}.xlsx", sheet_name="Matrix", header=None)
        num = m.apply(pd.to_numeric, errors="coerce")
        blocks = [r for r in range(len(m)) if str(m.iloc[r, 0]).strip() == "Size of Family Unit"]
        for b, start in enumerate(blocks):
            end = blocks[b + 1] if b + 1 < len(blocks) else len(m)
            base = next(num.iloc[r, 4] for r in range(start, end) if str(m.iloc[r, 0]).strip() == "Four people")
            for r in range(start, end):
                label, size = str(m.iloc[r, 0]).strip(), num.iloc[r, 1]
                for c in range(2, 11):
                    v = num.iloc[r, c]
                    if pd.isna(v) or v < 1000:
                        continue
                    kids = c - 2
                    if label == "Single Parent":
                        ad = 1
                    elif pd.notna(size):
                        ad = int(size) - kids
                        if size >= 3 and ad < 2:           # rows of three or more people are "two or more adults";
                            continue                       # the 2015 file has one stray one-adult cell there
                    else:
                        continue
                    n_f += 1
                    diff = abs(base * equiv(ad, kids) / equiv(2, 2) - v)
                    if diff > 1:
                        print(f"    {y} block {b} {label!r} adults {ad} children {kids}: Census {v:,.0f}, scale gives {base * equiv(ad, kids) / equiv(2, 2):,.0f}")
                    worst = max(worst, diff)
    print(f"family-size cells checked against the Census matrix: {n_f:,}; largest difference ${worst:.2f}")
    assert n_f > 1000 and worst < 1

    def thr(a, i, est):
        return a["est"][i] if est and a["est"][i] else a["th"][i]

    def test(a, i, p=2, ten=0, cush=10000, est=False):
        return a["w"][i][p] - thr(a, i, est)[ten] - cush

    print("\nspot rows (income, threshold, cushion, result)")
    for aid, y, p, ten, cush in [("22380", 2024, 2, 0, 10000), ("35620", 2025, 2, 0, 10000), ("26420", 2015, 1, 0, 5000),
                                 ("41860", 2019, 3, 1, 10000), ("2800006", 2025, 2, 0, 10000), ("71650", 2020, 2, 2, 0), ("11260", 2022, 0, 0, 10000)]:
        a, i = areas[aid], YEARS.index(y)
        print(f"  {a['n']}, {y}, {PCTS[p]}, {TEN[ten]}: {a['w'][i][p]:,} - {a['th'][i][ten]:,} - {cush:,} = {test(a, i, p, ten, cush):,}  [{a['sp'][i]}]")

    print("\nheadline, 50th percentile, renters, $10,000 cushion")
    for i, y in enumerate(YEARS):
        tot = sum(1 for a in areas.values() if a["w"][i])
        line = f"  {y} ({tot} areas):"
        for est in (True, False):
            rows = [(test(a, i, est=est), a["e"][i] or 0) for a in areas.values() if a["w"][i] and thr(a, i, est)]
            short = [r for r in rows if r[0] < 0]
            line += f" {'with our estimates' if est else 'Census figures only'}: short in {len(short)} of {len(rows)}, {100 * sum(e for _, e in short) / sum(e for _, e in rows):.0f}% of jobs;"
        print(line + f" national renter threshold {D['nat'][i][0]:,}")

    i = YEARS.index(2024)
    m = [(test(a, i), a["n"]) for a in areas.values() if a["t"] == 4 and a["w"][i] and a["th"][i] and a["s"] not in ("02", "15")]
    print(f"\n2024 lower-48 metros with a threshold: {len(m)}; min {min(m)}, max {max(m)}")
    print("published Tableau legend, 2024: -12,628 to 14,053")


if __name__ == "__main__":
    main()
