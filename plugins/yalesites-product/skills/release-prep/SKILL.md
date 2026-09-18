---
name: yalesites-release-prep
description: "End-to-end release prep workflow for YaleSites. Covers: drafting GitHub release notes, writing supplementary documentation for the featured new feature, drafting the release email communication, updating the Current Issues & Fixes page on yalesites.yale.edu, adding Release Testing Steps to GitHub issues for QA, syncing the YaleSites knowledge base with any platform changes introduced in the release, and reconciling the YaleSites Board after the release ships — verifying what actually made it into master, moving confirmed-shipped tickets from 'Ready for Release (in dev)' to 'Done', and catching tickets left stuck in In progress or In review. Use when it's time to plan or prepare for a release, and again after a release goes out to clean up the board."
---

# YaleSites Release Prep Skill

## Overview

This skill runs the full release workflow. Each phase produces a distinct deliverable. Jump to a specific phase if the others are already done.

**The numbering is not the running order.** Phases are numbered by deliverable, but they hang off two events: the **first RC cut** and the **release going out**.

| When | Phases |
|---|---|
| At the first RC cut | 1 (first draft), then 5 immediately |
| During the QA period | 2, 3, 4, 6 |
| Right before the release goes out | 1 again (refresh), then publish 2, 3, 4 |
| After the release ships | 7 |

Phase 5 in particular is **not** a late-stage phase. Testers need their steps the moment the RC is cut, so it runs right after the first pass of Phase 1. Running it in numeric order means the steps land after QA has already started.

| Phase | Deliverable |
|-------|------------|
| 1. Release Notes | GitHub comment (paste into release PR) |
| 2. Feature Documentation | New or updated page draft for yalesites.yale.edu |
| 3. Email Communication | Concise release announcement email |
| 4. Current Issues & Fixes | Updated version of the yalesites.yale.edu issues page |
| 5. QA Testing Steps | Release Testing Steps added to GitHub issues |
| 6. Knowledge Base Sync | Updated yalesites skill reference files reflecting platform changes |
| 7. Post-Release Reconciliation | Board cleaned up after the release ships — shipped tickets moved to Done, the rest carried over, milestone closed |

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

**Run this phase at least twice.** The first pass, at the RC cut, produces the draft and unblocks Phase 5. The second pass, right before the release goes out, re-runs the same search to catch everything that landed during the QA period: bug fixes found in testing, late additions, and anything pulled from the release. Treat the first draft as provisional and diff it against the second pass rather than assuming it's still complete.

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

The release notes comment is read by the whole community, and it is the least technical audience we write for. Per `../ticket/references/github-communication-format.md`: lead with a TL;DR, keep the Featured Feature visible, and collapse the longer lists (New Features & Enhancements, Bug Fixes, PRs Included) into named `<details>` blocks so the top of the comment stays short. Put the PR list as structured refs, the milestone, and the featured-feature issue in a closing `<!-- yalesites:agent -->` block as well, so a later release or sync pass can read them without parsing prose.

Write it per `../ticket/references/github-writing.md`: plain language, active voice, an 80-word TL;DR, and a 500-word budget on the visible layer. Lead each item with what changed for the reader, not with what the team did. "Galleries now accept alt text" beats "we implemented an alt-text field on the gallery paragraph." Check the draft with `python3 ../ticket/scripts/check-github-text.py notes.md --surface release-notes`.

```
## YaleSites v[X.X] in Collaboration with [Partner]
  — OR —
## YaleSites v[X.X]: [Descriptive Theme]

**TL;DR:** [One or two sentences: the release theme plus headline counts, e.g. "One featured feature (X), 6 enhancements, 11 bug fixes." Plain language.]

[Intro paragraph — collaboration callout + overview of the release]

---

### 📚 [Featured Feature Name]
[2–3 sentences. Lead with user benefit. Credit the collaboration.]

---

<details>
<summary><b>✨ New Features & Enhancements</b></summary>

- **Feature name** — Plain-English description of what changed and why it matters.

</details>

<details>
<summary><b>🐛 Bug Fixes</b></summary>

- **Fix name** — Plain English: what broke, what's fixed.

</details>

<details>
<summary><b>PRs Included</b></summary>

- [#XXXX](https://github.com/yalesites-org/yalesites-project/pull/XXXX) — One-line summary

</details>
```

