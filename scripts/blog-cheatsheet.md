# blog CLI cheat sheet

The "I just want to do X right now" reference, written for the first few
weeks of using `scripts/blog`. The comprehensive playbook is
[scripts/blog.md](./blog.md); this file is the cheat sheet that sits
next to it.

Every command in this file runs from the repo root with the venv active.

---

## Before every shell session

```bash
cd ~/git/zaherkarp.github.io
source .venv/bin/activate
```

This is non-negotiable. Without it:

- `./scripts/blog ...` fails with `ModuleNotFoundError: No module named 'frontmatter'`
  because the `#!/usr/bin/env python3` shebang resolves to system Python
  (which doesn't have the CLI's deps installed).
- `git push` fails inside the pre-push hook with `python: command not found`
  because the hook calls `python`, not `python3`, and only the venv puts
  `python` on `PATH`.

If you forget and hit either error: `source .venv/bin/activate` and re-run.

---

## "I want to..."

### ...start a new post

```bash
./scripts/blog new "My Post Title"
```

What happens, in order:

1. The CLI prompts you for tags and (optional) a homepage marginnote.
   Press Enter on tags to leave them empty (`tags: []`).
2. A draft file is created at `src/content/blog/my-post-title.md` with
   `draft: true` and `publishDate: <today>` in the frontmatter.
3. Your `$EDITOR` opens the file (`code --wait` for VS Code).
4. Type your post. Save and close the editor when done — control
   returns to the terminal.

Skip the editor open (scaffold only):

```bash
./scripts/blog new "My Post Title" --no-editor
```

**Slug gotchas:** non-ASCII titles slugify lossily. Emoji-only titles
become `untitled`. `"café"` becomes `caf`. Use an ASCII title, or run
`./scripts/blog rename` after scaffolding.

---

### ...keep working on a draft I started yesterday

```bash
./scripts/blog list --drafts          # see what's open
./scripts/blog edit my-post-title     # reopen in $EDITOR
```

Slug fragment works — `./scripts/blog edit paper` will resolve to
`paper-saver-estimating-xgboost-compute-costs-on-aws` if exactly one
post matches. Ambiguous fragments abort with a list of candidates.

---

### ...see everything I've written

```bash
./scripts/blog list             # all posts: draft + live
./scripts/blog list --drafts    # drafts only
./scripts/blog list --all       # also include _-prefixed scratch files
./scripts/blog status           # drafts + last 5 published + git branch state
```

---

### ...check that my post looks right before publishing

Two checks. Run both.

```bash
# 1. Source-side lint (HTML comment leaks, blockquote-as-diagram,
#    blank lines inside <svg>, vocab — all the things that would
#    make the pre-push hook reject you later).
./scripts/blog lint my-post-title

# 2. Browser preview.
./scripts/blog preview my-post-title
```

