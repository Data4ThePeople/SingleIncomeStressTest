"""Numbers and static charts for the takeaways post (Day 2), from data/processed/map_data.json.

Settings unless stated: 2025, median earner, two adults and two children, renters, the page's
default thresholds (Census figure, or our rent-based estimate where Census names no figure).
Writes data/processed/takeaways.json and seven charts. Dark house palette, every chart titled,
legends as colored words. Run after 08_build_data.py; the post is checked against the JSON."""
import json
import statistics as st

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import PROC, RAW, REF, ROOT, STATE_INFO  # noqa: E402

SLUG = "five-takeaways-single-income"          # provisional until step 2a
OUT = ROOT / "posts" / SLUG / "images"
FS = 1.35
BG, INK, MUTED, GRID = "#181A1B", "#BBBDC0", "#8C9094", "#2A2E31"
RED, TEAL, YELLOW, GREY = "#e0604c", "#2a9d9b", "#f5e6a0", "#7a7f85"
plt.rcParams.update({"text.parse_math": False, "font.family": "DejaVu Sans", "text.color": INK,
                     "xtick.color": MUTED, "ytick.color": INK})
SRC = "Sources: BLS Occupational Employment and Wage Statistics; U.S. Census Bureau, SPM thresholds."
CREDIT = "Built by Data 4 The People"
BIG, CUSHION, SAME_JOBS = 1_000_000, 10000, 0.01

D = json.loads((PROC / "map_data.json").read_text())
Y, A = D["years"], D["areas"]
I0, I1 = 0, len(Y) - 1


def thr(a, i):
    t = a["est"][i] or a["th"][i]
    return t[0] if t else None


def kind(a, i):
    return "e" if a["est"][i] else a["k"][i]


def short(t):
    for cut in ["-Sunnyvale-Santa Clara", "-Newark-Jersey City", "-Oakland-Fremont", "-Sandy Springs-Roswell",
                "-Pasadena-The Woodlands", "-San Bernardino-Ontario", "-Vancouver-Hillsboro", "-Henderson-North Las Vegas",
                "-Arlington-Alexandria", "-Concord-Gastonia", "-Chula Vista-Carlsbad", "-Carmel-Greenwood",
                "-Fort Lauderdale-West Palm Beach", "-Kissimmee-Sanford", "-Long Beach-Anaheim", "-St. Petersburg-Clearwater",
                "-New Braunfels", "-Mesa-Chandler", "-Fort Worth-Arlington", "-Davidson--Murfreesboro--Franklin",
                "-Round Rock-San Marcos", "-Camden-Wilmington", "-Warren-Dearborn", "-Naperville-Elgin", "-Roseville-Folsom",
                "-Aurora-Centennial", "-Columbia-Towson", "-Cambridge-Newton", "-St. Paul-Bloomington", "-Tacoma-Bellevue"]:
        t = t.replace(cut, "")
    return t


