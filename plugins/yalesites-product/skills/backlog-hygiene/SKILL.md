---
name: backlog-hygiene
description: "Audit the YaleSites backlog for tickets that don't meet the team's ticket standards and report what needs attention. Read-only: it never edits, closes, or relabels anything. Use when the user asks to check, audit, sweep, review, or clean up the backlog, wants to know which tickets need grooming before a sprint or grooming session, asks 'what's rotting in the backlog', or wants a recurring hygiene pass. Also the skill a scheduled Cowork task should invoke to produce a periodic backlog report. Findings hand off to the `ticket` skill for the actual grooming."
---

# YaleSites Backlog Hygiene

## What this skill is for

Not every YaleSites ticket is written through the `ticket` skill. People file issues directly in GitHub, from a meeting, or in a hurry. Those tickets are legitimate work but often don't carry the fields the team's process expects: acceptance criteria, Priority, Size, a Status on the board, a descriptive title.

This skill finds those tickets and reports them. It does **not** fix them.

## Hard rule: this skill is read-only

**Never edit, close, relabel, reassign, or move a ticket from this skill.** Not even an obviously-correct fix, not even when asked mid-run to "just fix that one."

The reason is trust. This runs across hundreds of tickets other people wrote, potentially unattended on a schedule. A pass that silently rewrites other people's tickets produces a backlog nobody believes. Report, hand off, let a human decide.

If the user wants a finding acted on, that's the `ticket` skill's job, run deliberately on a named ticket. Point them there and stop.

The only write this skill may ever make is posting its own summary as a new issue or comment, and only when the user explicitly asks for that in the current session.

---

## Step 1: Pull the data in bulk

The backlog is large (roughly 460 open issues, 500 board items as of this writing). **Do not fetch bodies for every ticket.** Two bulk metadata calls first, bodies only for a bounded candidate set later.

```bash
# Open issues, metadata only (no body), including the native Issue Type
gh api graphql --paginate -f query='query($endCursor:String) {
  repository(owner:"yalesites-org", name:"YaleSites-Internal") {
    issues(first:100, states:OPEN, after:$endCursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title createdAt updatedAt
        issueType { name }
        assignees(first:5) { nodes { login } }
        labels(first:20) { nodes { name } }
      }
    }
  }
}' --jq '.data.repository.issues.nodes[]'
```

**Use GraphQL rather than `gh issue list` here.** The team classifies tickets with GitHub's **native Issue Type** field, which `gh issue list --json` does not expose. Getting this wrong matters: type *labels* are only on about a third of the backlog, so checking labels would flag ~300 tickets as untyped when the actual number missing a native type is around 60.

```bash
# Board fields for every item, bodies stripped
gh project item-list 6 --owner yalesites-org --format json --limit 1000 \
  --jq '[.items[] | select(.content.type=="Issue") | {num: .content.number, repo: .content.repository, title, status, priority, size, labels, assignees}]'
```

Board items expose `status`, `priority`, and `size` at the top level. An unset field is absent or `null`. Note the board also contains closed issues and items from other repos, so filter to open `YaleSites-Internal` issues before comparing.

Join the two lists on issue number. An open issue with no matching board item is **not on the board at all**, which is its own finding.

If `gh` isn't available or lacks the `project` scope, say so and stop. See the `ticket` skill's `references/board-status.md` for the scope requirement. Don't fall back to per-issue MCP calls across a 460-ticket backlog.

---

## Step 2: Cheap checks (metadata only)

Run these across every open ticket. No bodies needed.

**Board field gaps**
- Not on the board at all. Worth keeping as a check, but expect it to be empty most runs; issues are added to the board reliably. If this suddenly returns a batch, something upstream broke.
- No Status. This is the common one, on the order of 50 tickets.
- No Priority
- No Size

**Status contradicted by reality**
- Status is `Done` but the issue is still open
- Status is `In progress` or `In review` with no assignee
- Status is `Backlog` or `To Do` but the ticket has an open PR against it
- Status is `In review` but every linked PR is merged or closed

**Classification gaps**
- **No native Issue Type set** (`issueType` is null). This is the one that matters; the team's types are `Feature`, `Bug`, `Task`, `Communications`, `AI`, `Vendor/Supported Builds`, and `Epic`.
- **Native Issue Type contradicts a type label**, for example native type `Feature` on a ticket labelled `task`. Report the conflict, don't pick a winner. Roughly a third of tickets carrying both disagree, so this is a real class, not an edge case.
- Title starts with `Epic:` but the `epic` label and native `Epic` type are both missing, or vice versa

**Leftover trigger labels**
- Any `status:*`, `priority:*`, or `size:*` label still present. These are meant to be consumed and deleted by a GitHub Action after it writes the board field. A surviving label means the Action didn't fire or didn't clean up, and the board field may never have been set. Small in number but worth surfacing, since it's a silent failure of the fallback path documented in the `ticket` skill's `references/board-status.md`.

**Age signals**
- Open more than 6 months with no update and still in `Backlog`
- Created more than 12 months ago, any status

---

## Step 3: Deep checks on a bounded candidate set

Only now fetch bodies, and only for tickets that failed a Step 2 check or look thin. **Cap this at about 40 tickets per run**, prioritizing tickets that are closest to being worked (`Ready For Work`, `To Do`) over ones buried in `Backlog`. Say in the report how many you examined and how many you skipped.

