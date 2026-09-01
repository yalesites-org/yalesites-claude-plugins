---
name: ticket-sync
description: "Check whether a GitHub issue still matches how the work actually turned out, and either edit it or comment on it to catch it up. Use standalone when someone asks 'does this ticket need updating,' 'is the ticket still accurate,' 'sync the ticket to the PR,' or 'does the epic need to reflect this.' Also invoked mid-flow by the pr-feedback, ticket, and yalesites-pr skills at the moments where drift is easiest to catch — after a PR review surfaces a scope question, while grooming a ticket that already has history, and before moving an issue to In review. Distinguishes context worth a comment from an actual scope/acceptance-criteria change worth an edit, and never posts either without confirmation. Most useful on epics and other long-running tickets, where scope gets resolved in conversation and never written back to the issue."
---

# YaleSites Ticket Sync Skill

## Overview

A ticket is accurate when it was written. Work then continues — a PR review resolves an open question, a spike ticket rules out an approach, a child ticket ships something slightly different than the epic assumed — and unless someone deliberately writes that resolution back into the issue, the ticket stays frozen at day one while everyone's understanding has moved on. Six weeks later, whoever reads the ticket sees the original ask, not what actually got approved.

This skill exists to catch that gap at the moments it's cheapest to catch it: right when a scope decision gets made, not months later during a confused re-read. It answers one question — **does the ticket still match reality, and if not, does that call for a comment or an edit?**

**This is a targeted check, not a full re-grooming pass.** It looks only at whether the **Description**, **Acceptance Criteria**, and (for epics) **Scope** and **Child Tickets** sections still hold up. It doesn't touch Priority, Size, Type, or labels — that's the `ticket` skill's job.

---

## When this runs

**Invoked mid-flow, with context already in hand.** `pr-feedback`, `ticket`, and `yalesites-pr` each load this skill at a natural checkpoint and hand it three things: the issue number, what actually happened (a diff, a decision, a PR body), and — where relevant — what the user already said about it. Don't re-ask the user something the calling skill already established; use what it hands you.

**Invoked directly.** Someone can ask about a specific ticket at any point — "does #1288 still reflect what we're building," "the scope changed on the auth epic, does the ticket need updating." When run standalone, ask what changed if it isn't already obvious from context (recent comments, a linked PR, conversation history).

**Either way, this is a fast check, not a ceremony.** If the ticket still matches, say so in one line and move on — don't manufacture a finding to justify having run. A skill that flags something every single time trains people to stop reading the flags.

---

## Step 1: Identify the ticket(s) in scope

Start with the ticket directly under discussion. Then check: **is it a child ticket under an epic?** Look for a "Part of #XXXX" reference, or check whether it's checklisted in a parent issue's `Child Tickets` section. If so, the parent epic is in scope too — epic staleness is exactly where this matters most, because the epic's `Scope` and `Child Tickets` sections are written once at kickoff and rarely revisited as child tickets actually complete.

Pull the current body of every ticket in scope with `mcp__github__get_issue` (or `gh issue view {NNN} --repo yalesites-org/YaleSites-Internal --json title,body`).

## Step 2: Gather what actually happened

The source of "what changed" depends on how this was invoked:

| Calling context | What actually happened, drawn from |
|---|---|
| `pr-feedback` | The diff-vs-acceptance-criteria divergences already found in its Step 2, plus whatever the user resolved in Step 3's back-and-forth |
| `ticket` (grooming) | Comment history on the ticket, the state of any linked/merged PRs, and — for epics — which child tickets have closed and what they actually shipped |
| `yalesites-pr` | The PR body(ies) just drafted, compared against the issue fetched in its Step 2 |
| Standalone | Ask directly: "what changed since this was written?" |

Don't re-derive this from scratch if the caller already did the work — that's the entire reason this runs mid-flow instead of as a cold re-read.

## Step 3: Compare against Description, Acceptance Criteria, and Scope

