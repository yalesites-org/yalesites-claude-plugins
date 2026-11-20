# Research sources

Every internal source the planning session reads, in order, with what each one answers and the
read-only way to reach it. Check availability for all of them in Step 1, then work down the list
in Step 2. A source that is unavailable is reported as skipped.

| # | Source | Answers | Availability check |
|---|---|---|---|
| 1 | yalesites-project code | What the feature touches, what already exists | A local checkout, or `gh` |
| 2 | Component library repos | Front-end and design system reach, how many repos | A local checkout, or `gh` |
| 3 | Portfolio crawl | Blast radius in sites and instances, heavy-use sites | The `yalesites:yalesites-portfolio` skill is installed |
| 4 | Pantheon | Live config and modules, where the crawl can't see | `terminus auth:whoami` |
| 5 | GitHub history | Earlier attempts, past decisions, related work, milestones | `gh auth status` |
| 6 | UX research | Who it serves, known pain points and delights | The `yalesites-product:ux-research` skill |
| 7 | Platform knowledge and docs site | How we tell editors to do this today, docs that change | The `yalesites:yalesites` skill, and yalesites.yale.edu |
| 8 | Live sites in a browser | What it looks like in use, screenshots for the board | A browser tool (Playwright or Claude in Chrome) |

## 1. yalesites-project code

Read `develop`. If the user keeps a local checkout, update it first: if it is clean and on
`develop`, `git pull --ff-only origin develop`; otherwise `git fetch origin` and read
`origin/develop`, and say so. Without a checkout, read through `gh api` or the GitHub connector.

Where things live:

| Path | Holds |
|---|---|
| `web/profiles/custom/yalesites_profile/modules/custom/ys_*` | Platform features: `ys_core` (sitewide settings, editor UI), `ys_layouts` (Layout Builder sections and block placement), `ys_themes` (theme and palette settings), `ys_localist`, `ys_views_basic`, `ys_node_access`, `ys_ai`, and the rest |
| `web/profiles/custom/yalesites_profile/config/sync` | Platform config: block types, fields, content types, views, roles and permissions |
| `web/themes/custom/ys_admin_theme` | The editor-side theme |
| `*.install` files and `post_update.php` | Update hooks: how earlier changes reached existing sites |

Look for: the block type, field, or setting the feature would extend; where its template and
form live; whether an option already covers part of the ask; which roles can reach it
(`user.role.*.yml`); and how an earlier change of the same shape reached existing sites (an
update hook, a config import, an opt-in setting). Note file paths with line numbers for
`research.md`. Do not judge the code's design; note what exists.

## 2. Component library repos

The front end spans several repos. A feature that changes what a block looks like usually
touches more than one, which is the biggest single driver of effort and timeline.

| Repo | Holds |
|---|---|
| `yalesites-org/component-library-twig` | Twig components and their Storybook stories |
| `yalesites-org/atomic` | The Drupal theme that maps Drupal output onto the components |
| `yalesites-org/tokens` | Design tokens: color, spacing, type |
| `yalesites-org/yale-ui-cl` | The UICL component library. Check it for parity: does UICL already have this, or will it need it |

For each: does a component already exist, would it need a new variant, and does a token cover
the color or spacing in question. Count the repos the feature would touch.

## 3. Portfolio crawl

Use the `yalesites:yalesites-portfolio` skill. If it is not installed, skip it and say so; never
estimate adoption numbers. Pull:

- Adoption for every block, setting, or layout the feature touches, with the crawl vintage
  ("on 38 of 296 crawled sites, 226 instances, 2026-10 crawl").
- The two or three heaviest-use sites for each, and any exemplar or anti-pattern sites the skill
  names. These are where screenshots come from in source 8.
- For a change to defaults or behavior: how many sites would see a change on the next deploy
  without doing anything. That number is the headline of the blast radius.

## 4. Pantheon

Use Terminus when a question needs live config the crawl can't see: which sites have a module
enabled, a setting's value, how many sites are on the platform today. Prefer the portfolio data
when it already answers the question.

Allowed commands, all read-only:

```bash
terminus auth:whoami
terminus org:list
terminus org:site:list <org> --format=csv --fields=name,id,frozen
terminus env:info <site>.live
terminus remote:drush <site>.live -- pm:list --status=enabled --format=json
terminus remote:drush <site>.live -- config:get <config.name> --format=json
terminus remote:drush <site>.live -- sql:query "SELECT COUNT(*) FROM <table>"
```

Rules:

- **Read only.** Never `config:set`, `config:import`, `cache:rebuild`, `updatedb`, `deploy`,
  `env:clone-content`, `multidev:create`, or anything that writes. A `sql:query` is a `SELECT`
  and nothing else.
- **Sample first.** Run against two or three sites before a sweep. Ask the user before running a
  command across more than ten sites, and say how many and why.
- **Not logged in:** report Pantheon as skipped and name the question it would have answered.
  Never ask for a machine token or enter one.

## 5. GitHub history

The same idea has often been raised before. Search before asking anything:

```bash
gh search issues "<keywords>" --owner yalesites-org --limit 30 --json repository,number,title,state,updatedAt,url
gh search prs "<keywords>" --owner yalesites-org --limit 30 --json repository,number,title,state,url
gh api repos/yalesites-org/YaleSites-Internal/milestones --paginate \
  -q '.[] | "\(.number)\t\(.title)\tdue=\(.due_on)\topen=\(.open_issues)"'
```

Look for: earlier tickets for the same ask (closed as won't-do, and why), PRs that tried it and
stalled, ADRs or decision comments that settle part of it, open work on the same block or setting
that this would collide with, and what the next two release milestones already hold. Read the
comment threads on the strongest matches; decisions hide there. Refer to every hit in
`owner/repo#number` form.

## 6. UX research

Load `yalesites-product:ux-research` and answer the three questions from the ticket skill's
"Step 1b": which archetypes this affects, whether it matches a known pain point (and its
percentage), and whether it puts a current delight at risk. Note the cost to Solo Starter and
New Recruit for anything that adds a term, setting, or screen.

## 7. Platform knowledge and docs site

Load `yalesites:yalesites` for how the feature area works today and what editors are told. Then
find the pages on yalesites.yale.edu that cover it: those are the docs that would change, and
they show the words editors already know. Note each page's URL for the Docs phase.

## 8. Live sites in a browser

Open the heavy-use sites from source 3 and screenshot the feature area as visitors see it, at
desktop and phone widths when layout matters. For a new feature with nothing to show yet,
screenshot the closest current option instead. Capture details, and the external inspiration
screenshots that join these on the board, are in `visual-evidence.md`. These are the images on the board, so name each
file for what it shows (`onha-facts-band-1440.png`) and keep the URL with it. Public pages only:
never sign in to a site to see its editor side. For the editor side, use a multidev or the
user's own screenshots.
