# Beyond-AC checks: what a thorough manual test actually covers

Read this from `SKILL.md` Step 3, after the acceptance criteria steps are written. It lists the
checks a human tester runs that no ticket asks for, so the test plan covers the blast radius of
a change and not just its stated goal.

**Where this came from.** A September 2026 read of every PR review and comment one reviewer
(the product manager) left across `yalesites-project`, `component-library-twig`, `atomic`, and
`tokens` since August 2025: 589 PRs, about 120 with findings from hands-on testing, roughly 300
findings. About half fell outside the acceptance criteria as written at review time, and a dozen
tickets had their AC rewritten afterward to absorb what the review found. The checks below are
the repeatable patterns behind those findings, each tied to real examples.

---

## How to use it

Do not run all fifteen on every PR. Use the trigger column to find the rows the diff touches,
and add those as steps after the AC steps. A copy-only PR might need two rows; a change to a
shared component might need eight.

**A row whose trigger matches is not optional.** To leave one out, name it and give the reason
before testing starts, so the user can overrule it. "Already known" or "deferred to another
ticket" is not a reason to skip: run it, and record the result as `fail (known)` with the
tracking ticket. A known issue says nothing about what else is broken in the same place.

The last column says whether a driven browser (Playwright) can settle the check on its own or
has to screenshot it and ask. Rows marked **ask** are design and product judgment: capture the
evidence, then put the question to the user in Step 3b. Never rule on those yourself.

## The checks

