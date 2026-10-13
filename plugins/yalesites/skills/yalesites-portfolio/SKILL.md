---
name: yalesites-portfolio
description: >-
  Live-portfolio knowledge base for YaleSites: real block usage, site
  configuration trends, exemplar sites, and page-building patterns measured
  across every live site on the platform (296 sites, 40k+ pages crawled).
  Use for questions like "what percent of sites use X block / center nav /
  theme two", "which sites use grand heroes (or any block) best", "what do
  typical homepages look like", "is this block actually used", and when
  building or recommending page layouts so they reflect how the community
  actually builds — especially in migration builds (D7 to YaleSites) and the
  D11 page build step. Complements the core yalesites skill (feature catalog)
  with measured adoption data.
---

# YaleSites Portfolio Knowledge Base

Measured usage data from the live YaleSites portfolio. Crawl vintage:
**2026-10 (296 of 299 live sites, 40k+ pages)**. Numbers are facts about
rendered public pages, not editor intent. Refresh pipeline lives in
`~/code/yalesites-portfolio-data` (crawler + raw data + screenshots).

## How to use this skill

| Question type | Go to |
|---|---|
| Adoption %, instance counts, config variant distributions per block | `references/block-usage.md` |
| Theme, nav position, header/footer, section layout trends | `references/site-configurations.md` |
| "Who uses X best" — exemplar sites per block, with URLs | `references/exemplars.md` |
| Homepage/page composition patterns, best practices, anti-patterns | `references/page-patterns.md` |
| "Which sites use block X / theme Y" — per-site lookup | `references/sites-index.csv` |

## Headline numbers (2026-10)

- TODO-FINAL: top-5 block adoption, zero-usage blocks, nav/theme splits
  (filled from dist/stats.md after the deep crawl aggregate)

## Rules for using this data

- **Adoption ≠ endorsement.** High usage means familiarity, not quality;
  check `exemplars.md` before holding a site up as a model.
- **Zero-usage blocks are findings, not errors** — verified against raw HTML.
- When building pages (D11 build step, migrations), default to patterns the
  community actually uses: see `page-patterns.md` before inventing a layout.
- Five sites are invisible to the crawl (CAS-walled or locked down); they are
  listed in `sites-index.csv` with `pages_crawled=0`.
- For survey/support-ticket usage data (who the editors are, pain points),
  use the `ux-research` skill's platform-usage-data reference instead; for
  what each block *is*, use the core `yalesites` skill's blocks-reference.
