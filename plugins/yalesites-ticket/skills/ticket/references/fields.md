# Ticket fields: asking for them and writing them

Load this when a groomer is setting a single ticket's fields: Status, Priority, Risk, Milestone, Assignee, and the `claude` label. It also covers writing those fields to the YaleSites Board and the issue, and setting the native Issue Type. The quick bug path in `SKILL.md` has a short version of these rules. This file is the full version and wins if they disagree.

---

## Clarify missing fields before starting

Before doing any grooming or drafting work on a **single ticket** (as a groomer; see "Who's filing" in `SKILL.md`), check whether the user's prompt covered **Status**, **Priority**, **Risk**, **Milestone**, **Assignee**, and whether they want the **`claude` label**. Ask about anything they haven't already answered, using the `AskUserQuestion` tool.

**Batch them, but mind the caps.** `AskUserQuestion` allows at most **4 questions per call** and at most **4 options per question**. Both are hard validation, so a call asking six questions is rejected outright and the user sees nothing. Six unanswered fields therefore go in two calls:

1. **Board fields:** Status, Priority, Risk, Milestone.
2. **Routing:** Assignee, and the `claude` label.

Two calls instead of six round trips. Drop whatever the user already answered, and if four or fewer are left, ask in one call.

The option cap bites just as easily: Status has six valid values and the assignee table below lists nine handles. Offer the few most likely for this ticket and let the user take **Other**, which `AskUserQuestion` supplies on its own. Never list every valid value as an option just because it is valid.

Do not guess or default these values silently. Status and Priority decide how the ticket is sequenced on the project board. Risk decides how carefully it's built and reviewed. Milestone decides which release it ships in. Assignee and the `claude` label decide who (or what) actually picks it up.

**Epics are different.** If the request is epic-shaped (see `references/epic.md`), don't apply Status, Priority, and Risk to the parent epic ticket the same way. Those apply to each child ticket individually. Use the epic's own clarifying-question flow instead.

### Status (project board column)

Valid options, exactly as configured on the YaleSites Board, in board order. **Match this capitalization exactly.** These strings get passed straight to the board write, and several are not title-cased. This is a convenience copy; `references/board-status.md` is canonical and wins if they ever disagree.

| Status | Meaning |
|--------|---------|
| `Backlog` | This item hasn't been started |
| `To Do` | This is ready to be picked up |
| `Blocked` | Work is blocked and cannot move forward |
| `In progress` | This is actively being worked on |
| `In review` | This item is in review |
| `Done` | Review is finished and the work is merged: to `develop`, to the release staging branch (`after-2260` and its successors), to an epic branch, or a hotfix to `master`. For a docs ticket, its draft is approved and staged on yalesites.yale.edu. Stays open until the release ships |

`Done` does not mean closed. A ticket moves to `Done` when its work merges (for a docs ticket, when its approved draft is staged), and stays open until the release ships and someone confirms it and closes it. Milestones, not a board status, say which release the work ships in.

If not specified, ask: *"What status should this ticket be set to on the project board?"* Six valid values against a 4-option cap, so offer the four that actually fit the ticket's shape, usually `Backlog`, `To Do`, and whichever in-flight state applies. **Other** covers the rest.

If the board's options ever change, re-check them rather than trusting this list:

```bash
gh project field-list 6 --owner yalesites-org
```

### Priority

Valid options: `Hotfix` · `High` · `Medium` · `Low`

If not specified, ask: *"What priority should this be: Hotfix, High, Medium, or Low?"*

If the answer is Hotfix, the title needs the `Hotfix:` prefix stacked in front of its type prefix. See "Title" in `references/issue-format.md`.

What each level means is in "Priority" in `references/issue-format.md`.

### Risk

Valid options: `Low` · `Medium` · `High`

If not specified, ask: *"What risk level is this: Low, Medium, or High?"* Lead with your own read from the definitions in "Risk" in `references/issue-format.md`. Size was retired on 2026-10-28; don't ask for it or set it.

### Milestone

Every ticket should land in a milestone. Ask which one, and **lead with the next upcoming feature release** as the recommended answer: the open milestone whose title is a dated release and whose due date is the soonest one still ahead of today.

