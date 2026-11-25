# Grooming existing tickets

Load this when a groomer fills out an existing stub, grooms a `forming` intake ticket, reviews a ticket for completeness, prepares tickets for a sprint or grooming session, or sweeps the backlog for work that is ready to pick up. It also holds the full ticket Quality Bar, which every groomed or newly written ticket should pass. Write fields per `references/fields.md` and the body per `references/issue-format.md`.

---

## Grooming a `forming` ticket

When a groomer grooms a `forming` ticket, run the full flow on it. Keep the request, source, and filer sections as they are. A feature becomes a feature parent: retitle it `Feature: <name>` and add its phases (see `references/feature.md`). Remove `forming` as the last step, once every field is written and read back.

## Grooming existing stub tickets

When grooming an existing ticket that's missing fields or has a thin description:

1. Read the existing issue body. Preserve anything already written.
2. Identify what's missing (description too vague, no acceptance criteria, no priority or risk, etc.), including whether the title is vague, generic, or doesn't match what the description actually says.
3. Search the relevant repos for context if the work is technical.
4. Fill in the missing fields following `references/issue-format.md`, rewriting the title if it doesn't clearly state the work (see "Title" there).
5. If the ticket has no TL;DR line, add one at the top. If it carries a block of platform-fit or archetype analysis inline above the Description, move it into a collapsed **Background and analysis** block. This is a reformat, not a rewrite; preserve the words.
6. Use `mcp__github__update_issue` (or `gh issue edit --body-file`) on `yalesites-org/YaleSites-Internal`. **Append or replace only the missing sections**; never overwrite content the team has already written.

If the ticket preserves an unresolved debate, keep it as an open acceptance-criteria item and raise a `needs-decision` (see `references/decisions.md`).

## Checking for drift, not just gaps

Grooming isn't only about filling in missing fields. A ticket can have a complete Description and Acceptance Criteria and still be wrong, because the work moved past what's written and nobody wrote the change back. This shows up most on epics and other long-running tickets, where scope gets resolved in PR reviews or side conversations that never make it into the ticket body itself.

This applies to an established ticket with real history (comments, linked PRs, sub-issues), not the blank-stub case the gap-filling steps above cover. Before treating that kind of ticket as groomed, check it for drift:

- **If the `ticket-sync` skill is installed** (it ships in the `yalesites-review` plugin), load it and run its check.
- **If it isn't,** do the short version yourself. Read the comments, linked PRs, and sub-issues. Compare them with the Description and Acceptance Criteria. Also look for text that treats a closed ticket as still open ("until the fix in another ticket lands").

Either way, decide whether anything needs a comment (context only) or an edit (scope or acceptance criteria actually changed). Never post either without the user's confirmation. Run this in addition to the gap-filling steps above, not instead of them.

## Backlog sweeps: before calling a ticket available

These matter when recommending tickets for pickup (by a person or an unmoderated agent), or when cleaning up the backlog:

- **Check more than the absence of an assignment label.** Confirm there's no assignee set and no `forming` label or `In progress` status on it. A ticket can look open on one signal and still be actively claimed.
- **Check for merged PRs, not just open ones.** A `claude`-tagged or open-looking ticket can already be done: the PR merged but the issue was never closed (the team's PR body format isn't a GitHub-recognized closing keyword, so merges don't auto-close issues). A sweep that only checks for *open* PRs will hand out already-finished work. Cross-reference against merged PR activity in the relevant repo(s) before calling a batch of tickets "ready."
- **Don't close a ticket as stale or duplicate without first checking for a live, unmerged PR against it.** Closing out from under active work is an easy mistake during a backlog sweep.
- **Board Status can't be read over REST.** Use `gh` (see `references/board-status.md`), or the PR-label proxy in `references/fields.md` when `gh` isn't available.

---

## Quality Bar

Before submitting or updating an issue, check:

- [ ] Title clearly states the specific work, and uses a matching prefix if one applies
- [ ] If Priority is Hotfix, the title carries the `Hotfix:` prefix in front of its type prefix
- [ ] Body opens with a TL;DR line: one or two plain-language sentences, no jargon
- [ ] Platform-fit and archetype analysis is in a collapsed **Background and analysis** block, not inline above the Description (an "already exists" or "conflicts" flag excepted: that stays visible under the TL;DR)
- [ ] Description is jargon-free and makes sense to a non-developer
- [ ] Acceptance criteria covers dev, UX, accessibility, and docs angles
- [ ] For user-facing work, affected archetypes are named and any new-user cost is stated (Step 1b of `references/platform-fit.md`), or the check is explicitly noted as not applicable
- [ ] For a ticket that names a specific block, section layout, or sitewide setting, the one-line adoption figure with its crawl vintage is in the Background and analysis block (Step 1c of `references/platform-fit.md`), or the `yalesites-portfolio` skill was unavailable and no number was estimated
- [ ] Priority reflects actual user and platform impact (don't default to Medium)
- [ ] Risk is set. If unsure, err toward the higher level
- [ ] Type is set as the native Issue Type field on the issue, not just stated in the body (see "Setting the native Issue Type" in `references/fields.md`)
- [ ] Status, Priority, Risk, Type, milestone, and assignee were **read back** from GitHub after writing, not assumed from a clean exit
- [ ] No `status:*`, `priority:*`, or `size:*` label is on the ticket
- [ ] Relevant labels are applied
- [ ] Milestone is set to the release the work is actually going into, not whichever open milestone sorted first
- [ ] A visreg site page ticket is in the release **after** the feature's, and in `Blocked`
- [ ] Assignee is set, or the user explicitly chose to leave it unassigned
- [ ] `claude` label is on only if the user asked for it and the ticket is complete enough for an agent to work it unattended
- [ ] For an established ticket with real history, Description and Acceptance Criteria still match what's actually been decided (see "Checking for drift" above)

For epics, also run the Epic quality bar in `references/epic.md`. For a feature parent, also run the Feature parent quality check in `references/feature.md`.
