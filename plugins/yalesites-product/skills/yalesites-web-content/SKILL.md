---
name: yalesites-web-content
description: "Draft web content for the YaleSites website (yalesites.yale.edu) — user guide pages, resource pages, release documentation, and knowledge base updates. Use this skill whenever the task is to write, draft, revise, or update a page that will live on yalesites.yale.edu, including when the request only names a GitHub ticket like 'draft the page for #1471', names a feature to document, or says something like 'we need a user guide page for X', 'write up the new dashboard for the site', or 'add documentation for this release'. Also use it when reviewing existing YaleSites page copy for style, reading level, or link hygiene. This skill covers researching the feature from merged code before writing, the required Title / Teaser / Config considerations block, ASD-STE100 Simplified Technical English, suggesting Layout Builder blocks, and YaleSites link and reuse conventions."
---

# YaleSites Web Content

Pages on yalesites.yale.edu are read by people who manage a Yale website on top of their actual job. They come back to the docs after weeks away, having forgotten the vocabulary. Everything in this skill exists to lower the cost of that return visit.

The end goal is a page the user can actually build in Drupal, not just prose. That shapes three things this skill insists on: verifying facts against the merged code instead of the ticket summary, handing over the config decisions alongside the copy, and pointing out which Layout Builder blocks and existing site patterns fit the content, since the user assembles the page from those pieces.

## Workflow

1. Orient: find where this page sits in the site, and check whether something similar already exists
2. Research the feature from the merged code, not the ticket summary
3. Read a sibling page to match house style
4. Draft, using the required deliverable structure, and suggest blocks
5. Run `scripts/check_draft.py` and fix what it finds
6. Report deviations from the ticket's acceptance criteria, and ask rather than guess wherever something is genuinely unclear

---

## Step 1: Orient within the site

This skill cannot crawl yalesites.yale.edu, and it shouldn't need to for the common case. `references/content-inventory.csv` is a bundled snapshot of every page and post on the site (199 rows as of 2026-08-05), with a derived section, nav status, and content cluster for each one. **Check it before fetching anything.** Search it for the topic or feature you're about to write about; it's faster than a round of live fetches and it covers content that never shows up in a hub page's visible nav, like block reference pages and training webinars that are only reachable through tag filters. Read `references/content-inventory.md` for the column definitions and what the file can't tell you.

The inventory is a snapshot, not a live source. It's a starting point for "does this already exist and where," not a citable source for what a page currently says or whether a feature still works the way it did when the export was taken. If it's the only thing available and clearly old, say so rather than presenting it as current.

**Before drafting a new page, check the inventory (or, failing that, fetch the relevant hub page) for something that already exists or overlaps.** If you find something close, say so and ask whether this should be an edit to the existing page instead of a new one, rather than assuming a new page is wanted.

The top-level navigation also renders in full on every page's markup, so a single live fetch of any published page (or `references/site-map.md`, which has it captured) confirms the real section structure when you need something more current than the snapshot, or when the inventory doesn't cover it.

See `references/site-map.md` for the verified section list and hub URLs.

## Step 2: Research the feature from the code

Ticket descriptions are written before the work is done and drift from what shipped. The PR body drifts too, because reviewers request changes. **The merged code is the only source that cannot be out of date.**

Given a ticket, find the implementing PR, then read the actual files:

| What you need to know | Where to look |
|---|---|
| What sections/fields exist and their exact labels | the Twig template, the form class (`buildForm`) |
| Column headings, sort order, row limits, empty-state text | the `views.view.*.yml` config files |
| **Who can actually see or do this** | `*.routing.yml` for the permission, then `user.role.*.yml` to see which roles hold it |
| Defaults, minimums, maximums | the form class and `config/install/*.yml` |
| What a setting does when toggled off | the template's `{% if %}` guards |

The permission check is the highest-value step and the easiest to skip. A ticket saying a feature is "admin-only" is a claim to verify, not a fact. Trace it: route requirement → which roles have that permission. If a control is reachable by more roles than the ticket implies, document it for all of them.

