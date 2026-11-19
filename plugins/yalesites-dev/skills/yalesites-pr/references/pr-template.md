# YaleSites PR Template

See `github-communication-format.md` for the reasoning: the body leads with a TL;DR, keeps
the "Description of work" bullets and "Functional testing steps" visible, and pushes any
granular change notes into a collapsed `Detailed changes` block.

See `github-writing.md` for the words: active voice, simple tenses, no em dashes, the
word-swap table, and 350 words as the budget for everything visible before a reviewer
expands anything.

See `preview-urls.md` for the testing steps: link a step's text to the exact multidev route
or Storybook story it exercises, so the reviewer lands on the work instead of hunting for
it. The URLs below carry real PR numbers only once the PRs exist and the skill
substitutes them.

## With associated issue

```
## [NNN: Issue Title](https://github.com/yalesites-org/YaleSites-Internal/issues/NNN)

**TL;DR:** One or two sentences — what this PR does and why it matters.

### Description of work
- Bullet describing what was added or fixed

### Functional testing steps:
- [ ] [Step that starts the job](https://pr-NNN-yalesites-platform.pantheonsite.io/node/add/page), linked to where it happens
- [ ] Step 2
- [ ] Step 3

References yalesites-org/YaleSites-Internal#NNN
```

## Without associated issue

```
## Brief description of the change

**TL;DR:** One or two sentences — what this PR does and why it matters.

### Description of work
- Bullet describing what was added or fixed

### Functional testing steps:
- [ ] [Step that starts the job](https://pr-NNN-yalesites-platform.pantheonsite.io/node/add/page), linked to where it happens
- [ ] Step 2
- [ ] Step 3
```

## Optional: collapsed detail

When there are finer-grained notes worth keeping but not worth putting in front of every
reviewer, add this after "Description of work" (leave the blank lines — GitHub needs them
to render the contents):

```
<details>
<summary><b>Detailed changes</b></summary>

- Longer per-area notes here

</details>
```

## Cross-repo PRs

When changes span multiple repos, add inside "Description of work":

```
- Other work completed in: yalesites-org/REPO#NNN
```

## Multidev-only PR

For the yalesites-project PR that exists only so a companion PR (atomic, component-library-twig,
tokens) gets a multidev. It has no code. Rules, all required:

- **Title:** the usual `{issue number}: {issue title}` plus the suffix ` — For multidev only`
  (`/merge-prs` closes PRs whose title matches `/multidev only/i` instead of merging them).
  The H2 link text in the body matches the title.
- **Label:** `don't merge` instead of `needs review`, applied at creation
  (`--label "don't merge"`). Never `needs review`: there is nothing to review, and the
  review queue would pick it up. `/prove-my-prs` and `/merge-prs` key off `don't merge`.
- **Draft**, same reviewer as the companion PR, and the real PR number in the multidev URL
  (Step 7).

```
## [{issue number}: {issue title} — For multidev only](https://github.com/yalesites-org/YaleSites-Internal/issues/{NNN})

**TL;DR:** Multidev only. This PR has no code change. It builds the matching {companion repo} branch into a multidev so the change can be tested in Drupal.

### Description of work
- No yalesites-project change. CI builds the same-named {companion repo} branch into this PR's multidev.
- Other work completed in: yalesites-org/{companion repo}#{N}

### Functional testing steps:
- [ ] (The companion PR's steps, rewritten to run on `https://pr-<N>-yalesites-platform.pantheonsite.io`.)

References yalesites-org/YaleSites-Internal#{NNN}

Created with AI
```
