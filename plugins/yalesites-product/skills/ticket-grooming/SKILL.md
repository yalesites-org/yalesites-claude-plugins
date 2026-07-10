---
name: yalesites-ticket-grooming
description: "Create and groom GitHub issues for the YaleSites backlog, including scoping multi-ticket epics. Use when creating a new issue, filling out an existing stub ticket, reviewing a ticket for completeness, or preparing issues for an upcoming sprint or grooming session. Also use when the user wants to create an epic, break a large initiative into an epic with child tickets, or describes a body of work spanning multiple tickets, developers, or sprints — trigger on phrases like 'create an epic', 'epic for X', 'break this into an epic', or 'this is too big for one ticket'. Applies the correct description format, acceptance criteria, priority, size, type, and labels, asks clarifying questions to scope epics properly, and always applies the epic label to parent tickets. Cross-references the YaleSites platform knowledge base to catch overlap with existing features before new work is scoped."
---

# YaleSites Ticket Grooming Skill

## Overview

This skill helps create well-formed GitHub issues for the YaleSites backlog — both single tickets and multi-ticket epics — and groom existing stub tickets into complete, actionable ones. Every issue should be readable by anyone on the team — content editors, site owners, project managers — regardless of technical background.

**Repositories available for developer context, relevant code, and existing patterns:**
- `yalesites-org/yalesites-project`
- `yalesites-org/component-library-twig`
- `yalesites-org/atomic`

Search these when you need implementation context, but always write the issue description in plain English first. Technical details belong in the acceptance criteria, not the description.

**GitHub write-permission scope:** The GitHub connector can create and comment on issues in `yalesites-org/YaleSites-Internal`, but it cannot write comments to `yalesites-org/yalesites-project` (read-only there — good for searching code and reading PRs, not for posting PR comments). If a task calls for commenting on a `yalesites-project` PR, draft the comment text and hand it to Michael to paste in rather than retrying the write.

**GitHub workflow notes:**
- Comments and reviews can only be *added*, never edited in place — there's no tool to revise a comment that's already posted. Post a follow-up comment instead of trying to update one.
- An epic's native GitHub progress bar only reflects open/closed sub-issue state. It has no awareness of custom Project board Status fields (e.g., "Ready for Deployment"), so don't expect it to show a custom workflow stage as complete — that needs to be tracked separately if it matters.
- Some larger reworks run as "the whole epic lives in one PR" — nothing merges until the full scope is done and approved, rather than the usual merge-then-follow-up-tickets model. Confirm which model applies to a given epic before drafting PR review feedback that assumes work will continue after merge.
- If a ticket should go to someone not yet onboarded to GitHub (no handle yet), assign it to the requester as a placeholder rather than leaving it unassigned, and swap in the real assignee once they're set up.
- **Status, Priority, and Size aren't set through issue creation.** These are GitHub Projects V2 custom fields, and the issue-creation/update tools can't write to them directly. After creating or updating an issue, these values still need to be set on the project board itself (or via the `status:*`/`priority:*`/`size:*` trigger labels, if that workflow is in place — they sync to the board field and then the label is auto-deleted, so don't expect the label to persist as a way to check the value later).
- **The Project V2 Status field isn't queryable via the REST API either** — `get_issue`/`search_issues`/`list_issues` won't return it. If asked to audit tickets by board status, the closest available proxy is PR review-state labels (`pass code review` / `pass functional review` / `pass design review`, `needs review`, `needs work`) on companion PRs across `yalesites-project`, `atomic`, and `component-library-twig` — not a direct status query.
- **GitHub's native Issue Type field** (Task/Feature/Bug/Epic/Communications/AI — distinct from the `feature`/`bug`/`task`/`epic` labels used in Step 5 above) also can't be set via the API/MCP tools — it has to be set manually in the issue UI or org settings.
- **Sub-issue linking may not be automatic.** A `- [ ] #XXXX` checklist reference in an issue body creates a backlink, but don't assume it always registers as a tracked GitHub sub-issue (the mechanism that drives the parent's progress bar) — if the epic's progress bar isn't reflecting a child ticket, check whether it needs to be linked explicitly via "Add sub-issue" in the GitHub UI.
- Before recommending a ticket as "available" for pickup (by a person or an unmoderated agent), check more than the absence of an assignment label — confirm there's no assignee set and no `in-review-tag`/`forming`-style in-progress signal on it. A ticket can look open on one signal and still be actively claimed.
- Don't close a ticket as stale or duplicate without first checking whether it has a live, unmerged PR against it — closing out from under active work is an easy mistake during a backlog sweep.

