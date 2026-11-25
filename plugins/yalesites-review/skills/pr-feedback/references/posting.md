# Posting: review event, @-mention, labels, and confirmation (Steps 6 to 9 detail)

Read this from `SKILL.md` Step 6, before anything is written to GitHub. Every rule here guards a
real, user-visible action.

## Step 6: Decide approve vs. request changes

**On a board review, the ruling is already made.** `answers.json` carries one `verdicts` entry per
PR (`review-board.md` Step R3): `approve`, `changes`, or `comment` (a decision still
pending, posted as a comment). Post exactly that. Do not ask again, and do not play it back for a
confirmation: the board's last page showed the reviewer every ruling and what sending would post,
and finishing the board is finishing the review.

**On the chat fallback,** ask the user directly if it isn't obvious from their feedback: is this
ready to approve, or does it need another pass?

**The event has to match the body.** Developers, and the Claude sessions they review with, treat
an approval as "done, merge it" and do not dig through its body for work. Developer Claude
sessions pick up work from the `needs work` label, and only request changes puts it there (Step
8). An approval lands `ready to merge` instead, so any edits in its body never get seen.
Confirmed on `component-library-twig#751`, 2026-09-28: the review said "Approving," listed
before-merge edits, and landed `pass functional review` + `ready to merge`. The developer's
Claude never saw the edits.

| What the feedback contains | Event |
|---|---|
| Nothing, or only items the dev can skip and still merge | **Approve** |
| Anything the reviewer expects changed before merge, even one small edit | **Request changes** |

When the user says "approve" but the composed body still carries a before-merge edit, stop and
say so before posting. On a board review, check every PR ruled `approve` or `comment` (a comment
is not a changes request either, so an edit in it is lost the same way). The edit can come from:

- a free-text answer ("Something else" always rules `comment`, whatever it says) or a note;
- the reviewer's own read (`ownRead`), or a pin, box, or comment on the board (`markups`), which
  the inferred ruling never reads;
- an option answer whose `verdict` is `changes`, on a PR whose entry has `inferred: false`, since
  the reviewer's manual ruling replaced what that answer pointed to.

That mismatch is the only reason to ask after the board. Offer the two honest options: request changes with those items as the
blocking list, or downgrade them to genuinely optional (or to a follow-up ticket) and approve.
Do not pick for them, and do not soften the wording to make an approval fit.

A request-changes review for a few small edits is normal and not a harsh verdict. Say so in the
TL;DR ("Requesting changes: four small doc edits, then this is good to go.") so the developer
reads it as close, not rejected.

Whichever way it goes, format the `body` per "How this reads on GitHub" in `composing-feedback.md`: TL;DR first, blocking items visible, everything else in named `<details>` blocks.

### Preflight: pick the write path once

Everything posted in Steps 6, 8, and 9 goes through the same path, so decide it here rather than
per call:

```bash
gh auth status
```

| Result | Path |
|---|---|
| Logged in, scopes include `repo` | **Use `gh`.** The normal path, and everything below assumes it. |
| `gh` not found, not logged in, or no `repo` scope | **Fall back to the GitHub connector**, using the alternate form given in each step. |

**Never try the connector first**, and never use it as a retry after a `gh` failure. `gh` is the
default whenever it is there. The fallback exists for one reason: someone who set Claude up from
the team wiki, which walks through connecting the GitHub *connector* and promises no terminal is
needed, should still be able to post a review. It is not a hedge against `gh` erroring, which
Step 9 triages instead.

**On the fallback path, say so and verify.** Tell the user you are posting through the connector
because `gh` is not set up, and that its token has an intermittent 403 write gap on these repos,
so they should expect you to confirm the review actually landed. Then actually confirm it, per
Step 9. A silently unposted review is the specific failure this whole arrangement exists to
avoid.

**Always pass the body as a file on stdin, never as a `-b` string.** Review bodies contain
backticks, `<details>` tags, and newlines. A double-quoted `-b` argument mangles the formatting
and can trigger command substitution on the backticks. Use a quoted heredoc every time:

**If approving:**

```bash
gh pr review NUMBER --repo yalesites-org/REPO --approve --body-file - <<'EOF'
TL;DR: approving. One optional note about the empty state.
...
EOF
```

