---
name: pr-brief
description: "Write the local pre-review brief for one YaleSites PR: read the diff and linked issue, map the acceptance criteria, list mechanical findings, the regression surface, where to test, a draft test plan, and the product calls held for a human. Writes one markdown file and nothing else. Never posts to GitHub, comments, or changes labels or assignees. Used by pr-feedback when no current brief exists; also runnable on its own, e.g. 'brief PR 1560', 'write a pre-review brief for clt 728'."
argument-hint: "<repo>#<number> [--dry-run is accepted and ignored: this skill never posts]"
---

# PR brief

Writes the brief `pr-feedback` starts from, so the human review is judgment, not homework. The
file format is the contract in `../pr-feedback/references/brief-format.md`. Read it first and
follow it exactly.

**This skill is read-only on GitHub.** No comment, no review, no label, no assignee, no edit to a
PR or issue. Its only output is one local file. `--dry-run` is accepted so callers can pass it,
and changes nothing.

**Repos:** `yalesites-project`, `component-library-twig`, `atomic`, `tokens`, `yale-ui-cl`.
Issues live in `yalesites-org/YaleSites-Internal`, except a `yale-ui-cl` PR's issue, which lives
in `yalesites-org/yale-ui-cl`. If the repo is not clear, ask. Do not guess.

## Step 1: Read the PR, its siblings, and the issue

```bash
gh pr view NUMBER --repo yalesites-org/REPO \
  --json title,body,author,assignees,labels,headRefOid,files,url
gh pr diff NUMBER --repo yalesites-org/REPO
gh pr checks NUMBER --repo yalesites-org/REPO
```

- Read the whole diff, not just the file list.
- Find the linked issue in the PR body (usually `## [#NNNN :: Title](url)`) and read it with
  `gh issue view NNNN --repo yalesites-org/YaleSites-Internal --json title,body,labels`. No linked
  issue is itself worth noting under **Your calls**.
- **Siblings:** open PRs in the other repos whose title carries the same ticket number. Read
  their diffs too. Acceptance criteria are often split across repos.
- For `yale-ui-cl`, also read the PR's existing review threads, so the brief does not repeat
  what is already open there.

## Step 2: Work through the diff

- **AC coverage.** For each acceptance criterion: covered here (`file:line`), covered in a
  sibling (`repo#number`), or not covered anywhere.
- **Regression surface.** For each shared thing the diff touches (a component, an SCSS partial,
  a form alter, a service, a config default), grep for every other consumer and name each one.
- **Edge cases.** Empty states, role gating, accessibility (labels, headings, `scope`, focus,
  alt text), small screens, long content.
- **CI claims.** Before saying a check covers something, read its workflow file's triggers and
  path filters.
- **Answer your own questions first.** Check the diff, the repo, the issue thread, and sibling
  PRs. Record each as answered (with what you checked) or held for a human.
- **`yale-ui-cl` only:** build the Parity map against the matching Twig Storybook story and the
  YaleSites option set (`ys_themes.component_overrides.yml` in `yalesites-project`). Sort each
  difference into one of the four kinds in `brief-format.md`.

## Step 3: Sort what you found

| Kind | Goes under |
|---|---|
| Mechanical: exact file and line, a concrete wrong behavior, no guess about intent | **Acceptance criteria coverage** (as not covered) or **Your calls**, stated as a finding with `file:line` |
| A question you answered yourself | **Already answered, no action needed** |
| Copy, defaults, role gating, scope, UX, or anything you are unsure of | **Your calls**, as a question |
| Missing visreg test content, or a docs item the AC asks for | **Follow-ups worth a ticket** |

Never send a finding to the developer. That is the reviewer's call, made in `pr-feedback`.

## Step 4: Where to test and the draft plan

Resolve the environment by probing, per `../pr-feedback/references/preview-environments.md`. A
URL that does not answer is worse than "no environment". Then draft the test plan: AC first, one
step per regression consumer, then the rows from `../pr-feedback/references/beyond-ac-checks.md`
whose trigger matches the diff. Mark each step AC, regression, or row N, and name any step that
needs a role other than platform admin. Keep it a draft.

## Step 5: Write the file

Write to `<brief_dir>/<repo>-<number>.md`. `brief_dir` comes from
`~/.claude/yalesites/pr-feedback/config.json`, default `~/.claude/yalesites/pr-feedback/briefs`.
Create the folder if needed. Overwrite any older brief for the PR. Use the header and section
order from `brief-format.md`, with **Written by:** `pr-brief` and **Audit outcome:** `local brief
only, nothing posted`. Write `None.` under an empty section.

Write as an observer ("the template does not guard..."), not as the reviewer. No em dashes.

## Step 6: Report

One short paragraph: the file path, the SHA, how many AC items are not covered, how many calls
are held, and the environment URL. When `pr-feedback` called this skill, return to it.
