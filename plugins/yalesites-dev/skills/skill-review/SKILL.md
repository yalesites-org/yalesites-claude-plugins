---
name: skill-review
description: "Pre-review a Claude Code skill change in yalesites-claude-plugins before the PR is opened, against the skill-authoring checklist built from three rounds of lead-developer review. Use when the user says 'review my skill before the PR', 'run the skill checklist', 'check this skill', 'pre-review this plugin change', 'is this skill ready for a PR', or has just finished a draft with the official skill-creator and wants it checked. Diffs the branch against main, walks every checklist item against the changed files, runs the commands the skill tells agents to run (on macOS, with its allowed-tools in hand), tests every regex against the known false positives, cross-checks every cited number, and reports findings in the reviewer's own shape. Posts nothing to GitHub."
argument-hint: "[branch or path to the changed skill (optional, defaults to the current branch against origin/main)]"
allowed-tools:
  - Bash(git fetch *)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git grep *)
  - Bash(grep *)
  - Bash(bash scripts/validate-plugins.sh)
  - Bash(bash scripts/run-skill-tests.sh)
  - Bash(bash scripts/sync-standards.sh *)
  - Bash(python3 *)
---

# Skill Review

A dry run of the lead developer's review, before the PR exists. The checklist in
`references/skill-authoring-checklist.md` carries the detail: thirteen defect classes plus a
section on what reviewers withdrew, each item a yes or no check with the PR it came from. This skill walks that list against a branch
and writes up what it finds. It changes nothing and posts nothing. The author decides what
to fix.

Read the checklist in full before Step 1. It is the review. This file is only the order of work.

## Step 1: Scope the diff

```bash
git fetch -q origin
git diff --name-only origin/main...HEAD
git log --oneline origin/main..HEAD
```

Group the changed files by skill. For each skill, read the whole SKILL.md and every changed
reference, not only the hunks. Half the findings in the source reviews were a changed
paragraph disagreeing with an unchanged one three sections away.

Note which plugin each changed file lives in. A pointer across plugins is checklist section 1.

## Step 2: Run what the repo already checks

```bash
bash scripts/validate-plugins.sh
bash scripts/run-skill-tests.sh
bash scripts/sync-standards.sh --check
```

A failure here is the first finding. Do not continue past a drift failure: the author edited a
generated copy, and every later finding on that file is on the wrong file.

## Step 3: Walk the checklist

Take the checklist section by section. For every item, decide pass, fail, or not applicable
to this diff, and keep a note of the fails. Four sections need more than reading:

**Commands (sections 4 and 5).** List every command the changed skill tells an agent to run.
For each one: find its `allowed-tools` entry, and run it on this Mac with the inputs the skill
describes. A `for` loop, a pipeline, or an `&&` chain in a command the agent must run under
`allowed-tools` is a fail even if it works in your shell. A prompt from the harness while you
run it is the finding. `\b` in `git grep -E`, `timeout`, `sed -i` with no argument, and
`sleep`-based waits are fails on sight.

**Regexes and match rules (section 7).** Write the checklist's false-positive inputs to a
scratch file (`loadRoutes.js`, `quadrant.twig`, `wrapped_image`, `https://site.edu.example.com/`,
a renamed file, a `## ADR links` heading in a README) with the Write tool, then run the skill's
own pattern against it with `grep`. A pattern that matches any of them is a fail. Then add the
real positives the skill names and make sure each is matched.

**Numbers (section 9).** Grep every number in the changed prose against the reference file it
came from, and every reference total against its source rows. Write down each pair. One base,
one count, one superlative that the table supports.

**Copies (section 2).** Pick a distinctive phrase from every rule the diff adds or edits and
`git grep -n` it across `plugins/` and `standards/`. More than one hit that is not a synced
copy is a fail.

## Step 4: Drop what a reviewer would withdraw

Before writing up, reread checklist section 14 and cut any finding that is:

- a scenario you could not make fail with a real input or a line in the files,
- about a case the file's own scope line excludes,
- about code the diff does not touch,
- a design suggestion or an efficiency nit,
- the same thread as another finding.

Eleven of 165 findings in the source reviews were withdrawn for these reasons. Do not make
the author read them.

## Step 5: Report, in chat only

One block per finding, in the shape the reviewer uses, ordered by the file and line it sits on:

```
**<One sentence: what is wrong and where, with file:line.>**

<The failure: the input, what the agent does with the text as written, what breaks.
Say "verified" and give the command when you ran it.>

Ask: <the change, concrete enough to make without a follow-up question.>
```

Lead the report with a TL;DR: the count of findings, the one or two that block the PR, and
whether the PR title type matches the CONTRIBUTING versioning table. Close with the checklist
items that passed by section, so the author can see what was covered.

Post nothing. No `gh pr comment`, no review, no label. This runs before the PR exists, and the
author owns every change. If they ask for a fix, hand the finding to the normal editing flow
and re-run this skill on the result.
