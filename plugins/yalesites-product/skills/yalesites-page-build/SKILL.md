---
name: yalesites-page-build
description: "Build a drafted page on yalesites.yale.edu in a visible Playwright browser: create an unpublished page, or stage a forward draft revision of a published one, assemble it in Layout Builder, and verify it before handing it back. Use when the user asks to build, stage, create, or put a page draft on the site, e.g. 'build this page on yalesites.yale.edu', 'create a draft of this page with Playwright', 'stage the docs for #1818', 'put this into Layout Builder', or right after yalesites-web-content produces a page draft. Never publishes. Covers the production safety rules, the Tasks sidebar Create New Draft workflow, Layout Builder recipes (Text, Quote Callout, View, Divider, moving blocks), the team's layout conventions (end on a non-text block, padding between adjacent blocks), and the verify pass (logged-out check, Editoria11y, screenshots)."
argument-hint: "[path to a page draft .md, or a ticket like yalesites-org/YaleSites-Internal#1818]"
---

# YaleSites Page Build

`yalesites-web-content` writes the page. This skill puts it on yalesites.yale.edu, in Layout Builder, as a draft nobody outside the team can see. It drives a headed browser on the user's machine so they can watch, and it ends every build with evidence: a logged-out check, an Editoria11y count, and screenshots.

**This is production.** The Gin toolbar says "Live Site." Everything here is built around one promise: the public site does not change until a person clicks Publish on release day. Nothing in this skill ever clicks Publish.

## Workflow

1. Have a page draft. If there is none, run `yalesites-web-content` first.
2. Preflight and log in (the user does CAS)
3. Decide: new page, or forward draft of a published page
4. Create the draft
5. Build the layout, following the layout conventions
6. Save as Draft, then verify
7. Hand off, and record what was created

---

## Step 1: Start from a page draft

Build from a draft that already passed `check-github-text.py --surface page-draft`. The draft's **Suggested blocks** line is the build plan. Building straight from a ticket skips the code research and the STE pass, and the page shows it.

If the draft is an edit to an existing page and leaves the teaser alone, copy the live teaser into the draft's `## Teaser` block (read it from the page's `<meta name="description">`). The checker requires a teaser and has no "unchanged" mode yet.

## Step 2: Preflight and log in

| Check | How | If it fails |
|---|---|---|
| Node is available | `command -v npx` | Hand the draft to the user to build by hand. |
| The CLI opens a browser | `npx -y @playwright/cli@0.1.22 -s=preflight open about:blank`, then `-s=preflight close` | See the Browsers table in `pr-feedback/references/drive-it.md`. |
| The session is on the user's desktop | not a cloud session | A headed browser nobody can see is pointless. Hand off. |

Make a run folder and a wrapper, since zsh does not word-split a command held in a variable:

```bash
RUN=~/.claude/yalesites/page-build/runs/<slug>-<YYYY-MM-DD>
mkdir -p "$RUN" && cat > "$RUN/pw" <<EOF
#!/bin/zsh
cd "$RUN"
exec npx -y @playwright/cli@0.1.22 -s=ys "\$@"
EOF
chmod +x "$RUN/pw"
"$RUN/pw" open --headed 'https://yalesites.yale.edu/user/login'
```

Then ask the user to log in with CAS in that window, and wait for them to say so. **Never type a NetID, password, or Duo code**, and never use `drush uli` against production. Confirm the login by reading `page.url()` after they reply. The session dies when the browser closes, so a second pass needs a second login.

## Step 3: New page, or forward draft?

| Situation | Do this |
|---|---|
| The page does not exist yet | New node: `/node/add/page`, saved with **Create New Draft** |
| The page exists and is published, and the change is for a future release | Forward draft through the **Tasks** sidebar (Step 4b). The live revision stays up. Release day is one Publish. |
| The page exists and the Tasks sidebar says `Status: Draft` | **Stop and ask.** Someone already has unpublished work on it. Building on top would mix their draft with ours. |
| The draft replaces a published page with a new URL | Build it as a new node. The swap (publish, redirect, unpublish the old one) is a release-day task. List it in the handoff. |

Before creating a new node, check `/admin/content?title=<title>` for a node you (or a failed earlier attempt) already made. A save that looks like it did nothing may still have created a node.

## Step 4a: Create a new page

On `/node/add/page`, fill **Title** and the teaser, then save with **Create New Draft**. Leave the menu link off unless the draft asks for one.

- The teaser field is CKEditor 5. Set it with the editor instance, not `fill` (see `references/playwright-recipes.md`). It has a 150-character limit.
- **Click the sticky header copy of the save button**, `#gin-sticky-edit-moderation-state-draft`. The form's own `#edit-moderation-state-draft` sits off screen, and a click on it silently does nothing.
- **Parent item only exists on a menu link.** Setting a parent means turning on **Provide a menu link**, which puts the page in that section's dropdown. "Breadcrumb only, not in the menu" is not an option on YaleSites. If the draft asks for that, it means no menu link at all. Say so in the handoff.
- The save lands on `/node/<nid>/layout`. Record `node <nid>` in `$RUN/.created`.

