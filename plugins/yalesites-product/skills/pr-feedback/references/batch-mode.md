# Batch mode: reviewing several PRs from one prompt

Read this when the user names more than one PR, or asks about the queue as a whole. For a
single PR, `SKILL.md` on its own is the whole flow and none of this applies.

## When batch mode applies

**Explicit list.** Two or more PRs named in one prompt: "review 1560, 1572 and clt 728",
"look at these three", "go through atomic#521 and tokens#94".

**Queue-wide.** No numbers given, scope implied: "review everything in needs review",
"what's in my review queue", "clear out the review queue", "go through the open PRs".

When the ask is ambiguous ("review the PRs"), enumerate the queue, show the work set, and
confirm before fanning anything out. Do not silently pick a subset.

## What batch mode changes, and what it does not

| `SKILL.md` step | In batch mode |
|---|---|
| 0, whose review this is | **Resolved once in the parent**, before the work set is built, and passed down |
| 1, load the brief | Fans out to one subagent per unit of work, concurrently |
| 2, spot-check the brief | Same subagent, same rules, read-only |
| 3, what to test | Becomes **one grouped testing sitting** across the whole batch (Step B3) |
| 3b, held calls | Batched into rounds of up to four questions (Step B4) |
| 4, actionable feedback | Per unit, in the main session, unchanged |
| 6, approve vs. request changes | **Per unit, explicitly, never batched** |
| 7 to 9b, post, mention, label, sync | Per unit, sequentially, in the main session, unchanged |

**The one rule that cannot bend:** every unit of work gets its own explicit approve or
request-changes ruling from the user. There is no "approve the rest," no "the others looked
fine," and no inferring approval from an absence of findings. Batch mode exists to collapse
the reading and the testing, not the decision. A blanket approval posted under the user's
account across six PRs is the worst outcome this skill can produce, and it is also the easiest
one to drift into, so treat any prompt that sounds like one as a request to go unit by unit.

## Step B0: Resolve the reviewer once

Run `SKILL.md` Step 0 **once, here, in the parent session**, before building the work set.
Profile first, then the login map, then the ungated fallback. Announce the scope one time for the
whole batch.

**Never let a subagent resolve it.** Six agents each running `gh api user` and each reading the
profile file is six chances to land on a different answer, and a batch where unit three is scoped
differently from unit four is unexplainable to the user. Resolve once, then pass the resolved
scope down to every prep agent in its prompt:

```
Reviewer scope for this batch: dimensions = functional, product.
Out of scope for this reviewer: code, design, a11y.
```

The prep agents stay read-only and decide nothing, so the scope changes only how they sort what
they return. Have them tag every item in `heldCalls` and `findingsForDev` with its dimension, and
return **all** of them regardless of scope. Filtering happens in the parent at Steps B4 and B5,
where the user can see what was set aside. An agent that drops an out-of-lane finding to be
helpful loses it for good.

**A `--as` override applies to the whole batch**, not per unit. `/pr-feedback --as code` on a
queue sweep scopes every unit in it. There is no per-unit override, and a reviewer who wants one
unit in a different lane should run that unit on its own.

**On the unscoped path, nothing in this step changes anything downstream.** Every held call in
every unit goes to the user, and the pass labels come from the repo, as they do today.

## Step B1: Build the work set

**From an explicit list:** parse each into `{repo}#{number}`. A bare number with no repo gets
asked about, same as single-PR mode. Do not assume `yalesites-project` just because it is the
most common.

**Queue-wide:** enumerate each repo in scope.

```
gh pr list --repo yalesites-org/REPO --state open \
  --json number,title,isDraft,labels,author,assignees,headRefOid,updatedAt,url,body
```

Include a PR when it carries `needs review`, is not a draft, and does not carry
`work in progress`, `don't merge`, `review in progress`, or `ready to close`. Exclude any title
containing `MULTIDEV ONLY`, `DEMO ONLY`, or `DO NOT MERGE` (case-insensitive) from a queue-wide
sweep, and say which ones you dropped. An explicitly named demo PR still gets reviewed, since
asking for it by number is the user overriding the filter.

