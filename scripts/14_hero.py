"""Hero source image: the 2025 map at the page's starting settings, rendered at hero scale
(1680x1080) in the dark house palette, with the title and the headline figure beside it.
`hero pad` then adds the padding.

Same data, class breaks and colors as the viz (median earner, two adults and two children, renters,
$10,000 cushion, rent-based estimates on). The hatch that marks estimated thresholds on the page is
left off here; the fills are the same."""
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

from common import PROC, ROOT  # noqa: E402

OUT = ROOT / "posts" / "stress-test-viz" / "images" / "stress-test-viz-hero-source.png"
BG, INK, MUTED = "#181A1B", "#BBBDC0", "#8C9094"
RAMP = ["#a52a24", "#e0604c", "#f6b8a8", "#f5e6a0", "#a0dad6", "#2a9d9b", "#00646b"]   # viz --neg3..--pos3
NONE, STATE = "#50565A", "#181A1B"
BINS = [-10000, -5000, -1000, 1000, 5000, 10000]
YEAR, CUSHION = 2025, 10000


def rings(polys, outer_only=False):
    for poly in polys:
        for r in (poly[:1] if outer_only else poly):
            yield np.cumsum(np.array(r, dtype=float).reshape(-1, 2), axis=0)


def area(xy):
    x, y = xy[:, 0], xy[:, 1]
    return abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) / 2


def main():
    md = json.loads((PROC / "map_data.json").read_text())
    i = md["years"].index(YEAR)
    geo = next(e["geo"] for e in md["eras"] if e["from"] <= YEAR <= e["to"])
    polys, cols = [], []
    n = short = jobs = short_jobs = 0
    for a in md["areas"]:
        if not a["w"][i]:
            continue
        thr = a["est"][i] or a["th"][i]
        if thr:
            v = a["w"][i][2] - thr[0] - CUSHION
            col = RAMP[int(np.searchsorted(BINS, v, side="right"))]
            n += 1
            jobs += a["e"][i] or 0
            if v < 0:
                short += 1
                short_jobs += a["e"][i] or 0
        else:
            col = NONE
        for r in rings(geo[a["id"]], outer_only=True):
            polys.append(r)
            cols.append(col)
    share = 100 * short_jobs / jobs
    assert (short, n) == (283, 521) and round(share) == 49, (short, n, share)    # matches the tie-out and the page
    order = np.argsort([-area(r) for r in polys])
    polys, cols = [polys[k] for k in order], [cols[k] for k in order]
    borders = [r for b in md["borders"] for r in rings(b)]
    allxy = np.vstack(polys)
    x0, y0 = allxy.min(0)
    x1, y1 = allxy.max(0)

    plt.rcParams.update({"text.parse_math": False, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(16.8, 10.8), dpi=100, facecolor=BG)
    ax = fig.add_axes([0.01, 0.17, 0.63, 0.74], facecolor=BG)
    ax.set_anchor("N")
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors=BG, linewidths=0.35))
    ax.add_collection(PolyCollection(borders, facecolors="none", edgecolors=STATE, linewidths=1.1))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)            # grid y points down
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(0.03, 0.94, f"One income, less the local poverty threshold, less $10,000, {YEAR}", fontsize=27, fontweight="bold", color=INK)

    lx, ly, lw, lh = 0.10, 0.105, 0.42, 0.028
    for k, c in enumerate(RAMP):
        fig.patches.append(plt.Rectangle((lx + k * lw / 7, ly), lw / 7, lh, transform=fig.transFigure, color=c, figure=fig))
    for k, b in enumerate(BINS):
        fig.text(lx + (k + 1) * lw / 7, ly - 0.012, ("−" if b < 0 else "+") + f"${abs(b) // 1000}k", fontsize=17, color=INK, ha="center", va="top")
    fig.text(lx, ly + lh + 0.012, "Falls short", fontsize=16, color=MUTED, va="bottom")
    fig.text(lx + lw, ly + lh + 0.012, "Has room", fontsize=16, color=MUTED, va="bottom", ha="right")

    tx = 0.66
    fig.text(tx, 0.80, "The Single\nIncome\nStress Test", fontsize=50, fontweight="bold", color=INK, va="top", linespacing=1.05)
    fig.text(tx, 0.47, f"{share:.0f}%", fontsize=72, fontweight="bold", color=RAMP[1], va="top")
    fig.text(tx, 0.345, f"of jobs are in areas where one\nmedian paycheck falls short in {YEAR}", fontsize=22, color=INK, va="top", linespacing=1.25)
    fig.text(tx, 0.225, "Two adults and two children, renting,\nwith $10,000 for surprise expenses", fontsize=18, color=MUTED, va="top", linespacing=1.35)
    fig.text(tx, 0.075, "Data 4 The People  ·  Sources: BLS, U.S. Census Bureau", fontsize=14, color=MUTED)
    os.makedirs(OUT.parent, exist_ok=True)
    fig.savefig(OUT, facecolor=BG)
    print("wrote", OUT, f"{short} of {n} areas, {share:.1f}% of jobs")


if __name__ == "__main__":
    main()
