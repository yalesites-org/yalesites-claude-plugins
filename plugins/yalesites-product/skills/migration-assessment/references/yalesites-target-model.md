# The YaleSites target model, for migration purposes

What a migration can land on. This file holds only what a **migration** needs
and the platform knowledge base does not: the machine names and hard limits that
decide whether source content can move at all.

**It is not a second copy of the content model.** The `yalesites` plugin owns
that, and those files are kept current by the release process (`release-prep`
Phase 6). Load them for anything field-level:

| For | Read |
|---|---|
| Every field on every content type, with required flags | `content-types-reference.md` |
| Every block/component and its fields | `blocks-reference.md` |
| Paragraph types nested inside components | `paragraphs-reference.md` |
| Views, display modes | `views-reference.md` |
| Sitewide settings | `settings-reference.md` |
| Roles and permissions | `user-roles-reference.md` |

Everything below is verified against
`web/profiles/custom/yalesites_profile/config/sync/` in
`yalesites-org/yalesites-project` (`develop`, September 2026). Machine names are
exact — copy them, do not paraphrase. Re-verify before quoting any of it in a
formal estimate; the authoritative source is always the profile's exported
config, not this file.

## The four constraints that decide a migration

1. **Five content types, fixed** — `page`, `post`, `event`, `profile`,
   `resource`. Every source type must fold into one of them. No role, not even
   `platform_admin`, holds `administer content types` or `administer node
   fields`, so new types and new fields are not something a project can buy.
2. **There is no body field.** Long-form content is Layout Builder components. A
   source `body` becomes one or more `text` components using `basic_html`, which
   strips `<div>`, `<iframe>`, `<script>`, `<style>`, `<form>`, and inline
   `<img>`. **Body HTML does not migrate as HTML.** This is the single most
   common surprise and the largest cost driver on a page-heavy site.
3. **Layout freedom is a per-region allow-list** for `page`, `post`,
   `profile` and `resource` — not a component catalogue. `event` is the one
   exception (a denylist); see below.
4. **Access is binary** — public, or CAS-gated via `field_login_required`;
   there is nothing per-role or per-group. See the hard-walls table for the
   config evidence and the security caveat.

## Which target type absorbs which source type

The source-type vocabulary lives in
`scripts/probe_site.py::SOURCE_TYPE_MAP` — one place, with a regression test
next to it. Add source-type spellings there, not here. It buckets to:

