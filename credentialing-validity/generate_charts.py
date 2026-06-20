#!/usr/bin/env python3
"""Generate the figures and the self-contained HTML post for the essay
"The credential looks rigorous; the score does not separate safe from dangerous."

WHY THIS SCRIPT EXISTS
----------------------
The argument of the post is statistical, and the charts are the argument made
visible rather than decoration. So every number a reader sees on a chart is
computed here from a stated formula on seeded, clearly-labelled SIMULATED data.
Nothing is hand-placed: control limits, reliability curves, and the
quartile-reshuffle share are all derived, not drawn by eye.

REPRODUCIBILITY CONTRACT
------------------------
- A single NumPy Generator is seeded with the integer SEED below, and the seed
  is printed on every run. Re-running reproduces byte-identical SVGs because
  (a) the RNG is fully determined by the seed, and (b) we strip the only two
  sources of run-to-run SVG drift matplotlib introduces: the embedded save
  timestamp (metadata Date=None) and salted element ids (a fixed svg.hashsalt).
- The post text that depends on the simulation (the reliability values, the
  funnel outlier count, the quartile-change share) is interpolated from the
  SAME computed variables used to draw the charts, so prose and figures cannot
  silently disagree.

WHAT IS SOURCED VS SIMULATED
----------------------------
Sourced, real, attributed in the prose and NOT altered here:
  - OPPE is required by The Joint Commission.
  - 12,854 providers, 0 OPPE-only outliers, ~$50/provider, ~$78M/year.
  - Reliability 0.90 needed 138-255 cases/physician in one worked case; a
    modest risk-adjustment change reclassified 8 of 56 doctors across quartiles.
  - The Joint Commission low-volume carve-out.
Everything drawn from the RNG is illustrative simulation, labelled as such on
every figure and in every caption. The simulated charts demonstrate the
mechanism (rare numerator over small denominator = noise); they are not real
provider data and make no claim to be.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless: write files, never open a window
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Determinism knobs. These must be set BEFORE any figure is created.
# svg.hashsalt fixes the salt matplotlib uses to generate clip-path/gradient
# ids, so the same drawing yields the same ids every run. svg.fonttype="none"
# emits real <text> elements (small files, selectable text) instead of tracing
# every glyph as a hashed path, which also removes a large source of id churn.
# ---------------------------------------------------------------------------
matplotlib.rcParams["svg.hashsalt"] = "credentialing-validity"
matplotlib.rcParams["svg.fonttype"] = "none"

# Visual tokens borrowed from the site palette so the figures sit comfortably
# on a cream page. INK is body text, MUTED is secondary, RULE is hairlines,
# ACCENT (petrol teal) is used at most once or twice per chart, never as
# decoration. These are presentation choices and carry no statistical meaning.
INK = "#111111"
MUTED = "#6a6a6a"
RULE = "#cfcfc7"
ACCENT = "#0a5c54"
PAPER = "#fffff8"

plt.rcParams.update({
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "font.family": "serif",
    # A serif stack that degrades gracefully wherever the SVG is opened. The
    # site's ETBook is not available to matplotlib, so we name common serifs.
    "font.serif": ["Palatino", "Palatino Linotype", "Book Antiqua", "Georgia",
                   "DejaVu Serif", "serif"],
    "font.size": 12,
    "text.color": INK,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.linewidth": 0.8,
})

SEED = 20260620  # printed below; any reader can re-run with this and reproduce.
OUTDIR = "charts"

# A common note stamped on every simulated figure so a chart can never be
# screenshotted out of context and mistaken for real provider data.
SIM_NOTE = "Illustrative simulation, not real provider data."


def _save(fig, name):
    """Write a figure as a reproducible SVG.

    metadata={'Date': None} suppresses the save-time timestamp matplotlib would
    otherwise embed, which is the last remaining source of byte drift once the
    RNG and hashsalt are pinned. bbox_inches='tight' trims whitespace so the
    inline SVG sits flush in the post.
    """
    path = f"{OUTDIR}/{name}.svg"
    fig.savefig(path, format="svg", bbox_inches="tight",
                metadata={"Date": None})
    plt.close(fig)
    return path


# ===========================================================================
# CHART 1 -- Reliability versus cases per physician
# ===========================================================================
# A physician-level performance measure can be split into true between-physician
# variation and measurement error. The reliability of the measure is the share
# of observed variation that is real signal:
#
#       R(n) = var_between / (var_between + var_within / n)
#
# The within-physician error variance shrinks as 1/n, so reliability rises with
# caseload. The whole point of the chart is that at the caseloads physicians
# actually generate, R sits far below the 0.90 a high-stakes decision would
# want. We pick illustrative variance components so that R near 30 cases lands
# in the 0.3-0.5 range the literature reports, and we STATE the chosen values on
# the chart and in the caption rather than hiding them.
VAR_BETWEEN = 1.0
VAR_WITHIN = 45.0  # ratio 45:1 puts R(30)=0.40, inside the target 0.3-0.5 band.


def reliability(n):
    """R(n) = var_between / (var_between + var_within / n). Vectorised over n."""
    return VAR_BETWEEN / (VAR_BETWEEN + VAR_WITHIN / n)


# Report the values the prose quotes, computed from the same function the curve
# uses, so the text cannot drift from the figure.
R20, R30, R50 = (float(reliability(np.array(k))) for k in (20, 30, 50))


def chart_reliability():
    # Dense log-spaced grid so the curve is smooth on a log x-axis. The curve is
    # computed at every grid point; no segment is drawn by hand.
    n = np.logspace(0, np.log10(500), 400)  # 1 to 500 cases
    R = reliability(n)

    fig, ax = plt.subplots(figsize=(7.0, 4.3))
    ax.plot(n, R, color=INK, lw=1.8)

    # The 0.90 reference line: the reliability a high-stakes ranking would want.
    # Drawn in accent because it is the single most important threshold here.
    ax.axhline(0.90, color=ACCENT, lw=1.2, ls=(0, (5, 3)))
    ax.text(1.05, 0.905, "Reliability 0.90, the level a high-stakes "
            "decision would want", color=ACCENT, fontsize=9.5,
            style="italic", va="bottom")

    # Shade the realistic-volume band (20 to 50 cases). The annotation reads the
    # actual computed endpoints so it always matches the curve.
    ax.axvspan(20, 50, color=MUTED, alpha=0.10)
    ax.text(31, 0.05, "Realistic volume\n20 to 50 cases",
            color=MUTED, fontsize=9.5, style="italic", ha="center")
    # Mark the reliability at 30 cases, the heart of the claim.
    ax.plot([30], [R30], "o", color=INK, ms=5)
    ax.annotate(f"30 cases: R = {R30:.2f}", xy=(30, R30),
                xytext=(70, R30 - 0.13), color=INK, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    ax.set_xscale("log")
    ax.set_xlim(1, 500)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Cases per physician (log scale)")
    ax.set_ylabel("Reliability of the performance measure")
    ax.set_title("A performance score is mostly noise at realistic caseloads",
                 fontsize=12.5, color=INK, pad=10)
    # State the assumptions on the chart itself.
    ax.text(1.0, -0.20,
            f"R(n) = var_between / (var_between + var_within / n), "
            f"with var_between = {VAR_BETWEEN:g}, var_within = {VAR_WITHIN:g}. "
            f"{SIM_NOTE}",
            transform=ax.transAxes, fontsize=8.5, color=MUTED, style="italic")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return _save(fig, "reliability")


# ===========================================================================
# CHART 2 -- Funnel plot with NO true differences
# ===========================================================================
# We build a world in which every provider is genuinely identical: one shared
# true event rate p0. Volumes are skewed (most see few cases, a few see many),
# drawn lognormal with median ~30. Each provider's observed rate is a single
# Binomial(n, p0) draw divided by n, so all spread is sampling noise.
#
# The control limits are the binomial standard error scaled by z:
#       limit(n) = p0 +/- z * sqrt(p0 * (1 - p0) / n)
# computed on a smooth grid, for z at the 95% and 99.8% two-sided levels.
N_PROVIDERS = 300
P0 = 0.03                       # shared true event rate, 3 percent (realistic, low)
LOGNORM_MEDIAN = 30.0           # median caseload
LOGNORM_SIGMA = 0.6             # spread on the log scale -> long right tail
Z95 = 1.959964                  # 95% two-sided
Z998 = 3.090232                 # 99.8% two-sided (common funnel-plot outer limit)


def simulate_volumes(rng):
    """Skewed caseloads: lognormal with the stated median, floored at 5.

    median of a lognormal is exp(mu), so mu = ln(median). The floor keeps a
    handful of tiny-volume providers from collapsing to n=0 (undefined rate)
    while preserving the long tail that makes the funnel fan out at the left.
    """
    n = rng.lognormal(mean=np.log(LOGNORM_MEDIAN), sigma=LOGNORM_SIGMA,
                      size=N_PROVIDERS)
    return np.maximum(5, np.round(n)).astype(int)


def chart_funnel(rng):
    n = simulate_volumes(rng)
    # Each provider: one binomial draw at the SHARED true rate, then observed
    # rate = events / n. Identical truth, different luck.
    events = rng.binomial(n, P0)
    obs = events / n

    # Smooth control-limit curves over the observed volume range, computed from
    # the binomial standard error. These are the funnel walls; they are derived,
    # never sketched.
    grid = np.linspace(n.min(), n.max(), 400)
    se = np.sqrt(P0 * (1 - P0) / grid)
    upper95, lower95 = P0 + Z95 * se, P0 - Z95 * se
    upper998, lower998 = P0 + Z998 * se, P0 - Z998 * se

    # How many providers a naive ranking would tag as "bad outliers": those
    # above their OWN 95% upper limit, despite all sharing p0. This count is
    # quoted in the prose.
    own_se = np.sqrt(P0 * (1 - P0) / n)
    n_outlier95 = int(np.sum(obs > P0 + Z95 * own_se))

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    # Funnel walls.
    ax.plot(grid, upper998, color=MUTED, lw=1.0, ls=(0, (1, 2)))
    ax.plot(grid, lower998, color=MUTED, lw=1.0, ls=(0, (1, 2)))
    ax.plot(grid, upper95, color=MUTED, lw=1.1)
    ax.plot(grid, lower95, color=MUTED, lw=1.1)
    ax.axhline(P0, color=INK, lw=1.0)
    # Providers.
    inside = obs <= P0 + Z95 * own_se
    ax.scatter(n[inside], obs[inside], s=16, color=INK, alpha=0.55,
               edgecolors="none")
    # The handful a league table would flag, drawn in accent to make the point.
    ax.scatter(n[~inside], obs[~inside], s=26, color=ACCENT, alpha=0.95,
               edgecolors="none", zorder=5)

    ax.text(grid.max(), P0, "  true rate p0 = 3%", color=INK, fontsize=9.5,
            va="center")
    ax.text(grid.max(), upper95[-1], "  95%", color=MUTED, fontsize=8.5,
            va="center")
    ax.text(grid.max(), upper998[-1], "  99.8%", color=MUTED, fontsize=8.5,
            va="center")
    ax.annotate(
        f"{n_outlier95} providers cross the 95% line,\n"
        "yet every provider shares one true rate:\n"
        "the spread is noise (league-table fallacy)",
        xy=(n[~inside][np.argmax(obs[~inside])], obs[~inside].max()),
        xytext=(0.40, 0.83), textcoords="axes fraction",
        color=ACCENT, fontsize=9.5, style="italic",
        arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))

    ax.set_xscale("log")
    ax.set_xlim(n.min() * 0.9, n.max() * 1.25)
    ax.set_ylim(0, max(obs.max(), upper998.max()) * 1.10)
    ax.set_xlabel("Cases per provider (log scale)")
    ax.set_ylabel("Observed event rate")
    ax.set_title("With no real differences, ranking still manufactures outliers",
                 fontsize=12.5, color=INK, pad=10)
    ax.text(0.0, -0.20,
            f"{N_PROVIDERS} simulated providers, shared true rate p0 = {P0:.0%}, "
            f"caseloads lognormal (median {LOGNORM_MEDIAN:g}). "
            f"Limits = p0 +/- z*sqrt(p0(1-p0)/n). {SIM_NOTE}",
            transform=ax.transAxes, fontsize=8.5, color=MUTED, style="italic")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    _save(fig, "funnel")
    return n_outlier95, n


def _quartiles(values, rng):
    """Sort values into 4 equal groups (1=lowest rate ... 4=highest).

    Low-volume providers pile up at exactly 0 observed events, so ties are
    heavy. We break ties with fresh uniform draws from the seeded RNG (a
    lexsort with the random key as the secondary sort), which is the honest
    thing to do: with no true signal, tied providers have no real ordering, so
    a random split is exactly right and keeps the four groups equal in size.
    """
    tiebreak = rng.random(values.size)
    order = np.lexsort((tiebreak, values))  # primary: values, secondary: random
    ranks = np.empty(values.size, dtype=int)
    ranks[order] = np.arange(values.size)
    return (ranks * 4) // values.size + 1   # 1..4


# ===========================================================================
# CHART 3 -- Quartile instability (slopegraph)
# ===========================================================================
# Same providers, same single true rate, two INDEPENDENT years. If the ranking
# measured something real it would be stable year to year. It is not: we sort
# each year into quartiles and connect them. Because the data contain no true
# differences, all movement is noise. We report the actual share that changes
# quartile.
def chart_slopegraph(n, rng):
    y1 = rng.binomial(n, P0) / n
    y2 = rng.binomial(n, P0) / n
    q1 = _quartiles(y1, rng)
    q2 = _quartiles(y2, rng)
    pct_change = float(np.mean(q1 != q2) * 100)

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    # Vertical jitter within each quartile level so the band of crossing lines
    # is legible; jitter is cosmetic and seeded, it does not touch the stat.
    jit1 = (rng.random(n.size) - 0.5) * 0.55
    jit2 = (rng.random(n.size) - 0.5) * 0.55
    changed = q1 != q2
    for i in range(n.size):
        ax.plot([0, 1], [q1[i] + jit1[i], q2[i] + jit2[i]],
                color=(ACCENT if changed[i] else MUTED),
                alpha=(0.30 if changed[i] else 0.12), lw=0.7)

    for lvl in (1, 2, 3, 4):
        ax.text(-0.06, lvl, f"Q{lvl}", ha="right", va="center",
                color=INK, fontsize=10.5)
        ax.text(1.06, lvl, f"Q{lvl}", ha="left", va="center",
                color=INK, fontsize=10.5)
    ax.text(0, 4.75, "Year 1", ha="center", color=INK, fontsize=11)
    ax.text(1, 4.75, "Year 2", ha="center", color=INK, fontsize=11)
    ax.text(0.5, 0.05,
            f"{pct_change:.0f}% of providers change quartile between two "
            f"identical years.\nWith no true differences, all of it is noise.",
            ha="center", color=ACCENT, fontsize=10, style="italic")

    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(-0.1, 5.0)
    ax.axis("off")
    ax.set_title("Rankings reshuffle when nothing real has changed",
                 fontsize=12.5, color=INK, pad=6)
    ax.text(0.5, -0.05,
            f"Quartiles from two independent Binomial(n, p0={P0:.0%}) years, "
            f"same {N_PROVIDERS} providers. {SIM_NOTE}",
            transform=ax.transAxes, ha="center", fontsize=8.5,
            color=MUTED, style="italic")
    _save(fig, "quartile_slopegraph")
    return pct_change


# ===========================================================================
# CHART 4 -- OPPE yield panel (sourced figures, sober)
# ===========================================================================
# No RNG here: this panel reports the published numbers verbatim. The framing is
# cost per outlier detected, whose denominator is zero, so there is no finite
# value. We state that rather than invent one.
OPPE_PROVIDERS = 12854
OPPE_OUTLIERS = 0
OPPE_COST_PER_PROVIDER = 50      # dollars, recurring labor, approximate
OPPE_NATIONAL_COST = 78_000_000  # dollars per year, approximate


def chart_oppe_yield():
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    ax.axis("off")
    cols = [
        (f"{OPPE_OUTLIERS} of {OPPE_PROVIDERS:,}",
         "flagged as outliers by\nOPPE metrics alone"),
        (f"~${OPPE_COST_PER_PROVIDER}",
         "recurring labor cost\nper provider"),
        (f"~${OPPE_NATIONAL_COST/1e6:.0f}M",
         "estimated cost\nper year, nationally"),
    ]
    for i, (big, small) in enumerate(cols):
        x = (i + 0.5) / len(cols)
        ax.text(x, 0.62, big, ha="center", va="center", fontsize=25,
                color=(ACCENT if i == 0 else INK))
        ax.text(x, 0.28, small, ha="center", va="top", fontsize=10,
                color=MUTED)
    ax.text(0.5, 0.96, "Cost per outlier detected has no finite value: "
            "the denominator is zero", ha="center", va="top", fontsize=11.5,
            color=INK)
    ax.text(0.5, -0.04,
            "Sourced figures (Joint Commission OPPE study), not simulation. "
            "Approximate values as reported.",
            ha="center", va="top", transform=ax.transAxes, fontsize=8.5,
            color=MUTED, style="italic")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return _save(fig, "oppe_yield")


# ===========================================================================
# Assemble the self-contained HTML post (SVGs inlined, no external assets).
# ===========================================================================
def read_svg_inline(name):
    """Return the <svg>...</svg> body with the XML prolog and DOCTYPE stripped,
    so it can be dropped straight into an HTML5 document."""
    with open(f"{OUTDIR}/{name}.svg", "r", encoding="utf-8") as f:
        s = f.read()
    return s[s.index("<svg"):]


def build_html(stats):
    r30, r20, r50 = stats["R30"], stats["R20"], stats["R50"]
    n_out = stats["n_outlier95"]
    qchg = stats["pct_change"]
    figs = {k: read_svg_inline(k) for k in
            ("reliability", "funnel", "quartile_slopegraph", "oppe_yield")}

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The credential looks rigorous; the score does not separate safe from dangerous</title>
<style>
  :root {{ --paper:{PAPER}; --ink:{INK}; --muted:{MUTED}; --rule:{RULE}; --accent:{ACCENT}; }}
  html {{ font-size: 18px; }}
  body {{
    background: var(--paper); color: var(--ink);
    font-family: Palatino, "Palatino Linotype", "Book Antiqua", Georgia, serif;
    line-height: 1.55; margin: 0; padding: 2.5rem 1.2rem 4rem;
  }}
  main {{ max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 1.85rem; line-height: 1.2; font-weight: normal; margin: 0 0 0.4rem; }}
  .standfirst {{ color: var(--muted); font-style: italic; font-size: 1.05rem; margin: 0 0 2rem; }}
  p {{ margin: 0 0 1.15rem; }}
  figure {{ margin: 2rem 0; text-align: center; }}
  figure svg {{ max-width: 100%; height: auto; }}
  figcaption {{ color: var(--muted); font-style: italic; font-size: 0.82rem;
    margin-top: 0.5rem; text-align: left; }}
  .formula {{ font-family: "Courier New", monospace; font-style: normal; }}
  hr {{ border: none; border-top: 1px solid var(--rule); margin: 2.5rem 0 1.5rem; }}
  .note {{ color: var(--muted); font-size: 0.8rem; }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
<main>
<h1>The credential looks rigorous; the score does not separate safe from dangerous</h1>
<p class="standfirst">Physician credentialing has high face validity. Whether it
has predictive validity is a separate, and statistical, question.</p>

<p>Physician credentialing and privileging are built to reassure. A hospital
verifies a license, confirms a board certification, reviews a work history, and
then keeps watch through performance data. The apparatus has high face validity.
It looks like exactly what a careful institution would do to keep a dangerous
provider away from patients, and that resemblance is most of why we trust it.
This piece is about a different property, predictive validity, which is whether
the same apparatus actually separates a safe provider from a dangerous one. The
two are not the same thing, and the distance between them is statistical, not
moral or procedural.</p>

<p>Consider the ongoing-monitoring half of the system. The Joint Commission
requires Ongoing Professional Practice Evaluation, or OPPE: performance data
collected on each individual privileged provider and factored into the decision
to keep, limit, or revoke privileges. The intent is sound and the data are real.
The difficulty is arithmetic. A dangerous provider is a rare event. Any one
physician accrues only a small number of relevant cases in a year. A rare
numerator measured over a small denominator produces an estimate that is
dominated by noise rather than by the quantity you wanted to measure, and no
amount of administrative care around the edges changes that core.</p>

<p>The standard way to make this precise is the reliability of a physician-level
measure, the share of the observed variation between physicians that reflects
true differences rather than measurement error. Written out, it is
<span class="formula">R(n) = var_between / (var_between + var_within / n)</span>.
Reliability rises with genuine physician-to-physician variation and falls as
measurement noise grows, and because the noise term shrinks as one over the
caseload, sample size is what tips the balance. The chart below traces that
curve. At realistic case volumes the measure barely lifts off the floor. With
the illustrative variance values shown, a physician with thirty cases has a
reliability near {r30:.2f}, and across a twenty-to-fifty-case band it stays
between {r20:.2f} and {r50:.2f}, far below any threshold one would trust for a
decision about someone's privileges. The published literature lands in the same
place from the other direction: in one worked case, reaching a reliability of
0.90 required between 138 and 255 cases per physician, and a modest change in
risk adjustment reclassified 8 of 56 doctors across quartiles.</p>

<figure>
{figs['reliability']}
<figcaption>Reliability of a physician-level performance measure as a function
of caseload, computed from R(n) = var_between / (var_between + var_within / n)
with var_between = {VAR_BETWEEN:g} and var_within = {VAR_WITHIN:g}, chosen so the
curve sits in the range the literature reports at realistic volumes. Illustrative
simulation, not real provider data.</figcaption>
</figure>

<p>It helps to see what a noise-dominated measure does when you rank people with
it. The cleanest way to see it is to build a world with no real differences at
all and watch the ranking invent some. In the funnel plot below, every one of
three hundred simulated providers shares a single true event rate of three
percent. Their caseloads are drawn from a skewed distribution with a median near
thirty, so most carry few cases and a few carry many, and the only thing that
varies between them is luck. The control limits are computed, not sketched: they
are the true rate plus or minus z times the binomial standard error,
<span class="formula">sqrt(p0 (1 - p0) / n)</span>, evaluated across the range of
volumes. Nearly every provider falls inside the funnel, exactly as they should,
because they are in truth identical. Yet a naive worst-to-best ranking still
lifts a handful above the line and labels them outliers. In this run
{n_out} providers cross the ninety-five-percent limit despite sharing the same
true rate. This is the league-table fallacy: the spread is noise, and ranking is
a machine for converting noise into apparent signal.</p>

<figure>
{figs['funnel']}
<figcaption>A funnel plot of 300 simulated providers who share one true event
rate (p0 = 3%); observed rates are single Binomial(n, p0) draws over lognormal
caseloads. The control limits are p0 +/- z*sqrt(p0(1-p0)/n) at the 95% and 99.8%
levels, computed on a grid. The accented points are flagged by a 95% cutoff even
though no provider differs from any other. Illustrative simulation, not real
provider data.</figcaption>
</figure>

<p>If the ranking were measuring something real, it would hold still from one
year to the next. It does not. Drawing two independent years from the identical
true rate and sorting each into quartiles, {qchg:.0f} percent of providers land
in a different quartile the second year. The slopegraph below draws that
movement. Because the data were built with no true differences whatsoever, every
line that changes height is pure noise. The sourced finding that a small change
in risk adjustment reclassified eight of fifty-six doctors across quartiles is
the same phenomenon seen in real data; the simulation shows that even more
reshuffling is the default once volumes are low and you simply let the same
providers play another season. The honest reading is that this churn is larger
than the one-in-seven figure, not smaller, because resampling the same people at
low volume is a harsher test than a single risk-adjustment tweak.</p>

<figure>
{figs['quartile_slopegraph']}
<figcaption>Quartile assignments for the same 300 simulated providers across two
independent years drawn from one true rate. Ties among low-volume providers are
broken at random, which is the correct treatment when there is no real ordering
to recover. The share changing quartile is computed directly. Illustrative
simulation, not real provider data.</figcaption>
</figure>

<p>None of this is hypothetical at the level of yield. In a study spanning
12,854 providers, zero were flagged as outliers through the OPPE metrics alone,
at a recurring labor cost near fifty dollars per provider, on the order of
seventy-eight million dollars per year nationally. The authors describe it as
possibly predominantly administrative waste. The cost per outlier detected has
no finite value, because the denominator is zero. The Joint Commission itself
concedes the underlying problem through its low-volume carve-out, which permits
supplemental outside data when local activity is too sparse to evaluate a
provider. That carve-out is an admission written in policy language that the
denominators are often too small to support the inference anyone wants to draw
from them.</p>

<figure>
{figs['oppe_yield']}
<figcaption>Reported yield of OPPE-metric monitoring at the scale studied. These
are sourced figures, not simulation, shown as the approximate values reported.
Cost per outlier detected is undefined because no outliers were detected by the
metrics alone.</figcaption>
</figure>

<p>Low yield is not zero value, and the distinction matters. A program that finds
nothing through its metrics can still deter, can still catch the rare
unambiguous case that no statistic was needed to see, and the entry-level work
of verifying a license and screening for outright fraud does real good that has
nothing to do with the reliability of a performance score. The claim worth
making is narrow and worth stating plainly. Credentialing and the OPPE score
have high face validity and weak predictive validity. They look like instruments
that separate safe providers from dangerous ones, and at the volumes most
physicians actually generate, they mostly cannot. Treating a noisy score as if
it were a sharp one does more than waste money. It manufactures false confidence
in both directions, flagging the unlucky and clearing no one in particular. The
charts above are simulated on clearly labelled illustrative data, but the
arithmetic they make visible is the same arithmetic that governs the real
programs.</p>

<hr>
<p class="note">Methods. Every simulated figure is generated by
<span class="formula">generate_charts.py</span> from a single seeded NumPy
generator (seed {SEED}), printed on each run. Reliability follows
R(n) = var_between / (var_between + var_within / n); funnel limits follow
p0 +/- z*sqrt(p0(1-p0)/n); quartile churn is computed from two independent
Binomial(n, p0) years. Re-running the script reproduces identical figures. The
OPPE yield panel reports published figures and is not simulated. Simulated
charts are illustrative and are not real provider data.</p>
</main>
</body>
</html>
"""
    with open("post.html", "w", encoding="utf-8") as f:
        f.write(html)
    return "post.html"


def main():
    print(f"[seed] NumPy default_rng seed = {SEED}")
    rng = np.random.default_rng(SEED)

    # Chart order matters: the funnel draws volumes and consumes RNG state first,
    # then the slopegraph reuses those SAME providers' volumes (n) for its two
    # fresh years, so the two charts describe one consistent cohort.
    chart_reliability()
    n_outlier95, n = chart_funnel(rng)
    pct_change = chart_slopegraph(n, rng)
    chart_oppe_yield()

    stats = {"R20": R20, "R30": R30, "R50": R50,
             "n_outlier95": n_outlier95, "pct_change": pct_change}
    build_html(stats)

    # Echo the computed numbers the prose depends on, for verification.
    print(f"[reliability] R(20)={R20:.3f}  R(30)={R30:.3f}  R(50)={R50:.3f}")
    print(f"[funnel] providers beyond 95% upper limit = {n_outlier95} / {N_PROVIDERS}")
    print(f"[quartiles] share changing quartile = {pct_change:.1f}%")
    print("[done] wrote charts/*.svg and post.html")


if __name__ == "__main__":
    main()