---

## Clarify Missing Fields Before Starting

Before doing any grooming or drafting work on a **single ticket**, check whether the user's prompt included **Status**, **Priority**, and **Size**. If any of these are missing, ask for them upfront using the `AskUserQuestion` tool — one question per missing field, or a single question covering all missing ones if there are multiple.

Do not guess or default these values silently. These fields directly affect how the ticket is prioritized and sequenced in the project board, so getting them right from Mike matters.

### Status (project board column)

Valid options: `Forming` · `Backlog` · `Ready For Work` · `In Progress` · `In Review` · `Done` · `Blocked`

If not specified, ask: *"What status should this ticket be set to on the project board?"*

### Priority

Valid options: `Hotfix` · `High` · `Medium` · `Low`

If not specified, ask: *"What priority should this be — Hotfix, High, Medium, or Low?"*

### Size

Valid options: `XS` · `S` · `M` · `L` · `XL`

If not specified, ask: *"What size estimate feels right — XS, S, M, L, or XL?"*

Once you have all three values confirmed, proceed with grooming.

**Note:** if the request is actually epic-shaped (see "Creating an Epic" below), don't apply Status/Priority/Size to the parent epic ticket the same way — those apply to each child ticket individually. Use the epic's own clarifying-question flow instead.

---

## Platform Fit Check (Do This First)

Before drafting or grooming any ticket — including each child ticket inside an epic — cross-reference the request against the YaleSites platform knowledge base. This catches overlap, suggests extensions over net-new work, and surfaces documentation implications early.

### Step 1: Check what already exists

Load the relevant yalesites skill references and ask:

- **Does a similar block, component, or content type already exist?**
  Check `blocks-reference.md` and `paragraphs-reference.md`. If the request is for something like "a new way to display a list of items," check whether an existing block (e.g., Collection, Custom Card Collection) already does this or could be extended.

- **Does an existing content type already support this use case?**
  Check `content-types-reference.md`. If the request adds a field or behavior to Pages, Posts, Events, etc., confirm whether the field already exists or if this is genuinely additive.

- **Does an existing setting or configuration option already cover this?**
  Check `settings-reference.md`. Some "feature requests" are already available but undiscovered by the requester.

- **Are there existing Views or display modes that could be repurposed?**
  Check `views-reference.md`.

### Step 2: Determine the scope recommendation

Based on the platform check, classify the ticket as one of:

| Classification | What it means | Action |
|---------------|---------------|--------|
| **Extend existing** | A current block/component/type already handles the core need; this request adds an option, field, or variant | Note the existing feature in the ticket description; scope the work as an enhancement to that feature |
| **New, distinct feature** | Nothing on the platform does this; the request is genuinely additive | Proceed as a new feature ticket |
| **Already exists** | The request is already supported on the platform | Flag this in the ticket; note where the feature lives and consider closing as "works as intended" or converting to a docs/training ticket |
| **Conflicts with platform direction** | The request would add complexity that cuts against platform constraints or brand consistency goals | Flag the concern in the ticket; surface it for PM discussion before scoping |

### Step 3: Surface the findings in the ticket

Incorporate the platform check findings directly into the ticket:

- **If extending existing:** The description should name the existing feature ("This adds a new layout option to the existing Action Banner block…"). The acceptance criteria should note which existing docs need updating rather than pointing to new docs.
- **If already exists:** Add a note at the top of the issue ("Note: this functionality may already exist via [X]. Recommend confirming before scoping.").
- **If conflicts:** Add a note flagging the concern for the PM to review before development is assigned.

