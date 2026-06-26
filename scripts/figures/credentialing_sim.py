#!/usr/bin/env python3
"""Computed figures for the credentialing-validity post.

Generates the four inline SVG figures for
src/content/blog/credentialing-validity.md. The argument of that post is
statistical, so the charts are computed from stated formulas on seeded,
clearly-labelled SIMULATED data, never drawn by hand. The OPPE yield panel is
the one exception: it reports published figures, no simulation.

Conventions match scripts/figures/tournament_sim.py: stdlib only, deterministic
(seeded), emits the figure SVG to stdout. The emitted SVG uses the site's
palette-adapter contract (presentation hexes #111, #6a6a6a, #7a0000, #d0d0c8,
which blog.css remaps to var(--text/--muted/--accent/--rule) for dark mode) and
carries a role="img" aria-label. No blank lines inside any <svg> (the blog lint
forbids them).

Why stdlib instead of NumPy: the binomial draws are just sums of Bernoulli
trials, the lognormal is random.lognormvariate, and the only "fancy" numbers are
two fixed normal quantiles. Keeping it stdlib means the figure generator carries
no dependency the rest of the blog pipeline does not already have.

Usage:
  python scripts/figures/credentialing_sim.py                 # summary stats
  python scripts/figures/credentialing_sim.py --emit reliability
  python scripts/figures/credentialing_sim.py --emit funnel
  python scripts/figures/credentialing_sim.py --emit quartile
  python scripts/figures/credentialing_sim.py --emit oppe
"""

import argparse
import math
import random

# --------------------------------------------------------------------------
# Global parameters. One seed governs every random draw, so re-running
# reproduces identical figures. The seed is printed by the summary path.
# --------------------------------------------------------------------------
SEED = 20260626

# Reliability model (Chart 1). A physician-level measure splits into true
# between-physician variance and measurement error that shrinks as 1/n:
#     R(n) = var_between / (var_between + var_within / n)
# The ratio 45:1 is chosen ILLUSTRATIVELY so that reliability near 30 cases
# lands in the 0.3-0.5 range the literature reports; the values are stated on
# the chart so nothing is hidden.
VAR_BETWEEN = 1.0
VAR_WITHIN = 45.0

# Funnel / quartile model (Charts 2 and 3). Every provider shares ONE true
# event rate; all spread is sampling noise. Caseloads are skewed (most see few
# cases, a few see many): lognormal with the stated median and a long tail.
N_PROVIDERS = 300
P0 = 0.03                 # shared true event rate, 3 percent (realistic, low)
LOGNORM_MEDIAN = 30.0     # median caseload; lognormal median is exp(mu)
LOGNORM_SIGMA = 0.6       # spread on the log scale -> long right tail
VOLUME_FLOOR = 5          # keep tiny-volume providers off n=0 (undefined rate)
Z95 = 1.959964            # 95% two-sided normal quantile
Z998 = 3.090232           # 99.8% two-sided normal quantile (funnel outer limit)

# OPPE yield panel (Chart 4): published figures, not simulation.
OPPE_PROVIDERS = 12854
OPPE_OUTLIERS = 0
OPPE_COST_PER_PROVIDER = 50      # ~$50.20/provider as reported
OPPE_NATIONAL_COST_M = 78        # ~$78.54M/year as reported

SIM_NOTE = "Illustrative simulation, not real provider data."


def reliability(n):
    """R(n) = var_between / (var_between + var_within / n)."""
    return VAR_BETWEEN / (VAR_BETWEEN + VAR_WITHIN / n)


def simulate(rng):
    """Draw the shared cohort used by both the funnel and the slopegraph.

    Volumes are lognormal (skewed) and floored. Each provider's event count for
    a year is Binomial(n, p0), sampled as a sum of n Bernoulli(p0) trials, which
    is the exact binomial without pulling in a stats library. Returns the volume
    vector and two INDEPENDENT years of observed rates from the identical true
    rate, so any year-to-year movement is pure noise.
    """
    n = [max(VOLUME_FLOOR,
             round(rng.lognormvariate(math.log(LOGNORM_MEDIAN), LOGNORM_SIGMA)))
         for _ in range(N_PROVIDERS)]

    def year():
        # events_i ~ Binomial(n_i, p0); observed rate = events_i / n_i
        return [sum(rng.random() < P0 for _ in range(ni)) / ni for ni in n]

    return n, year(), year()


