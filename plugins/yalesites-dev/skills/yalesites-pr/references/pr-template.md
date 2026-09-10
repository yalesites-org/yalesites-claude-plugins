# YaleSites PR Template

See `github-communication-format.md` for the reasoning: the body leads with a TL;DR, keeps
the "Description of work" bullets and "Functional testing steps" visible, and pushes any
granular change notes into a collapsed `Detailed changes` block.

## With associated issue

```
## [NNN: Issue Title](https://github.com/yalesites-org/YaleSites-Internal/issues/NNN)

**TL;DR:** One or two sentences — what this PR does and why it matters.

### Description of work
- Bullet describing what was added or fixed

### Functional testing steps:
- [ ] Step 1
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
- [ ] Step 1
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
