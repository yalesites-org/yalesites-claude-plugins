---
name: yalesites-pr-feedback
description: "The human half of YaleSites PR review, and the only way a PR reaches an approved state. Use whenever the user asks to review, look at, check, approve, or give feedback on a PR, even without the words 'PR feedback' explicitly, e.g. 'can you check PR 1288', 'review this PR', 'is this one ready to merge', 'approve #452', 'what do you think of this pull request'. Covers yalesites-project, component-library-twig, atomic, and tokens. Picks up the brief the automated pr-prereview pass already wrote (diff read, acceptance criteria mapped, mechanical findings already sent to the dev) instead of re-deriving it, then does what that pass cannot: walks the user through exactly what to test and where (multidev for yalesites-project, Storybook deploy preview for component-library-twig), settles the product and UX calls the pass held back, turns the answers into actionable developer feedback with exact file/line locations, and posts the review with the right approval state and labels, @-mentioning the assigned developer. Also handles several PRs in one pass when more than one is named or the whole queue is in scope, e.g. 'review 1560, 1572 and clt 728', 'go through my review queue', 'clear out needs review'."
argument-hint: "[repo#number, or several for batch mode, or nothing to sweep the review queue] [--as code|functional|design|a11y|product]"
---

# YaleSites PR Feedback Skill

## Overview

This skill is the **human half** of YaleSites PR review. The automated half, `pr-prereview`, runs every two hours: it reads the diff, checks it against the ticket, hands mechanical problems straight back to the developer, and writes a brief. It can never approve anything.

This skill picks up that brief and does what the automated pass deliberately cannot: put eyes on the running thing, settle the product calls, and post a real review with an approval state and labels. **Nothing reaches an approved state without going through here.**

So the order of work is: work out whose review this is, load the brief, spot-check it, walk the user through testing, get their calls, then post. The diff deep-dive is not repeated here, and re-deriving it is the main thing to avoid.

**The review is scoped to the reviewer.** Step 0 resolves who is running this and which review dimensions are theirs to rule on, from their own profile first and a shared login map second, and the rest of the steps ask, write, and label within that scope. A reviewer it cannot place gets today's behavior in full, ungated, which is the one guarantee this arrangement makes.

**Repos in scope:** `yalesites-org/yalesites-project`, `yalesites-org/component-library-twig`, `yalesites-org/atomic`, `yalesites-org/tokens`
**Issues live in:** `yalesites-org/YaleSites-Internal` (PRs link to them in the body, usually as a `#XXXX` reference or full URL)

Don't guess at a repo. If the user gives a bare PR number without one, ask which repo it's in, or check the URL if they pasted one.

