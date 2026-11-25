# Scoping the review to the reviewer (Step 0 detail)

Read this from `SKILL.md` Step 0. It holds the full resolution order, the guardrail for an
unmatched reviewer, the announce lines, the `--as` override, and what the rest of the skill does
with the scope.

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
| 2 | **The shared login map** | The reviewer login (`reviewer_login` in `config.md`, default `gh api user --jq .login`), looked up in `reviewer-roles.md` |
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
