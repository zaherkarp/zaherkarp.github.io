#!/usr/bin/env python3
"""_issue_forms.py — shared parser for rendered GitHub Issue Form bodies.

GitHub renders an issue form as `### <Label>` headings followed by the value,
with unfilled optional fields rendered as `_No response_`. Both
scripts/blog_ideas_intake.py and scripts/blog_draft_edit_intake.py parse that
same shape; this module is the one place it's implemented, so a future third
consumer doesn't fork the parsing logic again.
"""

from __future__ import annotations

import re

NO_RESPONSE = "_no response_"


def parse_issue_form(body: str, known_labels: set[str] | None = None) -> dict[str, str]:
    """Split a rendered issue-form body into {normalized label: value}.

    Unfilled optional fields come through as `_No response_` and are dropped,
    so a skipped field is absent rather than literally that string.

    `known_labels` (lowercased) restricts which heading lines are treated as
    field boundaries; a heading that doesn't match one is left as literal
    content of the section currently being read. Pass this whenever a field's
    VALUE can itself contain markdown headings — e.g. a textarea capturing a
    full post body, which routinely has its own `## Section` / `### Sub`
    headings that would otherwise be misread as new form fields and silently
    truncate everything parsed so far. Omit it only when no field's value can
    plausibly contain a heading-shaped line (the historical behavior, kept as
    the default so an existing caller need not pass anything to stay
    correct).
    """
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if current is None:
            return
        value = "\n".join(buf).strip()
        if value and value.lower() != NO_RESPONSE:
            sections[current] = value

    for line in (body or "").splitlines():
        m = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
        label = m.group(1).strip().lower() if m else None
        is_boundary = m is not None and (known_labels is None or label in known_labels)
        if is_boundary:
            flush()
            current = label
            buf = []
        elif current is not None:
            buf.append(line)
    flush()
    return sections
