# Prep mode: build the review board before the reviewer sits down

`/pr-feedback --prep` does everything in a review that does not need the reviewer, ahead of
time and unattended: load or write the brief, plan the test, drive it on the multidev, and build
the review board packet. When the reviewer is ready, a normal `/pr-feedback` on the same PR finds
the packet at `SKILL.md` Step 1 and opens the board in seconds instead of spending about 20
minutes getting there.

It is built to run as a scheduled task on the reviewer's own Mac. It also runs on demand, for
example from a dashboard's "Prep board" button.

**Prep mode never posts anything to GitHub.** No review, no comment, no label, no reaction, no
edit to a PR or an issue. The only comments on a PR come from the human review that follows. The
automated `pr-prereview` pass keeps its own comment and label loop, and prep mode does not add to
it.

## What prep mode skips, and what it keeps

| Part of the review | In prep mode |
|---|---|
| Step 0, whose review this is | Kept, silently, and run once before the first claim (Step P2). The packet is scoped to the reviewer's dimensions, and that scope is recorded in the status entry and `prep.json` (Steps P2 and P4), so a review scoped differently does not reuse it |
| Step 0b, session title | Skipped |
| Step 1, the brief | Kept. No current brief means `pr-prereview {repo}#{number} --dry-run`, as Step 1 says |
| Step 2, spot-check | Kept |
| Step 3, plan and drive | Kept, with the prep-mode changes to `drive-it.md` below |
| Step 3b, the board | Packet only (Step R1). No server, no browser, no waiting for answers |
| Steps 4 to 10 | Skipped. They need the reviewer's rulings |

**No one is present.** Never use `AskUserQuestion` and never wait for input. Where a step would
ask, take the rule in this file, and if there is none, stop that PR, record why (Step P5), and
move on.

## Step P1: Build the work set

**With a PR named** (`/pr-feedback ysp#1608 --prep`), prep that PR and its siblings, as one unit.
The siblings come from `batch-mode.md` Step B1's grouping, not from the brief: parse the leading
ticket number from the PR's title and list the open PRs in the other three repos whose title
carries the same number. Those PRs are the unit, and that list is what `start` records in
Step P2.

**With no PR named,** list every open PR in the four repos, with no reviewer filter, so sibling
grouping sees a sibling the reviewer was never requested on:

```bash
gh pr list --repo yalesites-org/REPO --state open \
  --json number,title,isDraft,labels,author,headRefOid,updatedAt,url,reviewRequests
```

Then apply `batch-mode.md` Step B1 to that full list: its readiness rules (carries `needs review`,
not a draft, no `work in progress`, `don't merge`, `review in progress`, or `ready to close`, no
`MULTIDEV ONLY`, `DEMO ONLY`, or `DO NOT MERGE` title), its sibling grouping into units, and its
skip for `needs work`. Only then pick which units to start: the ones where at least one PR
lists the reviewer in `reviewRequests`. The grouping uses every PR; the reviewer filter chooses
units, never members, so a unit is never marked failed for a sibling the sweep did not see. A PR
that is mid-fix will move again, so prepping it wastes a run.

