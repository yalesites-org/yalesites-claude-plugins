---
name: yalesites-migration-assessment
description: "Assess a public source website — starting with Drupal, including Drupal 7 — for migration onto the YaleSites platform, and produce a migration-path assessment: source-to-YaleSites content type and component mapping, the things that will not carry over cleanly with a suggested handling for each, an effort and complexity rating, and migration-mechanism options with tradeoffs. Use when someone asks whether a site can move onto YaleSites, how big a lift a migration would be, what a department's site would look like as a YaleSites site, or for a first-pass migration scope before committing to a project. Trigger on 'assess this site for migration', 'can we migrate X onto YaleSites', 'how hard would it be to move X', 'scope a migration', or a bare source URL offered as a migration candidate. Read-only: it never authenticates to or modifies the source site."
---

# YaleSites Migration Assessment

Produce a first-pass migration assessment for a source site: what its content
is, where each piece lands on YaleSites, what will not carry over one-to-one,
and roughly what the work costs. The output is a scoping document for a human to
decide on — **not** a migration plan and **not** a mechanism decision.

## Hard rules

1. **Read-only, public, unauthenticated.** GET requests only. Never log into the
   source site, never submit a form, never touch an admin or `/cas` path. If the
   assessment needs something only visible behind a login (unpublished content,
   the real node count, the redirect table), say so in the "could not determine"
   section instead of going after it.

   `probe_site.py` enforces this rather than trusting it: HTTP(S)-only opener
   (no `file://` or `ftp://` handler exists), no automatic redirects — each hop
   is re-checked against the base host and the account-route deny-list — and
   source-controlled `Sitemap:` targets are filtered before any fetch. If you
   drive a fetch by hand, apply the same rules; the source site chooses those
   values, not you.
2. **Never recommend a migration mechanism as decided.** Migrate module vs. the
   CSV importers vs. manual rebuild is the lead developer's call, informed by
   YaleSites-Internal#1561. Present options with tradeoffs; do not pick one.
3. **Distinguish counted from estimated.** A crawl-derived page count is a lower
   bound, not a census. Label every number as one or the other. An inflated
   confidence here is what turns a scope into a bad estimate.
4. **An unrecognised source content type is a finding, not a rounding error.**
   Never quietly fold it into Page. Surface it and ask for a decision.

## Step 1 — Run the probe

`scripts/probe_site.py` does the mechanical gathering: CMS fingerprint, URL
inventory (sitemap if there is one, a bounded link crawl if there is not),
navigation tree, and per-page signals across a spread of sampled pages. Standard
library only, GET-only, honours `robots.txt`, one request at a time.

```bash
python3 scripts/probe_site.py https://source.yale.edu --sample 12 --delay 1.0 > probe.json
```

| Flag | Default | Why you would change it |
|---|---|---|
| `--sample` | 12 | More sampled pages on a site with many sections (each is one request) |
| `--delay` | 0.6s | Raise it if `robots.txt` sets a `Crawl-delay`, or the host looks fragile |
| `--crawl-pages` | 12 | Only used when there is no sitemap; raises the discovery budget |
| `--max-urls` | 5000 | Guard for a very large sitemap |
| `--max-sitemaps` | 20 | Guard for a sitemap index with many dead children |

Read `references/signals.md` for what each field in the output means and which
ones are weak. Then read the JSON before reasoning from it, in particular:

- `url_inventory.source` (`sitemap` vs `link-crawl`) and `is_lower_bound` —
  these decide how much of the assessment is measured versus inferred.
- `url_inventory.excluded` — what the filters dropped, by reason. A surprising
  count here means a rule over-fired and the page count is wrong.
- `summary.buckets_by_basis` — how each bucket was decided. A bucket counted
  under `default` is a fallback, not a measurement, and must not be quoted as
  one. On a Drupal 7 source most pages land there.
- `summary.content_forms` vs `chrome_forms` — only the former is work.

**The probe does not replace looking at the site.** Fetch two or three
representative pages yourself and read them. The signals tell you a carousel
library is loaded; only reading the page tells you it drives one image.

## Step 2 — Map content to YaleSites

Load `references/yalesites-target-model.md`. It is the authoritative target: five
content types, 36 editor-placeable components, six layouts with per-region
allow-lists, and the enumerated list of what the platform deliberately does not
do. Do not reason about YaleSites from memory — the constraints are specific and
the mapping is only useful if it is exact.

Produce two tables:

- **Content type mapping** — every source content type → target content type,
  field by field for the fields that carry data, and what happens to the fields
  with no target.
- **Component mapping** — every recurring source page pattern (hero, callout,
  link list, accordion, image grid, embedded form, listing) → the YaleSites
  component that reproduces it, or "no equivalent."

The single most common surprise: **YaleSites content types have no body field.**
Long-form source content becomes Layout Builder components with `basic_html`,
which permits no `<div>`, `<iframe>`, `<script>`, `<style>`, or inline `<img>`.
Body HTML does not migrate as HTML. Say this explicitly, every time.

## Step 3 — List what will not carry over

For each item: what it is, why it does not fit, and a concrete suggested
handling. `references/curveballs.md` has the recurring ones and how they are
normally handled. Never leave an item without a suggestion, and never present a
suggestion as free if it is not.

## Step 4 — Rate effort and complexity

Rate on the three things that actually drive the work, separately, because a site
can be tiny and still hard:

| Driver | Low | High |
|---|---|---|
| **Volume** | tens of nodes | thousands, or a large people directory |
| **Structural fit** | source types map 1:1 onto the five | several unmapped types, or content modelled as one-off layouts |
| **Rebuild burden** | short pages, few components each | long body HTML, per-page bespoke composition, heavy inline styling |

Give an overall complexity rating (low / medium / high), state which driver
dominates, and give a rough effort band with the assumption it rests on. If any
number is inferred rather than counted, say which.

## Step 5 — Present mechanism options, do not choose

Route each content bucket to an option from the mechanism table in
`references/curveballs.md`, which carries the current state of each — including
which importers exist today and which do not. The usual answer is a *different*
mechanism per bucket, so say which goes where and why (Hard rule 2 applies).

## Step 6 — Write the assessment

Follow `references/assessment-format.md`. Lead with the constraints and the
unknowns, not with a summary that reads as approval. Post it as a comment on the
relevant GitHub issue, or as a standalone document if there is no issue.

## Tests

The probe's parsing helpers are covered by unit tests with no network access:

```bash
python3 scripts/test_probe_site.py                 # this suite
bash ../../../../scripts/run-skill-tests.sh        # what CI runs, from the repo root
```

`unittest discover` over `plugins/` is deliberately not used. Python 3.11
removed namespace-package discovery, so discovery refuses to recurse into any
directory without an `__init__.py` — and scattering package markers through
shipped skill directories is worse than running the files. (The blocker is the
missing `__init__.py`, not the dash in the directory name; dashes import fine
once a marker is present.) Discovery therefore reports `Ran 0 tests ... OK` and
exits 0 — a green check that tested nothing, which is why
`scripts/run-skill-tests.sh` asserts a non-zero collected count rather than just
the absence of failures.

Every signal in `references/signals.md` marked as a past false positive has a
regression test. Add one before changing a detector.
