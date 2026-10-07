"""Shared paths, HTTP helper, year list and state table for the pipeline."""
# Contact address for the User-Agent: read at run time, never hardcoded in the repo.
# Set D4TP_CONTACT_EMAIL in the environment or in ~/.claude/d4tp-process/.env.
import os as _os


def _d4tp_contact():
    v = _os.environ.get("D4TP_CONTACT_EMAIL")
    if v:
        return v
    try:
        with open(_os.path.expanduser("~/.claude/d4tp-process/.env"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("D4TP_CONTACT_EMAIL="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    except OSError:
        pass
    return ""


D4TP_CONTACT = _d4tp_contact()


import os
import time
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
REF = ROOT / "data" / "ref"
UA = f"Mozilla/5.0 (Macintosh) Data4ThePeople research {D4TP_CONTACT}"

# OEWS May of year Y is set against the SPM threshold for year Y
YEARS = list(range(2015, 2026))
PCTS = ["a_pct10", "a_pct25", "a_median", "a_pct75", "a_pct90"]

# OEWS geography eras: (first year, last year, BLS area definition file, county -> area patches).
# BLS posts no list for May 2017. It equals the May 2016 list except that Enid, OK (Garfield County)
# became a metro. May 2020 uses the May 2019 list and May 2025 the May 2024 list (identical area codes).
ERAS = [(2015, 2016, "area_definitions_m2016.xlsx", {}),
        (2017, 2017, "area_definitions_m2016.xlsx", {"40047": "21420"}),
        (2018, 2018, "area_definitions_2018.xlsx", {}),
        (2019, 2023, "area_definitions_m2019.xlsx", {}),
        (2024, 2025, "area_definitions_m2024.xlsx", {})]

# Census P60 report number that carries each year's "SPM Thresholds by Metro Area" file
SPM_FILES = {2015: (258, "pov-threshold-2015.xlsx"), 2016: (261, "pov-threshold-2016.xlsx"),
             2017: (265, "pov-threshold-2017.xlsx"), 2018: (268, "pov-threshold-2018.xlsx"),
             2019: (272, "pov-threshold-2019.xlsx"), 2020: (275, "pov-threshold-2020.xlsx"),
             2021: (277, "SPM-pov-threshold-2021.xlsx"), 2022: (280, "SPM-pov-threshold-2022.xlsx"),
             2023: (283, "SPM-pov-threshold-2023.xlsx"), 2024: (287, "SPM-pov-threshold-2024.xlsx"),
             2025: (290, "SPM-pov-threshold-2025.xlsx")}

# 50 states + DC: fips -> (abbreviation, name)
STATE_INFO = {"01": ("AL", "Alabama"), "02": ("AK", "Alaska"), "04": ("AZ", "Arizona"), "05": ("AR", "Arkansas"),
              "06": ("CA", "California"), "08": ("CO", "Colorado"), "09": ("CT", "Connecticut"),
              "10": ("DE", "Delaware"), "11": ("DC", "District of Columbia"), "12": ("FL", "Florida"),
              "13": ("GA", "Georgia"), "15": ("HI", "Hawaii"), "16": ("ID", "Idaho"), "17": ("IL", "Illinois"),
              "18": ("IN", "Indiana"), "19": ("IA", "Iowa"), "20": ("KS", "Kansas"), "21": ("KY", "Kentucky"),
              "22": ("LA", "Louisiana"), "23": ("ME", "Maine"), "24": ("MD", "Maryland"),
              "25": ("MA", "Massachusetts"), "26": ("MI", "Michigan"), "27": ("MN", "Minnesota"),
              "28": ("MS", "Mississippi"), "29": ("MO", "Missouri"), "30": ("MT", "Montana"),
              "31": ("NE", "Nebraska"), "32": ("NV", "Nevada"), "33": ("NH", "New Hampshire"),
              "34": ("NJ", "New Jersey"), "35": ("NM", "New Mexico"), "36": ("NY", "New York"),
              "37": ("NC", "North Carolina"), "38": ("ND", "North Dakota"), "39": ("OH", "Ohio"),
              "40": ("OK", "Oklahoma"), "41": ("OR", "Oregon"), "42": ("PA", "Pennsylvania"),
              "44": ("RI", "Rhode Island"), "45": ("SC", "South Carolina"), "46": ("SD", "South Dakota"),
              "47": ("TN", "Tennessee"), "48": ("TX", "Texas"), "49": ("UT", "Utah"), "50": ("VT", "Vermont"),
              "51": ("VA", "Virginia"), "53": ("WA", "Washington"), "54": ("WV", "West Virginia"),
              "55": ("WI", "Wisconsin"), "56": ("WY", "Wyoming")}
ABBR_FIPS = {v[0]: k for k, v in STATE_INFO.items()}
NEW_ENGLAND = ["09", "23", "25", "33", "44", "50"]


def era_of(year):
    return next(i for i, e in enumerate(ERAS) if e[0] <= year <= e[1])


def fetch(url, dest, tries=6):
    """Download url to dest unless it already exists. Returns False on 404."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    for i in range(tries):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=(20, 180), stream=True)
            if r.status_code == 404:
                return False
            if r.status_code in (429, 503):
                time.sleep(5 * (i + 1))
                continue
            r.raise_for_status()
            tmp = dest.with_suffix(dest.suffix + f".{os.getpid()}.part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            if dest.suffix in (".zip", ".xlsx") and not zipfile.is_zipfile(tmp):
                tmp.unlink()
                time.sleep(5 * (i + 1))
                continue
            os.replace(tmp, dest)
            return True
        except requests.RequestException:
            if i == tries - 1:
                raise
            time.sleep(2 ** i)
    raise RuntimeError(f"gave up on {url}")
