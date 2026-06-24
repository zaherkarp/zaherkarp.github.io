#!/usr/bin/env python3
"""Terminal (curses) editor for blog posts in src/content/blog/*.md.

A small, self-contained text editor: a frontmatter form (title, date, draft,
tags, description) over a scrollable plain-text body pane. It creates new posts
and edits existing ones, writing valid markdown + YAML frontmatter through the
python-frontmatter library, so the output round-trips cleanly through
build_blog.py / lint_blog.py.

It is intentionally plain: NO markdown / mermaid / KaTeX rendering, NO live
preview, NO syntax highlighting. Deliberately out of scope for this MVP:
search/replace, selection / copy-paste, mouse, multi-file editing, and
horizontal soft-wrap (long lines are truncated in the view but stored and saved
intact). Tab is reserved for moving between fields, so the body cannot insert a
literal tab. Ctrl-Z undoes and Ctrl-Y (or Ctrl-R) redoes, across both the body
pane and the form fields; consecutive same-kind keystrokes coalesce into one
step, and the history is capped.

In the picker, drafts float to the top of the list (the common case is resuming
an in-progress draft), "d" toggles a drafts-only view, and "/" starts a
case-insensitive title/slug filter (composes with the draft toggle); the header
shows the draft count and active filter.

The form exposes the two optional frontmatter fields that feed the homepage and
the life-in-weeks grid (homepageMarginnote, lifeweek_topic) alongside the core
fields; vocab_exempt (a list) is still carried through untouched. The divider
shows a live word count + reading time, and a save runs lint_blog.check_post on
the written file (non-drafts only, matching CI) and reports any violation in the
status bar.

Usage:
    python scripts/edit_blog.py                 # picker: "New post" + existing posts
    python scripts/edit_blog.py --new           # blank new-post editor
    python scripts/edit_blog.py --edit <slug>   # open src/content/blog/<slug>.md
    python scripts/edit_blog.py <slug>          # shorthand for --edit

Dev-only: curses needs a real terminal, so this never runs in CI. New posts
default to draft: true (and lint_blog.py skips drafts). Editing an existing
post's title does NOT rename the file (renaming would orphan /blog/<slug>/ URLs
and the homepage writing list); save under a new slug by creating a new post.
"""

from __future__ import annotations

import argparse
import curses
import locale
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import frontmatter

from _common import REPO_ROOT, install_git_hooks

install_git_hooks()

POSTS_DIR = REPO_ROOT / "src" / "content" / "blog"

# Form fields shown above the body pane, in display + save order. "draft" is a
# toggle rather than a free-text field.
FIELD_KEYS = ["title", "date", "draft", "tags", "description", "marginnote", "lifeweek"]
FIELD_LABELS = {
    "title": "Title",
    "date": "Date",
    "draft": "Draft",
    "tags": "Tags",
    "description": "Desc",
    "marginnote": "MarginNote",
    "lifeweek": "Lifeweek",
}
# Canonical frontmatter key order when serializing (matches existing posts).
SAVE_ORDER = [
    "title",
    "description",
    "publishDate",
    "draft",
    "tags",
    "homepageMarginnote",
    "lifeweek_topic",
    "vocab_exempt",
]

FOCUS_FORM = "form"
FOCUS_BODY = "body"


# --------------------------------------------------------------------------- #
# Pure helpers (no curses) -- unit-testable without a terminal.
# --------------------------------------------------------------------------- #
def slugify(title: str) -> str:
    """Kebab-case slug from a title: ascii-fold, lowercase, hyphenate."""
    norm = unicodedata.normalize("NFKD", title)
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    out = []
    prev_hyphen = False
    for ch in norm.lower():
        if ch.isalnum() and ch.isascii():
            out.append(ch)
            prev_hyphen = False
        else:
            if not prev_hyphen:
                out.append("-")
                prev_hyphen = True
    return "".join(out).strip("-")


def unique_path(slug: str) -> Path:
    """Return POSTS_DIR/<slug>.md, suffixing -2, -3, ... if it already exists."""
    candidate = POSTS_DIR / f"{slug}.md"
    n = 2
    while candidate.exists():
        candidate = POSTS_DIR / f"{slug}-{n}.md"
        n += 1
    return candidate


