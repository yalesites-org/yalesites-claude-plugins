---
name: router
description: "Run the YaleSites router: hand each feature phase (UX, Design, Development, QA, Visual regression, Docs) to its next owner when the phase before it finishes, and post a brief of who owes what: open `needs-decision` and `follow-up` items grouped by person with their due dates, plus In progress tickets that have gone quiet. Built to run unattended as a weekday scheduled task; also runnable on demand. Use when the user says 'run the router', 'who owes what', 'what's waiting on me', 'what decisions are open', 'what's stuck', 'post the router brief', or asks to dry-run or debug a hand-off that didn't happen. To create the phase children or raise a follow-up in the first place, use the ticket skill."
---

# YaleSites Router

## What this is

Work gets lost at hand-offs: a phase finishes and nobody tells the next person, or a question sits on a ticket until someone happens to reread it. The router closes those gaps with plain rules, no judgment.

It does three things each run:

1. **Hands off phases.** When every blocker of a feature's phase child is Done or closed, it moves that child from `Backlog` to `To Do`, assigns the phase's default owner if nobody is assigned, and comments on the feature parent.
   - **Gated phases wait.** If the phase has a Gate in `routing.md` (today: Development and Docs, both `miketullo95`), the router does not move it. It lists it under "Waiting on a go." The gatekeeper approves by moving it to To Do, or sends it back with a `follow-up`.
2. **Lists what's owed.** Every open `needs-decision` and `follow-up` (and legacy `question`) across the YaleSites repos, grouped by the person named in its block, oldest due date first.
3. **Lists intake.** Open `forming` tickets waiting to be groomed, plus tickets filed in the last 30 days by someone who isn't a groomer that still have no Priority.
4. **Flags what's stuck.** In progress tickets with no activity for 3+ working days (20+ for Communications; epics are skipped).

Then it posts a brief to the pinned Router brief issue. On Mondays the brief opens with the meeting agenda: a count per section, linked to the Monday view on the YaleSites Board (grouped by the router-set Stage field), plus a Features in flight table (see "Monday meeting" in `routing.md`). The agenda counts leave Communications items out, since those go to the weekly comms meeting.

The rules (phases, owners, labels, block formats, and the exact list of what the router may write) live in `../ticket/references/routing.md`. Read it before changing anything here. This is v0 of the router in yalesites-org/YaleSites-Internal#1915, run as a Claude routine for now instead of a GitHub Action.

## Hard rules

- **The script decides, not you.** All routing comes from `scripts/router.py`. Don't promote, assign, relabel, or comment on anything by hand during a router run, even when it looks obviously right. If the script missed something, report it in your summary so the rules get fixed.
- **Only the writes listed in `routing.md`.** Status Backlog → To Do on a phase child, the default assignee on a child it just promoted, one parent comment per promotion, the `awaiting-go` label on gated children waiting on a go, the board's Stage field, one brief comment per run. Nothing else, ever: no closing, no PRs, no agent runs.
- **No @-mentions.** The brief writes handles in backticks. Nudging people is a human call.

## Running it

```bash
cd <this skill's directory>
python3 scripts/router.py                       # dry run: prints planned hand-offs and the brief
python3 scripts/router.py --apply               # does the hand-offs and posts the brief
python3 scripts/router.py --apply --no-brief    # hand-offs only
python3 scripts/router.py --brief-file brief.md # also saves the brief
python3 scripts/router.py --json                # machine-readable results, no writes (the work dashboard reads this)
```

Needs `gh` signed in with the `project` scope (see `../ticket/references/board-status.md`). A run takes about 15 seconds.

**On demand** ("who owes what", "run the router"): do a dry run and show the user the brief. Only add `--apply` if they ask to post it or to do the hand-offs.

**Scheduled:** run with `--apply`. Then check the output before you finish:

- Exit code 1 means a promotion did not read back as To Do. Say which one in your final message.
- If the brief lists more than 3 hand-offs in one run, say so. That usually means a batch of dependencies was wired at once, which is fine, but worth a human glance.
- Any "Phase children the router did not move" entry means a rule held something back (closed parent, open decision, unknown phase key). Name them.

Keep your final message to a few lines: hand-offs made, anything that failed, and the overdue count. The brief itself is on GitHub.

## Configuration

At the top of `scripts/router.py`:

| Setting | Value |
|---|---|
| `BRIEF_ISSUE` | The pinned Router brief issue in YaleSites-Internal. `None` prints the brief without posting |
| `WATCH_REPOS` | Repos searched for `needs-decision`, `follow-up`, and `question` |
| `STALE_WORKING_DAYS` | In progress idle threshold (3) |
| `STALE_BY_TYPE` | Per Issue Type overrides. Communications gets 20 working days, since comms work moves slower. Epics are never listed; their children carry the activity |
| `DEFAULT_BY_WORKING_DAYS` | Due date when a block has none (5 working days after the label went on) |

Phase owners are not set here. They come from the table in `routing.md`, so owners change in one place.

## When a hand-off didn't happen

Run a dry run and check, in order:

0. Is its phase gated? Then it's waiting for a go, not stuck. Check "Waiting on a go" in the brief.
1. Does the child's `<!-- yalesites:agent -->` block have a `phase:` line with a key from `routing.md`?
2. Is the child's board Status exactly `Backlog`? The router never moves anything from another status.
3. Does it have native blocked-by dependencies? A child with none is treated as parked on purpose.
4. Is every blocker closed or `Done`?
5. Is the feature parent open, and is the child free of `needs-decision` and `follow-up`?

If all five hold and it still didn't move, it's a bug in the script. Report it rather than moving the ticket by hand.

## Not in v0

These are in yalesites-org/YaleSites-Internal#1915 sections 5 and 6 and come later: the PR bounce cap and `needs help`, ready-to-merge sets, the reconcile list, the multidev cap, park timers, lane floors, and nudges.
