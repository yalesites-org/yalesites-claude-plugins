# Drive it: running the test plan in a real browser

Read this from `SKILL.md` Step 3 once the test plan is written. Instead of handing the plan to
the user to click through, Claude runs it in a visible browser on the user's machine with
Playwright, while the user watches. Every step ends with a screenshot, pass or fail, so the
review rests on evidence rather than on a claim that something was checked.

**Scope today: every `yalesites-project` review, on its multidev.** It is required, not
offered, and it runs whether the brief came from the scheduled pre-review pass or was written
at the start of the session. Storybook previews (`component-library-twig`) need no login and
would work the same way, but that path is not written yet. For every other case, hand the plan
to the user as `SKILL.md` Step 3 describes.

**Prep mode changes some of this.** When this runs under `/pr-feedback --prep`
(`references/prep-mode.md`), no one is watching: sessions are headless, nothing is installed,
nothing is shown as it goes, and the disposable multidev rule in prep-mode.md Step P3 is the same
standing consent Step D1 gives. Everything else here applies as written, Step D5 cleanup included.

**The user watches, the user rules.** Driving the browser settles mechanical questions (does it
overflow, which column is on the left, does focus move). It never settles design or product
questions. Those rows (`ask` in `beyond-ac-checks.md`) get a screenshot and go to Step 3b.

---

## Step D0: Preflight, and fall back instead of forcing it

Check all of these before opening anything, and **finish all of D0 before Step D1 writes
anything to the multidev**. A check that fails after content exists leaves a mess behind. If a
check fails, say which one in one line and use the normal hand-off walkthrough instead. Do not
authenticate things on the user's behalf. The one install allowed is a browser, and only with
the user's OK (see below).

| Check | Command | If it fails |
|---|---|---|
| Node is available | `command -v npx` | Hand off. |
| Terminus is authenticated | `terminus multidev:list <site> --fields=id` returns rows | Hand off, and mention `terminus auth:login`. `terminus auth:whoami` can report "not logged in" while commands still work, so test with a real command. |
| The multidev exists and loads | `terminus multidev:list <site> --fields=id,domain` includes `pr-<N>`, and the site URL returns 200 | A missing environment is often the 25/25 multidev cap, not the code. Say so and hand off. |
| This is a machine the user can see | The session runs on the user's desktop, not in the cloud | A headed browser in a cloud session shows nobody anything. Hand off. |
| The CLI can launch a browser | `npx -y @playwright/cli@0.1.22 -s=preflight open about:blank`, then `-s=preflight close` | See "Browsers" below. Do not move on to D1 until a browser opens. |

### Browsers

`@playwright/cli@0.1.22` opens the installed **Google Chrome** by default. A machine without
Chrome passes every other check and then fails at `open`, which is why the launch check above
runs a real, headless `open` on a blank page rather than trusting `npx` alone.

If the launch fails, ask the user (one `AskUserQuestion`) which fix they want, then run it:

| Option | Command | Then open with | Note |
|---|---|---|---|
| Install Chrome | `npx -y @playwright/cli@0.1.22 install-browser chrome` | the default (no `--browser`) | A system-wide install; macOS may ask for an admin password |
| Use Firefox | `npx -y @playwright/cli@0.1.22 install-browser firefox` | `--browser firefox` | Installs into the user's Playwright cache, no admin needed |
| Hand off | none | none | Skip the run and give the walkthrough, per `SKILL.md` Step 3 |

Re-run the launch check after installing. Use the same `--browser` value on every `open` for
the rest of the run.

**Safari (checklist row 4)** needs WebKit, which is not installed by default. With the user's
OK, install it once (user cache, no admin), then run the Safari steps in their own session:

```bash
npx -y @playwright/cli@0.1.22 install-browser webkit
npx -y @playwright/cli@0.1.22 -s=<role>-webkit open --browser webkit --headed '<login link>'
```

A WebKit session needs its own `uli` login link: one-time links do not carry across sessions.

The site on Pantheon is `yalesites-platform`, and PR multidevs are named `pr-<N>`, served at
`https://pr-<N>-yalesites-platform.pantheonsite.io`. Confirm against the brief's **Where to
test** rather than assuming.