---

## Issue Format

Every issue needs a clear title plus these six fields, in this order:

---

### Title

The title is what shows up in board views, search results, and notification emails — it needs to tell someone what the work is without opening the issue. Write (or rewrite) the title so it names the specific thing being built, fixed, or requested, not a vague category. "Fix embed bug" tells nobody anything; "RC: Embed block: missing title attribute on Bluesky, Instagram, and event map embeds" tells the reader exactly what's broken and where.

When grooming an existing stub ticket, check the title along with the other fields — a placeholder or overly generic title ("Bug in Layout Builder", "Update embeds") should be rewritten to reflect what the description actually says once it's filled in. If rewriting a title would change what the issue appears to be about (e.g., the original title implies a different bug than what's described), flag that for Mike rather than silently reinterpreting.

**Common title prefixes.** The backlog uses a set of recurring prefixes that make similar tickets easy to spot and filter on. Apply one if it fits; don't force one onto a ticket that doesn't match any of these patterns — a plain, descriptive title is better than a mismatched prefix.

| Prefix | When to use |
|--------|-------------|
| `RC:` | A bug found during release-candidate testing, before the release ships. Use when the prompt says something like "make an RC ticket" or references RC/QA testing. (Occasionally numbered — `RC2:`, `RC3:` — for issues found in a later regression pass on the same release.) |
| `Epic:` | The parent ticket for a multi-ticket initiative. See "Creating an Epic" below. |
| `Bug:` | A defect found outside of RC testing (reported by an editor, caught in normal use, etc.). |
| `Embed:` | New or changed support for a specific embeddable content type (calendars, maps, social posts). |
| `Embed Request:` | An intake ticket for a new embed type someone has asked for but that isn't scoped/dev-ready yet. |
| `Feature Request:` | A new-functionality ask, typically as raised by a stakeholder, before it's fully scoped. |
| `UX Research:` / `UX Discovery:` / `UX Evaluation:` | Research-workstream tickets — study prep, participant outreach, interview scheduling, evaluating an existing flow. |
| `Design:` | A visual/design deliverable with no dev work implied (mockups, icon sets, etc.). |
| `Web:` | Work on the yalesites.yale.edu marketing/content site itself, not the platform. |
| `Docs:` | A documentation-only ticket. |
| `Migration Tool:` | Work on content migration tooling (CSV import/export, etc.). |
| `Community Spotlight:` | A specific Community Spotlight content ticket. |
| `YS-Email:` | YaleSites training or release email tickets. |

**Epic child tickets** follow a related but distinct pattern: they're prefixed with a short form of their epic's name rather than one of the prefixes above, so they group together visually in the backlog (e.g., `Views Block Rework: Authoring Form UX/UI Audit`, `Publications: Teaser Display`, `Wave 3: Interactive molecules`). When scoping child tickets for a new epic, pick one short, consistent name and apply it to every child ticket — see "Creating an Epic" below.

---

### 1. Description

Briefly describe the feature, bug, or improvement in plain language. Avoid developer jargon. Focus on **what it is** and **why it matters** to the user or platform. Anyone on the team, regardless of technical background, should be able to read this and understand the work.

---

### 2. Acceptance Criteria

A single bulleted list of everything required to close the issue. Cover all relevant angles:

- Developer tasks and technical requirements
- UX considerations (field labels, design option names, UI behavior)
- Accessibility: flag anything that needs WCAG 2.1 AA validation for the accessibility engineer
- Documentation: note if any existing docs need updating or new docs need to be created

If an existing ticket has an unresolved internal debate (e.g., a past comment thread arguing both sides of a design question), don't resolve it unilaterally while grooming — preserve it as an explicit open acceptance-criteria item so it gets a real decision rather than getting silently closed over.

