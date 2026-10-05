"""Every number quoted in posts/stress-test-viz/POST.md, computed from data/processed/map_data.json
with the page's default settings unless stated (rent-based estimates on, renters, two adults and
two children, $10,000 cushion). Run after 08_build_data.py; the post is checked against this output."""
import json
import statistics

from common import PROC

D = json.loads((PROC / "map_data.json").read_text())
Y = D["years"]
A = D["areas"]
PN = ["10th", "25th", "50th", "75th", "90th"]


def equiv(ad, kids):
    if kids == 0:
        return 1 if ad == 1 else 1.41 if ad == 2 else ad ** 0.7
    return (1.8 + 0.5 * (kids - 1)) ** 0.7 if ad == 1 else (ad + 0.5 * kids) ** 0.7


def kind(a, i, est=True):
    return "e" if est and a["est"][i] else a["k"][i]


def calc(a, y, p=2, ten=0, cush=10000, fam=(2, 2), est=True):
    i = Y.index(y)
    if not a["w"][i]:
        return None
    k = kind(a, i, est)
    if k == "x":
        return None
    base = (a["est"][i] if k == "e" else a["th"][i])[ten]
    thr = int(base * equiv(*fam) / equiv(2, 2) + 0.5)
    inc = a["w"][i][p]
    return {"inc": inc, "thr": thr, "dol": inc - thr - cush, "pct": 100 * inc / (thr + cush), "e": a["e"][i] or 0, "a": a}


def head(y, **kw):
    r = [c for c in (calc(a, y, **kw) for a in A) if c]
    s = [c for c in r if c["dol"] < 0]
    return len(s), len(r), 100 * sum(c["e"] for c in s) / sum(c["e"] for c in r)


