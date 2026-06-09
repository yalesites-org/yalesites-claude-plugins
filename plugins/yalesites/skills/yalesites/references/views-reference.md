# YaleSites Views Reference

Views is the most complex and powerful feature on the YaleSites platform. It dynamically queries and displays CMS content — posts, events, people, etc. — based on filters, sorts, and display configurations you set up. Understanding Views is essential for building dynamic content listings like news feeds, event calendars, staff directories, and resource libraries.

---

## What Views Is

Views is a core Drupal module that lets you build database queries through a UI and display the results as blocks, pages, or feeds. Think of it as a configurable content query builder with templated output.

**What you configure:**
- **What content to show** (content type, taxonomy terms, date range, author, etc.)
- **How to sort it** (newest first, alphabetically, by event date, etc.)
- **How to display it** (card grid, list, table, teaser)
- **Whether users can filter it** (exposed filters like a search box or dropdown)
- **Where it appears** (as a block in Layout Builder, or as a standalone page with its own URL)

---

## The Two Views Modules

YaleSites ships two custom Views modules:

### `ys_views_basic`

Simpler, out-of-the-box listings. Best for:
- Recent news/posts (e.g., "Latest 6 posts")
- Upcoming events
- Featured people listings
- Simple taxonomy-filtered content lists

Configuration is relatively accessible for site builders who understand basic Drupal concepts.

### `ys_views_content_resources`

More advanced content resource listings. Best for:
- Large resource libraries with user-facing filter panels
- Multi-type content listings (mixing Posts, Events, People)
- Complex exposed filter configurations (multiple selectable taxonomies + date ranges)
- Content that editors frequently filter/sort differently

This module typically requires more configuration effort and is better suited to sites with substantial structured content.

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
Content type = Post (or Event, or Person)
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

**Configuration:**
- Content type = Post
- Status = Published
- Sort: Post date (desc)
- Pager: Display 3 items (or 6 for a grid)
- Format: Card Grid
- Block display → place in Layout Builder

### Upcoming Events Listing

**Used for:** Events page, homepage events section

**Configuration:**
- Content type = Event
- Status = Published
- Filter: Event date ≥ current date (use "now" as the default value)
- Sort: Event start date (asc) — soonest first
- Exposed filter: optional date range or category
- Format: Card list or grid

**Note:** The `ys_localist` module can sync external Localist events into Drupal nodes, which then appear in standard Views like any other Event node.

### Staff Directory

**Used for:** People/faculty listing pages

**Configuration:**
- Content type = Person
- Sort: Last name (asc) or a custom weight field
- Exposed filters: Department (taxonomy), Role/Title
- Format: Grid (headshot + name + title) or List

### Resource Library

**Used for:** Publications, reports, tools — any tagged document library

**Configuration:** (`ys_views_content_resources` recommended)
- Content type = Post (or a custom type)
- Exposed filters: Category, Tags, Year
- Sort: Date (desc), with user-selectable sort
- Format: Condensed list or card grid
- Full-text search exposed filter optional

---

## Taxonomy and Views

Taxonomy is the primary way to filter Views. The relationship is:
1. Create vocabulary (e.g., "Category") in Structure → Taxonomy
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
- Show a Person node's name alongside the Department taxonomy term it belongs to
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

2. **Confusing Views pages with Drupal pages/nodes:** A Views page has its own URL but is not a node. It won't appear in the Content admin list. Manage it at Structure → Views.

3. **Setting a "Show all items" pager on a large content set:** This can result in hundreds of cards rendered at once, killing page performance. Set a reasonable pager limit.

4. **Using the wrong display for a Layout Builder placement:** Only Block displays can be placed in Layout Builder. Page displays cannot.

5. **Not setting the Published filter:** Without it, unpublished drafts will appear in the listing. Always add `Published = Yes` as an administrative filter.

---

## Views Configuration Path

To access and configure Views: **Administration → Structure → Views**

To edit a specific View:
1. Find it in the Views list
2. Click Edit
3. Select the display (Page, Block, etc.) from the left panel
4. Edit Format, Fields, Filter Criteria, Sort Criteria, Pager in the central configuration area
5. Click Save to apply

To add a new View: **Structure → Views → Add view**

The "Add view" wizard prompts for:
- View name (machine name auto-generated)
- Show: Content (or other entity types)
- Of type: (content type)
- Tagged with: (taxonomy filter, optional)
- Sorted by: (initial sort)
- Create a page / Create a block (initial display)
