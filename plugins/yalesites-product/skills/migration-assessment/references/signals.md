# What to inspect on a source site, and what each signal is worth

The written answer to "what does a migration-assessment tool need to look at."
Each section says what to gather, where `probe_site.py` puts it, and how much to
trust it. **Signals are evidence, not conclusions** — every one below has a
plausible reading that is wrong.

## 1. CMS and version — `fingerprint`

| Signal | Meaning |
|---|---|
| `X-Generator` header, `<meta name="Generator">` | Names Drupal and usually the major version. Most reliable single signal. |
| `X-Drupal-Cache` | Drupal 7-era page cache. `X-Drupal-Dynamic-Cache` is Drupal 8+. |
| `/core/misc/drupal.js` 200 | Drupal 8+ layout |
| `/misc/drupal.js` 200 | Drupal 7 layout |
| `/jsonapi` 200 | Drupal 8+ **and** a structured read path — the cheapest way to get an exact content inventory |
| `/CHANGELOG.txt` | Exact patch level; frequently 403 on Pantheon, so treat absence as no information |
| aggregated `/sites/default/files/css/css_*.css` | Drupal, any version |

**Why the major version dominates the estimate.** Drupal 7 reached end of life in
January 2025, so a D7 source is running unsupported core — which makes the
migration urgent, rules out JSON:API as a read path, and usually means no
sitemap. Drupal 7 also uses different body classes (`node-type-x`, not
`page-node-type-x`), which is exactly the kind of detail that silently produces
an empty content inventory.

## 2. URL inventory — `url_inventory`

Check `source` first:

- `sitemap` — a published list. Close to a census, though it omits unpublished
  and excluded content.
- `link-crawl` — discovered by following links within a fetch budget.
  `is_lower_bound: true`. **This is a floor and nothing more.** Content not linked
  from the navigation is invisible to it; on the accessibility.yale.edu run, two
  orphan pages and roughly 60 event nodes existed that the crawl never reached.

`path_buckets` gives the section shape and `depth_histogram` the URL depth, which
is the best available proxy for sub-navigation depth.

**A crawl double-counts aliases.** Drupal serves both `/node/1` and `/welcome`.
`summary.distinct_canonicals` collapses them using `<link rel="canonical">` and
is the number to quote for sampled pages.

**Node-ID probing is the fallback for a D7 site with no sitemap**, and it is
manual: fetch `/node/N` for a spread of N to find the upper bound, then reason
about the range. Do it sparingly and label the result an estimate.

## 3. Navigation — `navigation`

`top_level_count` and `max_depth` are what matter. YaleSites has seven fixed
menus and editors can only administer items in `main` and the two utility menus,
so a source site with deep or multiple custom navigation systems needs an
information-architecture decision, not a migration step.

`max_depth: 0` means a genuinely flat menu. Look at `other_navs` for a
secondary/utility nav, and read an interior page for a section/sidebar nav — a
sidebar nav is often hand-built blocks rather than a menu, which changes how it
migrates.

## 4. Content types — `summary.source_node_types_seen`, `buckets`

The body-class node type is the strongest signal there is, so sample widely
enough to see every type. `unmapped_source_types` is the important field: each
entry is a source type with no YaleSites equivalent identified, and each one
needs an explicit decision.

Weaker fallbacks, used only when no node type is exposed: `views_rows` (a listing
page), and `<time>` plus a byline class (a dated post). Both are noisy.
Drupal 7 emits no `<time>` element at all, so the dated-post heuristic simply
does not fire on D7 sources.

## 5. Imagery — `total_images_on_sample`, `pages_with_hero`, `carousel_libraries`

Image counts on the sample indicate density, not a total. `has_hero` looks for
`hero`/`banner`/`masthead` class tokens and **misses themes that name the region
something else** — the accessibility.yale.edu homepage has a header image the
detector does not see.

`carousel_libraries` is the highest-value field here, because YaleSites has no
carousel at all. Treat it as "a carousel library is loaded" and then go look:
one loaded library drove a single-image rotator on the test site, and
`colorbox` was loaded sitewide with nothing using it.

## 6. Interactive and custom features

| Field | Reading |
|---|---|
| `native_forms` | Forms the site owner built. **Each one is a problem**, because YaleSites cannot build forms. Search and sign-in forms are filtered out. |
| `has_webform` / `pages_with_webform` | Webform module in use — the most expensive single finding, since there is no target for it |
| `external_form_vendors` | Maxient, ServiceNow, Qualtrics, Google Forms, Formstack, JotForm, Smartsheet, Wufoo, Microsoft Forms. **Good news**: an external form migrates as a link or an embed. Check the embed allow-list — Qualtrics and Microsoft Forms have `ys_embed` sources; Maxient and ServiceNow do not, so they stay outbound links. |
| `embedded_media` | YouTube and Vimeo map to media `video`. Panopto, Kaltura, SoundCloud, Tableau, ArcGIS do not — SoundCloud has an embed source, the others need a decision. |
| `interactive_patterns` | `accordion` and `tabs` have real components. `map` maps to the `google_maps` embed only if it is Google Maps. `data_table` is fine (`basic_html` allows tables). `faceted_search` and `gated_content` need decisions. |
| `inline_style_blocks` / `pages_with_inline_style` | Inline styling in body content, which `basic_html` strips. High counts mean visual rebuild work, but the count includes theme markup — read a page to see whether it is editor-authored or template noise. |
| `third_party_script_hosts` | Analytics, chat, search vendors. Only `google_tag` has a sanctioned path. |
| `pdf_link_count` | Documents to move into media `document`, or model as `resource` nodes. |

Two things the probe cannot see, and both matter: **CSS Injector or similar
site-wide custom CSS** (found on the test site — look for
`/sites/default/files/css_injector/`), and **anything behind a login**.

## 7. Events

Establish which system feeds them before scoping anything. Look for `localist`
markup or `events.yale.edu` links (Localist — maps to `ys_localist`),
`bedework`/`eventView.do` (the retired Bedework calendar — the content is an
archive, not a live feed), or native event nodes with no external reference.

Check whether the listing still has upcoming items. On the test site the events
were one-way imports from a decommissioned system with the newest dated 2022 —
archive material, and a very different conversation from live events.

## Detectors with a regression test, and why

Each of these was a real false positive found on a real run. There is a test
guarding it; add one before changing a detector.

| Fixed | What went wrong |
|---|---|
| `.css` / `.js` excluded from the crawl | An aggregated CSS file was inventoried as a page, sampled, and its selectors reported a phantom `book` content type and two phantom carousel libraries |
| Drupal 7 `node-type-x` body class | Only the D8+ patterns were matched, so every page on a D7 site had no detected type |
| `/cas`, `/saml`, `/sso` never crawled | The crawl reached a CAS sign-in page — an authentication surface the assessment must not touch |
| Sign-in forms filtered from `native_forms` | A CAS login form was reported as a form the site owner had built |
| Malformed paths rejected | A broken `href` put `/&` in the inventory as a page |
| Homepage deduplicated in the crawl | A self-link counted the homepage twice |
| DOCTYPE/ENTITY sitemaps refused | The stdlib XML parser expands internal entities; a hostile sitemap could amplify |
| Every exclusion counted in `url_inventory.excluded` | Filters dropped URLs silently, so a rule that over-fired would have undercounted the site with no trace. A non-zero `malformed_path` count is usually harmless: entity-obfuscated `mailto:` links (`&#109;&#97;&#105;...`) decode to a path of `/&`. |
