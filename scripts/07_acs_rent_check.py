"""Check: can the SPM rent index be rebuilt from public ACS tables, and what would a
metro-specific threshold be for metros the SPM file does not name?

Census builds the index from 5-year ACS median gross rent for two-bedroom units with complete
kitchen and plumbing, from its internal file. The closest public table is B25031 (median gross
rent by bedrooms, all renter units paying cash rent). This script compares the two for the named
metros, then applies the public version to the unnamed ones. Analysis only; not used on the map.
Output: data/processed/acs_rent_check.csv"""
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import get_key, load_env  # noqa: E402

from common import PROC  # noqa: E402

YEAR, ACS = 2024, 2023      # the 2024 thresholds use the 2019-2023 ACS
CBSA = "metropolitan statistical area/micropolitan statistical area"


def acs(geo):
    r = requests.get(f"https://api.census.gov/data/{ACS}/acs/acs5",
                     params={"get": "NAME,B25031_004E", "for": geo, "key": get_key("CENSUS_API_KEY")}, timeout=60)
    r.raise_for_status()
    j = r.json()
    return pd.DataFrame(j[1:], columns=j[0])


def main():
    load_env()
    us = float(acs("us:1").B25031_004E[0])
    m = acs(f"{CBSA}:*").rename(columns={CBSA: "area"})
    m["rent2br"] = pd.to_numeric(m.B25031_004E)
    m = m[m.rent2br > 0]
    m["acs_idx"] = m.rent2br / us
    o = pd.read_csv(PROC / "oews_areas.csv", dtype={"area": str})
    t = pd.read_csv(PROC / "area_thresholds.csv", dtype={"area": str})
    s = pd.read_csv(PROC / "spm_thresholds.csv")
    nat = pd.read_csv(PROC / "spm_national.csv").set_index("year").loc[YEAR]
    d = o[(o.year == YEAR) & (o.area_type == 4)].merge(t[t.year == YEAR], on=["year", "area"]).merge(m[["area", "rent2br", "acs_idx"]], on="area", how="left")
    d = d.merge(s[s.year == YEAR][["code", "idx"]], left_on="spm_code", right_on="code", how="left")
    d["acs_rent_thr"] = (nat.rent * (nat.share_rent * d.acs_idx + 1 - nat.share_rent)).round()
    d["diff"] = d.acs_rent_thr - d.rent
    d[["area", "title", "kind", "spm_name", "idx", "acs_idx", "rent", "acs_rent_thr", "diff", "a_median", "tot_emp"]].to_csv(PROC / "acs_rent_check.csv", index=False)
    print(f"U.S. median 2-bedroom gross rent, ACS {ACS - 4}-{ACS}: ${us:,.0f}")
    named = d[(d.kind == "metro") & (d.how == "code") & d.acs_idx.notna()]
    e = named["diff"]
    print(f"named metros matched by code: {len(named)}. ACS-built threshold minus published: median ${e.median():,.0f}, "
          f"median absolute ${e.abs().median():,.0f}, 90th pct absolute ${e.abs().quantile(.9):,.0f}, max ${e.abs().max():,.0f}; "
          f"index correlation {named.idx.corr(named.acs_idx):.4f}")
    for k in ["state_metro", "none"]:
        u = d[(d.kind == k) & d.acs_idx.notna()]
        base = u["diff"] if k == "state_metro" else pd.Series(dtype=float)
        print(f"\n{k}: {len(u)} metros with an ACS rent ({(d.kind == k).sum()} in all)")
        if k == "state_metro":
            print(f"  ACS-built metro threshold minus the state figure: median ${base.median():,.0f}, median absolute ${base.abs().median():,.0f}, "
                  f"share within $1,000: {(base.abs() <= 1000).mean():.0%}, within $2,500: {(base.abs() <= 2500).mean():.0%}")
            print(u.assign(a=u["diff"].abs()).nlargest(12, "a")[["title", "rent", "acs_rent_thr", "diff"]].to_string(index=False))
            print(u[u.title.str.contains("Flagstaff|Olympia|Reno|Anchorage")][["title", "rent", "acs_rent_thr", "diff"]].to_string(index=False))
        else:
            print(u[["title", "acs_rent_thr", "a_median"]].to_string(index=False))


if __name__ == "__main__":
    main()
