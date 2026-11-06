---
name: yalesites-pr
description: Use when creating pull requests in YaleSites repositories (yalesites-project, atomic, component-library-twig, tokens)
disable-model-invocation: false
argument-hint: "[issue-number (optional, parsed from branch if omitted)] [--unattended] [--body-file <path>]"
allowed-tools:
  - Bash(git branch *)
  - Bash(git -C * branch *)
  - Bash(git push *)
  - Bash(git -C * push *)
  - Bash(git diff *)
  - Bash(git -C * diff *)
  - Bash(git -C * fetch *)
  - Bash(git -C * grep *)
  - Bash(git -C * worktree add *)
  - Bash(git -C * worktree remove *)
  - Bash(grep *)
  - Bash(cut *)
  - Bash(git -C * switch *)
  - Bash(git -C * add docs/adr)
  - Bash(git -C * rm *)
  - Bash(git -C * commit *)
  - Bash(git rm *)
  - Bash(git commit *)
  - Bash(gh repo clone yalesites-org/YaleSites-Internal *)
  - Bash(gh pr list *)
  - Bash(mkdir -p */YaleSites-Internal/docs/adr)
  - Bash(cp * */YaleSites-Internal/docs/adr/*)
  - Bash(gh issue view *)
  - Bash(gh issue create *)
  - Bash(gh issue edit *)
  - Bash(gh issue comment *)
  - Bash(gh pr create *)
  - Bash(gh pr edit *)
  - Bash(git log *)
---

# YaleSites PR

Creates pull requests following YaleSites conventions. See references/pr-template.md for the full template, references/github-communication-format.md for how the body is structured (TL;DR first, detail collapsed, machine-only payload in an HTML comment), references/github-writing.md for the words themselves (sentence caps, word swaps, a 350-word budget on the visible layer), and references/preview-urls.md for turning testing steps into links that land the reviewer on the change.

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

4. **ADR check** (always runs, with or without an issue, in the current repo plus every companion repo step 3 found)

   ADRs (architecture decision records) live in `yalesites-org/YaleSites-Internal` under `docs/adr/`, never in a product repo. What counts as an ADR path, an ADR heading, and a strong match is defined once, in the `yalesites` skill's `references/adr-conventions.md`; the commands below implement that definition and nothing else. `{base}` is the PR's base for that repo, defined once in step 6 and used here unchanged. Use `{branch}`, never `HEAD`: a companion checkout may have something else checked out.

   ```bash
   git -C {repo} fetch -q origin {base}
   git -C {repo} branch --list {branch}
   ```

   If that prints nothing, `{branch}` exists only on origin (common for a companion repo the dev never checked out). Make a local tracking branch first, so the commands below and the move read the same ref:

   ```bash
   git -C {repo} fetch -q origin {branch}
   git -C {repo} branch --track {branch} origin/{branch}
   ```

   Then detect:

   ```bash
   git -C {repo} diff --name-only --no-renames --diff-filter=A origin/{base}...{branch} -- '*.md'
   git -C {repo} diff --name-only --no-renames --diff-filter=A origin/{base}...{branch} -- '*.md' | grep -iE '(^|/)(adr|decisions)/|(^|/)adr-[^/]*\.md$'
   git -C {repo} grep -l -iE '^# (.*[^A-Za-z])?ADR([^A-Za-z]|$)|^# .*decision record' {branch} -- '*.md' | cut -d: -f2-
   ```

   The first command is the added list, the second the path matches, the third the heading matches (`git grep` prints `{branch}:path`, and `cut` drops the prefix so the paths compare as written). `--no-renames` makes a file moved into an ADR path count as added. A file in the added list that is in both the path and heading lists is a **strong match**; in only one, a **weak match**. Only added files count: an edit to an ADR that already exists in a product repo goes through, with a note in the PR body that the file should move in a follow-up.

   **Attended or unattended.** The run is unattended when the caller passes `--unattended`, or `--body-file` (an autonomous caller that pre-drafts the PR body); either one means nobody is there to answer, so the skill never pauses and appends its ADR note to the supplied body rather than writing its own. Without either, a user is present and every stop below is a real question.

   - **No match:** continue.
   - **Match, attended:** stop, show every matching file and repo, and offer to move each (below) and open the ADR PR in YaleSites-Internal instead. Only continue with a file in the product repo if the user explicitly says to.
   - **Match, unattended:** move only when there is exactly one strong match. A weak match, or more than one strong match, is left in place, named in the PR body, and logged for a person to decide. Every PR body this run opens says what was moved or flagged.

   The move uses a YaleSites-Internal checkout in `{scratch}`, the session's scratchpad folder named in the environment block (never the repo), cloned once per session and reused on a rerun or a second file. `{issue}` below is the issue number, or the branch slug when there is no issue, in the branch name, the file names, and both commit messages alike. One ADR branch per issue, `{adr-branch}`, holds every moved file: `{issue}-{slug}`, where `{slug}` is the issue title in kebab case, cut to four or five words (`1711-ai-readability-decision`); with no issue it is just `{issue}`, since that is already the branch slug. Each file is named `{issue}-{file-slug}.md`, where `{file-slug}` is its own basename without the extension and without any leading number (`docs/adr/0002-search.md` becomes `1711-search.md`). The product repo's checkout is never switched or dirtied:

   ```bash
   gh repo clone yalesites-org/YaleSites-Internal {scratch}/YaleSites-Internal   # skip if it exists
   git -C {scratch}/YaleSites-Internal fetch -q origin
   git -C {scratch}/YaleSites-Internal switch {adr-branch}                        # when origin/{adr-branch} exists (an earlier run pushed it): tracks it
   git -C {scratch}/YaleSites-Internal switch -c {adr-branch} origin/main         # only when no such branch exists on origin
   mkdir -p {scratch}/YaleSites-Internal/docs/adr
   git -C {repo} branch --show-current
   ```

   If that last command prints `{branch}` (the usual case: the dev runs this skill from the feature branch), work in `{repo}` itself:

   ```bash
   cp {repo}/{path} {scratch}/YaleSites-Internal/docs/adr/{issue}-{file-slug}.md
   git -C {scratch}/YaleSites-Internal add docs/adr
   git -C {scratch}/YaleSites-Internal commit -m "docs(adr): {issue} {short title}"
   git -C {scratch}/YaleSites-Internal push -u origin {adr-branch}
   git -C {repo} rm {path}
   git -C {repo} commit -m "chore({issue}): move ADR to YaleSites-Internal" -- {path}
   git -C {repo} push origin {branch}
   ```

   The `-- {path}` keeps anything the dev had staged out of the move commit. Otherwise (a companion repo with something else checked out) use a temporary worktree on the local `{branch}`, the same ref the detection read. `git worktree add` accepts it because that branch is not checked out anywhere, the commit advances the local ref, and the push is a fast-forward:

   ```bash
   git -C {repo} worktree add {scratch}/adr-move/{repo-name} {branch}
   cp {scratch}/adr-move/{repo-name}/{path} {scratch}/YaleSites-Internal/docs/adr/{issue}-{file-slug}.md
   git -C {scratch}/YaleSites-Internal add docs/adr
   git -C {scratch}/YaleSites-Internal commit -m "docs(adr): {issue} {short title}"
   git -C {scratch}/YaleSites-Internal push -u origin {adr-branch}
   git -C {scratch}/adr-move/{repo-name} rm {path}
   git -C {scratch}/adr-move/{repo-name} commit -m "chore({issue}): move ADR to YaleSites-Internal" -- {path}
   git -C {scratch}/adr-move/{repo-name} push origin {branch}
   git -C {repo} worktree remove {scratch}/adr-move/{repo-name}
   ```

   The ADR branch is pushed before the product branch loses the file, so a failure partway never leaves the ADR deleted from the product branch with no copy in YaleSites-Internal. The product push in either block is not optional: the branch is usually on origin already, so "push if not already pushed" in step 5 would skip it and the product PR would still ship the ADR. If the product branch held nothing but the ADR: skip its PR and leave that repo out of the step 7 cross-links. Delete the branch from origin only when `gh pr list --repo yalesites-org/{repo} --head {branch}` shows no open PR **and** the run is attended and the user confirms (`git -C {repo} push origin --delete {branch}`); an unattended run leaves the branch and says so in the ADR PR body. Step 6 opens the ADR PR against `main`.

5. **Push the branch** in each affected repo if not already pushed (a repo step 4 committed to was pushed there, and so was the ADR branch)
   ```bash
   git push -u origin {branch}
   git -C {repo-path} push -u origin {branch}
   ```

6. **Draft and create PRs** — companion repos first, yalesites-project last
   For each repo, draft the full PR title and body using the template from references/pr-template.md, then **show the draft to the user and wait for explicit approval before running `gh pr create`**. Do not create any PR without confirmation. The one exception is an unattended run (step 4: `--unattended` or `--body-file`): there is nobody to show it to, so use the supplied body as the PR body, append the step 4 ADR note to it, and create the PR without pausing.

   The body skeleton (with an issue; without one, swap the first line for `## Brief description of the change` and drop the `References` line). The `pr-body` checker fails a body missing either `###` heading, verbatim:

   ```
   ## [NNN: Issue Title](https://github.com/yalesites-org/YaleSites-Internal/issues/NNN)

   **TL;DR:** One or two sentences.

   ### Description of work
   - What was added or fixed

   ### Functional testing steps:
   - [ ] [Step](https://pr-NNN-yalesites-platform.pantheonsite.io/...), linked to where it happens

   References yalesites-org/YaleSites-Internal#NNN
   ```

   **The base is decided here, once.** `{base}` is the parent sub-issue branch when the work is stacked on one (the caller decides, not the script). Otherwise it is the output of `scripts/epic-branch.sh <issue> <repo>`, run per repo: the epic branch for work under an epic, and `develop` (`main` in tokens) for standalone or epic-level issues and when there is no issue. Step 4's detection diffs against the same `{base}`, so a tokens PR is never diffed against `main` and opened against `develop`. Step 4 runs the script without `--ensure`, so it creates nothing; if the epic branch does not exist yet in that repo, step 4 diffs against the repo's default branch, which the epic branch is cut from. Right before `gh pr create`, run it again with `--ensure`, companion repos first, which creates the epic branch and its draft Epic PR if missing.

   The body follows references/github-communication-format.md: a `**TL;DR:**` line under the H2 (one or two sentences, what the PR does and why), then the "Description of work" bullets and "Functional testing steps" visible as-is. If there are granular change notes worth keeping, put them in a collapsed `<details><summary><b>Detailed changes</b></summary>` block rather than expanding the bullet list. The H2 link line and the trailing `References ...` line stay visible.

   Write the words per references/github-writing.md: plain sentences, active voice, no em dashes, and 350 words as the budget for everything a reviewer sees before expanding anything. The reader is a developer peer, so normal technical vocabulary is fine, but do not narrate the diff. The diff is already there.

   Close the body with a `<!-- yalesites:agent -->` block holding the linked issue refs and any cross-repo companion branches. Check the draft before opening the PR:

   ```bash
   python3 scripts/check-github-text.py body.md --surface pr-body
   ```

   **Write the testing steps as links** — a step that names a place should link to it, so the
   reviewer lands on the change instead of hunting for it. references/preview-urls.md has the
   URL forms per repo, how to read a route out of a `*.routing.yml` and a Storybook slug out
   of a `.stories.js` `title`, and how to verify both. The PR numbers do not exist yet here,
   so draft with `<N>` placeholders and tell the user Step 7 fills them in.

   Each PR must include:
   - `--assignee @me`
   - `--base {base}` (as decided above)
   - When the base is an epic branch, add to Description of work: `- Part of epic yalesites-org/YaleSites-Internal#<epic> ; targets the epic branch <branch>.`
   - Title format: `{issue number}: {issue title}` — identical to the H2 link text in the PR body (e.g. `1025: Ensure Event Date/Time Changes in Campus Groups Sync to Website`). Do not use conventional commit style for the PR title.
   - "Other work completed in: yalesites-org/REPO#NNN" for each companion PR (added after all PRs exist)
   - `References yalesites-org/YaleSites-Internal#NNN` at the end of every body (omit if no issue)

   **An ADR PR from step 4 is the exception.** YaleSites-Internal has no `develop` branch and nothing deploys from it, so that PR uses `--repo yalesites-org/YaleSites-Internal --base main`, the same `{issue number}: {issue title}` title, and a body of a TL;DR line, a link to the ADR file on the branch, and the `References` line. No multidev, Netlify, or testing-step links. It gets the same `--assignee` and reviewer as the product PR and the `needs review` label, and an unattended run opens it without pausing. Once it exists, link it from the issue with `gh issue comment`. The full shape is in the `yalesites` skill's `references/adr-conventions.md`.

7. **Update cross-links and fill in the preview URLs** — once all PRs exist, every number is
   known. In one `gh pr edit` per repo, add the companion links **and** replace every `<N>`
   placeholder in the testing-step URLs with the real number (yalesites-project's number in a
   multidev URL, component-library-twig's in a Netlify URL):
   ```bash
   gh pr edit {NNN} --repo yalesites-org/{repo} --body "..."
   ```

   Then confirm no placeholder survived, and verify any Storybook link against the built
   preview's index if it is up (see references/preview-urls.md):
   ```bash
   gh pr view {NNN} --repo yalesites-org/{repo} --json body -q .body \
     | grep -nE '<N>|pr-<|deploy-preview-<'
   ```
   No output (exit 1) is the pass. A published body containing `<N>` is a broken link in
   front of every reviewer.

8. **Check whether the issue needs to catch up** (only if an issue number was found, and the `yalesites-product` plugin's `ticket-sync` skill is available)
   Load the `ticket-sync` skill and hand it the issue number and the PR body/bodies just created in Step 6 as the "what actually happened" input, to compare against the issue's Description and Acceptance Criteria. Fetch the full body first, since Step 2 only pulled the title:
   ```bash
   gh issue view {NNN} --repo yalesites-org/YaleSites-Internal --json body -q .body
   ```
   This catches cases where implementation drifted from the original ask during development — common on longer-running tickets — before the issue moves forward looking finished but describing something slightly different from what shipped.

   Non-blocking and silent if nothing has drifted. If something has, `ticket-sync` decides comment vs. edit and drafts the text for your approval — use `gh issue edit` for a scope/acceptance-criteria change or `gh issue comment` for context only. If the `ticket-sync` skill isn't available in this session, skip this step rather than attempting the comparison ad hoc.

9. **Move the issue to "In review"** (only if an issue number was found)
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

   Full board reference (all Status options and their meanings, Priority/Risk, reading current values, and which skill owns which transition) lives in the `ticket` skill's `references/board-status.md`, in the `yalesites-product` plugin. The command above is self-sufficient without it.
