# YaleSites Board: Status, Priority, and Size

**Canonical reference for reading and writing YaleSites Board fields.** If any skill's inline copy of this information disagrees with this file, this file wins.

Used by `ticket` and `release-prep` (yalesites-product) and `yalesites-pr` (yalesites-dev). Keep the mechanics here rather than restating them per skill, so the three don't drift apart.

---

## The board

| | |
|---|---|
| Org | `yalesites-org` |
| Project number | `6` |
| Project name | YaleSites Board |
| Issues repo | `yalesites-org/YaleSites-Internal` |

Status, Priority, and Size are **GitHub Projects v2 single-select fields**. They are not issue fields, not labels, and **not reachable through the REST API**, which is why `mcp__github__create_issue`, `update_issue`, `get_issue`, `search_issues`, and `list_issues` can neither read nor write them.

Projects v2 is GraphQL-only. The `gh` CLI's `gh project` subcommands wrap that GraphQL, which is the shortest path to both reads and writes.

---

## Field options

### Status

In board order. **Capitalization matters:** `--value` is matched against the configured option text, and several options are not title-cased.

| Status | Meaning |
|--------|---------|
| `Backlog` | This item hasn't been started |
| `To Do` | This is ready to be picked up |
| `Blocked` | Work is blocked and cannot move forward |
| `In progress` | This is actively being worked on |
| `In review` | This item is in review |
| `Done` | Merged to `develop`, or a hotfix merged to `master`. Stays open until the release ships |

**`Done` is not closed.** A ticket moves to `Done` when its work merges. It stays open, and visible on the Board view, until `release-prep` Phase 7 confirms the release shipped and closes it. The milestone says which release that is.

