---
name: yalesites
description: >
  Deep expertise on YaleSites — Yale University's custom Drupal 10 CMS platform. Use this skill for any question about building or managing a YaleSites website, including: adding or configuring blocks in the Layout Builder, choosing between page components, understanding Manage Settings vs Layout Builder, configuring sitewide settings (theme, menus, footer, analytics), working with Views, content types, taxonomy, user roles, accessibility requirements, integrations (Localist, ServiceNow, CAS), and platform eligibility. Also use when helping the Product Manager make platform decisions, evaluate feature requests, advise editors or site builders, or think through Drupal architecture choices for the platform.
---

# YaleSites Platform Skill

YaleSites is Yale University's managed Drupal 10 CMS, hosted on Pantheon as a custom upstream. It powers 300+ Yale department and unit websites for 1,200+ editors. The platform deliberately constrains design choices to enforce brand consistency — this is intentional, not a limitation to work around.

## How to use this skill

This skill gives you deep platform context. For most questions, the information in this SKILL.md is sufficient. For deep dives, load the relevant reference file:

| Topic | Reference File |
|---|---|
| All blocks + design options | `references/blocks-reference.md` |
| Block sub-items (accordion items, cards, tiles, etc.) | `references/paragraphs-reference.md` |
| Content type field labels (Page, Post, Event, Resource, Profile) | `references/content-types-reference.md` |
| Views (filters, displays, modules) | `references/views-reference.md` |
| Sitewide settings (Manage Settings page) | `references/settings-reference.md` |
| User roles and editorial workflow | `references/user-roles-reference.md` |

---

## Platform Architecture

**Multi-repo structure:**
- `yalesites-project` — Drupal 10 project (custom modules, config, Pantheon upstream)
- `atomic` — Drupal theme (connects Drupal to the component library)
- `component-library-twig` — Storybook component library (source of truth for design options)
- `tokens` — Figma design tokens (feeds the component library)

**Hosting:** Pantheon. Environment flow: Dev → Test → Live. Sites go live via a request workflow requiring OPAC (Office of Public Affairs and Communications) approval.

**Authentication:** Yale CAS (Central Authentication Service) via NetID. Editors log in by appending `/cas` to their site URL (e.g., `https://mysite.yale.edu/cas`).

---

## Admin Interface — The Two Surfaces

Understanding the split between these two surfaces prevents the most common editor confusion.

### Manage Settings (the "Edit" page, at `/edit`)
The **logistical/structural** surface. Accessed via the second toolbar → "Manage Settings." This page has two areas:
- **Main form area (left)** — content fields specific to the content type (title, body, metadata, etc.)
- **Right sidebar** — settings panels including menu placement, URL alias, publication status, and access restrictions. If the sidebar appears collapsed, use the small **settings gear icon** to reopen it.

**Key rule:** If it's about *what this page is called, where it lives, or whether it's published*, it's on Manage Settings.

### Layout Builder (the "Edit Layout and Content" page, at `/layout`)
The **visual composition** surface. Accessed via second toolbar → "Edit Layout and Content." This is where editors:
- Add, remove, and reorder blocks in the Banner area and Main content area
- Configure each block's visual design options (color, layout, etc.)
- Configure Views blocks — all Views configuration on YaleSites happens here in the block form, not in the Drupal admin toolbar

**Key rule:** If it's about *what's on the page visually and how it looks*, it's in the Layout Builder.

### Two Toolbars
1. **Top toolbar** (always visible): A **custom YaleSites toolbar** (provided by the `ys_toolbar` module) with site-wide tools for managing content, settings, users, and reports. **Important:** Standard Drupal admin items like "Structure," "Appearance," and "Modules" are **NOT visible** to regular YaleSites users — those items only appear for user0 (Drupal platform super-admins). A useful shortcut available to editors: Content → Manage Main Menu lets you manage navigation directly.
2. **Second toolbar** (content-specific, appears when viewing a node): Manage Settings | Edit Layout and Content | View | Revisions | Translate

---

## Content Types

YaleSites has five content types:

| Content Type | Purpose |
|---|---|
| **Page** | General content — department pages, about pages, standard site sections |
| **Post** | News/blog articles; appears in Views-powered listings |
| **Event** | Calendar events; feeds into Views; integrates with Localist |
| **Resource** | Documents, reports, publications, and reference materials |
| **Profile** | Faculty, staff, and people profiles |

There is no "Basic Page" or "Landing Page" content type. All pages use the **Page** content type.

---

## Layout Builder — Block Categories

Blocks live in two regions:

**Banner Area** — full-width, above the fold. Only one banner block at a time.
- Grand Hero, Action Banner, Image Banner, Video Banner

