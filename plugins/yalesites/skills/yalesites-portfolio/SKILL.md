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
vintage **2026-10**: 296 of 299 live sites, 48,285 pages, full sitemaps (the
3 uncrawled sites are named under "Rules for using this data"). Exemplar
picks come from a Sonnet screenshot review of the 8 richest usages per block
and of 24 block-rich homepages. Refresh pipeline and raw data:
`~/code/yalesites-portfolio-data` (dashboard at `dist/dashboard.html`).

## How to use this skill

| Question | Read |
|---|---|
| Adoption %, instance counts, design-option / color variant split, position norms per block | `references/block-usage.md` |
| Theme, nav position, header/footer, section layouts and section attrs, content types, D7 vs net-new gaps | `references/site-configurations.md` |
| "Who uses X best": ranked exemplar sites per block with URLs, patterns and good practices | `references/exemplars.md` |
| What goes wrong with each block (named teaching examples) | `references/anti-patterns.md` |
| Page archetypes, length norms, how pages open/close, homepage composition, tagged page-building rules | `references/page-patterns.md` |
| "Which sites use block X / theme Y / center nav", and which sites use a block most: one row per site, with `blocks_used` and a `block_counts` column (`block:count;...`, sorted by count, highest first) | `references/sites-index.csv` (grep it; do not read it whole) |

## Headline numbers (2026-10)

- Most adopted blocks: Text 99%, Image 82%, Wrapped Image 79%, Divider 76%, View 70%, Callout 69%, Button Link 69%, Grand Hero 68%, Accordion 68%.
- Feeds: Post Feed 25%, Calendar List 16%, Directory 10%, Event Calendar (month grid) 6%; the generic View block is on 70% of sites.
- Under-used blocks we invest in: Facts and Figures 13%, Tabs 12%, Wrapped Text Callout 11%, Reference Card 11%, Video Banner 4%, Related Content 1% (3 sites), Audio Player 0.3% (1 site). No block is at zero.
- Config: global theme one 67%; left nav 71%, right 21%, center 7%; basic footer 68%; focus header on 1 site.
- Built pages: median 2 blocks, 90th percentile 13. Text closes 65% of built pages; that is fine and the house preference. Strong homepages often close on an action band instead.
- 180 of 296 crawled sites (61%) are D7 migrations.

## Rules for using this data

- **Adoption is not endorsement.** Check `exemplars.md` before holding a site up as a model; `page-patterns.md` tags every rule *recommended* (data + reviewers + team conventions agree) or *common* (frequency only).
- **Cite the vintage** ("as of the 2026-10 crawl") and keep callouts to one line in tickets, PRs and docs. Never paste tables.
- **Zero-usage blocks are findings, not errors.**
- **Five live sites have no usable data.** Three could not be crawled at all and have no row in `sites-index.csv`: asclab.yale.edu (SSL error), blackvisualculture.yale.edu (HTTP 403) and unga.yale.edu (HTTP 403); that is the 299 vs 296 gap. Two more, aadhub.yale.edu and chat.finance.yale.edu, redirect to CAS login; they are in the CSV with `pages_crawled` 1 and empty block columns. (Airtable lists 300 live rows; one, invisibleuniverse, is a duplicate.)
- Survey and support-ticket data about editors lives in the `ux-research` skill; what each block *is* lives in the core `yalesites` skill's `references/blocks-reference.md`.