Read `references/researching-features.md` for the YaleSites repo layout and concrete file paths.

**Never document a control that a reader cannot reach.** If something really is gated to a narrower role, leave it out of the user guide and say so in your handoff notes.

**If you're still not sure how something works after reading the code**, that's a real signal, not something to paper over with a confident-sounding sentence. Go back to the originating ticket for context on intent, check whether there's a linked design doc or comment thread, and if it's still ambiguous, ask the user rather than presenting a guess as fact. This applies just as much to tone and scope calls (how much detail this audience needs, whether a feature is significant enough for its own page) as it does to how a feature technically works.

## Step 3: Match the sibling pages

Fetch one existing page in the same section before drafting. It shows you the heading depth, how much hand-holding the house style uses, and how features get named. `mcp__workspace__web_fetch` works on published pages.

Unpublished pages return an empty body, because unpublished content on yalesites.yale.edu sits behind CAS and needs an editor login. An empty result means "not published yet," not "broken." Verify against the local draft file instead, or ask the user to paste what they see.

## Step 4: Draft

### Deliverable structure

The user builds these pages in Drupal themselves. Body copy alone leaves them rediscovering the setup each time, and a wrong parent item means the page goes live but never appears in the nav. So every draft carries its own build instructions:

```markdown
# [Page Name] (page draft)

**Ticket:** [link]
**Status:** [draft / ready for review / blocked on X]

## Title
**Page title:** ...
**Left nav label:** ...
[one line on why, if the name isn't obvious]

## Teaser
**Teaser text (N characters):**
[~150 characters, hard ceiling 160]
Feeds the hub card, the meta description, and search results.

## Config considerations
- **Content type:**
- **Parent item:**
- **Content Collections:** enable/not needed
- **URL alias:**
- **Nav order:**
- **Hub card:** where it goes, what it needs
- **Teaser image:**
- **Cross-links:**
- **Suggested blocks:** which Layout Builder blocks fit each section of the copy below

---

## Page copy
[the actual page]

---

## Notes for the editor building this page
[screenshots still needed, publish timing, anything deliberately omitted and why]
```

See `references/page-config.md` for the User Guide's real nav structure and what each config field means.

### Suggest Layout Builder blocks

Pages aren't typed as raw HTML. The user assembles them from Layout Builder blocks and, for dynamic listings, Views. Look for a skill named `yalesites` (or similar) with `references/blocks-reference.md` and `references/views-reference.md` — those files hold the verified, current field labels for every block on the platform. If that skill is available, read them and use them.

As you draft, note which block fits each section rather than leaving the user to work it out:

- A repeated FAQ-style section → **Accordion**
- A pull quote or testimonial → **Quote Callout**
- A short highlighted message with a link → **Callout** or **Inline Message**
- A grid of related links or resources → **Link Grid** or **Quick Links**
- A dynamic list (recent posts, upcoming events, related resources) → a **Views** block, configured per `views-reference.md`
- Plain body prose → **Text**

Put this in the **Suggested blocks** line of the config block, not scattered through the copy, so it reads as build guidance rather than clutter.

### Reuse what the site already does

Some patterns repeat across YaleSites pages by design: a support callout with links to Office Hours and the team's email, a "Related Resources" list at the end of a page, a video demo embed. Before writing a new version of one of these from scratch, check `references/reusable-patterns.md` for the verified real examples and reuse the pattern rather than inventing a new phrasing.

If you spot a pattern repeating across pages that isn't captured there yet, mention it. That reference file should grow as more of these get noticed.

### Writing rules

Body copy follows **ASD-STE100 Simplified Technical English**. The rules that carry the most weight:

- Procedural sentences stay at 20 words or fewer. Descriptive ones can reach 25.
- Active voice, simple present tense, one instruction per sentence.
- One topic per paragraph.
- Reach for the plain word: *use* not *utilize*, *make sure* not *ensure*, *to* not *in order to*, *about* not *approximately*, *more* not *additional*.
- Keep noun stacks to three words or fewer.
- Say what to do rather than what not to do.

