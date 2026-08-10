#!/usr/bin/env python3
"""
build_og.py

Renders /og-default.png from a small composition rule. Run once locally
when the card content changes; commit the resulting PNG. Not wired to
CI, the card is essentially static.

Colors are READ from src/content/palette.yaml, not inlined. They used to be
inlined "because this is a one-off renderer", and they duly went stale: the
card was still painting Tufte cream months after the site moved to the Lichen
palette, and nothing caught it because lint_palette only inspects the CSS-ish
files carrying palette:* marker spans. Reading the source makes that class of
drift impossible here rather than merely detectable.

Local dev:
    pip install Pillow PyYAML
    python scripts/build_og.py
"""

from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "og-default.png"
FONT_DIR = Path(__file__).resolve().parent / "fonts" / "et-book"
ROMAN = FONT_DIR / "et-book-roman-line-figures.ttf"
PALETTE = ROOT / "src" / "content" / "palette.yaml"


def _rgb(hex_string: str) -> tuple:
    """'#f3f6f0' -> (243, 246, 240)."""
    h = hex_string.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _light_tokens() -> dict:
    """The screen light-mode roles, straight from the palette source."""
    light = yaml.safe_load(PALETTE.read_text(encoding="utf-8"))["screen"]["light"]
    return {role: _rgb(light[role]) for role in ("bg", "ink", "muted")}


_T = _light_tokens()
PAPER, INK, MUTED = _T["bg"], _T["ink"], _T["muted"]

# Open Graph canonical size.
W, H = 1200, 630

NAME = "Zaher Karp"
# Matches the homepage proposition. The former category-label subtitle
# ("Healthcare data engineering and Medicare Advantage analytics.") was
# retired from the page on 2026-07-29; the card follows it. Since
# 2026-08-10 the proposition is two sentences (the player-coach clause),
# drawn one per line because the pair overflows 1200px as a single run.
SUBTITLE_LINES = (
    "I work in healthcare data engineering and analytics.",
    "I lead a small data science team and still build.",
)
DOMAIN = "zaherkarp.com"


def render() -> None:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    name_font = ImageFont.truetype(str(ROMAN), 168)
    sub_font = ImageFont.truetype(str(ROMAN), 38)
    foot_font = ImageFont.truetype(str(ROMAN), 30)

    left = 110
    name_y = 200

    draw.text((left, name_y), NAME, font=name_font, fill=INK)

    # The Pillow textbbox returns (x0, y0, x1, y1) for the rendered run;
    # we use it to anchor the subtitle directly under the cap baseline.
    name_box = draw.textbbox((left, name_y), NAME, font=name_font)
    sub_y = name_box[3] + 40

    for line in SUBTITLE_LINES:
        draw.text((left, sub_y), line, font=sub_font, fill=MUTED)
        line_box = draw.textbbox((left, sub_y), line, font=sub_font)
        sub_y = line_box[3] + 14
    draw.text((left, H - 80), DOMAIN, font=foot_font, fill=MUTED)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    render()
