"""Parse the SPM threshold workbooks into one table.

Each workbook's "Thresholds <year>" sheet has one row per geographic adjustment area: a named
metro, a state's remaining smaller metros combined ("<State> Metro"), or a state's nonmetro areas
("<State> Nonmetro"). Thresholds are for two adults and two children, by housing status.
Output: data/processed/spm_thresholds.csv"""
import re

import pandas as pd

from common import PROC, RAW, STATE_INFO, YEARS

NAME_FIPS = {v[1]: k for k, v in STATE_INFO.items()}


def kind_of(name):
    m = re.fullmatch(r"(.+) (Metro|Nonmetro)", name)
    if m and m.group(1) in NAME_FIPS:
        return ("state_metro" if m.group(2) == "Metro" else "state_nonmetro"), NAME_FIPS[m.group(1)]
    return "metro", None


def main():
    out, nat = [], []
    for y in YEARS:
        raw = pd.read_excel(RAW / "spm" / f"spm_{y}.xlsx", sheet_name=f"Thresholds {y}", header=None)
        num = raw.apply(pd.to_numeric, errors="coerce")
        n = raw[num[0].isna() & num[2].isna() & num[5].notna()]
        assert len(n) == 1, f"{y}: national row not found"
        base = {"year": y, "own_mort": float(num.loc[n.index[0], 3]), "own_free": float(num.loc[n.index[0], 4]),
                "rent": float(num.loc[n.index[0], 5])}
        d = raw[num[0].notna()].copy()
        d.columns = ["code", "name", "idx", "own_mort", "own_free", "rent"]
        d["name"] = d.name.str.strip()
        for c in ["idx", "own_mort", "own_free", "rent"]:
            d[c] = pd.to_numeric(d[c]).astype(float)
        d["code"] = d.code.astype(int)
        d["year"] = y
        d[["kind", "state"]] = [kind_of(nm) for nm in d.name]
        assert not d.duplicated("code").any(), f"{y}: duplicate code"
        # the published thresholds follow national x (share x index + 1 - share); recover the share and check every row
        far = d[(d.idx - 1).abs() > 0.05]
        for c in ["own_mort", "own_free", "rent"]:
            share = ((far[c] / base[c] - 1) / (far.idx - 1)).median()
            err = (base[c] * (share * d.idx + 1 - share) - d[c]).abs().max()
            assert err < 1.5, f"{y} {c}: formula misses by ${err:.2f}"
            base["share_" + c] = round(share, 4)
        nat.append(base)
        out.append(d[["year", "code", "name", "kind", "state", "idx", "own_mort", "own_free", "rent"]])
    d = pd.concat(out, ignore_index=True)
    d.to_csv(PROC / "spm_thresholds.csv", index=False)
    n = pd.DataFrame(nat)
    n.to_csv(PROC / "spm_national.csv", index=False)
    print(d.groupby(["year", "kind"]).size().unstack().to_string())
    print(n.to_string(index=False))


if __name__ == "__main__":
    main()