# ---------- numbers ----------
def numbers():
    N = {}
    R = [(a, a["w"][I1], thr(a, I1), a["e"][I1] or 0) for a in A if a["w"][I1] and thr(a, I1)]
    jobs = sum(r[3] for r in R)
    N["areas"] = len(R)

    # 1. the cushion curve
    curve = []
    for c in range(0, 25001, 500):
        s = [r for r in R if r[1][2] - r[2] - c < 0]
        curve.append({"cushion": c, "areas": len(s), "jobs_pct": 100 * sum(r[3] for r in s) / jobs})
    room = sorted((r[1][2] - r[2], r[3]) for r in R)
    acc, wmed = 0, None
    for v, e in room:
        acc += e
        if acc >= jobs / 2:
            wmed = v
            break
    ex = next(r for r in R if r[0]["id"] == "17140")          # worked example in the post: Cincinnati
    example = {"name": ex[0]["n"], "wage": ex[1][2], "threshold": ex[2], "room": ex[1][2] - ex[2]}
    N["t1"] = {"example": example, "curve": curve, "room_median_area": st.median(v for v, _ in room), "room_median_job": wmed,
               "room_min": room[0][0], "room_max": room[-1][0]}

    # 2. pay levels with no cushion, and San Jose
    lv = []
    for p, name in enumerate(["10th", "25th", "50th", "75th", "90th"]):
        s = [r for r in R if r[1][p] - r[2] < 0]
        lv.append({"level": name, "areas": len(s), "jobs_pct": 100 * sum(r[3] for r in s) / jobs,
                   "median_gap": st.median(r[1][p] - r[2] for r in R)})
    sj = next(r for r in R if r[0]["id"] == "41940")
    drop = sorted(((r[1][2] - r[1][1], 100 * (1 - r[1][1] / r[1][2]), r[0]["n"]) for r in R if r[0]["t"] == 4), reverse=True)
    clears_med_not_25 = [r for r in R if r[1][2] - r[2] - CUSHION >= 0 and r[1][1] - r[2] < 0]
    N["t2"] = {"levels": lv,
               "san_jose": {"name": sj[0]["n"], "threshold": sj[2], "wages": sj[1], "median_room": sj[1][2] - sj[2],
                            "p25_gap": sj[1][1] - sj[2], "drop_dollars": sj[1][2] - sj[1][1],
                            "drop_pct": 100 * (1 - sj[1][1] / sj[1][2]),
                            "drop_rank_among_metros": 1 + [d[2] for d in drop].index(sj[0]["n"]), "metros": len(drop)},
               "largest_drops": [{"name": n, "dollars": d, "pct": p} for d, p, n in drop[:5]],
               "typical_drop_pct": st.median(d[1] for d in drop),
               "clear_10k_at_median_but_short_at_25th_no_cushion": len(clears_med_not_25),
               "clear_10k_at_median": sum(1 for r in R if r[1][2] - r[2] - CUSHION >= 0)}

    # 3. big metros in 2025
    big = sorted(({"name": r[0]["n"], "state": STATE_INFO[r[0]["s"]][0], "result": r[1][2] - r[2] - CUSHION,
                   "wage": r[1][2], "threshold": r[2], "jobs": r[3]} for r in R if r[0]["t"] == 4 and r[3] >= BIG),
                 key=lambda b: b["result"])
    by_state = {}
    for r in R:
        s = STATE_INFO[r[0]["s"]][0]
        d = by_state.setdefault(s, [0, 0])
        d[1] += r[3]
        if r[1][2] - r[2] - CUSHION < 0:
            d[0] += r[3]
    short_jobs = sum(v[0] for v in by_state.values())
    N["t3"] = {"big": big, "big_n": len(big), "big_short": sum(b["result"] < 0 for b in big),
               "short_states": sorted({b["state"] for b in big if b["result"] < 0}),
               "by_state": [{"state": s, "short_jobs": v[0], "share_of_short": 100 * v[0] / short_jobs, "share_of_state": 100 * v[0] / v[1]}
                            for s, v in sorted(by_state.items(), key=lambda kv: -kv[1][0])[:8]],
               "top3_share_of_short": 100 * sum(sorted((v[0] for v in by_state.values()), reverse=True)[:3]) / short_jobs}

    # 4. thresholds against pay over time: areas comparable 2015 to 2025 (same outline, same kind of threshold)
    cmp_ = [a for a in A if a["w"][I0] and a["w"][I1] and thr(a, I0) and thr(a, I1)
            and a["sh"][I0] == a["sh"][I1] and kind(a, I0) == kind(a, I1)]
    full = [a for a in cmp_ if all(a["w"]) and len(set(a["sh"])) == 1]
    series = []
    for i, y in enumerate(Y):
        series.append({"year": y, "national_threshold": D["nat"][i][0],
                       "threshold_pct": 100 * (D["nat"][i][0] / D["nat"][I0][0] - 1),
                       "wage_pct": st.median(100 * (a["w"][i][2] / a["w"][I0][2] - 1) for a in full),
                       "ratio": st.median(100 * a["w"][i][2] / thr(a, i) for a in full if thr(a, i))})
    yearly = [{"year": Y[i], "threshold": 100 * (D["nat"][i][0] / D["nat"][i - 1][0] - 1),
               "wage": st.median(100 * (a["w"][i][2] / a["w"][i - 1][2] - 1) for a in full)} for i in range(1, len(Y))]
    r0 = [100 * a["w"][I0][2] / thr(a, I0) for a in cmp_]
    r1 = [100 * a["w"][I1][2] / thr(a, I1) for a in cmp_]
    N["t4"] = {"comparable": len(cmp_), "full_history": len(full), "series": series, "yearly": yearly,
               "wage_growth_median": st.median(100 * (a["w"][I1][2] / a["w"][I0][2] - 1) for a in cmp_),
               "local_threshold_growth_median": st.median(100 * (thr(a, I1) / thr(a, I0) - 1) for a in cmp_),
               "ratio_2015": st.median(r0), "ratio_2025": st.median(r1),
               "ratio_fell": sum(b < a for a, b in zip(r0, r1)), "ratio_rose": sum(b > a for a, b in zip(r0, r1))}

    # top-down figures, Census Bureau, September 2026 (P60-289 table 2, P60-290 tables 3 and 8)
    inc = pd.read_excel(RAW / "census_p60" / "289_table2.xlsx", header=None)
    opm = pd.read_excel(RAW / "census_p60" / "290_table_3_opm_hist.xlsx", header=None)
    spm = pd.read_excel(RAW / "census_p60" / "290_table_8_spm_hist.xlsx", header=None)

    def first(d, year, col):          # the first row for the year is the "all races" block, newest method
        row = d[d[0].astype(str).str.strip().str.match(rf"^{year}(\s*\d)?$")].iloc[0]
        return float(row[col])

    N["top_down"] = {"official_poverty": {"2015": first(opm, 2015, 3), "2025": first(opm, 2025, 3)},
                     "spm_poverty": {"2015": first(spm, 2015, 4), "2025": first(spm, 2025, 4)},
                     "real_median_household_income": {"2015": first(inc, 2015, 12), "2025": first(inc, 2025, 12)},
                     "real_mean_household_income": {"2015": first(inc, 2015, 14), "2025": first(inc, 2025, 14)}}
    for k in ("real_median_household_income", "real_mean_household_income"):
        N["top_down"][k]["pct"] = 100 * (N["top_down"][k]["2025"] / N["top_down"][k]["2015"] - 1)

    # 5. big metros with stable boundaries: same outline, or the counties that moved hold under 1% of jobs
    bc = pd.read_csv(REF / "metro_boundary_change_2016_2025.csv", dtype={"area": str}).set_index("area")
    rows, left_out = [], []
    for a in A:
        if not (a["t"] == 4 and a["w"][I1] and (a["e"][I1] or 0) >= BIG):
            continue
        if not (a["w"][I0] and thr(a, I0)):
            left_out.append({"name": a["n"], "why": "not in the 2015 data under this code"})
            continue
        same = a["sh"][I0] == a["sh"][I1]
        moved = 0.0 if same else float(bc.change_share[a["id"]])
        if not same and moved >= SAME_JOBS:
            left_out.append({"name": a["n"], "why": f"counties that moved hold {100 * moved:.1f}% of jobs"})
            continue
        assert kind(a, I0) == kind(a, I1)
        rows.append({"name": a["n"], "same_outline": same, "jobs_moved_pct": 100 * moved,
                     "ratio_2015": 100 * a["w"][I0][2] / thr(a, I0), "ratio_2025": 100 * a["w"][I1][2] / thr(a, I1),
                     "result_2015": a["w"][I0][2] - thr(a, I0) - CUSHION, "result_2025": a["w"][I1][2] - thr(a, I1) - CUSHION,
                     "wage_pct": 100 * (a["w"][I1][2] / a["w"][I0][2] - 1), "threshold_pct": 100 * (thr(a, I1) / thr(a, I0) - 1)})
    for r in rows:
        r["change"] = r["ratio_2025"] - r["ratio_2015"]
    rows.sort(key=lambda r: r["change"])
    N["t5"] = {"metros": rows, "n": len(rows), "same_outline": sum(r["same_outline"] for r in rows), "left_out": left_out,
               "fell": sum(r["change"] < 0 for r in rows), "rose": sum(r["change"] > 0 for r in rows),
               "cleared_2015": sum(r["result_2015"] >= 0 for r in rows), "cleared_2025": sum(r["result_2025"] >= 0 for r in rows),
               "cleared_to_short": [r["name"] for r in rows if r["result_2015"] >= 0 > r["result_2025"]],
               "short_to_cleared": [r["name"] for r in rows if r["result_2015"] < 0 <= r["result_2025"]]}
    return N