**Group siblings into units of work.** Parse the leading ticket number from each PR title (`1648:`
or `fix(1308):`) and treat every PR sharing that number as **one unit**. A unit is the thing that
gets one prep agent, one testing block, one ruling, and one outcome. Acceptance criteria are
routinely split across repos, so a unit judged one PR at a time produces false unaddressed-AC
findings and half-approved tickets.

**Skip what is out with the developer.** A PR labeled `needs work` is mid-fix, usually because
`pr-prereview` handed it back. List it as skipped with that reason rather than reviewing a known
moving target. If the user named it explicitly, review it, but say plainly that it is mid-fix.

**Cap the batch at 6 units**, newest `updatedAt` first, and say what rolled over. The cap is
about the user's attention more than context: a testing sitting longer than about half an hour
stops getting done.

**Show the work set and confirm before fanning out.** A short table: unit, PRs in it, author,
brief freshness if known, why anything was skipped. This is the last cheap moment to drop
something.

## Step B2: Fan out the prep

One subagent per **unit of work**, not per PR. Siblings go to the same agent so it can judge
acceptance-criteria coverage across all the repos the ticket touches. Send every agent in a
single message so they run concurrently.

Use the `general-purpose` agent type. Each prompt must state these limits, because a subagent
cannot ask and will otherwise improvise:

- **Read-only on GitHub.** No comment, no review event, no label change, no PR or issue edit.
  Writing is the main session's job, after the user rules.
- **No `AskUserQuestion`.** The agent has no path to the user. Anything unresolved comes back as
  a question in the return payload, not a guess.
- **Do Steps 1 and 2 of `SKILL.md` only.** Load the brief, compare its SHA to head, spot-check
  every "not covered anywhere" acceptance-criteria item against the diff. Do not re-audit a
  brief that matches head. Do not decide anything.
- **Resolve and probe the preview URL for every PR in the unit**, per `pr-prereview`'s
  `references/preview-environments.md`: bot-posted link in the PR comments first, repo pattern
  second, and verify it answers. A URL that 404s comes back marked broken. This is the single
  most important thing the agent returns, see Step B3.
- **Missing brief:** run `pr-prereview {repo}#{number} --dry-run`, which writes the brief locally
  and touches nothing on GitHub. If more than two units need a dry run, tell the user the batch
  will take noticeably longer before starting.

Have each agent return this shape, so Step B3 can assemble the sitting without reopening any PR:

```
unit:            ticket number, or "none" if the title carries no number
prs:             repo, number, url, headSha, author, assignee, current labels, demo-only?
briefState:      fresh | stale | absent
environment:     per PR: kind (multidev | storybook | via-sibling | none),
                 full resolved URL, probed yes/no, what it cannot show
acCoverage:      per AC item: covered yes/no/partial, and where
confirmedGaps:   only gaps actually spot-checked against the diff
heldCalls:       the brief's product calls, each already phrased as a question
findingsForDev:  file:line, what to change, why, blocking yes/no
followUps:       visreg coverage gap, documentation gap
draftTestSteps:  per step: full URL, action, expected result, role needed
```

**Isolate failures.** One agent erroring out does not end the batch. Report that unit as prep
failed, carry on with the rest, and offer to retry it single-PR at the end.

## Step B3: The grouped testing sitting

One walkthrough for the whole batch, grouped by environment so the user is not bouncing between
a multidev, a Storybook preview, and a CMS login six times over. This is batch mode's headline
output, the same way Step 3 is single-PR mode's.

### Every block leads with its own full URL

In a single-PR review the environment is obvious from context. Across six PRs in four repos it
is not, and "open the multidev" is useless when there are four different multidevs in play. So:

- **Write the complete clickable URL every time.** Never "the multidev," never "the preview,"
  never "the usual place."
