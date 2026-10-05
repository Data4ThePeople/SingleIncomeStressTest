---
title: "The Single Income Stress Test: Can a Family Live on One Income Where You Live?"
subtitle: A free, interactive map of whether one paycheck clears the local poverty threshold for a family, with money left for surprise expenses, in every U.S. metro and rural area from 2015 to 2025.
slug: stress-test-viz
date: 2026-10-06
updated: 2026-10-06
prismic_id: aXtuIxAAACAABefK
section: Visualization
hero: images/stress-test-viz-hero-1680x1080.png
hero_alt: Map of U.S. metro and rural areas in 2025 on a dark background, titled One income, less the local poverty threshold, less $10,000. Areas run from deep red (short by $10,000 or more) through pale yellow (near break-even) to deep teal ($10,000 or more to spare). Red covers much of California, Florida and the Southeast; teal covers the upper Midwest and Northeast. Beside it: The Single Income Stress Test, 49% of jobs are in areas where one median paycheck falls short. Data 4 The People.
meta_title: "Can a Family Live on One Income? Map by City, 2015-2025"
description: "Free interactive map: does one paycheck cover the local poverty threshold plus a cushion for surprises? Every U.S. metro and rural area, 2015 to 2025."
keywords: can a family live on one income, cities where you can live on one income, can a family of 4 survive on one income, single income family, cost of living vs median income by city, poverty line by city, supplemental poverty measure by metro area, one income household map
schema_type: dataset
dataset_name: Single income excess or shortfall against local Supplemental Poverty Measure thresholds, U.S. metro and nonmetro areas, 2015 to 2025
dataset_description: "Annual pay at the 10th, 25th, 50th, 75th and 90th percentiles for every U.S. metro and nonmetro area, May 2015 to May 2025, from BLS Occupational Employment and Wage Statistics, set against the Census Bureau's Supplemental Poverty Measure threshold for the area and year, by housing status. Metro areas with no Census threshold of their own carry an estimate built from American Community Survey two-bedroom rents with the Census formula. Each year is on that year's area boundaries."
temporal: 2015/2025
spatial: United States
measured: Annual wage at the 10th, 25th, 50th, 75th and 90th percentiles|U.S. dollars; Supplemental Poverty Measure threshold, two adults and two children, by housing status|U.S. dollars; Income less threshold less cushion|U.S. dollars; Income as a share of threshold plus cushion|percent; Payroll jobs|count
sources: https://www.bls.gov/oes/|https://www.census.gov/topics/income-poverty/supplemental-poverty-measure.html|https://www.census.gov/programs-surveys/acs|https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
distribution: text/html|https://data4thepeople.github.io/SingleIncomeStressTest/;text/csv|https://github.com/Data4ThePeople/SingleIncomeStressTest/tree/main/data/processed
measurement_technique: OEWS all-occupations wage percentiles matched by area and year to Census SPM thresholds (named metro, state smaller-metro figure or state nonmetro figure); thresholds for unnamed metros estimated as national threshold x (housing share x ACS two-bedroom rent ratio + 1 - housing share); other family sizes by the SPM three-parameter equivalence scale; result is wage less threshold less a chosen cushion.
credit: Data 4 The People, from the U.S. Bureau of Labor Statistics and the U.S. Census Bureau
license: https://www.data4thepeople.com/terms-of-use
app_url: https://data4thepeople.github.io/SingleIncomeStressTest/
app_name: "The Single Income Stress Test: interactive map, 2015 to 2025"
app_category: EducationalApplication
app_description: Free interactive map of whether one paycheck covers the local poverty threshold plus a cushion for surprise expenses, in every U.S. metro and rural area, each year from 2015 to 2025.
app_features: Every U.S. metro and nonmetro area, 2015 to 2025|Play through the years at 1x, 2x or 3x|Slider for money set aside for surprise expenses|Five pay levels from the 10th to the 90th percentile|Nine family types and three housing types|Hover or tap any area for the math|History chart for each area|Search any area by name|Filter to one state|Change between any two years|Rankings of largest shortfalls and most room
drop_cap: false
heading_spacer: 20px
caption_spacer: 20px
dividers: false
---

# The Single Income Stress Test: Can a Family Live on One Income Where You Live?

