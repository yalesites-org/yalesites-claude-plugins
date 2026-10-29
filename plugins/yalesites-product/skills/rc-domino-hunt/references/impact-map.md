# Phase 1: the impact map

The goal is a list of every surface the RC changed, how each one was reached, and how many real sites would feel it. Build it by tracing files, not by guessing. Judgment comes in Phase 2, and only for what the trace cannot see.

Write the result to `impact-map.json` with the release branch head SHA, so later runs can tell whether it is stale.

## 1. The PRs in the release

```bash
git -C <yalesites-project checkout> fetch origin master <branch>
git -C <yalesites-project checkout> log --merges --format='%H %s' origin/master..origin/<branch>
```

With `--hotfix <PR>`, skip this range: the one PR is the whole list, and its diff comes from `gh pr diff <N>`. Save the PR head SHA in `impact-map.json` instead of the release branch head.

Pull the PR numbers from the merge commit subjects (`Merge pull request #<N> from <owner>/<head branch>`). Drop merges whose head branch is `develop`, `master`, or another `v<NNNN>` branch: those are syncs between branches (an RC update, a hotfix sync), not feature PRs. Their contents are already counted through the feature PRs they carry.

**On a `--dry-run`** the release branch is already merged into master, so `origin/master..origin/<branch>` is empty. Use the release PR's merge commit instead: `git log --merges <mergeCommit>^1..origin/<branch>`, with `mergeCommit` from `gh pr view <release PR> --json mergeCommit`. Then, for each PR, use `gh pr view <N> -R yalesites-org/yalesites-project --json title,body,files,closingIssuesReferences`. Read a local checkout that is up to date with the release branch. If the user's checkout is not clean, use a fetch plus `git show origin/<branch>:<path>`, and do not switch their branch.

## 2. The other repos the RC pulls in

yalesites-project does not commit a `composer.lock`, and the front end comes from three repos. Resolve the versions like this:

| Repo | Where the RC version comes from |
|---|---|
| atomic | `web/profiles/custom/yalesites_profile/composer.json`, the `yalesites-org/atomic` constraint. It is pinned exactly. Compare `origin/master` with `origin/<branch>`. |
| component-library-twig (CLT) | atomic's `package.json` has a caret range, so the version that ships is in atomic's lockfile **at the RC's atomic tag** (`package-lock.json` or `yarn.lock`). Read the lockfile at both tags (live's and the RC's). |
| tokens | The same again: CLT's lockfile at the two CLT versions found above. |

Then list the PRs merged into each repo between the two versions (`gh pr list -R yalesites-org/<repo> --state merged --search "merged:<from>..<to>"`, or the release notes between the two tags). If a version did not change, that repo has no surfaces in this RC.

## 3. Contrib and patches (the vendor diff)

