# edit_blog — terminal (curses) editor for blog posts

`scripts/edit_blog.py` is a small, self-contained TUI for writing and
editing `src/content/blog/*.md`: a frontmatter form (title, date, draft,
tags, description, plus the two optional homepage/life-in-weeks fields)
sitting above a scrollable plain-text body pane. It writes valid
markdown + YAML frontmatter through `python-frontmatter`, so its output
round-trips cleanly through `build_blog.py` / `lint_blog.py`.

It is intentionally a **plain text editor**: no markdown / Mermaid /
KaTeX rendering, no live preview, no syntax highlighting. If you want
the lint + preview + publish flow around a post, that lives in the
[`scripts/blog`](./blog.md) CLI; `edit_blog.py` is just the keyboard
surface for getting words into a file.

> **Companion docs:** [scripts/blog.md](./blog.md) is the build/lint/publish
> playbook and [scripts/blog-cheatsheet.md](./blog-cheatsheet.md) is the
> task-oriented quick reference. This file documents the editor only.

---

## 1. Setup

The editor needs the project venv (for `python-frontmatter`) and a real
interactive terminal. From the repo root:

```bash
cd ~/git/zaherkarp.github.io
source .venv/bin/activate        # every new shell session
```

If the venv does not exist yet, create it once:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

> **Why the venv matters.** `edit_blog.py` imports `frontmatter` (and,
> on save, `lint_blog` / `build_blog`). Without the activated venv you
> get `ModuleNotFoundError: No module named 'frontmatter'`. Same root
> cause documented for the `blog` CLI in
> [scripts/blog.md](./blog.md) §Setup.

The editor will not run outside a TTY. Piping or redirecting stdin/stdout
makes it exit with code 2 and the message
`edit_blog.py needs an interactive terminal` — so it never runs in CI.
Run it in a real terminal (the VS Code integrated terminal counts; a
piped command does not).

---

## 2. Running it

Four invocation forms (the first git-script run also self-installs the
repo's pre-push hook via `install_git_hooks()`, so the first launch may
print a one-line hook notice):

```bash
python scripts/edit_blog.py                 # picker: "+ New post" + every existing post
python scripts/edit_blog.py --new           # jump straight into a blank new-post editor
python scripts/edit_blog.py --edit <slug>   # open src/content/blog/<slug>.md
python scripts/edit_blog.py <slug>          # shorthand for --edit <slug>
```

`<slug>` is the filename stem (with or without the `.md` suffix). A
missing file exits with `No such post: …`. `--new` and a positional
slug are mutually exclusive.

To test against a throwaway file instead of a real post, just make a new
post (`--new`), give it a title, and save — it lands as a `draft: true`
file you can delete afterward (`rm src/content/blog/<slug>.md`).

---

## 3. The picker

Launched when you run with no arguments. It lists every post in
`src/content/blog/`, **drafts floated to the top** (resuming an
in-progress draft is the common case), each group newest-first. A
post counts as a draft if its frontmatter says `draft: true` *or* the
filename starts with `_`.

| Key | Action |
|-----|--------|
| `↑` / `k`, `↓` / `j` | move selection |
| `PgUp` / `PgDn` | page the list |
| `Enter` | open the selected post (or `+ New post`) |
| `/` | start a case-insensitive title/slug filter |
| `d` | toggle a drafts-only view |
| `Esc` | clear an active filter, else quit |
| `q` | quit |

**Search (`/`)** filters by substring against title *or* slug and
composes with the draft toggle. While typing: `Enter` keeps the filter
and returns to navigation, `Esc` abandons the query, `Backspace` edits
it. The header shows the live match count, the draft count, and the
active filter.

---

## 4. The editor

Two zones, separated by a divider rule:

- **Form** — seven labelled fields, top of the screen (see §5).
- **Body** — the scrollable markdown pane below the divider.

The **divider** carries a right-aligned `N words · M min` readout,
computed with `build_blog`'s own `count_words` / `reading_time_minutes`,
so it matches the reading time the build stamps on the published post.

The **status bar** (bottom) shows a leading `*` when there are unsaved
changes, plus the last action / hint.

> The view needs at least `len(fields) + 3` rows and 40 columns; below
> that it shows a "Terminal too small" notice until you resize.

### Moving around

`Tab` / `Shift-Tab` cycle focus through the seven form fields and then
the body, wrapping around. Within a field or the body, the arrow keys,
`Home`/`End`, and `PgUp`/`PgDn` (body) move the cursor as you'd expect.
`Enter` in the body splits the line; `Backspace`/`Delete` join lines at
the edges.

> `Tab` is reserved for field navigation, so the body **cannot** insert
> a literal tab character. Long lines are truncated in the view but
> stored and saved intact (no horizontal soft-wrap).

### Undo / redo

