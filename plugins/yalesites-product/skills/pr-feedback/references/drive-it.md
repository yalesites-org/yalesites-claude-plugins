# Drive it: running the test plan in a real browser

Read this from `SKILL.md` Step 3 once the test plan is written. Instead of handing the plan to
the user to click through, Claude runs it in a visible browser on the user's machine with
Playwright, while the user watches. Every step ends with a screenshot, pass or fail, so the
review rests on evidence rather than on a claim that something was checked.

**Scope today: `yalesites-project` multidevs only.** Storybook previews
(`component-library-twig`) need no login and would work the same way, but that path is not
written yet. For every other case, hand the plan to the user as `SKILL.md` Step 3 describes.

**The user watches, the user rules.** Driving the browser settles mechanical questions (does it
overflow, which column is on the left, does focus move). It never settles design or product
questions. Those rows (`ask` in `beyond-ac-checks.md`) get a screenshot and go to Step 3b.

---

## Step D0: Preflight, and fall back instead of forcing it

Check all of these before opening anything. If any fails, say which one in one line and use the
normal hand-off walkthrough instead. Do not try to install or authenticate things on the user's
behalf mid-review.

| Check | Command | If it fails |
|---|---|---|
| Node is available | `command -v npx` | Hand off. |
| Terminus is authenticated | `terminus multidev:list <site> --fields=id` returns rows | Hand off, and mention `terminus auth:login`. `terminus auth:whoami` can report "not logged in" while commands still work, so test with a real command. |
| The multidev exists and loads | `terminus multidev:list <site> --fields=id,domain` includes `pr-<N>`, and the site URL returns 200 | A missing environment is often the 25/25 multidev cap, not the code. Say so and hand off. |
| This is a machine the user can see | The session runs on the user's desktop, not in the cloud | A headed browser in a cloud session shows nobody anything. Hand off. |

The site on Pantheon is `yalesites-platform`, and PR multidevs are named `pr-<N>`, served at
`https://pr-<N>-yalesites-platform.pantheonsite.io`. Confirm against the brief's **Where to
test** rather than assuming.

Then run checklist row 13 from `beyond-ac-checks.md` (is the environment trustworthy) before
any real step: every testing link in the PR body resolves, logged-in pages do not 500, and the
served JS and CSS are the branch's. A failure here is a finding in its own right, and it also
means later steps cannot be trusted, so stop and tell the user.

## Step D1: Ask once, before writing anything

Visreg multidevs carry a red "DO NOT CHANGE CONTENT" banner. That banner protects the visreg
site itself; a PR multidev is a disposable copy. Still, ask the user once per PR, with one
`AskUserQuestion`, before doing any of these:

- creating test content (nodes, blocks, sections, media)
- creating `qa-<role>` users
- changing any setting

Offer the alternative in the same question: test on an existing page such as
`/empty-testing-page` or the `/blocks-for-visreg/...` pages, read-only, where the plan allows.
Record exactly what gets created (node IDs, usernames) so Step D5 can remove it.

## Step D2: Log in, one session per role

```bash
terminus drush yalesites-platform.pr-<N> -- uli --name=<username> --uri=https://pr-<N>-yalesites-platform.pantheonsite.io
npx -y @playwright/cli@0.1.22 -s=<role> open --headed '<login link>'
```

Follow "Roles" in `beyond-ac-checks.md`: user 1 (a bare `uli`) is for setup only, `e2etest` is
the site admin, `qa-<role>` users are created only with consent, and real people's accounts are
never used. Name each session after its role (`-s=site_admin`, `-s=editor`) so the logins never
mix. Open the role under test headed; setup-only sessions can stay headless.

## Step D3: Run each step, and screenshot every result

### Driving the page

The CLI works by element references from a page snapshot:

| Need | Command |
|---|---|
| Go somewhere | `goto <url>` |
| Find an element and its ref | `find '<text>'`, or `snapshot` then read the saved `.yml` |
| Act | `click <ref>`, `fill <ref> '<text>'`, `type '<text>'`, `select <ref> <value>`, `press Tab` |
| Measure | `eval "() => ..."` returning JSON (bounding boxes, computed colors, `document.activeElement`, `scrollWidth > innerWidth`) |
| Resize | `resize <w> <h>` |
| Point at something | `highlight <ref>` (and `highlight --hide` after) |
| Capture | `screenshot [ref] --filename=<path>` |