Read the ticket's `Description` and `Acceptance Criteria` (and, for an epic, `Scope` and `Child Tickets`) against what Step 2 turned up. Look specifically for:

- An acceptance criterion that no longer matches what was built, approved, or ruled out
- A description that implies a different shape of work than what's actually happening
- For epics: a child ticket that shipped something the `Scope` section didn't anticipate, or a `Child Tickets` checklist missing a ticket that got added (or still listing one that got cut)
- A title that no longer describes the work (flag it, but titles are the `ticket` skill's territory — don't rewrite it here)

## Step 4: Classify — comment, or edit

This is the judgment call the whole skill exists for. Use this test: **if someone closed this ticket today using the Acceptance Criteria exactly as written, would that misrepresent what actually happened?**

| | Comment | Edit |
|---|---|---|
| **Test** | Adds color on *how* or *why*, without changing what "done" means | Changes what "done" means, or what was actually decided to be in/out of scope |
| **Examples** | A decision rationale, a link to the PR that resolved an ambiguity, a note that an edge case was tested and works, status color for someone reading the thread later | An acceptance criterion added, removed, or reworded; scope narrowed or expanded; an approach ruled out that the description still implies; an epic's `Scope` or `Child Tickets` section out of sync with what child tickets actually cover |
| **Epic-specific** | A child ticket shipped exactly what the epic scoped, just later than planned | A child ticket shipped something the epic's `Scope` never anticipated, or got cut/split without the parent's `Child Tickets` list reflecting it |

When genuinely unsure which side a divergence falls on, treat it as an edit candidate and let the user downgrade it — a comment that should've been an edit is the failure mode this skill is meant to prevent.

**Don't resolve an open debate unilaterally while doing this.** If the "what changed" turns out to be an unresolved disagreement rather than a settled decision, that's not sync material yet — surface it to the user as still open, matching how the `ticket` skill handles unresolved threads during grooming.

## Step 5: Confirm before writing anything

Never post a comment or an edit without showing the user what it'll say first.

- **For an edit:** show the specific before/after of the section(s) you're proposing to change — not a full rewrite of the ticket. Get explicit confirmation.
- **For a comment:** show the drafted comment text. Given how low-stakes context comments usually are, a quick "I'll add this as a comment on #XXXX, sound right?" is enough — but still confirm; don't post silently.

If a ticket in scope needs both (an edit to the direct ticket, and a separate comment or edit on the parent epic), confirm each one — don't bundle them into one approval.

## Step 6: Write it

**Edits:** update only the affected section(s) of the body — `mcp__github__update_issue` (fetch the current body first, replace just the relevant section, preserve everything else) or `gh issue edit {NNN} --repo yalesites-org/YaleSites-Internal --body-file -` with the full reconstructed body. Same discipline as the `ticket` skill's grooming step: never overwrite content the team wrote that isn't part of what's actually changed.

**Comments:** `mcp__github__add_issue_comment`, or `gh issue comment {NNN} --repo yalesites-org/YaleSites-Internal --body "..."`.

**Parent epic updates** are a separate write from the child ticket's — don't fold an epic's `Scope`/`Child Tickets` correction into the same edit call as the child ticket's own update.

## When there's nothing to flag

Say so in one line — "the ticket still matches what's happening, nothing to update" — and let the calling skill continue. This is the common case; treat it that way.

---

## Notes

- Comments and edits can't be walked back once posted — there's no tool to revise a GitHub comment in place. If the draft is wrong, fix it before Step 6, not after.
- Cross-repo references need the full `owner/repo#number` form — a bare `#1299` in a comment always resolves against the current repo, not whatever repo the surrounding text names.
- This skill writes to `yalesites-org/YaleSites-Internal`. If the GitHub connector's token can't write there (a known intermittent gap — see the `ticket` and `pr-feedback` skills' notes on this), show the user the drafted edit/comment so nothing is lost rather than retrying blind.