| Bucket | YaleSites content type | Migration notes |
|---|---|---|
| `page` | `page` | The default destination. Also the only book/collection-enabled type. |
| `post` | `post` | Requires `field_publish_date`. No bulk importer exists (YaleSites-Internal#1230). |
| `event` | `event` | Decide native nodes vs the Localist integration **first** — it changes the whole migration. No bulk importer (YaleSites-Internal#1231). |
| `profile` | `profile` | The one type with a shipped CSV importer, so directories are the cheapest bucket. **No biography field** — every bio is a Layout Builder rebuild. |
| `resource` | `resource` | Scholarly/document metadata. A CSV importer shipped. |
| `listing` | none — a view, not a node | Becomes a placed view component. Custom sort/filter combinations may not be reproducible. |
| `unmapped` | needs a decision | No equivalent identified. Fold into `page`, model with taxonomy, or drop — but say so explicitly. |

Two traps to state in any mapping:

- **`profile` has no biography field** (above).
- **`event`'s `field_localist_*` fields are integration-owned.** `ys_localist`
  writes them; never map source data into them.

## Components

36 components are placeable by editors. `blocks-reference.md` lists them all
with their fields; what matters for a migration is narrower:

**Where migrated prose can go** (the rich-text-bearing components): `text`,
`wrapped_text_callout`, `wrapped_image`, `inline_message`, `content_spotlight`
and `_portrait`, `cta_banner`, `grand_hero`, `facts`, `pull_quote`,
`quote_callout`, `quick_links`, `image_banner` (caption), `video` (description).

**Paragraph types are internal.** The 11 of them (`accordion_item`,
`callout_item`, `cta_link`, `custom_card`, `facts_item`, `gallery_item`,
`link_list`, `media_grid_item`, `tab`, `text`, `tile`) are reachable only nested
inside a component, never placed directly.

**Styling is dials, not CSS.** 27 components expose a fixed option set via
`field_style_color`, `field_style_variation`, `field_style_position`,
`field_style_width`, `field_style_alignment`, defined in
`ys_themes.component_overrides.yml`. There is no per-component custom styling,
so a source site's bespoke look does not come across.

## Layouts and region allow-lists

| Layout id | Label |
|---|---|
| `layout_onecol` | One column (core) |
| `ys_layout_banner` | Banner |
| `ys_layout_page_meta` | Page Meta |
| `ys_layout_two_column` | Two column (70/30) |
| `ys_layout_two_column_50_50` | Two column (50/50) |
| `ys_layout_three_column_33_33_33` | Three column (33/33/33) |

Allowed per content type: `page` and `resource` get all of one-column, 70/30,
50/50 and three-column; `post` gets one-column and 50/50; `profile` gets
one-column and 70/30.

**`event` is the exception, and it goes the other way.**
`core.entity_view_display.node.event.default.yml` sets `allowed_layouts: {}`
(no layout restriction at all) and uses a **denylist** rather than a per-region
allow-list: the only component denied is `wrapped_text_callout`. So an event
page is the *least* constrained of the five for component placement — but its
title/metadata section carries all eight locks and its content section cannot
take sections before or after, so the section *structure* is fixed. Do not apply
the allow-list table below to `event`.

**Six layout plugins, four an editor can choose.** `ys_layout_banner` and
`ys_layout_page_meta` are structural — they appear only in locked default
sections and never in a layout picker, which is why the `yalesites` knowledge
base counts four. Both framings are correct; a migration cares about all six,
because banner components can only ever live in the banner section.

### The rule that matters most: one-column is the only open region

`layout_onecol` is the only layout with **no** component allow-list — every
multi-column layout enumerates exactly which components its regions accept, and
those lists are much shorter than the palette. So the mapping question is never
"does the platform have this component" but "does the region I want it in accept
it." Exact lists for `node.page.default`
(`entity_view_mode_restriction_by_region.allowlisted_blocks`):

| Layout / region | Components accepted |
|---|---|
| `layout_onecol` / all | **unrestricted** (any of the 36, subject only to the restricted categories below) |
| `ys_layout_banner` / all | `cta_banner`, `grand_hero`, `image_banner`, `content_spotlight`, `content_spotlight_portrait`, `video_banner` — **and nothing else** |
| `ys_layout_two_column` (70/30) / content | `accordion`, `button_link`, `directory`, `divider`, `embed`, `event_list`, `gallery`, `image`, `link_grid`, `media_grid`, `post_list`, `pull_quote`, `reference_card`, `tabs`, `text`, `video`, `wrapped_text_callout` (17) |
| `ys_layout_two_column` (70/30) / sidebar | `button_link`, `divider`, `image`, `link_grid`, `pull_quote`, `text`, `video`, `webform` (8) |
| `ys_layout_two_column_50_50` / all | `accordion`, `button_link`, `divider`, `embed`, `image`, `link_grid`, `pull_quote`, `tabs`, `text`, `video`, `webform` (11) |
| `ys_layout_three_column_33_33_33` / all | `button_link`, `divider`, `embed`, `image`, `link_grid`, `pull_quote`, `text`, `video` (8) |
| `ys_layout_page_meta` / all | `page_meta_block` only |

Consequences worth checking before promising a layout:

- **Banner components are banner-only.** They cannot go in a content section.
- **`callout`, `quick_links`, `tiles`, `custom_cards`, `facts`, `inline_message`,
  `quote_callout`, `wrapped_image`, `audio`, `view`, `event_calendar`,
  `resource_view` appear in no multi-column allow-list** — they are placeable
  only in a one-column section.
- **An events or post listing cannot go in the 70/30 sidebar** — `event_list`
  and `post_list` are in that layout's content region but not its sidebar.
- **`webform` is sidebar-and-50/50 only**, plus one-column.
- **Raw Views blocks and raw Webform blocks are never placeable.** The `Lists
  (Views)` and `Webform` block categories are restricted on every display.
  Listings must go through the `view` / `post_list` / `event_list` / `directory`
  / `resource_view` / `event_calendar` components.
- **Metadata sections are fully locked.** On `post`, `event` and `resource` the
  title/metadata section carries all eight `layout_builder_lock` locks, and
  post/event content sections cannot take sections before or after — so a post
  or event page's section structure is fixed.

The generic `view` component's scope is hard-coded in
`ys_views_basic/src/ViewsBasicManager.php::ALLOWED_ENTITIES` and covers `post`,
`event`, `page`, `profile` — **not `resource`**, which needs `resource_view`.

## Media

| Type | Source | Accepts |
|---|---|---|
| `image` | image | `png jpg jpeg webp` — **no GIF, no SVG** |
| `document` | file | `txt rtf doc docx pdf xls xlsx ppt pptx ics` |
| `audio` | audio_file | `mp3 wav aac` |
| `background_video` | video_file | `mp4` only, decorative hero use |
| `video` | oEmbed | **YouTube and Vimeo only** |
| `embed` | `ys_embed` | a regex-validated allow-list, below |

Six media types (`media.type.*.yml`), and no role can create a seventh. Note the
`yalesites` knowledge base says five — it omits `audio`, which does exist in
config.

**Embeds are an allow-list, not a paste box.** `EmbedSourceBase::isValid()`
regex-matches against a registered source. The 13 sources: `bluesky`,
`github_applet`, `google_calendar`, `google_maps`, `instagram`, `jwplayer`,
`localist`, `msforms`, `powerbi`, `qualtrics`, `soundcloud`,
`twenty_five_live_form`, `twitter`. Anything else is rejected.

**Gallery is a grid with a lightbox, not a carousel.** There is no carousel,
slider, or slideshow component anywhere in the platform, and no such library in
`atomic` or `component-library-twig`.

## Taxonomy

21 vocabularies. The five that matter to most migrations: `tags` (shared,
auto-creates terms), `audience`, `custom_vocab`, the per-type `*_category`
vocabularies (`page_category`, `post_category`, `event_category`,
`resource_category`), and `affiliation` for profiles. Resource adds
`academic_years`, `areas_of_study`, `discipline`, `geographic_areas`. The
Localist-owned event vocabularies (`localist_event_type`, `event_groups`,
`event_place`) are integration-managed and not editor-editable.

## What YaleSites deliberately does not do

Each of these is a hard wall, not a configuration choice.

| Not supported | Evidence |
|---|---|
| **Custom form building** | Webform is installed but no role holds `create webform` or `administer webform`; exactly one form ships (`webform.webform.contact.yml`); the block type is labelled "Pre-Built Form — Not intended for custom form creation." External forms go through the `msforms` / `qualtrics` / `twenty_five_live_form` embeds. |
| **Arbitrary HTML / CSS / JS** | No `full_html` format exists. `basic_html` permits no `<script>`, `<style>`, `<iframe>`, `<div>`, `<img>`, `<form>`, or `on*` attributes. No role holds `administer filters`. No custom-CSS or custom-JS field or block exists. CKEditor's `sourceEditing` is on but bounded by the same allow-list. |
| **Inline images in the editor** | `image_upload: {status: false}` on every editor. Images go through Media plus the Image / Wrapped Image / Gallery components. |
| **One-off custom layouts** | Six layouts, full stop. No role holds `configure any layout`; editors get only `configure editable <type> node layout overrides`, and `layout_builder_lock` fixes the rest. |
| **Public user accounts / gated content beyond CAS** | `register: admin_only`; anonymous holds three permissions; gating is the binary `field_login_required` via CAS. |
| **Multilingual content** | `language`, `content_translation`, `locale` and `config_translation` are all absent from `core.extension.yml`. **A source site with translations has no target.** |
| **Comments, forums, core contact forms, feed aggregation** | `comment`, `forum`, `contact`, `aggregator` all absent. |
| **Arbitrary menus** | Seven fixed menus; editors administer items in `main` and the two utility menus but hold no `administer menu`, so no new menus. The drop-button utility menu is capped at 10 items. |
| **Editors changing the content model** | No role holds `administer views`, `administer node fields`, `administer node display`, `administer media types`, `administer paragraphs types`, `administer themes`, or `administer permissions`. |

## Integrations a source system might map onto

| Plugin id | Label | Use in a migration |
|---|---|---|
| `ys_localist` | Localist | The answer for a live events feed. Often better than migrating event nodes. |
| `ys_campus_groups` | Campus Groups | Campus Groups event/organisation data; ships its own migrations. |
| `ys_ai` / `ys_beacon` | AI / Beacon | Site search and chat, not content migration. |

Plus CAS (`drupal/cas` + `yale_cas`) as the only authentication path, `google_tag`
/ `google_analytics` for analytics, and `search_api` with a public and a
CAS-only index.

**ServiceNow has no integration plugin** — `ys_servicenow` was removed
(yalesites-project issue #1372). A source site's ServiceNow forms stay as
outbound links or an embed.

## Migration tooling already in the profile

Relevant because it constrains the mechanism options: `migrate_plus` 6.0.8,
`migrate_tools` 6.1.4, `migrate_conditions`, `migrate_file_to_media`,
`single_content_sync`, plus `ys_migrate` (with per-site submodules
`ys_migrate_onha`, `ys_migrate_sustainability_news`, `ys_migrate_whc`) and
`ys_content_export`. `ys_migrate_onha` includes a `BodyToLayoutBuilder` process
plugin — precedent that migrating body HTML into Layout Builder components is
possible and has been done, per-site and with custom code.
