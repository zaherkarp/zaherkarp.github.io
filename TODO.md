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
