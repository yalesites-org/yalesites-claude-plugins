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
- Bug fix descriptions should name the symptom, not the cause

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
- Use plain English; avoid Drupal jargon where possible
- Steps should be numbered and scannable

### Output
Save as `feature-doc-[feature-name]-draft.md` in the workspace folder.

---

## Phase 3: Email Communication

The release email highlights 2–3 of the most impactful new features — not a comprehensive list, and no bug fixes section.

### Format

```
To: The YaleSites Community

[Opening line — one of two forms:]
  Collaboration release: "We're excited to share the latest YaleSites release, which we developed in collaboration with [Partner] and their vendor partner, [Vendor]."
  General release: "We're excited to share the latest YaleSites release, focused on [brief theme]."

What's new

* [Feature name] - [One to two sentences. Plain English, no jargon.]
* [Feature name] - [Same format. 2–3 bullets total.]

We encourage you to visit our Release Notes page for a full list of updates, including [brief mention of other categories].

Thank you for using YaleSites, and please continue to share your feedback on features you'd like to see next.

Best,
The YaleSites Team
```

### Key rules
- **2–3 feature bullets only**
- **No bug fixes section** — mention them only in the closing paragraph
- Feature format is `* Feature name - description` with a plain hyphen, not an em dash
- No subject line needed in the draft

### Output
Save as `release-email-v[version]-draft.md` in the workspace folder.

---

## Phase 4: Current Issues & Fixes Page Update

The Current Issues & Fixes page (https://yalesites.yale.edu/continuous-improvement/current-issues-fixes) is a living document listing known bugs and recently deployed fixes.

**Important:** yalesites.yale.edu is blocked from direct fetch. Paste the current page content in before drafting the update.

### What changes in each release
1. **Remove** bugs from the "known issues" list that were fixed in this release
2. **Add** new bug fixes to the "recent fixes" section
3. **Add** newly discovered bugs (confirm with the team)
4. **Archive or remove** older fixes no longer relevant

### Output
Save as `current-issues-fixes-v[version]-draft.md` in the workspace folder.

---

## Phase 5: QA Testing — Release Testing Steps (Runs in Parallel with Phases 2–4)

Adds a **Release Testing Steps** section to any issue in `yalesites-org/YaleSites-Internal` that lacks clear, actionable testing instructions.

Only issues linked from PRs in the confirmed release list should be updated.

**REST API limitation:** GitHub Project status fields are only queryable via GraphQL. Use the confirmed PR list from Phase 1 as the source of truth for which issues to update.

### Steps
1. Extract linked issues from PR bodies (`#XXXX` references or GitHub issue URLs)
2. Fetch each issue via `mcp__github__get_issue` on `yalesites-org/YaleSites-Internal`
3. Assess whether clear testing steps already exist (specific actions, accessible environment, stated expected outcome)
4. If missing, draft a **Release Testing Steps** section:

```
## Release Testing Steps

1. [Concrete action — where to go, what to click, what to do]
2. [What to verify or observe]
3. [Edge case or secondary scenario if relevant]

**Expected result:** [What a passing test looks like in plain English]
```

5. Append via `mcp__github__update_issue` — never overwrite existing content
6. Report: how many updated, how many already sufficient, any flagged for review

---

## Phase 6: Knowledge Base Sync (Runs After Phase 1)

Audits every PR in the release for user-facing platform changes and patches the affected yalesites skill reference files directly.

### Change-to-file mapping

| Change type | Reference file |
|-------------|----------------|
| New block added | `blocks-reference.md` |
| Block removed or deprecated | `blocks-reference.md` |
| Block field label changed | `blocks-reference.md` |
| New field option added to a block | `blocks-reference.md` |
| New paragraph type | `paragraphs-reference.md` |
| Paragraph field label or option changed | `paragraphs-reference.md` |
| New content type field | `content-types-reference.md` |
| Content type field label or behavior changed | `content-types-reference.md` |
| New Views filter, display, or module | `views-reference.md` |
| New sitewide setting or changed options | `settings-reference.md` |
| User role added, removed, or permission changed | `user-roles-reference.md` |

**Skip:** bug fixes restoring already-correct behavior, internal tooling, dependency bumps, styling tweaks with no field label changes.

### Process
1. Read each PR description for user-facing changes
2. Read the affected reference file(s) to understand current structure
3. Draft updates matching existing format (new block entries, updated field rows, added options, deprecation notes)
4. Edit reference files directly — additive only, preserve all existing content
5. Report: which files changed, what changed, any PRs flagged for manual review

---

## File Naming Conventions

| Deliverable | Filename |
|-------------|----------|
| Release notes | `release-notes-v[version]-draft.md` |
| Feature documentation | `feature-doc-[feature-name]-draft.md` |
| Email | `release-email-v[version]-draft.md` |
| Current Issues & Fixes | `current-issues-fixes-v[version]-draft.md` |

---

## Notes

- Run Phases 1 → 2 → 3 → 4 in order; Phases 5 and 6 run in parallel starting after Phase 1
- If a release has no major new feature (e.g., a hotfix), skip Phase 2
- Phase 4 is not always needed every release — confirm before starting
- Tables don't render reliably in GitHub comments — always use bulleted lists for PR references
- Issues live in `yalesites-org/YaleSites-Internal`; PRs live in `yalesites-org/yalesites-project`