An approval can be feedback-free. In that case drop `--body-file` entirely rather than piping an
empty body.

**If requesting changes:**

```bash
gh pr review NUMBER --repo yalesites-org/REPO --request-changes --body-file - <<'EOF'
TL;DR: requesting changes. Two blocking items, both about role gating.
...
EOF
```

`--request-changes` needs a body, so there is always something to pipe.

**Connector fallback:** `mcp__github__create_pull_request_review` with
`event: "APPROVE"` or `event: "REQUEST_CHANGES"` and the same composed body. The body text is
identical on either path, so compose it once before choosing.

Either way, update labels next (see Step 8).

**Why `gh` and not the GitHub connector:** the connector's token has an intermittent write gap on
these repos, a 403 "Permission Denied: Resource not accessible by personal access token," even
though it reads fine. `gh` is authenticated with `repo` scope, and the team's automated
pre-review standardized on it for exactly this reason. Reads through the connector are fine. Writes go
through `gh`.

**Nobody can approve their own PR.** If the PR author is the person running this skill, `--approve`
fails with "Can not approve your own pull request." Post the same body with `--comment` instead,
tell the user the approval has to come from someone else, and still apply the Step 8 labels if
that is what they decided.

## Step 7: @-mention the assigned developer

Pull the assignee's GitHub login from the `gh pr view` output in Step 1 (`assignees[].login`) and include `@login` in the comment body so they get notified. If there's no assignee set, mention this to the user rather than silently skipping the notification, an unassigned PR about to get review feedback is itself worth flagging.

## Step 8: Update labels

Labels go through `gh api ... -X PUT`, which **replaces the entire label set**. So **fetch the PR's current labels first** (Step 1 already did) and compute the new full list, don't just send the labels you're adding or you'll wipe out everything else on the PR (type labels, epic links, etc.).

**Do not use `gh pr edit --add-label` / `--remove-label` here.** Removing and adding the same label in one call silently no-ops on that label: it comes back off the PR with no error. That is precisely this step's reconcile case, where a label like `pass functional review` is stripped with the rest of the review-state set and then added back for an approval, so the one label the approval depends on is the one that vanishes. Confirmed on `yalesites-project#1453`, 2026-08-12.

Rather than a simple remove-one/add-one swap, **reconcile the whole set of review-state labels** every time. A PR can arrive in an inconsistent state (e.g. still carrying `pass functional review` / `ready to merge` from an earlier pass that a fresh deep-dive now contradicts), so start by stripping *all* of these regardless of which are present, then add back only the ones that match the new outcome:

Review-state labels to strip before reapplying: `needs review`, `needs work`, `pass code review`, `pass functional review`, `pass design review`, `pass a11y review`, `ready to merge`, `ready to close`. Leave every other label (type, epic, milestone-linked, etc.) untouched.

**`needs-decision` and `follow-up` are not review-state labels.** Never strip them in the reconcile. Add one only for a block raised in Step 3b, and remove one only when this review resolved it (see "Open calls go on the record").

Strip only labels actually present on the PR, and never add one the repo does not define. The full set differs by repo: `pass a11y review` exists in `yalesites-project` and `component-library-twig` only, `pass design review` in `component-library-twig` only, and `ready to close` in `yalesites-project` only. `yale-ui-cl` defines `pass code review` and `pass functional review` and none of the others. `reviewer-roles.md` holds the confirmed matrix and the command to re-verify it.

### The "pass ___ review" label comes from dimension and repo together

Not from the repo alone. A pass label is a claim that a specific check happened, so it has to
match what the reviewer from Step 0 actually reviewed. Picking it from the repo is how a design
reviewer's approval ends up stamped `pass functional review`, with nothing on the PR recording
that design was what got checked.

**Scoped path.** Take the reviewer's dimensions from Step 0, map each to its label, and keep only
the labels the repo defines. The full matrix and its verification command live in
`reviewer-roles.md`; the short form:

| Dimension | Label | Defined in |
|---|---|---|
| `code` | `pass code review` | all five repos |
| `functional` | `pass functional review` | all five repos |
| `design` | `pass design review` | `component-library-twig` only |
| `a11y` | `pass a11y review` | `yalesites-project`, `component-library-twig` |
| `product` | none | recorded in the review body, not on a label |