# ---------- chart helpers ----------
def frame(title, subtitle, h=5.4):
    fig = plt.figure(figsize=(8, h), dpi=200, facecolor=BG)
    fig.text(0.04, 1 - 0.3 / h, title, fontsize=13.5 * FS, fontweight="bold", va="top")
    fig.text(0.04, 1 - 0.66 / h, subtitle, fontsize=8.4 * FS, color=MUTED, va="top", linespacing=1.3)
    return fig


def legend_words(fig, items, y):
    x = 0.04
    for lab, col in items:
        t = fig.text(x, y, lab, fontsize=8.6 * FS, color=col, fontweight="bold", va="top")
        fig.canvas.draw()
        x += t.get_window_extent().width / fig.bbox.width + 0.03


def footer(fig, source=SRC, note=None):
    if note:
        fig.text(0.04, 0.048, note, fontsize=6.2 * FS, color=MUTED)
    fig.text(0.04, 0.02, source, fontsize=6.2 * FS, color=MUTED)
    fig.text(0.96, 0.02, CREDIT, fontsize=6.2 * FS, color=MUTED, ha="right")


def clean(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_facecolor(BG)


def usd(v):
    return ("−" if v < 0 else "") + f"${abs(v):,.0f}"


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, facecolor=BG)
    plt.close(fig)
    print("  wrote", name)