Keep the bulleted list inside "PRs Included" (not a table) — the no-table rule still applies inside a `<details>` block in a comment.

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

**Read the live page directly** rather than asking for a paste; `https://yalesites.yale.edu/continuous-improvement/current-issues-fixes` fetches fine.

**Check the "Last Updated" date against the release before trusting what you read.** A fetch can return a cached copy that is months out of date. This bit us on v2.26: a fetch returned the July 16 version of the page and was reported as "8 of 9 known issues are stale" when the page had in fact already been updated that morning. If the date is older than the release you're working on, re-fetch before drawing any conclusion, and say which date you saw.

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

## Phase 5: QA Testing — Release Testing Steps (Run at the RC Cut)

This phase prepares GitHub issues for QA testing by adding a **Release Testing Steps** section to any issue that lacks clear, actionable testing instructions. Testers use the issues in `yalesites-org/YaleSites-Internal` as their checklist — this phase makes sure every issue is ready for them.

Only issues with a GitHub Project status of **"Ready for Release (in dev)"** should be updated.

**Important — the status isn't in the REST API.** GitHub Project status fields (including "Ready for Release (in dev)") live on the Project board and are only reachable via GraphQL, so the GitHub MCP tools (`get_issue`, `search_issues`, `list_issues`) can't see or filter on them.

The **PR list from Phase 1 remains the source of truth.** Issues linked from those PRs should correspond to the ones marked "Ready for Release (in dev)". If there's any doubt, confirm before updating an issue.

Where `gh` is available, you can read the board directly as a cross-check rather than relying on the PR list alone:

```bash
gh project item-list 6 --owner yalesites-org --format json --limit 500
```

Filter client-side for items whose Status is "Ready for Release (in dev)". Treat a mismatch between that list and the Phase 1 PR list as a signal to ask, not as license to update issues the PR list didn't cover — nothing currently sets this status automatically, so the board can lag reality. See the `ticket` skill's `references/board-status.md` for the full field reference.

**Timing is the whole point of this phase.** Run it as soon as the first RC is cut, immediately after the first pass of Phase 1 confirms the PR list. Testers work the RC against these issues, so steps that arrive later than the RC are steps nobody used. If you reach this phase and QA is already underway, you are late: say so, and prioritise the issues still untested rather than working through the list in order.

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

**TL;DR:** [One line — what a tester is checking here, e.g. "Confirm the font-style setting saves and applies on the front end."]

1. [Concrete action — where to go, what to click, what to do]
2. [What to verify or observe]
3. [Edge case or secondary scenario if relevant]

**Expected result:** [What a passing test looks like in plain English]
```

Keep the numbered steps and the expected result visible — they are the tester's checklist, not detail to collapse. The TL;DR is the only thing added on top.

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

## Phase 7: Post-Release Board Reconciliation (Runs After the Release Ships)

Every other phase points forward at a release. This one runs **after** the RC is out, and it answers three questions:

1. Did the work marked `Ready for Release (in dev)` actually ship?
2. Which of those can move to `Done`?
3. What got left behind in `In progress` / `In review` / `Blocked` that should have moved?

**Why this phase exists.** The `Ready for Release (in dev)` → `Done` transition was supposed to be automatic. Workflow `02-pr-status-monitor` in `YaleSites-Internal` was built for it and has never fired on real work (wrong repo for the trigger, plus an inverted dry-run default — see the `ticket` skill's `references/board-status.md`). So the board accumulates shipped work indefinitely. Expect the first run to find a backlog spanning many releases, not just the one that shipped.

**Hard rule: never move an item to `Done` on the strength of its board status alone.** The status is the thing we don't trust — that's the whole reason for the phase. Every move must be backed by a merge commit verified to be an ancestor of `master`.

### Step 1: Establish what actually shipped

Find the release PR(s) merged to `master`. **Check for hotfixes too** — they ship straight to `master` as standalone PRs and won't match the `Release v*` pattern (same trap as Phase 1).

```bash
gh pr list --repo yalesites-org/yalesites-project --base master --state merged --limit 10 \
  --json number,title,mergedAt,mergeCommit \
  --jq '.[] | "\(.number)\t\(.mergedAt)\t\(.title)"'
