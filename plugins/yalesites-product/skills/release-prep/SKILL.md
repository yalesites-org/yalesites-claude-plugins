---
name: yalesites-release-prep
description: "End-to-end release prep workflow for YaleSites. Covers: drafting GitHub release notes, writing supplementary documentation for the featured new feature, drafting the release email communication, updating the Current Issues & Fixes page on yalesites.yale.edu, adding Release Testing Steps to GitHub issues for QA, grouping release-candidate test sites and sending the testing kickoff, and syncing the YaleSites knowledge base with any platform changes introduced in the release. Use when it's time to plan or prepare for a release."
---

# YaleSites Release Prep Skill

## Overview

This skill runs the full release planning workflow. Each phase produces a distinct deliverable. Run them in order, or jump to a specific phase if the others are already done.

| Phase | Deliverable |
|-------|------------|
| 1. Release Notes | GitHub comment (paste into release PR) |
| 2. Feature Documentation | New or updated page draft for yalesites.yale.edu |
| 3. Email Communication | Concise release announcement email |
| 4. Current Issues & Fixes | Updated version of the yalesites.yale.edu issues page |
| 5. QA Testing Steps | Release Testing Steps added to GitHub issues, RC site groups, testing kickoff message |
| 6. Knowledge Base Sync | Updated yalesites skill reference files reflecting platform changes |

---

## Before Starting

Confirm the following (if not already established):

1. **Which open PRs are included in this release?** (and which are excluded)
2. **What is the featured new feature?** — this drives the documentation phase
3. **Is the feature doc new or an addition to an existing page?** — ask if not obvious from the PR
4. **Is the Current Issues & Fixes page update needed this cycle?** — not always required
5. **Do you have the current content of the Current Issues & Fixes page?** — paste it in, since yalesites.yale.edu is blocked from direct fetch

---

## Phase 1: Release Notes (GitHub Comment)

### Finding what's in the release

1. Pull **closed PRs** from `yalesites-org/yalesites-project` sorted by `updated desc`
2. Find the most recent PR titled `Release v*` or `Release Update:*` — that's the last shipped release
3. Everything **merged after that date** is in the next release
4. Pull **open PRs** and cross-reference with the confirmed inclusion list

**Watch for hotfixes that skip the normal Release PR pattern.** Not every release ships through a `Release v*` PR — hotfixes can go straight to `master` as their own standalone PR (e.g. "Hotfix 1: 2.23.0"). These are real, versioned releases that won't turn up if you only search for the `Release v*`/`Release Update:*` naming pattern. When auditing "what's shipped since the last tracked release," also check for PRs merged directly to `master` in the relevant date range, not just PRs matching the release-title pattern.

**Don't trust a bundling/staging-branch PR's description as the complete manifest.** When a batch of fixes lands via an intermediate staging branch (e.g. "Bring in PRs held for after the X release"), other PRs can keep merging into that same staging branch *after* the bundling PR's description was written, and ride along in the eventual merge without ever being added to the list. Filtering strictly by base branch will structurally miss these. Cross-check the bundling PR's actual commit list, or the live GitHub Project board, rather than relying on its written body as ground truth.

**Filter rules:**
- Include only PRs where `merged_at` is set (not just `closed_at`)
- Exclude: "DEMO ONLY / DO NOT MERGE" titles, `chore(deps):` dependency bumps, internal-only tasks (migrations, CI fixes, etc.) that aren't user-facing
- Mark open PRs as in-flight until confirmed merged

### Categorizing changes

