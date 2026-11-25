---
name: yalesites-pr-feedback
description: "The human half of YaleSites PR review, and the only way a PR reaches an approved state. Use whenever the user asks to review, look at, check, approve, or give feedback on a PR, even without the words 'PR feedback', e.g. 'can you check PR 1288', 'review this PR', 'is this one ready to merge', 'approve #452'. Covers yalesites-project, component-library-twig, atomic, tokens, and yale-ui-cl (UICL). Starts from a local pre-review brief, walks the user through what to test and where, drives the test in a visible browser on multidevs and UICL Storybook with a screenshot per result, settles the held product calls on a review board, then posts the review with the right approval state and labels. Also batches several PRs or the whole queue ('review 1560, 1572 and clt 728', 'go through my review queue'). With --prep it runs unattended and leaves a review board packet, posting nothing."
argument-hint: "[repo#number, or several for batch mode, or nothing to sweep the review queue] [--as code|functional|design|a11y|product] [--prep]"
---

# YaleSites PR Feedback Skill

This skill is the **human half** of YaleSites PR review. A brief, written ahead of time or at the
start of the run, has already read the diff, mapped it to the ticket, and listed the calls a human
must make. This skill puts eyes on the running thing, gets the reviewer's calls, and posts a real
review with an approval state and labels. **Nothing reaches an approved state without going
through here.**

Order of work: whose review this is, load the brief, spot-check it, test, get the calls, then
post. Do not repeat the diff deep-dive. Re-deriving the brief is the main waste to avoid.

**Repos in scope:** `yalesites-org/yalesites-project`, `component-library-twig`, `atomic`,
`tokens`, `yale-ui-cl` (UICL). **Issues live in** `yalesites-org/YaleSites-Internal` (a UICL PR's
issue lives in `yale-ui-cl`). If the user gives a bare PR number with no repo, ask, or read the
URL they pasted. Do not guess.

## Load only what the step needs

All paths are relative to this skill's folder. Read a reference when you reach its step, not
before.

| When | Read |
|---|---|
| Start of every run | `references/config.md` (the optional per-person config file) |
| Two or more PRs, or the whole queue | `references/batch-mode.md`, and follow it instead of the steps below |
| `--prep` | `references/prep-mode.md`, and follow it instead of the steps below |
| Step 0, scoping detail and `--as` | `references/scoping.md`, `references/reviewer-roles.md` |
| Step 1, brief file format and freshness | `references/brief-format.md` |
| Step 1, a prepped packet exists | `references/prepped-board.md` |
| Step 3, the test plan | `references/test-plan.md`, `references/beyond-ac-checks.md`, `references/preview-environments.md` |
| Step 3, driving the browser (yalesites-project, yale-ui-cl) | `references/drive-it.md` |
| Step 3b, held calls and open decisions | `references/held-calls.md` |
| Step 3b, the review board | `references/review-board.md` |
| Steps 4 and 5, writing the body | `references/composing-feedback.md`, `references/github-writing.md`, `references/github-communication-format.md` |
| Steps 6 to 9, review event, labels, posting | `references/posting.md` |

---

## Step 0: Work out whose review this is

Do this first. It decides which calls go to the reviewer, what the review may claim, and which
`pass ___ review` label it may apply. Stop at the first hit:

1. **The reviewer's profile:** `cat ~/.claude/yalesites/pr-feedback/reviewer-profile.md`
2. **The shared login map:** the reviewer login (`reviewer_login` in config, default
   `gh api user --jq .login`) looked up in `references/reviewer-roles.md`
3. **No match:** today's full behavior, ungated

**An unmatched reviewer gets the full, ungated review. This does not bend.** Scoping may sharpen
a review for someone it knows. It may never make one smaller for someone it does not. A missing
profile, or `gh` not logged in, is a normal state.

**Say which way it went, once, in chat, before Step 1.** On the unmatched path, offer
`/reviewer-profile` once and then drop it. `--as <dims>` scopes one run to the named dimensions,
overriding the profile; say it is active. `--as` with no dimension or an unknown one is a
question, not a guess. Wording, the effects table, and the full rules are in
`references/scoping.md`.

## Step 0b: Title the session

Before Step 1, call `mcp__ccd_session_mgmt__set_session_title` once:

| Scope | Title |
|---|---|
| One PR | `PR review: yalesites-project #1560` |
| Named batch | `PR review: 1560, 1572, CLT 728` |
| Queue-wide sweep | `PR review queue: 2026-09-22 (5 PRs)` |

Bare numbers mean `yalesites-project`; name other repos (`CLT 728`, `atomic 521`, `tokens 94`,
`UICL 57`). A queue sweep is titled after batch Step B1 confirms the work set. Past three PRs,
name two and add `+N more`. Title once; never retitle or append outcomes. If the tool is not
available (CLI), skip this silently.

## Step 1: Load the pre-review brief

1. Get the PR's head and basics:
   ```
   gh pr view NUMBER --repo yalesites-org/REPO \
     --json title,url,headRefOid,author,assignees,labels,isDraft
   ```
