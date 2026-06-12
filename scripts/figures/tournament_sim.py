#!/usr/bin/env python3
"""Synthetic Stars tournament for the Lucas critique post.

Generates the "the threshold moves with the field" figure for
src/content/blog/lucas-critique-stars-forecasting.md. Everything here is
synthetic: invented contracts, two generic measures, percentile cut points.
No real plan data, no real cut points, no proprietary methodology. The
point is the textbook tournament mechanic, not calibration.

Setup
-----
N contracts each split a fixed effort budget between two measures, A and B,
with diminishing returns to effort. Star thresholds on each measure are
relative: fixed percentiles of the field's score distribution, recomputed
every round (a stand-in for CMS's clustering). A contract's overall rating
index is the weight-averaged measure star. Contracts best-respond to last
year's cut points. Measure B starts under-weighted (the pre-2023
patient-experience situation in caricature), then jumps to dominant weight.

Experiment
----------
Burn in under the old weights until allocations settle. Then raise the
weight on measure B and compute, for every contract:
  mechanical projection: the contract re-optimizes its own effort split,
    competitors frozen at pre-change behavior, cut points recomputed on
    that counterfactual field;
  equilibrium outcome: every contract re-optimizes simultaneously, cut
    points recomputed on the field that actually results.
The comparison step is deterministic comparative statics (no fresh noise),
so the gap between the two worlds is pure mechanism: the Lucas critique
in miniature.

Output: summary stats to stdout, figure SVG to stdout with --svg.
Deterministic (seeded); stdlib only.
"""

import argparse
import random
import statistics

SEED = 20260612
N = 120                      # contracts
BASE_MEAN, BASE_SD = 62.0, 7.0
GAIN = 14.0                  # score lift at full effort on a measure
NOISE = 2.0                  # per-round score noise during burn-in
EFF_GRID = [i / 20 for i in range(21)]   # effort share on B
PCTS = [10, 35, 65, 85]      # percentile thresholds for 2..5 stars
BURN_IN = 10
W_PRE = {"A": 3.0, "B": 1.5}
W_POST = {"A": 3.0, "B": 4.0}