# ---------- charts ----------
def chart_cushion(N):
    c = N["t1"]["curve"]
    fig = frame("The result turns on about $10,000",
                "Share of U.S. jobs in areas where one median paycheck falls short of the local poverty\nthreshold plus money for surprise expenses, 2025")
    ax = fig.add_axes([0.1, 0.2, 0.84, 0.55])
    clean(ax)
    x, y = [p["cushion"] for p in c], [p["jobs_pct"] for p in c]
    ax.plot(x, y, color=RED, lw=2.6)
    ax.fill_between(x, y, color=RED, alpha=0.12)
    for v in (0, 5000, 10000, 15000, 20000):
        p = next(q for q in c if q["cushion"] == v)
        ax.plot([v], [p["jobs_pct"]], "o", color=RED, ms=7, mec=BG, mew=1.5)
        lab = (f"{p['jobs_pct']:.0f}%" if v else f"{p['jobs_pct']:.1f}%") + " of jobs"
        if v == 0:                      # the curve leaves no room beside the first point: label it above, with a leader
            ax.annotate(lab, (v, p["jobs_pct"]), (1300, 24), fontsize=7.2 * FS, linespacing=1.25, va="bottom",
                        arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkB=4))
        else:                           # the other labels sit under the curve, to the right of their point
            ax.text(v + 650, p["jobs_pct"] - 4, lab, fontsize=7.2 * FS, ha="left", va="top", linespacing=1.25)
    ax.set_xlim(-600, 25600)
    ax.set_ylim(0, 108)
    ax.set_xticks(range(0, 25001, 5000))
    ax.set_xticklabels([f"${v // 1000}k" if v else "$0" for v in range(0, 25001, 5000)], fontsize=8 * FS)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8 * FS, color=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel("Money set aside for surprise expenses", fontsize=8 * FS, color=MUTED, labelpad=6)
    footer(fig, note="Median earner, two adults and two children, renting. Before taxes.")
    save(fig, "01-cushion-curve.png")


