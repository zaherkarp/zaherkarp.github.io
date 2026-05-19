#!/usr/bin/env python3
"""
build_og.py

Renders /og-default.png from a small composition rule. Run once locally
when the card content changes; commit the resulting PNG. Not wired to
CI, the card is essentially static.

Design tokens are inlined because this is a one-off renderer, not the
canonical declaration. Locked tokens live in CLAUDE.md §Palette.

Local dev:
    pip install Pillow
    python scripts/build_og.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "og-default.png"
FONT_DIR = Path(__file__).resolve().parent / "fonts" / "et-book"
ROMAN = FONT_DIR / "et-book-roman-line-figures.ttf"

# Locked palette (CLAUDE.md §Palette). Light-mode tokens.
PAPER = (255, 255, 248)
INK = (17, 17, 17)
MUTED = (106, 106, 106)

# Open Graph canonical size.
W, H = 1200, 630

NAME = "Zaher Karp"
SUBTITLE = "Healthcare data engineering and Medicare Advantage analytics."
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

    draw.text((left, sub_y), SUBTITLE, font=sub_font, fill=MUTED)
    draw.text((left, H - 80), DOMAIN, font=foot_font, fill=MUTED)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    render()
