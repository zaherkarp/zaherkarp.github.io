# TODO

Tracking small follow-ups that need a manual step or a separate decision.

---

## Bing Webmaster Tools verification

Google Search Console verification is live (token in `index.html` and
`scripts/templates/blog/base.html`). Bing's equivalent still needs a token.

### Steps

1. Go to https://www.bing.com/webmasters and sign in.
2. Add `https://zaherkarp.com/` as a site.
3. Choose **HTML Meta Tag** as the verification method.
4. Bing returns a tag of the form:
   `<meta name="msvalidate.01" content="ABC123...">`.
5. Copy the `content` value (the token, not the full tag).
6. Paste it into BOTH places where the placeholder lives, replacing
   `REPLACE_WITH_TOKEN` and removing the surrounding `<!-- ... -->`:
   - `index.html` (around line 12)
   - `scripts/templates/blog/base.html` (around line 12)
7. Commit and push. Wait for GitHub Pages to redeploy (~1 minute).
8. Return to Bing Webmaster Tools and click **Verify**.
9. Once verified, submit `https://zaherkarp.com/sitemap.xml` under
   **Sitemaps**.

### Faster alternative

Bing supports importing site verification from Google Search Console.
Since Google verification is already live, the import flow skips steps
2–7 above. Look for "Import from Google Search Console" on the Bing
add-site screen.

---

## Google Search Console — post-verification

The verification meta tag is live, but the property still needs to be
finalized in the console:

1. Visit https://search.google.com/search-console
2. Click **Verify** on the `zaherkarp.com` property
3. Submit `https://zaherkarp.com/sitemap.xml` under **Sitemaps**
4. Optionally check **Coverage** and **Mobile Usability** after a week,
   once Google has crawled

---

<<<<<<< HEAD
## Lighthouse CI follow-ups (PR #8 merged with the audit failing)

### `.lighthouserc.json` skipAudits doesn't skip

`collect.settings.skipAudits` does NOT override the `lighthouse:no-pwa`
preset's score-based assertions. The audits in that list still run and
still fire as errors. Fix: move them out of `collect.settings.skipAudits`
and into the `assertions` block as explicit `"off"` entries.

```json
"assertions": {
  "preset": "lighthouse:no-pwa",
  "uses-text-compression": "off",
  "unminified-css": "off",
  "unminified-javascript": "off",
  "total-byte-weight": "off",
  "unused-css-rules": "off",
  "uses-long-cache-ttl": "off",
  ...rest unchanged
}
```

These are local-server artifacts (Python `http.server` doesn't gzip,
doesn't minify). They don't reflect production at GitHub Pages and
shouldn't fail the build.

### `identical-links-same-purpose` vs `label-content-name-mismatch`

The homepage has two anchors pointing at
`/blog/star-rating-predictor-methodology/`:

- Writing-section listing: visible text "The Stars Cliff Simulator:
  Methodology and Evidence"
- Project 02 card: visible text "Methodology post"

These are in genuine WCAG tension:
- `identical-links-same-purpose` requires links with the same href to
  have the same accessible name.
- `label-content-name-mismatch` (WCAG 2.5.3, "Label in Name") requires
  the accessible name to contain the visible text.

My earlier fix added `aria-label="The Stars Cliff Simulator: Methodology
and Evidence"` to the Project 02 link to satisfy the first audit, which
then triggered the second because "Methodology post" isn't contained in
that aria-label.

Three viable resolutions:

1. **Change Project 02's visible text** to match the Writing-section
   title. Drops the "Methodology post" shorthand from the project card,
   keeps a single canonical link text.
2. **Rewrite the aria-label to start with the visible text.** E.g.
   `aria-label="Methodology post — Stars Cliff Simulator: Methodology
   and Evidence"`. Satisfies both audits because "Methodology post" is
   contained verbatim AND the names match across both links if the
   Writing entry uses the same aria-label.
3. **Drop one of the two links.** The Project 02 card already describes
   the methodology near the link; arguably the Writing-section entry is
   sufficient on its own.

Option 2 is the lowest-friction fix for the audit; option 1 is cleaner
editorially. Pick one.

### Quiet bug: `dateModified` is wrong in CI

`scripts/build_blog.py:git_iso_lastmod()` uses `git log -1 --format=%cI`
to fetch each post's last-modified date. In CI, `actions/checkout@v4`
defaults to `fetch-depth: 1` (shallow clone), so `git log` only sees
the most recent commit. Result: every post's `dateModified` in JSON-LD
is set to the latest commit's timestamp, regardless of when that post
was actually last touched.

Two viable fixes:
- Set `fetch-depth: 0` in `.github/workflows/build_blog.yml` and
  `build_portfolio.yml` to fetch full history. Slower clone, correct
  data.
- Fall back to `publishDate` in the helper when git returns the same
  timestamp for many files (heuristic, fragile).

Recommend `fetch-depth: 0`. Adds ~5s to the build.

---

=======
>>>>>>> origin/main
## Other deferred items (from the indexing/tracking spec)

### Per-post Open Graph images (#7)

Skipped during the discovery/indexing batch because it adds a Pillow
build dependency and a font-install step. Tradeoff is real: ETBook
for branding consistency vs. DejaVu for zero-dep. Decide before
implementing.

### Build-provenance line on the homepage (#9, partial)

Blog pages already get a "Built YYYY-MM-DD from <sha>" footer. The
homepage doesn't, because `index.html` is hand-maintained. To add it:
extend `scripts/build_portfolio.py` to inject a `<!-- build-info:start -->
... <!-- build-info:end -->` block (mirroring the activity-grid pattern),
then update the `build_portfolio.yml` workflow to commit the result.

### `rel="me"` social verification links (item #16 from "more tracking")

One-line additions in `<head>` linking to LinkedIn, GitHub, Scholar,
mailto. Useful for IndieWeb identity-graph propagation. Five minutes.

### Citation count history (#13 from "more tracking")

`scripts/build_portfolio.py` could append `{date, sid, count}` records
to a `data/citations.json` sidecar on each Sunday cron run. Over months
this becomes a citation-growth time series per publication.

### Custom 404.html for inbound dead-link tracking (#17)

Currently GitHub Pages serves its generic 404, which doesn't load the
GoatCounter tag. A site-styled 404.html would log the missed paths and
referrers — useful for catching dead inbound links.

---

## After RSS has been live a few weeks

Check GoatCounter's **Locations / Browsers / User-Agent** breakdown,
filtered to `/blog/feed.xml`. Common reader strings: `NetNewsWire`,
`Feedly`, `Inoreader`, `FreshRSS`, `Miniflux`. The deduplicated count
is your subscriber estimate. Zero code needed.
