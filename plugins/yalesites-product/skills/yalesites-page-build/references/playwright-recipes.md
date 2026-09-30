# Playwright recipes for yalesites.yale.edu

Each recipe below is the body of an `async page => { ... }` function for `"$RUN/pw" run-code`. Never type a recipe inline in a double-quoted shell string. The recipes use backticks, `${nid}` template literals, and `[name="..."]` selectors, and the shell would run the backticks, blank out `${nid}`, and end the string at the first inner `"`.

Instead, keep the values in a JSON file and the body in a file written with a quoted heredoc, then assemble them. `run-code` has no `require`, so this is also how HTML gets in:

```bash
python3 -c 'import json; json.dump({"nid": 559, "HTML": open("block.html").read().strip()}, open("'"$RUN"'/vars.json", "w"))'
cat > "$RUN/step.js" <<'JS'
// recipe body goes here, unchanged
JS
code() { python3 -c 'import json,sys; v=json.load(open(sys.argv[1])); print("async page => {\n" + "".join("const %s = %s;\n" % (k, json.dumps(x)) for k, x in v.items()) + open(sys.argv[2]).read() + "}")' "$1" "$2"; }
"$RUN/pw" run-code "$(code "$RUN/vars.json" "$RUN/step.js")"
```

Every name a recipe uses in capitals or as `nid` / `uuid` (`HTML`, `WEIGHTS`, `FIELD`, `OLD`, `NEW`) goes in `vars.json`. The shell does not re-expand the output of `$(...)`, so nothing in the body or the values is touched.

Things learned the hard way:

- Prefer `page.locator('[name="..."]')` and `getByRole` over snapshot refs. Drupal form rebuilds invalidate refs.
- After a submit, wait with `page.waitForURL(u => String(u).includes('/node/<nid>/layout'))`. A plain click with no wait can return before the save, or never submit at all.
- A `waitForURL` timeout does not always mean failure. The Move form redirected somewhere unexpected but still saved. Re-read the layout before retrying anything.

## Set a CKEditor 5 field

```js
await page.waitForSelector('.ck-editor__editable');
await page.evaluate(h => document.querySelector('.ck-editor__editable').ckeditorInstance.setData(h), HTML);
```

When a form has more than one editor (Quote Callout has two), find the editor next to its textarea:

```js
await page.evaluate(([name, html]) => {
  const ta = document.querySelector(`[name="${name}"]`);
  const ed = (ta.closest('.form-item') || ta.parentElement.parentElement).querySelector('.ck-editor__editable');
  ed.ckeditorInstance.setData(html);
}, ['settings[block_form][field_caption][0][value]', HTML]);
```

The Text block editor keeps `<h2>`, `<table>` (it adds `class="table"`), lists, links, and `<strong>`. Test anything unusual with `setData` then `getData` before relying on it.

## Add an inline block

