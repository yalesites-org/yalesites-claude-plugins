# Phase 3: charters, standing checks, and generators

Each hypothesis is explored in a **charter**: one focused, time-boxed session. This is session-based exploratory testing (Bach), adapted for a subagent. A charter has a clear target, a budget, and a debrief that says what was *not* covered. A quiet session is only a pass if it actually covered its target.

For bulk visual comparison (many pages at once rather than one condition), `yalesites-org/yalesites-automated-tests` has `scripts/compareSites.sh`, which compares two sites with Playwright. Its page list is hard-coded to the visreg component pages, so feed it the charter's real RC and live URLs instead. Treat its pixel diffs as leads for a charter to judge, never as findings.

## Writing a charter

Write one file per charter in `runs/<run>/charters/<NN>-<slug>.md`:

```markdown
# Charter <NN>: <one line>

Explore <surface> on <sites and pages> to find <the oracle from the hypothesis>.

- Hypothesis: h014 (<kind>, score <n>)
- PRs: yalesites-org/yalesites-project#1666
- Sites and pages: ys-your-yale-edu /about, ys-registrar-yale-edu /calendar
- Conditions to cover: <the untested condition, plus the pairwise rows if any>
- Login: logged out | user 1 (read-only) | user 1 or qa-<role> (reserved site only)
- Devices: desktop Chrome 1280 | phone (WebKit, iPhone 15) | both
- Budget: 20 minutes, or about 40 browser actions
- Evidence folder: runs/<run>/screenshots/<NN>/
```

Pick the pages from `rc_pages` in the impact map: real pages that already use the surface. Prefer live clones over other sources. Prefer two different sites over two pages on one site.

## Running a charter (the subagent's brief)

Start each charter with the Agent tool, at most two at a time. Give the subagent:

- the charter file path;
- the paths to `rc-sites.md` and this file;
- the session name `c<NN>`;
- and one instruction: read those, run the charter, write the debrief into the charter file, and reply with only the result line.

The subagent must:

1. **Check the site.** Fetch the page and record the response code. A 5xx is a finding.
2. **Drive it.** Use `pr-feedback/references/drive-it.md`, Step D3 "Driving the page", for the CLI commands, with `-s=c<NN>`. Prefer `run-code` with locators on forms.
3. **Capture the baseline.** For every check, capture the same page and condition on `live_url`. See "Baselines" in `rc-sites.md` for content drift.
4. **Measure, don't eyeball.** Bounding boxes, computed colors, `scrollWidth > innerWidth`, counts of items, response codes.
5. **Run phone checks on mobile WebKit**, not a narrow Chrome window (see "Phones" below).
6. **Screenshot every check**, pass or fail, named `<NN>-<result>-<site>-<device>-<slug>.png`. Follow "Screenshots: every step, pass or fail" in `drive-it.md`. Look at every image before giving it a result, and retake it if it is wrong.
7. **Re-run every failure once**, from a fresh page load. Agents misread pages that are still loading, and dynamic content, as failures. Only a failure that repeats is `confirmed`. A failure that does not repeat is `suspicious`, with both screenshots.
8. **Stay inside the rules** in `rc-sites.md`, "What the hunt may change": on the reserved site, edit and create freely, check `changes.md` before calling a finding, and log every change. On shared sites, read-only and Layout Builder discard only. No outbound forms anywhere.
9. **Close the browser session** when done.

### Phones

A narrow Chrome window tests breakpoints but not Safari's engine, touch instead of hover, or mobile form controls. So every phone check runs in Playwright's WebKit with iPhone emulation: Safari's engine, a 393px viewport at 3x density, an iPhone user agent, touch input, and `(hover: none)`.

```bash
npx -y @playwright/cli@0.1.22 -s=c<NN>-m open --browser webkit --device "iPhone 15" '<RC url or login link>'
```

- A phone session is its own session (`-s=c<NN>-m`), so it needs its own `uli` link: one-time links do not carry across sessions.
- Capture the live baseline in the same device setup.
- What to look for on phones in particular: sideways overflow (`document.documentElement.scrollWidth > innerWidth`), menus and dropdowns that only open on hover, sticky headers covering content, full-height heroes, tap targets under 24px, and images or embeds wider than the screen.
- This is still emulation, not a real iPhone. It does not show the Safari toolbar changing the screen height, real iOS fonts, or native date and select pickers. If a finding depends on those, mark it `suspicious` and say "needs a real iPhone or the iOS Simulator to confirm".

### Debrief

Append this to the charter file:

```markdown
## Debrief

- Result: confirmed | suspicious | clean | blocked (<reason>)
- Covered: <conditions actually checked, with counts>
- Not covered: <conditions in the charter that were not reached, and why>
- Findings: <one line each: what, where (URL), RC vs live, screenshot file names>
- Obstacles: <anything that wasted time: login, slow site, missing content>
- Changes: <reserved site only: each change as URL, what changed, value before. Also appended to `changes.md`. "none" on shared sites.>
- Leftovers: <anything left changed on a shared site. Should be "none". Reserved-site changes go under Changes instead.>
- Time: <minutes>, split into setup, testing, and investigating
```

Set `clean` only when "Not covered" is empty or trivial. Otherwise use `suspicious` or `blocked`, so the hypothesis stays open for a later run on another site.

### Findings are classes

One finding is usually one instance of a pattern. In v2.33.0 the hunt found "Padding Options" printed under a *reusable* listing (yalesites-org/YaleSites-Internal#2127) and stopped there. A tester then found the same text under an ordinary inline View block (yalesites-org/YaleSites-Internal#2312). The same visible-field config sat on 46 block types.

So every `confirmed` or `suspicious` finding gets a sibling sweep charter, ranked just under standing hypotheses:

- **Same cause, other surfaces.** Grep the config, template, or CSS that caused it (`config/sync`, atomic, CLT) and list every other block type, view, or form that has the same thing. Check each one.
- **Both placements.** Inline and reusable.
- **Set and unset.** The option at its default, empty, and at every other value. A field that is empty on old content often hides a bug that any edit shows.
- **Same class of bug on other surfaces.** A cache bug on news listings means checking every other list built from content (filter options, calendars, menus). A dead option on one block means checking the same option on every block that has it.

**"Pre-existing" needs proof.** Only call a finding pre-existing with a live screenshot of the same thing, or a code reference showing the cause shipped before this RC. Without that, report it as `new until proved otherwise`, so the board treats it as an RC bug and not a backlog item. New block types in the RC (for example the per-style listing blocks) cannot have pre-existing bugs.

## Standing checks

These run once per RC site per run, besides the charters. They are cheap, and they find the bugs no page view shows.

### Log diff

```bash
terminus drush <site>.<branch> -- watchdog:show --count=1000 --severity-min=Warning --format=json
terminus drush <site>.<branch> -- migrate:status --format=json
terminus drush <site>.<branch> -- state:get system.cron_last
```

The clone carries live's log with it. Split the RC's own log at `cloned_at`: entries before it are live's baseline, entries after it are the RC's. This needs no production reads, which matters because an unattended session is not allowed to read `live` with drush.

**Check the baseline first.** dblog keeps only 1000 rows (`row_limit: 1000` in the profile's `dblog.settings.yml`), and cron on the multidev trims the oldest, so on an older multidev every pre-clone row can be gone. Fetch the full 1000 rows, as above. If the oldest returned entry is not older than `cloned_at`, there is no baseline: mark the log diff `blocked: no pre-clone baseline` and do not report any group as new. In attended mode, with the user's OK, read `<site>.live` instead and compare against that. In `--drain`, leave it blocked. When there is a baseline, say in the report how many pre-clone rows the comparison rests on, since a thin one can make an old message look new.

Group the messages by type and by message text with the numbers stripped out. Report message groups that appear after `cloned_at` and not before, or much more often after it.

Cron runs on its own on Pantheon. Do not run it. If `system.cron_last` is older than about 3 hours, or cron entries after `cloned_at` include errors, report it. A warning that fires on every page view (yalesites-org/YaleSites-Internal#1824) shows up here and nowhere else. Check `migrate:status` for failed or stuck migrations (yalesites-org/YaleSites-Internal#1394).

The charters' own visits write to the same log. Match entries to the charters by timestamp, and say which ones the hunt caused.

### Old-data queries

For every update hook, new required field, new validation rule, or changed default that the impact map found:

1. Write a read-only `SELECT` that finds existing entities that would fail it or be changed by it. Look for empty values in the new field, legacy values, and the oldest revisions. Example: `sqlq "SELECT b.id, b.type, b.changed FROM block_content_field_data b LEFT JOIN block_content__field_new f ON f.entity_id=b.id WHERE b.type='cta_banner' AND f.entity_id IS NULL ORDER BY b.changed LIMIT 20"`.
2. Find pages that use those entities. For inline blocks, the `inline_block_usage` table maps `block_content_id` to `layout_entity_type` and `layout_entity_id` (the node). For reusable blocks, search the layout data for the block's UUID, or start from pages in the portfolio crawl that use that block type.
3. Render those exact pages and compare them with live. Where the hypothesis is about saving, open the block form through Layout Builder and discard it (see `rc-sites.md`).

This is how Drupal core tests update paths: on a database full of real content, not an empty one.

### Accessibility on changed surfaces

On each RC page a charter visits, run axe on the changed surface only:

```js
// in run-code
async page => {
  await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js' });
  return await page.evaluate(sel => axe.run(document.querySelector(sel) || document,
    { runOnly: ['wcag2a', 'wcag2aa'] }).then(r => r.violations.map(v => ({ id: v.id, n: v.nodes.length }))), '<selector>');
}
```

If the selector matches nothing, the snippet falls back to the whole page. Record that, since a whole-page count is not comparable with a scoped one. Run the same check on live. Only violations that are new on the RC are findings. If the script tag is blocked, fall back to Editoria11y's results when logged in (see `yalesites-page-build` Step 6).

axe does not know what a widget is meant to be. A row of `div`s styled as tabs has no rule to break, so axe passes it. Widgets get their own check, below.

### Visitor cache

Charters judge renders with a cache-busting query (`?cb=<n>`), which is right for comparing RC and live. But it hides what a real visitor gets: Pantheon's edge cache serves a saved copy for up to a day (`cache-control: max-age=86400`), and a page is only fresh if Drupal's cache tags purge it. In v2.33.0 every logged-out check was cache-busted, one charter even noted a stale copy after a Save and worked around it, and testers then found an events calendar whose Category filter was empty for visitors (yalesites-org/YaleSites-Internal#2307).

**A stale copy is never noise. It is a finding.**

On the reserved site, for every surface built from other content (listings, filter option lists, calendars, menus, breadcrumbs, counts, "related" blocks):

1. Load the page logged out with **no** cache-busting query, twice, and record `x-cache`, `age`, and `cache-control`. The second load should be a `HIT`.
2. Change what the surface is built from: add a taxonomy term, publish or unpublish an event or post, rename a term, add a menu link. Log it in `changes.md`.
3. Wait about 60 seconds for the purge, then load the same URL logged out, again without busting, and record the headers.
4. Load it once more with a cache-busting query. If the plain load and the busted load differ, the surface is missing a cache tag. Confirmed if it repeats after another 60 seconds.

Also test the empty state: build the surface while it has nothing to show (a filter with no terms yet), let a logged-out load cache it, then add the content. That is exactly how yalesites-org/YaleSites-Internal#2307 happened.

On shared RC sites, only step 1 is allowed (it is a read). Compare a plain logged-out load with a busted one on pages that show recent content, and report any difference as `suspicious`.

### Layout Builder AJAX parity

Layout Builder re-draws the whole layout over AJAX after each add, remove, move, or configure. That response can render blocks with a different theme or template than a full page load, so blocks nobody touched change. Testers found a View block's filter form turning into a floating card after a *different* block was removed (yalesites-org/YaleSites-Internal#2310).

On the reserved site, on a page with several changed block types (listings with filters, calendars, and anything with JS behaviors):

1. Load `/node/<nid>/layout` and snapshot every block: the class list of the block wrapper and its first two levels of children, plus the computed `display`, `position`, `box-shadow`, `background-color`, and bounding box of each.
2. Do one action: add a block, remove a block, move a block, or configure and Update a block.
3. Snapshot every block again, *except* the one acted on.
4. Reload the page and snapshot a third time.

Any block whose AJAX snapshot differs from its reload snapshot is a finding. Run all four actions, and repeat with two View blocks of different types on one page. Discard or save as the charter needs, and log it. Skip this on shared sites: it needs real edits.

### Widget patterns

For every widget in the impact map's `widgets` list (visitor pages and authoring screens alike), check it against its pattern in the WAI-ARIA Authoring Practices Guide (https://www.w3.org/WAI/ARIA/apg/patterns/). Read the Playwright accessibility snapshot, then drive it with the keyboard only:

| Pattern | Must have |
|---|---|
| Tabs | `tablist`, `tab` with `aria-selected`, `tabpanel` linked by `aria-controls`. Arrow keys move between tabs, one tab stop for the bar. |
| Switch or toggle | A name and Space to toggle, plus an exposed on/off state: a `switch` or `checkbox` role needs `aria-checked`, while a native `input[type="checkbox"]` uses its HTML `checked` state instead and is not a gap without `aria-checked`. |
| Multi-select or listbox | A name, `aria-expanded` on the trigger, options hidden while closed, `aria-selected` on chosen options, a labeled remove button for each selection, labeled option groups. |
| Dropdown, popover, or dialog | A **visible** way to close it, plus Escape and click outside. Focus returns to the trigger. While a popover is open, decide whether the rest of the page should still react. |

Compare with live where the widget exists there. A gap that live shares is still reported, marked pre-existing with the live evidence, because a widget the RC newly puts in front of editors raises its weight. Testers found the Views block form's tabs and switches with no roles (yalesites-org/YaleSites-Internal#2323), a multi-select screen readers can't use (yalesites-org/YaleSites-Internal#2324), and no way to close it (yalesites-org/YaleSites-Internal#2313) after the hunt's axe passes came back clean.

### Fleet config scan

Some bugs live in a stored setting on a site outside the RC list (yalesites-org/YaleSites-Internal#1735 was on gsa.yale.edu). When the RC adds validation to a setting, a read-only `config:get` across every site would find the sites that would fail it.

This touches about 299 production sites. **Attended mode only**, with the user's yes each time, until the team agrees otherwise (see `SKILL.md`). Never run it in `--drain`. When it runs, do it one site at a time, `config:get` only, against `live`, and stop at the first error that is not "config does not exist".

## Generators

When the ranked list is used up, make new charters from these, in this order. Weight every value by real use from the portfolio crawl, so common setups come first.

1. **Option effect.** For every block the RC changed, and every block in the impact map's `allowlist_widenings`, on the reserved site: place it (in each newly allowed region too), then set each editor option to each non-default value, one at a time, and save. Render the page logged out after each, and check two oracles:
   - **The page changed.** Compare the block's rendered HTML and screenshot with the previous value. No visible difference means a dead control: an option editors can pick that does nothing (yalesites-org/YaleSites-Internal#2314). Run it on an uncolored section and on each section color, since a section color can override the option.
   - **Nothing leaked.** Collect every field label and every option label from the block's form, then search the block's rendered text for each one. Any match is a leak of editor-only text (yalesites-org/YaleSites-Internal#2312).
   Use the pairwise script for blocks with many options. On shared sites this generator is `blocked: needs saves`.
2. **Pairwise combinations over the changed blocks.** Factors: global theme, section color, layout region, and device (phone on WebKit, tablet at 768 in Chrome, desktop at 1280 in Chrome). Take the values from what real sites use: `global_theme` in `sites-index.csv`, and `data-component-theme` plus the width and variation attributes in each site's `raw/sites/<site>.json`. Don't guess values, and drop empty ones (`global_theme` is blank for some sites). Generate the rows with `scripts/pairwise.py` (2-way), then find a real RC page that matches each row. 2-way covers most configuration bugs but not all of them, so also run 3-way, but only for blocks the RC directly changed.
3. **Content extremes.** Pages where the changed block has empty optional fields, a missing image, one item, the most items on any RC site, the longest title, or a long URL in a teaser (yalesites-org/YaleSites-Internal#1729). Find them with `SELECT`s, not by browsing.
4. **Date boundaries** for anything that shows dates or events. Month ends, multi-day events, all-day events, recurring events, and the current month's last day (yalesites-org/YaleSites-Internal#1374, yalesites-org/YaleSites-Internal#1379).
5. **Reusable vs. inline.** The same block type in existing placements of both kinds, found with a `SELECT` (on shared sites, never create one or submit a reusable block's form; see `rc-sites.md`) (yalesites-org/YaleSites-Internal#1381).
6. **Neighbors.** The changed block directly above and below each other block type it appears next to on real pages, and nested in tabs or accordions where that is possible.
7. **Phones.** Every changed surface on mobile WebKit (see "Phones" above), on the RC pages with the most items or the longest content. Safari-only bugs are real (yalesites-org/YaleSites-Internal#1730, an EXIF-rotated photo that broke a card in Safari).
8. **Editor sessions.** Act out a real editor on the reserved site, using the archetypes in the `ux-research` skill, at human pace through the normal screens. Two things PR steps never do:
   - **Realistic content.** Clone existing posts and events, back-date some, future-date others, and leave clones with the dates they came with. Whenever something the editor made does not show up where they expected, check whether the screen explains why. Silent filtering is a finding even when the behavior is intended (yalesites-org/YaleSites-Internal#2311).
   - **Change your mind.** After building a block, reopen it and try to change every choice made while creating it: wizard steps, display style, content type, layout. A choice that can only be undone by deleting and rebuilding is a finding (yalesites-org/YaleSites-Internal#2309).
9. **Another site.** A `clean` hypothesis, re-run on an RC site it has not been run on. This is the lowest priority: it never mattered in the hotfix lookback.

A generated charter gets a hypothesis entry of kind `generated` and goes through the same rules: concrete oracle, baseline, re-run, debrief.