Then run checklist row 13 from `beyond-ac-checks.md` (is the environment trustworthy) before
any real step: every testing link in the PR body resolves, logged-in pages do not 500, and the
server is running the branch's code. A failure here is a finding in its own right, and it also
means later steps cannot be trusted, so stop and tell the user.

**Prove the server runs the branch. Green CI does not.** "Deploy to Pantheon: pass" and a 200
on the home page have both been seen on a multidev serving a months-old profile. Check two
things against the PR head (`headRefOid`):

```bash
# 1. Profile version on the server vs the branch
terminus drush yalesites-platform.pr-<N> -- php:eval 'preg_match("/version: .*/", file_get_contents(DRUPAL_ROOT."/profiles/custom/yalesites_profile/yalesites_profile.info.yml"), $m); echo $m[0];'
gh api "repos/yalesites-org/yalesites-project/contents/web/profiles/custom/yalesites_profile/yalesites_profile.info.yml?ref=<head>" --jq .content | base64 -d | grep '^version'

# 2. Checksums of two or three PHP or JS files the PR adds or changes
terminus drush yalesites-platform.pr-<N> -- php:eval '$p=DRUPAL_ROOT."/<path under web/>"; echo file_exists($p) ? md5_file($p) : "MISSING";'
gh api "repos/yalesites-org/yalesites-project/contents/web/<path under web/>?ref=<head>" --jq .content | base64 -d | md5
```

Pick files the PR **adds** where possible: a missing new file is the clearest signal. If either
check disagrees, say which file, on which environment, with both values, and stop. Do not guess
at the cause; that is for the developer.

## Step D0b: Have the brief and the plan before driving

Do not start testing until Step 1 has a brief at the PR's current SHA and Step 3 has turned it
into a plan with its beyond-AC rows picked. A run planned without the brief tests what the
driver happens to think of, not what the diff points to, and misses whole areas (on one trial
run it skipped the region checks, the reusable block library, and logged-out viewing).

If the brief is still being written (including when `SKILL.md` Step 1 is writing it right now
because none existed), open the browser early for setup only: logging in, creating the test
page. No step gets a result until the plan exists. A missing brief delays testing; it never
cancels the run.

**Every checklist row whose trigger matches the diff gets run.** To skip one, say which row
and why before the run starts, so the user can overrule it. Skipping silently is not allowed.
"Known issue" and "deferred to another ticket" are not reasons to skip: run the row anyway and
record it as `fail (known)` with the ticket it is tracked on. The run cannot know that the
known issue is the only one there.

## Step D1: Before writing anything

Visreg multidevs carry a red "DO NOT CHANGE CONTENT" banner. That banner protects the visreg
site itself; a PR multidev is a disposable copy. **Running the skill is consent to write to PR
multidevs, so do not ask.** The reviewer does not want a question before every run. The consent
covers PR multidevs (`pr-<N>`) only, never a visreg multidev, `dev`, `test`, or `live`, and only
these kinds:

- creating test pages (nodes). Inline blocks and sections placed on a test page go with it
- creating reusable blocks or media (including uploaded files)
- creating `qa-<role>` users
- changing a setting

Only these kinds, because Step D5 knows how to handle each one. Anything else a step would
need is out of bounds: say so and hand that step off.

What happens afterwards does not change: on this PR's own `pr-<N>` multidev the test content
stays after the run, so the reviewer can open it and check the findings by hand, and settings go
back to their original values. Anywhere else, including another PR's multidev used as a
baseline, everything the run made is removed. See Step D5. Say so in one line when the run
starts, as a note, not a question.

Prefer an existing page such as `/empty-testing-page` or the `/blocks-for-visreg/...` pages,
read-only, where the plan allows it.

Record everything as it is created, in `.created` in the run folder, one line per item,
starting with the environment it lives on: `pr-1413 node <nid>`, `pr-1413 block_content <id>`,
`pr-1413 media <mid>`, `pr-1413 file <fid>`, `pr-1413 user qa-<role>`, and for a setting,
`pr-1413 config <name> <key> <original value>` written **before** changing it, from
`terminus drush ... -- config:get <name> <key>`. The environment column is what D5 keys on: a
parity run creates content on the reviewed PR's multidev and on a baseline, and `node 84` alone
cannot say which. Step D5 works from this file and nothing else.

