# yalesites

Deep expertise on the YaleSites Drupal 10 platform for Claude Code.

## What it does

Gives Claude detailed knowledge of YaleSites so it can assist editors,
site builders, and the platform team with:

- Layout Builder blocks and configuration
- Manage Settings vs. Layout Builder (the most common editor confusion)
- Views — display modes, filters, the ys_views_basic architecture
- Content types (Page, Post, Event, Resource, Profile)
- Menus and navigation (Basic Nav, Mega Nav, Focus Nav)
- Content Collections (secondary navigation)
- Sitewide Settings — global themes, fonts, GTM, footer
- Media Library — all five media types
- Editorial workflow — Draft/Published/Archived, Contributor/Editor/Admin roles
- Taxonomy and vocabulary planning
- Accessibility with Editoria11y
- Google Tag Manager setup
- Localist integration
- Training catalog, office hours, and user guide navigation
- Measured usage across the live portfolio (the `yalesites-portfolio` skill)

## Skills

| Skill | What it covers |
|---|---|
| `yalesites` | What each block, setting, content type, role and workflow is |
| `yalesites-portfolio` | How the community actually builds: block adoption, design-option and config trends, exemplar and anti-pattern sites per block, and page-building patterns from the 2026-10 crawl of 296 of 299 live sites (48k pages) |

Known gaps in `yalesites-portfolio`: Gallery has no exemplar guidance yet (its screenshots failed in the review session; the maintainer tracks the re-run), and 5 live sites have no usable data (3 could not be crawled, 2 redirect to CAS login).

## Installation

```
/plugin install yalesites@yalesites-claude-plugins
```

## Skill reference files

The skill loads deeper reference material on demand:

| Topic | File |
|---|---|
| All blocks + design options | `references/blocks-reference.md` |
| Block sub-items (accordion items, cards, tiles, etc.) | `references/paragraphs-reference.md` |
| Content type field labels | `references/content-types-reference.md` |
| Views filters, sorts, display modes | `references/views-reference.md` |
| Sitewide settings (Manage Settings page) | `references/settings-reference.md` |
| User roles and editorial workflow | `references/user-roles-reference.md` |

## Related plugins

- `yalesites-product` — release prep, ticket grooming, and UX research workflows for the product team

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