Every command takes `-s=<session>`. In zsh, a command stored in a variable is not word-split,
so write a small wrapper script rather than `P="npx ..."; $P goto ...`.

**Layout Builder's AJAX links sometimes do nothing when clicked** (seen on "Add block" in a
column). The first time a click on a `use-ajax` link fails to open its panel, stop retrying and
`goto` the link's `href` instead (for example
`/layout_builder/choose/block/overrides/node.<nid>/<delta>/<region>`). Drupal serves these as
full pages and the saved result is the same.

Prefer measuring to eyeballing. "The sidebar sits at x=64 and is 225px wide; the main column
sits at x=465" is evidence. "It looks right" is not.

### Screenshots: every step, pass or fail

Save them under one folder per run, so the user can find them later and attach them to GitHub:

```
~/.claude/yalesites/pr-feedback/runs/<repo>-<N>-<YYYY-MM-DD>/
```

Name each file `<NN>-<result>-<role>-<slug>.png`, where `<result>` is one of:

| Result | When | What the screenshot shows |
|---|---|---|
| `pass` | The step's expected outcome was confirmed, by measurement where possible | The thing that passed, at the width and role tested. Scroll it into view first; screenshot the element (`screenshot <ref>`) when the full page would bury it |
| `fail` | The expected outcome did not happen | The failure itself, with the failing element highlighted (`highlight <ref>` before the screenshot). Also capture the same view on `dev` when the question is "did this change it", so the two sit side by side |
| `ask` | A design or product row from the checklist | The thing needing a ruling, framed so the question can be answered from the picture alone |
| `blocked` | The step could not run (element missing, error page, environment broken) | Whatever the browser actually showed |

Example: `03-fail-editor-30-70-mobile-360.png`.

Alongside the images, write `results.md` in the same folder, one line per step:

```
| # | Step | Role | Result | Evidence | Screenshot |
|---|---|---|---|---|---|
| 1 | 30/70 appears in the section picker | site_admin | pass | listed between 70/30 and 50/50 | 01-pass-site_admin-picker.png |
| 4 | No overflow at 360px | editor | fail | scrollWidth 412 > 360 | 04-fail-editor-overflow-360.png |
```

### Show the user as you go

Do not save screenshots silently and summarize at the end. After each group of steps, show the
user what happened, with the screenshots, in the same turn:

- In the Claude desktop app, send the images with the file-sharing tool so they render inline.
- Anywhere else, give the file paths.

Show failures first and in full. Passes can be shown together. `ask` screenshots are shown with
their question, which then goes into Step 3b.

## Step D4: Check the log

When the steps are done, pull the Drupal log for the window of the run (checklist row 12):

```bash
terminus drush yalesites-platform.pr-<N> -- watchdog:show --count=50 --severity-min=Warning
```

Report entries that appeared during the run and relate to what was tested. Ignore old noise, and
say that you ignored it.

## Step D5: Clean up

Remove exactly what Step D1 recorded, and nothing else. Check each target before deleting it.

```bash
terminus drush yalesites-platform.pr-<N> -- sqlq "SELECT nid,title FROM node_field_data WHERE nid=<nid>"
terminus drush yalesites-platform.pr-<N> -- entity:delete node <nid>
terminus drush yalesites-platform.pr-<N> -- user:cancel --delete-content qa-<role>
npx -y @playwright/cli@0.1.22 -s=<session> close
```

Confirm removal (the node URL returns 404, the user no longer exists), and say so. Leave the
screenshots and `results.md`: they are the evidence for the review.

## Handing results to the rest of the skill

- **Fails feed Step 4.** Each `fail` becomes a feedback point with its screenshot filename, the
  measured evidence, and the file and line from the brief. `gh` cannot upload images, so tell
  the user which screenshots are worth dragging into the review comment; do not post them
  yourself.
- **Asks feed Step 3b** as questions, with their screenshots.
- **Passes support the approval.** The approval body can say what was verified and as which
  roles, instead of a bare "tested on multidev".
- **Blocked steps are not passes.** Say plainly which steps could not run and why; the user
  decides whether to test those by hand before ruling.
