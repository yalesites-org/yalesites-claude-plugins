# RC sites: finding them, preflight, logins, and what may change

This file adapts `pr-feedback/references/drive-it.md` for RC sites. That file is written for `yalesites-platform.pr-<N>`, with the visreg pages, an `e2etest` user, and permission to create throwaway content. None of that applies here. Each RC site is its own Pantheon site holding a copy of a real site's content, and it is shared with the team.

## Find the RC

```bash
# The open release PR: base master, head v<NNNN>
gh pr list -R yalesites-org/yalesites-project --base master --state open \
  --json number,title,headRefName,headRefOid --jq '.[] | select(.headRefName|test("^v[0-9]+$"))'

# The sites, one "<site>.<source env>" per line
gh variable get RELEASE_SITES -R yalesites-org/yalesites-project
```

The release workflow (`.ci/github/deploy_release_sites` in yalesites-project) creates a multidev named after the release branch on every listed site, clones it from the listed source env, and runs `drush deploy`. Record each site in `release.json` with:

| Field | Value |
|---|---|
| `site` | the Pantheon machine name, e.g. `ys-registrar-yale-edu` |
| `source` | the env after the dot. `live` is real content. Anything else (`dev`, another multidev) gets flagged as `not a live clone` in the report and ranks below live clones when picking sites. |
| `rc_url` | `https://<branch>-<site>.pantheonsite.io` |
| `live_url` | `https://live-<site>.pantheonsite.io` (the baseline) |
| `exists` | from `terminus multidev:list <site> --fields=id` |
| `fresh_install` | `true` for `yalesites-platform`, which is a fresh install plus imported content, not a clone. Use it only for clean-slate checks. |
| `cloned_at` | `terminus env:info <site>.<branch> --field=created`. The workflow clones only when the multidev does not exist yet. RC2 and later push code and run `drush deploy` without cloning again, so content dates from the first RC deploy. |

Do not rely on the "Environments ready for review" comment on the release PR. It only posts when the `RELEASE_SITES_DEPLOYED` repo variable is `0`. Only the cleanup script resets that variable, and the cleanup script has not been running on its own. Terminus is the source of truth.

**Stale multidevs.** Old release multidevs are not cleaned up on their own. The v2260 multidevs were still up six weeks after release. A multidev named after the *current* release branch is the current RC. Anything else is a dry-run target at best.

## Preflight

Finish every check before the first charter. If one fails, say which one in one line and stop. In `--drain`, write that line as the report's first line.

| Check | Command | If it fails |
|---|---|---|
| Node is available | `command -v npx` | Stop. |
| Terminus works | `terminus multidev:list yalesites-yale-edu --fields=id` returns rows | Stop, and mention `terminus auth:login`. `auth:whoami` can say "not logged in" while commands still work, so test with a real command. |
| The CLI opens a browser | `npx -y @playwright/cli@0.1.22 -s=preflight open about:blank`, then `-s=preflight close` | Follow "Browsers" in `pr-feedback/references/drive-it.md`. In `--drain`, never install anything: stop. |
| The CLI opens mobile WebKit | `npx -y @playwright/cli@0.1.22 -s=preflight-m open --browser webkit --device "iPhone 15" about:blank`, then `-s=preflight-m close` | Attended: ask once, then `npx -y @playwright/cli@0.1.22 install-browser webkit` (no admin needed). In `--drain`: do not install. Run phone checks in Chrome at 390px instead, and say in the report that Safari was not covered. |
| The RC runs the release branch | atomic version and a file checksum on one RC site vs the release branch head (below) | Stop. Say which site, with both values. Results from stale code are worse than none. |
| At least half the RC sites exist | `exists` in `release.json` | Report the missing ones. Continue on the rest if at least half exist, otherwise stop. |

Do not compare the profile version. The release branch keeps the previous release's version until after release (v2260 reports 2.25.1), so a clone that never got the new code passes that check. Check these two instead:

```bash
# 1. The atomic version installed on the RC vs the pin on the release branch
terminus drush <site>.<branch> -- php:eval 'echo \Composer\InstalledVersions::getPrettyVersion("yalesites-org/atomic");'
gh api "repos/yalesites-org/yalesites-project/contents/web/profiles/custom/yalesites_profile/composer.json?ref=<headRefOid>" --jq .content | base64 -d | grep '"yalesites-org/atomic"'

# 2. Checksum of a PHP or Twig file the RC adds or changes (pick an added file if there is one)
terminus drush <site>.<branch> -- php:eval '$p=DRUPAL_ROOT."/<path under web/>"; echo file_exists($p) ? md5_file($p) : "MISSING";'
gh api "repos/yalesites-org/yalesites-project/contents/web/<path under web/>?ref=<headRefOid>" --jq .content | base64 -d | md5
```

If the RC changes atomic and nothing in yalesites-project (or the other way around), check one of the two and say which.