```

Confirm with the user which of these is *the* release being reconciled, and note its merge timestamp. Anything merged to `develop` after that timestamp is in the *next* release and must not be touched.

**Scope the run by milestone.** Milestones in `YaleSites-Internal` map to releases (`09-17-26 Feature Release` is v2.26.0), which is far more tractable than reconciling the whole `Ready for Release (in dev)` column at once. Treat the milestone as a good but not perfect source of truth — it's set by hand, so a ticket can be in the wrong one.

```bash
gh api repos/yalesites-org/YaleSites-Internal/milestones --paginate -X GET -f state=all -f per_page=100 \
  --jq '.[] | "\(.number)\t\(.title)\topen=\(.open_issues) closed=\(.closed_issues)\tdue=\(.due_on)"'

gh issue list --repo yalesites-org/YaleSites-Internal --milestone "09-17-26 Feature Release" \
  --state all --limit 300 --json number,title,state,labels,issueType > milestone.json
```

Because the milestone can be wrong in either direction, the buckets in Step 5 still decide the outcome. A ticket in the milestone whose code isn't in `master` does not move, and a ticket outside the milestone whose code *is* in `master` is still worth reporting.

**Milestone scoping has one structural blind spot: tickets with no milestone at all.** They can never appear in a milestone-scoped run, so a purely milestone-scoped Phase 7 skips them every release, forever. This is not hypothetical. After the v2.26.0 run closed its milestone cleanly at zero open, 22 open tickets were still sitting in `Ready for Release (in dev)` with no milestone, 10 of them shipped children of a single parent. Step 8 sweeps for these, and it is not optional.

Then make sure the local checkout can answer ancestry questions. The `yalesites-project` clone usually tracks `develop` only, so `master` may not exist as a remote-tracking ref:

```bash
git fetch origin master:refs/remotes/origin/master develop:refs/remotes/origin/develop
```

### Step 2: Pull the board

```bash
gh project item-list 6 --owner yalesites-org --format json --limit 1200 > board.json
jq -r '.items | length' board.json
jq -r '.items | group_by(.status)[] | "\(.[0].status // "(none)"): \(length)"' board.json
```

**Set the limit well above the real item count and check what you got.** `gh` truncates silently at `--limit`, with no warning. The board was 641 items in September 2026 and grows every release, so a stale `--limit 600` drops the overflow without telling you. Print the length and confirm it is under the limit before trusting anything downstream.

**Capture each item's node `id` while you are here.** Step 6 needs it, and re-deriving it later costs a second full board pull:

```bash
jq -r '.items[] | select(.content.repository=="yalesites-org/YaleSites-Internal")
  | "\(.content.number)\t\(.id)"' board.json > itemids.tsv
```

Print the status distribution first and show it to the user. If `Ready for Release (in dev)` is in the hundreds, say so up front and ask whether to reconcile everything or only the items tied to this release — a 200-item confirmation list is not reviewable.

Each item carries everything needed for the join, no second lookup required:

```bash
jq -r '.items[] | select(.status=="Ready for Release (in dev)")
  | "\(.content.number)\t\(.content.repository)\t\(.title)"' board.json
