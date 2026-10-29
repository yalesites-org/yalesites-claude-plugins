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
- Login: logged out | user 1 (read-only)
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
5. **Screenshot every check**, pass or fail, named `<NN>-<result>-<site>-<slug>.png`. Follow "Screenshots: every step, pass or fail" in `drive-it.md`. Look at every image before giving it a result, and retake it if it is wrong.
6. **Re-run every failure once**, from a fresh page load. Agents misread pages that are still loading, and dynamic content, as failures. Only a failure that repeats is `confirmed`. A failure that does not repeat is `suspicious`, with both screenshots.
7. **Stay inside the rules** in `rc-sites.md`: read-only, Layout Builder discard only, no outbound forms.
8. **Close the browser session** when done.

### Debrief

Append this to the charter file:

```markdown
## Debrief

- Result: confirmed | suspicious | clean | blocked (<reason>)
- Covered: <conditions actually checked, with counts>
- Not covered: <conditions in the charter that were not reached, and why>
- Findings: <one line each: what, where (URL), RC vs live, screenshot file names>
- Obstacles: <anything that wasted time: login, slow site, missing content>
- Leftovers: <anything left changed. Should be "none".>
- Time: <minutes>, split into setup, testing, and investigating
```

Set `clean` only when "Not covered" is empty or trivial. Otherwise use `suspicious` or `blocked`, so the hypothesis stays open for a later run on another site.

## Standing checks

These run once per RC site per run, besides the charters. They are cheap, and they find the bugs no page view shows.

### Log diff

```bash
terminus drush <site>.<branch> -- watchdog:show --count=500 --severity-min=Warning --format=json
terminus drush <site>.<branch> -- migrate:status --format=json
terminus drush <site>.<branch> -- state:get system.cron_last
```

The clone carries live's log with it. Split the RC's own log at `cloned_at`: entries before it are live's baseline, entries after it are the RC's. This needs no production reads, which matters because an unattended session is not allowed to read `live` with drush. In attended mode you may also read `<site>.live` directly, with the user's OK, when the cloned log is too short to compare.

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

### Fleet config scan

Some bugs live in a stored setting on a site outside the RC list (yalesites-org/YaleSites-Internal#1735 was on gsa.yale.edu). When the RC adds validation to a setting, a read-only `config:get` across every site would find the sites that would fail it.

This touches about 299 production sites. **Attended mode only**, with the user's yes each time, until the team agrees otherwise (see `SKILL.md`). Never run it in `--drain`. When it runs, do it one site at a time, `config:get` only, against `live`, and stop at the first error that is not "config does not exist".

## Generators

When the ranked list is used up, make new charters from these, in this order. Weight every value by real use from the portfolio crawl, so common setups come first.

1. **Pairwise combinations over the changed blocks.** Factors: global theme, section color, layout region, viewport width (360, 768, 1280). Take the values from what real sites use: `global_theme` in `sites-index.csv`, and `data-component-theme` plus the width and variation attributes in each site's `raw/sites/<site>.json`. Don't guess values, and drop empty ones (`global_theme` is blank for some sites). Generate the rows with `scripts/pairwise.py` (2-way), then find a real RC page that matches each row. 2-way covers most configuration bugs but not all of them, so also run 3-way, but only for blocks the RC directly changed.
2. **Content extremes.** Pages where the changed block has empty optional fields, a missing image, one item, the most items on any RC site, the longest title, or a long URL in a teaser (yalesites-org/YaleSites-Internal#1729). Find them with `SELECT`s, not by browsing.
3. **Date boundaries** for anything that shows dates or events. Month ends, multi-day events, all-day events, recurring events, and the current month's last day (yalesites-org/YaleSites-Internal#1374, yalesites-org/YaleSites-Internal#1379).
4. **Reusable vs. inline.** The same block type in existing placements of both kinds, found with a `SELECT` (never create one, and never submit a reusable block's form; see `rc-sites.md`) (yalesites-org/YaleSites-Internal#1381).
5. **Neighbors.** The changed block directly above and below each other block type it appears next to on real pages, and nested in tabs or accordions where that is possible.
6. **WebKit.** Changed surfaces in WebKit (Safari's engine), using "Safari" in `drive-it.md` (yalesites-org/YaleSites-Internal#1730). In `--drain`, only if WebKit is already installed.
7. **Another site.** A `clean` hypothesis, re-run on an RC site it has not been run on. This is the lowest priority: it never mattered in the hotfix lookback.

A generated charter gets a hypothesis entry of kind `generated` and goes through the same rules: concrete oracle, baseline, re-run, debrief.
