# YaleSites Views Reference

Views is the most complex and powerful feature on the YaleSites platform. It dynamically queries and displays CMS content — posts, events, people, etc. — based on filters, sorts, and display configurations you set up. Understanding Views is essential for building dynamic content listings like news feeds, event calendars, staff directories, and resource libraries.

---

## How Views Works on YaleSites

**Critical difference from standard Drupal:** On YaleSites, neither editors nor Site Administrators have access to the "Structure → Views" admin screen. "Structure" is a user0 (platform super-admin) only item and does not appear in the custom YaleSites top toolbar at all. All Views configuration for regular users happens **within the Layout Builder block form**.

The workflow is:
1. Go to the page in Layout Builder ("Edit Layout and Content")
2. Click "+" to add a block
3. Find and select the Views block you want (from `ys_views_basic` or `ys_views_content_resources`)
4. Configure filters, sorting, display options, and exposed filters directly in the block configuration panel that appears
5. Save the block and the layout

This means Views is more accessible than in standard Drupal — editors configure it through a guided block form rather than the full Views admin UI. The tradeoff is that the options available are those surfaced by the YaleSites platform team through that form.

---

## What Views Is

Views is a core Drupal module that lets you build database queries through a UI and display the results as blocks or feeds. Think of it as a configurable content query builder with templated output.

**What you configure:**
- **What content to show** (content type, taxonomy terms, date range, author, etc.)
- **How to sort it** (newest first, alphabetically, by event date, etc.)
- **How to display it** (card grid, list, table, teaser)
- **Whether users can filter it** (exposed filters like a search box or dropdown)

---

## The Two Views Modules

YaleSites ships two custom Views modules. Each surfaces a custom block form in the Layout Builder — editors configure the View by filling out this form, not through a traditional Drupal Views admin.

---

### `ys_views_basic` — What Users See in the Block Form

This block lets users select a content type, display format, sort order, item limit, and optional filters. Here are the exact labels and options as they appear:

**Step 1 — Select Content Type:**

| Label shown | What it displays |
|---|---|
| **Posts** | Post content type nodes |
| **Events** | Event content type nodes |
| **Pages** | Page content type nodes |
| **Profiles** | Profile content type nodes |

**Step 2 — Select Display Format** (options change per content type):

| Content Type | Available Display Options |
|---|---|
| Posts | Post Card Grid, Post List, Condensed |
| Events | Event Card Grid, Event List, Condensed |
| Pages | Page Grid, Page List, Condensed |
| Profiles | Profile Grid, Profile List, Directory Grid, Condensed |

**Sort options** (also content-type specific):

| Content Type | Sort Options |
|---|---|
| Posts | Publish Date - newer first / Publish Date - older first |
| Events | Event Date - newer first / Event Date - older first |
| Pages | Title - A-Z / Title - Z-A |
| Profiles | Last Name - A-Z / Last Name - Z-A |

**Display quantity:**
- Specific number of items (default: 10)
- All items (no limit)
- Paged (with pagination controls)

**Field display options** (checkboxes to show/hide per card):
- Show Thumbnail (on by default)
- Show Categories
- Show Tags
- *Events only:* Hide "Add to Calendar"
- *Posts only:* Show Eyebrow

**Exposed filter options** (make filters visible to site visitors):
- Category filter (for Posts, Events, Pages) — or **Affiliation** filter for Profiles
- Audience filter
- Custom Vocabulary filter
- Search (full-text)
- Year filter (Posts only)

**Other options:**
- Include/exclude specific taxonomy terms
- Offset (skip first N results)
- Pin sticky content to top (with configurable "Pinned" badge label)
- Include or exclude the current page's node from results

---

### `ys_views_content_resources` — Resources Listings

This module is dedicated to **Resources** content type listings. It has its own block form with:

**Display formats:** Card Grid, Portrait Grid, List, Condensed

**Sort options:** Published Date - newer first / Published Date - older first

**Exposed filter options:**
- Category filter
- Custom Vocabulary filter
- Audience filter
- Search (full-text)
- Year filter

**Field display options:**
- Show Thumbnail (on by default)
- Show Category

