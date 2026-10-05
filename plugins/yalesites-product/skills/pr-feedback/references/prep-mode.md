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
| Step 0, whose review this is | Kept, silently. The packet is scoped to the reviewer's dimensions |
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

**With no PR named,** sweep every open PR in the four repos where the reviewer is a requested
reviewer:

```bash
gh pr list --repo yalesites-org/REPO --state open --search "review-requested:@me" \
  --json number,title,isDraft,labels,author,headRefOid,updatedAt,url
```

Then apply `batch-mode.md` Step B1: its readiness rules (carries `needs review`, not a draft, no
`work in progress`, `don't merge`, `review in progress`, or `ready to close`, no `MULTIDEV ONLY`,
`DEMO ONLY`, or `DO NOT MERGE` title), its sibling grouping into units, and its skip for `needs
work`. A PR that is mid-fix will move again, so prepping it wastes a run.

**Skip a unit whose packet is current.** For each PR, check the status file (Step P5):

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py get <repo>#<number> --head <headRefOid>
```

| `state` | What to do |
|---|---|
| `ready` | The packet matches the head. Skip the unit |
| `running` | Another prep run has it. Skip the unit |
| `stale`, `failed`, `none` | Prep it |

A `failed` unit is retried once per new head, not every run. If the failure was recorded against
the same head and the reason is the environment (no multidev, branch not deployed), skip it until
the head moves.

**Cap each run at 3 units**, newest `updatedAt` first. A driven run takes 15 to 20 minutes, and
the next scheduled run picks up the rest. Units on `yalesites-project` go first, because they are
the ones with a browser run to save.

Call `prep_status.py run-start` once before the first unit, and `run-end` once after the last.

## Step P2: Brief, spot-check, plan

For each unit, mark it running first, with every PR in the unit and its head:

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py start \
  --pr yalesites-project#1608=<head> --pr component-library-twig#774=<head> --packet ysp-1608
```

Then run `SKILL.md` Steps 0, 1, and 2 exactly as written, without the chat output. Write the
Step 3 test plan, beyond-AC rows included, to `plan.md` in the run folder. The review session
shows it to the reviewer, so write it for them.

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

For a unit with nothing to drive (Storybook, `atomic`, `tokens`, or a failed preflight), the
packet still gets built in Step P4, from the brief alone, and the plan in `plan.md` is the
hand-off walkthrough for the review session.

## Step P4: Build the packet

Follow `review-board.md` Step R1, with two differences:

- **Packets live with the status file, not in a session scratchpad,** because the session that
  builds them ends before the review starts:

  ```
  ~/.claude/yalesites/pr-review-prep/packets/<id>/
    packet.json
    prep.json
    plan.md            (copied from the run folder)
    results.md         (copied from the run folder, driven units only)
    01-fail-editor-overflow-360.png
  ```

  Use the unit's `yalesites-project` PR for the id when it has one (`ysp-1608`), or its first PR
  otherwise. Replace the folder if one exists, so no `answers.json` from an earlier head survives.
- **Write `prep.json` next to `packet.json`.** It holds what the review session needs and the
  board does not show:

  ```json
  {
    "prs": { "yalesites-project#1608": "<head>", "component-library-twig#774": "<head>" },
    "briefSha": "<sha the brief was written against>",
    "runDir": "~/.claude/yalesites/pr-feedback/runs/yalesites-project-1608-2026-10-04",
    "results": { "pass": 8, "fail": 1, "ask": 2, "blocked": 0 },
    "fails": ["04-fail-editor-overflow-360.png"],
    "outOfLane": ["The `--variant` default on line 88 is a code call, for our lead developer."],
    "cleanup": "done",
    "builtAt": "2026-10-04T13:05:00Z"
  }
  ```

The questions follow Step 3b's sorting: in-lane held calls and every `ask` screenshot go on the
board. `fail` results do not become questions, because a failure is a finding, not a call. Put
each `fail` on the board as context on a question only where it bears on one. The review session
shows the rest in chat.

## Step P5: Record the outcome

When a unit is done, mark every PR in it ready:

```bash
python3 <skill-dir>/scripts/review-prep/prep_status.py ready \
  --pr yalesites-project#1608=<head> --pr component-library-twig#774=<head> --packet ysp-1608 \
  --questions 3 --driven --results pass=8,fail=1,ask=2,blocked=0 --cleanup done
```

Leave out `--driven` when there was no browser run. When a unit stops early, mark it failed with
a reason a person can act on, in one line: "multidev pr-1605 does not exist (25/25 cap?)", "the
server runs profile 2.30.1, the branch has 2.30.3", "Chrome did not launch". The status file is
what a dashboard reads, so the reason is the whole message.

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