**Documentation tickets for features that haven't shipped yet:** these can still be marked `Ready For Work` so the doc can be drafted and staged in parallel with development — mark the ticket as blocked by the feature ticket, and add an explicit acceptance criterion not to publish until the feature ships.

---

### 3. Priority

Choose one based on user and platform impact:

| Priority | When to use |
|----------|-------------|
| **Hotfix** | Critical issue breaking core functionality or accessibility. Immediate deployment required. |
| **High** | Significantly impacts user experience or blocks key workflows. Soonest milestone priority. |
| **Medium** | Improves platform usability or addresses moderate user pain points. |
| **Low** | Nice-to-have enhancement with minimal user impact. Future consideration. |

---

### 4. Size

Estimate relative effort and complexity:

| Size | Definition |
|------|-----------|
| **XS** | Single file change or quick setting adjustment. < 1 hour |
| **S** | Minor feature update or simple block modification. 1–4 hours |
| **M** | New block component or moderate platform enhancement. 1–2 days |
| **L** | Complex feature with multiple components or significant UX changes. 3–5 days |
| **XL** | Major platform addition requiring design system updates and extensive testing. 1–2 weeks |

---

### 5. Type

Choose one:

| Type | When to use |
|------|------------|
| **AI** | Work related to the Beacon AI chatbot |
| **Bug** | An unexpected problem or behavior |
| **Communications** | Work that falls under the Communications workstream |
| **Feature** | A request, idea, or new functionality |
| **Task** | A specific piece of work |
| **Vendor/Supported Builds** | Websites being built by vendors or supported by the YaleSites team |

---

### 6. Labels

Apply all relevant labels: `ai-engine` `feedback` `vendor-build` `accessibility-bug` `opac` (add others as applicable)

---

## Creating an Epic

Use an epic when a request is genuinely too large for one ticket — it touches multiple components or content types, needs several developers, or will clearly span multiple sprints. If you can describe the work in one well-scoped Acceptance Criteria list, it's a ticket, not an epic. A useful gut-check from how epics are usually scoped: if you can't state the outcome in a sentence or two, or the work looks like it's more than about 4–6 weeks, it's epic-shaped.

The reference example is `yalesites-org/YaleSites-Internal#1161` (Views Block Architectural Rework) — the team's lead developer called this one out as working really well. When in doubt about how much detail to include or how to structure something, look at how #1161 handled it.

### Step 1: Ask clarifying questions before drafting

Epics fail most often because scope was never pinned down before work started (see anti-patterns below). Before drafting anything, use `AskUserQuestion` to gather whatever the user hasn't already told you:

- **Problem/goal** — What isn't working today, or what opportunity does this open up? What's the one-sentence outcome this epic delivers?
- **Scope boundaries** — What's explicitly in scope? Is there adjacent work that's tempting to fold in but should really be its own follow-up?
- **Success criteria** — How will you know the epic is done? An epic with no closure criteria never closes.
- **Milestone/timeline** — Does this need to land in a specific release, or is timing open? YaleSites epics ship as a single unit in one milestone once all child tickets are done — they don't span multiple releases. A scoping/spike ticket can land in an earlier milestone on its own if the epic itself isn't ready to commit to a release yet.
- **Known dependencies** — Anything that has to happen first, or any other epic/ticket this depends on?

Stay within PM scope: these are product-goal and boundary questions, not implementation questions. If the technical approach is still unknown, that's expected — that's what the spike ticket in Step 2 is for. Only ask about what's genuinely still ambiguous; skip anything the user already answered in their prompt.

### Step 2: Decide if a spike/ADR ticket comes first

If the technical approach isn't settled, make the first child ticket a spike or ADR (architecture decision record) — audit the current state and propose a design, to be reviewed and approved before the rest of the child tickets are written or estimated. This was #1162 in the Views Rework epic, and it's why the later child tickets could be scoped accurately. Don't force full detail into every child ticket up front if the design is still an open question — scope what you can, and let the spike inform the rest.

### Step 3: Write the epic (parent ticket)