2. **Check for a prepped board first:**
   ```bash
   python3 <skill-dir>/scripts/review-prep/prep_status.py get REPO#NUMBER --head <headRefOid> --scope <dims or all>
   ```
   `none`, or no script: carry on without comment. Any other state: read
   `references/prepped-board.md` and follow it. A `ready` unit (every sibling `ready`) covers
   this step, Step 2, and the browser run in Step 3. A `failed` or abandoned prep run must have
   its leftovers cleared before any live drive.
3. **Get the brief, in this order.** The file format, location, and freshness test are in
   `references/brief-format.md`.

| Order | Source | When |
|---|---|---|
| a | **A brief on disk** for this PR, current for the head SHA | Use it. Skip Step 2's diff read. The normal path |
| a2 | A brief on disk, behind the head | Use it for context, read only the newer commits (`gh pr diff`), and tell the user which parts may be stale |
| b | **The override skill** named by `brief_skill` in config, if set and installed | Invoke `/<brief_skill> <repo>#<number> --dry-run`. It writes the brief and posts nothing |
| c | **`pr-brief`** (this plugin) | No brief and no override. Invoke `/pr-brief <repo>#<number>`. A normal, fully working path |

If `brief_skill` is set but not installed, say so in one line and use `pr-brief`. On
`yalesites-project` and `yale-ui-cl`, start the Step 3 browser setup while the brief is written.

**The brief is local and stays local.** Nothing from its **Your calls** or **Not checked here**
sections goes onto GitHub word for word. What goes on GitHub is the outcome of Step 3, after the
user rules.

## Step 2: Spot-check the brief, do not re-audit it

On the current path, check only where being wrong is expensive:

- **Every "Not covered anywhere" AC item.** Confirm it against the diff, siblings included. A
  false unaddressed-AC claim sends a developer to build something that already exists.
- **Anything you have a concrete reason to doubt.** A specific doubt, not a general audit.
- **Nothing else.** An answered question that shows what it checked is answered.

You are here for what the brief cannot do: judge whether the AC was the right ask, weigh the
product calls it held (**Your calls**), and see the thing running (Step 3).

## Step 3: Walk the user through what to test

**The main output.** The reviewer needs a short answer to "where do I go and what do I click."
Start from the brief's **Where to test** and **Draft test plan**, and cut the draft to what a
human must see. Read `references/test-plan.md` for the full rules. The core:

- **Lead with the environment** and say what it cannot show. Storybook cannot show Layout Builder,
  editor labels, or role gating. Use the URL the brief resolved; never guess one.
- **Size the blast radius** with the `yalesites-portfolio` skill when the PR changes a block or
  setting, if that skill is installed. Skip it otherwise.
- **AC first, then the blast radius:** every matching row of `references/beyond-ac-checks.md`
  and every consumer in the brief's **Regression surface**. Skipping a matching row needs a
  stated reason.
- **Flag any step that needs a role other than platform admin.** `drush uli` is user 1, which is
  not a platform admin either.
- Keep it to what a human must see, and say how long it should take. It stays in chat: never post
  it, never copy it to a ticket as Release Testing Steps.

**Every `yalesites-project` and `yale-ui-cl` review gets a driven browser run.** Not optional,
not offered, and not repeated when a current prepped board already has one. Follow
`references/drive-it.md`. Screenshot every result, show failures first, and send `ask` checks to
Step 3b. A missing brief only delays testing: do the setup while the brief is written.
**Hand the plan off only for what cannot be driven:** CLT Storybook, `atomic`, `tokens`, or a
failed preflight. For a failed preflight, say which check failed and offer to drive it once fixed.
**Hand-off never means no pictures.** Every visual board question carries an `image` or `compare`
block, so screenshot the Storybook preview even when the rest is hand-off. Only process questions
(`"process": true`) are exempt, and the packet check enforces it (`references/test-plan.md`).

## Step 3b: Get the user's calls and their own read

Two parts, neither optional. **Ask on the review board, not in a chat text box**
(`references/review-board.md`; `AskUserQuestion` only in the fallback cases it lists). A current
prepped packet is served as-is; one already answered in a dashboard stands in for the board.

- **Part 1, held calls.** The brief's **Your calls**, in its own words where clear, with any
  `ask` screenshots. Sort each against the reviewer's dimensions: in lane, ask it; out of lane,
  **name it and its owner, never drop it**; unclear, ask it; anything in the profile's
  **Always ask me about**, ask it. On the unscoped path, ask everything. An empty section is said
  out loud.
- **Check what is already open first** (`needs-decision`, `follow-up`), and put open decisions
  that name the reviewer to them first.
- **Anything left open goes on the record** as a `needs-decision` or `follow-up` block, in the
  format the `ticket` skill (yalesites-ticket plugin) defines in its `routing.md`. Confirm the
  list before posting; never raise one silently.
- **Part 2, their own read.** Always ask what they noticed, even when your analysis found
  nothing. Board pins, boxes, and comments count.

