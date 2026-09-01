---
name: yalesites-pr-feedback
description: "Review a YaleSites pull request and post feedback directly on GitHub. Use whenever the user asks to review, look at, check, approve, or give feedback on a PR — even without the words 'PR feedback' explicitly, e.g. 'can you check PR 1288', 'review this PR', 'is this one ready to merge', 'approve #452', 'what do you think of this pull request'. Covers yalesites-project, component-library-twig, and atomic. Does a deep dive on the code diff, reads the linked issue, asks the user clarifying questions, turns their answers into actionable developer feedback with exact file/line locations, then posts the review comment on GitHub — approving with the right labels or requesting changes — and @-mentions the assigned developer so they're notified."
---

# YaleSites PR Feedback Skill

## Overview

This skill runs a full PR review pass: understand what changed, understand what it was supposed to do, surface open questions for the user, turn their feedback into something a developer can act on, and post it to GitHub with the correct approval state and labels.

**Repos in scope:** `yalesites-org/yalesites-project`, `yalesites-org/component-library-twig`, `yalesites-org/atomic`
**Issues live in:** `yalesites-org/YaleSites-Internal` (PRs link to them in the body, usually as a `#XXXX` reference or full URL)

Don't guess at a repo — if the user gives a bare PR number without a repo, ask which of the three it's in (or check the URL if they pasted one).

---

## Step 1: Load the PR and its linked issue

1. `mcp__github__get_pull_request` for the PR itself — title, body, assignee, base/head branches, current labels.
2. `mcp__github__get_pull_request_files` — the actual diff, file by file. This is what you'll cite locations from later.
3. Find the linked issue number in the PR body (near the top, usually `#XXXX` or a full GitHub URL) and pull it with `mcp__github__get_issue` on `YaleSites-Internal`. If nothing is linked, say so and ask the user for the issue before going further — reviewing code against no stated intent produces shallow feedback.

## Step 2: Deep-dive the diff against the issue

Read the changed files closely, not just the summary. For each file, understand *what* changed and *why* it plausibly changed that way. Then compare against the issue's acceptance criteria:

- Does the diff cover everything in the acceptance criteria? Note anything that looks unaddressed.
- Does it do anything **beyond** what the issue asked for? Not necessarily bad, but worth flagging.
- Are there edge cases the acceptance criteria implies but the code doesn't seem to handle (empty states, permissions, accessibility, mobile/responsive behavior)?
- Is there anything that looks like it could break existing behavior elsewhere (a shared component, a config default, a migration)?

**Don't assert CI/test coverage from memory — verify it.** If the diff touches an area where "we already have visual regression / a test / a CI check for that" seems like a reasonable assumption, confirm it by reading the actual workflow file (trigger conditions, path filters) rather than stating it as fact. A workflow that looks like it covers a directory can still miss it — e.g. a `paths-filter` scoped to `components/**` silently skips a sibling `web-components/**` directory, or a check that only runs on `ready_for_review` never fires on a draft PR. Wrong coverage claims undermine QA planning more than no claim at all.

Keep a running list of concrete file/line references as you go — you'll need these twice: once to ask the user sharper questions, and once in the final feedback.

Remember [[feedback_pm_scope]] (if this memory exists for the person running the skill): the PM makes product/UX/scope calls, not implementation calls. Don't surface things like "should this use a service class or a static method" — surface things like "the issue says this should be visible to all editors, but the diff gates it behind `platform_admin` — intentional?"

## Step 3: Ask the user your own questions, then ask for their feedback

This is always a two-part step, even on a bare "review this PR" with no other input from the user.

**Part 1 — your clarifying questions.** Use the `AskUserQuestion` tool to surface genuine ambiguities from Step 2 — not a rubber-stamp checklist. Good candidates:

