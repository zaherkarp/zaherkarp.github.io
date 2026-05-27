"""
scripts/build_cliff.py

Render the Medicare Advantage Star Rating density curve in
index.html from the canonical CMS distribution at
src/data/cms-ma-pd-stars-2025.csv. Replaces the hand-drawn bezier
that previously stood in for the data.

Idempotent. Run after updating the CSV (typically once a year when
CMS releases the new ratings in October). Output goes between the
<!-- cliff-path:start --> and <!-- cliff-path:end --> markers in
index.html.

No external dependencies; uses a pure-Python Gaussian KDE so the
script can run with stdlib only.

Geometry is locked to the cliff figure's viewBox (600 x 240). If
that viewBox or the axis layout in index.html changes, update the
constants below to match.
"""

from __future__ import annotations
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "src" / "data" / "cms-ma-pd-stars-2025.csv"
HTML_PATH = ROOT / "index.html"

START_MARKER = "<!-- cliff-path:start -->"
END_MARKER = "<!-- cliff-path:end -->"

# SVG geometry (must match the cliff-figure SVG in index.html).
# x-axis covers the rating range [RATING_LEFT, RATING_RIGHT] mapped
# to SVG pixels [X_LEFT, X_RIGHT]. Curve hangs from Y_BASE down to
# Y_TOP at peak density.
X_LEFT, X_RIGHT = 60.0, 540.0
RATING_LEFT, RATING_RIGHT = 2.5, 5.0
Y_BASE = 200.0
Y_TOP = 50.0
N_SAMPLES = 240
BANDWIDTH = 0.18  # Gaussian KDE bandwidth, in rating units


def load_distribution(path: Path) -> list[float]:
    """Return a flat sample list (one entry per contract) from the CSV.

    Lines starting with '#' are comments; the first non-comment row
    is the header.
    """
    samples: list[float] = []
    with path.open() as f:
        header_seen = False
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if not header_seen:
                header_seen = True
                continue
            rating_str, count_str = line.split(",")
            samples.extend([float(rating_str)] * int(count_str))
    return samples


def kde(samples: list[float], x: float, h: float) -> float:
    """Gaussian kernel density estimate evaluated at x."""
    n = len(samples)
    if n == 0:
        return 0.0
    s = sum(math.exp(-0.5 * ((x - sample) / h) ** 2) for sample in samples)
    return s / (n * h * math.sqrt(2.0 * math.pi))


def build_paths(samples: list[float]) -> tuple[str, str]:
    """Return two SVG `d` attributes: a closed fill path and an open line path.

    Two paths because the density at rating 2.5 (the leftmost visible
    rating) is non-zero — 35 contracts sit there in the CMS 2025
    data — so closing a single stroked path back to baseline would
    draw a visible vertical "wall" at the chart's left edge. The
    fill path closes invisibly (faint fill, no stroke); the line
    path traces only the curve top with a visible stroke.
    """
    points: list[tuple[float, float]] = []
    for i in range(N_SAMPLES + 1):
        t = i / N_SAMPLES
        rating = RATING_LEFT + (RATING_RIGHT - RATING_LEFT) * t
        d = kde(samples, rating, BANDWIDTH)
        points.append((rating, d))

    max_d = max(d for _, d in points)
    if max_d <= 0:
        sys.exit("KDE produced zero density everywhere; check the CSV.")

    rating_span = RATING_RIGHT - RATING_LEFT
    x_span = X_RIGHT - X_LEFT
    y_span = Y_BASE - Y_TOP

    svg_points: list[tuple[float, float]] = []
    for rating, d in points:
        x = X_LEFT + ((rating - RATING_LEFT) / rating_span) * x_span
        y = Y_BASE - (d / max_d) * y_span
        svg_points.append((x, y))

    # Fill path: closed shape from left baseline up to curve, across,
    # back down to right baseline, close. Stroked invisibly.
    fill_parts: list[str] = [f"M {svg_points[0][0]:.2f} {Y_BASE:.2f}"]
    fill_parts.append(f"L {svg_points[0][0]:.2f} {svg_points[0][1]:.2f}")
    for x, y in svg_points[1:]:
        fill_parts.append(f"L {x:.2f} {y:.2f}")
    fill_parts.append(f"L {svg_points[-1][0]:.2f} {Y_BASE:.2f} Z")
    fill_d = " ".join(fill_parts)

    # Line path: open trace of just the curve top.
    line_parts: list[str] = [f"M {svg_points[0][0]:.2f} {svg_points[0][1]:.2f}"]
    for x, y in svg_points[1:]:
        line_parts.append(f"L {x:.2f} {y:.2f}")
    line_d = " ".join(line_parts)

    return fill_d, line_d


def update_html(fill_d: str, line_d: str) -> None:
    html = HTML_PATH.read_text()
    start = html.find(START_MARKER)
    end = html.find(END_MARKER)
    if start == -1 or end == -1:
        sys.exit(
            f"Could not find both markers in {HTML_PATH}. "
            f"Expected {START_MARKER!r} and {END_MARKER!r}."
        )
    if end < start:
        sys.exit(f"End marker precedes start marker in {HTML_PATH}.")

    indent = "            "
    new_block = (
        f"{START_MARKER}\n"
        f'{indent}<path d="{fill_d}" fill="#111" fill-opacity="0.06" stroke="none"/>\n'
        f'{indent}<path d="{line_d}" fill="none" stroke="#111" stroke-width="1.5"/>\n'
        f"{indent}{END_MARKER}"
    )
    pre = html[:start]
    post = html[end + len(END_MARKER) :]
    HTML_PATH.write_text(pre + new_block + post)


def main() -> None:
    samples = load_distribution(DATA_PATH)
    total = len(samples)
    print(f"Loaded {total} contracts from {DATA_PATH.relative_to(ROOT)}")
    fill_d, line_d = build_paths(samples)
    update_html(fill_d, line_d)
    print(
        f"Updated cliff path in {HTML_PATH.relative_to(ROOT)} "
        f"({N_SAMPLES} samples, bandwidth {BANDWIDTH}, two paths: fill + line)"
    )


if __name__ == "__main__":
    main()