def quartiles(rates, rng):
    """Sort observed rates into 4 equal groups (1 = lowest rate ... 4 = highest).

    Low-volume providers pile up at exactly 0 observed events, so ties are heavy.
    Ties are broken with fresh uniform draws, which is the honest treatment: with
    no real signal there is no true order among tied providers, so a random split
    keeps the four groups equal without inventing a ranking. Returns a quartile
    label per provider in original order.
    """
    keyed = [(r, rng.random(), i) for i, r in enumerate(rates)]
    keyed.sort()  # by rate, then random tiebreak
    q = [0] * len(rates)
    for rank, (_, _, i) in enumerate(keyed):
        q[i] = rank * 4 // len(rates) + 1
    return q


# --------------------------------------------------------------------------
# Tiny SVG helpers. Coordinates are computed; nothing is hand-placed.
# --------------------------------------------------------------------------
def poly_len(pts):
    """Total path length of a polyline, for the stroke-dash draw animation."""
    return sum(math.dist(pts[k], pts[k + 1]) for k in range(len(pts) - 1))


def pts_str(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


# ============================ CHART 1: RELIABILITY =========================
def svg_reliability():
    W, H = 760, 400
    x0, x1 = 95, 700          # plot x range (pixels)
    yT, yB = 60, 330          # plot y range: yT = R 1.0, yB = R 0.0
    lo_n, hi_n = 1.0, 500.0
    logspan = math.log10(hi_n)

    def sx(n):
        return x0 + math.log10(n) / logspan * (x1 - x0)

    def sy(r):
        return yB - r * (yB - yT)

    # The reliability curve, sampled densely on a log grid and computed at every
    # point. R(n) = var_between / (var_between + var_within / n).
    grid = [10 ** (i / 200 * logspan) for i in range(201)]
    curve = [(sx(n), sy(reliability(n))) for n in grid]

    r30 = reliability(30)
    r20, r50 = reliability(20), reliability(50)

    p = []
    p.append(f'  <text x="20" y="24" font-size="11" letter-spacing="1.4" '
             f'fill="#6a6a6a">RELIABILITY OF A PHYSICIAN-LEVEL SCORE RISES '
             f'SLOWLY WITH CASELOAD</text>')
    p.append(f'  <text x="20" y="44" font-size="11" font-style="italic" '
             f'fill="#6a6a6a">R(n) = var_between / (var_between + var_within / '
             f'n), with var_between = 1, var_within = 45</text>')
    # Realistic-volume band, 20 to 50 cases.
    p.append(f'  <rect x="{sx(20):.1f}" y="{yT}" width="{sx(50) - sx(20):.1f}" '
             f'height="{yB - yT}" fill="#6a6a6a" opacity="0.10"/>')
    p.append(f'  <text x="{(sx(20) + sx(50)) / 2:.1f}" y="{yB - 8}" '
             f'font-size="10" font-style="italic" fill="#6a6a6a" '
             f'text-anchor="middle">realistic volume, 20 to 50 cases</text>')
    # Horizontal gridlines + y labels at 0, .25, .5, .75, 1.
    for r in (0.0, 0.25, 0.5, 0.75, 1.0):
        p.append(f'  <line x1="{x0}" y1="{sy(r):.1f}" x2="{x1}" y2="{sy(r):.1f}"'
                 f' stroke="#d0d0c8" stroke-width="1"/>')
        p.append(f'  <text x="{x0 - 8}" y="{sy(r) + 3:.1f}" font-size="10" '
                 f'fill="#6a6a6a" text-anchor="end">{r:.2f}</text>')
    # The 0.90 reference line, the level a high-stakes decision would want.
    p.append(f'  <line class="crv-fade" style="animation-delay:1.2s" x1="{x0}" '
             f'y1="{sy(0.90):.1f}" x2="{x1}" y2="{sy(0.90):.1f}" '
             f'stroke="#7a0000" stroke-width="1.2" stroke-dasharray="5,3"/>')
    p.append(f'  <text class="crv-fade" style="animation-delay:1.3s" '
             f'x="{x1}" y="{sy(0.90) - 6:.1f}" font-size="11" font-style="italic"'
             f' fill="#7a0000" text-anchor="end">reliability 0.90, the level a '
             f'high-stakes decision wants</text>')
    # The curve itself, traced on load.
    L = poly_len(curve)
    p.append(f'  <polyline class="crv-trace" style="--crv-len:{L:.0f}" '
             f'points="{pts_str(curve)}" fill="none" stroke="#111" '
             f'stroke-width="1.8"/>')
    # The point at 30 cases, the heart of the claim.
    p.append(f'  <circle class="crv-fade" style="animation-delay:1.5s" '
             f'cx="{sx(30):.1f}" cy="{sy(r30):.1f}" r="4" fill="#111"/>')
    p.append(f'  <text class="crv-fade" style="animation-delay:1.6s" '
             f'x="{sx(30) + 10:.1f}" y="{sy(r30) + 14:.1f}" font-size="11" '
             f'fill="#111">30 cases: R = {r30:.2f}</text>')
    # X axis ticks.
    p.append(f'  <line x1="{x0}" y1="{yB}" x2="{x1}" y2="{yB}" '
             f'stroke="#d0d0c8" stroke-width="1"/>')
    for n in (1, 5, 10, 30, 50, 100, 300, 500):
        p.append(f'  <text x="{sx(n):.1f}" y="{yB + 18}" font-size="10" '
                 f'fill="#6a6a6a" text-anchor="middle">{n}</text>')
    p.append(f'  <text x="{(x0 + x1) / 2:.0f}" y="{yB + 38}" font-size="11" '
             f'font-style="italic" fill="#6a6a6a" text-anchor="middle">cases '
             f'per physician (log scale)</text>')

    aria = (f"Line chart of measure reliability against caseload on a log scale, "
            f"computed from R of n equals var between over var between plus var "
            f"within over n, with var between 1 and var within 45. Reliability is "
            f"{r20:.2f} at 20 cases, {r30:.2f} at 30 cases, and {r50:.2f} at 50 "
            f"cases, all far below the marked 0.90 line, which the curve does not "
            f"reach until several hundred cases. {SIM_NOTE}")
    body = "\n".join(p)
    return (f'<figure>\n'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{aria}" style="width:100%;height:auto;'
            f"font-family:'et-book',Palatino,Georgia,serif\">\n"
            f'{body}\n</svg>\n'
            f'<figcaption>Reliability of a physician-level performance measure as '
            f'a function of caseload, R(n) = var_between / (var_between + '
            f'var_within / n) with var_between = 1 and var_within = 45, chosen so '
            f'the curve sits in the range the literature reports at realistic '
            f'volumes. {SIM_NOTE}</figcaption>\n'
            f'</figure>')


# ============================== CHART 2: FUNNEL ============================
def svg_funnel(rng_state):
    n, y1, _ = rng_state
    obs = y1
    W, H = 760, 420
    x0, x1 = 95, 690
    yT, yB = 60, 340
    lo_n, hi_n = min(n), max(n)
    logspan = math.log10(hi_n) - math.log10(lo_n)

    def sx(v):
        return x0 + (math.log10(v) - math.log10(lo_n)) / logspan * (x1 - x0)

    # Control limits over a smooth grid: p0 +/- z*sqrt(p0(1-p0)/n). Computed,
    # never sketched. The y-scale is set from the data and the outer limits.
    grid = [lo_n * (hi_n / lo_n) ** (i / 120) for i in range(121)]

    def se(v):
        return math.sqrt(P0 * (1 - P0) / v)

    ymax = max(max(obs), P0 + Z998 * se(lo_n)) * 1.10

    def sy(r):
        return yB - max(0.0, r) / ymax * (yB - yT)

    def limit_pts(z, sign):
        return [(sx(v), sy(P0 + sign * z * se(v))) for v in grid]

    u95, l95 = limit_pts(Z95, +1), limit_pts(Z95, -1)
    u998, l998 = limit_pts(Z998, +1), limit_pts(Z998, -1)

    # Providers a naive ranking would tag as bad outliers: above their OWN 95%
    # upper limit despite sharing p0. This count is quoted in the prose.
    flagged = [obs[i] > P0 + Z95 * se(n[i]) for i in range(len(n))]
    n_out = sum(flagged)

    p = []
    p.append('  <text x="20" y="24" font-size="11" letter-spacing="1.4" '
             'fill="#6a6a6a">WITH NO REAL DIFFERENCES, RANKING STILL '
             'MANUFACTURES OUTLIERS</text>')
    p.append('  <text x="20" y="44" font-size="11" font-style="italic" '
             'fill="#6a6a6a">300 simulated providers, one shared true rate '
             'p0 = 3%, lognormal caseloads (median 30)</text>')
    # Limit curves, traced (outer dotted, inner solid).
    for k, (curve, dash, delay) in enumerate((
            (u998, '2,3', 0.0), (l998, '2,3', 0.1),
            (u95, None, 0.2), (l95, None, 0.3))):
        Lc = poly_len(curve)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        # crv-trace overrides dasharray for the draw; for dotted limits we keep
        # them static (fade) so the dotted pattern survives.
        cls = 'crv-fade' if dash else 'crv-trace'
        style = (f'animation-delay:{delay}s' if dash
                 else f'--crv-len:{Lc:.0f};animation-delay:{delay}s')
        p.append(f'  <polyline class="{cls}" style="{style}" '
                 f'points="{pts_str(curve)}" fill="none" stroke="#6a6a6a" '
                 f'stroke-width="1"{da}/>')
    # The true-rate line.
    p.append(f'  <line x1="{x0}" y1="{sy(P0):.1f}" x2="{x1}" y2="{sy(P0):.1f}" '
             f'stroke="#111" stroke-width="1"/>')
    p.append(f'  <text x="{x1 + 4}" y="{sy(P0) + 4:.1f}" font-size="10" '
             f'fill="#111">p0 = 3%</text>')
    p.append(f'  <text x="{x1 + 4}" y="{sy(P0 + Z95 * se(hi_n)) + 3:.1f}" '
             f'font-size="9" fill="#6a6a6a">95%</text>')
    p.append(f'  <text x="{x1 + 4}" y="{sy(P0 + Z998 * se(hi_n)) + 3:.1f}" '
             f'font-size="9" fill="#6a6a6a">99.8%</text>')
    # Provider points, faded in as a group. Inside = ink (muted), flagged = accent.
    pts = ['  <g class="crv-fade" style="animation-delay:0.9s">']
    for i in range(len(n)):
        if flagged[i]:
            pts.append(f'    <circle cx="{sx(n[i]):.1f}" cy="{sy(obs[i]):.1f}" '
                       f'r="3.2" fill="#7a0000"/>')
        else:
            pts.append(f'    <circle cx="{sx(n[i]):.1f}" cy="{sy(obs[i]):.1f}" '
                       f'r="2.4" fill="#111" opacity="0.5"/>')
    pts.append('  </g>')
    p.extend(pts)
    # League-table annotation.
    p.append(f'  <text class="crv-fade" style="animation-delay:1.4s" x="320" '
             f'y="84" font-size="11" font-style="italic" fill="#7a0000">'
             f'{n_out} providers cross the 95% line, yet all share one true</text>')
    p.append('  <text class="crv-fade" style="animation-delay:1.4s" x="320" '
             'y="100" font-size="11" font-style="italic" fill="#7a0000">'
             'rate: the spread is noise (the league-table fallacy)</text>')
    # X axis.
    p.append(f'  <line x1="{x0}" y1="{yB}" x2="{x1}" y2="{yB}" '
             f'stroke="#d0d0c8" stroke-width="1"/>')
    for v in (5, 10, 20, 30, 50, 100, 200):
        if lo_n <= v <= hi_n:
            p.append(f'  <text x="{sx(v):.1f}" y="{yB + 18}" font-size="10" '
                     f'fill="#6a6a6a" text-anchor="middle">{v}</text>')
    p.append(f'  <text x="{(x0 + x1) / 2:.0f}" y="{yB + 38}" font-size="11" '
             f'font-style="italic" fill="#6a6a6a" text-anchor="middle">cases '
             f'per provider (log scale)</text>')
    p.append(f'  <text x="20" y="{(yT + yB) / 2:.0f}" font-size="11" '
             f'font-style="italic" fill="#6a6a6a" transform="rotate(-90 20 '
             f'{(yT + yB) / 2:.0f})" text-anchor="middle">observed event '
             f'rate</text>')

    aria = (f"Funnel plot of {N_PROVIDERS} simulated providers who share one true "
            f"event rate of 3 percent, with skewed caseloads. Observed rates are "
            f"single binomial draws. Control limits are p0 plus or minus z times "
            f"the square root of p0 times one minus p0 over n, at the 95 and 99.8 "
            f"percent levels. Nearly all providers fall inside the funnel; {n_out} "
            f"cross the 95 percent line by chance alone. {SIM_NOTE}")
    body = "\n".join(p)
    return (f'<figure>\n'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{aria}" style="width:100%;height:auto;'
            f"font-family:'et-book',Palatino,Georgia,serif\">\n"
            f'{body}\n</svg>\n'
            f'<figcaption>A funnel plot of {N_PROVIDERS} simulated providers who '
            f'share one true event rate (p0 = 3%); observed rates are single '
            f'Binomial(n, p0) draws over lognormal caseloads. The control limits '
            f'are p0 +/- z*sqrt(p0(1-p0)/n) at the 95% and 99.8% levels, computed '
            f'on a grid. The accented points are flagged by a 95% cutoff even '
            f'though no provider differs from any other. {SIM_NOTE}</figcaption>\n'
            f'</figure>'), n_out


# ============================ CHART 3: QUARTILES ==========================
def svg_quartile(rng_state, rng):
    n, y1, y2 = rng_state
    q1 = quartiles(y1, rng)
    q2 = quartiles(y2, rng)
    changed = [q1[i] != q2[i] for i in range(len(n))]
    pct = sum(changed) / len(n) * 100

    W, H = 620, 420
    xL, xR = 200, 420
    yT, yB = 95, 330

    def qy(q, jit):
        # Q4 at top, Q1 at bottom; jitter spreads the band of crossing lines.
        return yT + (4 - q) / 3 * (yB - yT) + jit

    p = []
    p.append('  <text x="20" y="24" font-size="11" letter-spacing="1.4" '
             'fill="#6a6a6a">RANKINGS RESHUFFLE WHEN NOTHING REAL HAS '
             'CHANGED</text>')
    p.append('  <text x="20" y="44" font-size="11" font-style="italic" '
             'fill="#6a6a6a">two independent years, one shared true rate; '
             'every quartile move is noise</text>')
    p.append(f'  <text x="{xL}" y="74" font-size="12" fill="#111" '
             f'text-anchor="middle">Year 1</text>')
    p.append(f'  <text x="{xR}" y="74" font-size="12" fill="#111" '
             f'text-anchor="middle">Year 2</text>')
    # The crossing lines, faded in as one group.
    p.append('  <g class="crv-fade" style="animation-delay:0.4s">')
    for i in range(len(n)):
        j1 = (i % 7 - 3) * 4.0    # deterministic jitter from index (seed-free)
        j2 = ((i * 3) % 7 - 3) * 4.0
        col = '#7a0000' if changed[i] else '#6a6a6a'
        op = '0.35' if changed[i] else '0.13'
        p.append(f'    <line x1="{xL}" y1="{qy(q1[i], j1):.1f}" x2="{xR}" '
                 f'y2="{qy(q2[i], j2):.1f}" stroke="{col}" stroke-width="0.8" '
                 f'opacity="{op}"/>')
    p.append('  </g>')
    # Quartile labels both sides.
    for q in (1, 2, 3, 4):
        yy = qy(q, 0)
        p.append(f'  <text x="{xL - 30}" y="{yy + 4:.1f}" font-size="11" '
                 f'fill="#111" text-anchor="end">Q{q}</text>')
        p.append(f'  <text x="{xR + 30}" y="{yy + 4:.1f}" font-size="11" '
                 f'fill="#111" text-anchor="start">Q{q}</text>')
    p.append(f'  <text class="crv-fade" style="animation-delay:1.1s" '
             f'x="{(xL + xR) / 2:.0f}" y="{yB + 40}" font-size="12" '
             f'font-style="italic" fill="#7a0000" text-anchor="middle">'
             f'{pct:.0f}% of providers change quartile between two identical '
             f'years</text>')

    aria = (f"Slopegraph connecting each of {N_PROVIDERS} simulated providers' "
            f"quartile in year one to its quartile in year two, both years drawn "
            f"from one shared true rate. {pct:.0f} percent of providers land in a "
            f"different quartile the second year; with no true differences, all of "
            f"the movement is noise. {SIM_NOTE}")
    body = "\n".join(p)
    return (f'<figure>\n'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{aria}" style="width:100%;height:auto;'
            f"font-family:'et-book',Palatino,Georgia,serif\">\n"
            f'{body}\n</svg>\n'
            f'<figcaption>Quartile assignments for the same {N_PROVIDERS} '
            f'simulated providers across two independent years drawn from one '
            f'true rate. Ties among low-volume providers are broken at random, '
            f'the correct treatment when there is no real order to recover. The '
            f'share changing quartile is computed directly. {SIM_NOTE}'
            f'</figcaption>\n</figure>'), pct


# ============================== CHART 4: OPPE =============================
def svg_oppe():
    W, H = 760, 250
    cols = [
        (f"{OPPE_OUTLIERS} of {OPPE_PROVIDERS:,}",
         "flagged as outliers by", "OPPE metrics alone", "#7a0000"),
        (f"~${OPPE_COST_PER_PROVIDER}", "recurring labor cost",
         "per provider", "#111"),
        (f"~${OPPE_NATIONAL_COST_M}M", "estimated cost per",
         "year, nationally", "#111"),
    ]
    p = []
    p.append('  <text x="380" y="40" font-size="14" fill="#111" '
             'text-anchor="middle">Cost per outlier detected has no finite '
             'value: the denominator is zero</text>')
    p.append('  <g class="crv-fade" style="animation-delay:0.3s">')
    for i, (big, s1, s2, col) in enumerate(cols):
        x = (i + 0.5) / 3 * W
        p.append(f'    <text x="{x:.0f}" y="130" font-size="40" fill="{col}" '
                 f'text-anchor="middle">{big}</text>')
        p.append(f'    <text x="{x:.0f}" y="172" font-size="12" fill="#6a6a6a" '
                 f'text-anchor="middle">{s1}</text>')
        p.append(f'    <text x="{x:.0f}" y="190" font-size="12" fill="#6a6a6a" '
                 f'text-anchor="middle">{s2}</text>')
    p.append('  </g>')
    p.append('  <line x1="60" y1="218" x2="700" y2="218" stroke="#d0d0c8" '
             'stroke-width="1"/>')
    p.append('  <text x="380" y="238" font-size="11" font-style="italic" '
             'fill="#6a6a6a" text-anchor="middle">Sourced figures (Joint '
             'Commission OPPE cost study), not simulation.</text>')

    aria = ("Panel of three published figures from a six-system OPPE cost study: "
            "zero of 12,854 providers flagged as outliers by OPPE metrics alone, "
            "about 50 dollars recurring labor cost per provider, and about 78 "
            "million dollars estimated cost per year nationally. Cost per outlier "
            "detected is undefined because no outliers were found.")
    body = "\n".join(p)
    return (f'<figure>\n'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{aria}" style="width:100%;height:auto;'
            f"font-family:'et-book',Palatino,Georgia,serif\">\n"
            f'{body}\n</svg>\n'
            f'<figcaption>Reported yield of OPPE-metric monitoring at the scale '
            f'studied: 0 of 12,854 providers flagged, about $50 per provider, '
            f'about $78M per year nationally. These are sourced figures, not '
            f'simulation. Cost per outlier detected is undefined because no '
            f'outliers were detected by the metrics alone.</figcaption>\n'
            f'</figure>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", choices=["reliability", "funnel", "quartile",
                                       "oppe"])
    args = ap.parse_args()

    rng = random.Random(SEED)
    state = simulate(rng)  # (volumes, year1 rates, year2 rates)

    if args.emit == "reliability":
        print(svg_reliability())
    elif args.emit == "funnel":
        print(svg_funnel(state)[0])
    elif args.emit == "quartile":
        print(svg_quartile(state, rng)[0])
    elif args.emit == "oppe":
        print(svg_oppe())
    else:
        # Summary: print the seed and every number the prose depends on.
        _, n_out = svg_funnel(state)
        _, pct = svg_quartile(state, rng)
        print(f"seed = {SEED}")
        print(f"reliability: R(20)={reliability(20):.3f} "
              f"R(30)={reliability(30):.3f} R(50)={reliability(50):.3f}")
        print(f"funnel: providers beyond 95% upper limit = {n_out} / "
              f"{N_PROVIDERS}")
        print(f"quartiles: share changing quartile = {pct:.1f}%")


if __name__ == "__main__":
    main()
