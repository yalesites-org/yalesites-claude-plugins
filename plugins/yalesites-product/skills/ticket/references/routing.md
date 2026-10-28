# YaleSites routing rules

**Canonical reference for who owns what, and how work waits on a person.** The `ticket` skill reads it when it scopes a feature epic. The `router` skill reads it on every run. If a skill's inline copy disagrees with this file, this file wins.

When an owner changes, edit the table here. Nothing else needs to change.

Background: yalesites-org/YaleSites-Internal#1915 (the AI-native process plan). v0 of the router runs as a scheduled Claude routine instead of the GitHub Action in that plan. It can move to an Action once these rules settle.

---

## Features are epics, one child per phase

A feature almost never fits in one ticket. It needs some mix of UX, design, development, QA, visual regression, and docs, often from different people. So a `Feature` is scoped as an epic up front, with one child ticket per phase that applies. Small enhancements that one developer can build from one AC list stay single tickets. The `ticket` skill decides which with the user.

### Phases and default owners

| Phase | Key | Default owner | Blocked by | Done when |
|---|---|---|---|---|
| UX | `ux` | `atiddei` (April) | nothing | Flows or research findings are attached and the owner sets Done |
| Design | `design` | `miketullo95` (Michael) | `ux` | Designs are attached and the owner sets Done |
| Development | `dev` | `dblanken-yale` (Dave). `vinmassaro` for CI, deploy, and upgrade work | `design` (or `ux` if no design phase) | PRs merge. Merge automation or `/merge-prs` sets Done |
| QA | `qa` | `miketullo95` (functional review on the multidev) | `dev` | The owner signs off on the ticket and sets Done |
| Visual regression | `visreg` | `dblanken-yale` | `dev` | Visreg baselines are updated or the diff is approved |
| Docs | `docs` | `miketullo95` (drafts). Chris and Rachel for comms | `dev` | The docs draft is staged. Publishing waits for the release |

Rules:

- **Create only the phases that apply.** Most features skip one or more.
- **Blocked by skips missing phases.** If there is no Design child, Development is blocked by UX. If there is no UX or Design child, Development starts first.
- **QA, Visreg, and Docs run in parallel** once Development is done.
- **Product calls are not a phase.** They come up inside any phase and go through `needs-decision` (below). The decider is `miketullo95` unless the block names someone else.
- **Defaults, not rules.** Reassign any child when the work calls for it. The router only assigns the default owner when a child it promotes has no assignee.
- April (UX) and Michael (QA) are first guesses as of 2026-10-27. Confirm or change them here.

### How a phase child is marked

Each phase child carries the phase in its title and in its machine block:

- **Title:** `<Feature short name>: <Phase>`, e.g. `Card Collection Filters: UX`. The epic is `Epic: Card Collection Filters`.
- **Machine block:** the closing `<!-- yalesites:agent -->` block includes `phase: ux` (the Key column) and `epic: yalesites-org/YaleSites-Internal#NNNN`.

The router finds phase children through the `phase:` line, not the title, so a renamed ticket still routes.

### Wiring

- Each child is a native **sub-issue** of the epic.
- Order is set with native **"blocked by"** dependencies, per the table above. Not a checklist.
- The first phase starts in `To Do`, assigned to its owner. Every later phase starts in `Backlog`, assigned to its owner. The router moves each one to `To Do` when all its blockers are Done or closed.

A phase is "done" for routing when its ticket is **closed** or its board Status is **`Done`**. Design, UX, and Docs have no PR to merge, so their owners set Done by hand when they finish.

---

## Waiting on a person: `needs-decision` and `follow-up`

Two labels, on issues and PRs, in every YaleSites repo. Each one comes with a block in the body (or in a comment) that names who owes what.

| Label | Means | Example |
|---|---|---|
| `needs-decision` | Someone must make a choice before work can go on | Which filter layout ships first |
| `follow-up` | Someone owes an action: a reply, a test, a review, a check-in with a requester | Confirm the card layout on mobile |

`needs-decision` replaces `question`. Leave `question` on old items for now. The router reads it as a decision with no block.

### The blocks

Put the block in the issue body when you file it, or in a comment when you raise it later. Keep it on two lines so it reads well and is easy to parse.

```markdown
## Decision needed
**Question:** ...   **Options:** (a) ... (b) ...   **Recommendation:** ...
**Decides:** @miketullo95   **Needed by:** 2026-11-03   **Raised by:** Dave's agent, on yalesites-org/yalesites-project#1517
```

```markdown
## Follow-up needed
**Who:** @atiddei   **What:** confirm the card layout works on mobile
**By:** 2026-11-03   **Raised by:** router, from yalesites-org/YaleSites-Internal#1234
```

- **Who / Decides:** one GitHub handle. The router groups by this. If it is missing, the router falls back to the assignee and lists the item under "No owner named."
- **By / Needed by:** an ISO date. If it is missing, the router uses 5 working days from when the label went on.
- **One open block per label per item.** A second ask on the same item is a second comment with its own block.

### Closing one out

- **Decision:** reply with `## Decision: (b), decided by Michael on 2026-11-03. Reason: ...` and remove `needs-decision`.
- **Follow-up:** reply with what was done and remove `follow-up`.

The label is the switch. The router treats a block with no label as closed.

---

## What the router may change

The router runs unattended, so its writes are a short, fixed list. Anything not on it goes in the brief as a suggestion for a person.

| Write | When |
|---|---|
| Set Status `Backlog` → `To Do` on a phase child | Every blocker is Done or closed, the epic is open, and the child has no open `needs-decision` |
| Assign the phase's default owner | Only on a child it just promoted, and only if that child has no assignee |
| Comment on the epic | One comment per promotion, naming the child and its owner |
| Comment on the brief issue | Once per run |

The router never closes, relabels, or reassigns anything else, never touches a PR, never starts an agent, and never @-mentions anyone in the brief (it writes handles in backticks so nobody gets a notification storm). Nudges happen in person or in the Monday meeting.

## Brief

The router posts its brief as a comment on the pinned **Router brief** issue in YaleSites-Internal, every weekday morning. The issue number lives in the `router` skill.