```bash
gh issue view NNNN --repo yalesites-org/YaleSites-Internal --json number,title,body,labels
```

Against the `ticket` skill's Issue Format, check:

- **Description missing or too thin to act on.** A one-line title restatement is not a description.
- **No acceptance criteria**, or a criteria section that's empty or a single vague bullet.
- **Vague title.** "Fix embed bug" or "Update Layout Builder" name a category, not the work. Suggest a concrete replacement drawn from the body.
- **Missing title prefix** where one clearly applies (`RC:`, `Bug:`, `Docs:`, `Embed:`, and so on). Don't invent a prefix for a ticket that doesn't match a known pattern.
- **Epic without child tickets** referenced in the body.
- **Unresolved debate** left in comments without a decision captured in the criteria.

For any ticket that changes user-facing behavior, also note if it has **no UX consideration at all** in the criteria. Don't attempt the full archetype analysis here; that's Step 1b of the `ticket` skill when the ticket actually gets groomed.

---

## Step 4: Safety cross-checks before recommending anything destructive

These exist because each has burned a backlog sweep before. Run them before any finding that implies closing or reassigning.

- **Never recommend closing a ticket without checking for PRs, merged as well as open.** A ticket can look abandoned while its PR merged and simply never closed the issue. The team's PR body format uses `References`, not a closing keyword, so merges do not auto-close issues and this case is common rather than rare.
- **Never call a ticket "available" from the absence of an assignment label alone.** Confirm there's no assignee and no in-progress signal. A ticket can look free on one signal and be actively claimed.
- **Check for existing duplicates before flagging something as a gap** rather than after.

Cross-repo PR check for a ticket:

```bash
gh search prs --owner yalesites-org "NNNN" --limit 20 \
  --json number,title,state,repository,url
```

**Omit `--state` deliberately.** It only accepts `open` or `closed`, and neither surfaces merged PRs as such. With the flag omitted, results include `state: "merged"`, which is the case this check exists to catch. Searching the whole org in one call also covers `yalesites-project`, `atomic`, and `component-library-twig` at once, since the work for a `YaleSites-Internal` ticket lives in whichever of those it touches.

---

## Step 5: Report

Group by what the reader should do, not by which check fired. Lead with the count, then the tickets.

Suggested structure:

```markdown
# Backlog Hygiene Report — <date>

Scanned <N> open issues, <M> board items. Examined <K> ticket bodies in detail.

## Ready to groom (highest value)
Tickets close to being worked that are missing what a developer needs.
| Ticket | Title | What's missing |

## Not on the board
Open issues with no board item. These are invisible to sprint planning.
| Ticket | Title | Created |

## Missing board fields
| Ticket | Status | Missing |

## Status looks wrong
Board status contradicted by PR or assignee reality. Verify before changing.
| Ticket | Board says | Reality |

## Type classification
Missing native Issue Type, or native type conflicting with a type label.
| Ticket | Native type | Type label | Issue |

## Leftover trigger labels
`status:`/`priority:`/`size:` labels the sync Action should have consumed and deleted.
The board field may never have been written.
| Ticket | Label(s) still present |

## Possibly stale
Open 6+ months, no recent activity, still in Backlog. Not a close recommendation.
| Ticket | Title | Last update |

## Possible duplicates
| Tickets | Overlap |

## Skipped
<count> tickets not examined in detail this run, and why.
```

Link every ticket as a full URL so it's clickable.

When running interactively and the report is long, offer to publish it as an artifact. When running as a scheduled task, output the markdown directly.

---

## Noise control

A report that flags 400 tickets gets ignored. Be deliberately conservative:

- **Skip tickets updated in the last 14 days.** They're likely in flight.
- **Skip quality nits on tickets already `In progress` or `In review`.** Too late to be useful, and the developer already has context.
- **Don't flag missing Size or Priority on `Backlog` tickets** unless the user asked for a full audit. Those get set when work is queued, and flagging all of them buries the real findings.
- **Cap each section at 15 tickets**, ordered by how actionable they are, and give the total count so nothing looks hidden.
- **Don't flag intentional patterns as problems.** Placeholder epics, tracking tickets, and long-lived `Blocked` items are often deliberate. If a ticket looks odd but has recent human comments explaining why, leave it alone.

If a run produces almost nothing, say so plainly. "Backlog is in good shape, 3 items worth a look" is a useful result, not a failed run.

---

## Handoff

End the report with the next action, not a list of everything wrong. Something like:

> The 6 tickets under "Ready to groom" are the highest-value fixes. Want me to run `/ticket` against them one at a time?

Grooming happens through the `ticket` skill, one ticket at a time, with the user confirming Status, Priority, and Size. **Don't batch-groom from a hygiene report**, and don't carry findings straight into edits without the user picking them.

---

## Running on a schedule

This skill is safe to run unattended because it's read-only. For a recurring Cowork task:

- Weekly or biweekly is enough. The backlog doesn't rot fast, and a daily report trains people to ignore it.
- It holds no state between runs, so the same finding reappears until someone acts on it. That's intentional. If the repetition gets noisy, scope a run to tickets created or updated since a given date rather than trying to track what was already reported.
- A good default scheduled scope is tickets in `Ready For Work` and `To Do`, which is where bad tickets actually cost the team time, rather than the whole backlog.