def build_metadata(state: "EditorState") -> dict:
    """Build the frontmatter dict in canonical order, omitting empty optionals."""
    meta: dict = {}
    for key in SAVE_ORDER:
        if key == "title":
            meta["title"] = state.fields["title"].strip()
        elif key == "publishDate":
            meta["publishDate"] = date.fromisoformat(state.fields["date"].strip())
        elif key == "draft":
            meta["draft"] = state.fields["draft"].strip().lower() == "true"
        elif key == "description":
            desc = state.fields["description"].strip()
            if desc:
                meta["description"] = desc
        elif key == "tags":
            tags = [t.strip() for t in state.fields["tags"].split(",") if t.strip()]
            if tags:
                meta["tags"] = tags
        elif key == "homepageMarginnote":
            note = state.fields["marginnote"].strip()
            if note:
                meta["homepageMarginnote"] = note
        elif key == "lifeweek_topic":
            topic = state.fields["lifeweek"].strip()
            if topic:
                meta["lifeweek_topic"] = topic
        else:
            # Preserved optional keys carried through from a loaded post (today
            # just vocab_exempt, a list the form does not expose).
            value = state.preserved.get(key)
            if value:
                meta[key] = value
    return meta


def serialize(state: "EditorState") -> str:
    """Render the post to a frontmatter+markdown string."""
    meta = build_metadata(state)
    post = frontmatter.Post("\n".join(state.body), **meta)
    # sort_keys=False keeps the canonical title-first order from build_metadata
    # (PyYAML sorts alphabetically by default); allow_unicode keeps accented
    # text and em-dashes literal rather than \uXXXX-escaped.
    return frontmatter.dumps(post, sort_keys=False, allow_unicode=True)


def load_post_rows() -> list[dict]:
    """List existing posts, newest first, for the picker."""
    rows = []
    for path in POSTS_DIR.glob("*.md"):
        try:
            post = frontmatter.load(path)
            meta = post.metadata
        except Exception:
            meta = {}
        pub = meta.get("publishDate")
        try:
            sort_key = date.fromisoformat(str(pub)) if pub else None
        except ValueError:
            sort_key = None
        rows.append(
            {
                "path": path,
                "title": str(meta.get("title", path.stem)),
                "date": str(pub) if pub else "",
                "draft": bool(meta.get("draft", False)) or path.name.startswith("_"),
                "sort_key": sort_key,
                "mtime": path.stat().st_mtime,
            }
        )
    # Drafts float to the top (resume-in-progress is the common case), then each
    # group is newest-first. reverse=True makes draft True sort before False.
    rows.sort(
        key=lambda r: (
            r["draft"],
            r["sort_key"].toordinal() if r["sort_key"] else -1,
            r["mtime"],
        ),
        reverse=True,
    )
    return rows


# Undo history is capped so a long session can't grow it without bound; each
# snapshot is a shallow copy of the editable state, so the cost is small.
UNDO_MAX = 200

# Pressing one of these breaks undo coalescing (the next edit starts a fresh
# group), so an undo never jumps the cursor across an intervening navigation.
_NAV_KEYS = {
    curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN,
    curses.KEY_HOME, curses.KEY_END, curses.KEY_NPAGE, curses.KEY_PPAGE,
}


# --------------------------------------------------------------------------- #
# Editor state
# --------------------------------------------------------------------------- #
@dataclass
class Snapshot:
    """An undo/redo point: a shallow copy of everything an edit can change."""
    body: list[str]
    fields: dict
    focus: str
    field_idx: int
    fcur: int
    cy: int
    cx: int


