# Creating an epic

Load this when the request is epic-shaped: "create an epic", "epic for X", "break this into an epic", "this is too big for one ticket", or a body of work spanning several tickets, developers, or sprints. Each child ticket still follows `references/issue-format.md`, with fields per `references/fields.md`. If a child is itself a feature, scope it per `references/feature.md`.

---

Use an epic when a request is genuinely too large for one ticket: it touches multiple components or content types, needs several developers, or will clearly span multiple sprints. If you can describe the work in one well-scoped Acceptance Criteria list, it's a ticket, not an epic. A useful gut-check from how epics are usually scoped: if you can't state the outcome in a sentence or two, or the work looks like it's more than about 4 to 6 weeks, it's epic-shaped.

An epic is not a feature parent. A single shippable feature with UX, design, dev, QA, and docs phases is a feature parent; see the comparison table in `references/feature.md`.

The reference example is yalesites-org/YaleSites-Internal#1161 (Views Block Architectural Rework). The team's lead developer called this one out as working really well. When in doubt about how much detail to include or how to structure something, look at how yalesites-org/YaleSites-Internal#1161 handled it.

Don't apply Status, Priority, and Risk to the parent epic the way you would a single ticket. Those apply to each child ticket individually. The epic's own clarifying questions (Step 1) replace the single-ticket field questions, including the milestone question.

## Step 1: Ask clarifying questions before drafting

Epics fail most often because scope was never pinned down before work started (see anti-patterns below). Before drafting anything, use `AskUserQuestion` to gather whatever the user hasn't already told you:

- **Problem/goal:** What isn't working today, or what opportunity does this open up? What's the one-sentence outcome this epic delivers?
- **Scope boundaries:** What's explicitly in scope? Is there adjacent work that's tempting to fold in but should really be its own follow-up?
- **Success criteria:** How will you know the epic is done? An epic with no closure criteria never closes.
- **Milestone/timeline:** Does this need to land in a specific release, or is timing open? YaleSites epics ship as a single unit in one milestone once all child tickets are done. They don't span multiple releases. A scoping/spike ticket can land in an earlier milestone on its own if the epic itself isn't ready to commit to a release yet.
- **Known dependencies:** Anything that has to happen first, or any other epic/ticket this depends on?

Stay within PM scope: these are product-goal and boundary questions, not implementation questions. If the technical approach is still unknown, that's expected; that's what the spike ticket in Step 2 is for. Only ask about what's genuinely still ambiguous; skip anything the user already answered in their prompt. Remember the `AskUserQuestion` caps: at most 4 questions per call and 4 options per question.

## Step 2: Decide if a spike/ADR ticket comes first

If the technical approach isn't settled, make the first child ticket a spike or ADR (architecture decision record): audit the current state and propose a design, to be reviewed and approved before the rest of the child tickets are written or estimated. This was yalesites-org/YaleSites-Internal#1162 in the Views Rework epic, and it's why the later child tickets could be scoped accurately. Don't force full detail into every child ticket up front if the design is still an open question. Scope what you can, and let the spike inform the rest. The ADR's location rule is under "Acceptance Criteria" in `references/issue-format.md`.

## Step 3: Write the epic (parent ticket)

Use this structure, modeled on yalesites-org/YaleSites-Internal#1161. Same GitHub-reading rules as a regular ticket (see "How this reads on GitHub" in `references/issue-format.md`): lead with a TL;DR, keep Summary, Scope, and Child Tickets visible, and collapse the longer context (Current State, Proposed Approach) into a named `<details>` block.