def main():
    print("A. median earner, each year: short / areas with a figure / share of jobs")
    for y in Y:
        s, n, j = head(y)
        print(f"   {y}: {s} of {n}, {j:.1f}%   national renter threshold {D['nat'][Y.index(y)][0]:,}")
    n0, n1 = D["nat"][0][0], D["nat"][-1][0]
    print(f"   national renter threshold {Y[0]} to {Y[-1]}: {n0:,} to {n1:,}, +{100 * (n1 / n0 - 1):.1f}%")

    i = Y.index(2025)
    cur = [a for a in A if a["w"][i]]
    print(f"\nB. 2025 areas: {len(cur)} ({sum(a['t'] == 4 for a in cur)} metro, {sum(a['t'] == 6 for a in cur)} nonmetro); "
          f"threshold kinds: " + ", ".join(f"{k} {sum(kind(a, i) == k for a in cur)}" for k in "mens x".replace(" ", "")))
    print(f"   all areas ever: {len(A)}; areas with all 11 years on one outline: {sum(1 for a in A if all(a['w']) and len(set(a['sh'])) == 1)}")
    for p in range(5):
        s, n, j = head(2025, p=p)
        print(f"   2025, {PN[p]} percentile: short in {s} of {n}, {j:.1f}% of jobs")
    for label, kw in [("no cushion", {"cush": 0}), ("$5,000 cushion", {"cush": 5000}), ("$20,000 cushion", {"cush": 20000}),
                      ("owner with mortgage", {"ten": 1}), ("owner, no mortgage", {"ten": 2}),
                      ("one adult, two children", {"fam": (1, 2)}), ("one adult, one child", {"fam": (1, 1)}), ("two adults, no children", {"fam": (2, 0)}),
                      ("two adults, three children", {"fam": (2, 3)}), ("Census figures only", {"est": False})]:
        s, n, j = head(2025, **kw)
        print(f"   2025 median, {label}: short in {s} of {n}, {j:.1f}% of jobs")

    r = sorted((c for c in (calc(a, 2025) for a in A) if c), key=lambda c: c["dol"])
    lo, hi = min(r, key=lambda c: c["thr"]), max(r, key=lambda c: c["thr"])
    print(f"   2025 renter threshold range: {lo['thr']:,} ({lo['a']['n']}) to {hi['thr']:,} ({hi['a']['n']})")
    print("   family scale, share of the two-adult, two-child figure: " + ", ".join(
        f"{ad}A{k}C {100 * equiv(ad, k) / equiv(2, 2):.1f}%" for ad, k in [(1, 0), (2, 0), (1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (2, 4)]))
    print("\nC. 2025 largest shortfalls")
    for c in r[:10]:
        print(f"   {c['a']['n']}: {c['dol']:,} (income {c['inc']:,}, threshold {c['thr']:,})")
    print("   most room")
    for c in r[::-1][:10]:
        print(f"   {c['a']['n']}: {c['dol']:,} (income {c['inc']:,}, threshold {c['thr']:,})")
    big = [c for c in r if c["a"]["t"] == 4 and c["e"] >= 1_000_000]
    print(f"   metros with 1,000,000 or more jobs: {len(big)}; short: {sum(c['dol'] < 0 for c in big)}")
    for c in big:
        print(f"      {c['a']['n']}: {c['dol']:,} (income {c['inc']:,}, threshold {c['thr']:,}, {c['pct']:.0f}%)")

    print("\nD. change 2015 to 2025, areas with the same outline and the same kind of threshold in both years")
    i0 = 0
    cmp_ = []
    for a in A:
        b, c = calc(a, 2015), calc(a, 2025)
        if b and c and a["sh"][i0] == a["sh"][i] and kind(a, i0) == kind(a, i):
            cmp_.append((a, b, c))
    for m in ("dol", "pct"):
        up = sum(c[m] > b[m] for _, b, c in cmp_)
        dn = sum(c[m] < b[m] for _, b, c in cmp_)
        print(f"   {m}: {len(cmp_)} comparable; improved {up}, worsened {dn}")
    up2 = sum(c["pct"] - b["pct"] >= 2 for _, b, c in cmp_)
    dn2 = sum(c["pct"] - b["pct"] <= -2 for _, b, c in cmp_)
    print(f"   percent measure, moved 2 points or more: up {up2}, down {dn2}, within 2 points {len(cmp_) - up2 - dn2}")
    print(f"   of the comparable areas: {sum(a['t'] == 4 for a, _, _ in cmp_)} metro, {sum(a['t'] == 6 for a, _, _ in cmp_)} nonmetro")
    wg = [100 * (c["inc"] / b["inc"] - 1) for _, b, c in cmp_]
    tg = [100 * (c["thr"] / b["thr"] - 1) for _, b, c in cmp_]
    print(f"   median wage growth across them: median {statistics.median(wg):.1f}%; local threshold growth: median {statistics.median(tg):.1f}%; "
          f"wage grew faster than threshold in {sum(w > t for w, t in zip(wg, tg))}")
    s15 = sum(b["dol"] < 0 for _, b, c in cmp_)
    s25 = sum(c["dol"] < 0 for _, b, c in cmp_)
    print(f"   short in 2015: {s15}; short in 2025: {s25}; short to not short: {sum(b['dol'] < 0 <= c['dol'] for _, b, c in cmp_)}; "
          f"not short to short: {sum(c['dol'] < 0 <= b['dol'] for _, b, c in cmp_)}")
    ch = sorted(cmp_, key=lambda t: t[2]["pct"] - t[1]["pct"])
    print("   largest declines, percent of threshold plus cushion")
    for a, b, c in ch[:6]:
        print(f"      {a['n']}: {b['pct']:.0f}% to {c['pct']:.0f}% ({c['pct'] - b['pct']:+.1f}); dollars {b['dol']:,} to {c['dol']:,}")
    print("   largest gains")
    for a, b, c in ch[::-1][:6]:
        print(f"      {a['n']}: {b['pct']:.0f}% to {c['pct']:.0f}% ({c['pct'] - b['pct']:+.1f}); dollars {b['dol']:,} to {c['dol']:,}")

    print("\nE. spot values")
    for aid, y in [("22380", 2024), ("17140", 2025), ("41940", 2025), ("36500", 2024)]:
        a = next(x for x in A if x["id"] == aid)
        c = calc(a, y)
        j = Y.index(y)
        print(f"   {a['n']} {y}: income {c['inc']:,}, threshold {c['thr']:,} [{kind(a, j)}; Census row {a['sp'][j]}: {a['th'][j][0] if a['th'][j] else None}], result {c['dol']:,}, {c['pct']:.0f}%")
    a = next(x for x in A if x["id"] == "17140")
    for fam in [(1, 0), (2, 0), (2, 2)]:
        print(f"   Cincinnati 2025 threshold, {fam}: {calc(a, 2025, fam=fam)['thr']:,}")


if __name__ == "__main__":
    main()