@dataclass
class EditorState:
    path: Path | None = None
    fields: dict = field(default_factory=dict)
    body: list[str] = field(default_factory=lambda: [""])
    preserved: dict = field(default_factory=dict)  # untouched optional keys
    focus: str = FOCUS_FORM
    field_idx: int = 0
    fcur: int = 0          # cursor column within the active form field
    cy: int = 0            # body cursor line
    cx: int = 0            # body cursor column
    scroll: int = 0        # first body line shown
    dirty: bool = False
    status: str = ""
    undo_stack: list = field(default_factory=list)
    redo_stack: list = field(default_factory=list)
    last_edit_kind: str | None = None  # coalescing key for checkpoint()

    def snapshot(self) -> "Snapshot":
        return Snapshot(
            body=list(self.body),
            fields=dict(self.fields),
            focus=self.focus,
            field_idx=self.field_idx,
            fcur=self.fcur,
            cy=self.cy,
            cx=self.cx,
        )

    def restore(self, snap: "Snapshot") -> None:
        self.body = list(snap.body)
        self.fields = dict(snap.fields)
        self.focus = snap.focus
        self.field_idx = snap.field_idx
        self.fcur = snap.fcur
        self.cy = snap.cy
        self.cx = snap.cx

    def checkpoint(self, kind: str) -> None:
        """Record an undo point before a mutation, coalescing same-kind runs.

        Call this inside a mutation guard, just before changing the buffer, so a
        no-op keystroke never creates a dead undo step. A run of consecutive
        edits of the same `kind` (e.g. typing) collapses to a single undo;
        navigation/focus changes reset `last_edit_kind` to break the run.
        """
        if kind != self.last_edit_kind:
            self.undo_stack.append(self.snapshot())
            if len(self.undo_stack) > UNDO_MAX:
                del self.undo_stack[:-UNDO_MAX]
            self.redo_stack.clear()
        self.last_edit_kind = kind

    @classmethod
    def new(cls) -> "EditorState":
        return cls(
            fields={
                "title": "",
                "date": date.today().isoformat(),
                "draft": "true",
                "tags": "",
                "description": "",
                "marginnote": "",
                "lifeweek": "",
            },
            body=[""],
            status="New post (draft). Ctrl-S save  Ctrl-Z undo  Tab next field  Ctrl-Q quit",
        )

    @classmethod
    def load(cls, path: Path) -> "EditorState":
        post = frontmatter.load(path)
        meta = post.metadata
        tags = meta.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        # homepageMarginnote and lifeweek_topic are now editable form fields;
        # only vocab_exempt (a list) is carried through untouched.
        preserved = {k: meta[k] for k in ("vocab_exempt",) if k in meta}
        body = post.content.split("\n")
        if not body:
            body = [""]
        return cls(
            path=path,
            fields={
                "title": str(meta.get("title", "")),
                "date": str(meta.get("publishDate", date.today().isoformat())),
                "draft": "true" if meta.get("draft") else "false",
                "tags": ", ".join(str(t) for t in tags),
                "description": str(meta.get("description", "")),
                "marginnote": str(meta.get("homepageMarginnote", "")),
                "lifeweek": str(meta.get("lifeweek_topic", "")),
            },
            body=body,
            preserved=preserved,
            status=f"Editing {path.name}. Ctrl-S save  Ctrl-Z undo  Tab next field  Ctrl-Q quit",
        )

    def clamp_scroll(self, body_h: int) -> None:
        if body_h < 1:
            return
        if self.cy < self.scroll:
            self.scroll = self.cy
        elif self.cy >= self.scroll + body_h:
            self.scroll = self.cy - body_h + 1


# --------------------------------------------------------------------------- #
# Save
# --------------------------------------------------------------------------- #
def save(state: EditorState) -> bool:
    """Validate and write the post. Returns True on success (status set either way)."""
    title = state.fields["title"].strip()
    if not title:
        state.status = "Cannot save: title is required"
        return False
    try:
        date.fromisoformat(state.fields["date"].strip())
    except ValueError:
        state.status = "Cannot save: date must be YYYY-MM-DD"
        return False

    if state.path is None:
        slug = slugify(title)
        if not slug:
            state.status = "Cannot save: title produces an empty slug"
            return False
        state.path = unique_path(slug)

    text = serialize(state)
    state.path.write_text(text, encoding="utf-8")
    state.dirty = False
    rel = state.path.relative_to(REPO_ROOT)
    state.status = _saved_status(state.path, rel)
    return True