**Main Content Area** — below the banner. Multiple blocks stacked vertically.
- Text & Content: Accordion, Callout, Inline Message, Quote Callout, Tabs, Wrapped Image, Wrapped Callout
- Spotlights: Content Spotlight Portrait, Content Spotlight Landscape
- Media: Video, Embed, Gallery
- Navigation: Link Grid, Quick Links
- Collections: Custom Cards, Tiles, Facts & Figures
- Dynamic (Views-powered): Views blocks — configured directly in the Layout Builder block form

For the full list of each block's design options, read `references/blocks-reference.md`.

---

## Layout Builder — Section Layouts

Within the Main Content Area, editors can create **sections** with different column layouts. Each section is one of four layout types (defined in `ys_layouts`):

| Layout | Machine name | Regions |
|---|---|---|
| **Full width (1 column)** | `ys_layout_banner` | `content` |
| **Two column 70/30** | `ys_layout_two_column` | `content` (70%), `sidebar` (30%) |
| **Two column 50/50** | `ys_layout_two_column_50_50` | `content_primary`, `content_secondary` |
| **Three column 33/33/33** | `ys_layout_three_column_33_33_33` | `content_primary`, `content_secondary`, `content_tertiary` |

Section padding (top/bottom spacing) is configurable per section via the section settings gear. Options: Default, No top padding, No bottom padding, No padding (top and bottom). Adjacent sections can be visually connected by removing bottom padding on the first and top padding on the second.


---

## The Design System — Themes and Constraints

### Global Theme ("lever")
Set at the site level in Sitewide Settings. Controls the overall color palette for the site — which named colors are available and what they look like. Editors cannot override this per-page.

**Available Global Themes (as of current release):**
- **Old Blues** — Yale blue-centric palette
- **New Haven Greens** — green-focused palette
- **Shoreline Summer** — warm/summer tones
- **ONHA** — Office of New Haven Affairs palette
- **It's Your Yale** — Yale community-focused palette
- **AI** — palette for AI-related sites

**Coming in the next release (not yet in production):**
- **Whitney Humanities Center** — do not recommend or promise this to editors until it ships

The full color swatches per theme are viewable at: https://yalesites-org.github.io/component-library-twig/?path=/story/tokens-colors--color-global-themes

### Per-block color picker ("Theme" field)
Each block in the Layout Builder exposes a **"Theme"** field — a color swatch picker showing named colors with hex codes (e.g., "Blue Yale #00366b", "Gray 100 #f7f7f7", "Blue Light #61a8ff"). Editors select from these named swatches. The available colors depend on the site's Global Theme.

**Important language note:** Always refer to colors by their actual displayed names (e.g., "Blue Yale", "Gray 800"). Never reference internal values like "theme one" or "color slot 3" — editors don't see those.

**Critical constraint:** The platform is intentionally prescriptive. Design options are limited to what the component library exposes — editors cannot add custom CSS, override colors arbitrarily, or inject HTML. This is by design to maintain brand consistency across 300+ Yale sites.

### What editors CAN control (per block):
- Color accent (via the color swatch picker)
- Layout variants (e.g., image left/right, column count)
- Content/text fields
- Whether optional elements appear (images, links, badges, overlays)
- Font family (within 3 Yale-approved combinations — see Site Settings)

### What editors CANNOT control:
- Font size (set by design tokens)
- Custom colors outside the Yale-approved palette
- Arbitrary HTML injection into most blocks
- Moving blocks between Banner and Main Content regions

### Font Family Settings
In Site Settings, editors can choose from three Yale-approved font combinations:
- **YaleNew / Mallory** (default)
- **Mallory / Mallory**
- **YaleNew (old numbers variant) / Mallory** *(coming soon in next release)*

These are the only font options available. Font size is not customizable — it is set by the design token system.

---

## Views — How They Work on YaleSites

Views are configured **entirely within the Layout Builder**. Neither editors nor Site Administrators have access to the standard Drupal "Structure → Views" admin screen — "Structure" is a user0 (platform super-admin) only item and is not present in the custom YaleSites toolbar. The workflow is:

1. In the Layout Builder, click "+" to add a block
2. Search for and select the View block you want
3. Configure the View's content type, display format, sort, filters, and item count directly in the block form
4. Save the block

**The two View block modules:**
- **ys_views_basic** — for Posts, Events, Pages, and Profiles listings
- **ys_views_content_resources** — for Resources listings only

**Content type labels in the Views block form:** Posts, Events, Pages, Profiles (not "Person"), Resources. These are the exact labels users see — never refer to content types by their Drupal machine names (post, event, page, profile, resource) when helping users.

### Views Display Modes
Each content type supports specific display modes. These are editor-facing labels (not Drupal machine names):

