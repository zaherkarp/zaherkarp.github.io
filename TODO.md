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
6. Paste it into the one place the placeholder still lives, replacing
   `REPLACE_WITH_TOKEN` and removing the surrounding `<!-- ... -->`:
   - `scripts/templates/blog/base.html` (around line 14)
   It was removed from `index.html`, so the homepage needs no edit. The
   commented-out placeholder in the template does ship (inert) into every
   built blog page.
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

## Other deferred items (from the indexing/tracking spec)

### Per-post Open Graph images (#7)

Skipped during the discovery/indexing batch because it adds a Pillow
build dependency and a font-install step. Tradeoff is real: ETBook
for branding consistency vs. DejaVu for zero-dep. Decide before
implementing.

### Build-provenance line on the homepage (#9, mostly shipped)

Most of this landed already, under the marker name `updated` rather than
`build-info`. `build_updated_footer()` in `scripts/build_portfolio.py`
injects a date stamp between `<!-- updated:start -->` and
`<!-- updated:end -->` in index.html's footer (currently rendering
"Updated 2026-08."), the marker pair is registered in
`lint_markers.PAIR_MARKERS`, and `build_portfolio.yml` already commits
the regenerated index.html. What's still missing is the `<sha>` half of
the blog footer's "Built YYYY-MM-DD from <sha>" pattern: the homepage
stamp is month-precision and carries no build identifier.
`scripts/build_blog.py` already has a `git_short_sha()` helper for this;
`build_updated_footer()` could take a similar short SHA and append it.

### `rel="me"` social verification links (item #16 from "more tracking")

One-line additions in `<head>` linking to LinkedIn, GitHub, Scholar,
mailto. Useful for IndieWeb identity-graph propagation. Five minutes.

### ~~Citation count history (#13 from "more tracking")~~ DONE

Shipped, under a different name than proposed. `write_citation_snapshot()`
in `scripts/build_portfolio.py` writes a `{date, source, citations}`
record to `data/snapshots/<date>.json` on any run where at least one
fresh citation count lands (record-on-change, so most runs add nothing).
`data/snapshots/` currently holds seven real files, a citation-growth
time series per publication. Landed as `data/snapshots/<date>.json`
rather than the `data/citations.json` sidecar proposed here. Kept here
struck through rather than deleted so the item is not re-proposed.

### ~~Custom 404.html for inbound dead-link tracking (#17)~~ DONE

Shipped. `404.html` exists, is site-styled, and carries the GoatCounter
tag with the 404-prefix callback, so missed paths and referrers are
logged. Kept here struck through rather than deleted so the item is not
re-proposed.

---

## After RSS has been live a few weeks

Check GoatCounter's **Locations / Browsers / User-Agent** breakdown,
filtered to `/blog/feed.xml`. Common reader strings: `NetNewsWire`,
`Feedly`, `Inoreader`, `FreshRSS`, `Miniflux`. The deduplicated count
is your subscriber estimate. Zero code needed.
