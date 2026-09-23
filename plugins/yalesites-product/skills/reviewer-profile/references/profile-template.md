# The reviewer profile file

Lives at `~/.claude/yalesites/pr-feedback/reviewer-profile.md`. One per person, per machine.
Never committed to a repo, never posted to GitHub.

`pr-feedback` reads the frontmatter to decide what to ask and what to label, and reads the prose
to decide how to phrase it. Both halves matter: the frontmatter without the prose gives correct
labels and generic questions, the prose without the frontmatter gives good questions and wrong
labels.

## Schema

```markdown
---
login: miketullo95
role: Product Manager
dimensions: [functional, product]
not-mine: [code, design, a11y]
updated: 2026-09-21
---

## What I care about

Whether an editor can actually find and use the thing without being told it exists. Copy in the
UI, field labels, help text. Defaults, because most sites never change them. Whether the feature
works for a Site Editor and not just a platform admin.

## Always ask me about

- Anything that changes what an editor sees in Layout Builder or Manage Settings
- Role gating: who can see or do this, and was that deliberate
- New UI copy, before it ships rather than after

## Not my call, hand it to someone else

- Implementation approach, refactor strategy, anything architectural. That goes to our lead
  developer.
- Visual fidelity against the design files. That is April's.

## Tone

First person singular, direct, no ownership stamps. Matches my `michael-voice` skill.
```

## Field rules

| Field | Rule |
|---|---|
| `login` | The exact GitHub login, from `gh api user --jq .login`. Not a display name. This is how a profile is matched to the person running the skill. |
| `role` | Free text, one short phrase. Shown back to the user in Step 0 so they can see what matched. |
| `dimensions` | One or more of `code`, `functional`, `design`, `a11y`, `product`. These are the calls this person rules on, and they drive which `pass ___ review` label the review may apply. |
| `not-mine` | Dimensions this person explicitly wants left for someone else. Not simply the leftovers: an explicit list is how `pr-feedback` knows to name an out-of-lane call as out of lane rather than dropping it. |
| `updated` | Absolute date, `YYYY-MM-DD`. A profile more than a year old is worth re-running the interview on. |

The dimensions are defined in
`../../pr-feedback/references/reviewer-roles.md`. Do not invent a sixth one: `pr-feedback` maps
dimensions to labels from that file's matrix, and an unrecognized dimension maps to nothing.

## Prose sections

All four are optional, and a profile with only frontmatter is valid. They earn their place by
changing what `pr-feedback` asks rather than just describing the person.

| Section | What `pr-feedback` does with it |
|---|---|
| `## What I care about` | Weights which of the brief's held calls surface first, and what edge cases make the testing walkthrough |
| `## Always ask me about` | A hard floor. If the PR touches one of these, the question gets asked even when the brief did not hold it |
| `## Not my call, hand it to someone else` | Named out loud as out of lane, with who it belongs to, instead of being silently dropped |
| `## Tone` | How the posted review body reads. Named writing-voice skills are honored here |

## A note on honesty

The point of `not-mine` is to make the posted review claim only what the reviewer checked. Padding
`dimensions` with things you do not really review defeats that, and the cost lands on someone
else: a `pass a11y review` label on a PR nobody checked for keyboard access reads, to the next
person, as a completed check. Under-claiming costs nothing. Over-claiming costs a real check.