`Ctrl-Z` undoes and `Ctrl-Y` (or `Ctrl-R`) redoes, across both the form
fields and the body. A run of consecutive same-kind edits (e.g. a burst
of typing) collapses into a single undo step, and any cursor move or
focus change starts a fresh group — so an undo never jumps the cursor
across an intervening navigation. The history is capped, so a long
session can't grow it without bound. The status bar reports `Undo` /
`Redo` (or `Nothing to undo` / `Nothing to redo` at the ends).

> The editor puts the terminal in `curses.raw()` mode so that control
> keys (`Ctrl-S`, `Ctrl-Q`, `Ctrl-Z`, `Ctrl-Y`, `Ctrl-R`, `Esc`) reach
> the editor directly. Without it, the tty intercepts `Ctrl-S`/`Ctrl-Q`
> as XOFF/XON flow control and the save/quit keys silently do nothing.
> The trade-off is deliberate: `Ctrl-C` no longer raises
> `KeyboardInterrupt` — quit with `Ctrl-Q` or `Esc` instead.

---

## 5. Form fields

Display order top-to-bottom; the file is always serialized in the
canonical title-first key order regardless of how you fill them in.

| Label | Frontmatter key | Notes |
|-------|-----------------|-------|
| Title | `title` | Required. Drives the slug on a new post. |
| Date | `publishDate` | `YYYY-MM-DD`. Defaults to today on a new post. |
| Draft | `draft` | A `[x]` checkbox — **Space** (or Enter / `x`) toggles it. New posts default to `true`. |
| Tags | `tags` | Comma-separated; split into a YAML list on save. Empty → key omitted. |
| Desc | `description` | Optional. Empty → key omitted. |
| MarginNote | `homepageMarginnote` | Optional. Homepage writing-list margin note. Must be additive to title+description (`lint_notes.py` enforces). |
| Lifeweek | `lifeweek_topic` | Optional. Label for the 💭 dot in the life-in-weeks grid. |

Empty optional fields are dropped from the frontmatter rather than
written as blanks. A `vocab_exempt` list, if present on a post you open,
is **preserved untouched** (the form doesn't expose it).

---

## 6. Saving, slugs, and lint-on-save

`Ctrl-S` saves. Before writing, the editor validates:

- **Title required** — empty title refuses to save.
- **Date must be `YYYY-MM-DD`** — a bad date refuses to save.

On a **new** post the filename is derived from the title via
`slugify()` (ascii-fold, lowercase, hyphenate), suffixed `-2`, `-3`, …
if that slug already exists. **Editing an existing post's title does
NOT rename the file** — renaming would orphan the `/blog/<slug>/` URL
and the homepage writing list. To publish under a new slug, create a
new post.

After a successful write, the editor runs `lint_blog.check_post()` on
the saved file — the *same* check that gates CI — and surfaces the first
violation in the status bar (e.g. an HTML comment in a published post, a
blank line inside an `<svg>`, a Mermaid diagram written as a blockquote).
`check_post` skips drafts by design, so this only fires on `draft: false`
posts. Any lint import/run failure is swallowed: **a save is never
blocked by the linter.**

---

## 7. Quitting

`Ctrl-Q` (or `Esc`) quits. With unsaved changes it prompts
`[s]ave  [d]iscard  [c]ancel`:

- `s` — save (and quit only if the save succeeds),
- `d` — discard and quit,
- `c` / `Esc` — cancel and stay in the editor.

---

## 8. Out of scope (by design)

This is a small editor. Deliberately **not** implemented:
search-and-replace, text selection / copy-paste, mouse support,
multi-file editing, horizontal soft-wrap, and any markdown/Mermaid/KaTeX
rendering or preview. (Undo/redo *is* supported — see §4.) For anything
past plain typing, edit the `.md` file in your normal editor and use the
[`blog`](./blog.md) CLI for the preview/lint/publish loop.

---

## 9. Local test checklist

A quick pass to confirm the editor works on your machine:

```bash
source .venv/bin/activate
python scripts/edit_blog.py --help          # prints usage, exits 0
echo "" | python scripts/edit_blog.py ; echo $?   # prints TTY message, exits 2
```

Then, interactively:

1. `python scripts/edit_blog.py` → picker opens; drafts are at the top.
2. `/` and type a few letters → list filters live; `Esc` clears it.
3. `d` → list narrows to drafts only; `d` again restores it.
4. `Enter` on `+ New post` → blank editor; `Draft` shows `[x]`.
5. Type a Title, `Tab` to the body, type a line, `Ctrl-S` →
   status bar shows `Saved src/content/blog/<slug>.md`.
6. Type more, then `Ctrl-Z` a few times → edits undo; `Ctrl-Y`
   (or `Ctrl-R`) redoes them.
7. `Ctrl-Q` → exits cleanly (or prompts to save if you left edits).
8. `rm src/content/blog/<slug>.md` to clean up the throwaway post.

To eyeball a lint-on-save message, set the post `draft: false` (Space on
the Draft field), put an `<!-- comment -->` in the body, and `Ctrl-S` —
the status bar should report a lint issue while still saving the file.
