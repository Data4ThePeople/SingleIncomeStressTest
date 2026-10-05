"""Source coverage check: for each year, what kind of Census threshold each OEWS area gets, by
count of areas and by share of jobs. Output: data/processed/coverage.csv"""
import pandas as pd

from common import PROC

LABEL = {"metro": "metro-specific", "state_metro": "state smaller-metro figure", "state_nonmetro": "state nonmetro figure", "none": "no published figure"}


def main():
    o = pd.read_csv(PROC / "oews_areas.csv", dtype={"area": str})
    t = pd.read_csv(PROC / "area_thresholds.csv", dtype={"area": str})
    d = o.merge(t, on=["year", "area"], validate="one_to_one")
    d["kind"] = d.kind.map(LABEL)
    n = d.groupby(["year", "kind"]).size().unstack(fill_value=0)
    j = d.groupby(["year", "kind"]).tot_emp.sum().unstack(fill_value=0)
    share = (100 * j.div(j.sum(axis=1), axis=0)).round(1)
    out = n.add_suffix(" (areas)").join(share.add_suffix(" (% of jobs)"))
    out.to_csv(PROC / "coverage.csv")
    cols = list(LABEL.values())
    print("areas\n" + n[cols].to_string())
    print("\npercent of jobs in all areas shown\n" + share[cols].to_string())
    m = d[d.area_type == 4]
    ms = m.groupby(["year", "kind"]).tot_emp.sum().unstack(fill_value=0)
    print("\npercent of metro jobs\n" + (100 * ms.div(ms.sum(axis=1), axis=0)).round(1).to_string())
    print("\nhow named-metro thresholds were matched\n" + d[d.kind == "metro-specific"].groupby(["year", "how"]).size().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