def chart_levels(N):
    lv = N["t2"]["levels"]
    fig = frame("Below the median, there is no cushion to speak of",
                "Share of U.S. jobs in areas where pay at each level is below the local poverty threshold\nfor two adults and two children, with nothing set aside, 2025", h=4.6)
    ax = fig.add_axes([0.31, 0.13, 0.6, 0.58])
    clean(ax)
    names = ["10th percentile", "25th percentile", "50th percentile (median)", "75th percentile", "90th percentile"]
    yy = np.arange(5)[::-1]
    vals = [p["jobs_pct"] for p in lv]
    ax.barh(yy, vals, color=RED, height=0.62)
    for y, p in zip(yy, lv):
        ax.text(p["jobs_pct"] + 1.5, y, f"{p['jobs_pct']:.1f}%   ({p['areas']} of {N['areas']} areas)" if 0 < p["jobs_pct"] < 100 else f"{p['jobs_pct']:.0f}%   ({p['areas']} of {N['areas']} areas)",
                va="center", fontsize=7.6 * FS)
    ax.set_yticks(yy)
    ax.set_yticklabels(names, fontsize=8 * FS)
    ax.set_xlim(0, 165)
    ax.set_xticks([])
    footer(fig, note="Renters. Before taxes.")
    save(fig, "02-pay-levels-no-cushion.png")


def chart_san_jose(N):
    s = N["t2"]["san_jose"]
    fig = frame("San Jose: room at the median, none a step below",
                "Annual pay at five points on the pay scale against the local poverty threshold for\ntwo adults and two children, San Jose-Sunnyvale-Santa Clara, CA, 2025", h=5.6)
    legend_words(fig, [("Above the threshold", TEAL), ("Below the threshold", RED)], 1 - 1.18 / 5.6)
    ax = fig.add_axes([0.08, 0.19, 0.86, 0.5])
    clean(ax)
    names = ["10th", "25th", "50th\n(median)", "75th", "90th"]
    w = s["wages"]
    cols = [TEAL if v >= s["threshold"] else RED for v in w]
    ax.bar(range(5), w, color=cols, width=0.62)
    for i, v in enumerate(w):
        ax.text(i, v + 2200, usd(v), ha="center", fontsize=8 * FS, fontweight="bold")
        gap = v - s["threshold"]
        ax.text(i, v / 2, ("+" if gap >= 0 else "") + usd(gap), ha="center", va="center", fontsize=7.4 * FS, color=BG, fontweight="bold")
    ax.axhline(s["threshold"], color=YELLOW, lw=1.6, ls=(0, (5, 3)))
    ax.text(-0.45, s["threshold"] + 3500, f"Local poverty threshold {usd(s['threshold'])}", ha="left", fontsize=7.6 * FS, color=YELLOW, fontweight="bold")
    ax.set_xticks(range(5))
    ax.set_xticklabels(names, fontsize=8 * FS)
    ax.set_yticks([])
    ax.set_ylim(0, max(w) * 1.1)
    ax.set_xlim(-0.5, 4.5)
    footer(fig, note="Numbers inside the bars: pay less the threshold, with nothing set aside. Renters. Before taxes.")
    save(fig, "03-san-jose-pay-scale.png")