def percentile(sorted_vals, p):
    """Linear-interpolated percentile, p in [0, 100]."""
    k = (len(sorted_vals) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def cut_points(scores):
    s = sorted(scores)
    return [percentile(s, p) for p in PCTS]


def stars(score, cuts):
    return 1 + sum(score >= c for c in cuts)


def mean_score(base, eff_b, on_b):
    eff = eff_b if on_b else 1 - eff_b
    return base + GAIN * eff ** 0.5


def rating(scores_ab, cuts_ab, w):
    sa = stars(scores_ab[0], cuts_ab[0])
    sb = stars(scores_ab[1], cuts_ab[1])
    return (w["A"] * sa + w["B"] * sb) / (w["A"] + w["B"])


def best_response(base_a, base_b, cuts_ab, w):
    """Effort split maximizing expected rating against given cut points.

    Ties break toward the balanced split so the steady state is not an
    artifact of grid order.
    """
    best, best_e = -1.0, 0.5
    for e in EFF_GRID:
        r = rating(
            (mean_score(base_a, e, False), mean_score(base_b, e, True)),
            cuts_ab, w)
        if r > best + 1e-12 or (abs(r - best) <= 1e-12
                                and abs(e - 0.5) < abs(best_e - 0.5)):
            best, best_e = r, e
    return best_e


def realize(bases, efforts, rng):
    """Noisy scores for the whole field given effort splits (burn-in)."""
    out = []
    for (ba, bb), e in zip(bases, efforts):
        out.append((mean_score(ba, e, False) + rng.gauss(0, NOISE),
                    mean_score(bb, e, True) + rng.gauss(0, NOISE)))
    return out


def field_cuts(scores):
    return (cut_points([s[0] for s in scores]),
            cut_points([s[1] for s in scores]))


def run():
    rng = random.Random(SEED)
    bases = [(rng.gauss(BASE_MEAN, BASE_SD), rng.gauss(BASE_MEAN, BASE_SD))
             for _ in range(N)]

    efforts = [0.5] * N
    scores = realize(bases, efforts, rng)
    cuts = field_cuts(scores)
    for _ in range(BURN_IN):
        efforts = [best_response(ba, bb, cuts, W_PRE) for ba, bb in bases]
        scores = realize(bases, efforts, rng)
        cuts = field_cuts(scores)

    pre_ratings = [rating(s, cuts, W_PRE) for s in scores]
    pre_b_stars = [stars(scores[i][1], cuts[1]) for i in range(N)]

    def det(i, e):
        ba, bb = bases[i]
        return (mean_score(ba, e, False), mean_score(bb, e, True))

    new_efforts = [best_response(ba, bb, cuts, W_POST) for ba, bb in bases]

    predicted, mech_b_stars, mech_cut4 = [], [], []
    for i in range(N):
        # contract i re-optimizes; everyone else frozen at old behavior
        cf = [det(j, new_efforts[j] if j == i else efforts[j])
              for j in range(N)]
        cf_cuts = field_cuts(cf)
        predicted.append(rating(cf[i], cf_cuts, W_POST) - pre_ratings[i])
        mech_b_stars.append(stars(cf[i][1], cf_cuts[1]))
        mech_cut4.append(cf_cuts[1][2])

    eq_scores = [det(i, new_efforts[i]) for i in range(N)]
    eq_cuts = field_cuts(eq_scores)
    realized = [rating(eq_scores[i], eq_cuts, W_POST) - pre_ratings[i]
                for i in range(N)]
    eq_b_stars = [stars(eq_scores[i][1], eq_cuts[1]) for i in range(N)]

    projectors = [i for i in range(N) if mech_b_stars[i] > pre_b_stars[i]]
    realizers = [i for i in projectors if eq_b_stars[i] > pre_b_stars[i]]

    return {
        "mean_b_pre": statistics.mean(s[1] for s in scores),
        "mean_b_eq": statistics.mean(s[1] for s in eq_scores),
        "cut4_pre": cuts[1][2],
        "cut4_mech": statistics.mean(mech_cut4),
        "cut4_eq": eq_cuts[1][2],
        "n_projectors": len(projectors),
        "n_realizers": len(realizers),
        "mean_predicted": statistics.mean(predicted),
        "mean_realized": statistics.mean(realized),
        "effort_pre": statistics.mean(efforts),
        "effort_post": statistics.mean(new_efforts),
    }


def summarize(r):
    lines = [
        f"contracts: {N}",
        f"mean effort share on B: {r['effort_pre']:.2f} pre-change"
        f" -> {r['effort_post']:.2f} post-change",
        f"mean measure-B score: {r['mean_b_pre']:.1f} pre-change"
        f" -> {r['mean_b_eq']:.1f} equilibrium"
        f" ({r['mean_b_eq'] - r['mean_b_pre']:+.1f})",
        f"4-star cut point on B: {r['cut4_pre']:.1f} pre-change,"
        f" {r['cut4_mech']:.1f} mechanical recomputation"
        f" ({r['cut4_mech'] - r['cut4_pre']:+.1f}),"
        f" {r['cut4_eq']:.1f} equilibrium"
        f" ({r['cut4_eq'] - r['cut4_pre']:+.1f})",
        f"contracts projecting a measure-B star gain: {r['n_projectors']}",
        f"of those, realizing it in equilibrium: {r['n_realizers']}",
        f"mean projected rating change (mechanical): {r['mean_predicted']:+.3f}",
        f"mean realized rating change (equilibrium): {r['mean_realized']:+.3f}",
    ]
    return "\n".join(lines)


def svg(r):
    """Dumbbell chart: the score moves, the threshold moves further."""
    lo, hi = 68.0, 80.0
    x0, x1 = 240, 700

    def sx(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    rows = [
        ("Average contract, measure-B score",
         r["mean_b_pre"], r["mean_b_eq"], "#111", 120),
        ("4-star threshold, mechanical recomputation",
         r["cut4_pre"], r["cut4_mech"], "#6a6a6a", 190),
        ("4-star threshold, equilibrium",
         r["cut4_pre"], r["cut4_eq"], "#7a0000", 260),
    ]
    parts = []
    for label, a, b, color, y in rows:
        parts.append(
            f'  <text x="20" y="{y - 24}" font-size="13" fill="#111">{label}</text>')
        parts.append(
            f'  <line x1="{sx(a):.1f}" y1="{y}" x2="{sx(b):.1f}" y2="{y}"'
            f' stroke="{color}" stroke-width="2.2"/>')
        parts.append(
            f'  <circle cx="{sx(a):.1f}" cy="{y}" r="4" fill="none"'
            f' stroke="{color}" stroke-width="1.6"/>')
        parts.append(
            f'  <circle cx="{sx(b):.1f}" cy="{y}" r="4.5" fill="{color}"/>')
        parts.append(
            f'  <text x="{sx(a):.1f}" y="{y - 10}" font-size="11"'
            f' fill="#6a6a6a" text-anchor="middle">{a:.1f}</text>')
        parts.append(
            f'  <text x="{sx(b) + (14 if b >= a else -14):.1f}" y="{y + 4}"'
            f' font-size="11" fill="{color}"'
            f' text-anchor="{"start" if b >= a else "end"}">'
            f'{b:.1f} ({b - a:+.1f})</text>')
    body = "\n".join(parts)
    axis_ticks = "\n".join(
        f'  <text x="{sx(v):.1f}" y="318" font-size="10" fill="#6a6a6a"'
        f' text-anchor="middle">{v:.0f}</text>'
        for v in range(int(lo), int(hi) + 1, 2))
    return f"""<figure>
<svg viewBox="0 0 760 380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Dumbbell chart from a synthetic tournament of {N} contracts. After a weight increase on measure B, the average contract improves its measure-B score from {r['mean_b_pre']:.1f} to {r['mean_b_eq']:.1f}. The 4-star threshold barely moves under mechanical recomputation with competitors frozen, from {r['cut4_pre']:.1f} to {r['cut4_mech']:.1f}, but rises from {r['cut4_pre']:.1f} to {r['cut4_eq']:.1f} in equilibrium when every contract re-optimizes. The threshold outruns the average improvement." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="24" font-size="11" letter-spacing="1.4" fill="#6a6a6a">A SYNTHETIC TOURNAMENT: THE THRESHOLD MOVES WITH THE FIELD</text>
  <text x="20" y="44" font-size="11" font-style="italic" fill="#6a6a6a">weight on measure B rises; every contract re-allocates toward it</text>
{body}
  <line x1="{x0}" y1="300" x2="{x1}" y2="300" stroke="#d0d0c8" stroke-width="1"/>
{axis_ticks}
  <text x="{(x0 + x1) / 2:.0f}" y="344" font-size="11" font-style="italic" fill="#6a6a6a" text-anchor="middle">measure-B score (synthetic units)</text>
  <text x="20" y="344" font-size="11" font-style="italic" fill="#6a6a6a">{r['n_projectors']} of {N} contracts project a</text>
  <text x="20" y="360" font-size="11" font-style="italic" fill="#6a6a6a">measure-star gain; {r['n_realizers']} realize it.</text>
</svg>
</figure>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg", action="store_true", help="emit the figure SVG")
    args = ap.parse_args()
    res = run()
    if args.svg:
        print(svg(res))
    else:
        print(summarize(res))
