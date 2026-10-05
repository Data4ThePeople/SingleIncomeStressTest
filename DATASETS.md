# Datasets

Written at the start of Step 1 (October 5, 2026) and updated as the build turned
up more. Numbers marked "measured" come from `scripts/10_coverage.py`,
`scripts/11_tieout.py` or the script named.

## 1. Occupational Employment and Wage Statistics, all occupations (BLS)

**What it is.** Wage estimates from a semiannual survey of about 1.1 million
establishments. We use one row per area and year: the all-occupations total
(`occ_code` 00-0000) with annual wages at the 10th, 25th, 50th, 75th and 90th
percentiles and total employment.

**Where it comes from.** The May "All data" XLSX for each year, cleaned in the
WageLorenzCurve project (`../WageLorenzCurve/scripts/01_load_oews.py`, output
`data/interim/oews_<year>.parquet`, local only). `scripts/01_extract_oews.py`
reads those and writes `data/processed/oews_areas.csv` (5,830 rows, committed).
The BLS API holds only the latest year, so history must come from the files.

**Version and vintage.** May 2015 to May 2025. Each May estimate pools six
semiannual panels (three years of survey data), with older panels wage-adjusted
to the reference period. Adjacent years share five of six panels, so year to
year changes are smoothed. Only years three apart share no survey data.

**Coverage.** Payroll jobs only: no self-employed, unincorporated owners or
private household workers. Metro areas (`area_type` 4) and nonmetro areas
(`area_type` 6) in the 50 states and DC: 552 to 553 areas in 2015 to 2017, 521
to 522 from 2018. Puerto Rico, Guam and the Virgin Islands are dropped (no SPM
threshold). Metro divisions (`area_type` 5, 2015 to 2017) are dropped; their
parent metros are kept. All values are survey estimates; none are filled in.

**Changes over time.**
- *Geography.* Five sets of boundaries: May 2015 to 2016; May 2017 (Enid, OK
  becomes a metro); May 2018 (nonmetro areas redrawn, 165 become 133); May 2019
  to 2023 (Twin Falls, ID becomes a metro); May 2024 to 2025 (new metro
  delineations, New England moves from towns to counties, Connecticut to
  planning regions). Measured: 320 of 626 area codes have all 11 years on one
  unchanged outline. An outline counts as unchanged if less than 0.5% of the
  combined land differs (`scripts/06_build_geo.py`).
- *New England before May 2024.* Areas are built from towns and carry codes in
  the 70000s (Boston is 71650). From May 2024 they are county-based with
  standard codes (Boston is 14460). The two are different places with
  different codes, so each has its own history.
- *Estimation method.* BLS moved to a model-based estimator with May 2021.
  Levels before and after are not strictly comparable. Not adjusted for.
- *Area definition lists.* BLS posts no list for May 2017, May 2020 or May
  2025. Checked against area codes in the data: 2020 equals 2019, 2025 equals
  2024, and 2017 equals 2016 plus Enid.

**Suppressed, censored or masked values.** `**` employment not published, `*`
wage not published, `#` wage at or above the top-code limit. Measured on our
rows: no wage percentile is flagged or missing in any area or year. Employment
is withheld for three nonmetro areas in May 2020 (Alaska, Central Louisiana,
Southern Vermont); their wages are published. They are on the map and count
as zero jobs in the "share of jobs" line for 2020.

**Missing data.** None in the wage columns used.

**Revisions.** BLS does not revise past May estimates. We pin each year's file.

**Units and rounding.** Annual dollars, rounded by BLS to the nearest $10.
Annual wage is the hourly wage times 2,080 hours. Before taxes and before any
benefits.

**Known quirks.** The principal state of a multi-state metro is the first state
in its title; checked equal to BLS's `prim_state` for every metro from 2020.
A wage percentile describes jobs in the area, not households: it says nothing
about how many earners a family has.

**Uncertainty.** BLS publishes relative standard errors for employment and the
mean wage, not for percentiles. Small areas have wider error. We do not show an
error band.

**License and attribution.** Public domain. Credit: U.S. Bureau of Labor
Statistics, Occupational Employment and Wage Statistics.

## 2. SPM Thresholds by Metro Area (Census Bureau, thresholds from BLS)

**What it is.** The Supplemental Poverty Measure threshold for a family of two
adults and two children, by housing status (renter, owner with a mortgage,
owner without), for each geographic adjustment area. BLS sets the national
thresholds from spending on food, clothing, shelter, utilities, telephone and
internet. Census adjusts the housing part for local rents.

