# YaleSites routing rules

**Canonical reference for who owns what, and how work waits on a person.** The `ticket` skill reads it when it scopes a feature. The `router` skill reads it on every run. If a skill's inline copy disagrees with this file, this file wins.

When an owner changes, edit the table here. Nothing else needs to change.

Background: yalesites-org/YaleSites-Internal#1915 (the AI-native process plan). v0 of the router runs as a scheduled Claude routine instead of the GitHub Action in that plan. It can move to an Action once these rules settle.

---

## Features: a parent issue, one child per phase

A feature almost never fits in one ticket. It needs some mix of UX, design, development, QA, visual regression, and docs, often from different people. So a feature gets a parent issue up front (Issue Type `Feature`, title `Feature: <name>`, no `epic` label), with one child ticket per phase that applies. Epics stay for initiatives that hold several features. A feature parent can sit under an epic. Small enhancements that one developer can build from one AC list stay single tickets. The `ticket` skill decides which with the user.

### Phases and default owners

| Phase | Key | Default owner | Blocked by | Gate | Done when |
|---|---|---|---|---|---|
| UX | `ux` | `atiddei` (April) | nothing | auto | Flows or research findings are attached and the owner sets Done |
| Design | `design` | `miketullo95` (Michael) | `ux` | auto | Designs are attached and the owner sets Done |
| Development | `dev` | `dblanken-yale` (Dave). `vinmassaro` for CI, deploy, and upgrade work | `design` (or `ux` if no design phase) | `miketullo95`: design is approved | PRs merge. Merge automation or `/merge-prs` sets Done |
| QA | `qa` | `miketullo95` (functional review on the multidev) | `dev` | auto | The owner signs off on the ticket and sets Done |
| Visual regression | `visreg` | `dblanken-yale` | `dev` | auto | Visreg baselines are updated or the diff is approved |
| Docs | `docs` | `miketullo95` (drafts). Chris and Rachel for comms | `dev` | `miketullo95`: feature is accepted | The docs draft is staged. Publishing waits for the release |

Rules:

- **Create only the phases that apply.** Most features skip one or more.
- **Blocked by skips missing phases.** If there is no Design child, Development is blocked by UX. If there is no UX or Design child, Development starts first.
- **QA, Visreg, and Docs run in parallel** once Development is done.
- **Product calls are not a phase.** They come up inside any phase and go through `needs-decision` (below). The decider is `miketullo95` unless the block names someone else.
- **Gates.** A phase with a handle in the Gate column needs that person's go before it starts. When its blockers finish, the router does not move it. It lists it under "Waiting on a go" instead. `auto` means the router moves it on its own. Gates are set per phase here, so adding or removing one is a one-cell edit.
- **Defaults, not rules.** Reassign any child when the work calls for it. The router only assigns the default owner when a child it promotes has no assignee.
- April (UX) and Michael (QA) are first guesses as of 2026-10-27. Confirm or change them here.
- **April's capacity varies week to week.** The `ticket` skill asks before assigning a UX phase to her and falls back to Michael. The router only assigns default owners to children it promotes, and UX is always a first phase, so it never assigns April on its own.

### How a phase child is marked

Each phase child carries the phase in its title and in its machine block:

- **Title:** `<Feature name>: <Phase>`, e.g. `Office Hours: Docs`. The parent is `Feature: Office Hours block`. A phase may have more than one child.
- **Machine block:** the closing `<!-- yalesites:agent -->` block includes `phase: ux` (the Key column) and `parent: yalesites-org/YaleSites-Internal#NNNN`.

The router finds phase children through the `phase:` line, not the title, so a renamed ticket still routes.

### Wiring

- Each child is a direct native **sub-issue** of the feature parent.
- Order is set with native **"blocked by"** dependencies, per the table above. Not a checklist.
- The first phase starts in `To Do`, assigned to its owner. Every later phase starts in `Backlog`, assigned to its owner. The router moves each one to `To Do` when all its blockers are Done or closed.

A phase is "done" for routing when its ticket is **closed** or its board Status is **`Done`**. Design, UX, and Docs have no PR to merge, so their owners set Done by hand when they finish.

---

## Intake: who grooms, and what everyone else files

Grooming a ticket means making product calls: priority, scope, phases, milestone, who builds it. Those calls belong to the groomers below. Everyone else files what they know and hands it off.

| Groomer | Handle | Grooms |
|---|---|---|
| Michael | `miketullo95` | Everything |
| Dave | `dblanken-yale` | Dev-only work (Issue Type `Task` or `Bug` with no user-facing change) |

When someone who is not a groomer runs the `ticket` skill:

| They're filing | They get | Labels and fields |
|---|---|---|
| A feature request or enhancement (new or changed functionality) | An **intake stub**: what was asked, who asked, where it came from, why it matters | Title `Feature Request: ...`, Issue Type `Feature`, `forming`, Status `Backlog`. No Priority, Risk, milestone, assignee, or `claude` |
| A bug, or comms, docs, or training work | A full ticket, as today | Everything except Priority, which a groomer sets |

**`forming` is the intake label.** It means "filed, not yet groomed." Every open `forming` ticket shows in the router brief's Intake section and in the dashboard's Intake queue. Grooming removes it.

