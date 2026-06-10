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


def render_homepage_entry(pub: dict) -> str:
    """Render one homepage publication <div>, 4-space base indent."""
    pid = pub["id"]
    has_sid = bool(pub.get("sid"))
    cls = "entry pub-entry" if has_sid else "entry"
    data_sid = f' data-sid="{pub["sid"]}"' if has_sid else ""

    detail = pub.get("detail") or ""
    detail_suffix = f" {_esc(detail)}" if detail else "."

    marginnote = _homepage_marginnote(pub)

    return (
        f'    <div class="{cls}" id="pub-{pid}"{data_sid}>\n'
        f'      <p style="margin-bottom: 0.3rem;">\n'
        f'        <span class="date">{pub["year"]}</span>\n'
        f'        <em>{_esc(pub["title"])}</em>\n'
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
    return "\n\n".join(render_homepage_entry(p) for p in pubs)


# ─── homepage citations figure ─────────────────────────────────────────────

# Consolidated citations figure: one horizontal bar per cited paper, sitting
# under the Publications lead. Replaces the per-entry inline tick-bars with a
# single comparable chart. Build-generated so the bars track the live counts
# (a hand-authored SVG would drift the moment a count is refreshed).
# Monochrome only: #111 -> var(--ink), #6a6a6a -> var(--muted), #d0d0c8 ->
# var(--rule) via the locked SVG palette-adapter attribute selectors in
# index.html, so it adapts to light/dark with no per-element edits. #7a0000
# (the accent sentinel) is deliberately NOT used, so the figure spends zero
# accent. Reuses figure.outcome-figure sizing + its fig-grow-x scroll-draw
# primitive (no new CSS, no 4th motion style). The exact counts also remain
# as text in each entry's margin note, so nothing lives solely in the SVG.
CITE_FIG_X0    = 95     # bar left edge
CITE_FIG_W     = 380    # usable bar field width (leaves room for the count)
CITE_FIG_PITCH = 52     # vertical row pitch
CITE_FIG_TOP   = 30     # first row label baseline

# Short, direct journal labels keyed by pub id (kept here so the figure is
# self-contained). Falls back to the full venue if an id is missing.
_CITE_FIG_LABELS = {
    "jihi":    "Health Informatics, 2014",
    "herd":    "HERD, 2019",
    "acadmed": "Academic Medicine, 2019",
}


def render_citations_figure(pubs: list[dict]) -> str:
    """Render ONE figure.outcome-figure: a citations-by-paper bar chart.

    Only entries with a cached `citations` count are plotted, sorted
    descending for a clean staircase. Returns '' if no entry carries a
    count (graceful: the marker pair then renders empty and the page falls
    back to prose plus the per-entry margin-note counts). 4-space base
    indent to match the surrounding markers in index.html.
    """
    cited = sorted(
        (p for p in pubs if p.get("citations") is not None),
        key=lambda p: p["citations"], reverse=True,
    )
    if not cited:
        return ""
    max_count = cited[0]["citations"]
    last_bar_y = CITE_FIG_TOP + (len(cited) - 1) * CITE_FIG_PITCH + 8
    height = last_bar_y + 16 + 14  # last bar height + bottom padding

    rows = []
    for i, p in enumerate(cited):
        c = p["citations"]
        label = _CITE_FIG_LABELS.get(p["id"], _esc(p["venue"]))
        count_txt = f"{c} {_citation_label(c)}"
        label_y = CITE_FIG_TOP + i * CITE_FIG_PITCH
        bar_y = label_y + 8
        bar_w = max(2, round(CITE_FIG_W * c / max_count))
        count_x = CITE_FIG_X0 + bar_w + 8
        rows.append(
            f'        <text x="{CITE_FIG_X0}" y="{label_y}" '
            f'font-family="et-book, Palatino, Georgia, serif" font-size="15" '
            f'font-style="italic" fill="#6a6a6a">{label}</text>\n'
            f'        <rect x="{CITE_FIG_X0}" y="{bar_y}" width="{CITE_FIG_W}" '
            f'height="16" fill="#d0d0c8"/>\n'
            f'        <rect x="{CITE_FIG_X0}" y="{bar_y}" width="{bar_w}" '
            f'height="16" fill="#111"><title>{_esc(label)}: {count_txt}</title></rect>\n'
            f'        <text x="{count_x}" y="{bar_y + 12}" '
            f'font-family="et-book, Palatino, Georgia, serif" font-size="14" '
            f'fill="#111">{count_txt}</text>'
        )
    body = "\n".join(rows)
    aria = "Bar chart of citations per paper, most cited first: " + "; ".join(
        f'{_CITE_FIG_LABELS.get(p["id"], p["venue"])}, '
        f'{p["citations"]} {_citation_label(p["citations"])}'
        for p in cited
    )
    return (
        f'    <figure class="outcome-figure">\n'
        f'      <figcaption>Citation counts, most cited first. Three of the six '
        f'papers carry tracked counts.</figcaption>\n'
        f'      <svg viewBox="0 0 600 {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{_esc(aria)}">\n'
        f'{body}\n'
        f'      </svg>\n'
        f'    </figure>'
    )


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