def chart_big(N):
    b = N["t3"]["big"]
    h = 8.6
    fig = frame("Big metros that fall short: all South and West",
                f"One median paycheck, less the local poverty threshold, less $10,000, in the {len(b)} metro areas\nwith 1,000,000 or more jobs, 2025", h=h)
    legend_words(fig, [("Falls short", RED), ("Has room", TEAL)], 1 - 1.2 / h)
    ax = fig.add_axes([0.05, 0.06, 0.9, 0.78])
    clean(ax)
    yy = np.arange(len(b))[::-1]
    vals = [x["result"] for x in b]
    ax.barh(yy, vals, color=[RED if v < 0 else TEAL for v in vals], height=0.7)
    for y, x in zip(yy, b):
        v = x["result"]
        name = short(x["name"])
        if v < 0:
            ax.text(250, y, name, va="center", ha="left", fontsize=6.9 * FS)
            ax.text(v - 250, y, usd(v), va="center", ha="right", fontsize=6.9 * FS, color=MUTED)
        else:
            ax.text(-250, y, name, va="center", ha="right", fontsize=6.9 * FS)
            ax.text(v + 250, y, "+" + usd(v), va="center", ha="left", fontsize=6.9 * FS, color=MUTED)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlim(-16000, 16000)
    ax.set_ylim(-0.7, len(b) - 0.3)
    ax.set_xticks([])
    ax.set_yticks([])
    footer(fig, note="Two adults and two children, renting. Before taxes.")
    save(fig, "04-largest-metros-2025.png")


def chart_index(N):
    s = N["t4"]["series"]
    fig = frame("The poverty threshold rose faster than pay",
                f"Change since 2015 in the national poverty threshold (two adults and two children, renters)\nand in the median wage of the typical area ({N['t4']['full_history']} areas with unchanged boundaries)")
    legend_words(fig, [("Poverty threshold", RED), ("Median wage, typical area", TEAL)], 1 - 1.2 / 5.4)
    ax = fig.add_axes([0.09, 0.11, 0.78, 0.6])
    clean(ax)
    yrs = [p["year"] for p in s]
    for key, col in (("threshold_pct", RED), ("wage_pct", TEAL)):
        v = [p[key] for p in s]
        ax.plot(yrs, v, color=col, lw=2.6)
        ax.plot(yrs[-1:], v[-1:], "o", color=col, ms=7, mec=BG, mew=1.5)
        ax.text(yrs[-1] + 0.2, v[-1], f"+{v[-1]:.1f}%", color=col, fontsize=9 * FS, fontweight="bold", va="center")
    ax.set_xlim(2015, 2025.2)
    ax.set_ylim(0, 70)
    ax.set_xticks(yrs[::2])
    ax.set_xticklabels(yrs[::2], fontsize=8 * FS)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_yticklabels(["0%", "+20%", "+40%", "+60%"], fontsize=8 * FS, color=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    footer(fig, note="Dollars are not adjusted for inflation. The threshold follows what families spend on basics.")
    save(fig, "05-threshold-vs-pay.png")


def chart_top_down(N):
    t, r = N["top_down"], N["t4"]
    fig = frame("Two readings of the same ten years", "The national figures, and one paycheck against the local poverty threshold, 2015 and 2025", h=5.2)
    panels = [("Official poverty rate", "national", [t["official_poverty"]["2015"], t["official_poverty"]["2025"]], "{:.1f}%", TEAL, "Lower is better"),
              ("Median household income", "national, in 2025 dollars", [t["real_median_household_income"]["2015"], t["real_median_household_income"]["2025"]], "${:,.0f}", TEAL, "Higher is better"),
              ("Median wage as a percent\nof local poverty threshold", f"typical area of {r['comparable']}", [r["ratio_2015"], r["ratio_2025"]], "{:.0f}%", RED, "Higher is better")]
    for k, (name, sub, vals, fmt, col, hint) in enumerate(panels):
        ax = fig.add_axes([0.04 + k * 0.325, 0.22, 0.27, 0.4])
        clean(ax)
        ax.bar([0, 1], vals, color=[GREY, col], width=0.62)
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals) * 0.03, fmt.format(v), ha="center", fontsize=8.6 * FS, fontweight="bold")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["2015", "2025"], fontsize=8 * FS)
        ax.set_yticks([])
        ax.set_ylim(0, max(vals) * 1.18)
        ax.set_xlim(-0.6, 1.6)
        fig.text(0.04 + k * 0.325, 0.8, name, fontsize=7.8 * FS, fontweight="bold", va="top", linespacing=1.2)
        fig.text(0.04 + k * 0.325, 0.69, sub, fontsize=7 * FS, color=MUTED, va="top")
        fig.text(0.04 + k * 0.325 + 0.135, 0.125, hint, fontsize=7 * FS, color=MUTED, ha="center")
    footer(fig, source="BLS Occupational Employment and Wage Statistics; Census SPM thresholds.",
           note="Sources: U.S. Census Bureau, Poverty in the United States: 2025 and Income in the United States: 2025;")
    save(fig, "06-two-readings.png")