---

## Anatomy of a View

Every View has these key parts:

### Display
A View can have multiple displays — each is a separate output:
- **Page display:** Creates its own URL (e.g., `/news`)
- **Block display:** Can be placed in Layout Builder as a block
- **Attachment display:** Attaches to another display (e.g., a filter panel attaches to a list)

Each display can have different settings for format, fields, filters, and sort.

### Format (View Style)
How results are rendered:
- **Unformatted list** — raw output, styled by Twig templates
- **Grid** — card grid layout
- **Table** — tabular data
- **HTML list** — `<ul>/<ol>` list

On YaleSites, the display format connects to the component library's card and collection templates.

### Fields vs. Content
- **Fields** mode shows specific fields from each node (title, date, image)
- **Content** (rendered entity) mode renders the full node teaser or view mode

For card-style listings, YaleSites typically uses rendered content (the node's "card" view mode).

### Filters
Criteria that restrict which content appears. Two types:
- **Administrative filters** — hidden from users, always applied (e.g., "content type = Post", "status = published")
- **Exposed filters** — turned into a UI element that site visitors can interact with (dropdowns, search boxes, checkboxes)

Common administrative filter patterns:
```
Content type = Post (or Event, or Profile)
Published = Yes
```

Common exposed filter patterns:
```
Taxonomy term (Category, Tags, Audience) = user-selectable dropdown
Date (for Events) = date range picker
Full-text search = search box
```

### Sort Criteria
Determines the order results appear:
- Post date (descending) — newest first
- Title (ascending) — A to Z
- Event start date (ascending) — upcoming first
- Sticky/Featured (descending) — pinned content first, then by date

Multiple sort criteria can be stacked — e.g., "sticky first, then newest."

### Pager
Controls how many results show and whether there's pagination:
- **Display a specified number of items** — show exactly N (no pagination)
- **Paged output** — standard pagination (Next/Prev links)
- **Infinite scroll / Load more** — if configured via module
- **Mini pager** — compact page number display

---

## Common Views Patterns on YaleSites

### Recent News Block

**Used for:** Homepage news teaser, department news sidebar

**In the Layout Builder block form:**
- Content type: **Posts**
- Display: **Post Card Grid** (or Post List for a sidebar)
- Sort: **Publish Date - newer first**
- Number of items: 3 or 6

### Upcoming Events Listing

**Used for:** Events page, homepage events section

**In the Layout Builder block form:**
- Content type: **Events**
- Display: **Event Card Grid** or **Event List**
- Sort: **Event Date - older first** (soonest upcoming events appear first)
- Optionally enable the Category filter for user-facing filtering

**Note:** The `ys_localist` module can sync external Localist events into Drupal Event nodes, which then appear in the Events View automatically.

### Staff / Profiles Directory

**Used for:** People, faculty, and staff listing pages

**In the Layout Builder block form:**
- Content type: **Profiles**
- Display: **Profile Grid**, **Profile List**, or **Directory Grid** (Directory Grid is specifically designed for people listings with headshots)
- Sort: **Last Name - A-Z**
- Optionally enable the **Affiliation** filter (not "Category" — for Profiles, the filter is called Affiliation and uses the `affiliation` taxonomy vocabulary)

### Resource Library

**Used for:** Publications, reports, tools — any tagged document library

**Use `ys_views_content_resources`:**
- Content type is always **Resources** (this module only handles Resources)
- Display: **Card Grid**, **Portrait Grid**, **List**, or **Condensed**
- Sort: **Published Date - newer first**
- Optionally enable Category, Audience, Custom Vocabulary, Search, and/or Year filters

---

## Taxonomy and Views

Taxonomy is the primary way to filter Views. The relationship is:
1. Create vocabulary (e.g., "Category") via the taxonomy manager — accessible through the top toolbar (not via "Structure → Taxonomy," which is a user0-only path unavailable to regular YaleSites users)
2. Add a taxonomy field to your content type (e.g., "Category" field on Post)
3. Tag your content with terms
4. In Views, add a filter for that taxonomy field
5. Optionally expose it so users can filter by category

**Best practice:** Plan your taxonomy vocabulary structure before building Views. Changing taxonomy structures mid-site is disruptive to existing Views filters and any hardcoded term IDs.

---

## Exposed Filters

Exposed filters turn View filters into user-facing controls. In YaleSites:

- **Dropdown select** — most common for taxonomy; user picks one term
- **Checkboxes** — allows multi-select (good for "show me posts tagged X or Y")
- **Text search** — full-text search of specified fields
- **Date picker** — for Events, filter by a date range

**Exposed filter form placement:** By default, Drupal renders exposed filters above the results. On YaleSites, the placement is templated — typically above the content grid. The form submits with a page reload (standard Drupal) unless AJAX is enabled.

**AJAX mode:** When enabled, filters update results without a full page reload. This improves UX but adds complexity. Confirm whether `ys_views_basic` or `ys_views_content_resources` has AJAX enabled for the specific display before advising on behavior.

---

## Views and Layout Builder Integration

A Views block display can be placed in the Layout Builder like any other block:

1. In Layout Builder, click "+"
2. Search for the View name
3. Select the block display
4. Optionally configure per-instance overrides (some Views expose override options)

**Important limitation:** Views blocks placed in Layout Builder cannot have their filters configured per-placement. The filter configuration is global to that View/display. If you need a "Posts tagged with Category A" block and a "Posts tagged with Category B" block, you need either two separate Views displays, or a contextual filter (see below).

---

## Contextual Filters

Contextual filters (called "arguments" in older Drupal) allow a View to pull its filter value from context — the URL, the current node's field values, or a relationship — rather than a hardcoded value.

**Example:** A "Related Posts" block that automatically shows posts sharing the same category as the current page:
- Contextual filter: Taxonomy term ID from the current node's Category field
- This single View display can serve every page without per-page configuration

Contextual filters are advanced Drupal configuration and typically require a developer or experienced site builder.

---

## Relationships

Relationships in Views allow you to join data from related entities. For example:
- Show a Profile node's name alongside the Department taxonomy term it belongs to
- Show an Event node with its Location reference's address field

Adding relationships increases query complexity. Use sparingly on large datasets.

---

## Performance Considerations

Views can be slow if misconfigured on large datasets:

- **Avoid exposed full-text search on large databases** — use a dedicated search module instead
- **Cache Views output** where possible (Drupal's render cache + Views result cache)
- **Limit the number of exposed filters** — each adds a query condition
- **Use indexed taxonomy fields** — Drupal automatically indexes these for efficient filtering
- **Pager instead of "all items"** — never display an unlimited number of results

---

## Common Editor Mistakes with Views

1. **Expecting a Views block to auto-update when content is added:** It will, but cached pages may not reflect changes immediately. Clear caches or check cache max-age settings.

2. **Confusing Views blocks with Drupal Views pages:** On YaleSites, editors work exclusively with Views *blocks* placed in the Layout Builder. Standard Drupal Views pages (which have their own URL and are managed at "Structure → Views") are not an editor-facing concept — that admin screen is user0-only and not visible in the custom YaleSites toolbar.

3. **Setting a "Show all items" pager on a large content set:** This can result in hundreds of cards rendered at once, killing page performance. Set a reasonable pager limit.

4. **Using the wrong display for a Layout Builder placement:** Only Block displays can be placed in Layout Builder. Page displays cannot.

5. **Not setting the Published filter:** Without it, unpublished drafts will appear in the listing. Always add `Published = Yes` as an administrative filter.

---

## Views Configuration Path on YaleSites

All Views configuration for site editors and administrators happens in the Layout Builder:

1. Navigate to a page and click "Edit Layout and Content" in the second toolbar
2. Click "+" to add a block
3. Search for and select the Views block (from `ys_views_basic` or `ys_views_content_resources`)
4. Configure the View's options in the block configuration panel
5. Save the block and the layout

**Platform administrators** (Drupal super-admins, not typical site admins) do have access to the standard Views admin at Structure → Views for platform-level maintenance. But this is not the configuration path for editors or typical site builders on YaleSites.