<iframe src="https://data4thepeople.github.io/SingleIncomeStressTest/?v=20261005b#embed=1" width="100%" height="780" loading="lazy" style="border:0" title="The Single Income Stress Test: interactive map, 2015 to 2025"></iframe>

::: spacer 40px

::: blurb
**[Open the full visualization](https://data4thepeople.github.io/SingleIncomeStressTest/)** **for a larger map and dark mode.**
:::

::: spacer

::: blurb Updated October 6, 2026
We rebuilt this map with 11 years of history. It now shows every year from 2015 to 2025, rural areas as well as metro areas, Alaska and Hawaii, and a choice of family size and housing. The first version, published January 29, 2026, showed 2024 only, for metro areas in the lower 48 states.
:::

## Purpose

::: spacer

This map runs one test on every part of the United States. Take one person's annual pay. Subtract the local poverty threshold for their family. Subtract some money for surprise expenses. What is left is the excess, or the shortfall. The map is free to use and needs no sign-in. It is built from the U.S. Bureau of Labor Statistics' wage survey and the Census Bureau's Supplemental Poverty Measure thresholds, which change with local rents.

We first published this map on January 29, 2026, built in Tableau from 2024 data. This version is rebuilt from scratch and adds four things. It shows every year from 2015 to 2025, so you can play it and see where the result got better or worse. It covers 521 areas in 2025, up from 383, by adding rural areas, Alaska and Hawaii. It lets you change the family and the housing. And it gives smaller metro areas a threshold based on their own rents.

::: blurb Read this first
This map is an illustration, not a poverty rate. Its purpose is to show how much room one paycheck leaves to absorb a surprise expense, once a family's most basic local costs are covered. It compares one job's pay before taxes with the local poverty threshold plus a cushion you set. It does not count taxes, a second earner, tax credits, food aid or housing aid, and it does not subtract child care, commuting or medical bills. So a shortfall does not mean a family is in poverty. It means one paycheck does not cover the threshold and the cushion together. Read it as a rough, illustrative guide.
:::

## Using the visualization

::: spacer

<iframe src="https://www.youtube-nocookie.com/embed/zkITTX8_02c?rel=0" width="100%" height="440" loading="lazy" style="border:0" title="How to use the Single Income Stress Test map (57-second video)" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

::: spacer

**1. Pick a year.** Drag the Year slider, or click Play to move through every year from 2015 to 2025. The button next to Play sets the speed: 1x, 2x or 3x.

**2. Pick the earner.** "Earner's place on the pay scale" chooses whose pay is tested. The 50th percentile is the median: half of jobs in the area pay more and half pay less. The 10th percentile is near the bottom of the pay scale and the 90th is near the top.

**3. Set the cushion.** "Money for surprise expenses" is the amount set aside for a car repair, a medical bill or a missed paycheck. It starts at $10,000 and goes from $0 to $25,000.

**4. Pick the family and the housing.** The Family box goes from one adult with no children to two adults with four children. The Housing box chooses a renter, an owner with a mortgage, or an owner with no mortgage. Each has its own threshold.

**5. Point at an area.** On a computer, move your mouse over it. On a phone or tablet, tap it. A box shows the math: income, less the threshold, less the cushion. The Area panel shows the same math and a chart of the area's income against its threshold plus cushion in every year.

**6. Find an area or pick a state.** Type a city name in "Find an area" and pick it from the list. "Show one state" zooms the map to one state and limits the rankings to it.

**7. See the change.** The Change view colors each area by how much its result moved between two years.

**8. Read the rankings.** The Rankings panel lists the 25 largest shortfalls and the 25 areas with the most room, nationally or for the state you picked. Click a name to zoom to it.

**9. Zoom and move around.** Use the + and − buttons, scroll with a mouse or trackpad, or pinch on a phone. Drag to move the map. Reset brings everything back to the start.

### How to read it

- **Excess or shortfall.** Annual income, less the local poverty threshold, less the cushion. Red areas fall short. Teal areas have room. Pale yellow areas are within $1,000 of breaking even.
- **Percent.** "Show as percent" divides income by the threshold plus the cushion. At 100%, the paycheck exactly covers both.
- **Local poverty threshold.** The Supplemental Poverty Measure threshold. It is higher where rents are higher. In 2025, for two adults and two children who rent, it ranged from $33,406 in Johnstown, PA to $61,763 in San Jose, CA.
- **Metro and nonmetro areas.** The map uses the Bureau of Labor Statistics' wage areas: 387 metro areas and 134 nonmetro areas in 2025. A nonmetro area is a group of rural counties in one state.
- **Hatched areas.** A diagonal hatch means the threshold is our estimate from that metro's own rents (see Step 4). You can switch these to the Census Bureau's state-level figure with "Small-metro thresholds."
- **Crosshatched areas.** In the Change view, a crosshatch means the two years cannot be compared, because the area's boundaries changed or its threshold came from a different kind of figure. In the one-year view, it marks the few areas with no threshold at all.
- **Dollars are not adjusted for inflation.** Each year uses that year's pay and that year's threshold. The cushion stays at the amount you set.

### What it shows right now

In 2025, for a median earner supporting two adults and two children in a rented home, with $10,000 set aside, one income falls short in 283 of 521 areas. Those areas hold 49% of the jobs. In 2015, it fell short in 346 of 551 areas, which held 40% of the jobs. The lowest share was in 2020, at 31%.

The cushion decides much of this. With no cushion, the median paycheck falls short of the threshold in 5 of 521 areas in 2025. With $5,000, it falls short in 66. With $20,000, it falls short in 515.

So does the earner's place on the pay scale. At the 25th percentile, one income falls short in all 521 areas in 2025. At the 75th percentile, it clears the threshold and the cushion in all of them.

Family size and housing matter as well. For one adult with two children, the median paycheck falls short in 35 areas. For two adults with three children, it falls short in 473. For a family that owns its home with no mortgage, it falls short in 40.

Thresholds rose faster than pay over these years. The national threshold for renters with two adults and two children went from $25,583 in 2015 to $41,701 in 2025, an increase of 63.0%. Among the 290 areas we can compare across both years, the median wage rose 45.8% in the typical area and the local threshold rose 60.9%. The wage rose faster than the threshold in 5 of the 290. The threshold follows what families spend on basics, so it can rise faster than prices.

### Cities where one income goes furthest, and where it falls short

These rankings use 2025, the median earner, two adults and two children, renters, and a $10,000 cushion.

Largest shortfalls:

1. Salinas, CA (short by $13,207)
2. Myrtle Beach-Conway-North Myrtle Beach, SC (short by $11,573)
3. Daphne-Fairhope-Foley, AL (short by $10,687)
4. Hilton Head Island-Bluffton-Port Royal, SC (short by $10,567)
5. Oxnard-Thousand Oaks-Ventura, CA (short by $10,478)
6. McAllen-Edinburg-Mission, TX (short by $9,996)
7. Santa Maria-Santa Barbara, CA (short by $9,876)
8. Miami-Fort Lauderdale-West Palm Beach, FL (short by $9,545)
9. Orlando-Kissimmee-Sanford, FL (short by $9,505)
10. Santa Cruz-Watsonville, CA (short by $9,496)

Most room:

1. West North Dakota nonmetropolitan area ($14,860 to spare)
2. San Jose-Sunnyvale-Santa Clara, CA ($12,287)
3. Seattle-Tacoma-Bellevue, WA ($12,116)
4. Rochester, MN ($10,980)
5. Washington-Arlington-Alexandria, DC-VA-MD-WV ($10,713)

High rents do not decide the result on their own. San Jose has the highest threshold on the map, $61,763, and the second-most room, because its median wage is $84,050. Salinas has a threshold of $50,587 and a median wage of $47,380.

Among the 36 metro areas with 1,000,000 or more jobs, one income falls short in 15. The largest shortfalls in that group are in Miami, Orlando, Riverside, Las Vegas and Los Angeles. The most room is in San Jose, Seattle and Washington, DC.

From 2015 to 2025, measured as a percent of threshold plus cushion, the largest gains among comparable areas were in Grants Pass, OR (87% to 105%), Yuma, AZ (79% to 95%) and the South Florida nonmetropolitan area (90% to 104%). The largest declines were in Trenton-Princeton, NJ (127% to 114%), Hanford-Corcoran, CA (111% to 99%) and San Jose (128% to 117%).

## What this page is

::: spacer

Every chart we publish should be something you can check, question and rebuild yourself. This page documents how we built this one: where the data comes from, every step we took, and the judgment calls we made. The code, the data and the built files are in a public repository, linked at the end.

## The data sources

::: spacer

**Occupational Employment and Wage Statistics (OEWS), U.S. Bureau of Labor Statistics.** A survey of employers that reports pay for every metro and nonmetro area. We use the figures for all occupations combined: annual pay at the 10th, 25th, 50th, 75th and 90th percentiles, and the number of jobs, for each May from 2015 to 2025. The same survey is behind our [chart of wage inequality by city and state](https://www.data4thepeople.com/p/lorenz-chart-viz).

**Supplemental Poverty Measure thresholds by metro area, U.S. Census Bureau.** For each year from 2015 to 2025, the poverty threshold for two adults and two children, for renters, owners with a mortgage and owners without one. The Bureau of Labor Statistics sets the national figure and the Census Bureau adjusts it for local rents.

**American Community Survey, table B25031, U.S. Census Bureau.** The median monthly rent for a two-bedroom home in every metro area, averaged over five years. We use it to estimate a threshold for metro areas that have no Census figure of their own (Step 4).

**OEWS area definitions, U.S. Bureau of Labor Statistics.** The list of counties, or New England towns, that make up each wage area in each year.

**Cartographic boundary files, U.S. Census Bureau.** Simplified county, town and state shapes, used only to draw the map.

## How we built it

::: spacer

### Step 0: What the agencies do before we get the data

We start from published estimates, so their limits are our limits.

The wage survey covers jobs on company payrolls. It does not cover the self-employed, owners of unincorporated businesses, or people who work for a private household. Annual pay is the hourly wage times 2,080 hours, before taxes. Each May estimate combines survey rounds collected over three years, so neighboring years share most of their data. With the May 2021 estimates, the Bureau of Labor Statistics also changed how it produces the numbers.

The Supplemental Poverty Measure threshold is not the official poverty line. It is based on what families spend on food, clothing, shelter, utilities, phone and internet, and it moves as that spending moves. It is not a fixed amount raised for inflation. The Census Bureau then adjusts the housing part of the threshold for each area, using the area's median rent for a two-bedroom home compared with the national median.

The Census Bureau publishes a threshold of its own for about 260 metro areas, the ones large enough to be identified in its household survey. Every other metro area shares one figure with all the other smaller metro areas in its state. All the rural areas in a state share one figure too.

### Step 1: Rebuild the original

We rebuilt the January map's method in Python and compared it with the data behind the published map: 383 metro areas at five pay levels for 2024. All 1,915 wage figures match. So do 357 of the 383 thresholds.

Two thresholds differ. Cleveland's was taken from the column for owners with a mortgage ($35,270) when the renter figure is $35,517. Prescott Valley-Prescott, AZ used the Arizona state figure ($41,316) when the Census Bureau publishes one for Prescott itself ($38,609), under an older name and code. The other 24 are small metro areas in states where the Census Bureau publishes no figure for smaller metro areas. The first version used the state's rural figure for them. This version estimates one from local rents (Step 4).

### Step 2: Pick the years

The Census Bureau posts its metro threshold file for 2015 and each year after. Each May wage estimate is set against the threshold for the same year. The map runs from 2015 to 2025.

### Step 3: Match each area to its threshold

The two agencies do not always use the same codes and names. For each area and year, we look for a threshold in this order:

- **A metro area the Census Bureau names.** Matched by code: 246 to 283 metro areas a year.
- **A metro area named under a different code.** Matched by hand, 18 cases. Four are metro areas that got new codes in 2024. Fourteen are in New England before 2024, when the wage survey built its areas from towns and the Census Bureau built its metro areas from counties. We matched each to the metro area with the same main city.
- **Any other metro area.** The state's figure for its smaller metro areas, or our estimate (Step 4).
- **A rural area.** The state's figure for its nonmetro areas.

### Step 4: Estimate a threshold for smaller metro areas

A state-level figure can be far from a single metro area's own costs. Olympia, WA and Bremerton, WA both got Washington's smaller-metro figure of $37,037 in 2024, though rents in the two are not the same.

The Census Bureau's adjustment follows a formula, which we confirmed against every published threshold in every year: the national threshold, with its housing share moved up or down by the area's rent compared with the national rent. The rent it uses is not public, but a close version is. So for each metro area with no figure of its own, we apply the same formula to the area's median two-bedroom rent from the American Community Survey.

To check the method, we ran it each year on the metro areas the Census Bureau does name. Our figure differed from the published one by $38 to $122 for the typical metro area, depending on the year, and by $1,869 at most. It runs slightly low.

For the metro areas that use it, the estimate can move the threshold a lot. In 2024 it is $7,943 lower than the state figure in Sierra Vista-Douglas, AZ, and $7,367 higher in Bremerton, WA. In 2025, 112 metro areas use an estimate. They are hatched on the map, and the box for each one shows the Census Bureau's state figure beside it, where one exists. Rural areas always use the Census Bureau's figure.

### Step 5: Scale for family size

The published thresholds are for two adults and two children. For other families, the Census Bureau uses a fixed scale, and we apply the same one. One adult is 46% of the two-adult, two-child figure. Two adults are 65%. One adult with two children is 83%. Two adults with three children are 111%.

A second adult adds less than a first because the scale assumes a couple shares one home and one set of bills. We checked the scale against the family-size table in each year's Census file. It matches to the dollar, apart from one cell in the 2015 file that does not follow the Census Bureau's own scale.

### Step 6: Draw each year on that year's boundaries

Wage areas change. The Bureau of Labor Statistics redrew its rural areas in 2018, and redrew many metro areas in 2024, when New England also moved from towns to counties. The map has five sets of boundaries and shows each year on the set that year used. Of the 626 areas that appear in any year, 320 keep the same outline for all 11 years.

When an area's boundaries change, its history chart breaks at that year, and a dotted line marks the change. Some places appear twice in the search box, with their years beside them, because the area before and after the change is not the same place.

The projection is Albers USA, which moves Alaska and Hawaii into the lower left.

### Step 7: Build the change view

The change view subtracts one year's result from another's. It compares an area only when the area existed in both years, had the same outline, and had the same kind of threshold. For 2015 to 2025, that leaves 290 areas: 248 metro areas and 42 rural ones. Most rural areas drop out because they were redrawn.

### Step 8: Check the numbers

Before publishing, a script recomputes the map's numbers from the source files and compares them with what the map shows: 29,150 wage figures, 16,821 thresholds and 4,041 estimates, with no differences. A second check, written separately from the raw files without using our scripts, reached the same wages, thresholds, estimates and headline counts. The numbers on this page come from a script that reads the same checked data.

## Updating

::: spacer

The Bureau of Labor Statistics releases new May wage estimates each spring, and the Census Bureau releases new thresholds each September. We plan to add 2026 when both are out. Every number on the map is computed by the build scripts.

## Honest notes and limitations

::: spacer

**This is an illustration, not a measurement of hardship.** The Census Bureau compares its threshold with a family's resources: income after taxes, plus tax credits and aid such as food and housing help, minus work expenses, child care and medical costs. This map compares it with one job's pay before taxes. That leaves out costs nearly every working family pays, which makes the paycheck look larger than it is. It also leaves out a second earner, tax credits and aid, which makes a family look worse off than it may be. We have not measured which effect is larger, and it will differ from family to family. Read each area's dollar figure as a rough, illustrative guide.

**One job is not one household.** The wage survey counts jobs, not families. It cannot say how many earners a family has, or whether the person at the median wage supports anyone else.

**Child care is not in the threshold.** That matters most for single parents. One adult with two children falls short in 35 areas in 2025, but a single parent who works may need to pay for child care, and the test does not subtract it.

**The threshold is not adjusted for inflation alone.** It follows what families spend on basics, so it can rise faster than prices. It rose 63.0% from 2015 to 2025. The share of the threshold that the Census Bureau adjusts for local rents also dropped in 2020, from about 50% to about 44% for renters, so local thresholds sit closer to the national figure from 2020 on. We did not adjust for either.

**The cushion does not grow.** The same $10,000 is a larger share of pay in 2015 than in 2025. That works in favor of later years, most of all in the Percent view.

**Neighboring years overlap.** Each May wage estimate uses three years of survey data, so a one-year change in one area is smoothed and should be read with caution. The 2021 change in method may also affect comparisons across that year.

**Our estimates are approximations.** They use public rent data that is close to, but not the same as, the rent the Census Bureau uses. For 2015 they use rents from one year later than the Census Bureau did, because the public table starts then. Five metro areas in 2015 and eight in 2016 have no rent figure and use the state figure.

**State figures are coarse.** Every rural area in a state shares one threshold, whatever its own rents.

**Boundaries change.** In 2024 the wage survey moved to new metro boundaries a year before the Census Bureau's threshold file did. A few metro areas that were split off or newly created that year get a state figure or an estimate, not the figure of the larger metro area they came from.

**No error bars.** The Bureau of Labor Statistics does not publish margins of error for wage percentiles, and the Census Bureau publishes none for its rent adjustment. Small differences between areas should not be read as real.

**The boundaries are simplified.** They are accurate at map scale, not for deciding which area a particular address is in.

## Reproduce it yourself

::: spacer

The code, the build steps and the published files are at [github.com/Data4ThePeople/SingleIncomeStressTest](https://github.com/Data4ThePeople/SingleIncomeStressTest). You need the OEWS "All data" files for May 2015 to May 2025, the Census Bureau's SPM threshold files for 2015 to 2025, a free Census API key for the rent table, the cartographic boundary files, and Python. Every step above is in the scripts, in order. If you get a different number from us, tell us, and we will look.

::: divider

## Common questions

::: spacer

### What is the Single Income Stress Test?

One person's annual pay, less the local poverty threshold for their family, less money set aside for surprise expenses. If the result is below zero, one income falls short in that area. You choose the pay level, the cushion, the family and the housing.

### Which poverty threshold does it use?

The Census Bureau's Supplemental Poverty Measure threshold, which is higher where rents are higher. In 2025 the national figure for two adults and two children who rent was $41,701. It is not the official poverty line, which is the same everywhere in the country. We wrote about how the official line was built in [Frozen in 1963](https://www.data4thepeople.com/p/frozen-in-1963/).

### Does a shortfall mean a family is in poverty?

No. The test uses one job's pay before taxes. It leaves out a second earner, tax credits and aid, and it leaves out taxes, child care and medical costs. It shows how far one paycheck goes against a local standard.

### Can a family of four live on one income?

It depends on where and on the paycheck. In 2025, a median earner with two adults and two children in a rented home and a $10,000 cushion falls short in 283 of 521 areas, which hold 49% of the jobs. With no cushion, the same paycheck falls short in 5.

### Where can a family live on one income?

By this test, in 2025 the median paycheck covers the local threshold for two adults and two children and a $10,000 cushion in 238 of 521 areas. The most room is in the West North Dakota nonmetropolitan area, San Jose, CA, Seattle, WA, Rochester, MN and Washington, DC. The test is against a poverty threshold plus a cushion, not a comfortable budget.

### Is there a poverty line for my city?

The official poverty line is the same everywhere in the country. The Census Bureau's Supplemental Poverty Measure threshold is not. It is higher where rents are higher, and this map shows it for every metro and rural area. Point at an area, or search for it, to see its figure.

### Is it getting better or worse?

The share of jobs in areas that fall short was 40% in 2015, 31% in 2020 and 49% in 2025, at the starting settings. Thresholds rose faster than pay: the national threshold rose 63.0% from 2015 to 2025, and the median wage rose 45.8% in the typical area we can compare.

### Are the dollars adjusted for inflation?

No. Each year uses that year's pay and that year's threshold. The Percent view makes years easier to compare, though the cushion you set stays the same in every year.

### Why is my metro area hatched?

The Census Bureau does not publish a threshold for it alone. The hatch means the threshold is our estimate from that metro area's own rents. The box for the area shows the Census Bureau's state-level figure as well.

### Why does my city appear twice in the search box?

Its boundaries changed, usually in 2024. The area before and after is not the same place, so each has its own history. The years are shown beside each name.

### Why does a second adult add so little to the threshold?

The Census Bureau's scale sets two adults at 41% more than one, because a couple shares one home and one set of bills. Costs that do rise with each person, such as taxes, commuting and medical bills, are not part of the threshold.

### How do I find my city?

Type its name in "Find an area" above the map and pick it from the list. The map zooms to it, and the Area panel shows the math and the history.

### Where does the data come from?

Pay is from the Bureau of Labor Statistics' Occupational Employment and Wage Statistics, May 2015 to May 2025. Thresholds are from the Census Bureau's Supplemental Poverty Measure, 2015 to 2025. Rents for our estimates are from the American Community Survey.

### How often is the map updated?

Once a year, after the Census Bureau releases the next year of thresholds each September.

### Can I embed the map?

Yes. It is free to use and embed. Add #embed=1 to the end of the full visualization's address for the 780-pixel version shown on this page.