- **Use the URL the prep agent probed.** Do not rebuild it from the pattern and do not guess a
  visreg slug. A wrong URL costs the user a tab, a 404, and their trust in the rest of the plan.
- **`yalesites-project`:** the Pantheon multidev, deep-linked to the page that actually shows the
  change, `https://pr-{NUMBER}-yalesites-platform.pantheonsite.io/blocks-for-visreg/{slug}` or
  `/content-types/{slug}`, not the homepage.
- **`component-library-twig`:** the Netlify deploy preview,
  `https://deploy-preview-{NUMBER}--dev-component-library-twig.netlify.app`. Say in the group
  heading that it is Storybook only, and name what it cannot show: Layout Builder placement,
  editor-facing field labels, role gating, anything needing Drupal to pass real values in.
- **`atomic`:** no environment of its own. Give the sibling `yalesites-project` PR's multidev URL
  **and name that sibling PR**, so it is clear why the number in the URL does not match the PR
  under review.
- **`tokens`:** same, through the sibling `component-library-twig` preview.
- **No sibling, or a probe that did not answer:** say there is no deployed way to see this and
  that it is local-only. Never print a link that failed its probe.

### Shape of the sitting

Order the groups multidev, then Storybook, then via-sibling, then nothing-deployed, so the dead
ends sit at the end instead of interrupting the flow.

```
## Testing sitting: 4 units, about 25 minutes

### Pantheon multidev, the full CMS
**yalesites-project#1560** (ticket 1648, with clt#728 below)
https://pr-1560-yalesites-platform.pantheonsite.io/blocks-for-visreg/accordion
1. Open the URL above. Each table header should carry scope="col".
2. Drag the block into a 33% section. Expected: no horizontal scroll at 1440px or 360px.
3. Log in as an **editor, not platform admin**. Expected: the new control is visible.

### Storybook only, cannot show Layout Builder placement, editor field labels, or role gating
**component-library-twig#728** (ticket 1648, sibling of ysp#1560 above)
https://deploy-preview-728--dev-component-library-twig.netlify.app
4. Open the Accordion story. Expected: the new variant appears in the controls panel.

### No environment of its own, test through the sibling
**atomic#521** (ticket 1652) via yalesites-project#1571's multidev
https://pr-1571-yalesites-platform.pantheonsite.io/content-types/profile
5. ...

### Nothing deployed
**tokens#94** (ticket 1660): no sibling component-library-twig PR is open, so there is no
deployed way to see this change. Local only, or wait for the sibling.
```

Rules that keep this useful instead of noise:

- **Number steps continuously across the whole sitting**, so the user can say "step 7 failed"
  without naming a PR.
- **Flag every step needing a role other than platform admin**, every time. The user is a
  platform admin by default, so a role-gated step passes silently for them and fails for
  everyone else. In a six-PR sitting this is the thing most likely to slip.
- **Give a total estimate and a per-unit one.** Over about thirty minutes total, say so and offer
  to split the batch in half rather than pushing through.
- **Cut hard.** The draft steps from six briefs concatenated are far too long. Drop anything CI
  or the audit already proved from the code, and say that is why it is not listed.
- **This stays in chat.** Do not post the sitting to GitHub, and do not copy it onto a ticket as
  Release Testing Steps. `release-prep` owns those.

## Step B4: Batch the held calls

`AskUserQuestion` takes at most four questions per call, so group the units' held calls into
rounds of four.

- **Name the PR in every header.** Four questions can span four different PRs and a header of
  just "Copy" is unreadable in that context. Headers cap at twelve characters, so `1560 copy`,
  `728 default`, `521 gating`.
- **Keep a unit's questions together** in one round rather than interleaving units, so the user
  is not context-switching inside a single round. A unit with more than four held calls gets a
  round to itself.
- **Empty is a real answer.** If a unit's brief held nothing, say so for that unit instead of
  inventing a question to fill the round.
