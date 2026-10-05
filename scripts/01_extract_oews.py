"""All-occupations wage percentiles for every OEWS metro and nonmetro area, May 2015 to May 2025.

Reads the cleaned annual files built in the WageLorenzCurve project (its scripts/01_load_oews.py,
from the BLS "All data" XLSX for each year) and keeps one row per area and year.
Output: data/processed/oews_areas.csv"""
import re

import pandas as pd

from common import ABBR_FIPS, PCTS, PROC, ROOT, STATE_INFO, YEARS

SRC = ROOT.parent / "WageLorenzCurve" / "data" / "interim"


def state_of(area, area_type, title):
    """Principal state fips: the first state named in a metro title; the code prefix for a nonmetro area."""
    if area_type == 6:
        return area[:2]
    m = re.search(r",\s*([A-Z]{2})(?:-[A-Z]{2})*\s*$", title)
    return ABBR_FIPS.get(m.group(1)) if m else None


def main():
    out = []
    for y in YEARS:
        o = pd.read_parquet(SRC / f"oews_{y}.parquet")
        o = o[(o.occ_code == "00-0000") & o.area_type.isin([4, 6])].copy()
        o["title"] = o.area_title.str.strip()
        o["state"] = [state_of(a, t, n) for a, t, n in zip(o.area, o.area_type, o.title)]
        o = o[o.state.isin(STATE_INFO)]                    # drops Puerto Rico, Guam, Virgin Islands
        flags = o[[c + "_flag" for c in PCTS]].notna().any(axis=1)
        assert not flags.any(), f"{y}: flagged wage cell\n{o[flags].title.tolist()}"
        assert o[PCTS].notna().all().all(), f"{y}: missing wage"
        # BLS withholds the job count (**) for three nonmetro areas in May 2020; their wages are published
        for t in o[o.tot_emp.isna()].title:
            print(f"{y}: employment not published for {t}")
        if o.prim_state.notna().any():               # BLS's own principal state, published from 2020
            ps = o.prim_state.map(ABBR_FIPS)
            bad = o[(o.area_type == 4) & (ps != o.state)]
            assert bad.empty, f"{y}: principal state differs from title\n{bad[['title', 'prim_state']]}"
        out.append(o[["year", "area", "title", "area_type", "state", "tot_emp"] + PCTS])
    d = pd.concat(out, ignore_index=True)
    assert not d.duplicated(["year", "area"]).any(), "duplicate (year, area)"
    for c in PCTS + ["tot_emp"]:
        d[c] = d[c].astype("Int64")
    d.to_csv(PROC / "oews_areas.csv", index=False)
    print(d.groupby(["year", "area_type"]).size().unstack().to_string())
    print(f"wrote oews_areas.csv: {len(d):,} rows")


if __name__ == "__main__":
    main()
