#!/usr/bin/env python3
"""_publications.py

Shared publications data layer for the two build steps that surface the
publication record:

  - build_portfolio.py  -> homepage Publications block (the Tufte margin-note
                           / checkbox-hack markup) + Semantic Scholar count
                           refresh written back to publications.yaml.
  - build_resume.py     -> the CV's Publications section (cv.pdf / cv.html),
                           a flat academic listing using the cached counts.

Keeping the loader and both renderers here (rather than in either build
script) avoids a circular import between the two build scripts and gives a
single place that knows the publications.yaml schema. See that file's header
for the field contract.
"""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PUBS_YAML = ROOT / "src" / "content" / "publications.yaml"


def _esc(s: str) -> str:
    """HTML-escape text (matches build_portfolio's _esc: no quote escaping)."""
    return html_lib.escape(str(s), quote=False)


def load_publications(path: Path = PUBS_YAML) -> list[dict]:
    """Parse publications.yaml into a list of entry dicts, in file order."""
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a top-level list of publications")
    return data


def _citation_label(n: int) -> str:
    return "citation" if n == 1 else "citations"


# Inline citation-magnitude tick-bar. The bar length encodes one paper's
# citation count relative to the most-cited entry in the set; the faint
# full-width track marks that maximum. Monochrome only: #111 maps to
# var(--ink) and #d0d0c8 to var(--rule) via the locked SVG palette-adapter
# attribute selectors in index.html, so the glyph adapts to light/dark with
# no per-element edits. It must never use the #7a0000 accent sentinel (that
# renders teal and counts against the accent cap; a data glyph spends no
# accent). Width here matches the svg.cite-bar rule in index.html.
CITE_BAR_W = 52  # px


def _citation_glyph(count: int, max_count: int) -> str:
    """Inline SVG tick-bar for one publication's citation count.

    Width is proportional to count / max_count (min 2px so a low but nonzero
    count still shows). Additive only: the numeric count also stays as visible
    margin-note text, so no information lives solely inside the SVG. The
    <title> is the accessible layer, matching the dot-plot's title pattern.
    """
    if not max_count:
        return ""
    w = max(2, round(CITE_BAR_W * count / max_count))
    label = f"{count} {_citation_label(count)}"
    return (
        f'<svg class="cite-bar" viewBox="0 0 {CITE_BAR_W} 7" '
        f'role="img" aria-label="{label}">'
        f'<title>{label}</title>'
        f'<rect x="0" y="2.5" width="{CITE_BAR_W}" height="2" fill="#d0d0c8"/>'
        f'<rect x="0" y="0.5" width="{w}" height="6" fill="#111"/>'
        f'</svg>'
    )


# ─── homepage renderer ─────────────────────────────────────────────────────

def _homepage_marginnote(pub: dict) -> str:
    """Render the margin-note span body for one homepage entry.

    Two flavors, matching the hand-authored markup the YAML replaced:
      - prose `note` (the ACOs entry), or
      - a list of `links` optionally followed by a <br> + citation count.
    """
    note = pub.get("note")
    if note:
        inner = f"\n          {note}\n        "
        return f'<span class="marginnote">{inner}</span>'

    links = pub.get("links") or []
    link_lines = []
    for i, link in enumerate(links):
        sep = " &middot;" if i < len(links) - 1 else ""
        link_lines.append(
            f'<a href="{link["url"]}" aria-label="{link["aria"]}">'
            f'{_esc(link["label"])}</a>{sep}'
        )
    body = "\n          ".join(link_lines)

    count = pub.get("citations")
    if count is not None:
        body += (
            f'\n          <br>\n          '
            f'<span class="pub-citations">{count} {_citation_label(count)}</span>'
        )

    inner = f"\n          {body}\n        "
    return f'<span class="marginnote">{inner}</span>'


