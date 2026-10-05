"""Our estimate of a metro-specific SPM threshold for metros the Census file does not name.

Census adjusts the national threshold with a rent index: the area's 5-year ACS median gross rent
for two-bedroom units with complete kitchen and plumbing, over the national median, from the ACS
ending the year before. The closest public table is B25031 (median gross rent by bedrooms, all
renter units paying cash rent). For each year this script
  1. pulls the two-bedroom median for every metro and for the U.S.,
  2. applies the published formula: national x (housing share x index + 1 - housing share),
  3. compares the result with the published threshold wherever Census names the metro.
The estimate is used on the map only for metros with no figure of their own.
Output: data/processed/acs_thresholds.csv, data/processed/acs_check.csv"""
import json
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import get_key, load_env  # noqa: E402

from common import PROC, RAW, YEARS  # noqa: E402

TEN = ["rent", "own_mort", "own_free"]
# B25031 is first published in the 2011-2015 file. The 2015 thresholds use the 2010-2014 ACS, which has
# no public equivalent, so 2015 borrows the 2011-2015 rents (one year later than Census used).
FIRST_ACS = 2015
GEOS = {"cbsa": "metropolitan statistical area/micropolitan statistical area", "necta": "new england city and town area", "us": "us"}


def acs(vintage, geo):
    """B25031_004E (two bedrooms) for one geography level and 5-year vintage, cached on disk."""
    dest = RAW / "acs" / f"b25031_{vintage}_{geo}.json"
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(f"https://api.census.gov/data/{vintage}/acs/acs5",
                         params={"get": "NAME,B25031_004E", "for": GEOS[geo] + (":1" if geo == "us" else ":*"), "key": get_key("CENSUS_API_KEY")}, timeout=90)
        if r.status_code in (204, 400, 404):      # NECTAs are not published in the latest vintages
            dest.write_text("[]")
        else:
            r.raise_for_status()
            dest.write_text(r.text)
    j = json.loads(dest.read_text())
    if not j:
        return pd.DataFrame(columns=["area", "rent2br"])
    d = pd.DataFrame(j[1:], columns=j[0])
    d = d.rename(columns={d.columns[-1]: "area"})
    d["rent2br"] = pd.to_numeric(d.B25031_004E, errors="coerce")
    return d[d.rent2br > 0][["area", "rent2br"]]


def main():
    load_env()
    o = pd.read_csv(PROC / "oews_areas.csv", dtype={"area": str})
    t = pd.read_csv(PROC / "area_thresholds.csv", dtype={"area": str})
    nat = pd.read_csv(PROC / "spm_national.csv").set_index("year")
    out, chk = [], []
    for y in YEARS:
        v = max(y - 1, FIRST_ACS)
        us = acs(v, "us")
        assert len(us) == 1, f"no U.S. rent for ACS {v}"
        us = float(us.rent2br.iloc[0])
        rents = pd.concat([acs(v, "cbsa"), acs(v, "necta")]).drop_duplicates("area")
        d = o[(o.year == y) & (o.area_type == 4)].merge(t[t.year == y], on=["year", "area"]).merge(rents, on="area", how="left")
        d["rent2br"] = d.rent2br.astype(float)
        d["acs_idx"] = d.rent2br / us
        for c in TEN:
            s = nat.loc[y, "share_" + c]
            d["est_" + c] = (nat.loc[y, c] * (s * d.acs_idx + 1 - s)).round()
        out.append(d[["year", "area", "title", "kind", "rent2br", "acs_idx"] + ["est_" + c for c in TEN]])
        named = d[(d.kind == "metro") & (d.how == "code") & d.rent2br.notna()]
        e = (named.est_rent - named.rent).astype(float)
        small = d[d.kind.isin(["state_metro", "none"])]
        sm = small[small.kind == "state_metro"]
        gap = (sm.est_rent - sm.rent).astype(float).dropna()
        chk.append({"year": y, "acs": f"{v - 4}-{v}", "us_rent": int(us), "named_compared": len(named), "median_diff": e.median(),
                    "median_abs": e.abs().median(), "p90_abs": e.abs().quantile(.9), "max_abs": e.abs().max(),
                    "small_metros": len(small), "with_estimate": int(small.rent2br.notna().sum()),
                    "no_rent": "; ".join(small[small.rent2br.isna()].title), "state_vs_own_over_1000": (gap.abs() > 1000).mean()})
    d = pd.concat(out, ignore_index=True)
    d.to_csv(PROC / "acs_thresholds.csv", index=False)
    c = pd.DataFrame(chk)
    c.to_csv(PROC / "acs_check.csv", index=False)
    pd.set_option("display.width", 250)
    print(c.drop(columns="no_rent").round({"median_diff": 0, "median_abs": 0, "p90_abs": 0, "max_abs": 0, "state_vs_own_over_1000": 2}).to_string(index=False))
    for r in c.itertuples():
        if r.no_rent:
            print(f"{r.year}: no ACS rent for {r.no_rent}")


if __name__ == "__main__":
    main()