| Section | What goes here |
|---------|---------------|
| **Featured Feature** | The headline collaboration item — gets its own named section |
| **New Features & Enhancements** | New capabilities, design options, content type improvements |
| **Bug Fixes** | Fixes to existing behavior; navigation fixes belong here too |
| **PRs Included** | Bulleted list with linked PR numbers — no table (tables don't render reliably in GitHub comments) |

Internal tasks (migrations, CI work, dependency updates) are omitted from user-facing notes unless they have direct user impact.

### Format

```
## YaleSites v[X.X] in Collaboration with [Partner]
  — OR —
## YaleSites v[X.X]: [Descriptive Theme]

[Intro paragraph — collaboration callout + overview of the release]

---

### 📚 [Featured Feature Name]
[2–3 sentences. Lead with user benefit. Credit the collaboration.]

---

### ✨ New Features & Enhancements
- **Feature name** — Plain-English description of what changed and why it matters.

---

### 🐛 Bug Fixes
- **Fix name** — Plain English: what broke, what's fixed.

---

### PRs Included
- [#XXXX](https://github.com/yalesites-org/yalesites-project/pull/XXXX) — One-line summary
```

### Publishing to the website
This format, PRs Included section and all, is for the GitHub comment audience. If the same content gets reused as the public Release Notes page on yalesites.yale.edu, drop the **PRs Included** section before publishing — that list isn't something the site's audience sees; it belongs to the GitHub PR thread only.

### Voice & tone
- Write for non-technical users first: site owners, content editors, department admins
- Lead with user benefit, not technical implementation
- Warm and collegial — this is a community announcement, not a changelog
- Bug fix descriptions should name the symptom ("a site's custom branding name could revert to..."), not the cause

### Version numbering
Announcement title uses short form: v2.22.0 in code → "v2.22" in title. URL slug drops dots: v2.22 → `v222`.

---

## Phase 2: Feature Documentation

### Determine the doc type
**Is this a brand new documentation page, or an addition to an existing one?**

- **New page** — Draft a full standalone page following the YaleSites documentation style
- **Addition** — Paste in the current page content; draft the new section to insert

**Name the actual page, not "the documentation."** YaleSites documentation on yalesites.yale.edu is plain page content — there's no help center, no article IDs, no doc-tree structure to point at generically. A documentation acceptance criterion that says "update the documentation" gives whoever picks it up nothing to work from, and they'll spend the first twenty minutes finding the page you already found.

Before writing a docs acceptance criterion, fetch the live site and confirm where the content actually belongs, then write the criterion as a specific URL plus the section within it — e.g. "Add to yalesites.yale.edu/building-with-blocks, Media Content Blocks section" or "Update yalesites.yale.edu/in-line-message-block." If the feature genuinely has no existing page, say that explicitly and flag it as a new-page decision rather than guessing at a URL that doesn't exist. Guessed URLs are worse than an honest "no page yet."

While you're in there, note any stale or duplicate pages you pass through, but keep them out of the release ticket — they're their own cleanup item.

### Linking a draft page for review

Documentation drafts usually go up on yalesites.yale.edu as an unpublished revision before anyone reviews them, and the link you hand a reviewer has to point at that revision rather than the published page.

**Use the node path, not the path alias.** The reviewable URL is `https://yalesites.yale.edu/node/[nid]/latest`. Appending `/latest` to a path alias (`/in-line-message-block/latest`) doesn't resolve — Drupal's Latest Version tab only lives under the canonical node route, so the alias form gives a 404 and the reviewer assumes the draft doesn't exist.

To find the node ID without admin access, fetch the published page and read `currentPath` out of the `drupalSettings` JSON in the page source. That gives you `node/[nid]` directly.

Two things worth telling the reviewer in the same message:

- They need to be logged in. `/latest` is behind CAS, so a logged-out visitor sees nothing.
- If you fetch a draft URL yourself and get an empty body, that's the expected signature of an unpublished page behind CAS, not a broken link. It confirms the draft exists and isn't live yet.

### Structure for a new documentation page

```
# [Feature Name]

## Overview
[1–2 sentences: what this feature does and who it's for]

## How to use it
[Step-by-step instructions written for a content editor, not a developer]

## [Optional: Use cases / examples]
[When would you use this? What does it enable?]

## [Optional: Notes / Limitations]
[Anything the user should know that isn't obvious]
```

### Voice & tone for docs
- Write for a content editor who has never seen this feature
- Use plain English; avoid Drupal jargon where possible (e.g., "block" is fine, "config entity" is not)
- Steps should be numbered and scannable
- Reference Yale's web writing best practices: short sentences, active voice, front-load the key information

### Output
Save as `feature-doc-[feature-name]-draft.md` in the workspace folder.

---

## Phase 3: Email Communication

The release email is a brief, friendly announcement sent to the YaleSites community. It highlights 2–3 of the most impactful new features — not a comprehensive list, and no bug fixes section. Bug fixes are acknowledged in passing in the closing line, which directs readers to the full release notes.

### Format

```
To: The YaleSites Community

[Opening line — one of two forms:]
  Collaboration release: "We're excited to share the latest YaleSites release, which we developed in collaboration with [Partner] and their vendor partner, [Vendor]."
  General release: "We're excited to share the latest YaleSites release, focused on [brief theme]."

What's new

* [Feature name] - [One to two sentences describing what it does and why it matters. Plain English, no jargon.]
* [Feature name] - [Same format. 2–3 bullets total — only the most impactful features.]

We encourage you to visit our Release Notes page for a full list of updates, including [brief mention of other categories, e.g. "enhancements to content creation and numerous bug fixes"].

Thank you for using YaleSites, and please continue to share your feedback on features you'd like to see next.

Best,
The YaleSites Team
```

### Key rules
- **2–3 feature bullets only** — be selective; this is not a comprehensive list
- **No bug fixes section** — mention them only in the closing paragraph as "numerous bug fixes"
- Feature format is `* Feature name - description` with a plain hyphen, not an em dash
- Feature names are not bolded in the bullet — just plain text followed by a hyphen
- The opening line establishes collaboration context (or theme) once — don't repeat it
- No subject line is needed in the draft; that's handled separately
- Closing paragraph always references the Release Notes page on yalesites.yale.edu

### Who approves and who sends

The email isn't sent by whoever drafts it. Chris Suquilanda (Information Services Consultant) approves the copy, and ITS Communications sends it to the YaleSites community list. Build that into the ticket's acceptance criteria so the handoff is explicit rather than assumed.

**Publish the Release Notes page before the email goes out.** The closing paragraph links to it, so sending first means the link 404s for everyone who opens the email early. Sequence it as: release notes drafted → page published on yalesites.yale.edu → email approved → email sent.

When a single ticket covers all three deliverables (release notes draft, Release Notes webpage, release email), split the acceptance criteria by deliverable rather than running them together. Each one has a different owner and a different "done."

### Don't ship in-progress framing to the community

Release notes and the release email describe what shipped. Drop "(in progress)" qualifiers, migration status labels, and reassurance filler like "no action needed from site owners" before publishing. If work genuinely isn't done, either describe the user-visible part plainly or leave it out of this release's notes entirely.

### Output
Save as `release-email-v[version]-draft.md` in the workspace folder.

---

## Phase 4: Current Issues & Fixes Page Update

The Current Issues & Fixes page (https://yalesites.yale.edu/continuous-improvement/current-issues-fixes) is a living document that lists known bugs and recently deployed fixes.

**Important:** yalesites.yale.edu is blocked from direct fetch in this environment. Paste the current page content in before drafting the update.

### What changes in each release
1. **Remove** any bugs from the "known issues" list that were fixed in this release
2. **Add** the new bug fixes from this release to the "recent fixes" section
3. **Add** any newly discovered bugs that aren't yet fixed (confirm with the team)
4. **Archive or remove** older fixes that are no longer relevant to call out

### Format guidance
- Keep the "known issues" list honest and specific — vague entries erode trust
- Bug fix descriptions should match the plain-English phrasing used in the release notes for consistency
- Date each fix entry with the release version and approximate date
- Keep the page skimmable — short bullets, no paragraphs
- For a standalone hotfix summary (e.g. a quick post-release note of what got pushed), phrase each fix as "Fixed X where XYZ happened," and only include fixes that were actually user-facing and reported/noticed — leave out fixes for problems the release itself caused that no one flagged (no need to surface a bug nobody knew existed)

### Copy-paste into the Drupal WYSIWYG
When the output needs to be pasted directly into a Drupal WYSIWYG block form (CKEditor), don't hand over a markdown table — CKEditor treats pipe syntax as plain text, so the whole table lands in a single cell. Build a real HTML file instead (an actual `<table>` and `<ul>` list), open it in a browser, and copy from there — the browser copies the real HTML structure, so cells and bullets paste in correctly.

### Output
Save as `current-issues-fixes-v[version]-draft.md` in the workspace folder. This draft gets pasted into the CMS.

---

## Phase 5: QA Testing — Release Testing Steps (Runs in Parallel with Phases 2–4)

This phase prepares GitHub issues for QA testing by adding a **Release Testing Steps** section to any issue that lacks clear, actionable testing instructions. Testers use the issues in `yalesites-org/YaleSites-Internal` as their checklist — this phase makes sure every issue is ready for them.

Only issues with a GitHub Project status of **"Ready for Release (in dev)"** should be updated.

**Important — the status isn't in the REST API.** GitHub Project status fields (including "Ready for Release (in dev)") live on the Project board and are only reachable via GraphQL, so the GitHub MCP tools (`get_issue`, `search_issues`, `list_issues`) can't see or filter on them.

The **PR list from Phase 1 remains the source of truth.** Issues linked from those PRs should correspond to the ones marked "Ready for Release (in dev)". If there's any doubt, confirm before updating an issue.

Where `gh` is available, you can read the board directly as a cross-check rather than relying on the PR list alone:

```bash
gh project item-list 6 --owner yalesites-org --format json --limit 500
```

Filter client-side for items whose Status is "Ready for Release (in dev)". Treat a mismatch between that list and the Phase 1 PR list as a signal to ask, not as license to update issues the PR list didn't cover — nothing currently sets this status automatically, so the board can lag reality. See the `ticket` skill's `references/board-status.md` for the full field reference.

This phase can start as soon as the PR list from Phase 1 is confirmed, and runs in parallel with the communication phases.

### Step 1: Extract linked issues from PRs

Each PR in the release links to one or more issues in `yalesites-org/YaleSites-Internal`. Extract these from the PR body — they typically appear as GitHub issue URLs or `#XXXX` references near the top of the description.

Use `mcp__github__get_issue` on `yalesites-org/YaleSites-Internal` to fetch each issue.

### Step 2: Assess whether testing steps are needed

Read the issue description and acceptance criteria. Ask:

- Are there clear, step-by-step instructions a tester could follow right now?
- Do the steps reference a specific environment or URL the tester can actually access?
- Are the expected outcomes clearly stated?

If yes to all three — no action needed, move on.

If any are missing or vague — draft a **Release Testing Steps** section.

### Step 3: Draft the Release Testing Steps section

Write step-by-step testing instructions grounded in:
- The PR description's "Description of work" and "Functional testing steps"
- The issue's acceptance criteria
- What the feature or fix is supposed to do from a user perspective

**Format:**

```
## Release Testing Steps

1. [Concrete action — where to go, what to click, what to do]
2. [What to verify or observe]
3. [Edge case or secondary scenario if relevant]

**Expected result:** [What a passing test looks like in plain English]
```

**Guidelines:**
- Write for a tester, not a developer — use the admin UI path, not code references
- Be specific: "Go to Site Settings → Appearance → Font Style" beats "check the font setting"
- Each step should be a single action or observation
- Include the expected result at the end so the tester knows what "passing" looks like
- If the feature has multiple scenarios (e.g., a fix that should work for both inline and reusable blocks), cover each one
- For bug fixes, include a step that confirms the broken behavior no longer occurs
- Some tickets have no direct UI reproduction path at all (CI fixes, dev tooling). Don't invent steps for these — say plainly that verification happens in dev and point at what to check.

### Step 4: Update the issue

Use `mcp__github__update_issue` on `yalesites-org/YaleSites-Internal` to append the new section to the existing issue body. Preserve all existing content — only add the new section at the bottom.

Do not overwrite acceptance criteria or existing descriptions. The Release Testing Steps section is additive.

### Step 5: Report back

After processing all issues, report a summary:
- How many issues were updated with new testing steps
- How many already had sufficient steps (no action needed)
- Any issues where the PR description lacked enough detail to write confident testing steps (flag these for review)

Two things worth surfacing separately from the counts, because they're board-hygiene problems rather than testing-steps problems:

- An issue marked ready for release whose acceptance criteria are still largely unchecked — especially where only the research/discovery items are ticked and the implementation items aren't. That usually means it landed on the board ahead of the work, and a tester needs to confirm with the developer what actually shipped before testing it.
- An issue that's unassigned or still carrying a `forming`-style label. Both signal it wasn't fully groomed, and it's worth confirming it belongs in the release at all.

### Step 6: Group the RC test sites and send the testing kickoff

Once the issues are ready, testers need somewhere to test and a note telling them to start.

**Grouping the RC sites.** The release candidate spins up a multidev per participating site, following the pattern `https://v{VERSION}-{site-slug}.pantheonsite.io` (e.g. `v2260-ys-mcdb-yale-edu` for v2.26.0). Split those links into two groups:

- **Site-owner outreach** — sites that have a named contact. Pair each RC link with its contact so the outreach can go out per site rather than as a broadcast.
- **Internal team** — platform/sandbox sites, plus any site whose contact list says they're no longer participating. These go to the testing team as a single block of links.

Matching RC slugs back to a contact list is fuzzier than it looks: slugs flatten dots to hyphens and sometimes carry extra segments (`research-computing` vs `research.computing`, `-yalecollege-` inserted mid-slug). Match on the underlying domain, and report any site that appears in one list but not the other rather than silently dropping it.

**The kickoff message.** This goes to the testing team, usually in Teams. Keep it short and lead with the version. It should cover:

- The version number, confirmed against the release PR rather than inferred from the RC slug
- That the testing board is updated and every issue has testing steps, with a link to the board view
- That they can start now or wait for the kickoff meeting, either is fine
- Important dates: testing start, pending release date, communications date
- The internal-team testing links
- Anything that makes this release unusual — a longer testing window, a migration bundled in, an unusually large scope. Testers plan their time around this, so say it plainly.

---

## Phase 6: Knowledge Base Sync (Runs After Phase 1)

This phase keeps the YaleSites skill's reference files accurate. Every release may introduce new blocks, change field labels, add content type fields, modify settings options, or alter user roles — any of these can silently invalidate what's in the skill's references. This phase audits each PR and patches the affected reference files directly.

This phase can begin as soon as the PR list from Phase 1 is confirmed.

### Step 1: Audit the release for platform changes

For each PR in the release, read the PR description and any linked diffs to identify changes that affect the documented platform behavior. Look for:

| Change type | Where it affects |
|-------------|-----------------|
| New block added | `blocks-reference.md` |
| Block removed or deprecated | `blocks-reference.md` |
| Block field label changed | `blocks-reference.md` |
| New field option added to a block | `blocks-reference.md` |
| New paragraph type (accordion item, card, tile, etc.) | `paragraphs-reference.md` |
| Paragraph field label or option changed | `paragraphs-reference.md` |
| New content type field (Page, Post, Event, Resource, Person) | `content-types-reference.md` |
| Content type field label or behavior changed | `content-types-reference.md` |
| New Views filter, display, or module | `views-reference.md` |
| New sitewide setting or changed setting options | `settings-reference.md` |
| User role added, removed, or permission changed | `user-roles-reference.md` |

**What does NOT require a knowledge base update:**
- Bug fixes that restore behavior already documented correctly
- Internal/dev tooling changes with no user-facing effect
- Dependency bumps with no behavior change
- Styling tweaks that don't change field labels or options

### Step 2: Read the affected reference files

For each reference file that needs updating, read its current contents from the yalesites skill's `references/` directory (available in the skill's context). Understand the existing structure before making changes — new entries should follow the same format as existing ones.

### Step 3: Draft the updates

For each change identified:

**New block:** Add a full entry following the existing block format — name, description, and a field table with Drupal field labels and notes. Mark it `✅` if fully documented or `⚠️` if field details are uncertain. Group it under the correct region (Banner Area, Main Content, etc.).

**Changed field label:** Update the field table row in-place. Note the old label in parentheses if the rename is recent enough that editors may still see the old term in staging environments.

**New field or option:** Add a new row to the relevant field table, or add the new option to the Notes column of the existing row.

**Removed block or field:** Remove the entry or row. If it may still appear on older sites, add a deprecation note instead of deleting.

**New paragraph type:** Add an entry under the correct parent block in `paragraphs-reference.md`, following the existing format.

**Settings or roles change:** Update the relevant section in `settings-reference.md` or `user-roles-reference.md` following existing formatting conventions.

### Step 4: Apply the updates

Edit the reference files directly. Preserve all existing content — only add, modify, or remove the specific entries identified in Step 3. Do not reformat unrelated sections.

### Step 5: Report back

After processing all PRs, report a summary:
- Which reference files were updated and what changed in each
- Any PRs where the description lacked enough detail to confidently update the references (flag for review — may need to inspect the actual Drupal config YAML or check a staging environment)
- Any changes that were skipped because they had no user-facing documentation impact

---

## File Naming Conventions

| Deliverable | Filename |
|-------------|----------|
| Release notes | `release-notes-v[version]-draft.md` |
| Feature documentation | `feature-doc-[feature-name]-draft.md` |
| Email | `release-email-v[version]-draft.md` |
| Current Issues & Fixes | `current-issues-fixes-v[version]-draft.md` |

All draft files saved to the workspace folder.

---

## Notes

- Run Phases 1 → 2 → 3 → 4 in order; Phases 5 and 6 run in parallel starting after Phase 1
- If a release has no major new feature (e.g., a hotfix release), skip Phase 2
- The Current Issues & Fixes update (Phase 4) is not always needed every release — confirm before starting
- For collaboration releases, the partner name should appear in the release notes title, intro, and featured feature section — but doesn't need to be repeated in the email subject or docs page
- Tables don't render reliably in GitHub comments — always use bulleted lists for the PR reference section
- Issues live in `yalesites-org/YaleSites-Internal`; PRs live in `yalesites-org/yalesites-project` — don't mix them up when making API calls
- Phase 6 edits the skill's own reference files — this keeps the knowledge base self-maintaining across releases