def render_homepage_entry(pub: dict, max_count: int = 0) -> str:
    """Render one homepage publication <div>, 4-space base indent.

    `max_count` is the largest citation count across the set, used to scale
    the inline citation tick-bar. Entries with no cached count get no glyph.
    """
    pid = pub["id"]
    has_sid = bool(pub.get("sid"))
    cls = "entry pub-entry" if has_sid else "entry"
    data_sid = f' data-sid="{pub["sid"]}"' if has_sid else ""

    detail = pub.get("detail") or ""
    detail_suffix = f" {_esc(detail)}" if detail else "."

    marginnote = _homepage_marginnote(pub)

    count = pub.get("citations")
    glyph_line = (
        f'        {_citation_glyph(count, max_count)}\n'
        if count is not None and max_count
        else ""
    )

    return (
        f'    <div class="{cls}" id="pub-{pid}"{data_sid}>\n'
        f'      <p style="margin-bottom: 0.3rem;">\n'
        f'        <span class="date">{pub["year"]}</span>\n'
        f'        <em>{_esc(pub["title"])}</em>\n'
        f'{glyph_line}'
        f'        <label for="mn-{pid}" class="margin-toggle">&#8853;</label>\n'
        f'        <input type="checkbox" aria-label="{pub["toggle_aria"]}" '
        f'id="mn-{pid}" class="margin-toggle"/>\n'
        f'        {marginnote}\n'
        f'      </p>\n'
        f'      <p style="color: var(--muted); font-size: 1.05rem; margin-top: 0;">\n'
        f'        {_esc(pub["authors"])}<br>\n'
        f'        <em>{_esc(pub["venue"])}</em>{detail_suffix}\n'
        f'      </p>\n'
        f'    </div>'
    )


def render_homepage_entries(pubs: list[dict]) -> str:
    """Render all homepage entries, blank-line separated (matches prior markup)."""
    counts = [p["citations"] for p in pubs if p.get("citations") is not None]
    max_count = max(counts) if counts else 0
    return "\n\n".join(render_homepage_entry(p, max_count) for p in pubs)


# ─── CV renderer ───────────────────────────────────────────────────────────

def render_cv_entries(pubs: list[dict]) -> str:
    """Render the CV Publications section as a numbered academic citation list.

    Each entry is an <li> in an ordered list, formatted in a compact
    AMA-style citation: authors, title, italic venue, year and volume/pages,
    then the identifier (PMID/DOI) and a cached citation count where present.
    No hyperlinks or checkbox-hack markup (the CV has no sidenote system).
    """
    items: list[str] = []
    for pub in pubs:
        authors = _esc(pub["authors"]).strip()
        if not authors.endswith("."):
            authors += "."
        title = _esc(pub["title"]).rstrip(".")
        venue = _esc(pub["venue"])
        detail = (pub.get("detail") or "").strip().rstrip(".")
        year = pub["year"]
        if detail:
            source = f"<em>{venue}</em>. {year};{detail}."
        else:
            source = f"<em>{venue}</em>. {year}."

        parts = [f"{authors} {title}. {source}"]
        sid = pub.get("sid")
        if sid and ":" in sid:
            kind, num = sid.split(":", 1)
            parts.append(f"{_esc(kind)}: {_esc(num)}.")
        count = pub.get("citations")
        if count is not None:
            label = "time" if count == 1 else "times"
            parts.append(f'<span class="pub-cited">Cited {count} {label}.</span>')

        items.append("  <li>" + " ".join(parts) + "</li>")
    return '<ol class="pub-cv-list">\n' + "\n".join(items) + "\n</ol>"


# ─── citation cache write-back ─────────────────────────────────────────────

def save_citation_counts(pubs: list[dict], path: Path = PUBS_YAML) -> None:
    """Write refreshed `citations:` values back into publications.yaml in place.

    Targeted line edits (not a full re-dump) so the file's comments, ordering,
    and formatting are preserved. Only entries that carry a `citations` value
    are touched; the matcher is scoped to each entry's own block by stopping
    at the next top-level `- id:` item.
    """
    text = path.read_text(encoding="utf-8")
    for pub in pubs:
        count = pub.get("citations")
        if count is None:
            continue
        pat = re.compile(
            rf'(\n- id: {re.escape(pub["id"])}\n(?:(?!\n- id:).)*?\n  citations: )\d+',
            re.DOTALL,
        )
        text = pat.sub(lambda m: f"{m.group(1)}{count}", text)
    path.write_text(text, encoding="utf-8")
