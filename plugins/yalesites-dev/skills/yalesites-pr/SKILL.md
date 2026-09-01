---
name: yalesites-pr
description: Use when creating pull requests in YaleSites repositories (yalesites-project, atomic, component-library-twig, tokens)
disable-model-invocation: false
argument-hint: "[issue-number (optional — parsed from branch if omitted)]"
allowed-tools:
  - Bash(git branch *)
  - Bash(git -C * branch *)
  - Bash(git push *)
  - Bash(git -C * push *)
  - Bash(gh issue view *)
  - Bash(gh issue create *)
  - Bash(gh issue edit *)
  - Bash(gh issue comment *)
  - Bash(gh pr create *)
  - Bash(gh pr edit *)
  - Bash(git log *)
---

# YaleSites PR

Creates pull requests following YaleSites conventions. See references/pr-template.md for the full template.

## Steps

1. **Determine the issue number**
   - Parse from the current branch name: `git branch --show-current`
   - Branch format is `{issue-number}-{short-description}` — the number is the prefix
   - If the branch **does not** start with a number, **stop and warn the user:**

     > **No issue found for this branch.**
     >
     > Issues are important — they provide traceability, give reviewers context, and ensure work is tracked before it's merged. Every PR should ideally have one.
     >
     > Would you like me to create an issue in yalesites-org/YaleSites-Internal based on the work in this branch? I can summarize the commits and draft one for you. Or you can create one manually and re-run this skill.
     >
     > Options:
     > 1. Create an issue for me, then continue with the PR
     > 2. I'll create the issue myself — stop here
     > 3. Proceed without an issue anyway

   - If the user chooses **option 1**: summarize the branch commits (`git log main..HEAD --oneline`), draft an issue title and body, and **show it to the user for approval before creating anything**. Only run `gh issue create` after the user explicitly confirms the draft. Capture the new issue number, then continue
   - If the user chooses **option 2**: stop — do not create the PR
   - If the user chooses **option 3**: continue without an issue (use the no-issue template variant)

2. **Fetch the issue title** (only if an issue number was found)
   ```bash
   gh issue view {NNN} --repo yalesites-org/YaleSites-Internal --json title -q .title
   ```

3. **Detect cross-repo changes**
   - Check if the same branch exists with commits in any other repos (atomic, component-library-twig, tokens)
   - If so, those repos get PRs first — yalesites-project is always last (its CI/CD picks up companion branches during build)

4. **Push the branch** in each affected repo if not already pushed
   ```bash
   git push -u origin {branch}
   git -C {repo-path} push -u origin {branch}
   ```

5. **Draft and create PRs** — companion repos first, yalesites-project last
   For each repo, draft the full PR title and body using the template from references/pr-template.md, then **show the draft to the user and wait for explicit approval before running `gh pr create`**. Do not create any PR without confirmation.
   Each PR must include:
   - `--assignee @me`
   - `--base develop`
   - Title format: `{issue number}: {issue title}` — identical to the H2 link text in the PR body (e.g. `1025: Ensure Event Date/Time Changes in Campus Groups Sync to Website`). Do not use conventional commit style for the PR title.
   - "Other work completed in: yalesites-org/REPO#NNN" for each companion PR (added after all PRs exist)
   - `References yalesites-org/YaleSites-Internal#NNN` at the end of every body (omit if no issue)

6. **Update cross-links** — once all PRs exist, edit each body to add the companion links:
   ```bash
   gh pr edit {NNN} --repo yalesites-org/{repo} --body "..."
   ```

7. **Check whether the issue needs to catch up** (only if an issue number was found, and the `yalesites-product` plugin's `ticket-sync` skill is available)
   Load the `ticket-sync` skill and hand it the issue number and the PR body/bodies just created in Step 5 as the "what actually happened" input, to compare against the issue's Description and Acceptance Criteria. Fetch the full body first, since Step 2 only pulled the title:
   ```bash
   gh issue view {NNN} --repo yalesites-org/YaleSites-Internal --json body -q .body
   ```
   This catches cases where implementation drifted from the original ask during development — common on longer-running tickets — before the issue moves forward looking finished but describing something slightly different from what shipped.

   Non-blocking and silent if nothing has drifted. If something has, `ticket-sync` decides comment vs. edit and drafts the text for your approval — use `gh issue edit` for a scope/acceptance-criteria change or `gh issue comment` for context only. If the `ticket-sync` skill isn't available in this session, skip this step rather than attempting the comparison ad hoc.

8. **Move the issue to "In review"** (only if an issue number was found)
   Once the PR(s) exist, the solution is ready for review, so set the issue's status to **In review** on the YaleSites Board (GitHub Projects v2, org `yalesites-org`, project number 6) — but only if it is not already there.

   Check the current status first, and only write if it differs:

   ```bash
   # a. Current Status for this issue
   gh api graphql -f query='query { repository(owner:"yalesites-org", name:"YaleSites-Internal") { issue(number:NNN) { projectItems(first:10) { nodes { project { number } fieldValueByName(name:"Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } } } } } } }'

   # b. Only if it is not already "In review":
   gh project item-edit 6 --owner yalesites-org --url https://github.com/yalesites-org/YaleSites-Internal/issues/NNN --field "Status" --value "In review"
   ```

   - The option name is **"In review"**, lowercase "r". `--value` is matched against the configured option text, so the capitalization matters.
   - If the issue has no item in project 6, skip silently — nothing to move.
   - If it is already "In review", make no change.
   - `gh` needs the **`project` scope** for this write; `read:project` can read the board but not write to it. If the write fails, don't retry or troubleshoot the user's `gh` setup mid-task — report that the status wasn't moved and carry on. The PR itself is the important artifact.

   Full board reference (all Status options and their meanings, Priority/Size, reading current values, and which skill owns which transition) lives in the `ticket` skill's `references/board-status.md`, in the `yalesites-product` plugin. The command above is self-sufficient without it.