```

### Step 3: Build the PR index in bulk

**Budget the GraphQL calls before you start, because the reads are what break this phase, not the writes.** `gh pr list`, `gh issue list` and `gh project item-list` all go through GraphQL and are expensive in proportion to how many records they return. Three `gh pr list` pulls plus two full board pulls is enough to exhaust the hourly GraphQL quota on its own, and once it is gone every mutation in Step 6 fails too.

Two things make this worse than it sounds:

- **`gh api rate_limit` under-reports it.** When the quota is blown, `graphql` can still read `5000/5000 remaining` while every call returns `API rate limit exceeded`. Do not pace against that number, because it is not telling you the truth.
- **It clears on the hour, not in seconds.** This is not a short abuse-detection cooldown you can retry past. Check `core`'s `reset_in` for the real hour boundary, since both windows share it.

So: do every bulk read **once**, write the JSON to disk, and join from the files. Never re-pull a list you already have. If you need a single item later, query that one item rather than re-listing the board.

Do **not** search per issue. One search per item across 150+ items is slow and rate-limited. Pull merged PRs once per repo and join locally:

```bash
for repo in yalesites-project atomic component-library-twig; do
  gh pr list --repo yalesites-org/$repo --state merged --limit 400 \
    --json number,title,baseRefName,mergedAt,mergeCommit > prs-$repo.json
done
```

The team's PR titles start with the issue number, in **two conventions** — `1518: Section Color: ...` and the older `#1232 :: Bug: Site-Wide Alert ...`. Match both or you will miss roughly one in ten:

```bash
jq -r '.[] | select(.title|test("^#?[0-9]{3,4} *(:|::)")) | "\(.title|capture("^#?(?<n>[0-9]+)").n)\t\(.number)\t\(.mergeCommit.oid)\t\(.baseRefName)"' prs-yalesites-project.json
```

For board items with no title match, fall back to the issue timeline, which gives real linkage rather than full-text guessing:

```bash
gh api repos/yalesites-org/YaleSites-Internal/issues/NNNN/timeline \
  --jq '.[] | select(.event=="cross-referenced") | .source.issue
        | select(.pull_request) | "\(.number)\t\(.state)\t\(.title)"'
```

**Two search traps, both confirmed live:**

- **Never full-text search a bare issue number.** `gh search prs "1518"` returns `yalesites-project#1518` (an unrelated dependabot PR that merely shares the number), every PR in the epic that mentions 1518, and `YALB-1518` from 2022. Use `--match title` at minimum, and prefer the bulk join above.
- **Timeline cross-references include issue→issue mentions.** Filter on `select(.pull_request)` or you'll treat sibling tickets as PRs.

### Step 4: Verify each item actually shipped

Ship verification keys on the **`yalesites-project`** PR wherever one exists. A merged `atomic` or `component-library-twig` PR on its own proves nothing, because those reach production only through a version bump.

**For tickets whose only PRs are in `atomic` or `component-library-twig`, walk the release chain.** It is three hops, and each one is a pin you can read out of `master`:

```bash
# hop 1: which atomic release does master pin?
git show origin/master:web/profiles/custom/yalesites_profile/composer.json | grep atomic
# -> "yalesites-org/atomic": "1.84.0"   (tags are prefixed: v1.84.0)

# hop 2: which component-library-twig version is inside that atomic release?
# package.json only gives a caret range, so read the lock file for the resolved version
gh api "repos/yalesites-org/atomic/contents/package-lock.json?ref=v1.84.0" --jq .content \
  | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin)['packages']; print(d['node_modules/@yalesites-org/component-library-twig']['version'])"
# -> 1.85.0
```

Then a satellite PR shipped if its merge commit is contained in that release's tag:

```bash
gh api repos/yalesites-org/atomic/compare/v1.84.0...<mergeCommit> --jq '.status'
gh api repos/yalesites-org/component-library-twig/compare/v1.85.0...<mergeCommit> --jq '.status'
```