**Title test content so anyone can tell it apart.** Kept content shows up in views, calendars,
search, and listing blocks on other pages, where the next tester or a visreg pass will see it.
Start every test page, event, post, profile, and reusable block title with
`QA pr-<N> <YYYY-MM-DD>:`, where N is the number of the PR under review, not the ticket (for
example `QA pr-1413 2026-10-13: Event with no end date` for the 1435 ticket's PR).

**Reuse before creating, on a second run of the same PR, on that PR's own multidev only.**
Step D5 keeps content and `qa-<role>` users on the multidev of the PR under review, so a later
run on the same PR finds them already there. Before creating a user, check for it
(`terminus drush ... -- user:information qa-<role>`) and reuse it if it exists, since
`user:create` fails on a duplicate name. Before creating content, read the `.created` files of
earlier run folders for the same PR (`~/.claude/yalesites/pr-feedback/runs/<repo>-<N>-*/`) and
reuse a `kept` item that still exists, is still ours, and fits the step. Only nodes and users
can be shown to be ours, so only they are reused; kept media, files, and reusable blocks have no
ownership check and are recreated instead. A node is still ours when its title still starts
with `QA pr-<N> ` with the trailing space (check with the `sqlq` title query from D5;
`QA pr-141` must not match `QA pr-1413 ...`). A user is still ours when `user:information`
shows its roles are exactly `<role>` plus authenticated; the name alone proves nothing, since
you looked it up by name, and a multidev rebuilt from `dev` can carry someone else's
`qa-editor` with other roles, or reuse a node id for real content. A user with any other role
set means stop and ask. Write a reused item into this run's `.created` as
`pr-<N> node 84 reused`, so D5 knows this run did not make it and must never remove it.

An earlier run folder for this PR whose `.created` has no `kept` or `reused` markers is a run
that stopped before D5 (a crash, a preflight failure, a user stop). Its lines for this PR's own
multidev are kept candidates under the same ownership checks: a node or user that passes is
reusable and becomes `kept` at this run's D5; one that fails is reported, not touched; its media,
files, and reusable blocks are reported as leftovers for the user to decide on.

Reuse only what the step reads. A step that tests creating or saving (and any step whose
earlier finding was a create or save bug) runs against the new code only if it creates the
item again, so recreate for those steps rather than reusing a node the old code saved.

Anywhere other than the PR's own multidev, an existing `qa-<role>` user or `QA pr-` content is
not ours: do not reuse it and do not remove it. Ask the user how to proceed.

## Step D2: Log in, one session per role

```bash
terminus drush yalesites-platform.pr-<N> -- uli --name=<username> --uri=https://pr-<N>-yalesites-platform.pantheonsite.io
npx -y @playwright/cli@0.1.22 -s=<role> open --headed '<login link>'
```

Follow "Roles" in `beyond-ac-checks.md`: user 1 (a bare `uli`) is for setup only, `e2etest` is
the site admin, `qa-<role>` users are created only under Step D1's consent, and real people's accounts are
never used. Confirm `e2etest` exists and still holds `site_admin` before relying on it
(`terminus drush ... -- user:information e2etest`). If it does not, treat site admin like any
other role: a `qa-site_admin` user, created with the D1 consent. Name each session after its role (`-s=site_admin`, `-s=editor`) so the logins never
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

**For forms, prefer `run-code` with Playwright locators over refs.** Refs change every time a
page or AJAX rebuild re-renders, which Drupal forms do constantly. `run-code "async page =>
{ ... }"` with `page.getByLabel('Closed on Sunday')`, `page.locator('[name="..."]')`, or
`page.getByRole('link', {name: 'Office Hours', exact: true})` survives rebuilds and lets one
call fill a whole form and loop over regions or widths.

**Narrow-column tests need the other columns filled.** Drupal leaves empty regions out of the
front end, so a block alone in a 70/30 sidebar renders at the section's full width and the test
proves nothing. Put a Text block in every other column of the section first.

**In Layout Builder, take the editor's path. Never `goto` a Layout Builder URL.** An editor
adds a block by clicking "Add block" in a region, picking it from the block browser, and
filling "Configure block" in the same dialog. Adding or configuring a section works the same
way. Do the same. Never open a `/layout_builder/choose/...`, `/layout_builder/add/...`, or
`/layout_builder/configure/...` URL directly. Drupal serves those as full admin pages, which
saves the same data but skips everything the editor actually sees: the dialog, its styling and
scrolling, the AJAX rebuilds inside it, and where focus goes. A PR can break any of those and a
run that went around them would still pass.

The two dialogs look different, so expect the right one:

| Link | Opens | Title |
|---|---|---|
| "Add block", configure a block | Centered modal (the block browser) | "Choose a block", then "Configure block" |
| "Add section", "Configure section" | Off-canvas sidebar on the right (`.ui-dialog-off-canvas`) | "Choose a layout for this section", then "Configure section" |

**Hover the section before clicking "Add block".** The section wrapper sits on top of its "Add
block" links until the pointer is over the section, so a bare `click` fails with "`<div
class="layout-builder__section">` intercepts pointer events" and times out. A real mouse
always hovers first. This, not a broken link, is why these clicks used to "do nothing". So, in
one `run-code` call:

1. Wait for the link to carry Drupal's AJAX handler: its `data-once` attribute includes `ajax`.
2. Hover the section (`div.layout-builder__section[aria-label="<section label>"]`), then click
   the link.
3. Wait for the dialog (`.ui-dialog[role="dialog"]`, visible). Picking a block or layout
   replaces the dialog's content, so wait for the next title or button before filling.
4. Scope every locator to the dialog (`dialog.getByLabel(...)`), because the page behind it
   has fields with the same labels. For a CKEditor field, click `.ck-editor__editable` in the
   dialog and `type`; `fill` does not reach it.
5. After "Add block", "Add section", or "Update", wait for the dialog to close and the new
   content to appear on the page before the next step.
6. Confirm `page.url()` is still `/node/<nid>/layout`. If it changed, the run left the
   editor's path.

If the modal still does not open after waiting, the step is `blocked`: screenshot what the
browser shows and tell the user. Do not work around it. A modal that will not open may be the
bug the PR introduced.

Prefer measuring to eyeballing. "The sidebar sits at x=64 and is 225px wide; the main column
sits at x=465" is evidence. "It looks right" is not.

### Screenshots: every step, pass or fail

Save them under one folder per run, so the user can find them later and attach them to GitHub:

```
~/.claude/yalesites/pr-feedback/runs/<repo>-<N>-<YYYY-MM-DD>-<HHMM>/
```

The time suffix gives every run its own folder and its own `.created`, so a second run on
the same day neither overwrites the first run's results nor mixes its items into one file.

Name each file `<NN>-<result>-<role>-<slug>.png`, where `<result>` is one of:

| Result | When | What the screenshot shows |
|---|---|---|
| `pass` | The step's expected outcome was confirmed, by measurement where possible | The thing that passed, at the width and role tested. Scroll it into view first; screenshot the element (`screenshot <ref>`) when the full page would bury it |
| `fail` | The expected outcome did not happen | The failure itself, with the failing element highlighted (`highlight <ref>` before the screenshot). Also capture the same view on `dev` when the question is "did this change it", so the two sit side by side |
| `fail (known)` | It failed, and the failure is already tracked (an open AC item, a deferral ticket) | Same as `fail`. Name the tracking ticket in `results.md`, and say whether this failure is wider than what the ticket describes |
| `ask` | A design or product row from the checklist | The thing needing a ruling, framed so the question can be answered from the picture alone |
| `blocked` | The step could not run (element missing, error page, environment broken) | Whatever the browser actually showed |

Example: `03-fail-editor-30-70-mobile-360.png`.

**Look at every screenshot before giving it a result.** Open the image and confirm it shows
what its name claims. In trial runs, a screenshot taken right after a resize captured the page
before layout settled, one cropped away the very table it was meant to prove, and one scrolled
past its target and came out blank. A wrong screenshot is worse than none, because it gets
dragged into a review as evidence. After `resize`, wait for layout to settle; scroll to the
element itself (`scrollIntoView` on it, then allow for the sticky admin toolbar) rather than to
a computed offset; and clip to the element's box, re-measured after scrolling. If it is wrong,
retake it. Never relabel a bad image.

Alongside the images, write `results.md` in the same folder, one line per step:

```
| # | Step | Role | Result | Evidence | Screenshot | Clip |
|---|---|---|---|---|---|---|
| 1 | 30/70 appears in the section picker | site_admin | pass | listed between 70/30 and 50/50 | 01-pass-site_admin-picker.png | |
| 4 | No overflow at 360px | editor | fail | scrollWidth 412 > 360 | 04-fail-editor-overflow-360.png | |
| 6 | Escape closes the dialog and returns focus | editor | fail | focus lands on `body` | 06-fail-editor-escape-focus.png | 06-fail-editor-escape-focus.webm |
```

### Clips: when a still is not enough

A screenshot shows where a step ended. Some steps are about how it got there. For those, also
record a short clip of the interaction, so the reviewer and the developer can watch it happen.
The clip is extra evidence. It never replaces the step's screenshot, which still carries the
result.

**Record a clip when the thing under test moves or happens in order:**

| Record a clip for | Example |
|---|---|
| Something that opens, closes, slides, or animates | A modal, the off-canvas sidebar, a menu, an accordion, tabs |
| Focus order and keyboard paths | Tab through a form, Escape returns focus to the trigger |
| An AJAX rebuild | A field that appears after a choice, the Layout Builder dialog swapping content |
| Hover and drag | Hover states, drag to reorder |
| A failure that happens partway through, or only sometimes | A flicker, a layout jump, a double submit, a dialog that opens and closes again |
| An `ask` row that is about behavior | "The menu snaps open with no transition. Is that what we want?" |

**Do not record a clip for** layout, color, copy, spacing, or widths. A screenshot shows those
better, and the reviewer can pin it. Keep each clip to one interaction and under 30 seconds.
Most runs need none, or two or three. If every step gets a clip, nobody watches them.

The CLI records the page viewport only, not the browser UI or the desktop. It works headed or
headless and needs no macOS permissions. Record in the same session as the step:

```bash
pw resize 1280 720
pw video-start <run folder>/<NN>-<result>-<role>-<slug>.webm --size 1280x720 --cursor
pw video-show-actions --highlight-style "outline: 3px solid #f9c642"
pw video-chapter "Open the dialog" --duration 1200
pw click <ref>
pw run-code "async page => { await page.waitForTimeout(1500); }"
pw video-chapter "Close it with Escape" --duration 1200
pw press Escape
pw run-code "async page => { await page.waitForTimeout(1500); }"
pw video-stop
```

(`pw` is the small wrapper script "Driving the page" asks for, which runs
`npx -y @playwright/cli@0.1.22 -s=<session>`.) Name the clip the same as
the step's screenshot, with `.webm`. What we learned in trial runs:

- **Resize first, and pass a matching `--size`.** The default frame fits 800x800, which shrinks
  a desktop page until text is hard to read.
- **Fit the whole component in the frame, for the whole clip.** Measure the element first
  (`boundingBox()` on it) and size the viewport to its height plus a little margin, keeping the
  width you are testing at. Then scroll its top edge to the top of the frame before
  `video-start`. 1280x720 is not a default to reach for: a month calendar is about 1,100px tall
  at 1280px wide, and a 720px clip of it cut off the rows and the month controls the bug
  depended on, so the reviewer could not follow it. If the component is taller than a sensible
  frame, record the part the bug happens in and say so in the caption. Keep the planned
  viewport when the behavior depends on viewport height (sticky headers, `vh`-sized heroes,
  modals and dialogs centered on the viewport): a taller frame changes the layout under test.
  Scroll or record in parts instead, and say so in the caption.
- **Drive the steps you want seen with CLI commands** (`click <ref>`, `press`, `fill`).
  `--cursor` draws a pointer that travels to each action and paces it by 800ms, so a viewer can
  follow. Actions inside one `run-code` call run at machine speed: add a
  `page.waitForTimeout(800)` between them.
- **Hold the end state.** Wait about 1.5 seconds after the last action, or the clip stops on
  the moment that matters.
- **Chapter cards blur the page while they show.** Use one per sub-step, keep
  `--duration` at 1000 to 1500, and add it before an action, never during the moment in
  question.
- **Clips have no audio.**

**Look at every clip before using it,** the same as a screenshot. Make a frame strip, and read
it:

```bash
ffmpeg -v error -y -i <clip>.webm -vf "fps=2,scale=320:-1,tile=6x5" -frames:v 1 <clip>-strip.png
```

Frames run left to right, top to bottom, half a second apart, so frame *n* (from 0) is at
*n* / 2 seconds. Use that to find the timestamps the review board needs (`moments` in
`review-board.md`). For a clip longer than 15 seconds, raise the tile count. If `ffmpeg` is
not installed, keep the clip but say it is unchecked. The screenshot still carries the result.

**For GitHub, also make an MP4.** GitHub accepts `.webm`, but QuickTime and Safari do not play
it, and the MP4 is smaller:

```bash
ffmpeg -v error -y -i <clip>.webm -c:v libx264 -pix_fmt yuv420p -movflags +faststart <clip>.mp4
```

A 15-second clip at 1280x720 came out at about 2 MB as MP4. Keep clips under 10 MB, which GitHub
accepts on every plan. If one is bigger, it is probably too long: re-record it shorter.

### Show the user as you go

Do not save screenshots silently and summarize at the end. After each group of steps, show the
user what happened, with the screenshots, in the same turn:

- In the Claude desktop app, send the images with the file-sharing tool so they render inline.
  Send a clip's MP4 the same way, with its frame strip, so the user can see what it shows
  without opening it.
- Anywhere else, give the file paths.

Show failures first and in full. Passes can be shown together. `ask` screenshots are shown with
their question, which then goes into Step 3b.

## Step D4: Check the log

When the steps are done, pull the Drupal log for the window of the run (checklist row 12):

```bash
terminus drush yalesites-platform.pr-<N> -- watchdog:show --count=50 --severity-min=Warning
```

Report entries that appeared during the run and relate to what was tested. Ignore old noise, and
say that you ignored it. Match entries to the run by timestamp: anything else that touched the
environment in the same window (a background `pr-prereview` pass probing logged out, another
reviewer) shows up in the same log, and its access-denied entries are not the run's.

## Step D5: Clean up

**On the multidev of the PR under review, keep the test content and revert only the
settings.** That is `pr-<N>` for the PR's own number, and only that one: another PR's multidev
used as a baseline (the 1435 parity run used pr-1612 for develop) belongs to that PR's
reviewer, who never agreed to our content in their calendars and listings, so it gets the
"anywhere else" treatment. The PR's own multidev goes away with the PR: the yalesites-project build workflow runs `push-to-pantheon`
with `delete_old_environments` on, which deletes the `pr-<N>` multidev of every closed PR,
merged or not, after the next successful PR deploy. So a closed PR's multidev lasts until the
next deploy, not a moment longer, and an open PR keeps its multidev, and anything kept on it,
for as long as the PR stays open. Leftover test pages cost nothing there. Deleting them costs
a lot: the review board links straight to those pages, and a finding the reviewer cannot
reproduce by hand is one they cannot confirm. This is not hypothetical. On the 1435 Vite
parity run, cleanup deleted the four calendar events that the top finding needed, and the
reviewer opened the board link to an empty calendar.

| Kind | On the PR's own `pr-<N>` | Anywhere else |
|---|---|---|
| Setting | Revert it | Revert it |
| Test page, reusable block, media, file | **Keep it** | Remove it |
| `qa-<role>` user | **Keep it**, so role checks can be repeated with `uli` | Remove it |
| Anything marked `reused` | Leave it | Leave it: this run did not make it |
| Browser sessions | Close them | Close them |

Revert settings even on the PR's own multidev: a changed setting alters every page for the next tester,
who has no way to know it was changed. Kept content can show up for others too (a kept event
sits in every calendar, a kept post in every listing and search), which is why D1 titles it
`QA pr-<N> <date>:`, so whoever meets it knows what it is and that it is safe to ignore.

When a finding depends on a changed setting, the kept page stops reproducing it the moment the
setting is reverted. Say so in the screenshot caption and in the report, with the setting and
the value needed to see it again (for example "needs `ys_core.settings theme` set to
`theme_four`"), so the reviewer who opens the board link knows what to change first.

Kept nodes still get their Layout Builder tempstore cleared. A step that cancelled or discarded
a layout change can leave an unsaved draft behind, and the reviewer who opens the kept page's
layout then finds it locked by the run's user, or sees draft content that differs from the
screenshot. Run the `key_value_expire` delete below for every kept `node <nid>`, unless the
unsaved draft is itself the finding, in which case say so in the report.

One line format for what stays. At D5, every item left in place ends up in `.created` as
`<env> <kind> <id> kept` (for example `pr-1413 node 84 kept`), whether this run created it or
reused it (rewrite a `reused` line to `kept` once it is confirmed still there). Kept handling (the tempstore clear above, the URL
in the report) applies to all of them, and the next run looks only for `kept`. List kept
items in the report with their URLs, so the reviewer can find them. The `qa-<role>` users have
no password and are reachable only by `uli`; if a PR goes quiet for weeks, removing them is
still the right call, with `-y user:cancel --reassign-content qa-<role>` so the kept content
they authored stays and the board links keep working.

"Anywhere else" covers `dev`, `test`, `live`, any other PR's multidev, and any shared or
long-lived multidev. If you are unsure which kind of environment it is, ask before leaving
anything behind.

When removing, remove exactly what `.created` lists as made by this run, and nothing else:
never a `reused` line, since `user:cancel --delete-content` on a user this run did not create
would also delete content it never made. Read the environment off each line and decide keep
or remove per line, so a parity run keeps `pr-1413 node 84` and removes `pr-1612 node 91`.
Check each target before removing or reverting it (its title, name, or current value), and
work through the kinds in this order:

| Kind | Check | Remove | Confirm |
|---|---|---|---|
| Setting | `config:get <name> <key>` | `config:set <name> <key> <original value> -y` | `config:get` returns the original |
| Reusable block | `sqlq "SELECT id,info FROM block_content_field_data WHERE id=<id>"` | `entity:delete block_content <id>` | the query returns nothing |
| Media | `sqlq "SELECT mid,name FROM media_field_data WHERE mid=<mid>"` | `entity:delete media <mid>` | the query returns nothing |
| File | `sqlq "SELECT fid,filename FROM file_managed WHERE fid=<fid>"` | `entity:delete file <fid>` | the query returns nothing |
| Test page | `sqlq "SELECT nid,title FROM node_field_data WHERE nid=<nid>"` | `entity:delete node <nid>` | its URL returns 404 |
| `qa-<role>` user | `user:information qa-<role>` | `-y user:cancel --delete-content qa-<role>` | `user:information` finds no user |

Every command runs as `terminus drush yalesites-platform.<env> -- <command>`, with `<env>` taken
from the `.created` line being handled, never assumed to be the reviewed PR's multidev. Deleting media
does not delete its file, so each upload needs both lines. Deleting a test page does not delete
an unsaved Layout Builder draft for it either. After deleting the node, clear it:
`sqlq "DELETE FROM key_value_expire WHERE collection LIKE 'tempstore.shared.layout_builder%' AND (name = 'node.<nid>' OR name LIKE 'node.<nid>.%')"`. Then close every browser session
(`npx -y @playwright/cli@0.1.22 -s=<session> close`).

Report cleanup item by item, kept items included. If anything could not be removed or
reverted, say which item and why. Do not report cleanup as done while `.created` lists a
setting that has not been reverted, or, anywhere other than the reviewed PR's own multidev,
anything still in place. Leave the screenshots, clips, and `results.md`: they are the evidence
for the review.

## Handing results to the rest of the skill

- **Fails feed Step 4.** Each `fail` becomes a feedback point with its screenshot filename, the
  measured evidence, and the file and line from the brief. Images posted with the
  `github-screenshots` skill only show for org members, so it refuses the public PR repos.
  Tell the user which screenshots are worth adding, and offer two options: they drag those
  into the review comment, or, if the PR has a linked YaleSites-Internal issue, we post them
  there with `github-screenshots` and link that comment from the review. Ask which one.
  Posting on the issue is a GitHub write, so it needs the same confirmation as the review
  itself. `github-screenshots` posts images only, so a clip (the MP4) always goes in by the
  user dragging it into the review comment. A clip is often the fastest way for a developer
  to see a timing or focus bug.
- **Asks feed Step 3b** as questions, with their screenshots and clips. Those become the
  question's context on the review board (`references/review-board.md`), so frame each one so
  the call can be made from the picture or the clip.
- **Passes support the approval.** The approval body can say what was verified and as which
  roles, instead of a bare "tested on multidev".
- **Blocked steps are not passes.** Say plainly which steps could not run and why; the user
  decides whether to test those by hand before ruling.
