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

Closes yalesites-org/YaleSites-Internal#NNN
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
