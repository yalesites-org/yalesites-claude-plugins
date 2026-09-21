# Bundled content inventory

`references/content-inventory.csv` is a snapshot of every page and post on yalesites.yale.edu: 199 rows (151 pages, 48 posts), exported 2026-08-05 from a release candidate build. Treat it as a fast starting point, not a live source.

## Why this exists

Step 1 of this skill (orienting within the site, checking for overlap before drafting something new) previously meant fetching hub pages one at a time and hoping the relevant existing page turned up in the nav. That's slow, and it misses anything that's reachable only through a tag filter rather than a menu link, which turns out to be most of the site: block reference pages, training webinars, Localist event-management guides, and release note posts are all real, real content, but none of them sit in the static nav tree.

Grepping this file first is faster and more complete than a round of fetches, for the specific question "does something like this already exist, and if so where."

## Columns

| Column | What it is |
|---|---|
| `Type` | Page or Post |
| `Title` | as published |
| `URL Path` | relative path, e.g. `/editorial-workflow`. Build the full URL as `https://yalesites.yale.edu` + this path. |
| `Section (from URL)` | inferred from the path against the known top-level structure (Platform, Community, Resource Library incl. User Guide, Trainings, Get Started, Support, Posts/Announcements, Events, Home). Inferred, not read from Drupal's actual menu config. |
| `In Known Nav Menu` | `Yes` only for rows matching a real top-nav or User Guide left-nav link, verified by fetching live pages in August 2026. Everything else reads `Not a known menu link*`, which means *unverified*, not *confirmed absent from nav*. |
| `Nav Location` | which menu and section, for the rows marked `Yes` above |
| `Content Cluster (from tags)` | a second, independent grouping from Tags/Category and a few title-keyword matches: block reference library, training catalog/webinars, release notes, Localist event-management guide, tips and tricks, community contributions, sample/demo content, homepage spotlight rotation. This is what explains most of the content that "Section (from URL)" alone would leave in a vague "Other" bucket. |
| `Published`, `CAS Protected`, `Category`, `Tags`, `Audience`, `Custom Vocab` | straight from the source export |
| `Flags` | mechanical notes: whitespace in the source title, an old `/resource-library/` URL prefix still in use next to the newer `/explore-resources/` prefix, a raw `/node/NNN` link with no alias, or something that looks like sample/demo content |

## How to use it

**Checking for overlap before drafting a new page (Step 1):** search this file for the feature or topic name before fetching anything. If something close turns up, that's the moment to surface it and ask whether this should be an edit instead of a new page, per the skill's main workflow, not a moment to keep drafting.

**Finding the real URL for a page you're linking to:** look it up here instead of guessing a slug from the title. Saves a fetch, and the whole point of the relative-link rule is not to introduce a wrong path.

**Getting oriented on a section fast:** filter by `Section (from URL)` or `Content Cluster (from tags)` to see what already exists in, say, the block reference library or the User Guide, without fetching every child page one at a time.

## What this file cannot tell you, and what to still verify live

This is a snapshot of titles, URLs, and taxonomy metadata. It says nothing about a page's actual body content, whether a feature it describes still works the way it did on 2026-08-05, or whether the page has been edited, renamed, or unpublished since. Don't cite it as a source for what a page currently says, and don't treat `Nav Location` as gospel: it's based on a nav structure verified once, on a different environment than whatever you're working against today, and it does not cover every secondary or contextual menu on the site.

When something in this file is load-bearing for the draft, meaning a claim the reader will act on, verify it by fetching the live page rather than trusting the row.

**This file will go stale.** If you regenerate it from a fresher export, replace `content-inventory.csv` in place and update the "exported" date in this file and in the CSV's own header comment area (or just note the new date here, since CSV doesn't support comments cleanly). If a while has passed and no fresher export is available, say so plainly when relying on it rather than presenting a two-year-old inventory as current.