Use this structure, modeled on #1161:

```markdown
## Summary
[What is being built or changed, and why — the outcome, not just the mechanism]

## Current State
[Optional, valuable for refactors/rework: what exists today and why it's a problem]

## Proposed Approach
[High-level shape of the solution — enough for the team to orient, not a full technical design. Point to the spike/ADR ticket for the detailed design.]

## Scope
[What's in scope — content types, features, user flows, etc. affected]

## Child Tickets (intended order)
- [ ] #XXXX -- [Spike/ADR: design approval before further work, if applicable]
- [ ] #XXXX -- [Child ticket 1]
- [ ] #XXXX -- [Child ticket 2]

## Follow-up Work (Post-Epic)
[Explicitly out-of-scope items this epic unblocks or surfaces. Tag with a `<epic-name>-followup` label so they're easy to find later, and note they shouldn't be pulled into active work until the epic's milestone closes.]
```

Create the child tickets as real GitHub issues first, then reference their numbers in the parent's checklist — GitHub automatically tracks checklist items that reference issue numbers as sub-issues, which is what gives the parent a clean progress view (this is what made #1161 easy to follow).

### Step 4: Apply the epic label

**Always apply the `epic` label to the parent ticket.** This is how the epic is distinguished from a regular issue on the board and in filtered views — don't skip it, and double-check it's set before treating the epic ticket as done.

### Step 5: Write each child ticket using the standard Issue Format

Every child ticket still follows the six-field format above (Description, Acceptance Criteria, Priority, Size, Type, Labels). An epic doesn't change how individual tickets are written — it just adds a parent that ties them together and gives the whole body of work a shared goal.

### Avoid these epic anti-patterns

- **No defined outcome.** If you can't say what "done" looks like, the epic will never close out. Pin this down in Step 1.
- **The dumping ground.** Don't let unrelated bugs, requests, or "while we're in there" ideas get folded into an in-flight epic — route them to the Follow-up Work section or a separate ticket instead.
- **Scope creep without re-scoping.** If new child tickets keep getting added without the goal itself changing, the epic was probably under-scoped at the start. Pause and revisit Step 1 rather than continuing to bolt things on.
- **Spanning multiple releases.** YaleSites epics ship as one unit in one milestone. If it's genuinely going to take multiple releases, it likely needs to be split into two epics that each deliver independent value.

### Epic Quality Bar

Before treating an epic as ready:

- [ ] Problem/goal and success criteria are stated in the Summary
- [ ] Scope is explicit — in-scope, and out-of-scope/follow-up if relevant
- [ ] `epic` label is applied to the parent ticket
- [ ] Child tickets exist and are checklisted in the parent
- [ ] If the technical approach is unsettled, a spike/ADR ticket is first in the child list
- [ ] Milestone reflects a single release, not an open-ended span

---

## Grooming Existing Stub Tickets

When grooming an existing ticket that's missing fields or has a thin description:

1. Read the existing issue body — preserve anything already written
2. Identify what's missing (description too vague, no acceptance criteria, no size/priority, etc.) — including whether the title is vague, generic, or doesn't match what the description actually says
3. Search the relevant repos for context if the work is technical
4. Fill in the missing fields following the format above, rewriting the title if it doesn't clearly state the work (see "Title" above)
5. Use `mcp__github__update_issue` on `yalesites-org/YaleSites-Internal` — **append or replace only the missing sections**, never overwrite content the team has already written

---

## Quality Bar

Before submitting or updating an issue, check:

- [ ] Title clearly states the specific work, and uses a matching prefix if one applies
- [ ] Description is jargon-free and makes sense to a non-developer
- [ ] Acceptance criteria covers dev, UX, accessibility, and docs angles
- [ ] Priority reflects actual user/platform impact (don't default to Medium)
- [ ] Size is realistic — if unsure, err toward larger
- [ ] Type is set
- [ ] Relevant labels are applied

For epics specifically, also run through the Epic Quality Bar above.
