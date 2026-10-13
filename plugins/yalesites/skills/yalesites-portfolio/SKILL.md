---
name: yalesites-portfolio
description: >-
  Measured knowledge base of the live YaleSites portfolio: real block adoption,
  design-option and color usage, site configuration trends, exemplar and
  anti-pattern sites per block, and page-building patterns, from a crawl of
  every live site (296 sites, 48k pages, Oct 2026) plus a screenshot review of
  the strongest usages. Use for "what percent of sites use X block / center nav /
  theme two", "which sites use grand heroes (or any block) best", "what does a
  typical or a strong homepage look like", "is this block actually used", for
  blast-radius sizing on tickets and PRs, and when composing or recommending
  page layouts (migration builds, the D11 page build step, docs pages) so they
  reflect how the community actually builds. Complements the core yalesites
  skill (what each block is) with evidence of how blocks are used.
---

# YaleSites Portfolio Knowledge Base

Measured facts about rendered public pages across the live portfolio. Crawl
vintage **2026-10** (296 of 299 live sites; the other 3 are CAS-walled or
locked down; 48,285 pages, full sitemaps). Exemplar picks come from a Sonnet
screenshot review of the 8 richest usages per block and of 24 block-rich
homepages. Refresh pipeline and raw data: `~/code/yalesites-portfolio-data`
(dashboard at `dist/dashboard.html`).

## How to use this skill

| Question | Read |
|---|---|
| Adoption %, instance counts, design-option / color variant split, position norms per block | `references/block-usage.md` |
| Theme, nav position, header/footer, section layouts and section attrs, content types, D7 vs net-new gaps | `references/site-configurations.md` |
| "Who uses X best": ranked exemplar sites per block with URLs, patterns and good practices | `references/exemplars.md` |
| What goes wrong with each block (named teaching examples) | `references/anti-patterns.md` |
| Page archetypes, length norms, how pages open/close, homepage composition, tagged page-building rules | `references/page-patterns.md` |
| "Which sites use block X / theme Y / center nav": one row per site | `references/sites-index.csv` (grep it; do not read it whole) |

## Headline numbers (2026-10)

- Most adopted blocks: Text 99%, Image 82%, Wrapped Image 79%, Divider 76%, View 70%, Callout 69%, Button Link 69%, Grand Hero 68%, Accordion 68%.
- Under-used blocks we invest in: Facts and Figures 13%, Tabs 12%, Wrapped Text Callout 11%, Reference Card 11%, Directory 10%, Event Calendar 6%, Video Banner 4%, Related Content 1% (3 sites), Audio Player 0.3% (1 site).
- Zero usage anywhere: Calendar List (verified against raw HTML of all 48k pages).
- Config: global theme one 67%; left nav 71%, right 21%, center 7%; basic footer 68%; focus header on 1 site.
- Built pages: median 2 blocks, 90th percentile 13. Text closes 65% of built pages; that is fine and the house preference. Strong homepages often close on an action band instead.
- 181 of 300 live sites are D7 migrations.

## Rules for using this data

- **Adoption is not endorsement.** Check `exemplars.md` before holding a site up as a model; `page-patterns.md` tags every rule *recommended* (data + reviewers + team conventions agree) or *common* (frequency only).
- **Cite the vintage** ("as of the 2026-10 crawl") and keep callouts to one line in tickets, PRs and docs. Never paste tables.
- **Zero-usage blocks are findings, not errors.**
- Five sites are not in the data (login walls or locked down); they appear in `sites-index.csv` with `pages_crawled` 0 or 1.
- Survey and support-ticket data about editors lives in the `ux-research` skill; what each block *is* lives in the core `yalesites` skill's `references/blocks-reference.md`.