```js
await page.goto(`https://yalesites.yale.edu/layout_builder/add/block/overrides/node.${nid}/2/content/inline_block%3Atext`);
await page.waitForSelector('.ck-editor__editable');
await page.fill('[name="settings[label]"]', 'Short admin label');
await page.evaluate(h => document.querySelector('.ck-editor__editable').ckeditorInstance.setData(h), HTML);
if (await page.locator('[name=reusable]').isChecked()) await page.locator('[name=reusable]').uncheck();
await Promise.all([
  page.waitForURL(u => String(u).includes(`/node/${nid}/layout`), {timeout: 45000}),
  page.getByRole('button', {name: 'Add block', exact: true}).first().click(),
]);
```

Machine names seen in the picker: `text`, `accordion`, `divider`, `inline_message`, `pull_quote` (Quote), `quote_callout`, `tabs`, `wrapped_text_callout`, `callout`, `custom_cards`, `quick_links`, `link_grid`, `button_link`, `cta_banner` (Action Banner), `grand_hero`, `content_spotlight` (Spotlight - Landscape), `view`, `resource_view`, `post_list` (Post feed). The edit form uses **Update** instead of **Add block**.

## Block form fields

| Block | Fields (`settings[block_form][...]`) |
|---|---|
| Text | `field_text` (editor), `field_style_variation` (default / emphasized), `field_padding_options` (default **no_padding**) |
| Quote Callout | `field_text` (Quote), `field_caption` (Attribution), `field_style_alignment`, `field_style_variation` (bar / quote), `field_style_color` (one to six), `field_padding_options`, optional media |
| Divider | `field_style_position` (left), `field_style_width` (100%), `field_padding_options` (default) |
| View | `field_heading` (**View Heading**, use it instead of a separate Text heading), then the `group_user_selection` fields below |

Padding option values: `default`, `no_top`, `no_bottom`, `no_padding`.

## Configure a View block

The block saves from the form fields, not from the **Params** textarea. `ViewsBasicDefaultWidget::massageFormValues()` rebuilds Params on submit, so the textarea not updating in the browser is expected.

```js
const P = 'settings[block_form][group_user_selection]';
await page.fill('[name="settings[block_form][field_heading][0][value]"]', 'All spotlight stories');
await page.evaluate(P => {
  const pick = (n, vals) => { const s = document.querySelector(`[name="${n}"]`);
    [...s.options].forEach(o => o.selected = vals.includes(o.value));
    s.dispatchEvent(new Event('change', {bubbles: true})); };
  pick(P + '[filter_and_sort][terms_include][]', ['85']);   // Spotlight Site (Tags)
  pick(P + '[filter_and_sort][terms_exclude][]', ['21']);   // Release Notes (Tags)
  const d = document.querySelector(`[name="${P}[options][display]"]`); d.value = 'all';
}, P);
```

Look up term IDs from the include select's options (`"<id>=<name> (<vocabulary>)"`) rather than trusting the ones above. The defaults are Posts, Post Card Grid, Show Teaser Image on, and **Can have any term**. After saving, read the card headings in `.ys-view` on the layout page and check the count against what you expected.

## Move a block

The Move form has a weight select for every block in the region. Set the new block's weight, then bump everything that should come after it:

```js
await page.goto(`https://yalesites.yale.edu/layout_builder/move/block/overrides/node.${nid}/2/content/${uuid}`);
await page.evaluate(w => { for (const [u, v] of Object.entries(w)) {
  const s = document.querySelector(`[name="components[${u}][weight]"]`); s.value = v;
  s.dispatchEvent(new Event('change', {bubbles: true})); } }, WEIGHTS);
await Promise.all([
  page.waitForNavigation({timeout: 45000}),
  page.getByRole('button', {name: 'Move', exact: true}).first().click(),
]);
```

Wait for the navigation before anything else. A reload right after the click can cut off the submit, so the move is lost or the order you read back is stale. Any destination counts, since Move does not always land back on the layout page. Then reload `/node/<nid>/layout` and print the block order to confirm.

## Edit existing blocks by exact replace

Set `FIELD` to the textarea name of the field you mean, for example `settings[block_form][field_text][0][value]`. Do not take the first editor on the form: Quote Callout has two.

```js
const result = await page.evaluate(([name, OLD, NEW]) => {
  const ta = document.querySelector(`[name="${name}"]`);
  const ed = (ta.closest('.form-item') || ta.parentElement.parentElement).querySelector('.ck-editor__editable').ckeditorInstance;
  const before = ed.getData();
  const count = before.split(OLD).length - 1;
  if (count !== 1) return `NO CHANGE: found ${count} matches, expected exactly 1`;
  ed.setData(before.replace(OLD, () => NEW));
  return 'REPLACED';
}, [FIELD, OLD, NEW]);
if (result !== 'REPLACED') return result;
```

It refuses anything but exactly one match, so a phrase that appears twice is never half-updated. Widen `OLD` until it is unique, or run it once per match. The replacer function keeps `$&`, `$$`, and similar patterns in `NEW` from being rewritten.

Existing content carries `data-list-item-id` attributes and `&nbsp;` entities. Match against `getData()` output, not the rendered text.

## Save the layout as Draft

```js
await page.locator('[name="moderation_state[0][state]"]').selectOption('draft');
await Promise.all([page.waitForNavigation({timeout: 60000}), page.click('#edit-submit')]);
```

## Read Editoria11y results

```js
await page.goto(`https://yalesites.yale.edu/node/${nid}/latest`);
await page.waitForTimeout(2500);
return await page.evaluate(() => [...document.querySelectorAll('ed11y-element-result')]
  .map(r => ({test: r.result.test, el: r.result.element.outerHTML.slice(0, 120)})));
```

Compare each element against the blocks you touched to tell new alerts from old ones.