**Where it comes from.** One workbook per year from the P60 report tables,
`www2.census.gov/programs-surveys/demo/tables/p60/<n>/`, sheet
`Thresholds <year>`. Report numbers: 258 (2015), 261, 265, 268, 272, 275, 277,
280, 283, 287 (2024), 290 (2025). `scripts/02_fetch_spm.py` downloads them;
`scripts/03_parse_spm.py` writes `data/processed/spm_thresholds.csv`. Method:
`spm_techdoc.pdf` section 4.2.2 in report 287, and Renwick (2011), SEHSD
Working Paper 2011-21.

**Version and vintage.** 2015 to 2025. No metro file is posted at the same
address for 2014 or earlier, which sets the start of the series.

**Coverage.** Three kinds of row:
- a named metro: the metros large enough to be identified in the public CPS
  file (297 in 2015, 260 in 2016 to 2024, 275 in 2025);
- "<State> Metro": all the state's smaller metros combined (34 to 42 states);
- "<State> Nonmetro": the state's nonmetro areas (47 to 48 states).

Measured share of jobs by the kind of threshold an OEWS area gets:

| | Metro-specific | State smaller-metro figure | State nonmetro figure | None published |
|---|---|---|---|---|
| 2015 | 84.7% | 3.2% | 11.9% | 0.2% |
| 2016 to 2024 | 83.1% to 83.6% | 4.2% to 5.1% | 10.9% to 11.6% | 0.2% to 1.3% |
| 2025 | 84.3% | 4.4% | 10.9% | 0.4% |

By count, 257 to 297 areas a year are metro-specific, 86 to 123 use the state
smaller-metro figure, 133 to 164 the state nonmetro figure, and 5 to 27 have no
published figure.

**How the local adjustment works.** Measured, exact to the dollar in every row
and year: threshold = national threshold x (housing share x rent index + 1 -
housing share). The rent index is the area's median gross rent for
two-bedroom units with complete kitchen and plumbing, divided by the national
median, from the 5-year ACS ending the year before (2024 thresholds use
2019 to 2023). The index is a survey estimate; areas within a combined row
share one index whatever their own rents.

**Changes over time.**
- *Housing share.* Renters: about 0.50 in 2015 to 2019, 0.44 from 2020. Owners
  with a mortgage: 0.50 then 0.44. Owners without: 0.41 then 0.33. The
  technical documentation says moving telephone spending out of utilities
  reduced the share that is adjusted. Local thresholds therefore spread less
  around the national figure from 2020. Not adjusted for.
- *Which metros are named* changes in 2016 (297 to 260) and 2025 (260 to 275).
  A metro can move between its own figure and the state figure.
- *Metro definitions.* Through 2024 the file uses older metro codes (Cleveland
  17460, Dayton 19380, Prescott 39140) and county-based New England metros. The
  2025 file matches OEWS codes exactly.
- Seven state "Metro" rows drop out between 2016 and 2017, and one more in 2023
  (South Carolina; the documentation calls it a programming refinement).

**Suppressed, censored or masked values.** None in the file. The masking is
upstream: metros too small to identify in the public CPS have no row.

**Missing data, and how each OEWS area gets its threshold**
(`scripts/04_crosswalk.py`, output `data/processed/area_thresholds.csv`):
1. Same code as a named metro: 246 to 283 metros a year.
2. Hand table `data/ref/spm_oews_hand.csv`, 18 rows: 14 town-based New England
   areas matched to the county-based metro with the same principal city (2015 to
   2023), and 4 renumbered metros (2024). The New England pairs cover somewhat
   different land.
3. Otherwise the state's "Metro" row for the metro's principal state.
4. Nonmetro areas: the state's "Nonmetro" row.
5. No row: 5 to 27 areas a year, mostly small metros in states with no "Metro"
   row (Alabama, California, Colorado, Wisconsin, Tennessee and others), plus
   unmatched New England areas (Danbury, Waterbury, Dover-Durham, Portsmouth).
   These are shown as "no published threshold". Nothing is guessed.

**Revisions.** The 2015 workbook is marked revised. We use the file as posted
on October 5, 2026.

**Units and rounding.** Annual dollars. Fractional in the earliest files (2015),
whole dollars later; rounded here to the dollar.

**Known quirks.** The SPM compares its threshold with resources after taxes,
benefits and work and medical expenses. This project compares it with gross
wages from one job, which is a different and rougher test. Three named metros
in the 2024 file are no longer OEWS metros (Carbondale-Marion, East
Stroudsburg, Pine Bluff) and go unused.