def _saved_status(path: Path, rel: Path) -> str:
    """Saved-confirmation, augmented with the first lint_blog violation (if any).

    Reuses the same check_post() that gates CI, so the editor flags the
    mistakes (HTML comment in a published post, blank line in <svg>, mermaid-as-
    blockquote) that would otherwise only surface on push. check_post skips
    drafts by design, so this fires only on draft: false posts. Any failure to
    import or run the linter is swallowed; a save must never be blocked by it.
    """
    try:
        from lint_blog import check_post

        issues = check_post(path)
    except Exception:
        issues = []
    if issues:
        # check_post strings are "<file>:<line>: <message>"; show the message.
        first = issues[0].split(": ", 1)[-1]
        n = len(issues)
        return f"Saved {rel} — {n} lint issue{'s' if n != 1 else ''}: {first}"
    return f"Saved {rel}"


# --------------------------------------------------------------------------- #
# Picker screen
# --------------------------------------------------------------------------- #
def _row_matches(row: dict, query: str) -> bool:
    """Case-insensitive substring match on a post's title or slug (filename)."""
    q = query.lower()
    return q in row["title"].lower() or q in row["path"].stem.lower()


def run_picker(stdscr) -> EditorState | None:
    """Choose a post to edit, or create a new one. Returns None to quit."""
    rows = load_post_rows()
    n_drafts = sum(1 for r in rows if r["draft"])
    drafts_only = False
    query = ""           # active substring filter (composes with drafts_only)
    search_mode = False  # True while typing the query
    sel = 0
    top = 0
    curses.curs_set(0)
    while True:
        visible = rows
        if drafts_only:
            visible = [r for r in visible if r["draft"]]
        if query:
            visible = [r for r in visible if _row_matches(r, query)]
        items = [{"new": True, "title": "+ New post"}] + visible
        sel = max(0, min(sel, len(items) - 1))
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        list_h = max(1, h - 2)
        if search_mode:
            header = f"Search: {query}_  ({len(visible)} match)  (Enter keep  Esc clear)"
        elif query:
            scope = "drafts" if drafts_only else "posts"
            header = f'Filter "{query}" ({len(visible)} {scope})  (/ edit  d drafts  Esc clear  q quit)'
        elif drafts_only:
            header = f"Drafts only ({n_drafts})  (Enter open  / search  d all  q quit)"
        else:
            header = f"Open a blog post  ({n_drafts} drafts)  (Enter open  / search  d drafts  q quit)"
        stdscr.addnstr(0, 0, header.ljust(w - 1), w - 1, curses.A_REVERSE)
        if sel < top:
            top = sel
        elif sel >= top + list_h:
            top = sel - list_h + 1
        for i in range(top, min(len(items), top + list_h)):
            item = items[i]
            if item.get("new"):
                label = "+ New post"
            else:
                mark = "[draft] " if item["draft"] else ""
                d = f"{item['date']}  " if item["date"] else ""
                label = f"{d}{mark}{item['title']}"
            attr = curses.A_REVERSE if i == sel else curses.A_NORMAL
            stdscr.addnstr(1 + i - top, 0, label[: w - 1].ljust(w - 1), w - 1, attr)
        stdscr.refresh()

        key = stdscr.getch()

        # Search mode: keys build the query rather than navigate.
        if search_mode:
            if key in (curses.KEY_ENTER, 10, 13):
                search_mode = False  # keep the filter, return to nav
            elif key == 27:          # Esc: abandon the query
                search_mode = False
                query = ""
                sel = top = 0
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                query = query[:-1]
                sel = top = 0
            elif 32 <= key < 127:
                query += chr(key)
                sel = top = 0
            continue

        if key in (curses.KEY_UP, ord("k")):
            sel = max(0, sel - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            sel = min(len(items) - 1, sel + 1)
        elif key == curses.KEY_NPAGE:
            sel = min(len(items) - 1, sel + list_h)
        elif key == curses.KEY_PPAGE:
            sel = max(0, sel - list_h)
        elif key == ord("/"):
            search_mode = True
        elif key in (ord("d"), ord("D")):
            drafts_only = not drafts_only
            sel = top = 0
        elif key == 27:  # Esc clears an active filter, else quits
            if query:
                query = ""
                sel = top = 0
            else:
                return None
        elif key == ord("q"):
            return None
        elif key in (curses.KEY_ENTER, 10, 13):
            item = items[sel]
            if item.get("new"):
                return EditorState.new()
            return EditorState.load(item["path"])


# --------------------------------------------------------------------------- #
# Editor screen
# --------------------------------------------------------------------------- #
def _body_stats(body: list[str]) -> str:
    """`N words · M min` for the body, via build_blog's own counters.

    Reuses count_words/reading_time_minutes so the editor's readout matches the
    reading-time the build stamps on the published post. Best-effort: any import
    or compute failure yields an empty string and the plain divider is drawn.
    """
    try:
        from build_blog import count_words, reading_time_minutes

        words = count_words("\n".join(body))
        return f"{words} words · {reading_time_minutes(words)} min"
    except Exception:
        return ""


def draw(stdscr, state: EditorState) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    nfields = len(FIELD_KEYS)
    if h < nfields + 3 or w < 40:
        stdscr.addnstr(0, 0, f"Terminal too small (need >= {nfields + 3} rows, 40 cols)", w - 1)
        stdscr.refresh()
        return
    body_h = h - nfields - 2
    label_w = max(len(v) for v in FIELD_LABELS.values()) + 2

    cursor_yx = (0, 0)
    # Form fields.
    for i, key in enumerate(FIELD_KEYS):
        active = state.focus == FOCUS_FORM and state.field_idx == i
        label = FIELD_LABELS[key].rjust(label_w - 2) + ": "
        if key == "draft":
            checked = state.fields["draft"].strip().lower() == "true"
            value = f"[{'x' if checked else ' '}] draft (space toggles)"
        else:
            value = state.fields[key]
        attr = curses.A_REVERSE if active else curses.A_NORMAL
        stdscr.addnstr(i, 0, label, label_w, curses.A_BOLD if active else curses.A_NORMAL)
        stdscr.addnstr(i, label_w, value[: w - label_w - 1].ljust(w - label_w - 1), w - label_w - 1, attr)
        if active and key != "draft":
            cursor_yx = (i, label_w + min(state.fcur, len(value)))

    # Divider, with a right-aligned word-count / reading-time readout.
    stats = _body_stats(state.body)
    dash_w = w - 1
    if stats and len(stats) + 2 <= dash_w:
        divider = "-" * (dash_w - len(stats) - 1) + " " + stats
    else:
        divider = "-" * dash_w
    stdscr.addnstr(nfields, 0, divider, w - 1)

    # Body pane.
    for row in range(body_h):
        idx = state.scroll + row
        y = nfields + 1 + row
        if idx < len(state.body):
            stdscr.addnstr(y, 0, state.body[idx][: w - 1], w - 1)
    if state.focus == FOCUS_BODY:
        cursor_yx = (nfields + 1 + (state.cy - state.scroll), min(state.cx, w - 1))

    # Status bar.
    flag = "*" if state.dirty else " "
    status = f"{flag} {state.status}"
    stdscr.addnstr(h - 1, 0, status[: w - 1].ljust(w - 1), w - 1, curses.A_REVERSE)

    try:
        stdscr.move(*cursor_yx)
    except curses.error:
        pass
    stdscr.refresh()


def handle_form_key(state: EditorState, key) -> None:
    if key in _NAV_KEYS:
        state.last_edit_kind = None  # break undo coalescing on a cursor move
    fkey = FIELD_KEYS[state.field_idx]
    if fkey == "draft":
        if key in (" ", curses.KEY_ENTER, 10, 13, "x"):
            state.checkpoint("toggle")
            checked = state.fields["draft"].strip().lower() == "true"
            state.fields["draft"] = "false" if checked else "true"
            state.dirty = True
        return

    value = state.fields[fkey]
    if key == curses.KEY_LEFT:
        state.fcur = max(0, state.fcur - 1)
    elif key == curses.KEY_RIGHT:
        state.fcur = min(len(value), state.fcur + 1)
    elif key == curses.KEY_HOME:
        state.fcur = 0
    elif key == curses.KEY_END:
        state.fcur = len(value)
    elif key in (curses.KEY_BACKSPACE, "\x7f", "\b", "\x08"):
        if state.fcur > 0:
            state.checkpoint("delete")
            state.fields[fkey] = value[: state.fcur - 1] + value[state.fcur:]
            state.fcur -= 1
            state.dirty = True
    elif key == curses.KEY_DC:
        if state.fcur < len(value):
            state.checkpoint("delete")
            state.fields[fkey] = value[: state.fcur] + value[state.fcur + 1:]
            state.dirty = True
    elif isinstance(key, str) and key.isprintable():
        state.checkpoint("type")
        state.fields[fkey] = value[: state.fcur] + key + value[state.fcur:]
        state.fcur += 1
        state.dirty = True


def handle_body_key(state: EditorState, key, body_h: int) -> None:
    if key in _NAV_KEYS:
        state.last_edit_kind = None  # break undo coalescing on a cursor move
    line = state.body[state.cy]
    if key == curses.KEY_LEFT:
        if state.cx > 0:
            state.cx -= 1
        elif state.cy > 0:
            state.cy -= 1
            state.cx = len(state.body[state.cy])
    elif key == curses.KEY_RIGHT:
        if state.cx < len(line):
            state.cx += 1
        elif state.cy < len(state.body) - 1:
            state.cy += 1
            state.cx = 0
    elif key == curses.KEY_UP:
        if state.cy > 0:
            state.cy -= 1
            state.cx = min(state.cx, len(state.body[state.cy]))
    elif key == curses.KEY_DOWN:
        if state.cy < len(state.body) - 1:
            state.cy += 1
            state.cx = min(state.cx, len(state.body[state.cy]))
    elif key == curses.KEY_HOME:
        state.cx = 0
    elif key == curses.KEY_END:
        state.cx = len(line)
    elif key == curses.KEY_NPAGE:
        state.cy = min(len(state.body) - 1, state.cy + body_h)
        state.cx = min(state.cx, len(state.body[state.cy]))
    elif key == curses.KEY_PPAGE:
        state.cy = max(0, state.cy - body_h)
        state.cx = min(state.cx, len(state.body[state.cy]))
    elif key in (curses.KEY_ENTER, 10, 13, "\n", "\r"):
        state.checkpoint("newline")
        rest = line[state.cx:]
        state.body[state.cy] = line[: state.cx]
        state.body.insert(state.cy + 1, rest)
        state.cy += 1
        state.cx = 0
        state.dirty = True
    elif key in (curses.KEY_BACKSPACE, "\x7f", "\b", "\x08"):
        if state.cx > 0:
            state.checkpoint("delete")
            state.body[state.cy] = line[: state.cx - 1] + line[state.cx:]
            state.cx -= 1
            state.dirty = True
        elif state.cy > 0:
            state.checkpoint("delete")
            prev = state.body[state.cy - 1]
            state.cx = len(prev)
            state.body[state.cy - 1] = prev + line
            del state.body[state.cy]
            state.cy -= 1
            state.dirty = True
    elif key == curses.KEY_DC:
        if state.cx < len(line):
            state.checkpoint("delete")
            state.body[state.cy] = line[: state.cx] + line[state.cx + 1:]
            state.dirty = True
        elif state.cy < len(state.body) - 1:
            state.checkpoint("delete")
            state.body[state.cy] = line + state.body[state.cy + 1]
            del state.body[state.cy + 1]
            state.dirty = True
    elif isinstance(key, str) and key.isprintable():
        state.checkpoint("type")
        state.body[state.cy] = line[: state.cx] + key + line[state.cx:]
        state.cx += 1
        state.dirty = True


def confirm_quit(stdscr, state: EditorState) -> bool:
    """Return True if the editor should exit."""
    if not state.dirty:
        return True
    state.status = "Unsaved changes: [s]ave  [d]iscard  [c]ancel"
    draw(stdscr, state)
    while True:
        key = stdscr.get_wch()
        if key in ("s", "S"):
            return save(state)
        if key in ("d", "D"):
            return True
        if key in ("c", "C", "\x1b"):
            state.status = "Cancelled"
            return False


def run_editor(stdscr, state: EditorState) -> None:
    curses.curs_set(1)
    stdscr.keypad(True)
    # raw() delivers control chars (Ctrl-S/Q/Z/Y/R, Esc) to get_wch uniformly
    # instead of letting the tty intercept them as signals or flow control;
    # Ctrl-Q (with its save/discard confirm) is the deliberate quit, so losing
    # Ctrl-C's KeyboardInterrupt here is intended, not a regression.
    curses.raw()
    nfields = len(FIELD_KEYS)
    while True:
        draw(stdscr, state)
        h, _ = stdscr.getmaxyx()
        body_h = max(1, h - nfields - 2)
        try:
            key = stdscr.get_wch()
        except curses.error:
            continue

        if key == curses.KEY_RESIZE:
            state.clamp_scroll(body_h)
            continue
        # Ctrl-S (save), Ctrl-Q (quit).
        if key == "\x13":
            save(state)
            continue
        if key in ("\x11", "\x1b"):
            if confirm_quit(stdscr, state):
                return
            continue
        # Ctrl-Z (undo), Ctrl-Y / Ctrl-R (redo).
        if key == "\x1a":
            if state.undo_stack:
                state.redo_stack.append(state.snapshot())
                state.restore(state.undo_stack.pop())
                state.last_edit_kind = None
                state.dirty = True
                state.clamp_scroll(body_h)
                state.status = "Undo"
            else:
                state.status = "Nothing to undo"
            continue
        if key in ("\x19", "\x12"):
            if state.redo_stack:
                state.undo_stack.append(state.snapshot())
                state.restore(state.redo_stack.pop())
                state.last_edit_kind = None
                state.dirty = True
                state.clamp_scroll(body_h)
                state.status = "Redo"
            else:
                state.status = "Nothing to redo"
            continue
        if key == "\t":
            order = len(FIELD_KEYS) + 1  # fields + body
            cur = order - 1 if state.focus == FOCUS_BODY else state.field_idx
            nxt = (cur + 1) % order
            _set_focus(state, nxt)
            continue
        if key == curses.KEY_BTAB:
            order = len(FIELD_KEYS) + 1
            cur = order - 1 if state.focus == FOCUS_BODY else state.field_idx
            nxt = (cur - 1) % order
            _set_focus(state, nxt)
            continue

        if state.focus == FOCUS_FORM:
            handle_form_key(state, key)
        else:
            handle_body_key(state, key, body_h)
            state.clamp_scroll(body_h)


def _set_focus(state: EditorState, idx: int) -> None:
    state.last_edit_kind = None  # break undo coalescing on a focus change
    if idx >= len(FIELD_KEYS):
        state.focus = FOCUS_BODY
    else:
        state.focus = FOCUS_FORM
        state.field_idx = idx
        state.fcur = len(state.fields[FIELD_KEYS[idx]])


def run(stdscr, state: EditorState | None) -> None:
    if state is None:
        state = run_picker(stdscr)
        if state is None:
            return
    run_editor(stdscr, state)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def resolve_edit_target(slug: str) -> Path:
    name = slug if slug.endswith(".md") else f"{slug}.md"
    path = POSTS_DIR / name
    if not path.exists():
        sys.exit(f"No such post: {path.relative_to(REPO_ROOT)}")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Terminal editor for blog posts.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--new", action="store_true", help="create a new post")
    group.add_argument("--edit", metavar="SLUG", help="edit src/content/blog/<slug>.md")
    parser.add_argument("slug", nargs="?", help="shorthand for --edit <slug>")
    args = parser.parse_args(argv)

    if args.new and args.slug:
        parser.error("--new cannot be combined with a slug")

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("edit_blog.py needs an interactive terminal", file=sys.stderr)
        return 2

    if args.new:
        state: EditorState | None = EditorState.new()
    elif args.edit or args.slug:
        state = EditorState.load(resolve_edit_target(args.edit or args.slug))
    else:
        state = None  # picker

    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(run, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
