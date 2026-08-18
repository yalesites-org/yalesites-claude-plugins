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
| `Ready For Work` | Work that is up next |
| `To Do` | This is ready to be picked up |
| `Blocked` | Work is blocked and cannot move forward |
| `In progress` | This is actively being worked on |
| `In review` | This item is in review |
| `Ready for Release (in dev)` | This work is done, but has not been released yet |
| `Done` | This has been completed |

Two easily-confused pairs:

- **`Ready For Work` vs `To Do`.** Both are pre-start. `Ready For Work` means queued as up-next; `To Do` means cleared for someone to pick up now. If the distinction matters and the user hasn't said which, ask.
- **`Ready for Release (in dev)` vs `Done`.** Work merged to `develop` but not yet shipped is `Ready for Release (in dev)`. It only becomes `Done` once released.

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

If `gh` is unavailable or unauthorized, **do not troubleshoot the user's setup mid-task.** Use the label fallback at the bottom of this file and tell them what was missing.

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

**On failure, don't retry.** Any error (auth, scope, renamed option, issue not on the board) means fall back to labels and tell the user `gh` wasn't usable. A retry loop against a permissions problem just burns turns.

---

## Lifecycle: who sets what, and when

The board is only as accurate as the transitions we actually perform. Ownership is split between skills and GitHub Actions in `yalesites-org/YaleSites-Internal/.github/workflows/`.

| Transition | Trigger | Owner | State |
|---|---|---|---|
| Ticket created or groomed | PM sets Status/Priority/Size | `ticket` skill | Working |
| Work starts → `In progress` | Dev picks up the ticket | *(nothing)* | **Genuine gap** |
| PR opened → `In review` | PR(s) created for the issue | `yalesites-pr` skill | Working |
| PR reviewed | Approve or request changes | `pr-feedback` skill | Labels only, board untouched by design |
| Merged to `develop` → `Ready for Release (in dev)` | PR merges | Workflow `02-pr-status-monitor` | **Built but dormant** |
| Merged to `master` → `Done` | RC released | Workflow `02-pr-status-monitor` | **Built but dormant** |
| Status set to `Done` → issue closed | Board change | Workflow `06-close-issue-when-done` | Working |
| Trigger label → board field | Label applied | Workflow `07-label-to-project-fields` | Working |

**Workflow 02 is written correctly but has never fired on real work.** It last ran 2026-01-06. Two independent causes, either fatal on its own:

1. **Wrong repo for the trigger.** It uses `on: pull_request` but lives in `YaleSites-Internal`, while the actual PRs are in `yalesites-project`, `atomic`, and `component-library-twig`. A `pull_request` event only fires in the repo containing the PR, so it never sees them.
2. **Inverted dry-run default.** `const dryRun = '${{ github.event.inputs.dry_run }}' !== 'false'` evaluates to `true` on any non-`workflow_dispatch` event, because `inputs` doesn't exist there and the expression renders as `''`. Every automatic run would make no changes even if it fired.

Workflows `03-pr-link-creator` and `04-release-test-extractor` are dormant for the same reasons.

**Practical consequence:** treat `Ready for Release (in dev)` and `Done` as **not reliably set** until workflow 02 is fixed. This is why `release-prep` infers release-readiness from the confirmed PR list rather than querying board Status.

**Do not invent transitions.** If a skill's own instructions don't tell you to move a ticket, don't move it. Changing board state out from under a developer is worse than a stale board.

---

## Fallback: trigger labels

For sessions without a usable `gh`, including Cowork sessions that have the GitHub connector but no CLI.

Apply the matching `status:*` / `priority:*` / `size:*` label via `mcp__github__update_issue` (for example `status:ready-for-work`, `priority:high`, `size:m`). A GitHub Action reads the label, writes the corresponding Projects v2 field, and then deletes the label.

Two consequences:

- The label **will not persist**, so it can't be used later to check what the value was.
- The write is **asynchronous**. Don't read the field back immediately and conclude it failed.

`mcp__github__update_issue` takes a **full replacement array** for `labels`. Fetch the issue's current labels first and compute the complete new list, or the update will wipe every other label on the issue.
