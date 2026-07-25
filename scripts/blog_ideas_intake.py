#!/usr/bin/env python3
"""blog_ideas_intake.py — append a phone-captured idea to the ledger.

The mobile capture path. .github/ISSUE_TEMPLATE/blog-idea.yml renders a native
form in the GitHub mobile app; submitting it opens an issue labelled
`blog-idea`; .github/workflows/blog-idea-intake.yml runs this script to turn
that issue into a ledger row, then commits and closes the issue.

Reads from the environment (the workflow passes the issue through untouched):

    ISSUE_NUMBER   the issue number, recorded as `source: issue#N`
    ISSUE_TITLE    fallback title when the form body has no Title section
    ISSUE_BODY     the rendered issue-form body

Prints the assigned id to stdout so the workflow can quote it back in its
comment. Exits 0 and prints nothing when the issue was already ingested, which
is what makes re-labelling an issue safe.

GitHub renders an issue form as `### <Label>` headings followed by the value,
with unfilled optional fields rendered as `_No response_`.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date

from _ideas import load_ideas, new_id, save_ideas

# Form field labels -> ledger fields. Matching is case-insensitive and
# tolerant of GitHub appending nothing / trailing whitespace.
SECTION_ALIASES = {
    "title": "title",
    "angle": "note",
    "note": "note",
    "the angle": "note",
    "tags": "tags",
}

NO_RESPONSE = "_no response_"


def parse_issue_form(body: str) -> dict[str, str]:
    """Split a rendered issue-form body into {normalized label: value}.

    Unfilled optional fields come through as `_No response_` and are dropped,
    so a skipped field is absent rather than literally that string.
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
        if m:
            flush()
            current = m.group(1).strip().lower()
            buf = []
        elif current is not None:
            buf.append(line)
    flush()
    return sections


def strip_em_dashes(text: str) -> str:
    """Ledger titles/notes must be em-dash-clean (lint_ideas check 7).

    A phone keyboard produces them readily, and a capture is not worth failing
    CI over, so normalize on the way in rather than reject. Mirrors what
    build_portfolio does when pulling post frontmatter into homepage chrome.
    """
    return re.sub(r"\s*—\s*", ", ", text)


def build_entry(number: str, title: str, body: str, existing: list[dict]) -> dict:
    sections = parse_issue_form(body)
    fields: dict[str, str] = {}
    for label, value in sections.items():
        key = SECTION_ALIASES.get(label)
        if key:
            fields[key] = value

    # The form's Title field wins; the issue title is the fallback for an
    # issue hand-labelled `blog-idea` without using the template at all.
    resolved_title = fields.get("title") or re.sub(r"^\s*idea:\s*", "", title or "", flags=re.I)
    resolved_title = strip_em_dashes(resolved_title.strip())
    if not resolved_title:
        raise ValueError("no title found in the issue form or the issue title")

    tags = [t.strip() for t in re.split(r"[,\n]", fields.get("tags", "")) if t.strip()]

    return {
        "id": new_id(resolved_title, existing),
        "title": resolved_title,
        "note": strip_em_dashes(fields.get("note", "").replace("\n", " ").strip()),
        "tags": tags,
        "added": date.today(),
        "status": "idea",
        "source": f"issue#{number}",
    }


def main() -> int:
    number = (os.environ.get("ISSUE_NUMBER") or "").strip()
    title = os.environ.get("ISSUE_TITLE") or ""
    body = os.environ.get("ISSUE_BODY") or ""
    if not number:
        print("ISSUE_NUMBER is required", file=sys.stderr)
        return 2

    ideas = load_ideas()

    # Idempotency: labelling an already-ingested issue must not duplicate it.
    # The `issues: [opened, labeled]` trigger fires twice for a templated
    # issue (the template applies the label at creation), so this is the
    # normal path, not an edge case.
    source = f"issue#{number}"
    if any(str(e.get("source", "")) == source for e in ideas):
        print(f"::notice::{source} already in the ledger; nothing to do", file=sys.stderr)
        return 0

    try:
        entry = build_entry(number, title, body, ideas)
    except ValueError as e:
        print(f"::error::{e}", file=sys.stderr)
        return 1

    ideas.append(entry)
    save_ideas(ideas)
    # stdout is the workflow's channel for the assigned id.
    print(entry["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