def chart_stable(N):
    m = N["t5"]["metros"]
    h = 8.0
    fig = frame("Every large metro we can compare lost ground",
                f"Median wage as a percent of the local poverty threshold, 2015 and 2025, in {len(m)} metro areas\nwith 1,000,000 or more jobs and stable boundaries. Bars show the change in percentage points.", h=h)
    legend_words(fig, [("Change, 2015 to 2025", RED), ("Went from clearing the $10,000 test to falling short", YELLOW)], 1 - 1.22 / h)
    ax = fig.add_axes([0.05, 0.06, 0.9, 0.75])
    clean(ax)
    yy = np.arange(len(m))[::-1]
    ax.barh(yy, [r["change"] for r in m], color=RED, height=0.68)
    for y, r in zip(yy, m):
        flip = r["result_2015"] >= 0 > r["result_2025"]
        ax.text(0.5, y, short(r["name"]), va="center", ha="left", fontsize=7 * FS, color=YELLOW if flip else INK,
                fontweight="bold" if flip else "normal")
        ax.text(r["change"] - 0.5, y, f"{r['ratio_2015']:.0f}% to {r['ratio_2025']:.0f}%", va="center", ha="right", fontsize=6.9 * FS, color=MUTED)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlim(-42, 26)
    ax.set_ylim(-0.7, len(m) - 0.3)
    ax.set_xticks([])
    ax.set_yticks([])
    footer(fig, note="Two adults and two children, renting. The $10,000 test: wage less threshold less $10,000.")
    save(fig, "07-large-metros-since-2015.png")


def hero(N):
    """Chart 1 re-rendered at hero scale (1412x812, which `hero pad` brings to 1680x1080 with 8% padding)."""
    c = N["t1"]["curve"]
    fig = plt.figure(figsize=(14.12, 8.12), dpi=100, facecolor=BG)
    fig.text(0.0, 0.985, "The result turns on about $10,000", fontsize=38, fontweight="bold", va="top")
    fig.text(0.0, 0.885, "Share of U.S. jobs in areas where one median paycheck falls short of the local\npoverty threshold plus money for surprise expenses, 2025",
             fontsize=20, color=MUTED, va="top", linespacing=1.3)
    ax = fig.add_axes([0.07, 0.17, 0.91, 0.54])
    clean(ax)
    x, y = [p["cushion"] for p in c], [p["jobs_pct"] for p in c]
    ax.plot(x, y, color=RED, lw=4.5)
    ax.fill_between(x, y, color=RED, alpha=0.12)
    for v in (0, 5000, 10000, 15000, 20000):
        p = next(q for q in c if q["cushion"] == v)
        ax.plot([v], [p["jobs_pct"]], "o", color=RED, ms=13, mec=BG, mew=2.5)
        lab = (f"{p['jobs_pct']:.0f}%" if v else f"{p['jobs_pct']:.1f}%") + " of jobs"
        if v == 0:
            ax.annotate(lab, (v, p["jobs_pct"]), (1300, 24), fontsize=20, va="bottom",
                        arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2, shrinkB=7))
        else:
            ax.text(v + 600, p["jobs_pct"] - 4, lab, fontsize=24 if v == 10000 else 20, ha="left", va="top",
                    fontweight="bold" if v == 10000 else "normal")
    ax.set_xlim(-600, 25600)
    ax.set_ylim(0, 108)
    ax.set_xticks(range(0, 25001, 5000))
    ax.set_xticklabels([f"${v // 1000}k" if v else "$0" for v in range(0, 25001, 5000)], fontsize=19)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=19, color=MUTED)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.set_xlabel("Money set aside for surprise expenses", fontsize=19, color=MUTED, labelpad=10)
    fig.text(0.0, 0.0, "The Single Income Stress Test: five takeaways  ·  Data 4 The People", fontsize=16, color=MUTED, va="bottom")
    fig.text(1.0, 0.0, "Sources: BLS, U.S. Census Bureau", fontsize=16, color=MUTED, va="bottom", ha="right")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{SLUG}-hero-source.png", facecolor=BG)
    plt.close(fig)
    print("  wrote", f"{SLUG}-hero-source.png")