**Uncertainty.** Census publishes no error for the index. A state figure can be
well off for an individual small metro; see section 4 for the check and for
the rent-based estimate the page uses in its place by default.

**License and attribution.** Public domain. Credit: U.S. Census Bureau;
thresholds from the Bureau of Labor Statistics.

## 3. Area definitions and boundaries (BLS, Census Bureau)

**What it is.** BLS lists of the counties (or New England towns) in each OEWS
area (`data/ref/area_definitions_*.xlsx`), and Census cartographic boundary
files at 1:500,000 used to draw them.

**Where it comes from.** `scripts/05_fetch_geo.py`:
`www2.census.gov/geo/tiger/GENZ<year>/shp/`. Counties 2020 (for May 2015 to
2023), counties 2024 (for May 2024 and 2025, with Connecticut planning
regions), county subdivisions 2020 for the six New England states, states 2024.

**Coverage.** Every OEWS area with data has a shape in its era (checked in
`scripts/06_build_geo.py` and `08_build_data.py`).

**Known quirks.**
- BLS county codes fixed to the 2020 file: 02261 to 02063 + 02066, 02270 to
  02158, 46113 to 46102, 51515 to 51019, 02201 to 02198, 02232 to 02230 +
  02105, 02280 to 02275 + 02195. Three listed units no longer exist as counties
  and add no land (Yellowstone National Park part, Oak Ridge Reservation,
  Clifton Forge city).
- New England towns, 1,603 in the Census file: 1,497 match the BLS list by
  county and full name, 66 by name without the type word ("Bridgeport city" vs
  "Bridgeport town"), 22 because their county has only one area, and 18 by the
  neighbor they share the longest border with (Maine unorganized territories
  listed under older names). The last 40 are placed for drawing only.
- Shapes are simplified to 250 meters and clipped to the shoreline. They are
  for drawing, not for measuring.
- Albers USA projection; Alaska and Hawaii are moved and Alaska is shrunk.

**License and attribution.** Public domain.

## 4. ACS table B25031, median gross rent by bedrooms (Census Bureau)

**What it is.** Median monthly gross rent for two-bedroom renter units, from the
5-year American Community Survey, for every metro area and the U.S. We use it
to estimate a metro-specific threshold for metros the SPM file does not name
(`scripts/07_acs_thresholds.py`). The estimate applies Census's own formula
(section 2) with index = metro rent / U.S. rent.

**Where it comes from.** Census API, `api.census.gov/data/<year>/acs/acs5`,
variable `B25031_004E`, cached in `data/raw/acs/`. Key from the shared loader.

**Version and vintage.** For threshold year Y we use the 5-year file ending
Y - 1, as Census does. The table is first published in the 2011 to 2015 file,
so the 2015 thresholds borrow that file, one year later than Census used.

**Coverage.** Used only where an OEWS metro has no Census figure of its own:
metros on a state smaller-metro figure and metros with no published figure,
90 to 130 a year. Measured: every such metro has a rent from 2017 on; 5 lack
one in 2015 and 8 in 2016 (code differences) and keep the state figure. Before
2024 New England areas use the ACS town-based areas with the same codes.
Nonmetro areas always use the Census state nonmetro figure.

**How good the estimate is.** Measured each year on the 244 to 278 metros Census
does name: our rebuilt renter threshold differs from the published one by $38
to $122 at the median and by $366 to $1,869 at most. It runs slightly low
(median $6 to $114 below Census).

**What it changes.** The state figure and the metro's own estimate differ by
more than $1,000 for 16% of these metros in 2015, rising to 43% in 2025.
Largest in 2024: Sierra Vista-Douglas, AZ ($7,943 lower than the Arizona
figure) and Bremerton, WA ($7,367 higher than the Washington figure).

**Known quirks.** The public table covers all renter units paying cash rent.
Census's internal figure is limited to units with complete kitchen and
plumbing, which the public table cannot reproduce. The ACS metro boundaries of
a given vintage can differ slightly from the OEWS boundaries of the matching
May. These are our estimates, labeled as such on the page (hatched, and named
in the tooltip with the Census state figure beside them). The page has a
switch back to Census figures only.

**Uncertainty.** ACS medians carry sampling error, larger in small metros. Not
shown.

**License and attribution.** Public domain. Credit: U.S. Census Bureau,
American Community Survey 5-year estimates.