Read the status the same way in both directions: `behind` or `identical` means the merge commit is contained in that tag, so it shipped. `ahead` or `diverged` means it did not.

Note the version skew is real and not a mistake: atomic 1.84.0 carries CLT 1.85.0. Never assume the two track each other, and never compare a CLT commit against an atomic tag.

Locally, read all three exit codes. `--is-ancestor` returns `0` for shipped, `1` for genuinely not shipped, and `128` when the object isn't in the clone at all. A bare `&& echo shipped || echo not-shipped` collapses `128` into `1` and reports a shipped-but-unfetched commit as not shipped, which is the one mistake this phase exists to avoid:

```bash
git merge-base --is-ancestor <mergeCommit> origin/master
case $? in
  0) echo shipped ;;
  1) echo not-shipped ;;
  *) echo unknown-locally ;;   # 128: SHA not in this clone, fall through to the compare API
esac
```

A missing SHA is common here, because commits that only ever lived on a feature or epic branch are exactly the population this phase reconciles. On `unknown-locally`, either fetch the commit or ask the compare API — `behind` or `identical` means shipped, `ahead` or `diverged` means not:

```bash
gh api repos/yalesites-org/yalesites-project/compare/master...<mergeCommit> --jq '.status'
```

**Merging is not shipping.** A PR can be `MERGED` and still be nowhere near production, because it merged into an epic or staging branch rather than `develop`. Real example: `yalesites-project#1508` is merged, its ticket #1518 sat in `Ready for Release (in dev)`, and its merge commit is `diverged` from `master` — it went into `1616-section-color-parity` and is waiting on the epic PR. Always check `baseRefName` alongside ancestry, and treat a non-`develop`/non-`master` base as not shipped no matter what the board says.

### Step 5: Bucket the results

| Bucket | Condition | Action |
|---|---|---|
| **A — Confirmed shipped** | The ticket's ship-verifying PR is in `master` — the `yalesites-project` PR where one exists, otherwise a satellite PR confirmed through the release chain in Step 4 | Eligible to move to `Done` |
| **B — Not shipped** | Merged to an epic/staging branch, or merged to `develop` after the RC cut | Leave as-is; list them so the user knows the board was optimistic |
| **C — Stragglers** | Board says `In progress` / `In review` / `Blocked` / `To Do`, but a linked PR *is* in `master` | Propose `Done`, flagged separately — these need a closer look than bucket A |
| **D — Undetermined** | No linked PR found, or the ticket has no code (docs, research, coordination) | Ask; never guess |

**`unknown-locally` is never bucket B.** A `128` from `--is-ancestor` says the SHA isn't in your clone, not that the code didn't ship. Resolve it with the compare API in Step 4 and bucket on that answer. If it still won't resolve, it's bucket D. Bucket B means the code was found and is genuinely not in `master`.

**Parents of any kind stay out of bucket A.** A parent with shipped children is not done until every child ships. Hold those back for explicit confirmation, listing which children shipped and which didn't.

**Do not key this check on the `epic` label.** Plenty of parents don't carry it. YaleSites-Internal #1396 is typed `Task`, has no `epic` label, and has 11 sub-issues; a label-only guard waved it straight into bucket A and closed it while its children stayed open. Check for actual sub-issues instead:

```bash
gh api graphql -f query='query($n:Int!){repository(owner:"yalesites-org",name:"YaleSites-Internal"){
  issue(number:$n){subIssues(first:50){totalCount nodes{number state}}}}}' -F n=NNNN \
  --jq '.data.repository.issue.subIssues | "\(.totalCount) sub-issues, \([.nodes[]|select(.state=="OPEN")]|length) still open"'
```

Any non-zero open-child count means the parent is not bucket A, whatever its label says.

### Step 6: Report, then confirm, then write

Show the user a report before touching anything:

```
## Post-release reconciliation — v[X.X.X]

**TL;DR:** [N] confirmed shipped and ready to move to Done, [N] not actually shipped, [N] stragglers, [N] need your call.

### Confirmed shipped → move to Done ([N])
- #NNNN [title] — yalesites-project#PPPP, in master as of [date]

### On the board as released, but not shipped ([N])
- #NNNN [title] — PR merged into [branch], not in master

### Stragglers — shipped but still show [status] ([N])
- #NNNN [title] (currently [status]) — yalesites-project#PPPP is in master

### Need your call ([N])
- #NNNN [title] — [why it couldn't be determined]
```

**Wait for explicit approval.** Ask per bucket, not per item, but do not write anything before the user says so. Buckets A and C get separate approvals — C is where a wrong move is most likely, because something kept those tickets out of `Ready for Release (in dev)` in the first place.

**Do not use `gh project item-edit --url` for a bulk run.** It resolves the item by paginating the entire board on every single call, so at 600+ items it is enormously expensive and will trip the GraphQL limit within the first few writes. It is fine for one-off use in the `ticket` skill; it is the wrong tool here.

Write the field directly instead, using the node ids you captured in Step 2. One cheap mutation per item, no lookup:

```bash
PROJ=PVT_kwDOA_XQ-s4A-PeJ
FIELD=PVTSSF_lADOA_XQ-s4A-PeJzgxtHE8   # Status
DONE=98236657                          # the "Done" option

MUT='mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){updateProjectV2ItemFieldValue(
  input:{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){projectV2Item{id}}}'

gh api graphql -f query="$MUT" -f p=$PROJ -f i=<item-id> -f f=$FIELD -f o=$DONE
```

Re-read the ids rather than trusting those literals if a mutation 404s:

```bash
gh api graphql -f query='{organization(login:"yalesites-org"){projectV2(number:6){id
  field(name:"Status"){... on ProjectV2SingleSelectField{id options{id name}}}}}}'
```

**Use `-f`, not `-F`, for the option id.** `-F` type-coerces its value, so a numeric-looking option id like `98236657` is sent as an integer and the mutation fails with `Variable $o of type String! was provided invalid value`. `-f` sends it as the string the schema wants.

**Pace the writes and make the runner resumable.** Projects v2 mutations trip a secondary rate limit well before the documented quota. Space them roughly 3 seconds apart, back off for several minutes on a throttle rather than retrying tight, and record each completed issue to a log file so an interrupted run picks up exactly where it stopped instead of re-writing from the top.

**You do not need to close the issues yourself.** The board's built-in Projects v2 auto-close workflow is enabled and closes an issue within seconds of its Status being set to `Done`. Verified by controlled test: setting #190 to `Done` through the API, with no close call made, closed it on its own.

This is worth stating plainly because an earlier version of this skill said the opposite and budgeted ~110 manual `gh issue close` calls per run, which is pure waste. The dormant workflow that misled it, `06-close-issue-when-done`, is a *different* mechanism: a custom Actions workflow that has never fired. Its triggers are wrong for this board (`project_card: moved` is Projects v1 only, and a Projects v2 `Status` change fires neither it nor `issues: edited`), and it shares the inverted dry-run default described in Step 9. The built-in Projects workflow makes it redundant regardless. Tracked in YaleSites-Internal #1753.

Verify rather than assume, since this depends on a board setting someone could turn off:

```bash
gh api repos/yalesites-org/YaleSites-Internal/milestones/<n> --jq '"open=\(.open_issues)"'
```

If issues are not closing on their own, fall back to `gh issue close <number> --repo yalesites-org/YaleSites-Internal` per item and say so in the report.

**On failure, stop.** Any error (auth, scope, item not on the board) means report what was written, what wasn't, and what the error was. Don't retry in a loop, and don't fall back to labels here — a partially-applied bulk status change is worse than none, and the user needs to know exactly where it stopped.

### Step 7: Carry the rest over, then close the milestone