**Order the units with one sort key:** `yalesites-project` units first, because they are the ones
with a browser run to save, then newest `updatedAt` first within each group (a unit's `updatedAt`
is its newest PR's). Walk the list in that order.

**Cap each run at 3 prepped units.** A driven run takes 15 to 20 minutes, and the next scheduled
run picks up the rest. A unit the claim in Step P2 refuses does not count against the cap: move on
to the next one in the list. Which units are worth prepping is decided by that claim, not here:
do not pre-filter the list with `get`.

Call `prep_status.py run-start` once before the first unit, and `run-end` once after the last.

## Step P2: Resolve the scope, claim the unit, then brief, spot-check, plan

**Run `SKILL.md` Step 0 first, once per run, before any claim.** The claim below records the
reviewer scope, and the review session's `get` passes the scope it resolved, so the two have to
come from the same Step 0. Resolve it silently (profile, then the login map, then the unscoped
fallback), the way `batch-mode.md` Step B0 does for a batch, and use that one answer for every
unit in the run.

**Then claim the unit, with `start`.** It is the only claim there is. Do not check with `get`
and then call `start`: two runs (the schedule and a dashboard "Prep board" click) can both read
`stale` in between and both drive the same multidev, creating the same `qa-<role>` users and
removing each other's test content. `start` runs under the status file's lock and either takes
the unit or refuses, in one step. Name every PR in the unit with its head (the unit is the Step
B1 grouping from Step P1, siblings included), the reviewer scope Step 0 resolved (the
dimensions as a comma list, or `all` on the unscoped path), and the run folder:

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py start \
  --pr yalesites-project#1608=<head> --pr component-library-twig#774=<head> \
  --packet ysp-1608 --scope functional,product \
  --run-dir ~/.claude/yalesites/pr-feedback/runs/yalesites-project-1608-<yyyy-mm-dd>
```

`--run-dir` is the drive-it run folder, named the way `drive-it.md` names it
(`~/.claude/yalesites/pr-feedback/runs/<repo>-<N>-<YYYY-MM-DD>`, for the unit's
`yalesites-project` PR or its first PR). Pass it on every unit, driven or not: `plan.md` is
written there, and when a run dies mid-drive the review session reads the folder's `.created`
from the status entry to clear the multidev before it drives (`SKILL.md` Step 1).

| `start` says | What to do |
|---|---|
| `claimed: true` | Prep it. The entry is `running`, with the scope, the unit's PR list, `runDir`, and `packetDir` recorded. **Keep the `claim` token from that line for the whole unit:** `heartbeat`, `ready`, and `fail` all take it back as `--claim`, and without it they refuse. **Build the packet in the `packetDir` the line prints** (Step P4), nowhere else |
| Refused: another prep run has it | Skip the unit. The other run is driving that multidev now. `--force` does not override this one |
| Refused: the packet is current | Skip the unit. Every PR in it reads `ready` for these heads and this scope |
| Refused: already failed on these heads | Skip the unit. A failed unit is retried once per new head, not every run; a dashboard button that wants a rebuild now passes `--force` |
| Refused: `status.json` cannot be read (`written: false`) | Stop the run and say so in the digest (Step P6). The script copied the bad file to `status.json.corrupt-<timestamp>` and wrote nothing. No claim can be taken until someone fixes or removes `status.json`, so there is nothing to prep |

A refusal is exit code 2 with the reason as one JSON line on stdout. Record it in the digest
(Step P6) as skipped, with that reason.

Then run `SKILL.md` Steps 1 and 2 exactly as written, without the chat output and with one
exception: **skip Step 1's prepped-board check** (the `get` under "Start from a prepped
board"). This run holds the claim, so `get` would return the run's own `running` entry, and
that row (wait, or review now) is a question for a reviewer, not a rule for a run. The claim
above is the only status check prep mode makes. The unit is fixed at the claim: if the brief
names an open sibling the Step B1 grouping missed (a title without its ticket number, usually),
mark the unit failed with that reason (Step P5) instead of driving it, because the review
session drops a packet whose `unit` is short. Write the Step 3 test plan, beyond-AC rows
included, to `plan.md` in the run folder. The review session shows it to the reviewer, so write
it for them.

## Step P3: Drive it, under the disposable multidev rule

Driving applies to `yalesites-project` units, as in `SKILL.md` Step 3. Follow `drive-it.md`,
with these changes:

**The disposable multidev rule replaces the Step D1 ask.** A PR multidev is a disposable copy of
the platform, so prep mode has standing consent to create the Step D1 kinds on it (test pages,
reusable blocks, media and files, `qa-<role>` users, and setting changes) without asking. The
rule holds only when all of these are true:

- The environment is `yalesites-platform.pr-<N>`, the PR's own multidev. Never a visreg
  multidev (the red "DO NOT CHANGE CONTENT" banner), never `dev`, `test`, or `live`, and never
  another PR's multidev.
- Only the Step D1 kinds. Anything else a step would need is out of bounds: record the step as
  `blocked` with the reason.
- Every item goes in `.created` as it is created, and a setting's original value goes in
  **before** it changes.
- **Step D5 cleanup runs in the same run, before the unit is marked done.** Nothing prep mode
  creates is left for the reviewer to find. If an item cannot be removed, record it (Step P5,
  `--cleanup failed`) and name it in the packet's subtitle, so the review session raises it.

**Headless.** No one is watching, so open every session without `--headed`. Drop the D0 check
"this is a machine the user can see" and keep "this is the user's own machine": the run needs
Terminus, Node, and a local browser. A cloud session cannot prep.

**No browser installs.** If the D0 launch check fails, do not install anything. Record the unit
as failed with the reason and move on. The reviewer fixes it in a live session.

**Every other D0 check stays.** A missing multidev, an unauthenticated Terminus, or a server not
running the branch fails the unit with that reason. These are the same checks a live run makes,
and a prepped board built on a broken environment is worse than none.

**Show nothing, save everything.** Skip "Show the user as you go." Every screenshot still gets
looked at before it gets a result, and `results.md` is written as usual. The packet carries them
to the reviewer instead.

**Heartbeat between steps.** A `running` entry expires 90 minutes after its last stamp, and a
unit with a slow multidev, several roles, or a clip retry can run longer than that. Once it
expires, a live review reads it as `failed: interrupted` and drives the same multidev. So after
every D-step, and after each role in a multi-role run, re-stamp the unit:

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py heartbeat --packet ysp-1608 --claim <token>
```

`--claim` is required: a heartbeat without the token is refused outright, so a run that lost
its token cannot keep another run's claim alive. A run that dies stops stamping, and reads as
interrupted once the 90 minutes pass. That is the only way a dead run is ever reported, so do
not skip the heartbeat on a short unit either.

**A heartbeat that exits 1 means the claim is lost. Stop driving at once.** The entry has either
passed the TTL, in which case a review session may already have read it as interrupted and
started its own run on this multidev, or another prep run has claimed the unit under a new
token. The script never stamps an expired or reclaimed entry back to `running`. So: close the
browser, do not call `ready` or `fail` (the entry is not this run's to write, and both refuse
anyway), leave Step D5 cleanup to whoever holds the claim now (their test content shares names
with yours), and record the unit in the digest (Step P6) as lost with the script's reason.

For a unit with nothing to drive (Storybook, `atomic`, `tokens`, or a failed preflight), the
packet still gets built in Step P4, from the brief alone, and the plan in `plan.md` is the
hand-off walkthrough for the review session.

## Step P4: Build the packet

Follow `review-board.md` Step R1, with two differences:

- **Packets live with the status file, not in a session scratchpad,** because the session that
  builds them ends before the review starts, and **every build gets its own folder:** the
  `packetDir` the claim printed in Step P2, `packets/<id>-<sha7>-<builtAt>`, where `<id>` is the
  packet id, `<sha7>` the first 7 characters of the unit's first PR head, and `<builtAt>` the
  claim time in ISO basic form:

  ```
  ~/.claude/yalesites/pr-review-prep/packets/ysp-1608-4ae17e5-20261004T130500Z/
    packet.json
    prep.json
    plan.md            (copied from the run folder)
    results.md         (copied from the run folder, driven units only)
    01-fail-editor-overflow-360.png
  ```

  Use the unit's `yalesites-project` PR for the id when it has one (`ysp-1608`), or its first PR
  otherwise. Build only in that folder, and **never rename, move, or delete another one.** A
  rebuild (a new head, `--force`, or a scope change on an unchanged head) is a new claim, so it
  gets a new folder, and the older folders stay as they are: a review session that still has one
  of them open keeps serving its own files, because its symlink points at the versioned path
  (`review-board.md` Step R1); its `answers.json`, and any `answers-<timestamp>.json` a review
  archived there, stays with it as the record of that review (Step R4); and a folder a dead run
  left half-built needs no name and no tidying. The status entry's `packetDir` is the only
  pointer anyone follows, so an old folder is never mistaken for the current packet, and no old
  `answers.json` can end the next review's wait early.
- **Write `prep.json` next to `packet.json`.** It holds what the review session needs and the
  board does not show:

  ```json
  {
    "prs": { "yalesites-project#1608": "<head>", "component-library-twig#774": "<head>" },
    "scope": ["functional", "product"],
    "briefSha": "<sha the brief was written against>",
    "runDir": "~/.claude/yalesites/pr-feedback/runs/yalesites-project-1608-2026-10-04",
    "results": { "pass": 8, "fail": 1, "ask": 2, "blocked": 0 },
    "fails": ["04-fail-editor-overflow-360.png"],
    "heldCalls": [
      { "dimension": "product", "question": "Should the new field default to on for existing sites?", "onBoard": "default-on" },
      { "dimension": "code", "question": "Keep the `--variant` default on line 88, or make it explicit?", "onBoard": null, "owner": "lead developer" }
    ],
    "findingsForDev": [
      { "dimension": "functional", "file": "web/modules/custom/ys_core/src/Form/SettingsForm.php", "line": 88,
        "what": "The default is set twice", "why": "The second assignment wins silently", "blocking": false }
    ],
    "cleanup": "done",
    "builtAt": "2026-10-04T13:05:00Z"
  }
  ```

  `scope` is the reviewer scope from Step P2, as recorded in the status entry (`["all"]` on the
  unscoped path), and `runDir` is the folder the claim's `--run-dir` named. `heldCalls` and
  `findingsForDev` carry **every** item from the brief, tagged with its dimension and
  unfiltered, in the shape `batch-mode.md` Step B2 has a subagent return.
  The board holds only the in-lane questions, so this is where the review session gets the
  out-of-lane calls to name (`SKILL.md` Step 3b) and the mechanical findings for Step 4, and
  where batch mode reads them for a prepped unit instead of fanning out a subagent. `onBoard`
  is the question id when the call went on the board, and `null` when it did not.

The questions follow Step 3b's sorting: in-lane held calls and every `ask` screenshot go on the
board. `fail` results do not become questions, because a failure is a finding, not a call. Put
each `fail` on the board as context on a question only where it bears on one. The review session
shows the rest in chat.

## Step P5: Record the outcome

When a unit is done, mark every PR in it ready:

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py ready \
  --pr yalesites-project#1608=<head> --pr component-library-twig#774=<head> --packet ysp-1608 \
  --scope functional,product --claim <token> --questions 3 --driven \
  --results pass=8,fail=1,ask=2,blocked=0 --cleanup done
```

`--scope` is the same value the claim in Step P2 used, and `--claim` is the token it printed.
Leave out `--driven` when there was no browser run. When a unit stops early, mark it failed with
a reason a person can act on, in one line: "multidev pr-1605 does not exist (25/25 cap?)", "the
server runs profile 2.30.1, the branch has 2.30.3", "Chrome did not launch". The status file is
what a dashboard reads, so the reason is the whole message.

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py fail \
  --pr yalesites-project#1605=<head> --claim <token> --reason "multidev pr-1605 does not exist (25/25 cap?)"
```

**Both settle every PR that carries the claim token,** named with `--pr` or not, so a sibling
never stays `running` on its own until the TTL. Name every PR in the unit anyway, as the
examples do: a PR left out keeps the head it was claimed at. Both carry the claim's `packetDir`
and `runDir` onto the finished entry, which is how the review session finds the packet, and the
run folder's `.created` after a failure.

**Both refuse, with exit 2, when the claim is lost:** another run claimed the unit after this
one passed the TTL, so the entry carries a different token, and this run's result would overwrite
a live run's state. Treat that the way Step P3 treats a failed heartbeat: record the unit in the
digest as lost, with the script's reason, and move on. Nothing else is written.

**Check the head again before marking ready.** If a developer pushed while the unit ran, the
packet already describes the old head. Mark it ready against the head it was built from. The
status file then reports it as `stale`, and the next run rebuilds it.

## Step P6: Report the run

Write a short digest to `~/.claude/yalesites/pr-review-prep/digest/<yyyy-mm-dd>.md`, appending one
section per run: each unit with its outcome (ready with question and result counts, failed with
the reason, skipped and why), and anything cleanup could not remove. End the session with the
same summary in two or three lines. No one reads it live, so keep it short.

## In the review session

`SKILL.md` Step 1 checks the status file before anything else. When the packet is current, the
review starts at the board, and when it is not, the review runs the normal way. Prep mode only
ever saves time. A missing, stale, or failed packet never makes a review shallower.