| # | Check | Trigger: add it when the diff... | Past examples | Driven browser |
|---|---|---|---|---|
| 1 | **Everything else that shares the changed code.** List the other blocks, forms, and pages that use the changed component, SCSS partial, form element, formatter, or library, and look at each. | touches a shared CLT component or partial, a form alter, a field formatter, a shared JS behavior | Linkit fix also broke the Header CTA and 10 of 11 Footer link fields (yalesites-org/yalesites-project#1466). Converting cells to `th` picked up library table styling (yalesites-org/yalesites-project#1552). Taxonomy and Tiles still showed the old color picker (yalesites-org/yalesites-project#1174). Divider went full strength on every default section (yalesites-org/component-library-twig#743). | yes: visit each consumer, compare against `dev` |
| 2 | **Every section layout, including the narrow regions.** One column, 50/50, 33/33/33, 70/30, 30/70, and specifically the 30% sidebar and 33% column. Check that a new block is offered in every region it should be and absent from the ones it should not (Banner). Fill the other columns of a section before judging a narrow one: empty regions are not rendered, so a lone sidebar block gets full width. Include an empty themed section. | adds or changes a block, a layout, a section setting, or anything with width-dependent CSS | Empty themed One column section painted no color band (yalesites-org/yalesites-project#1470). Filter row spilled out of 50/50 and 70/30 (yalesites-org/yalesites-project#1299). Moving a block between regions broke Configure with an Invalid UUID error (yalesites-org/yalesites-project#1532). | yes: place, save, check overflow and errors |
| 3 | **Section themes and global palettes, including hover and focus.** Every component theme on at least two global palettes. Contrast in resting, hover, and focus states. | touches color, tokens, theming, links, or any text over a background | Accordion heading near-invisible on theme five (yalesites-org/component-library-twig#705). Form select text at 1.36:1 (yalesites-org/component-library-twig#721). Hover contrast failed where resting passed (yalesites-org/component-library-twig#714). Gray-400 section foreground failures across many blocks (yalesites-org/yalesites-project#1242). | yes: compute contrast from rendered colors per combination |
| 4 | **In-between widths and Safari.** 360, 765, 992, 1200, 1440, and above 1400. Check Safari (WebKit) when images, aspect ratios, or container queries are involved. | changes CSS, images, grids, or breakpoints | Card grids lost stacking below about 765px, which Storybook could not reproduce (yalesites-org/yalesites-project#1532). EXIF-rotated photo went portrait in Safari at mobile width (yalesites-org/yalesites-project#1562). 70/30 divider only drew above 1400px (yalesites-org/component-library-twig#750). | yes: resize, and run the same steps in WebKit |
| 5 | **Other roles, and logged out.** See "Roles" below. Check the logged-out front end separately from the logged-in one. | adds a control, route, permission, form, or anything an editor sees | Only user 1 could add terms to the new vocabularies (yalesites-org/yalesites-project#1233). Front-end filters picked up admin styling for logged-in users only (yalesites-org/yalesites-project#1299). | yes: one session per role |
| 6 | **Other content types.** Page, Post, Event, Profile, Resource, including their locked sections. | touches Layout Builder, node forms, metadata, or anything content-type-aware | Post "Title and Metadata" section could be cloned into two titles (yalesites-org/yalesites-project#1529). Resource CSV import left out four fields (yalesites-org/yalesites-project#1462). "Archive" button showed on an unsaved event (yalesites-org/yalesites-project#1290). | yes |
| 7 | **Block form preview against the rendered front end.** Set an option in the form, then check both the preview and the saved page. | touches a block form, its preview, or its display options | Picker colors rendered as different colors on the front end (yalesites-org/yalesites-project#1174). Resource options changed nothing in the preview (yalesites-org/yalesites-project#1591). A DCN of "0" saved but vanished from the page (yalesites-org/yalesites-project#1386). | yes |
| 8 | **Content that existed before the change.** Look at a page already using the feature, not only a freshly made one. | adds a field default, update or deploy hook, schema change, or changes an existing setting's meaning | Existing In-Line Message blocks would lose their icon (yalesites-org/yalesites-project#1407). Saved "skip" values would suddenly start dropping items (yalesites-org/yalesites-project#1585). Microsite header did nothing on an existing collection until a cache flush (yalesites-org/yalesites-project#1200). | partly: view an existing visreg page, flag hooks to the user |
| 9 | **Empty and edge values.** Empty section or list, the value 0, leading whitespace, very long text, missing image. | handles user input, lists, captions, or exports | Long headingless captions lost their links (yalesites-org/component-library-twig#742). A leading space and hyphen exported with a visible apostrophe (yalesites-org/yalesites-project#1577). | yes |
| 10 | **Keyboard and screen reader basics.** Tab order, focus moving to the first error, `aria-describedby` wiring, focus outlines on the right element. | touches forms, errors, dialogs, menus, or interactive widgets | Focus did not move to the invalid image field (yalesites-org/yalesites-project#1581). Focus box wrapped the whole fieldset instead of the card (yalesites-org/yalesites-project#1513). | yes: press Tab, read the focused element, run an automated a11y scan |
| 11 | **Admin screens in Gin dark mode.** | touches any admin form, dashboard, picker, or preview | Color picker labels failed contrast in dark mode (yalesites-org/yalesites-project#1174). Announcement dates unreadable (yalesites-org/yalesites-project#1288). Block form preview followed dark mode when it should stay light (yalesites-org/yalesites-project#1342). | yes |
| 12 | **The Drupal log after testing.** Warnings and errors that never reach the screen. | always, on `yalesites-project` | White screen fixing a quick link URL (yalesites-org/yalesites-project#1251). Missing template white screen (yalesites-org/yalesites-project#1254). "Sync now" reported success next to an error (yalesites-org/yalesites-project#1355). | yes: `terminus drush <site>.<env> -- watchdog:show` |
| 13 | **Is the environment itself trustworthy?** PR testing links resolve, the server runs the branch's code (profile version and changed-file checksums, not CI status), no 500 on logged-in pages, deploy hooks did not already run under an old name. | always, first | Stale aggregated JS showed the old form (yalesites-org/yalesites-project#1477). Deleted JS still served (yalesites-org/yalesites-project#1482). Testing links 404ed (yalesites-org/yalesites-project#1557). Testing link used the wrong query parameter and looked exactly like the bug (yalesites-org/yalesites-project#1559). Every logged-in page 500ed (yalesites-org/yalesites-project#1587). CI green while the multidev ran a months-old profile, so a reported duplicate card was the stale code, not the PR (yalesites-org/yalesites-project#1311). | yes: run before any other step |
| 14 | **Editor UX polish.** Help text that contradicts the options, disabled fields that do not look disabled, missing selected states, wrong icon or category in the block picker, crowded spacing. | adds or changes anything an editor clicks | Help text promised "blank means closed" while blank days vanished (yalesites-org/yalesites-project#1477). Wizard cards had no selected state (yalesites-org/yalesites-project#1513). New picker entry showed the placeholder icon (yalesites-org/yalesites-project#1587). Help text still named a removed option (yalesites-org/yalesites-project#1593). | **ask**: screenshot, then Step 3b |
| 15 | **Labels agree everywhere.** The PR body, its testing steps, the UI, Storybook, and the ticket all use the same words. | renames anything, or ships testing steps | Testing steps used stale labels (yalesites-org/yalesites-project#1447). PR body said 1000000 while the code set 400000 (yalesites-org/yalesites-project#1492). PR bodies still said "Cards per row" after it became "Card size" (yalesites-org/yalesites-project#1532). | yes: compare strings, then flag mismatches |

## Roles

**User 1 is not a platform admin.** A `drush uli` with no user name logs in as user 1, which
bypasses every permission check. It sees routes, toolbar items, and form options that no real
role has: on a visreg multidev, user 1 opens `/admin/config` and a site administrator gets
Access denied there. A step "passed as admin" proves nothing about any real role. Use user 1
only for setup, never as the role under test.

The roles on the platform are `platform_admin`, `site_admin`, `editor`, `contributor`, and
`file_manager`, plus anonymous. Pick the ones the change touches; editor and site admin cover
most PRs.

To act as a role, log in with a one-time link for a user holding it:

```bash
terminus drush <site>.<env> -- uli --name=<username> --uri=https://<env>-<site>.pantheonsite.io
```

Run each role in its own browser session (`playwright-cli -s=<role> ...`) so cookies never mix,
and run the same steps in each.

**Where the users come from:**

- Visreg multidevs carry `e2etest`, a `site_admin`. Use it.
- There is usually no editor or contributor test user. Creating one is a write to the multidev,
  so ask the user once per PR first (the same gate as creating test content). Name them
  `qa-<role>`, and remove them when testing ends:
  ```bash
  terminus drush <site>.<env> -- user:create qa-editor --mail=qa-editor@example.invalid
  terminus drush <site>.<env> -- user:role:add editor qa-editor
  terminus drush <site>.<env> -- -y user:cancel --delete-content qa-editor
  ```
- **Never log in as a real person's account**, even though `uli --name` would allow it. Real
  accounts (NetIDs) exist on these environments; acting as one puts their name on whatever the
  test does.