| Content Type | Display Modes |
|---|---|
| **Posts** | Card Grid, List, Condensed |
| **Events** | Card Grid, List, Condensed, Calendar |
| **Pages** | Card Grid, List, Condensed |
| **Profiles** | Profile Grid, Profile List, Directory Grid, Condensed |
| **Resources** | (handled by `ys_views_content_resources`) |

The **Calendar** display mode for Events is a separate block content type (`event_calendar`). The **Directory Grid** display mode for Profiles is a grid/table format specific to profile directories.

**Block picker grouping** — Views listing blocks are grouped by content type in the Layout Builder picker:
- Post Listings → Posts — Card Grid, Posts — List, Posts — Condensed
- Event Listings → Events — Card Grid, Events — List, Events — Condensed, Events — Calendar
- Profile Listings → Profiles — Profile Grid, Profiles — Profile List, Profiles — Directory Grid, Profiles — Condensed
- Page Listings → Pages — Card Grid, Pages — List, Pages — Condensed

### Views Architecture (ys_views_basic)
Internally, `ys_views_basic` uses:
- `ViewsBasicManager` — service class that builds and executes views queries; contains `ALLOWED_ENTITIES` constant defining content types, view modes, and sort options
- `ViewsBasicDefaultWidget` — the main FieldWidget that renders the block configuration form in Layout Builder
- `EventCalendarDefaultWidget` — separate widget for the calendar display mode; extends `ViewsBasicWidgetBase`
- The two Drupal Views scaffolds used internally: `views_basic_scaffold` (for post/page/profile) and `views_basic_scaffold_events` (for events, which requires aggregation for date handling)

See `references/views-reference.md` for the complete list of display formats, sort options, and filter options with their exact labels.

---

## Common Misconceptions

**1. "I'll just edit the layout from the Manage Settings page."**
Wrong surface. Manage Settings (`/edit`) controls page metadata, content fields, menus, and publication status. The Layout Builder (`/layout`) controls blocks and visual design. Many editors spend 10 minutes on the wrong screen.

**2. "I need to add a block every time I want new content."**
Not always. For basic text content, the body/content fields in Manage Settings may be sufficient. Layout Builder is for structured/designed components.

**3. "Why can't I pick Yale Blue in the color picker?"**
The color options shown in the block's color picker are defined by the site's Global Theme — they are already Yale-approved colors. If the color the editor wants isn't shown, it means their site's theme doesn't include it as an option, and that is intentional.

**4. "Views is just a list block I can drop on the page."**
Views is the most complex feature on the platform. It dynamically queries content based on filters, sorts, and display configurations. On YaleSites, all Views configuration happens in the Layout Builder block form — there's no separate Views admin. See `references/views-reference.md`.

**5. "Any Yale department can just get a YaleSites site."**
Not quite. Sites require OPAC approval. Yale School of Medicine (YSM) has their own separate platform and is explicitly excluded. Student organizations have a separate pathway.

**6. "I can customize the design beyond what's in the block settings."**
No. The platform is intentionally locked down. Editors cannot add custom CSS or override design tokens. Site builders can request custom components through the product roadmap process.

**7. "The menu section isn't on the Manage Settings page."**
It is — but it's in the **right sidebar**, which can be accidentally collapsed. Tell the editor to look for the small gear/settings icon to reopen the sidebar. Menu settings live there, not in the main form area.

---

## Taxonomy

Taxonomy vocabularies are used for categorizing content and powering Views filters. Common vocabularies:
- **Tags** — general-purpose content tagging
- **Category** — structured classification
- **Audience** — who content is for

Taxonomy is managed via the `ys_taxonomy_manager` custom module.

---

## Menus

YaleSites supports multiple menu types:
- **Main Navigation** — primary site nav, appears in header
- **Footer Menu** — links in site footer
- **Utility Menu** — secondary header links

**To add a page to a menu:** Go to the page's Manage Settings → right sidebar → Menu settings → enable "Provide a menu link" → select the correct menu and parent item.

**Shortcut for managing navigation directly:** Top toolbar → Content → Manage Main Menu.

---

## Accessibility

YaleSites has **Editoria11y** built in — an accessibility checker developed by Princeton that scans for WCAG violations after each page save. It highlights issues like missing alt text, empty headings, and poor link text directly on the page.

---

## Integrations & Custom Modules

Key custom modules (`web/profiles/custom/yalesites_profile/modules/custom/`):