- A place where the code's behavior and the issue's acceptance criteria seem to diverge
- A UX/product judgment call embedded in the implementation (copy text, default values, what's shown to which role)
- Something the PR does that wasn't asked for, where it's unclear if that's welcome scope creep or worth cutting

If the diff and issue line up cleanly with nothing ambiguous, it's fine to skip this part and tell the user so — don't invent questions for the sake of asking.

**Part 2 — their feedback.** Regardless of whether Part 1 produced any questions, always explicitly ask the user if they have their own feedback or notes on the PR (things they noticed testing it, UX opinions, concerns not obvious from the diff alone). They may have looked at the multidev environment themselves and have observations the code alone won't surface. Don't skip this just because your own analysis turned up nothing — their input is a first-class input to the review, not a fallback for when you're stuck.

**Where to look on the multidev:** PR multidevs are seeded from the `dev-yalesites-platform.pantheonsite.io` database, which now runs the **visreg** (visual regression) content set. That means most multidevs already have dedicated test content for blocks and content types, so testing rarely requires building content from scratch or guessing at URLs.

The base pattern is `https://pr-{PR_NUMBER}-yalesites-platform.pantheonsite.io/`. When testing steps mention a block or content type, go straight to its page below (swap in the PR number) instead of navigating the menu to find it:

**Blocks** — `/blocks-for-visreg/{slug}`

| Block | slug |
|---|---|
| Accordion | `accordion` |
| Action Banner | `action-banner` |
| Button Link | `button` |
| Calendar List | `calendar-list` |
| Callout | `callout` |
| Custom Cards | `custom-cards` |
| Directory | `directory` |
| Divider | `divider` |
| Embed | `embed` |
| Events Calendar | `events-calendar` |
| Facts and Figures | `facts-and-figures` |
| Gallery | `gallery` |
| Grand Hero | `grand-hero` |
| Image Banner | `image-banner` |
| Image | `image` |
| In-Line Message | `in-line-message` |
| Link Grid | `link-grid` |
| Media Grid | `media-grid` |
| Post feed | `post-feed` |
| Pre-Built Form | `pre-built-form` |
| Quick Links | `quick-links` |
| Quote Callout | `quote-callout` |
| Quote | `quote` |
| Reference Card | `reference-card` |
| Spotlight - Landscape | `spotlight-landscape` |
| Spotlight - Portrait | `spotlight-portrait` |
| Tabs | `tabs` |
| Text | `text` |
| Tiles | `tiles` |
| Video Banner | `video-banner` |
| Video | `video` |
| View | `view` |
| Wrapped Image | `wrapped-image` |
| Wrapped Text Callout | `wrapped-text-callout` |

**Content types** — `/content-types/{slug}`

| Content type | slug |
|---|---|
| Events | `events` |
| Posts | `posts` |
| Profile | `profile` |
| Resource | `resource` |

Example: PR #1374 testing steps that mention the Accordion block → `https://pr-1374-yalesites-platform.pantheonsite.io/blocks-for-visreg/accordion`.

This list reflects the menu structure as of 2026-07-20 — if a lookup 404s, the block/content type may be new or renamed; fall back to browsing `/blocks-for-visreg` or `/content-types` on that PR's multidev directly and note the discrepancy to the user.

## Step 4: Turn the user's answers into actionable feedback

Once the user responds, your job is translation: turn their (possibly short, possibly informal) input into feedback a developer can act on without a follow-up round trip. For every point:

- **Name the file and line(s)** from the diff pulled in Step 1 (`path/to/file.php:42` style, or the closest anchor if exact lines shifted).
- **Say what to change**, not just what's wrong. "This should check the user's role before rendering" beats "this seems off."
- **Say why**, tying back to the issue or a concrete risk (a11y, broken state, security, mismatched spec) — one line is enough.
- **Separate blocking from optional.** If the user's feedback includes both must-fix items and nice-to-haves, label them so the developer doesn't have to guess what's gating merge.

Keep the tone direct and collegial, matching [[feedback_ticket_tone]] (if this memory exists for the person running the skill) — no "PM-approved," no "do not push back," no ownership stamps. State the feedback and let it speak for itself.

**New scope found mid-review doesn't automatically become a new ticket.** If reviewing the diff surfaces functionality worth adding beyond what the linked issue asked for, don't default to grooming it into a separate backlog ticket — ask the user first. They may want it folded into the existing ticket instead (edited in after the PR merges) with the new functionality just drafted as a PR comment for the developer to see now.

**Voice:** if a personal writing-voice skill exists for whoever is running this, check for it and apply it — the comment is going out under that person's name. If none exists, default to a plain, direct, dev-facing tone: specific, unadorned, no forced friendliness.

**Exception — stay singular ("I"), not "we."** This overrides any writing-voice skill's default person, even if that skill normally speaks as "we" (e.g. `michael-voice`). PR feedback is one reviewer's read on the code, not an org-wide statement, so write it in first person singular: "I think this should check the role first," not "we think." Apply this to every comment this skill posts — clarifying questions, the review body, and any follow-up ticket offers from Step 5.

## Step 5: Flag follow-up work — visreg coverage and documentation

Two independent checks, both non-blocking. Neither should affect the approve/request-changes call in Step 6 — these are optional follow-up tickets to offer the user, not gating conditions for this PR.

**A. New or changed blocks not yet represented in visreg**

While deep-diving the diff in Step 2, note whether the PR:

- Introduces a brand-new block (new Twig component, new SDC, new block plugin), or
- Adds a new feature, variant, field, or display option to an *existing* block

Check the block against the reference table in Step 3. If it's a new block that isn't listed there, or an existing block gaining a variant the table's page won't show, the visreg dev instance has a coverage gap: the block/feature exists in code but isn't represented in the shared test content, so the *next* PR that touches this area won't have a reference page for it either.

When you spot this, tell the user directly (a heads-up, not an `AskUserQuestion` — it's not a blocking ambiguity) and ask if they want a follow-up ticket opened to add representative content for the new block/feature to the dev visreg instance. Be explicit that it's non-blocking — this PR can be reviewed and merged on its own merits regardless of the answer.

If they say yes, draft the ticket using the ticket-grooming skill's conventions: a plain descriptive title (no special prefix needed unless one clearly fits), assignee defaulting to whoever is running this skill, and acceptance criteria naming the specific block/feature and which page it belongs on under `/blocks-for-visreg` (or `/content-types`).

**B. Documentation follow-up**

Check the linked issue's acceptance criteria (pulled in Step 1) for a documentation item — YaleSites tickets commonly include one (see the ticket-grooming skill's "Documentation" acceptance-criteria line: note if any existing docs need updating or new docs need to be created). If the issue calls for a doc update, or the diff clearly changes user-facing or editor-facing behavior with no accompanying doc change in the PR, ask the user if they want a follow-up documentation ticket spun off — don't create it unprompted.

If they say yes:

- **Assignee:** default to whoever is running this skill (the PM), not the PR's developer.
- **Title prefix:** `Docs:`, per the ticket-grooming skill's conventions.
- **Where it lives:** ask or note which of these applies, since YaleSites documentation has a few homes:
  - **External** (end-user/editor-facing): yalesites.yale.edu
  - **Internal**: Teams, or GitHub (either the org-wide internal knowledge repo or a repo-specific README/docs folder)

This is a follow-up ticket, not scope on this PR — it doesn't affect the approve/request-changes decision in Step 6 either.

## Step 5b: Check whether the linked ticket needs to catch up

This is exactly the moment tickets go stale — Step 2 may have surfaced a place where the diff and the issue's acceptance criteria diverge, and Step 3 resolved it in conversation with the user. If nothing writes that resolution back to the ticket, the next person who reads it sees the original ask, not what was actually decided.

Load the `ticket-sync` skill and hand it the linked issue from Step 1, the divergences found in Step 2, and how they were resolved in Step 3. It decides whether the resolution is worth a comment (context only) or an edit (scope/acceptance criteria actually changed), and — if the issue is a child ticket under an epic — whether the parent epic's `Scope` or `Child Tickets` section needs a matching update.

Non-blocking, like Step 5 above: it doesn't change the approve/request-changes call, it just makes sure the ticket reflects it. Skip straight to Step 6 if `ticket-sync` finds nothing to flag.

## Step 6: Decide approve vs. request changes

Ask the user directly if it isn't obvious from their feedback: is this ready to approve, or does it need another pass?

**If approving:**
- `mcp__github__create_pull_request_review` with `event: "APPROVE"` and the feedback (if any — approvals can be feedback-free) as `body`.
- Update labels (see Step 8).

**If requesting changes:**
- `mcp__github__create_pull_request_review` with `event: "REQUEST_CHANGES"` and the actionable feedback from Step 4 as `body`.
- Update labels (see Step 8).

## Step 7: @-mention the assigned developer

Pull the assignee's GitHub login from `get_pull_request` (`assignee.login`, or `assignees[]` if more than one) and include `@login` in the comment body so they get notified. If there's no assignee set, mention this to the user rather than silently skipping the notification — an unassigned PR about to get review feedback is itself worth flagging.

## Step 8: Update labels

`mcp__github__update_issue` takes a full replacement array for `labels` — **fetch the PR's current labels first** (from Step 1) and compute the new full list, don't just push the labels you're adding or you'll wipe out everything else on the PR (type labels, epic links, etc.).

Rather than a simple remove-one/add-one swap, **reconcile the whole set of review-state labels** every time. A PR can arrive in an inconsistent state (e.g. still carrying `pass functional review` / `ready to merge` from an earlier pass that a fresh deep-dive now contradicts), so start by stripping *all* of these regardless of which are present, then add back only the ones that match the new outcome:

Review-state labels to strip before reapplying: `needs review`, `needs work`, `pass code review`, `pass functional review`, `pass design review`, `ready to merge`, `ready to close`. Leave every other label (type, epic, milestone-linked, etc.) untouched.

**The "pass ___ review" label depends on the repo:**

| Repo | Approval review label |
|---|---|
| `yalesites-project` | `pass functional review` |
| `atomic` | `pass functional review` |
| `component-library-twig` | `pass design review` |

| Outcome | Add back |
|---|---|
| Requesting changes | `needs work` |
| Approving (normal PR) | the repo's review label (above) + `ready to merge` |
| Approving (demo/multidev-only PR) | the repo's review label (above) + `ready to close` |

This matters in practice — a PR can look "ready to merge" on the label alone while a deep-dive turns up something the earlier pass missed. Reconciling the full set avoids leaving contradictory labels (e.g. `needs work` sitting next to `ready to merge`), and picking the wrong review label (functional vs. design) is an easy mistake to make once this skill covers all three repos.

**Detecting a demo-only PR:** check the PR title (case-insensitive) for any of `MULTIDEV ONLY`, `DEMO ONLY`, `DO NOT MERGE`. These PRs aren't meant to ship — they're just for showing work on a multidev environment — so they get closed out instead of queued to merge.

Apply the label update via `mcp__github__update_issue` with `owner`, `repo`, `issue_number` (the PR number — PRs share the issue numbering), and the recomputed `labels` array.

## Step 9: Post it — and handle the permission gap

Post the review from Step 6 and the label update from Step 8.

**Known issue:** the GitHub connector's token has previously been unable to write (comment/review/label) on `yalesites-project` and other org repos, even though it can read fine — confirmed 403 "Permission Denied: Resource not accessible by personal access token." If `create_pull_request_review` or `update_issue` fails with a permission error, don't retry blindly. Instead:

1. Tell the user plainly that the write failed due to a token permission gap, and show them the drafted review body + label plan so nothing is lost.
2. Walk them through creating a token with write access:
   - Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
   - Scope it to the relevant repo(s) (`yalesites-project`, `component-library-twig`, `atomic` as needed).
   - Under **Repository permissions**, grant **Pull requests: Read and write** and **Issues: Read and write** (labels are an Issues permission even on a PR).
   - Copy the generated token.
   - In the app, go to the GitHub connector's settings and reconnect/update it with the new token (exact path may vary — look under Settings → Connectors → GitHub).
3. Once reconnected, retry posting the same review and label update — don't make the user redo the analysis.

## Step 10: Confirm back to the user

After posting, report: a link to the review/comment, the final approval state, the labels applied (and removed), and who was @-mentioned. Keep it short — the user was following along and doesn't need the whole analysis repeated.

---

## Notes

- Multiple repos in scope means the same PR number can exist in more than one repo — always confirm which repo before acting if there's any doubt.
- `update_issue`'s `labels` param replaces the entire label set — always start from the PR's current labels, not an empty list.
- This skill performs real, user-visible GitHub actions (a review, a notification, label changes). When in doubt about approve vs. request-changes, or about scope-creep questions, ask rather than assume.
- The team's PR body format (e.g. `## [#1157 :: Title](url)`) is not a GitHub-recognized closing keyword (`Fixes #`, `Closes #`, etc.), so merged PRs do not auto-close their linked issue. Don't assume an issue is closed just because its PR merged — check or close it explicitly.