The preview opens in your default browser, rendered from the actual
markdown. **It deliberately does NOT load KaTeX, Mermaid, or Prism**
(they're CDN scripts the site loads conditionally). If your post has:

- `\(...\)` or `\[...\]` math → looks like unstyled `\(...\)` source
- ` ```mermaid ` fenced blocks → looks like the raw `flowchart TB` text
- Language-tagged fenced code → looks like plain text without highlighting

…that is the preview being honest about what it can show. To see the
fully-rendered version, run the real build:

```bash
python scripts/build_blog.py
python3 -m http.server 8765 &
open "http://127.0.0.1:8765/blog/my-post-title/"
# Ctrl-C to stop the server when done
```

---

### ...publish my post to the live site

```bash
./scripts/blog publish my-post-title --dry-run   # show the plan, change nothing
./scripts/blog publish my-post-title             # do it
```

The dry run is recommended on every publish. It prints the title, slug,
publishDate, and the draft transition without touching anything.

The real publish does this in order:

1. **Branch check.** Refuses to run from a non-main branch unless you
   pass `--force-branch` (see blog.md §2f for the safety guard).
2. **Pre-flight lint.** All three legacy linters; aborts on any failure.
3. **Plan + confirm.** Prints the plan; `proceed?` prompt defaults to No.
4. **Flip the flag.** `draft: true` → `draft: false` on disk.
5. **Commit.** `git add <path>` and `git commit -m "Publish: <title>"`
   with a `Blog-CLI-Linted: <iso-ts>` trailer.
6. **Push.** `git push origin main`.

If step 6 fails (network blip, branch protection, non-fast-forward):
do **not** re-run `blog publish` (the flag is already flipped). See
"Push rejected" below.

---

### ...take a post down (unpublish)

```bash
./scripts/blog draft my-post-title
```

This flips `draft: true` on disk. **It does NOT commit or push.** The
post stays live until you finish the takedown manually:

```bash
git add src/content/blog/my-post-title.md
git commit -m "Drop: <title> back to draft"
git push origin main
```

This is intentional. Un-publishing usually wants human judgment about
what links broke, whether the post needs a redirect stub, etc.

---

### ...rename a post slug

```bash
./scripts/blog rename old-slug new-slug
```

Renames the source file. **Does NOT update inbound references.** After
renaming, sweep:

```bash
grep -rn old-slug index.html src/content/blog/ blog/ sitemap.xml
```

The homepage Writing list regenerates from frontmatter on next CI run,
so it heals automatically. In-prose links from other posts, the rendered
`/blog/old-slug/` directory, and external inbound links won't.

---

## The 10 commands at a glance

| Command | What it does |
|---|---|
| `blog new "Title"` | Scaffold draft, open in `$EDITOR` |
| `blog list [--drafts\|--all]` | List posts with state |
| `blog edit <slug>` | Open existing post in `$EDITOR` |
| `blog lint [<slug>]` | Run linters; scoped to one post if slug given |
| `blog preview <slug>` | Render to tempfile and open in browser |
| `blog status` | Drafts + last 5 published + git state |
| `blog publish <slug> [--dry-run\|--force-branch\|-m]` | Lint, flip draft, commit, push |
| `blog draft <slug>` | Flip back to draft (no commit/push) |
| `blog rename <old> <new>` | Rename source file (no inbound link sweep) |
| `blog config show\|set <key> <value>` | Manage redundancy toggles |

Slug arguments accept fragments — `blog edit paper` resolves to
`paper-saver-...` if exactly one post matches.

---

## Things that will trip you up

### `ModuleNotFoundError: No module named 'frontmatter'`

You forgot to activate the venv. Run `source .venv/bin/activate` from
the repo root and retry.

### `python: command not found` from `git push`

Same root cause. The pre-push hook calls `python`, which only exists
on `PATH` when the venv is active. Activate and re-push.

### `Pre-push hook: "blank line inside <svg>"`

You have a blank line between elements inside an inline `<svg>` block
in your markdown. The blank line ends markdown-it's HTML block; the rest
of the SVG gets wrapped in `<p>` tags and the chart breaks. Fix: remove
the blank line. `./scripts/blog lint <slug>` catches this before push.

### `Pre-push hook: "fragment 'X' resolved to 'Y'; proceed?"` from `publish/draft/rename`

You typed an ambiguous-but-not-quite-ambiguous slug fragment. The CLI
asks before mutating because `proceed=No` is the default. Type `n` if
that's not the post you meant, then re-run with a longer fragment.

`edit`, `lint`, and `preview` skip this prompt because they're
non-destructive.

### `git push` rejected: "fetch first" / "non-fast-forward"

`origin/main` advanced (CI committed regenerated HTML, or someone landed
a PR via the GitHub UI) since your last fetch. Fix:

```bash
git pull --rebase origin main
git push origin main
```

If your local publish commit is the same content as something already on
origin (e.g. it was squash-merged via PR), `git pull --rebase` detects
this via patch-id and silently drops the duplicate — only the
genuinely-new commits replay.

### Pre-push hook failed but you're sure the file is fixed

Open a fresh terminal. Old shells can have stale CWD or stale env. From
a clean shell:

```bash
cd ~/git/zaherkarp.github.io
source .venv/bin/activate
python scripts/lint_blog.py     # run the same script the hook runs
git push origin main
```

If `lint_blog.py` reports clean but the pre-push hook still fails, the
hook is checking something other than the source markdown — most likely
the `<p>-wrapped SVG children` check on the built HTML in `blog/`. That
means `build_blog.py` already rendered the broken version into `blog/`
on a previous run. Rebuild: `python scripts/build_blog.py`.

---

## When the published post has a bug

The post is on `origin/main` and CI has built it. The fix path:

```bash
# 1. fix the source markdown
./scripts/blog edit my-post-title
# (make the change, save, close the editor)

# 2. lint scoped to the post
./scripts/blog lint my-post-title

# 3. commit as a NEW commit (not amend — the original is already on origin)
git add src/content/blog/my-post-title.md
git commit -m "fix: <one-line description of the bug>"

# 4. push
git push origin main
```

CI rebuilds the post on push. The live site updates within ~1-2 minutes.

---

## What `blog publish` is doing under the hood

If you understand the steps, you can recover from any failure mid-flow.
For a typical publish, the CLI:

1. Reads `src/content/blog/<slug>.md` and confirms `draft: true`.
2. Verifies you're on `main` (or `--force-branch` is set AND you're
   exactly one commit ahead of `origin/main`).
3. Runs `python scripts/lint_blog.py`, `lint_vocab.py`, `lint_facts.py`
   as a pre-flight. Any non-zero exit aborts.
4. Prints the plan, prompts `proceed?` (default No).
5. Edits the file: `draft: true` → `draft: false`.
6. `git add <path>` and `git commit -m "Publish: <title>"` with the
   `Blog-CLI-Linted: <iso-ts>` trailer in the body.
7. `git push origin main`. Pre-push hook runs (and may short-circuit
   the lint blocks if `prepush_lint=skip` is set; see blog.md §3).

If something fails after step 5, the draft flag is already flipped on
disk. Re-running `blog publish` will say "nothing to commit". Finish
manually from wherever it stopped:

| Failed at | Fix |
|---|---|
| Step 6 (commit) | `git add src/content/blog/<slug>.md && git commit -m "Publish: <title>"` |
| Step 7 (push) | `git pull --rebase origin main && git push origin main` |

---

## See also

- [scripts/blog.md](./blog.md) — full playbook with architecture diagram,
  redundancy-toggle semantics, security footguns, and the file map.
- [CLAUDE.md](../CLAUDE.md) — design constraints and architectural
  invariants for the whole repo.
- [scripts/lint_facts.md](./lint_facts.md) — playbook for cross-surface
  `lint_facts` failures.
