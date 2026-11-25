# Writing and running the test plan (Step 3 detail)

Read this from `SKILL.md` Step 3. It covers sizing the blast radius, naming the environment and
what it cannot show, the rules for the steps, and when to drive the run or hand it off.

## Step 3: Walk the user through what to test

**This is the skill's main output.** Everything before it was preparation and everything
after it is posting. The reviewer is usually not the developer who built it, whatever their
role: the useful thing this skill produces is a short, concrete answer to "where do I go and
what do I click."

The brief's **Where to test** and **Draft test plan** sections are the starting point. Treat
the draft as a draft. The audit has never seen the feature work and its plan will be
over-thorough in some places and thin in others. Cut it down to what genuinely needs a human
looking at it.

### Size the blast radius with real usage data

When the PR changes a block's template, styles, or data model, or ships an update hook
against a block or setting, use the `yalesites-portfolio` skill if it is available (it
ships in the separate `yalesites` plugin; if it is not installed, skip this step and don't
estimate usage numbers). Say in the test plan how many sites the change touches ("grand
hero renders on 202 of 296 crawled sites, as of the 2026-10 crawl") and name 2-3 of the
heaviest-usage sites from the block's `Top sites` line in its `references/block-usage.md`.
Those live sites run the current code, so they are where to see current behavior and
where to find the content shape to recreate on the PR's preview (the multidev, or the
sibling yalesites-project multidev for a component-library-twig or atomic PR); they are
not where the change gets tested. A yalesites-project multidev carries one site's content,
so the plan says "build a page shaped like poorvucenter's grand hero on the multidev and
check it there", never "check it on poorvucenter". A regression in a 70%-adoption block is a
platform incident; the same bug in a 5% block is a patch. The test plan should reflect
which one this is. Skip this step for PRs that don't touch a measurable block or setting:
don't pad reviews with usage trivia.

### Lead with the environment, and be specific about what it can show

Resolve the URL from the brief. If the brief says there is no environment, say that first,
because it changes what this review can conclude.

| Repo | Where | What it cannot show |
|---|---|---|
| `yalesites-project` | Pantheon multidev, the full CMS | Nothing, this is the real thing |
| `component-library-twig` | Netlify deploy preview, Storybook only | Layout Builder placement, editor field labels, role gating, anything that depends on Drupal passing real values in |
| `atomic` | No preview of its own. The sibling `yalesites-project` PR's multidev, if one exists | If there is no sibling, there is no deployed way to see this. Say so. |
| `tokens` | No preview of its own. The sibling `component-library-twig` preview, if one exists | Same. Say so. |
| `yale-ui-cl` | The PR's deployed Storybook preview if it has one (none do yet), otherwise Storybook built locally from the PR head (`drive-it.md`, "The `yale-ui-cl` path"). Its GitHub Pages Storybook (`https://yalesites-org.github.io/yale-ui-cl/`) builds from `main` only, so it is the baseline, never the PR's environment | Anything that depends on a consuming site: how YaleSites or another app passes real values in |

Full patterns and the direct visreg content URLs are in
`preview-environments.md` (this folder). Do not restate the block slug table
here, and do not guess a URL: the brief resolved it by probing, so use what it resolved.

When the environment is Storybook and the ticket's acceptance criteria are about what an
**editor** can do, say plainly that the preview cannot answer that. It is a real limit on the
review, not a detail.

### Then give the steps

Short numbered list. Each step is a link, an action, and what should happen:

```
1. Open <direct URL>. The table headers should each carry scope="col" (check with the
   inspector or a screen reader).
2. Drag that block into a 33% section. Expected: no horizontal scrollbar at 1440px or 360px.
3. Log in as an editor, not platform admin. Expected: the new control is visible.
```

Rules that make this useful instead of noise:

- **Cover the acceptance criteria first, then the blast radius.** After the AC steps, read
  `beyond-ac-checks.md` and add the rows whose trigger matches what the diff
  touches: other places that share the changed code, other section layouts and themes,
  in-between widths, other content types, existing content. About half of past manual review
  findings sat outside the AC, so a plan that stops at the AC misses them. A row whose trigger
  matches gets run; skipping one needs a stated reason before testing starts, and "already
  known" is not one. Row 1 (other places that share the changed code) starts from the
  brief's **Regression surface** section, which names each consumer and where to see it.
  Every consumer listed there gets a step; a brief without that section predates it, so do
  the grep yourself.
