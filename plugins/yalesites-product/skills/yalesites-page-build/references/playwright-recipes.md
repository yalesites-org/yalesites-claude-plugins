# Playwright recipes for yalesites.yale.edu

Every recipe runs as `"$RUN/pw" run-code "async page => { ... }"`. Things learned the hard way:

- `run-code` has no `require`. To pass HTML in, JSON-encode it in the shell and paste it into the script: `H=$(python3 -c 'import json;print(json.dumps(open("block.html").read().strip()))')`, then use `$H` inside the double-quoted script.
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
await page.getByRole('button', {name: 'Move', exact: true}).first().click();
```

Then reload `/node/<nid>/layout` and print the block order to confirm.

## Edit existing blocks by exact replace

```js
const before = await page.evaluate(() => document.querySelector('.ck-editor__editable').ckeditorInstance.getData());
const after = before.replace(OLD, NEW);
if (after === before) return 'NO CHANGE: pattern not found';
```

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