STE reads a little flat to a marketer. That is the point. The reader is often anxious about breaking their site, and short literal sentences are easier to trust. `references/ste-rules.md` has the word-swap table and the fuller rule set.

**No em dashes, ever.** Use a comma, a period, a colon, parentheses, or restructure the sentence. If the user has a personal writing-voice skill installed, apply it on top of STE. Otherwise, default to "we" for the YaleSites team rather than "I," and avoid corporate filler (leverage, utilize, circle back, synergy).

### Who you are writing for

The YaleSites User Insight Report archetypes matter here. User guide pages are read most by the **Uninformed** and **Dabbler** archetypes: they manage the site as a side duty, return infrequently, and fear making mistakes. The **Intermediate + Owner + Mechanic** combination is the core active user and will skim for the specific thing they need.

Practical consequences:

- Say what a section is *for*, not just what it shows. "Use this to find work you did not finish" beats "Shows unpublished content."
- When a setting has a consequence the reader would not predict, state it. A toggle that quietly stops release announcements deserves a sentence saying so, and a recommendation.
- End internal-only or no-action sections with an explicit "no action is necessary on your site," so a nervous reader stops worrying.
- If a `ux-research` skill is available, read it before making calls about depth and tone.

### Links

**Link to other content on the site whenever you mention it.** If the copy references another feature, page, or setting, add the link rather than leaving the name bare. A reader who has to go search for "Editorial Workflow" themselves is a reader who might give up.

Internal links use site-relative paths (`/editorial-workflow`), never absolute `https://yalesites.yale.edu/...` URLs. Pasting an absolute URL for a page on the same site is effectively hotlinking your own content: it works today, but it bypasses whatever the platform would otherwise handle for you. External links and `mailto:` links stay absolute.

**Verify the path before using it.** Don't guess a slug from the page title. Look it up in `references/content-inventory.csv` first; failing that, fetch the page or find it in `site-map.md` or a hub page's nav. Confirm the real path the same way you'd verify a permission claim in code rather than assuming it.

Relative paths are better than absolute URLs but not bulletproof: if Pathauto regenerates an alias after a title change, a hardcoded path goes stale and relies on a redirect. The most durable option is Drupal's Linkit autocomplete in the WYSIWYG, which stores an entity reference and renders the current alias regardless of future renames. Note that in the config block so whoever builds the page picks from the dropdown instead of pasting your paths verbatim.

### Screenshots

Mark them inline with the alt text written, so nothing gets published without it:

```markdown
*[SCREENSHOT: the Dashboard Settings form, as seen by a site administrator]*
*Alt text: The Dashboard Settings form, with the Announcements section open.*
```

Screenshots usually come later, during release testing on a stable environment. Say so in the handoff notes rather than blocking the draft.

## Step 5: Check the draft mechanically

```bash
python3 scripts/check_draft.py <path-to-draft.md>
```

It flags em dashes, over-length sentences, absolute internal URLs, banned words, and teaser length. Eyeballing these is unreliable and the script is faster. Fix what it reports before handing over, and mention anything you deliberately left.

## Step 6: Reconcile with the ticket, and ask rather than guess

Research often contradicts an acceptance criterion. When it does, say so plainly and let the user decide, rather than silently following either the ticket or your own finding. This is a product call, not a writing call.

The same instinct applies more broadly. If you're unsure whether a page should exist as a standalone piece or a section of something bigger, whether a detail belongs in the user guide versus internal docs, or what tone a section needs, ask. A short clarifying question costs less than a draft the user has to substantially rework.

If the user agrees to deviate from a ticket, offer to update the AC. Rewrite it as a stated decision with the reasoning ("Leave X out of the user guide because it is gated to a narrower role") rather than deleting the bullet, so a reviewer reads it as intentional rather than as an oversight.

## Related skills

- `yalesites-release-prep` — its Feature Documentation phase should hand off to this skill for the actual drafting
- `yalesites-ticket-grooming` — for writing the ticket, rather than the page
- `ux-research` — the archetypes referenced above
- `yalesites` (platform reference) — `blocks-reference.md` and `views-reference.md` for suggesting Layout Builder components