**Reviewing more than one PR?** Read `references/batch-mode.md` before starting, and follow it
instead of running the steps below once per PR. It applies whenever the user names two or more
PRs in one prompt, or scopes the ask to the queue as a whole ("review everything in needs
review", "what's in my queue"). It fans the brief-loading and spot-checking out to one subagent
per unit of work, assembles a single testing sitting grouped by environment, and batches the
held product calls. What it deliberately does not batch is the approve or request-changes call:
that stays one explicit ruling per unit of work, because a blanket approval posted across six
PRs under the user's account is the worst thing this skill can do.

---

## Step 0: Work out whose review this is

**Do this first, before loading anything.** Who is running this decides which calls are worth
putting to them, which feedback the review can honestly claim, and which `pass ___ review` label
it may apply. Reviewers on this team do not all review the same thing, and a review scoped to the
repo instead of the reviewer asks a design reviewer to gate code and stamps a functional-review
label on a design pass.

Resolve it in this order and stop at the first hit:

| Order | Source | How |
|---|---|---|
| 1 | **The reviewer's own profile** | `cat ~/.claude/yalesites/pr-feedback/reviewer-profile.md` |
| 2 | **The shared login map** | `gh api user --jq .login`, then look the login up in `references/reviewer-roles.md` |
| 3 | **No match** | Today's behavior, in full, ungated. See below. |

The profile wins over the map when both exist, because the person wrote the profile and the map
was written about them.

**An unmatched reviewer gets today's full behavior. This is the guardrail, and it does not bend.**
No dimension filtering, every held call put to them, the pass label picked from the repo as it
always was. This feature can make the review sharper for someone it recognizes; it can never make
the review *smaller* for someone it does not. A missing profile is a normal state, not a
misconfiguration, and `gh` not being authenticated resolves here too.

**Say which way it went, once, in chat, before Step 1.** One line, so the reviewer can see the
scoping rather than discovering it three steps later when a question they expected never arrives:

```
Scoping this to your profile: Product Manager, ruling on functional and product.
Code and design calls will be surfaced but left for whoever owns them.
```

```
No reviewer profile and no role-map entry for `<login>`, so this runs unscoped: every held call
comes to you and the pass label comes from the repo. Want me to set up a profile? /reviewer-profile
```

Offer `reviewer-profile` on the unmatched path, once, and then drop it. Do not re-offer it later
in the run and do not block the review on it.

### The `--as` override

`/pr-feedback 1560 --as code` scopes this one run to the named dimension or dimensions
(`--as code,a11y`), whatever the profile says. It exists for covering a lane that is not normally
yours: someone out, or a PR nobody else can get to. Scoping is a default, not a lock.

Say the override is active and that it overrode the profile, and treat the named dimensions as
the reviewer's own for the rest of the run, including the pass label. `--as` with no dimension, or
an unrecognized one, is a question to the user rather than a guess.

### What the rest of the skill does with this

| Step | Effect |
|---|---|
| 3b | Held calls outside the reviewer's dimensions are named as out of lane, not put to them and not dropped |
| 4 | Composed feedback covers the reviewer's dimensions only |
| 8 | The pass label comes from dimension and repo together, never repo alone |

Nothing else changes. Steps 1, 2, 3, 5, 6, 7, 9, and 10 run identically for every reviewer: the
brief is the brief, the environment is the environment, and the approve or request-changes ruling
is always the user's.

## Step 0b: Title the session so it can be found again

Reviews get done in batches, and the sidebar fills with auto-generated titles that all read
alike. Set the session title from the PR numbers **before Step 1**, so a review can be found
weeks later without opening it.

Call `mcp__ccd_session_mgmt__set_session_title` once, with the scope that matches the ask:

| Scope | Title |
|---|---|
| One PR | `PR review: yalesites-project #1560` |
| Named batch | `PR review: 1560, 1572, CLT 728` |
| Queue-wide sweep | `PR review queue: 2026-09-22 (5 PRs)` |

- Bare numbers mean `yalesites-project`. Name the other repos: `CLT 728`, `atomic 521`,
  `tokens 94`.
- **A queue sweep has no numbers in the prompt**, so it gets titled after Step B1 confirms the
  work set, using today's date and the unit count. This is the case that needs a title most, because
  the auto-generated one carries nothing at all.
- Keep it short enough to read in a narrow sidebar. Past three PRs, name the first two and add
  `+N more`.
- **Title once.** Do not retitle as the run progresses and do not append outcomes to it. The
  title is for finding the session, not for reporting on it.
- **The tool is desktop-app only.** When it is not available, skip this step silently: no
  mention, no fallback, no error. A CLI run loses nothing else.

## Step 1: Load the pre-review brief

The `pr-prereview` pass runs every two hours and deep-dives every PR that enters the review
queue. By the time a PR reaches you it has already read the diff, mapped it against the
ticket's acceptance criteria, answered what it could answer alone, fixed nothing but handed
anything mechanical back to the developer, and written down the rest. **Start from that
brief, not from the diff.** Re-deriving it is the single biggest waste in this review.

1. Get the PR's current head and basics:
   ```
   gh pr view NUMBER --repo yalesites-org/REPO \
     --json title,url,headRefOid,author,assignees,labels,isDraft
   ```
2. Read the brief at `~/.claude/yalesites/pr-prereview/briefs/{repo}-{number}.md`.
3. Compare the brief's **Brief written against SHA** line to the PR's `headRefOid`.

| Brief state | What to do |
|---|---|
| Present, SHA matches head | **Use it. Skip Step 2 entirely.** This is the normal path. |
| Present, SHA is behind head | Use it for context, then read only the new commits: `gh pr diff NUMBER --repo yalesites-org/REPO` and compare against the brief's claims. Tell the user which parts of the brief may be stale. |
| Absent | Invoke the `pr-prereview` skill scoped to this one PR, in dry-run mode: `pr-prereview {repo}#{number} --dry-run`. It writes the brief without posting anything to GitHub or touching a label. Then continue here. |

The dry-run fallback matters: it means this skill has exactly one deep-dive implementation
to maintain, living in `pr-prereview`, and a PR the schedule never saw still gets reviewed
properly rather than shallowly.

**The brief is local and stays local.** It contains the product calls the audit is forbidden
to publish. Nothing from its "Your calls" or "Not checked here" sections goes onto GitHub
verbatim. What goes on GitHub is the outcome of Step 3, after the user rules on it.

## Step 2: Spot-check the brief, do not re-audit it

Only on the stale or absent paths above does this involve reading much diff. On the normal
path, check the brief where being wrong would be expensive and take the rest:

- **Every "Not covered anywhere" AC item.** Confirm it against the diff before it reaches
  feedback. A false unaddressed-AC claim is the most costly error this review can make: it
  sends a developer to build something that already exists, usually in a sibling repo.
- **Anything in the brief you have concrete reason to doubt.** Not a general audit, a
  specific doubt.
- **Nothing else.** If the brief says a question is answered and shows what it checked, that
  is the answer. Do not re-check it to feel thorough.

What the brief could not do, and you are here for:

- Judge whether the ticket's acceptance criteria were the right ask in the first place.
- Weigh the product calls the audit deliberately held (copy, defaults, role gating, scope,
  UX). These are in the brief's **Your calls** section, already phrased as questions.
- Put eyes on the thing actually running. That is Step 3.

## Step 3: Walk the user through what to test

**This is the skill's main output.** Everything before it was preparation and everything
after it is posting. The user is the PM, not the developer: the useful thing this skill
produces is a short, concrete answer to "where do I go and what do I click."

The brief's **Where to test** and **Draft test plan** sections are the starting point. Treat
the draft as a draft. The audit has never seen the feature work and its plan will be
over-thorough in some places and thin in others. Cut it down to what genuinely needs a human
looking at it.

### Lead with the environment, and be specific about what it can show

Resolve the URL from the brief. If the brief says there is no environment, say that first,
because it changes what this review can conclude.

| Repo | Where | What it cannot show |
|---|---|---|
| `yalesites-project` | Pantheon multidev, the full CMS | Nothing, this is the real thing |
| `component-library-twig` | Netlify deploy preview, Storybook only | Layout Builder placement, editor field labels, role gating, anything that depends on Drupal passing real values in |
| `atomic` | No preview of its own. The sibling `yalesites-project` PR's multidev, if one exists | If there is no sibling, there is no deployed way to see this. Say so. |
| `tokens` | No preview of its own. The sibling `component-library-twig` preview, if one exists | Same. Say so. |

Full patterns and the direct visreg content URLs are in
`pr-prereview`'s `references/preview-environments.md`. Do not restate the block slug table
here, and do not guess a URL: the brief resolved it by probing, so use what it resolved.

When the environment is Storybook and the ticket's acceptance criteria are about what an
**editor** can do, say plainly that the preview cannot answer that. It is a real limit on the
review, not a detail.

### Then give the steps

Short numbered list. Each step is a link, an action, and what should happen:

```
1. Open <direct URL>. The table headers should each carry scope="col" (check with the
   inspector or a screen reader).
2. Drag that block into a 33% section. Expected: no horizontal scrollbar at 1440px or 360px.
3. Log in as an editor, not platform admin. Expected: the new control is visible.
```

Rules that make this useful instead of noise:

- **Cover the acceptance criteria first**, then edge cases worth a human eye: empty state,
  long content, mobile, keyboard and screen reader paths.
- **Flag any step that needs a role other than platform admin.** The user is a platform admin
  by default, so a role-gated step silently passes for them and fails for everyone else. This
  is the single most common thing a PM review misses.
- **Keep it to what a human must see.** If CI already proves it, or the audit already verified
  it from the code, leave it out and say the audit covered it.
- **Say how long it should take.** Three steps or ten changes whether this happens now.

This is a walkthrough for the user in chat, not a GitHub comment. Do not post it, and do not
copy it onto the ticket as Release Testing Steps. (The `release-prep` skill owns those, later,
once the behavior is settled.)

Eventually this step will drive a browser directly. Until then it hands off to the user, so
write it for someone reading it on a second monitor with the PR open.

## Step 3b: Get the user's calls and their own feedback

Two parts, and neither is optional.

**Part 1, the held calls.** Use `AskUserQuestion` on the brief's **Your calls** items. They
are already scoped to real product decisions (copy, defaults, role gating, scope) because the
audit was forbidden to decide them, so put them to the user in the brief's own words where they
are already clear.

**Sort them against the reviewer's dimensions from Step 0 first.** Every held call belongs to one
of the five dimensions, usually obviously: a copy or defaults question is `product`, a keyboard
path is `a11y`, a spacing question is `design`, an implementation-approach question is `code`.

| The call is | What to do |
|---|---|
| In the reviewer's dimensions | Ask it, as you would have anyway |
| Not in their dimensions | **Name it, do not ask it.** One line: what the call is, which dimension it belongs to, and who owns it if the role map names someone |
| Unclear which dimension | Ask it. Scoping is a filter on questions that clearly are not theirs, not a reason to lose one |
| Anything in the profile's **Always ask me about** | Ask it, even if the brief never held it and even if it sits outside their dimensions. That section is a floor the reviewer set for themselves |

**Out-of-lane calls are stated, never dropped.** The brief raised them for a reason, and this
review is where they would otherwise disappear. Listing them also tells the reviewer what the
posted review will *not* cover, which is what makes a scoped approval honest:

```
Two calls are outside your lane, so I have left them:
- The `--variant` default on line 88 is a code call. That one is for our lead developer.
- The 12px gap under the heading is a design call, April's.
Neither gates your functional approval. Want me to flag them on the PR for whoever picks them up?
```

Offer to flag them as a plain non-blocking comment if the reviewer wants, and skip it if not.

**On the unscoped path from Step 0, none of this applies.** Every held call goes to the user, as
it does today.

If the brief's Your calls section is empty, say so plainly rather than inventing questions.
An empty section means the audit found nothing that needed a human ruling, which is a real
and common outcome. Say it is empty even when the reviewer is scoped, so an empty brief and a
fully-out-of-lane brief do not look the same from the outside.

**Part 2, their own read.** Always ask what they noticed, separately from your questions. They
may have tested the multidev before starting this session, or carry context from a meeting the
diff cannot show. Ask even when your own analysis turned up nothing: their input is a
first-class input to this review, not a fallback for when you are stuck.


## Step 4: Turn the user's answers into actionable feedback

Once the user responds, your job is translation: turn their (possibly short, possibly informal) input into feedback a developer can act on without a follow-up round trip.

**Scope the composed feedback to the reviewer's dimensions from Step 0.** The brief carries
findings across every dimension, and the temptation is to pour all of them into the review body
because they are sitting right there. Don't. A design reviewer's review must not carry code-level
file-and-line notes they never made: the developer reads the whole body as that person's review,
and follows up with them on notes they cannot defend.

So: the reviewer's own observations and the brief findings inside their dimensions go in the body.
Findings outside their dimensions stay out of it, having already been named in Step 3b. The
mechanical ones among them already went to the developer from the automated pass, so they are not
lost by being left here.

If that empties the body completely, say so. An approval with no feedback is a normal outcome and
Step 6 already handles a feedback-free approval.

**On the unscoped path, no filtering. Everything the user's answers support goes in.**

For every point that does go in:

- **Name the file and line(s)** from the brief's acceptance-criteria coverage map, or from the diff if Step 2 had to read it (`path/to/file.php:42` style, or the closest anchor if exact lines shifted).
- **Say what to change**, not just what's wrong. "This should check the user's role before rendering" beats "this seems off."
- **Say why**, tying back to the issue or a concrete risk (a11y, broken state, security, mismatched spec), one line is enough.
- **Separate blocking from optional.** If the user's feedback includes both must-fix items and nice-to-haves, label them so the developer doesn't have to guess what's gating merge.

Keep the tone direct and collegial, matching [[feedback_ticket_tone]] (if this memory exists for the person running the skill), no "PM-approved," no "do not push back," no ownership stamps. State the feedback and let it speak for itself.

**New scope found mid-review doesn't automatically become a new ticket.** If reviewing the diff surfaces functionality worth adding beyond what the linked issue asked for, don't default to grooming it into a separate backlog ticket, ask the user first. They may want it folded into the existing ticket instead (edited in after the PR merges) with the new functionality just drafted as a PR comment for the developer to see now.

**Voice:** if a personal writing-voice skill exists for whoever is running this, check for it and apply it, the comment is going out under that person's name. If none exists, default to a plain, direct, dev-facing tone: specific, unadorned, no forced friendliness.

**Exception, stay singular ("I"), not "we."** This overrides any writing-voice skill's default person, even if that skill normally speaks as "we" (e.g. `michael-voice`). PR feedback is one reviewer's read on the code, not an org-wide statement, so write it in first person singular: "I think this should check the role first," not "we think." Apply this to every comment this skill posts, clarifying questions, the review body, and any follow-up ticket offers from Step 5.

### How this reads on GitHub

The review body is read by a person first. Compose it per `../ticket/references/github-communication-format.md` and write it per `../ticket/references/github-writing.md`:

- **Open with a TL;DR line**, the outcome in one or two sentences. "Approving. One optional note about the empty state." / "Requesting changes: two blocking items, both about role gating."
- **Keep visible:** the TL;DR, and on a request-changes review the numbered list of blocking items (one line each, what to change, which file).
- **Collapse into `<details>` blocks with named summaries:** the per-item detail (file/line references, why it matters, how to fix), the optional/nice-to-have items, "what I checked" notes, and the visreg-coverage and documentation follow-up discussion from Step 5. Group them, two to four blocks, not one per point.
- **Close with a `<!-- yalesites:agent -->` block** holding the acceptance-criteria coverage map from the brief, what this pass checked, and the file/line index. That payload is what the next agent would otherwise re-derive from the diff, and no person needs to read it. Never put the approve/request-changes call or a blocking item in there: if it changes what someone does, it stays visible.
- The same TL;DR-first shape applies to the Step 3 clarifying-question comment if it goes to GitHub rather than staying in chat.

**On the words.** `github-writing.md` caps a review's visible layer at 250 words, the tightest of any surface, because a reviewer's verdict is the whole point and everything else is support. It also carries the one exception that matters here: a review is argument, not procedure, so the 20-word sentence cap and the one-instruction rule are relaxed for rationale, and only inside a collapsed block. The word swaps, active voice, and the no-em-dash rule still apply everywhere.

Check the draft body before posting:

```bash
python3 ../ticket/scripts/check-github-text.py review.md --surface pr-review
```

## Step 5: Offer the follow-up tickets the brief already found

The audit's brief has a **Follow-ups worth a ticket** section. It covers both checks that used
to happen here, so this step is now offering them, not finding them.

**Both are non-blocking.** Neither affects the approve or request-changes call in Step 6. Say
that explicitly when raising them, so an offer to open a ticket does not read as a condition
on this PR.

**A. Visreg coverage gaps.** The brief flags a brand-new block, or a new variant, field, or
option on an existing block, that the shared visreg content set will not represent. The
consequence is worth stating when you raise it: the next PR to touch this area will have no
reference page either, so the gap compounds. Offer a follow-up ticket as a heads-up, not an
`AskUserQuestion`. If they want it, draft it with the `ticket` skill's conventions, assigned to
whoever is running this, with acceptance criteria naming the specific block and the page it
belongs on under `/blocks-for-visreg` or `/content-types`.

**B. Documentation.** The brief flags a documentation item in the ticket's acceptance criteria
that the PR does not include, or user-facing behavior changing with no doc change anywhere.
Offer a follow-up ticket. If they want it:

- **Assignee:** whoever is running this skill (the PM), not the PR's developer.
- **Title prefix:** `Docs:`, per the `ticket` skill's conventions.
- **Where it lives:** ask which applies. External and editor-facing is yalesites.yale.edu.
  Internal is Teams, or GitHub (the org-wide internal knowledge repo, or a repo-specific
  README or docs folder).

If the brief's follow-ups section is empty, skip this step without comment. Do not go hunting
for follow-up work the audit did not surface.


## Step 6: Decide approve vs. request changes

Ask the user directly if it isn't obvious from their feedback: is this ready to approve, or does it need another pass?

Whichever way it goes, format the `body` per "How this reads on GitHub" above: TL;DR first, blocking items visible, everything else in named `<details>` blocks.

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
though it reads fine. `gh` is authenticated with `repo` scope and `pr-prereview` already
standardized on it for exactly this reason. Reads through the connector are fine. Writes go
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

Strip only labels actually present on the PR, and never add one the repo does not define. The full set differs by repo: `pass a11y review` exists in `yalesites-project` and `component-library-twig` only, `pass design review` in `component-library-twig` only, and `ready to close` in `yalesites-project` only. `references/reviewer-roles.md` holds the confirmed matrix and the command to re-verify it.

### The "pass ___ review" label comes from dimension and repo together

Not from the repo alone. A pass label is a claim that a specific check happened, so it has to
match what the reviewer from Step 0 actually reviewed. Picking it from the repo is how a design
reviewer's approval ends up stamped `pass functional review`, with nothing on the PR recording
that design was what got checked.

**Scoped path.** Take the reviewer's dimensions from Step 0, map each to its label, and keep only
the labels the repo defines. The full matrix and its verification command live in
`references/reviewer-roles.md`; the short form:

| Dimension | Label | Defined in |
|---|---|---|
| `code` | `pass code review` | all four repos |
| `functional` | `pass functional review` | all four repos |
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

**Open question, not settled here: whether one dimension's approval should still add
`ready to merge`.** Today it does, for everyone, and the table above keeps that unchanged on
purpose. But once a `pass design review` label means design and only design was checked, a lone
design approval marking a PR merge-ready is arguably claiming more than it should. That changes
what "approved" means on every PR, so it is a team-wide call for our lead developer rather than
something to settle inside this skill. Until it is settled, **behave as the table says and do not
improvise a stricter rule mid-review.** Tracked in
[yalesites-claude-plugins#30](https://github.com/yalesites-org/yalesites-claude-plugins/issues/30).

**`ready to close` only exists in `yalesites-project`.** `atomic`, `tokens`, and
`component-library-twig` do not have that label, and applying a label a repo does not define
either errors or silently creates it. For a demo-only PR in one of those three, apply the
repo's review label, leave `ready to merge` off, and tell the user the PR needs closing by
hand. This is not hypothetical: `component-library-twig` has a long-lived `DEMO ONLY, DO NOT
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

Post the review from Step 6 and the label update from Step 8, in that order.

`gh` writes with the CLI's own credentials, so the GitHub connector's 403 write gap does not
apply here. If a write does fail, read the error rather than retrying blindly:

| Error | What it means | What to do |
|---|---|---|
| `gh: Not Found` or `HTTP 404` | Wrong repo for that PR number, and the number exists in more than one repo | Re-confirm the repo with the user, do not guess |
| `Can not approve your own pull request` | The user authored it | Step 6's `--comment` fallback |
| Label set comes back wrong from Step 8's verify | A label was sent that the repo does not define, or the computed set dropped something | Step 8's per-repo tables, then re-send the corrected full set |
| `HTTP 401` / `gh auth status` shows no active account | The CLI is not authenticated | Switch to the connector fallback for this review, per Step 6's preflight. Offer `gh auth login` with `repo` scope as the durable fix, but do not block the review on it |
| `403 Resource not accessible by personal access token` | You are on the connector fallback and hit its write gap | Do not retry. Show the user the drafted body and computed label set verbatim, and tell them `gh auth login` with `repo` scope clears this permanently |
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

## Step 9b: Check whether the linked ticket needs to catch up

This is exactly the moment tickets go stale, Step 2 may have surfaced a place where the diff and the issue's acceptance criteria diverge, and Step 3 resolved it in conversation with the user. If nothing writes that resolution back to the ticket, the next person who reads it sees the original ask, not what was actually decided.

Now that the review from Step 9 is posted, load the `ticket-sync` skill and hand it the linked issue from Step 1, the divergences found in Step 2, and how they were resolved, Step 3's conversation plus the final posted review body. It decides whether the resolution is worth a comment (context only) or an edit (scope/acceptance criteria actually changed), and, if the issue is a child ticket under an epic, whether the parent epic's `Scope` or `Child Tickets` section needs a matching update.

Non-blocking: it doesn't change the approve/request-changes call already made in Step 6, it just makes sure the ticket reflects it. Running this after Step 9 rather than before means the ticket never ends up reading as settled before the review that settled it actually posts.

## Step 10: Confirm back to the user

After posting, report: a link to the review/comment, the final approval state, the labels applied (and removed), who was @-mentioned, and whether Step 9b updated the linked ticket. Keep it short, the user was following along and doesn't need the whole analysis repeated.

**Say what this review did not cover.** If Step 0 scoped the run, close with the out-of-lane calls from Step 3b and who they are waiting on, plus which dimensions the PR still needs a pass from. That line is the difference between an approval read as partial and one read as final.

---

## Notes

- Multiple repos in scope means the same PR number can exist in more than one repo, always confirm which repo before acting if there's any doubt.
- **Two or more PRs in one prompt means `references/batch-mode.md`**, not this file run in a loop. Running the steps above once per PR re-asks the same questions in series and, worse, invites a single blanket ruling at the end. Batch mode exists to collapse the reading and the testing while keeping the approve or request-changes call one explicit ruling per unit of work.
- **GitHub writes prefer `gh`**, per Step 6's preflight, because the connector's token has an intermittent 403 write gap on these repos while reading fine. The connector stays a documented fallback for anyone who set Claude up from the team wiki and has no terminal tooling, and on that path the review must be read back and confirmed rather than assumed. Reads through the connector are fine on either path.
- Labels are a full-set `PUT` (Step 8), so always start from the PR's current labels, never an empty list. `gh pr edit --add-label/--remove-label` is not a safe substitute: removing and adding the same label in one call silently drops it.
- This skill performs real, user-visible GitHub actions (a review, a notification, label changes). When in doubt about approve vs. request-changes, or about scope-creep questions, ask rather than assume.
- The team's PR body format (e.g. `## [#1157 :: Title](url)`) is not a GitHub-recognized closing keyword (`Fixes #`, `Closes #`, etc.), so merged PRs do not auto-close their linked issue. Don't assume an issue is closed just because its PR merged, check or close it explicitly.
- **This skill is the only approval gate.** `pr-prereview` can move a PR backward to `needs work` and back again, but it can never set a `pass` label, `ready to merge`, or `ready to close`, and it never submits a review event. If a PR arrives already carrying an approval label, that came from a human, so treat it as a real prior sign-off rather than something to walk back silently.
- **A PR labeled `needs work` is out with the developer**, usually because the audit handed it back. Reviewing it now means reviewing something known to be mid-fix. Check the audit's comment on the PR first (it carries an `ys-prereview` HTML marker) and consider waiting for the fix.
- **If the same ticket number is open in more than one repo, they are one unit of work.** The brief lists siblings. Acceptance criteria are routinely split across repos, so approving one PR's coverage in isolation is how a half-implemented ticket gets signed off.
- If a brief looks thin or hedged, that is a signal about `pr-prereview`, not a reason to distrust the workflow. Worth mentioning to the user so the audit skill can be tightened.
- **Role scoping can only narrow the questions, never the guarantees.** An unrecognized reviewer gets the full ungated run, and Step 0 announces which way it went before anything else happens. A scoped review that silently asks less than the reviewer expected is the one failure mode of this feature, and saying the scope out loud once is what prevents it.
- **Out of lane means stated, not dropped.** Every held call the brief raised either gets asked or gets named with its owner. A call that disappears because nobody's profile claimed it is worse than one asked of the wrong person.
- **`references/reviewer-roles.md` is the part of this that goes stale.** It carries the login-to-dimensions map and the confirmed dimension-to-label matrix, and both change as the team and the repos' label sets change. Handles in it are confirmed with the person, never inferred from org membership or commit history.
- **A pass label is a claim that a check happened.** Step 8 picks it from the reviewer's dimensions and the repo's label set together, and applies none when they do not intersect. Reaching for a label the repo happens to define, to avoid an unlabeled approval, is the specific bug that made role scoping necessary.