Tickets with no Priority filed in the last 30 days by someone who isn't a groomer also show under Intake as "Needs a priority."

---

## Priority and the agent pickup order

Milestone and Priority answer different questions. Don't make one stand in for the other.

- **Milestone = when.** The release a ticket ships in. No milestone means we haven't committed to it yet.
- **Priority = what goes first.** The order inside a milestone, and which unscheduled tickets we pull in first when we plan the next release. `High`, `Medium`, and `Low` are about importance, not timing.
- **`Hotfix` is the one exception.** It jumps ahead of every milestone and ships on its own.

Priority is also how every agent orders its work, whoever runs it. Nobody hands an agent its next ticket. Each agent picks from its pool in this order:

1. **Rework.** Its own PRs that came back with `needs work`.
2. **`Hotfix`**, whatever the milestone.
3. **The current milestone** (the open one with the soonest due date), `High` then `Medium` then `Low`.
4. **The next milestone**, in the same order, only once the current one has nothing left it can take. During an RC window, next-release work doesn't merge to `develop`.
5. **Never a ticket with no milestone.** A person schedules it first.

Ties go to lower Risk (a board field since 2026-10-28). When Risk isn't set, the older ticket wins.

**The team cap.** Every open yalesites-project PR uses one of Pantheon's 25 multidevs, and the whole team shares them. When 25 or more yalesites-project PRs are open, agents stop taking new work and only do rework and `Hotfix` tickets. A person can wave through something that's clearly urgent. It's a soft cap on purpose: it doesn't matter whether those PRs are waiting on review, approved, or in rework. A closed PR's multidev lives until the next deploy, so the open count can run a little low.

This order is the rule for every agent. Change it here, not in one person's agent setup.

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

## Approving or sending back a gated phase

- **Approve:** move the phase child to `To Do` (on the board, or with the dashboard's Approve button, which also assigns the default owner if nobody is assigned and comments on the parent). The router never sees it as waiting again.
- **Send back:** post a `## Follow-up needed` block on the gated child naming who owes the fix (usually the owner of the phase before it), and add `follow-up`. The child stays in `Backlog`, drops out of "Waiting on a go," and shows under that person in the brief. When they finish and remove the label, it comes back to the gate.

A gated child with an open `needs-decision` is held the same way until the decision is made.

## What the router may change

The router runs unattended, so its writes are a short, fixed list. Anything not on it goes in the brief as a suggestion for a person.

| Write | When |
|---|---|
| Set Status `Backlog` → `To Do` on a phase child | Every blocker is Done or closed, the parent is open, the child has no open `needs-decision` or `follow-up`, and its phase's Gate is `auto` |
| Assign the phase's default owner | Only on a child it just promoted, and only if that child has no assignee |
| Comment on the parent | One comment per promotion, naming the child and its owner |
| Set or clear the board's **Stage** field | Every run, so each board item shows the stage it is in today (see "The Stage field") |
| Add or remove `awaiting-go` | Kept on exactly the gated children waiting on a go, so the board's Gates view can find them. Removed once a child moves on or is held |
| Comment on the brief issue | Once per run |

The router never closes, relabels, or reassigns anything else, never touches a PR, never starts an agent, and never @-mentions anyone in the brief (it writes handles in backticks so nobody gets a notification storm). Nudges happen in person or in the Monday meeting.

## Monday meeting

Monday is "Exceptions and bets": 30 minutes at most, run from Monday's brief, which opens with an agenda and a count per section. Skip empty sections, and skip the meeting when every section is empty.

Monday is the dev meeting. Communications work (Issue Type `Communications`) goes to the weekly comms meeting with its own board, so the **Monday** view filters to dev Issue Types and the agenda counts leave Communications out. The rest of the brief still lists everything.

| # | Section | Where | What we do |
|---|---|---|---|
| 1 | Decisions & follow-ups | **Monday** view, Stage `Decision` and `Follow-up` | Decisions that need the room. Each leaves decided or with a new date |
| 2 | Stuck | **Monday** view, Stage `Stuck` | In progress with no activity. Each leaves with an owner and a date |
| 3 | Intake | **Monday** view, Stage `Intake` | New `forming` tickets and new tickets with no priority: groom now, park, or decline |
| 4 | Features | The brief (Mondays) | Release-planning weeks only: feature parents by milestone and progress, and which we take on next |
| 5 | Gates | **Monday** view, Stage `Gate` | Phases waiting on a gatekeeper's go (`awaiting-go`) |

### The Stage field

**Stage** is a single-select field on the YaleSites Board that only the router sets. Every run, it gives each board item the stage it is in today and clears it once the item moves on. The **Monday** view shows `has:stage` items, minus Communications, grouped by Stage. When an item is in more than one stage, the first of Gate, Decision, Follow-up, Stuck, Intake wins.

Don't set Stage by hand: the next run overwrites it. Change the label, status, or block that put the item there instead. Items outside the board (PRs in the code repos) never get a Stage, so the brief and the work dashboard remain the full lists.

## Brief

The router posts its brief as a comment on the pinned **Router brief** issue in YaleSites-Internal, every weekday morning. It is yalesites-org/YaleSites-Internal#1987.