A reviewer owning two dimensions that both have labels in this repo gets both. **Never apply a
label for a dimension the reviewer does not own**, and never one the repo does not define, since
Step 8's `PUT` creates a missing label instead of erroring.

**Unscoped path (Step 0 found no profile and no map entry).** Today's behavior exactly, from the
repo alone:

| Repo | Approval review label |
|---|---|
| `yalesites-project` | `pass functional review` |
| `atomic` | `pass functional review` |
| `tokens` | `pass functional review` |
| `component-library-twig` | `pass design review` |
| `yale-ui-cl` | `pass functional review` |

**When the reviewer's dimensions yield no label for this repo**, a design reviewer on a
`yalesites-project` PR or a product-only reviewer anywhere, apply no pass label. Say plainly
which dimension they own, that the repo defines no label for it, and ask before adding
`ready to merge`. Do not reach for `pass functional review` just to have something to apply: an
unlabeled honest approval beats a labeled false one.

| Outcome | Add back |
|---|---|
| Requesting changes | `needs work` |
| Approving (normal PR) | the reviewer's pass label(s) for this repo + `ready to merge` |
| Approving (demo/multidev-only PR) | the reviewer's pass label(s) for this repo + `ready to close`, but see below |
| Approving, no pass label matched this repo | `ready to merge` only, and only after asking |

**`yale-ui-cl` (UICL) needs two approvals before `ready to merge`.** Every UICL PR needs approval
from both required approvers listed under "UICL required approvers" in `reviewer-roles.md` (team
data, not personal config). So on a UICL approval, `ready to merge` goes on only when this review is the **second** of those two. Before
computing the label set, check whether the other required approver already approved:

```bash
gh api repos/yalesites-org/yale-ui-cl/pulls/NUMBER/reviews --paginate \
  -q '.[] | select(.user.login == "OTHER_LOGIN") | select(.state != "COMMENTED") | .state' | tail -n 1
```

`OTHER_LOGIN` is whichever of the two the current reviewer is not. The current reviewer is
`reviewer_login` from `config.md`, which defaults to `gh api user -q .login`. Set that key only to
the same account the review posts as.
With `--paginate`, `gh` runs the `-q` filter once per page, so the filter prints every matching
state and `tail -n 1` keeps the latest across all pages. Empty output means no review.

- **`APPROVED`:** this review is the second approval. Apply the pass label(s) + `ready to merge`
  as the table says.
- **Anything else** (empty output, `CHANGES_REQUESTED`, `DISMISSED`): this is the first approval.
  Submit the approval and apply the pass label(s), but leave `ready to merge` off and keep
  `needs review` on so the PR stays in the other reviewer's queue. Tell the user the PR is
  waiting on the other approval, by name.
- **The current user is neither of the two:** apply the pass label(s) only and leave
  `ready to merge` off. Their approval does not count toward the two.

Never apply `ready to merge` on a first approval, even if the PR already carries it from an
earlier pass: the strip-and-reapply above takes it off, and this check decides whether it comes
back. This applies to `yale-ui-cl` only; the other repos keep the single-approval table above.

