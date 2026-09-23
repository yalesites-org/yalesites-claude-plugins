---
name: reviewer-profile
description: "Builds or updates the personal reviewer profile that tells the pr-feedback skill what a given person actually reviews, so a design reviewer stops getting asked to rule on code and a developer stops getting asked to rule on UI copy. Use when someone wants to set up, see, change, or reset how PR review is tailored to them, e.g. 'set up my review profile', 'pr-feedback keeps asking me about code and that is not my call', 'what does Claude think I review', 'update my reviewer profile', 'stop asking me design questions on PRs'. Also invoked by pr-feedback itself when it finds no profile for whoever is running it. Interviews the person about their role, the review dimensions they own, what they explicitly want left for someone else, and their tone, then writes the profile file."
argument-hint: "[nothing to build or update, 'show' to print the current one]"
---

# Reviewer profile

## Overview

`pr-feedback` runs the same review for everyone by default: it asks every product and UX call
the automated pass held back, and stamps a pass label picked from the repo alone. That is wrong
in both directions. A design reviewer gets asked to gate code. A developer gets asked to rule on
editor-facing copy. And the posted label claims a check nobody performed.

This skill fixes that by writing down what one person actually reviews. It produces a single
file:

```
~/.claude/yalesites/pr-feedback/reviewer-profile.md
```

One per person, per machine. **It is local and it stays local.** Nothing here is committed to a
repo or posted to GitHub. The schema and every field rule live in
`references/profile-template.md`, and the five review dimensions are defined in
`../pr-feedback/references/reviewer-roles.md`. Read both before writing anything.

**The interview is short on purpose.** Four questions, not twelve. A profile that takes twenty
minutes to build does not get built, and a half-accurate profile is still a large improvement
over no profile at all. It can be re-run any time, so the first pass does not have to be
complete.

---

## Step 1: Work out what already exists

```bash
cat ~/.claude/yalesites/pr-feedback/reviewer-profile.md 2>/dev/null
gh api user --jq .login
```

| State | What to do |
|---|---|
| No file | Build one. Go to Step 2. |
| File exists, `login` matches | **Updating, not rebuilding.** Show the current profile, then ask what to change. Carry every answer they do not revisit. |
| File exists, `login` does not match | Two people share this machine account, or the login changed. Show both, ask which is right, do not overwrite on a guess. |
| `gh` not authenticated | Say so and ask for the login directly. The profile still works: `pr-feedback` matches it by the `login` field, and only needs `gh` to know who is running. |

If the user asked to **show** the profile rather than build one, print it and stop here.

## Step 2: Ask the four questions

Use `AskUserQuestion`. Offer the dimension list from
`../pr-feedback/references/reviewer-roles.md` with its one-line descriptions, because nobody
should have to guess what `functional` means as distinct from `product`.

1. **Which dimensions are yours to rule on?** Multi-select across `code`, `functional`, `design`,
   `a11y`, `product`. This is the one question with a mechanical consequence: it decides which
   `pass ___ review` label a review of theirs may apply.
2. **Which are explicitly not yours?** Multi-select over what is left. Ask it as its own
   question rather than inferring it from the leftovers. An explicit answer is what lets
   `pr-feedback` say "this one is out of my lane, it belongs to X" instead of dropping the call
   silently. Offer a "no strong feeling" option, which is a real answer.
3. **What do you care about most in a PR?** Free text, and prompt for specifics: a person, a
   role, a surface, a recurring thing they always end up catching. "Accessibility" is less
   useful than "keyboard order on anything with a dropdown."
4. **Anything you always want asked, even when nobody flagged it?** Free text. This becomes a
   hard floor in the review, so keep it to two or three items. Ten defeats the purpose.

**Offer their role as a fifth, quick confirmation**, prefilled from what they said. It is one
short phrase, shown back to them at the top of every scoped review, so it should read the way
they would introduce themselves.

**Do not ask about tone.** Check for a personal writing-voice skill instead (a
`*-voice` skill for this person) and record that if it exists. Ask about tone only if none does.

### What not to do in this interview

- **Do not infer dimensions from a job title.** A developer who does the team's accessibility
  passes owns `a11y` and their title never says so. Ask, take the answer.
- **Do not talk anyone into a broader profile.** Over-claiming is the failure mode that costs
  something. If they own one dimension, write down one.
- **Do not ask about `ready to merge`.** Whether one dimension's approval is enough to mark a PR
  merge-ready is a team-wide call, not a per-person setting. See the open question in
  `../pr-feedback/references/reviewer-roles.md`.

## Step 3: Write the file

Create the directory if it is not there, then write the profile per
`references/profile-template.md`: frontmatter first, then only the prose sections the interview
actually filled. Omit an empty section rather than writing a heading with nothing under it.

```bash
mkdir -p ~/.claude/yalesites/pr-feedback
```

Set `updated` to today's absolute date. Write `login` from Step 1, exactly as `gh` returned it.

## Step 4: Show them what it will change

Read the file back and, in chat, tell them concretely what is now different:

- The role and dimensions that matched.
- Which `pass ___ review` label a review of theirs will apply, **per repo**, from the matrix in
  `../pr-feedback/references/reviewer-roles.md`. Name the repos where their dimension has no
  label at all, because that is the surprising case: a design reviewer on `yalesites-project`
  gets no pass label, since only `component-library-twig` defines one.
- That out-of-lane calls will still be surfaced and named, not dropped.
- That `/pr-feedback 1560 --as code` overrides the scoping for one run, for when they are
  covering someone else's lane.

Then say it can be re-run any time with `/reviewer-profile`, and that deleting the file restores
the unscoped behavior exactly.

---

## Notes

- **A missing profile is not an error state.** `pr-feedback` without one does exactly what it
  does today, for everyone, ungated. This skill is an improvement on that baseline, never a
  precondition for it. Do not write a profile pre-emptively for someone who has not asked.
- **The profile is per machine.** Someone on a new laptop has no profile until they re-run this.
  The shared login-keyed table in `../pr-feedback/references/reviewer-roles.md` is the portable
  fallback that covers that gap, so a teammate who wants their scoping to travel should get a row
  there as well, with their handle confirmed by them.
- **`dimensions` is the only field with teeth.** Everything else shapes phrasing. If an interview
  gets cut short, get that one field right and leave the rest for a later pass.
- Never write a dimension that is not one of the five. `pr-feedback` maps dimensions to labels
  from the matrix and an unrecognized value maps to nothing, which silently produces an unlabeled
  approval.