```markdown
**TL;DR:** [One or two sentences: the outcome this epic delivers and why. Plain language.]

## Summary
[What is being built or changed, and why: the outcome, not just the mechanism]

<details>
<summary><b>Current state and proposed approach</b></summary>

### Current State
[Optional, valuable for refactors/rework: what exists today and why it's a problem]

### Proposed Approach
[High-level shape of the solution: enough for the team to orient, not a full technical design. Point to the spike/ADR ticket for the detailed design.]

</details>

## Scope
[What's in scope: content types, features, user flows, etc. affected]

## Child Tickets (intended order)
- [ ] yalesites-org/YaleSites-Internal#XXXX -- [Spike/ADR: design approval before further work, if applicable]
- [ ] yalesites-org/YaleSites-Internal#XXXX -- [Child ticket 1]
- [ ] yalesites-org/YaleSites-Internal#XXXX -- [Child ticket 2]

## Follow-up Work (Post-Epic)
[Explicitly out-of-scope items this epic unblocks or surfaces. Add each as a native sub-issue of this epic so it's easy to find later, and note it shouldn't be pulled into active work until the epic's milestone closes. Don't create a `<epic-name>-followup` label: those were retired on 2026-10-28, and the `follow-up` label means something else: an action a named person owes, like a reply or a check-in.]
```

Create the child tickets as real GitHub issues first, then reference their numbers in the parent's checklist. GitHub tracks checklist items that reference issue numbers, which is what gives the parent a clean progress view (this is what made yalesites-org/YaleSites-Internal#1161 easy to follow). Write each reference in the full `owner/repo#number` form.

**Sub-issue linking may not be automatic.** A checklist reference creates a backlink, but don't assume it always registers as a tracked GitHub sub-issue (the mechanism that drives the parent's progress bar). If the epic's progress bar isn't reflecting a child ticket, link it explicitly: use the sub-issue call in step 8 of `references/feature.md`, or "Add sub-issue" in the GitHub UI.

**The progress bar only knows open and closed.** An epic's native GitHub progress bar reflects open/closed sub-issue state only. It has no awareness of custom Project board Status fields (e.g., `Done`), so don't expect it to show a custom workflow stage as complete. That needs to be tracked separately if it matters.

**One-PR epics.** Some larger reworks run as "the whole epic lives in one PR": nothing merges until the full scope is done and approved, rather than the usual merge-then-follow-up-tickets model. Confirm which model applies to a given epic before drafting PR review feedback that assumes work will continue after merge.

## Step 4: Set the Epic Issue Type

**Always set the parent's Issue Type to `Epic`** (see "Setting the native Issue Type" in `references/fields.md`). That's how the epic is told apart from a regular issue on the board, in filtered views, and by developer tooling such as the epic-branch script in the `yalesites-dev` plugin. Read it back before treating the epic ticket as done. Don't add an `epic` label: it was retired on 2026-10-28.

## Step 5: Write each child ticket using the standard issue format

Every child ticket still follows the six-field format in `references/issue-format.md` (Description, Acceptance Criteria, Priority, Risk, Type, Labels), with fields asked for and written per `references/fields.md`. An epic doesn't change how individual tickets are written. It just adds a parent that ties them together and gives the whole body of work a shared goal. Child titles use the epic's short name as their prefix (see "Title" in `references/issue-format.md`). The `claude` label goes on individual children, never on the parent.

## Avoid these epic anti-patterns

- **No defined outcome.** If you can't say what "done" looks like, the epic will never close out. Pin this down in Step 1.
- **The dumping ground.** Don't let unrelated bugs, requests, or "while we're in there" ideas get folded into an in-flight epic. Route them to the Follow-up Work section or a separate ticket instead.
- **Scope creep without re-scoping.** If new child tickets keep getting added without the goal itself changing, the epic was probably under-scoped at the start. Pause and revisit Step 1 rather than continuing to bolt things on.
- **Spanning multiple releases.** YaleSites epics ship as one unit in one milestone. If it's genuinely going to take multiple releases, it likely needs to be split into two epics that each deliver independent value.

## Epic quality bar

Before treating an epic as ready:

- [ ] Body opens with a TL;DR line, and the longer context (Current State, Proposed Approach) is in a collapsed block
- [ ] Problem/goal and success criteria are stated in the Summary
- [ ] Scope is explicit: in-scope, and out-of-scope/follow-up if relevant
- [ ] The parent's Issue Type is `Epic` (no `epic` label)
- [ ] Child tickets exist and are checklisted in the parent
- [ ] If the technical approach is unsettled, a spike/ADR ticket is first in the child list
- [ ] Milestone reflects a single release, not an open-ended span
- [ ] `Scope` and `Child Tickets` reflect current reality. If any child ticket has diverged since the epic was written, run the drift check in `references/grooming.md` before calling the epic ready
