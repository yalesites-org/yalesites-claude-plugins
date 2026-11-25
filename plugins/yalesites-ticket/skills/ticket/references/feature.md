# Scoping a feature (parent issue and phase children)

Load this when a groomer scopes a new Feature, turns a `forming` feature request into a feature parent, or gathers an in-flight feature's loose tickets under one parent. Also load `references/routing.md` for the phase table. Each child still follows `references/issue-format.md`, and its fields are set per `references/fields.md`.

---

**A `Feature` gets a parent issue with one sub-issue per phase.** Nearly every feature needs work from more than one person: UX, design, development, QA, visual regression, docs. Grooming those tickets up front is how none of them gets forgotten. The blocked-by chain between them records who waits on whom. If your team runs the router routine, it uses that chain to hand each phase off when the one before it finishes. Without it, people move the next phase by hand. Either way, this skill creates the same tickets and the same chain.

**A feature parent is not an epic.** The two work at different sizes:

| | Feature parent | Epic |
|---|---|---|
| What it is | One shippable thing, e.g. the Office Hours block | An initiative made of several features or a large rework, e.g. the Views Block Rework |
| Title | `Feature: Office Hours block` | `Epic: Views Block Architectural Rework` |
| Issue Type | `Feature` | `Epic` |
| Children | Phase tickets | Features, spikes, and tasks |

Neither gets an `epic` label: that label was retired on 2026-10-28, and the Issue Type tells them apart.

A feature parent can be a sub-issue of an epic when it is part of a bigger initiative. The reference example is yalesites-org/YaleSites-Internal#1542 (Office Hours block).

The exception is a small enhancement: one developer, one Acceptance Criteria list, no UX or design work, and docs that fit as one AC line. That stays a single ticket. If you aren't sure, ask the user.

## Steps

