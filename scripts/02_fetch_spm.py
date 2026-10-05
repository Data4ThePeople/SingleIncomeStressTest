"""Download the Census "SPM Thresholds by Metro Area" workbook for each year, and the SPM
technical documentation. Output: data/raw/spm/spm_<year>.xlsx, data/raw/docs/"""
from common import RAW, SPM_FILES, fetch

BASE = "https://www2.census.gov/programs-surveys/demo/tables/p60"

for year, (n, name) in SPM_FILES.items():
    ok = fetch(f"{BASE}/{n}/{name}", RAW / "spm" / f"spm_{year}.xlsx")
    print(year, f"p60-{n}", name, "ok" if ok else "NOT FOUND")
for name in ("spm_techdoc.pdf", "readme.pdf"):
    fetch(f"{BASE}/287/{name}", RAW / "docs" / name)
