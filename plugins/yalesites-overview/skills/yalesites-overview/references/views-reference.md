# YaleSites Views Reference

Views is the most complex and powerful feature on the YaleSites platform. It dynamically queries and displays CMS content based on filters, sorts, and display configurations. Understanding Views is essential for building dynamic content listings like news feeds, event calendars, staff directories, and resource libraries.

---

## How Views Works on YaleSites

**Critical difference from standard Drupal:** Site Administrators do not have access to the "Structure → Views" admin screen. All Views configuration happens **within the Layout Builder block form**.

The workflow is:
1. Go to the page in Layout Builder ("Edit Layout and Content")
2. Click "+" to add a block
3. Find and select the Views block you want
4. Configure filters, sorting, display options, and exposed filters directly in the block configuration panel
5. Save the block and the layout

---

## The Two Views Modules

### `ys_views_basic` — What Users See in the Block Form

**Step 1 — Select Content Type:**

| Label shown | What it displays |
|---|---|
| **Posts** | Post content type nodes |
| **Events** | Event content type nodes |
| **Pages** | Page content type nodes |
| **Profiles** | Person/profile content type nodes |

**Step 2 — Select Display Format:**

| Content Type | Available Display Options |
|---|---|
| Posts | Post Card Grid, Post List, Condensed |
| Events | Event Card Grid, Event List, Condensed |
| Pages | Page Grid, Page List, Condensed |
| Profiles | Profile Grid, Profile List, Directory Grid, Condensed |

**Sort options:**

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

**Field display options** (checkboxes):
- Show Thumbnail (on by default)
- Show Categories
- Show Tags
- *Events only:* Hide "Add to Calendar"
- *Posts only:* Show Eyebrow

**Exposed filter options** (make filters visible to site visitors):
- Category filter (or **Affiliation** filter for Profiles)
- Audience filter
- Custom Vocabulary filter
- Search (full-text)
- Year filter (Posts only)

**Other options:**
- Include/exclude specific taxonomy terms
- Offset (skip first N results)
- Pin sticky content to top
- Include or exclude the current page's node from results

---

### `ys_views_content_resources` — Resources Listings

**Display formats:** Card Grid, Portrait Grid, List, Condensed

**Sort options:** Published Date - newer first / Published Date - older first

**Exposed filter options:** Category, Custom Vocabulary, Audience, Search, Year

**Field display options:** Show Thumbnail, Show Category

---

## Common Views Patterns on YaleSites

### Recent News Block
- Content type: **Posts** | Display: **Post Card Grid** | Sort: **Publish Date - newer first** | Items: 3 or 6

### Upcoming Events Listing
- Content type: **Events** | Display: **Event Card Grid** or **Event List** | Sort: **Event Date - older first** (soonest events appear first)

### Staff / Profiles Directory
- Content type: **Profiles** | Display: **Profile Grid** or **Directory Grid** | Sort: **Last Name - A-Z** | Optionally enable the **Affiliation** filter

### Resource Library
- Use `ys_views_content_resources` | Display: **Card Grid**, **Portrait Grid**, **List**, or **Condensed** | Sort: **Published Date - newer first**

---

## Anatomy of a View

### Filters
Two types:
- **Administrative filters** — hidden from users, always applied (e.g., "content type = Post", "status = published")
- **Exposed filters** — turned into a UI element that site visitors can interact with

### Sort Criteria
Multiple sort criteria can be stacked — e.g., "sticky first, then newest."

### Pager
- **Display a specified number of items** — show exactly N (no pagination)
- **Paged output** — standard pagination (Next/Prev links)

---

## Block Picker Grouping

Views listing blocks are grouped by content type in the Layout Builder picker:
- Post Listings: Posts — Card Grid, Posts — List, Posts — Condensed
- Event Listings: Events — Card Grid, Events — List, Events — Condensed, Events — Calendar
- People Listings: People — Card Grid, People — List, People — Directory, People — Condensed
- Page Listings: Pages — Card Grid, Pages — List, Pages — Condensed

---

## Views Architecture (ys_views_basic)

- `ViewsBasicManager` — service class; contains `ALLOWED_ENTITIES` constant defining content types, view modes, and sort options
- `ViewsBasicDefaultWidget` — the main FieldWidget that renders the block configuration form in Layout Builder
- `EventCalendarDefaultWidget` — separate widget for the calendar display mode
- `ViewsBasicWidgetBase` — abstract base class containing shared form logic
- Internal Views scaffolds: `views_basic_scaffold` (post/page/profile) and `views_basic_scaffold_events` (events, requires aggregation for date handling)

---

## Taxonomy and Views

1. Create vocabulary in Structure → Taxonomy
2. Add a taxonomy field to your content type
3. Tag your content with terms
4. In Views, add a filter for that taxonomy field
5. Optionally expose it so users can filter

**Best practice:** Plan your taxonomy vocabulary structure before building Views. Changing taxonomy structures mid-site is disruptive to existing Views filters.

---

## Common Editor Mistakes with Views

1. **Expecting cached pages to update immediately** — clear caches or check cache max-age settings.
2. **Confusing Views pages with Drupal nodes** — a Views page has its own URL but is not a node; it won't appear in the Content admin list.
3. **Setting "Show all items" on a large content set** — this renders hundreds of cards at once and kills page performance. Set a reasonable pager limit.
4. **Not setting the Published filter** — without it, unpublished drafts appear in listings.

---

## Performance Considerations

- Avoid exposed full-text search on large databases
- Cache Views output where possible
- Limit the number of exposed filters
- Use pager instead of "all items" on large datasets