Contrib and core patch bumps cause hotfixes too (yalesites-org/YaleSites-Internal#1791 came from a gin_lb major version plus a core patch revision). The repo diff alone does not show them, so diff them on their own:

- **Declared:** diff the `require` and `extra.patches` sections of `web/profiles/custom/yalesites_profile/composer.json` between `origin/master` and `origin/<branch>`, plus any changed file under the repo-root `patches/` folder (`patches/drupal-core/`, `patches/contrib/`).
- **Installed (attended mode only):** on two or three RC sites and their live envs, compare `terminus drush <site>.<env> -- pm:list --status=enabled --format=json` (the `version` field) and `drush status --field=drupal-version`. Floating constraints mean the installed versions can differ even when `composer.json` did not change. This reads production, which the permission check refuses in an unattended session, so in `--drain` skip it and note `installed versions not compared` in the report. The declared diff still runs.

Every module whose version or patch changed is a surface. Its blast radius is every page that uses what the module provides. For example: gin_lb is every Layout Builder screen, and views_ajax_history is every view with AJAX paging. Write it to `vendor-diff.json`.

## 4. Trace each change to blocks and pages

Trace outward, one hop at a time, and record each hop, so the report can say *why* a block is on the list:

| Changed file | Next hop |
|---|---|
| tokens (`tokens/**`) | the CLT components that use the changed token |
| CLT SCSS, JS, or Twig under `components/` | the CLT components that include or extend it (`{% include %}`, `{% embed %}`, `@import`, `@use`) |
| a CLT component | the atomic templates that include it (search atomic's `templates/` for the component path) |
| an atomic template | the block type, view mode, or content type it renders (`block--inline-block--<type>`, `node--<type>--<view-mode>`) |
| a yalesites-project custom module or config | the block types, forms, routes, views, or field storage it touches. Read the code. |
| an update hook (`hook_update_N`, `hook_post_update_NAME`, `hook_deploy_NAME`) | the entity types, fields, and config it loads or writes |
| a block type, view, or content type | the real pages that use it (below) |

**Wide triggers.** A change to a global token, theme-wide CSS (`base`, `global`, theme or color variables), or a Twig include used by more than about 15 components marks every block as touched. Do not try to trace that fan-out. Flag it as wide, and let Phase 2 sample it with pairwise combinations (see `charters.md`).

**Fan-out cap.** If any single trace reaches more than about 15 block types, stop tracing it and treat it as a wide trigger. Over-prediction is a known failure of this kind of analysis: one tool predicted 10,000+ tests for a single file.

**What the trace cannot see:** dynamic includes (template names built from variables), JS behaviors attached by selector, CSS that matches by attribute, and config that only applies on some sites. Note each one as `untraced` with the reason, and Phase 2 covers it by judgment.

## 5. Real pages and blast radius

Use the portfolio crawl (from the `yalesites-portfolio` skill):

- `~/code/yalesites-portfolio-data/dist/sites-index.csv`: the `blocks_used` column, per site. Count the sites that use each surface. That count is the blast radius.
- `~/code/yalesites-portfolio-data/raw/sites/<site>.json`: `pages[].url` and `pages[].blocks[].type` / `.attrs` (theme, variation, width). Use these to pick the exact RC pages a charter should visit.

Known gaps:

- Three RC sites are not in the crawl: `yalesites-platform`, `yalesites-sebastianna`, and `ys-wgss-yale-edu`.
- Several RC sites were crawled with a page cap (`capped.txt`, one comma-separated line of site names), so a missing block there does not mean the site lacks it.
- For any of these, check the RC site directly. A read-only `sqlq "SELECT type, COUNT(*) FROM block_content_field_data GROUP BY type"` gives a quick census.

## 6. Overlaps

An overlap is two or more PRs (from any of the four repos) that touch the same:

- block type, component, or template;
- token or theme variable;
- config entity (same config name);
- field, entity type, or table that an update hook reads or writes;
- contrib module (one PR bumps it while another changes code that uses it).

Every overlap becomes its own hypothesis in Phase 2, ranked high. PRs that each pass alone and break together are the class of bug that only an RC-level pass can find.

## Output shape

```json
{
  "branch": "v2270",
  "head": "<sha>",
  "built": "<ISO time>",
  "prs": [{"repo": "yalesites-project", "number": 1666, "title": "...", "issue": "yalesites-org/YaleSites-Internal#1954"}],
  "surfaces": [{
    "id": "block:image",
    "kind": "block",
    "prs": ["yalesites-project#1666", "component-library-twig#740"],
    "trace": ["CLT components/02-molecules/image/_image.scss", "atomic templates/block/block--inline-block--image.html.twig", "block type image"],
    "sites_using": 212,
    "rc_pages": [{"site": "ys-your-yale-edu", "url": "/about"}]
  }],
  "wide_triggers": [{"file": "...", "pr": "...", "why": "global token"}],
  "untraced": [{"file": "...", "pr": "...", "why": "dynamic include"}],
  "overlaps": [{"surface": "block:image", "prs": ["...", "..."]}]
}
```