**Open question, not settled here: whether one dimension's approval should still add
`ready to merge`.** Today it does, for everyone, and the table above keeps that unchanged on
purpose. But once a `pass design review` label means design and only design was checked, a lone
design approval marking a PR merge-ready is arguably claiming more than it should. That changes
what "approved" means on every PR, so it is a team-wide call for our lead developer rather than
something to settle inside this skill. Until it is settled, **behave as the table says and do not
improvise a stricter rule mid-review.** Tracked in
[yalesites-claude-plugins#30](https://github.com/yalesites-org/yalesites-claude-plugins/issues/30).

**`ready to close` only exists in `yalesites-project`.** `atomic`, `tokens`,
`component-library-twig` and `yale-ui-cl` do not have that label, and applying a label a repo does not define
either errors or silently creates it. For a demo-only PR in one of those three, apply the
repo's review label, leave `ready to merge` off, and tell the user the PR needs closing by
hand. A demo-only `yale-ui-cl` PR follows this too, and never gets `ready to merge` from the
two-approval check. This is not hypothetical: `component-library-twig` has a long-lived `DEMO ONLY, DO NOT
MERGE` PR open.

This matters in practice, a PR can look "ready to merge" on the label alone while a deep-dive turns up something the earlier pass missed. Reconciling the full set avoids leaving contradictory labels (e.g. `needs work` sitting next to `ready to merge`), and picking the wrong review label is an easy mistake to make once it depends on both the reviewer's dimensions and the repo's label set.

**Detecting a demo-only PR:** check the PR title (case-insensitive) for any of `MULTIDEV ONLY`, `DEMO ONLY`, `DO NOT MERGE`. These PRs aren't meant to ship, they're just for showing work on a multidev environment, so they get closed out instead of queued to merge.

Send the whole computed set, one `labels[]` flag per label, including every label you are
keeping:

```bash
gh api repos/yalesites-org/REPO/issues/NUMBER/labels -X PUT \
  -f "labels[]=pass functional review" \
  -f "labels[]=ready to merge" \
  -f "labels[]=type: feature" \
  -f "labels[]=epic: 1648"
```

Anything absent from that list comes off the PR, which is the whole point for the review-state
labels and a real hazard for everything else. There is no separate remove call.

Then **verify, don't assume.** Silent label failures are the reason this step is written this
way:

```bash
gh pr view NUMBER --repo yalesites-org/REPO --json labels -q '.labels[].name'
```

If something is missing, re-send the corrected full set rather than patching with
`gh pr edit --add-label`.

**Connector fallback:** `mcp__github__update_issue` with `owner`, `repo`, `issue_number` (the PR
number, PRs share the issue numbering), and the same recomputed `labels` array. That call is also
a full replacement, so the computed set is identical on either path and none of the reconcile
logic above changes. Verify afterwards either way.

One thing neither full-replace form will catch for you: **both happily create a label the repo
does not define.** `gh pr edit --add-label` would have errored with `'X' not found`, but `PUT` just makes
it. So the per-repo tables above are load-bearing here, not advisory: sending
`pass design review` to `yalesites-project`, or `ready to close` to `component-library-twig`,
silently litters a new label onto the repo instead of failing. Check the repo before sending.

## Step 9: Post it, and confirm it landed

Post any decision or follow-up blocks and resolution lines from Step 3b first, each as its own PR comment, then the review from Step 6, then the label update from Step 8.

`gh` writes with the CLI's own credentials, so the GitHub connector's 403 write gap does not
apply here. If a write does fail, read the error rather than retrying blindly:

| Error | What it means | What to do |
|---|---|---|
| `gh: Not Found` or `HTTP 404` | Wrong repo for that PR number, and the number exists in more than one repo | Re-confirm the repo with the user, do not guess |
| `Can not approve your own pull request` | The user authored it | Step 6's `--comment` fallback |
| Label set comes back wrong from Step 8's verify | A label was sent that the repo does not define, or the computed set dropped something | Step 8's per-repo tables, then re-send the corrected full set |
| `HTTP 401` / `gh auth status` shows no active account | The CLI is not authenticated | Switch to the connector fallback for this review, per Step 6's preflight. Offer `gh auth login -h github.com -s project,repo,read:org,workflow,gist` as the durable fix (never plain `gh auth login`, which resets scopes and drops `project`), but do not block the review on it |
| `403 Resource not accessible by personal access token` | You are on the connector fallback and hit its write gap | Do not retry. Show the user the drafted body and computed label set verbatim, and tell them `gh auth refresh -h github.com -s project,repo,read:org,workflow,gist` clears this permanently (`gh auth login -h github.com -s project,repo,read:org,workflow,gist` if `gh` is not logged in at all; never plain `gh auth login`, which drops `project`) |
| Anything else | Unclear | Show the user the drafted body and label plan verbatim so nothing is lost, then ask |

**On the connector fallback path, confirm the review landed before reporting success**, because
this is the path with a history of silent write failures:

```bash
gh pr view NUMBER --repo yalesites-org/REPO --json reviews -q '.reviews[-1].state'
```

If `gh` is missing entirely, read it back with `mcp__github__get_pull_request_reviews` instead.
Either way, do not tell the user a review posted until something confirms it did.

Whatever happens, **never make the user redo the analysis.** Keep the composed review body and
the computed label set, and retry those exact artifacts once the cause is fixed.
