# Starting from a prepped board (Step 1 detail)

Read this from `SKILL.md` Step 1 when `prep_status.py get` returns anything other than `none`.
It covers how to check a whole unit, what each state means, and clearing what a prep run left on
the multidev.

### Start from a prepped board

Prep mode (`prep-mode.md`) may already have done Steps 1 to 3 for this PR, including
the driven run. Check before loading anything else, with the head from step 1 and the scope
Step 0 resolved (the reviewer's dimensions as a comma list, or `all` on the unscoped path):

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py get REPO#NUMBER --head <headRefOid> --scope functional,product
```

**Check the whole unit, not only this PR.** The entry's `unit` field lists every PR the packet
was built for: prep mode groups siblings the way `batch-mode.md` Step B1 does, every
open PR whose title carries the same leading ticket number, and records that list when it claims
the unit. For each sibling in `unit`, get its `headRefOid` with the same `gh pr view` as step 1
and run `get` on it too, with the same `--scope`. The unit is prepped only when **every** PR in
it reads `ready`. When any sibling reads anything else, take that row below for the whole unit:
the packet's plan, driven results, and questions describe the unit at the heads it was prepped
at, and a sibling that moved makes them describe old code. If the brief, read on the `ready`
path, names a sibling that `unit` does not list, the unit grew after the prep, or a sibling's
title is missing its ticket number, so run the review the normal way.

| `state` | What to do |
|---|---|
| `ready` | **Start from the packet.** Read `prep.json` and `plan.md` in its `packetDir` (a versioned folder, `packets/<id>-<sha7>-<builtAt>`; take the path from the entry, never build it from the id), and the brief its `briefSha` names. Tell the reviewer in two or three lines when it was prepped, the driven result counts, and how many questions the board holds. Show every `fail` screenshot from `prep.json` in chat, failures first, as `drive-it.md` does live. Then skip to Step 3b and open the board on the prepped packet. Steps 2 and 3 are done. If the reviewer already answered this packet in a dashboard (`review-board.md` Step R1, "Answered already"), do not open the board: go to Step 3b and use those answers in place of the board. Only the board is skipped: still run "Before asking anything, check what's already open" and turn any `defer` answer into a `needs-decision` block per "Open calls go on the record" |
| `running` | A prep run is working on it now. Say so, and offer to wait for it or to review now. Never drive the same multidev from two sessions at once |
| `stale` | The developer pushed after the prep, or the packet was built for a different reviewer scope: `reason` says which. Say so, then run the review the normal way. The old packet is not reused. If `previousState` is `running`, a prep run is still driving the old head on this multidev: wait for it to finish, or for its 90-minute TTL, before any browser run of your own |
| `failed` | Say the recorded reason in one line, then run the review the normal way, **after clearing what the prep run left on the multidev** (below). An `interrupted` reason means the run died before its own cleanup and never wrote `prep.json`. A failure from the environment (no multidev, branch not deployed) usually fails the live run too, so check it first. A failure is only reported against the head it was recorded on; after a push it reads as `stale` |
| `unreadable` | `status.json` is corrupt. Say so in one line, with the script's `reason`, then run the review the normal way. No prep run can write until someone fixes or removes the file; the next one that tries copies it aside as `status.json.corrupt-<timestamp>` and stops |
| `none`, or the script is missing | Run the review the normal way, without comment |

**Clear what a prep run left before any live drive.** Whenever the entry reads `failed`, or
`stale` with a `previousState` of `running` or `failed`, and carries a `runDir`, read `.created`
in that folder (the prep run's drive-it folder) and run `drive-it.md` Step D5 on every line
that is still on the multidev, before Step 3 drives anything. An interrupted run never reached
D5, and a push does not clear a multidev's content, so its `qa-<role>` users and test pages are
still there and would collide with the live run's. D5 checks each item before removing it, so
running it over a list a finished run already cleaned costs nothing. If `prep.json` says
cleanup failed, name the items still on the multidev before anything else: they were left by
the prep run and need removing the same way.

On the `ready` path, the review still owes everything after Step 3b: the reviewer's rulings,
which the board's last page gives per PR, and Steps 4 to 10. A prepped board saves the wait,
not the review.
