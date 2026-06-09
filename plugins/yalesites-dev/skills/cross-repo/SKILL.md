---
name: cross-repo
description: >
  Manage branches and check status across all YaleSites repos (yalesites-project, atomic,
  component-library-twig, tokens) at once. Use this skill whenever the user asks about branch
  status across repos, wants to create matching branches in multiple repos, clean up old branches,
  or check what state the repos are in. Also trigger on: "cross-repo", "all repos", "repo status",
  "branch in all repos", "sync branches", "clean branches", "what branch am I on in all repos",
  "check the repos".
argument-hint: "[status | branch <name> | clean]"
allowed-tools:
  - Bash(git *)
  - Bash(git -C *)
---

# Cross-Repo Management

Manage branches and check status across the 4 YaleSites repositories simultaneously.

## Repository Detection

From the yalesites-project git root, the repos are accessed via convenience symlinks:

| Repo | Symlink | Remote |
|---|---|---|
| yalesites-project | `.` (git root) | yalesites-org/yalesites-project |
| atomic | `./atomic` | yalesites-org/atomic |
| component-library-twig | `./component-library-twig` | yalesites-org/component-library-twig |
| tokens | `./tokens` | yalesites-org/tokens |

These symlinks only exist in the local dev environment. The actual git repos live deeper
in the tree (`web/themes/contrib/atomic`, etc.), but always use the symlinks for commands.

**Important:** `tokens` uses `main` as its default branch. The other 3 use `develop`.

### Detecting available repos

Before running any command, check which repos are actually present as standalone git repos.
A repo is available if:
1. The symlink path exists
2. `git -C <path> rev-parse --git-dir` succeeds
3. `git -C <path> rev-parse --show-toplevel` returns a path DIFFERENT from the yalesites-project root
   (if it returns the yalesites-project root, the directory is part of the parent repo — not its own repo)

Exception: yalesites-project itself is always available (it IS the root).

If a repo isn't available, include it in the output as "not set up" rather than silently
skipping it — the user should know if a repo is missing so they can run their sync script.

---

## Commands

### `status` (default — runs when no subcommand is given)

For each available repo, run these commands (all repos can be queried in parallel):

```bash
git -C <path> branch --show-current
git -C <path> status --porcelain
git -C <path> rev-list --left-right --count HEAD...@{upstream} 2>/dev/null
```

Present as a compact table:

```
Cross-Repo Branch Status
========================

Repo                      Branch                      Status    Remote
yalesites-project         1188-text-button-refactor    clean     up to date
atomic                    1188-text-button-refactor    2 mod     1 ahead
component-library-twig    develop                      clean     up to date
tokens                    main                         clean     up to date
```

Status column rules:
- "clean" = no modified, staged, or untracked files
- "N mod" = N modified or staged files
- "N new" = N untracked files (show alongside mod count if both exist, e.g. "2 mod, 1 new")

Remote column rules:
- "up to date" = 0 ahead, 0 behind
- "N ahead" = N commits ahead of upstream
- "N behind" = N commits behind upstream
- "N ahead, M behind" = diverged
- "no upstream" = no tracking branch set
- Do NOT use arrow symbols — they don't render well in all terminals

After the table, if any repos are on a different branch than yalesites-project, add a note:

```
Note: component-library-twig is on `develop`, tokens is on `main`
      (yalesites-project is on `1188-text-button-refactor`)
```

Only include repos whose branch genuinely differs — don't flag `tokens` for being on `main`
if yalesites-project is also on its own default branch (`develop`). The point is to highlight
repos that haven't been switched to a feature branch yet.

### `branch <name>`

Create a new branch in selected repos.

1. For each available repo, check the current state:
   - Already on a branch named `<name>`? Mark as "already on this branch"
   - On a different non-default branch? Mark as "on another branch" (needs attention)
   - On the default branch (`develop` or `main`)? Mark as "ready"

2. Present the plan and ask for confirmation via AskUserQuestion (multiSelect):
   - Pre-select repos marked "ready"
   - Include "already on this branch" repos as unselected with a note
   - Include "on another branch" repos as unselected with a warning

3. For each confirmed repo:
   ```bash
   git -C <path> checkout -b <name>
   ```
   Uncommitted changes will carry over to the new branch, which is usually intended.

4. Report results:
   ```
   Created branch `1188-new-feature`:
     yalesites-project          created (from develop)
     atomic                     created (from develop)
     component-library-twig     already on this branch
     tokens                     skipped
   ```

### `clean`

Remove local branches whose remote tracking branch has been deleted (merged and cleaned up
upstream).

1. Fetch and prune all repos in parallel:
   ```bash
   git -C <path> fetch --prune
   ```

2. Find gone branches in each repo:
   ```bash
   git -C <path> branch -vv | grep ': gone]'
   ```

3. Present findings:
   ```
   Branches with deleted remotes:

   yalesites-project:
     - 1150-old-feature
     - 1160-another-fix

   atomic:
     - 1150-old-feature

   component-library-twig: (none)
   tokens: (none)
   ```

4. If branches were found, ask for confirmation before deleting — this is destructive.

5. For each confirmed branch, check it's not the current branch, then delete:
   ```bash
   git -C <path> branch -D <branch-name>
   ```

6. If deleting the current branch in any repo, switch to the default branch first:
   ```bash
   git -C <path> checkout <default-branch>
   git -C <path> branch -D <branch-name>
   ```

7. Report what was cleaned:
   ```
   Cleaned 3 branches across 2 repos.
   ```
