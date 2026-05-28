---
name: yalesites-release-prep
description: "End-to-end release prep workflow for YaleSites. Covers: drafting GitHub release notes, writing supplementary documentation for the featured new feature, drafting the release email communication, updating the Current Issues & Fixes page on yalesites.yale.edu, adding Release Testing Steps to GitHub issues for QA, and syncing the YaleSites knowledge base with any platform changes introduced in the release. Use when it's time to plan or prepare for a release."
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
| 5. QA Testing Steps | Release Testing Steps added to GitHub issues |
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

### Output
Save as `current-issues-fixes-v[version]-draft.md` in the workspace folder. This draft gets pasted into the CMS.

---

## Phase 5: QA Testing — Release Testing Steps (Runs in Parallel with Phases 2–4)

This phase prepares GitHub issues for QA testing by adding a **Release Testing Steps** section to any issue that lacks clear, actionable testing instructions. Testers use the issues in `yalesites-org/YaleSites-Internal` as their checklist — this phase makes sure every issue is ready for them.

Only issues with a GitHub Project status of **"Ready for Release (in dev)"** should be updated.

**Important — REST API limitation:** GitHub Project status fields (including "Ready for Release (in dev)") are stored in the Project board and are only queryable via GraphQL, not the REST API used by the GitHub MCP tool. This means the status cannot be filtered directly. The practical workaround: use the confirmed PR list from Phase 1 as the source of truth. Issues linked from those PRs should correspond exactly to the ones with "Ready for Release (in dev)" status. If there's any doubt, confirm before updating an issue.

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

### Step 4: Update the issue

Use `mcp__github__update_issue` on `yalesites-org/YaleSites-Internal` to append the new section to the existing issue body. Preserve all existing content — only add the new section at the bottom.

Do not overwrite acceptance criteria or existing descriptions. The Release Testing Steps section is additive.

### Step 5: Report back

After processing all issues, report a summary:
- How many issues were updated with new testing steps
- How many already had sufficient steps (no action needed)
- Any issues where the PR description lacked enough detail to write confident testing steps (flag these for review)

---

## Phase 6: Knowledge Base Sync (Runs After Phase 1)

This phase keeps the YaleSites skill's reference files accurate. Every release may introduce new blocks, change field labels, add content type fields, modify settings options, or alter user roles — any of these can silently invalidate what's in the skill's references. This phase audits each PR and patches the affected reference files directly.

This phase can begin as soon as the PR list from Phase 1 is confirmed.

### Step 1: Audit the release for platform changes

For each PR in the release, read the PR description and any linked diffs to identify changes that affect the documented platform behavior. Look for:

| Change type | Where it affects |
|-------------|------------------|
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