- **Flag any step that needs a role other than platform admin.** The user is a platform admin
  by default, so a role-gated step silently passes for them and fails for everyone else. This
  is the single most common thing a non-developer review misses. A `drush uli` login is user 1, which is
  not a platform admin either; see "Roles" in `beyond-ac-checks.md`.
- **Keep it to what a human must see.** If CI already proves it, or the audit already verified
  it from the code, leave it out and say the audit covered it.
- **Say how long it should take.** Three steps or ten changes whether this happens now.

This is a walkthrough for the user in chat, not a GitHub comment. Do not post it, and do not
copy it onto the ticket as Release Testing Steps. Those are written later, at release prep, once
the behavior is settled.

### Then drive it, or hand it off

**Every `yalesites-project` review gets a driven browser run.** A current prepped board
(Step 1) already carries one, so it is not repeated. Otherwise it is not optional, and it
does not depend on where the brief came from. A brief a scheduled pass or an override skill wrote,
a stale one refreshed from the new commits, and one `pr-brief` wrote at the start of this
session all lead to the same run. Do not offer the hand-off walkthrough as
an alternative, and do not ask whether to drive it. Read `drive-it.md` and follow
it: preflight (including proof the server runs the branch, since green CI does not show that),
the brief and plan before any testing, create test content without asking (running the skill
is consent, `drive-it.md` Step D1), log in per role with
`drush uli`, run each step in a visible Playwright browser while the user watches, screenshot
every result (pass, fail, ask, or blocked), record a short clip where the step is about
behavior over time (a dialog, focus order, an AJAX rebuild), check the Drupal log, and clean
up (settings reverted, test content kept on a PR multidev so the reviewer can recheck it).
Show the screenshots as the run goes, failures first. Checks marked `ask` in
`beyond-ac-checks.md` are never ruled on by the browser run; they go to Step 3b with
their screenshots.

**Every `yale-ui-cl` review gets a driven browser run too,** under the same rules: required,
not offered, and not repeated when a current prepped board already carries one. Follow "The
`yale-ui-cl` path" in `drive-it.md`: check first for a deployed Storybook preview
and drive that if the PR has one; otherwise build Storybook locally from the PR head in a
checkout the skill owns, drive the stories, screenshot every result at the widths the plan
names, record clips for behavior over time (focus order, menus, tabs and accordions, pagers),
and capture side-by-sides against the published UICL Storybook on `main` and the matching CLT
story for parity and change questions. Then stop the server and remove the checkout.

**No brief yet is not a reason to skip the run.** When Step 1 has to write the brief itself,
open the browser and do the setup (log in, create the test page) while the brief is being
written, then start testing once the plan exists. The user gets something to watch without the
run getting ahead of the plan.

**The hand-off walkthrough is for what cannot be driven, and only that.** That covers
`component-library-twig` Storybook, `atomic`, and `tokens`; a `yalesites-project` PR whose
drive-it preflight fails (no multidev, a server not running the branch, a cloud session, a
machine without Terminus or Node); and a `yale-ui-cl` PR with no deployed preview whose local
preflight fails (no Node, no `YALESITES_BUILD_TOKEN`, `npm ci` failed, Storybook did not
build, a cloud session). For a failed preflight, say which check failed, hand the plan to the user, and offer to
run the browser pass as soon as the cause is fixed: a skipped run is a gap in the review, not
a different kind of review. Write the hand-off plan for someone reading it on a second monitor
with the PR open.

**Hand-off never means no pictures.** A hand-off covers the steps a human has to do (an
editor's view, Layout Builder, a role), not the screenshots. Every board question about
something a person can see (layout, size, spacing, wording, color, a message, a Storybook
story) carries at least one `image` or `compare` block, and that holds in prep runs and live
runs alike. So for `component-library-twig`, and for `atomic` or `tokens` through the sibling
preview, open the Storybook deploy preview story in Playwright and screenshot it, even when
the rest of the walkthrough stays hand-off. Where the question compares two states (current
against this PR, two widths, two variants), screenshot both: the published Storybook story on
`main` as `Published:` and the deploy preview as `Preview:`, in one `compare` block. When the
preview is down or the story is missing, screenshot the closest thing that shows the problem
(the published story, the sibling multidev, the PR's own screenshots) and say so in the
caption; never leave a visual question bare. Only process questions (which release it ships
in, who owns a follow-up) are exempt, and they say so with `"process": true` in the packet
(`references/review-board.md`, "Every visual question gets a picture"). The packet check
fails any other question with no picture.