1. **Pick the phases.** Ask which phases apply, as one multi-select `AskUserQuestion` question. The phases, their keys, their default owners, and their order are in `references/routing.md`. Read it fresh each time rather than working from memory, because owners change there first. Preselect the ones the request obviously needs. Product calls are not a phase; they go through `needs-decision` (see `references/decisions.md`).
2. **Allowed regions, when the feature is a new block or changes where a block can go.** Ask which Layout Builder regions it may be placed in. There are six regions, more than the 4-option cap of `AskUserQuestion` allows in one question, so ask two multi-select questions in one call:
   1. **Full-width and equal columns:** One column, Banner, Two column (50/50), Three column (33/33/33).
   2. **Two column (70/30) or (30/70):** The main region, The sidebar region, Neither.

   "Not decided yet" has no option of its own: say in the first question that the user can answer Other with "not decided", and treat any answer like that as not decided. Write the answer into the parent's Scope as an **Allowed regions** line, and into the parent's machine block as `allowed_regions: [one_col, half, third, main, sidebar, banner]` (only the ones allowed), or as `allowed_regions` in its `open_decisions` list when not decided. Then carry it into the children:
   - **Design child:** an AC line "Mockups at each allowed region width, plus 360px", with the narrowest one named (the 70/30 sidebar is about 305px at 1440, and it is the width that broke Office Hours late in yalesites-org/YaleSites-Internal#1710).
   - **Not decided yet:** make it an AC item on the UX child ("Decide which regions the block is allowed in"), so it is settled before design starts. Don't guess it, and don't leave it out: design work can't size its mockups without it.
   - **Dev and QA children:** an AC line that the block is offered in exactly those regions and no others.
3. **Write the parent.** Title `Feature: <name>`, Issue Type `Feature`, no `epic` label. The body is a TL;DR, the outcome, the Scope, and a **Phases** list naming each child and its owner. Status, Priority, and Risk go on the parent like any ticket, and the parent's milestone is the release the feature ships in.
4. **One child per phase,** more when a phase splits naturally (two design deliverables, say). Title each `<Feature name>: <Phase>`, e.g. `Office Hours: Docs`, or a more specific title when there are several in one phase. Each child still follows the full issue format. Its Acceptance Criteria say what "done" means for that phase, which is what lets the next owner start without a meeting.
5. **Machine block.** Every phase child's closing `<!-- yalesites:agent -->` block includes `phase: <key>` and `parent: yalesites-org/YaleSites-Internal#NNNN`. Tools that route phases (the router routine, if your team runs it) find phase children by the `phase:` line.
6. **Assign the phase owner** from `references/routing.md` unless the user names someone else. **UX is the exception: April's time varies week to week.** Before assigning a UX phase to `atiddei`, ask the user whether April has room this week. If not, or if they aren't sure, assign it to `miketullo95`, who can hand it to April later. Ask once for the whole set ("use the default owners?") rather than per child.
7. **Status.** The first phase goes to `To Do`. Every later phase goes to `Backlog`, except a `release`-gated phase (Visreg site pages), which goes to `Blocked`. Don't move later phases to `To Do` yourself. They move when their blockers finish (by the router routine if your team runs one, otherwise by a person), except gated phases (the Gate column in `references/routing.md`), which wait for the gatekeeper's go.
8. **Wire it natively.** Add each child as a sub-issue of the parent, then add the blocked-by dependencies from the routing table, skipping phases that weren't created:

   ```bash
   # Sub-issue: the child's numeric id, not its number
   CHILD_ID=$(gh api repos/yalesites-org/YaleSites-Internal/issues/<child> --jq .id)
   gh api -X POST repos/yalesites-org/YaleSites-Internal/issues/<parent>/sub_issues -F sub_issue_id="$CHILD_ID"

   # <child> is blocked by <blocker>
   BLOCKER_ID=$(gh api repos/yalesites-org/YaleSites-Internal/issues/<blocker> --jq .id)
   gh api -X POST repos/yalesites-org/YaleSites-Internal/issues/<child>/dependencies/blocked_by -F issue_id="$BLOCKER_ID"
   ```

   A child that already has a different parent must be moved: add `-F replace_parent=true` to the sub-issue call. Read both back (`gh api repos/yalesites-org/YaleSites-Internal/issues/<child>/dependencies/blocked_by --jq '.[].number'`) before reporting the feature as done.
9. **Milestone.** Every phase child gets the parent's milestone, Docs included. The exception is a `release`-gated phase (Visreg site pages): it gets the **next** release milestone after the parent's, because its work can't start until the parent's release ships.
10. **`claude`.** Only on dev children, only when groomed and with no open `needs-decision`. UX, Design, QA, and Docs children never get it.

**Board writes in a batch.** Use `scripts/set-board-fields.sh` for every child, never `gh project item-edit --url`. A 4-phase feature trips GitHub's rate limit partway through with the latter. See `references/fields.md`.

## Retrofitting a feature already in flight

A feature that grew a pile of loose tickets can be gathered under a parent after the fact. Use the original feature ticket as the parent if it is typed `Feature` (retitle it `Feature: <name>`), otherwise create one. Then, for each related ticket:

- Make it a direct sub-issue of the parent (move it with `replace_parent=true` if it sits under a sibling).
- Add `phase: <key>` and `parent: ...` to its machine block. **Append** the block to the end of the body if it has none; never rewrite text someone else wrote.
- Leave Status alone. Routing only moves tickets out of `Backlog` (or `Blocked`, for a `release`-gated child), so in-flight work is untouched.
- Leave out tickets that span many features (e.g. "redo all block picker icons"). Link them from the parent's body instead.

Add blocked-by links only between phases that haven't started yet. Linking finished work is noise.

## Feature parent quality check

On top of the ticket Quality Bar in `references/grooming.md`, check:

- [ ] One child per phase that applies, each with its `phase:` machine line, its phase owner, and the parent's milestone (a `release`-gated child takes the next release)
- [ ] Native sub-issues and blocked-by dependencies are wired and read back
- [ ] Only the first phase is in `To Do`
- [ ] The parent is typed `Feature` with no `epic` label
