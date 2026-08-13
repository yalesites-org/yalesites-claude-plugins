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

7. **Move the issue to "In review"** (only if an issue number was found)
   Once the PR(s) exist, the solution is ready for review, so set the issue's status to **In review** on the YaleSites Board (GitHub Projects v2, org `yalesites-org`, project number 6) — but only if it is not already there.

   Look the IDs up dynamically, then mutate only when the status actually differs:

   ```bash
   # a. Project id + Status field/options
   gh api graphql -f query='query { organization(login:"yalesites-org") { projectV2(number:6) { id field(name:"Status") { ... on ProjectV2SingleSelectField { id options { id name } } } } } }'

   # b. The issue's item in project 6 and its current Status
   gh api graphql -f query='query { repository(owner:"yalesites-org", name:"YaleSites-Internal") { issue(number:NNN) { projectItems(first:10) { nodes { id project { number } fieldValueByName(name:"Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } } } } } } }'

   # c. Only if that item's current Status is NOT already "In review", set it:
   gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input:{ projectId:"<PROJECT_ID>", itemId:"<ITEM_ID_IN_PROJECT_6>", fieldId:"<STATUS_FIELD_ID>", value:{ singleSelectOptionId:"<IN_REVIEW_OPTION_ID>" } }) { projectV2Item { id } } }'
   ```

   - If the issue has no item in project 6, skip silently — nothing to move.
   - If it is already "In review", make no change.
   - The option name is **"In review"** (lowercase "r"). As of this writing the project id is `PVT_kwDOA_XQ-s4A-PeJ`, the Status field id is `PVTSSF_lADOA_XQ-s4A-PeJzgxtHE8`, and the "In review" option id is `aba860b9` — but prefer the dynamic lookup above in case they change.