Check one site per run in preflight. Each charter re-checks its own site's response code before it starts (a site that returns 5xx is a finding, not a skip).

## Logins

**User 1 is not a real role.** A bare `drush uli` logs in as user 1, which bypasses every permission check. Bugs like media library Access denied for site admins (yalesites-org/YaleSites-Internal#1791) only show up for real roles. A check that "passed as user 1" proves nothing about editors or site admins.

**Never log in as a real person's account**, even on a clone. Actions on a clone are still recorded under their name, and the team reads those logs.

Until the team decides on test users (see "Pending team decisions" in `SKILL.md`):

| Need | Do this |
|---|---|
| Public pages | Logged out. Most charters need nothing else. |
| Admin reads (block library, views config, field settings, user lists) | User 1, read-only, and label every result `as user 1`. Never call a user 1 pass a role pass. |
| Anything that depends on a role | Mark the hypothesis `blocked: needs role users` and move on. |

Log in with:

```bash
terminus drush <site>.<branch> -- uli --uri=https://<branch>-<site>.pantheonsite.io
npx -y @playwright/cli@0.1.22 -s=c<NN> open '<login link>'
```

Once the team allows `qa-<role>` users, follow "Roles" in `pr-feedback/references/beyond-ac-checks.md` for which roles to use. Record each user in the run's `.created` file, and remove them at the end with `user:cancel --delete-content` (they will own nothing, because the hunt creates nothing).

## What the hunt may change

Almost nothing:

| Allowed | Not allowed |
|---|---|
| Browsing, logged out or as user 1. `drush uli` is the one allowed write: a login records a session and a last-login time, which harms nobody. | Saving a node, block, media item, menu, or setting |
| Read-only drush: `watchdog:show`, `sqlq` with a `SELECT` only, `config:get`, `migrate:status`, `pm:list`, `status`, `user:information`, `php:eval` that only reads | `config:set`, `cron`, `cache:rebuild`, `entity:delete`, any `sqlq` that writes, `state:set`, `queue:run` |
| Opening a Layout Builder form on an existing page, then discarding it (below) | **Save layout**, ever |
| Filling a search or filter form that only reads (calendar filters, view exposed filters) | Submitting any form that sends, saves, or registers (webforms, contact, newsletter sign-ups, event registration) |

**Layout Builder on existing pages.** This rule comes from `yalesites-web-content`. It is how the hunt checks old blocks against new validation (yalesites-org/YaleSites-Internal#1052):

1. Open `/node/<nid>/layout`. If the page shows "You have unsaved changes" or a "being edited by" lock **before you touch anything**, that is someone else's work in progress. Leave it and pick another page.
2. Open the block's configure form from the editor's contextual link, the way an editor would. Read it. Submitting the form is allowed **only for an inline block**, and only when the hypothesis is about validation: for an inline block, Update changes only the unsaved layout.
   - **Never submit a reusable block's form.** Our core patch for reusable inline blocks (`patches/drupal-core/2999491-162.patch` in yalesites-project) saves the `block_content` entity on Update, right away. That is a new revision on a block shared by other pages, and Discard does not undo it. Open a reusable block's form to read it, then close it.
   - **Never tick the Reusable checkbox** on an inline block's form. Submitting with it ticked saves a new reusable block.
   - Check which kind it is before you submit: a reusable block's form has no Reusable checkbox, and its component is `block_content:<uuid>` rather than `inline_block:<type>`.
3. Close the form. If "You have unsaved changes" appeared, select **Discard changes** and confirm.
4. Reload `/node/<nid>/layout` and confirm that no unsaved-changes notice is there.

If step 4 fails, the page is locked for the next editor, and the hunt cannot clear it. The fix is a tempstore delete, which is a write the permission system refuses on shared sites, and must not be worked around. Add it to `leftovers.md` with the URL, and stop opening Layout Builder for the rest of the run. Every later Layout Builder charter gets `blocked: leftover draft on <url>`.

## Baselines

Every finding compares the RC with the same view on live (`live_url`). Browsing live's public pages is fine in every mode. The clone was taken at `cloned_at`, and live has changed since then. On a `--dry-run`, live also runs later releases, so expect code differences that have nothing to do with the RC, and say so in the report. So a difference on its own is not a finding:

- If the content itself is different (text, images, list items), it is content drift. Compare the node's `changed` time on live with `cloned_at` before you blame the code.
- If the same content renders differently (spacing, color, missing element, error), that is a candidate finding.
- Mask volatile regions when comparing images: Localist feeds, dates, "random" sort views, and chatbot widgets. Mask only those. A wide mask hides real bugs.

## Cost and courtesy

- At most two charters at once across all RC sites, and at most one per site.
- No crawling. Visit the pages the charter names, plus at most 50 more per site per charter.
- Close every browser session when its charter ends (`npx -y @playwright/cli@0.1.22 -s=c<NN> close`).