**Retired statuses.** `Ready for Release (in dev)` was retired on 2026-09-23 (YaleSites-Internal#1778), because milestones now mark the release. `Ready For Work` is not a board status either. It survives only as a catch-all *milestone* name. Setting either as a Status fails.

There is **no `Forming` status.** Older skill text listed one. If you see `forming` referenced, it is a label or an informal signal, not a board Status.

### Priority

`Hotfix` · `High` · `Medium` · `Low`

### Size

`XS` · `S` · `M` · `L` · `XL`

---

## Prerequisites

`gh` must be installed, authenticated, and hold the **`project` scope**. `read:project` alone can read the board but **cannot write to it**.

```bash
gh auth status
```

If the scope is missing, the user can add it themselves (this is an interactive browser flow, so it cannot be run unattended):

```bash
gh auth refresh -h github.com -s project
```

If `gh` is unavailable or unauthorized, **do not troubleshoot the user's setup mid-task**, and do not reach for labels. Finish the parts that don't need the board, then hand the user the exact field values to set by hand, per "No `gh`: hand the fields to the user" at the bottom of this file.

---

## Reading

Confirm the current option lists (do this rather than trusting any inline copy, if there's reason to think the board changed):

```bash
gh project field-list 6 --owner yalesites-org
```

Read one issue's current field values:

```bash
gh project item-list 6 --owner yalesites-org --format json --limit 500
```

`item-list` returns every item, so filter client-side by issue URL or number. For a single issue, GraphQL is more direct:

```bash
gh api graphql -f query='query { repository(owner:"yalesites-org", name:"YaleSites-Internal") { issue(number:NNN) { projectItems(first:10) { nodes { project { number } fieldValueByName(name:"Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } } } } } } }'
```

---

## Writing

Two steps. Both are safe to repeat.

**1. Make sure the issue is on the board.** No-op if it's already there.

```bash
gh project item-add 6 --owner yalesites-org --url <issue-url>
```

**2. Set the field by name.** No field or option ID lookup needed.

```bash
gh project item-edit 6 --owner yalesites-org --url <issue-url> --field "Status" --value "In review"
gh project item-edit 6 --owner yalesites-org --url <issue-url> --field "Priority" --value "High"
gh project item-edit 6 --owner yalesites-org --url <issue-url> --field "Size" --value "M"
```

Only one field per invocation for non-draft issues. Run the command once per field.

**Read before you write when the transition is conditional.** If the rule is "move to X only if it isn't already X," check current status first rather than writing unconditionally, so the board's updated timestamp and activity feed stay meaningful.

**On failure, don't retry.** Any error (auth, scope, renamed option, issue not on the board) means stop writing, tell the user `gh` wasn't usable, and hand them the values to set by hand. A retry loop against a permissions problem just burns turns.

**3. Read it back.** A write that returned no error is not proof the field is set. Confirm every field you wrote, in one query:

```bash
gh api graphql -f query='query($n:Int!){repository(owner:"yalesites-org",name:"YaleSites-Internal"){issue(number:$n){issueType{name} milestone{title} assignees(first:5){nodes{login}} projectItems(first:5){nodes{project{number} fieldValues(first:20){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2FieldCommon{name}}}}}}}}}}' -F n=<number>
```

Anything missing or wrong gets fixed before the ticket is reported as done. Say which field it was.

---

## Lifecycle: who sets what, and when

The board is only as accurate as the transitions we actually perform. Ownership is split between skills and GitHub Actions in `yalesites-org/YaleSites-Internal/.github/workflows/`.

| Transition | Trigger | Owner | State |
|---|---|---|---|
| Ticket created or groomed | PM sets Status/Priority/Size | `ticket` skill | Working |
| Work starts → `In progress` | Dev picks up the ticket | *(nothing)* | **Genuine gap** |
| PR opened → `In review` | PR(s) created for the issue | `yalesites-pr` skill | Working |
| PR reviewed | Approve or request changes | `pr-feedback` skill | Labels only, board untouched by design |
| PR merged → PR's own card to `Done` | PR merges | Board workflow "Pull request merged" | Working. Moves the PR card only, not the linked ticket |
| Merged to `develop` → ticket to `Done` | PR merges | Workflow `02-pr-status-monitor` | **Built but dormant** (see YaleSites-Internal#1385) |
| Release ships → ticket closed | Release merged to `master` | `release-prep` Phase 7 | Working |
| Status set to `Done` → issue closed | Board change | Workflow `06-close-issue-when-done` | **Dormant** (see `release-prep` Phase 7). Must stay that way |
| Status set to `Done` → issue closed | Board change | Board workflow "Auto-close issue" | **Off by design** since 2026-09-23. Turning it on closes tickets before they ship |
| Trigger label → board field | Label applied | Workflow `07-label-to-project-fields` | **Not used by any skill.** See "Why there is no label fallback" below |

**Workflow 02 is written correctly but has never fired on real work.** It last ran 2026-01-06. Two independent causes, either fatal on its own:

1. **Wrong repo for the trigger.** It uses `on: pull_request` but lives in `YaleSites-Internal`, while the actual PRs are in `yalesites-project`, `atomic`, and `component-library-twig`. A `pull_request` event only fires in the repo containing the PR, so it never sees them.
2. **Inverted dry-run default.** `const dryRun = '${{ github.event.inputs.dry_run }}' !== 'false'` evaluates to `true` on any non-`workflow_dispatch` event, because `inputs` doesn't exist there and the expression renders as `''`. Every automatic run would make no changes even if it fired.

Workflows `03-pr-link-creator` and `04-release-test-extractor` are dormant for the same reasons.

**Practical consequence:** treat `Done` as **not reliably set** until workflow 02 is fixed, since tickets reach it by hand. This is why `release-prep` infers release-readiness from the confirmed PR list rather than querying board Status.

**Closing a ticket at merge time undoes the model.** A closed ticket drops off the Board view, which filters on `state:open`, before its release ships. Leave merged tickets open in `Done` and let Phase 7 close them.

**Do not invent transitions.** If a skill's own instructions don't tell you to move a ticket, don't move it. Changing board state out from under a developer is worse than a stale board.

---

## No `gh`: hand the fields to the user

Skills write Status, Priority, and Size **only** with `gh project item-edit`. There is no label fallback.

When `gh` is missing, unauthenticated, or lacks the `project` scope:

1. Create or update the issue itself through whatever path works (the GitHub connector can create issues, set the milestone, assignees, and labels).
2. Tell the user, in one short block, the exact values to set on the YaleSites Board, with the issue link. For example: `Status: Backlog, Priority: Medium, Size: XS`.
3. Mention `gh auth login` plus `gh auth refresh -h github.com -s project` as the durable fix, once.
4. Do not report the ticket as complete until the user confirms the fields are set, or says they will do it.

### Why there is no label fallback

Older versions of this skill applied `status:*` / `priority:*` / `size:*` labels and relied on workflow `07-label-to-project-fields` to copy them onto the board. That never worked for skill-created tickets. The workflow's mappings expect a space after the colon (`priority: medium`), and the repo's labels have none (`priority:medium`). The workflow logged "No label mappings matched" and left both the label and an empty board field behind. On 2026-10-05, about 30 open tickets were carrying these labels with no matching board field.

**Never apply these labels.** A `priority:*`, `size:*`, or `status:*` label on a ticket is a sign the board field was never set. `backlog-hygiene` reports them for that reason.