def main():
    N = numbers()
    (PROC / "takeaways.json").write_text(json.dumps(N, indent=1))
    t1, t2, t3, t4, t5, td = N["t1"], N["t2"], N["t3"], N["t4"], N["t5"], N["top_down"]
    print(f"1. room at the median: typical area {usd(t1['room_median_area'])}, job-weighted {usd(t1['room_median_job'])}; "
          + "; ".join(f"${p['cushion']:,}: {p['areas']} areas, {p['jobs_pct']:.1f}%" for p in t1["curve"] if p["cushion"] % 5000 == 0))
    print("2. no cushion: " + "; ".join(f"{p['level']}: {p['areas']} areas, {p['jobs_pct']:.1f}% of jobs" for p in t2["levels"]))
    s = t2["san_jose"]
    print(f"   San Jose: threshold {usd(s['threshold'])}; wages {s['wages']}; median room {usd(s['median_room'])}; 25th gap {usd(s['p25_gap'])}; "
          f"median to 25th drop {usd(s['drop_dollars'])} ({s['drop_pct']:.1f}%), rank {s['drop_rank_among_metros']} of {s['metros']} metros; typical metro drop {t2['typical_drop_pct']:.1f}%")
    print("   largest median-to-25th drops:", [(d["name"], round(d["dollars"]), round(d["pct"], 1)) for d in t2["largest_drops"]])
    print(f"   of {t2['clear_10k_at_median']} areas that clear the $10,000 test at the median, {t2['clear_10k_at_median_but_short_at_25th_no_cushion']} are below the threshold at the 25th percentile with no cushion")
    print(f"3. big metros {t3['big_n']}, short {t3['big_short']}, states {t3['short_states']}; top 3 states hold {t3['top3_share_of_short']:.1f}% of short jobs")
    print("   ", [(b["state"], round(b["share_of_short"], 1), round(b["share_of_state"])) for b in t3["by_state"]])
    print(f"4. comparable {t4['comparable']} (full history {t4['full_history']}); wage +{t4['wage_growth_median']:.1f}%, local threshold +{t4['local_threshold_growth_median']:.1f}%; "
          f"ratio {t4['ratio_2015']:.0f}% to {t4['ratio_2025']:.0f}%; fell in {t4['ratio_fell']}, rose in {t4['ratio_rose']}")
    print("   yearly:", [(p["year"], round(p["threshold"], 1), round(p["wage"], 1)) for p in t4["yearly"]])
    print("   series end:", {k: round(v, 1) for k, v in t4["series"][-1].items()})
    print("   top-down:", json.dumps(td))
    print(f"5. stable big metros {t5['n']} ({t5['same_outline']} same outline); fell {t5['fell']}, rose {t5['rose']}; cleared $10k test {t5['cleared_2015']} then {t5['cleared_2025']}; "
          f"cleared to short {t5['cleared_to_short']}; short to cleared {t5['short_to_cleared']}")
    print("   left out:", t5["left_out"])
    for f in (chart_cushion, chart_levels, chart_san_jose, chart_big, chart_index, chart_top_down, chart_stable):      # hero() made the first, chart-based hero; the post now uses an AI image
        f(N)


if __name__ == "__main__":
    main()