Closing bucket A out in Step 6 leaves every non-shipped ticket still sitting on the milestone of a release it didn't make. Left alone that milestone stops being a truthful record of what shipped, which matters because Step 1 scopes the whole phase by milestone. The phase would corrode its own input.

**Every past release milestone ends at zero open issues.** Check this before deciding you're done:

```bash
gh api repos/yalesites-org/YaleSites-Internal/milestones --paginate -X GET -f state=all -f per_page=100 \
  --jq '.[] | select(.title|test("Release")) | "\(.title)\topen=\(.open_issues)\tclosed=\(.closed_issues)\tstate=\(.state)"'
```

Split what remains by board status, because the two groups make different claims:

| Remaining status | Action | Why |
|---|---|---|
| `Ready for Release (in dev)`, `In review`, `In progress` | Move to the next release milestone | Actively in flight, so it lands in the next release |
| `To Do`, `Backlog`, `Blocked` | **Clear the milestone** | Never started. Carrying them forward asserts they're committed to the next release, which is a bigger claim than the board supports |
| No board item | Ask | Nothing to reason from |

```bash
# in flight -> next release
gh issue edit NNNN --repo yalesites-org/YaleSites-Internal --milestone "12-08-26 Feature Release"

# not started -> no milestone, back to the unpromised backlog
gh issue edit NNNN --repo yalesites-org/YaleSites-Internal --remove-milestone
```

Same rule as the status writes: **report the split, get approval per group, then write.** Do not carry tickets forward silently. A ticket quietly appearing in the next release is how a release plan grows without anyone deciding it should.

Once the milestone reads zero open, close it:

```bash
gh api -X PATCH repos/yalesites-org/YaleSites-Internal/milestones/<number> -f state=closed
```

If anything is still open, do not close it. A closed milestone holding open issues is the failure mode this step exists to prevent, and it already exists on the board (the `Drupal AI Migration` milestone is closed with 35 open issues).

### Step 8: Sweep the unmilestoned, then scope the straggler check

**First, sweep the tickets no milestone can reach.** Closing the milestone at zero open does not mean the release is reconciled, because unmilestoned work was never in scope to begin with. Run this after Step 7, every time:

```bash
gh project item-list 6 --owner yalesites-org --format json --limit 1200 > board.json
jq -r '.items[] | select(.status=="Ready for Release (in dev)")
  | select(.content.repository=="yalesites-org/YaleSites-Internal")
  | .content.number' board.json |
while read n; do
  ms=$(gh api repos/yalesites-org/YaleSites-Internal/issues/$n --jq '[.milestone.title // "NONE", .state] | @tsv')
  case "$ms" in NONE*open*) echo "$n unmilestoned+open" ;; esac
done
```

Anything it finds goes through the same Step 4 verification as everything else. Do not move it on board status alone, and do not assume it belongs to the release you just shipped. Report it as its own group, since these tickets are usually orphaned rather than merely late.

Two patterns to expect, both seen in the v2.26.0 run:

- **Sub-issues that never inherited their parent's milestone.** #1396 was in the release milestone; all 11 of its children had none. Verify the children independently, because a shipped parent does not mean every child shipped: 10 of those 11 were in `master` and the 11th was not.
- **Work tracked outside the release cadence entirely**, like vendor builds and tooling spikes. These usually want their milestone left alone. Ask rather than assigning one.

**Second, keep the straggler check release-scoped**: items whose code shipped in this release but whose board status didn't follow. That's it.

Broader backlog problems — tickets with no acceptance criteria, missing board fields, native-type vs. type-label conflicts, tickets stale for months with no PR at all — belong to a planned `backlog-hygiene` skill, which audits the whole backlog read-only. It is not released yet, so don't re-implement those checks here and don't send the user off to invoke it. If the reconciliation surfaces a pile of them, list them in the report and say they're out of this phase's scope.

### Step 9: Report back

