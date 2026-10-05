# Status

Project: SingleIncomeStressTest
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet
Step: 1
Since: 2026-10-05

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | | |
| 2a | Draft with brackets resolved | | |
| 2b | Eric's edit, Claude's look-over | | |
| 2c | Slice markup | | |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-10-05 Step 1 opened. Topic: rebuild the Single Income Stress Test
  (Tableau, 2024 only, published January 29, 2026) as a self-contained
  interactive map that plays over time. Metro level only, no occupations.
  OEWS percentile wages against SPM local thresholds, 2015 to 2025. Goals:
  a year slider with play, better map coverage, better usability.
- 2026-10-05 First build. Pipeline scripts 01 to 11, DATASETS.md, dist/index.html.
  626 areas, May 2015 to May 2025, five boundary sets, metro and nonmetro
  areas, Alaska and Hawaii. Tie-out: 0 differences across 29,150 wages and
  16,821 thresholds; 2024 lower-48 metro range matches the published Tableau
  legend (-$12,628 to $14,053). Open with Eric: areas with no published
  threshold (5 to 27 a year), and whether to use ACS-based thresholds for
  metros on a state figure.
- 2026-10-05 Eric: try the ACS rent-based thresholds. Added for all 11 years
  for metros with no Census figure of their own (default on, with a switch
  back to Census figures only). 4,041 estimates recomputed in the tie-out, 0
  differences. Still open: review of data/ref/spm_oews_hand.csv.