"Dated release" means `MM-DD-YY <anything> Release`, not `MM-DD-YY Feature Release` specifically. Non-feature releases use the same shape, as `07-07-26 Drupal 10.6 Release` does, and matching only on "Feature" would skip it and schedule an upgrade ticket a release late. Match on the leading date and the trailing `Release` instead. (Milestone #1 is `11-24-2025 Feature Release`, with a four-digit year. It is closed and in the past, so it cannot win this sort, but allow for both year formats if you ever reuse the pattern for a broader sweep.)

Read the live list rather than working from memory, because the dates move and releases close:

```bash
gh api repos/yalesites-org/YaleSites-Internal/milestones --paginate \
  -q '.[] | "\(.number)\t\(.title)\tdue=\(.due_on)\topen=\(.open_issues)"'
```

Several kinds of milestone show up in that list, and only the first is ever a valid default:

| Kind | Examples | When it's right |
|------|----------|-----------------|
| **Dated release** | `12-08-26 Feature Release`, `07-07-26 Drupal 10.6 Release` | The normal case. This is what "next upcoming release" means. |
| **Initiative** | `Views Block Rework`, `Drupal AI Migration` | Only when the ticket is a child of that epic or initiative. Don't pick one just because it happens to be open. |
| **Hotfix** | `10-14-26 Hotfix` | Only for a `Hotfix`-priority ticket. See "Hotfix tickets" below. |
| **Catch-all bucket** | `Ready For Work`, `Backlog` | The work is real but genuinely unscheduled. These carry sentinel due dates far in the future (2030), so they'll never win a soonest-due-date sort. Don't let one become the default by accident. |

Two traps when working out which release is "next":

- **A due date that has already passed, or is today, is not upcoming.** The current release milestone stays open through and past its due date while the release ships and late fixes land, so the smallest due date in the list is often the one that's already going out the door. Sort only on due dates still ahead of today.
- **Don't drop new feature work into a release that's already in its RC window.** Once RC testing has started, only fixes for that release belong in it; new feature work goes to the release after. If you can't tell whether a release is locked, ask instead of assuming.

If not specified, ask: *"What milestone should this go in?"* Offer the next upcoming feature release first as the recommendation, with the current in-flight release and "no milestone for now" as the alternatives.

**Hotfix tickets.** A `Hotfix`-priority ticket still gets a milestone: the open `MM-DD-YY Hotfix` milestone for the hotfix it ships in. Agents will pick up a Hotfix with no milestone (see "Priority and the agent pickup order" in `references/routing.md`), but that is a fallback, not the plan. List open milestones whose title ends in `Hotfix`:

- **One or more open:** recommend the soonest, with "no milestone for now" as the alternative.
- **None open:** ask *"There's no open hotfix milestone. Do you want to create one for the upcoming hotfix?"* If yes, ask the hotfix date, then create `MM-DD-YY Hotfix` with its due date one week after the hotfix date at `T12:00:00Z`, matching the release milestones' hotfix buffer:

  ```bash
  gh api repos/yalesites-org/YaleSites-Internal/milestones -X POST \
    -f title="MM-DD-YY Hotfix" -f due_on="YYYY-MM-DDT12:00:00Z"
  ```

  If no, leave the milestone empty and say the ticket is unscheduled until someone picks a hotfix date.

**Visreg site page tickets** go in the release **after** the feature's. See "Acceptance Criteria" in `references/issue-format.md`.

For an **epic**, the milestone is a scoping decision rather than a routine field, and the epic's own clarifying questions already cover it (Step 1 in `references/epic.md`: YaleSites epics ship as a single unit in one milestone). Don't ask for it twice.

### Assignee

Always ask whether the ticket should go to someone, rather than creating it unassigned by default. An unassigned ticket is easy to lose in the backlog.

Ask: *"Who should this be assigned to?"*

**Offer at most four options**, per the cap above: the three handles most likely for this ticket's shape, chosen with the routing habits below, plus **"leave it unassigned for now."** The table is routing reference, not the option list. **Other** covers anyone else, and the `gh api` fallback below covers spelling.

| Handle | Who | Usually gets |
|--------|-----|--------------|
| `dblanken-yale` | David Blankenship, lead developer (Yale) | Development work. The default for anything that needs code written. |
| `vinmassaro` | Vincent Massaro, senior developer (Yale) | CI/CD and Drupal version upgrades: build and deploy pipelines, Pantheon workflow, core and contrib major-version updates. |
| `laura-johnson` | Laura Johnson, Four Kitchens | Development work. Four Kitchens is our outside dev partner, so weigh in-house capacity before routing here by default. |
| `atiddei` | April | UX work: flows, interface design, research-driven changes. |
| `ntay90` | Nick Taylor | Accessibility. Anything needing WCAG 2.1 AA validation or an a11y review. |
| `alyssadechiaro` | Alyssa DeChiaro | Events and Localist: channels, imports, event content and display. |
| `chrissuquie` | Chris Suquilanda | Communications workstream (release emails, training emails, office hours, yalesites.yale.edu content), and a lot of feature requests and bug reports, since he works the ServiceNow queue. |
| `rachel-is-at-yale` | Rachel | Same shape as Chris: support intake off the ServiceNow queue, so a lot of feature requests and bug reports, plus mailing list and support-page work. |
| `miketullo95` | Mike Tullo, Product Manager | PM-owned tickets, release coordination, ticket grooming follow-ups. |

Three routing habits worth keeping:

- **Accessibility is easy to leave unrouted.** If a ticket carries an accessibility acceptance criterion or the `accessibility` label and nobody is named, suggest `ntay90`.
- **Upgrade and pipeline work has its own owner.** If a ticket is a Drupal core or contrib major-version upgrade, a PHP version bump, or a change to CI, build, or deploy tooling, suggest `vinmassaro` rather than routing it to general development.
- **A ticket that came in through ServiceNow usually stays with whoever filed it.** `Feature Request:` and `Bug:` tickets often originate with Chris or Rachel working the support queue. If the user is grooming one of theirs, keep them on it rather than reassigning, since they hold the reporter context and will be the one closing the loop with the requester.

Keep **"leave it unassigned for now"** as one of the four. That is a legitimate answer while grooming a backlog, and it is better than parking the ticket on someone who isn't going to do it.

If the handle you want isn't one of these, pull the current list rather than guessing at spelling:

```bash
gh api repos/yalesites-org/YaleSites-Internal/assignees --jq '.[].login'
```

If the ticket belongs to someone who isn't on GitHub yet (no handle yet), assign it to the requester as a placeholder rather than leaving it unassigned, and say that's what you did. Swap in the real assignee once they're set up.

### Claude pickup (the `claude` label)

The `claude` label is defined on the repo as *"tickets that are fully groomed and can be taken from a claude agent to be worked on asynchronously."* Applying it puts the ticket in the pool the dev team's Claude agent pulls work from, so it is an actual handoff, not a category tag.

Always ask before applying it: *"Do you want to tag this `claude`, so the dev team's Claude agent can pick it up and work it asynchronously?"*

These things have to be true before it goes on:

- **The ticket is genuinely groomed.** Description, a complete Acceptance Criteria list, Priority, Risk, Type, and a milestone all present (agents never pick up a ticket with no milestone, except a `Hotfix`; a Hotfix still gets its hotfix milestone, see "Milestone" above), and specific enough that an agent with no other context could implement it and know when it's done. If the ticket is still a stub, say so and offer to finish grooming it first instead of tagging it as-is.
- **A new embed provider has its approval.** See "New embed providers" in `references/routing.md`. A Priority or milestone is not an approval.
- **Nothing in it is waiting on a human decision.** An open design question, an unresolved debate preserved as an acceptance-criteria item (see "Acceptance Criteria" in `references/issue-format.md`), a "conflicts with platform direction" flag from the platform fit check, an open `needs-decision`, or work gated on a spike should not go into the async pool.

On epics, the label belongs on individual child tickets, never the parent. The parent is a container, not a unit of work.

Assignee and `claude` are independent: a ticket can be both assigned to a person and tagged for agent pickup, so ask both questions rather than treating one as the answer to the other.

Once the values are confirmed, proceed with grooming.

---

## Writing Status, Priority, and Risk to the board

**Status, Priority, and Risk aren't set through issue creation.** These are GitHub Projects V2 custom fields. Neither the issue-creation tools (`gh issue create`, `mcp__github__create_issue`/`update_issue`) nor labels set them. Only a board write does.

Once the issue exists and Status, Priority, and Risk are confirmed, write them to the **YaleSites Board** project (`yalesites-org`, project number `6`) with the `gh` CLI. This is the only supported path. **Never apply `status:*`, `priority:*`, or `size:*` labels as a substitute.** The label-sync workflow does not match them, so they leave the board field empty while looking like they worked. `references/board-status.md` has the history.

1. Check `gh` is usable before relying on it: `gh auth status`. `gh` needs to be installed, authenticated, and its token needs the `project` scope specifically. `read:project` alone can read the board but can't write to it. If any of that isn't true, don't troubleshoot the user's `gh` setup mid-task. Go to "No `gh`" below.
2. Put the issue on the board and set every field in one go with `scripts/set-board-fields.sh`. It adds the issue if it isn't there yet, writes all the fields in a single call, and prints what the board now says:
   ```bash
   scripts/set-board-fields.sh <issue-number> Status="To Do" Priority=High Risk=Medium
   ```
   Use the exact option text from "Clarify missing fields" above, including its capitalization. The script refuses a value that isn't an option, and several Status options are not title-cased (`In progress`, `In review`). Add `-R owner/repo` for an issue outside YaleSites-Internal.
3. **Don't use `gh project item-edit --url` for this.** On a board this size, each call looks the item up again and is expensive. A batch of tickets (a feature with its phases, a set of sub-issues) trips GitHub's per-minute limit partway through and leaves tickets half set. The script makes about four cheap calls per ticket. For the other writes, prefer REST: `gh api -X PATCH repos/<repo>/issues/<n> -f type=Task` sets the Issue Type, and the sub-issue and blocked-by calls in `references/feature.md` are REST already.
4. If the script fails for any reason (auth, scope, a renamed option, a rate limit), don't loop on it. Go to "No `gh`" below, or wait a few minutes if the error says the rate limit was hit.
5. **Read it back.** After every field, milestone, assignee, and Issue Type write, confirm them in one query (the read-back query is in `references/board-status.md`, step 3 of "Writing"). A command that returned no error is not proof. Fix anything missing before reporting the ticket as done, and name which field it was.

**No `gh`:** create the issue through whatever works, then give the user the exact values to set on the board by hand (`Status: Backlog, Priority: Medium, Risk: Low`) with the issue link. Don't report the ticket as complete until they confirm. Mention `gh auth refresh -h github.com -s project,repo,read:org,workflow,gist` once as the durable fix (`gh auth login -h github.com -s project,repo,read:org,workflow,gist` only on a new machine or a revoked token; plain `gh auth login` resets the scopes and drops `project`). The `onboard` skill in this plugin (`/yalesites-ticket:onboard`) walks them through it.

**The Project V2 Status field isn't queryable via the REST API either.** `get_issue`, `search_issues`, and `list_issues` won't return it. If asked to audit tickets by board status without `gh`, the closest available proxy is PR review-state labels (`pass code review` / `pass functional review` / `pass design review`, `needs review`, `needs work`) on companion PRs across `yalesites-project`, `atomic`, and `component-library-twig`. That is not a direct status query.

### Writing the milestone, assignee, and `claude` label

None of these three is a Project v2 field, so none of them needs a board write. All three live on the issue itself:

```bash
gh issue edit <number> --repo yalesites-org/YaleSites-Internal --milestone "12-08-26 Feature Release"
gh issue edit <number> --repo yalesites-org/YaleSites-Internal --add-assignee dblanken-yale
gh issue edit <number> --repo yalesites-org/YaleSites-Internal --add-label claude
```

`gh issue edit --milestone` takes the milestone's **title**, matched exactly. `mcp__github__create_issue`/`update_issue` take the milestone's **number** instead, so grab it from the `gh api .../milestones` listing above rather than passing the title.

All three can also be set at creation time via `mcp__github__create_issue` (`milestone`, `assignees`, `labels`), or after the fact with `mcp__github__update_issue`. If you use `update_issue`, remember it replaces the whole label array: fetch the issue's current labels first and send the complete list, or you'll silently drop the ones already on it.

For the full board reference (reading current values, the `project` scope requirement, which step owns which lifecycle transition, and the known gaps), see `references/board-status.md`. **Only set the fields this skill is responsible for (the ones the user confirmed at creation or grooming time). Don't advance a ticket through the workflow as a side effect of grooming it.**

---

## Setting the native Issue Type

GitHub's native Issue Type field (Task, Feature, Bug, Epic, Communications, AI; it replaced the `feature`/`bug`/`task`/`epic` type labels, retired 2026-10-28) **is** settable from the CLI, and should be set on every ticket. It is not a Project v2 field, so `gh project item-edit` cannot touch it, and `mcp__github__create_issue`/`update_issue` do not expose it either.

The shortest path is REST:

```bash
gh api -X PATCH repos/yalesites-org/YaleSites-Internal/issues/<n> -f type=Bug
```

Or use the `updateIssue` GraphQL mutation, which takes an `issueTypeId`:

```bash
# 1. list the org's types and their ids (ids are stable; look them up once)
gh api graphql -f query='query{organization(login:"yalesites-org"){issueTypes(first:20){nodes{id name}}}}'

# 2. get the issue's NODE id (not its number)
ID=$(gh api graphql -f query='query{repository(owner:"yalesites-org",name:"YaleSites-Internal"){issue(number:1583){id}}}' --jq '.data.repository.issue.id')

# 3. set the type
gh api graphql -f query='mutation($id:ID!,$t:ID!){updateIssue(input:{id:$id,issueTypeId:$t}){issue{number issueType{name}}}}' -F id="$ID" -F t="<type-id>"
```

Type ids as of 2026-08-20: Task `IT_kwDOA_XQ-s4Av2Na`, Bug `IT_kwDOA_XQ-s4Av2Nd`, Feature `IT_kwDOA_XQ-s4Av2Nf`, Vendor/Supported Builds `IT_kwDOA_XQ-s4BtnpX`, Communications `IT_kwDOA_XQ-s4BwK1h`, AI `IT_kwDOA_XQ-s4BwLHQ`, Epic `IT_kwDOA_XQ-s4CE0Px`. Re-run step 1 rather than trusting this list if a type looks missing.

An older version of this skill said Issue Type had to be set manually in the UI. That was wrong, and it meant tickets created through this skill were shipping with no Type set at all.
