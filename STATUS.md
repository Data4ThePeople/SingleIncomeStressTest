# Status

Project: SingleIncomeStressTest
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: stress-test-viz
Step: 2d
Since: 2026-10-05

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | 2026-10-05 | Viz live on Pages; tie-out and independent tie-out clean |
| 2a | Draft with brackets resolved | 2026-10-05 | Written by Claude in the rebuild-post format at Eric's request |
| 2b | Eric's edit, Claude's look-over | 2026-10-05 | No edits from Eric; six look-over edits accepted and applied |
| 2c | Slice markup | 2026-10-05 | 2 embeds (map, video), 3 blurbs, 1 divider; same structure as children-poverty-viz |
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
- 2026-10-05 Eric reviewed data/ref/spm_oews_hand.csv: fine as is. State filter:
  now includes metros that cross into the chosen state, moved up in the
  controls.
- 2026-10-05 Eric: add the family size selector. Added (one or two adults, zero
  to four children) using the SPM equivalence scale, checked against the
  Census matrix sheet in every year's workbook. Scale midpoint changed from
  grey to pale yellow at Eric's request.
- 2026-10-05 Legend moved below the map (Eric: it covered Florida). Phone
  layout checked at 390px: less-used controls now sit behind a "More options"
  button so the map is on the first screen.
- 2026-10-05 Compared the published Tableau data (data/*pct.csv, May 2024, 383
  metros x 5 percentiles) with this build (scripts/12_compare_published.py).
  Wages: 0 differences. Thresholds: 357 equal, 2 differ (Cleveland, Prescott),
  24 used a state nonmetro figure where Census publishes none for the metro.
- 2026-10-05 Independent tie-out by a fresh agent from raw BLS, Census and ACS
  files: 0 differences in wages, thresholds, estimates, family scale and nine
  headlines. Judgment calls on 2024 boundaries, New England and multi-state
  metros left as is (the rent-based estimate covers them); to be noted in the
  methodology. Fixed headline rounding near 0% and 100%; search shows years.
  Not independently checked: map outlines, Change view, rankings past the top five.
- 2026-10-05 Step 1 confirmed by Eric.
- 2026-10-05 Step 2a opened. Slug stress-test-viz (reuses the January post's
  slug). Eric asked for the post in the format of the child poverty and wage
  gap rebuild posts, written by Claude. Draft in posts/stress-test-viz/POST.md;
  every number from scripts/13_post_numbers.py.
- 2026-10-05 Tutorial video rendered (video/single-income-stress-test-tutorial.mp4,
  57 s, 1920x1080, seven beats approved by Eric, cushion slider first) and
  YouTube thumbnail. Waiting for Eric to watch it and upload; the post needs the
  YouTube link.
- 2026-10-05 Eric accepted edits 1 and 2 (illustration framing), ending on
  "rough, illustrative guide".
- 2026-10-05 Step 2a confirmed by Eric. Carried forward as drafted unless he
  says otherwise: date October 6, 2026; no link to the old-method PDF; Step 1
  names the Cleveland and Prescott differences; no tutorial video in the post
  until he sends the YouTube link.
- 2026-10-05 Step 2b: Eric had no edits. Look-over found no number mismatches
  and proposed six wording edits; Eric said "good", edits not yet accepted by
  number, so none applied.
- 2026-10-05 Step 2c: convert-only run. 89 slices: 1 embed, 3 blurbs, 41 text,
  43 spacers, 1 divider. Same structure as children-poverty-viz.
- 2026-10-05 Tutorial video re-rendered (caption now matches the slider at
  $25,000) and uploaded by Eric: https://www.youtube.com/watch?v=zkITTX8_02c.
  Embedded in the post under "Using the visualization".
- 2026-10-05 Eric accepted all six look-over edits; applied.
- 2026-10-05 Step 2c confirmed by Eric. Step 2d: Eric chose an image of the new
  viz. Hero rendered by scripts/14_hero.py (2025 map, starting settings, dark
  palette) and padded with `hero pad` to 1680x1080; alt text written.