## Step 4b: Stage a forward draft of a published page

1. Open the page and select **Tasks** in the top right. The moderation sidebar opens.
2. Confirm it reads `Status: Published` and offers **Create New Draft**. If not, go back to Step 3.
3. Check **Use custom log message** and write one that a stranger can act on: `DRAFT for 12-01-26 release: <what> (<owner/repo#N>). Do not publish before the release ships.`
4. Select **Create New Draft** (`#create_new_draft`). The page lands on `/node/<nid>/latest`.
5. Confirm on `/node/<nid>/revisions`: the new revision is on top, and the old one still says **Current revision**.
6. Record `draft-revision node <nid> (<ticket>)` in `$RUN/.created`.

The Layout Builder save form has no log message field. The Tasks sidebar is the only place to leave the note, so do not skip step 3.

## Step 5: Build the layout

Work from direct URLs rather than clicking the Layout Builder UI. Drupal serves every Layout Builder dialog as a full page, and URLs survive the AJAX rebuilds that break element refs.

| Need | URL |
|---|---|
| Map the page | `/node/<nid>/layout`, then read `.layout-builder__section` and `[data-layout-block-uuid]` in order |
| Block picker (shows real block names and reusable blocks) | `/layout_builder/choose/block/overrides/node.<nid>/<section>/<region>` |
| Add an inline block | `/layout_builder/add/block/overrides/node.<nid>/<section>/<region>/inline_block%3A<type>` |
| Edit a block | `/layout_builder/update/block/overrides/node.<nid>/<section>/<region>/<uuid>` |
| Reorder | `/layout_builder/move/block/overrides/node.<nid>/<section>/<region>/<uuid>` |

A new page's content region is section `2`, region `content`. A new block always lands at the **end** of its region, so plan to move it (recipe in `references/playwright-recipes.md`).

**Never edit a reusable block.** Its form has no **Reusable Block** checkbox. An edit to one goes live on every page that uses it at once, whatever the moderation state of this page. Placing an existing reusable block is fine and encouraged (see the conventions).

**Leave Reusable Block unchecked** on every new inline block. It starts unchecked; check it anyway.

**Read before you write on an existing page.** Pull each target block's HTML with `getData()`, change it with an exact string replace, and log whether the pattern was found. A replace that finds nothing must report `NO CHANGE`, not pass silently.

Read `references/layout-conventions.md` before placing anything. It holds the team's rules for how pages end, how padding works between blocks, and how to match a page's existing rhythm.

## Step 6: Save as Draft, then verify

Save from the layout page: set `moderation_state[0][state]` to `draft` **explicitly**, then submit `#edit-submit` (**Save layout**). On a published node the select can default to Published.

Then prove it:

| Check | How | Pass |
|---|---|---|
| The public cannot see it | `curl -s -o /dev/null -w "%{http_code}"` on the new page's URL, logged out | `403` |
| The live page did not change (forward draft) | `curl` the live URL, logged out, and grep for a phrase from the new copy | `0` matches |
| The revision stack is right | `/node/<nid>/revisions` | our revision on top, the old one still **Current revision** |
| No new accessibility alerts | On `/node/<nid>/latest`, wait 2 seconds, read `ed11y-element-result` elements and their `result.test` | Zero alerts inside the blocks we touched. Pre-existing alerts get reported, not fixed |
| It looks right | Full-page screenshot at 1280 wide, plus a clip of each changed area | Open every image and look before calling it a pass |

If Editoria11y flags something we wrote (for example `LINK_STOPWORD` on link text like "View"), fix it and save again.

Full-page screenshots at phone width come out blank because of the sticky toolbar and moderation bar. For mobile, check `document.documentElement.scrollWidth <= innerWidth` and take a viewport screenshot instead.

## Step 7: Hand off

Report, in this order:

1. The draft URL and node ID, and that it is unpublished (with the 403 or the unchanged-live proof)
2. What was built, block by block, with the Layout Builder labels used
3. Anything that differs from the page draft, and why
4. Release-day steps: publish, redirects, unpublishing a replaced page, cross-links on other pages, screenshots still owed
5. Pre-existing problems noticed on the page (broken links, old Editoria11y alerts), offered as separate fixes rather than slipped into this draft
6. Where the screenshots are

Update the page draft `.md` so it matches what was built. Then close the browser (`$RUN/pw close`). Leave `.created` and the screenshots in the run folder.

## Undoing a build

Only when the user asks. For a new node, delete it from its Tasks sidebar (**Delete content**) after checking the title. For a forward draft, open `/node/<nid>/revisions` and revert to the revision marked **Current revision**. Deleting the draft revision itself needs an admin. Work only from `.created`.

## Related skills

- `yalesites-web-content`: writes the page draft this skill builds
- `pr-feedback`: `references/drive-it.md` has the shared Playwright CLI setup and the screenshot discipline this skill borrows
- `release-prep`: publishes the staged drafts on release day