| Module | Purpose |
|---|---|
| `ys_core` | Platform foundation, shared utilities |
| `ys_layouts` | Layout Builder regions and layout types |
| `ys_themes` | Global theme system, design tokens bridge |
| `ys_toolbar` | Custom admin toolbars |
| `ys_views_basic` | Simple Views blocks for listing content |
| `ys_views_content_resources` | Advanced content resource Views |
| `ys_localist` | Localist events integration |
| `ys_embed` | Third-party iframe embeds (via Media Library) |
| `ys_servicenow` | ServiceNow integration |
| `ys_ai` | Ask Beacon AI integration |
| `ys_alert` | Sitewide alert banner |
| `ys_captcha` | Form spam protection |
| `ys_migrate` | Content migration tools |
| `ys_node_access` | Content access restrictions |
| `ys_starterkit` | New site scaffolding |
| `ys_campus_groups` | Campus Groups integration |
| `ys_mail` | Email configuration |
| `ys_file_management` | File/media management |
| `ys_book` | Book (hierarchical page) content type |
| `ys_taxonomy_manager` | Taxonomy administration |
| `ys_integrations` | Shared integrations framework |

---

## Localist Integration

Localist is a third-party event management platform used by many Yale departments. Sites with the Localist integration enabled (`ys_localist` module) get automatic event syncing:

- Events created in Localist are **automatically fed into the YaleSites Drupal site** as Event content type nodes — no manual re-entry needed.
- The synced events appear in Views-powered event listings automatically, just like manually created Event nodes.
- Several fields on the Event edit form are **disabled (read-only)** when populated by Localist — Localist ID, Event Source, Event Status, Localist event URL, image URL, ICS URL, and Register enabled. Editors should not attempt to edit these.
- Editors can still create events manually in Drupal if they don't use Localist.
- The integration is enabled per-site, not globally — not every YaleSites site uses Localist.

---

## User Roles & Editorial Workflow

YaleSites has three user roles. See `references/user-roles-reference.md` for the full permissions table.

- **Site Administrator** — full control: can assign roles, publish, delete, restore content, and manage all site settings
- **Editor** — can publish, edit, create drafts, restore, and delete content; cannot assign roles
- **Contributor** — can create and edit drafts; **cannot publish** — changes must be approved by an Editor or Administrator

**Content moderation states:** Draft (default, not public) → Published (live) → Archived (hidden, preserved).

Existing users remain Site Administrators when these roles were introduced.

---

## Platform Eligibility & Lifecycle

- **Who qualifies:** Yale departments, units, and affiliated organizations with OPAC approval
- **Who doesn't:** Yale School of Medicine (separate platform); student orgs have separate pathway
- **Implementation options:** Self-service (editors build it), or assisted implementation with vendor support
- **Go-live process:** Requires OPAC sign-off → Pantheon dev environment → Test → Live
- **Scale:** 300+ active sites, 1,200+ editors as of platform documentation

---

## Editor Support Resources

When editors need help beyond what you can provide, direct them to these resources:

- **Email support:** yalesites@yale.edu — emails create ServiceNow tickets and are responded to by the YaleSites team. Best for specific issues, bug reports, or questions that need a team member's attention.
- **Trainings and office hours:** https://yalesites.yale.edu/trainings — YaleSites hosts regular training sessions and **office hours** where editors get one hour with a team member to ask any questions they have. Highly recommended for editors who are getting started or have complex questions.
- **User guide:** https://yalesites.yale.edu/explore-resources/user-guide — text documentation covering all platform features. The fallback reference for editors who want self-serve answers on specific topics.

---

## Answering Common User Questions

**"How do I add a block to my page?"**
1. Navigate to your page and click "Edit Layout and Content" in the second toolbar
2. In the Layout Builder, click the "+" button in the region where you want the block (Banner or Main content area)
3. Browse or search for the block type you want
4. Configure its content and design options in the block configuration panel
5. Click Save Layout when done

**"How do I change the color of a block?"**
In the Layout Builder, click the edit (pencil) icon on the block. Look for the color swatch picker — it shows the available colors with their names and hex code previews. Select the color you want and save the block.

**"My page isn't showing up in navigation."**
Go to the page's Manage Settings (`/edit`) and look at the **right sidebar**. If the sidebar is collapsed, click the gear icon to open it. Find "Menu settings," enable "Provide a menu link," select the correct menu, and save. You can also manage navigation directly at Content → Manage Main Menu in the top toolbar.

**"How do I create a news listing page?"**
In the Layout Builder, add a block and look for the Views block options. Choose a Views block from `ys_views_basic` or `ys_views_content_resources` and configure it in the block form. See `references/views-reference.md` for details on configuration options.

**"Why can't I change the font or colors freely?"**
Colors are limited to the Yale-approved palette in your site's theme. Font family can be changed in Site Settings (3 approved combinations), but font size is locked by the design system. This is intentional to maintain Yale brand consistency.