- **Filter to the reviewer's dimensions from Step B0, then list what that set aside.** Per
  `SKILL.md` Step 3b, out-of-lane calls are named with their dimension and owner, never dropped.
  In a batch this list is long enough to want its own block rather than a line per round, so
  collect it across all units and present it once after the last round:

  ```
  Outside your lane across this batch, left for whoever owns them:
  - ysp#1560: the `--variant` default (code, lead developer)
  - clt#728: 12px heading gap (design, April)
  - atomic#521: focus order on the new dropdown (a11y)
  ```

  Then offer, once for the batch, to flag them on their PRs as plain non-blocking comments.
- **A unit whose every held call is out of lane is not an empty unit.** Say which it is, because
  otherwise a fully-out-of-lane unit and a unit the audit held nothing on look identical, and only
  one of them is actually clear.

Then ask once, for the whole batch, what they noticed during the sitting, with room to attach
notes per PR. Their own read is a first-class input here exactly as it is in single-PR mode.

## Step B5: Rule on each unit, then post it

**Run Step 6's write-path preflight once for the whole batch**, not per unit. `gh auth status`
does not change between units, and on the connector fallback path the user needs to hear once
that writes may 403 and that you will confirm each one, rather than six times.

Walk the units one at a time. For each:

1. Present the assembled feedback per `SKILL.md` Step 4, blocking separated from optional.
2. **Ask for the ruling on this unit.** Approve, or request changes. One unit, one question, in
   the user's own words back to them. Never roll several units into one ask.
3. Post per Steps 6 through 9. Every PR in the unit gets the same outcome.
4. Only then move to the next unit.

**Siblings share the outcome but not the labels.** The pass label comes from the reviewer's
dimensions and the repo's label set together, per `SKILL.md` Step 8 and
`reviewer-roles.md`, so it differs across the PRs inside a single unit. A `design` reviewer's
approval of a unit spanning `yalesites-project` and `component-library-twig` puts
`pass design review` on the `component-library-twig` PR and **no pass label at all** on the
`yalesites-project` one, because that repo does not define it. That asymmetry is correct, and it
is the thing in batch mode most likely to look like a bug. Say it out loud when it happens.

Getting the label set wrong is batch mode's most likely mechanical error, so recompute it per PR
from Step 8's tables rather than reusing the previous unit's, and never substitute a label the
repo happens to define for one it does not.

**Isolate posting failures.** If one unit's `gh` write fails, triage it against Step 9's error
table, report it, keep the drafted body and computed label set, and continue the batch. Never
abandon five posted reviews because the sixth failed to write.

**Verify every unit's labels before moving on.** Step 8's `PUT` will silently create a label the
repo does not define, so a label set reused from a unit in a different repo does not error, it
just lands wrong. In a six-unit batch that is the mistake most likely to go unnoticed, so run
Step 8's verify query per PR rather than at the end.

**Ticket sync once per ticket.** Step 9b runs per unit after its review posts. When several
units in the batch hang off the same epic, hand `ticket-sync` all of them together so the epic
gets one comment rather than one per child.

## Step B6: Report the batch

Close with a table, not prose:

| Unit | PRs | Outcome | Labels applied | Mentioned | Ticket synced |
|---|---|---|---|---|---|

Then, briefly: what rolled over past the cap, which units had prep or posting failures and what
the user can do about them, any follow-up tickets offered or created, anything still waiting
on a decision, and, if the batch was scoped, which dimensions each unit still needs a pass from. **Say explicitly if the batch ended partially done.** A batch that quietly reports
success while two units never got a ruling is worse than one that says it stopped halfway.

## The five ways batch mode goes wrong

1. **Blanket approval.** The likeliest and most expensive failure. One explicit ruling per unit.
2. **The wrong pass label**, because the previous unit's label set got reused, or because the
   label was picked from the repo without checking the reviewer's dimensions.
3. **A guessed or stale URL.** Cheapest to avoid, most corrosive to the user's confidence in the
   rest of the plan.
4. **A sibling judged in isolation**, producing a false unaddressed-AC finding and a wasted
   developer round trip.
5. **Silent partial completion.** Report what did not finish, every time.