The sorting table, examples, and the open-call rules are in `references/held-calls.md`.

## Step 4: Turn the answers into actionable feedback

Read `references/composing-feedback.md` before writing. The core:

- **Scope the body to the reviewer's dimensions.** Out-of-lane findings stay out (they were named
  in Step 3b). Unscoped: everything goes in. An empty body is a normal approval.
- Every point: **file and line, what to change, why**, and **blocking or optional**. There is no
  third bucket. "Edits before merge (non-blocking)" is a contradiction.
- **First person singular ("I"), never "we"**, whatever a voice skill says. Apply a personal voice
  skill if one is available (`voice_skill` in config, or one installed for this person);
  otherwise plain and direct.
- **TL;DR first**, blocking items visible, detail in named `<details>` blocks, the AC map in a
  closing `<!-- yalesites:agent -->` block. Then run
  `python3 <skill-dir>/scripts/check-github-text.py review.md --surface pr-review`.
- New scope found mid-review: ask whether it is a new ticket or a fold-in. Do not decide.

## Step 5: Offer the follow-ups the brief found

Visreg coverage gaps and missing docs, from the brief's **Follow-ups worth a ticket**. Both are
**non-blocking**; say so. Every ticket goes through the `ticket` skill (yalesites-ticket plugin),
never a hand-written `gh issue create`. Empty section: skip without comment. Detail in
`references/composing-feedback.md`.

## Step 6 to Step 9: Decide, mention, label, post

Read `references/posting.md` before writing anything to GitHub. The rules that must never slip:

- **The event matches the body.** Anything the reviewer expects changed before merge, however
  small, means **request changes**. An approval carries no to-do list. On a board review, post
  the board's verdict without asking again, unless an approved PR still carries a before-merge
  edit: then stop and offer the two honest options.
- **Write path:** `gh` when `gh auth status` shows `repo` scope; the GitHub connector only when
  `gh` is not set up, never as a retry. Bodies go through a quoted heredoc on stdin. On the
  connector path, confirm the review landed before saying so.
- **Nobody approves their own PR.** Post as `--comment` and say why.
- **@-mention the assignee** (Step 7). No assignee is worth flagging.
- **Labels are a full-set `PUT`** (Step 8). Start from the current labels, strip the whole
  review-state set, add back what matches. Never `gh pr edit --add-label/--remove-label`. Never
  send a label the repo does not define. Leave `needs-decision` and `follow-up` alone unless this
  review raised or resolved one. Verify after.
- **The pass label comes from dimension and repo together**, never the repo alone. No match means
  no pass label, and ask before `ready to merge`.
- **`yale-ui-cl` needs two approvals** (the required approvers in `reviewer-roles.md`) before
  `ready to merge`.
- **Post order (Step 9):** decision and follow-up blocks, then the review, then labels. On an
  error, read it, never retry blindly, and never make the user redo the analysis.

## Step 9b: Check whether the linked ticket needs to catch up

After the review posts, load `ticket-sync` with the linked issue, the Step 2 divergences, how
Step 3 resolved them, and the posted body. It decides between a comment and an edit, and checks a
parent epic. On a board review, the packet already asked; apply that answer without a second
confirmation. Non-blocking. Running it after Step 9 means the ticket never reads as settled
before the review that settled it.

## Step 10: Confirm back to the user

Report the review link, the approval state, labels added and removed, who was @-mentioned, and
whether Step 9b updated the ticket. Keep it short. **Say what this review did not cover:** on a
scoped run, list the out-of-lane calls, who they wait on, and which dimensions still need a pass.

---

## Notes

- The same PR number can exist in several repos. Confirm the repo before acting.
- **Two or more PRs means `batch-mode.md`**, not this file in a loop. Batch mode shares the
  reading and testing, but every unit still gets its own explicit approve or request-changes
  ruling. A blanket approval across PRs is the worst thing this skill can do.
- This skill takes real, visible GitHub actions. When unsure about the event or about scope,
  ask.
- The team's PR body link (`## [#1157 :: Title](url)`) is not a closing keyword, so a merged PR
  does not close its issue. Check, or close it explicitly.
- **This skill is the only approval gate.** An automated pass may move a PR to `needs work` and
  back, never to a `pass` label, `ready to merge`, or `ready to close`. An approval label already
  on a PR came from a human; do not walk it back silently.
- **A `needs work` PR is out with the developer.** Check for an automated pass's comment (it
  carries an `ys-prereview` marker) and consider waiting for the fix.
- **One ticket number open in several repos is one unit of work.** AC is often split across
  repos, so never approve one PR's coverage in isolation.
- A thin or hedged brief is a signal about its producer, not the workflow. Mention it so the
  producer can be tightened.
- **Scoping narrows questions, never guarantees.** Say the scope out loud once. Out of lane means
  named, not dropped.
- `references/reviewer-roles.md` is the part that goes stale: confirm handles with the person,
  never infer them.
- **A pass label claims a check happened.** Apply none rather than a false one.