- How many items moved to `Done` and were closed, and how many were left alone
- How many carried to the next milestone, how many had their milestone cleared, and whether the milestone was closed
- Any item where the board and the code disagreed, since a repeat offender usually means a broken process rather than a one-off
- How many unmilestoned tickets the Step 8 sweep turned up, since a growing number there means tickets are being created outside the release cadence
- Whether workflow `02-pr-status-monitor` is still dormant. It is tracked in YaleSites-Internal #1753 (the shared inverted dry-run default) and #1385 (building its replacement), so report the state rather than filing anything new. Workflow `06-close-issue-when-done` is dormant *and* redundant, since the built-in Projects auto-close already does its job; #1753 covers deleting it

### What a real run looks like

The first real run of this phase, against v2.26.0 (milestone `09-17-26 Feature Release`, 190 issues), to calibrate what to expect:

| Bucket | Count |
|---|---|
| A, confirmed shipped, eligible for `Done` | 111 |
| B, board said released, code not in `master` | 5 |
| C, shipped but open in another status | 5 |
| D, undetermined | 13 |
| Already closed and shipped, never on the board | 10 |
| In the milestone but not release-ready | 3 |

Those buckets resolved into 114 moved to `Done` (bucket A plus the 3 genuinely stale stragglers) and 38 milestone edits: 5 to a hotfix milestone, 21 carried to the next release, 12 cleared back to no milestone. The milestone then closed at 154 closed, 0 open.

Then the Step 8 sweep found **22 more** open tickets in `Ready for Release (in dev)` with no milestone, which the milestone-scoped run could never have seen. Ten were shipped children of #1396. Budget for that sweep; it is not a rounding error.

Four numbers worth carrying into the next run:

- **Bucket D is mostly noise.** 10 of its 13 were already closed and simply never on the board. Separate those out before presenting, or you hand the user a 13-item decision list where only 3 need a decision.
- **Bucket C is smaller than it looks, and half of it should not move.** Of 5 shipped-but-stuck items, 2 had open PRs still outstanding and were correctly in flight. "Shipped" at the commit level does not mean the ticket is done.
- **Bucket B clusters.** 4 of 5 were epic-branch work and 3 shared one branch. Report the branch, not five separate problems.
- **One bucket-A item was only resolvable by reading a PR's closing comment.** #1496's own PR was closed unmerged; a sibling PR fixed it and the developer said so in a comment. Neither ancestry nor title matching would have found that.

Expect the whole run to take well over an hour of wall clock, most of it waiting on GraphQL rate limits rather than doing work.

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

- Order by event, not by number: Phase 1 then Phase 5 at the RC cut; Phases 2, 3, 4 and 6 through the QA period; Phase 1 again right before the release; Phase 7 after it ships
- Phase 1 runs twice. The pre-release refresh is what catches fixes made during QA
- Phase 7 runs after the release is out, not with the rest — it needs the RC merged to `master` before it can verify anything
- If a release has no major new feature (e.g., a hotfix release), skip Phase 2
- The Current Issues & Fixes update (Phase 4) is not always needed every release — confirm before starting
- For collaboration releases, the partner name should appear in the release notes title, intro, and featured feature section — but doesn't need to be repeated in the email subject or docs page
- Tables don't render reliably in GitHub comments — always use bulleted lists for the PR reference section
- Issues live in `yalesites-org/YaleSites-Internal`; PRs live in `yalesites-org/yalesites-project` — don't mix them up when making API calls
- Phase 6 edits the skill's own reference files — this keeps the knowledge base self-maintaining across releases
- Phase 7 is the only phase that writes to the YaleSites Board, and it never writes without explicit approval — board mechanics and field options live in the `ticket` skill's `references/board-status.md`
- Broad backlog quality problems are out of Phase 7's scope and belong to the planned `backlog-hygiene` skill, which isn't released yet — Phase 7 only reconciles status against what shipped
