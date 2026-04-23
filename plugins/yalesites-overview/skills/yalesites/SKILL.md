---
name: yalesites
description: >
  Deep expertise on YaleSites — Yale University's custom Drupal 10 CMS platform. Use this skill for any question about building or managing a YaleSites website, including: adding or configuring blocks in the Layout Builder, choosing between page components, understanding Manage Settings vs Layout Builder, configuring sitewide settings (theme, menus, footer, analytics), working with Views, content types, taxonomy, user roles, accessibility requirements, integrations (Localist, ServiceNow, CAS), and platform eligibility. Also use when helping the Product Manager make platform decisions, evaluate feature requests, advise editors or site builders, or think through Drupal architecture choices for the platform. Use this skill whenever someone asks about trainings, office hours, the training catalog, user guide topics, or YaleSites learning resources.
---

# YaleSites Platform Skill

YaleSites is Yale University's managed Drupal 10 CMS, hosted on Pantheon as a custom upstream. It powers 300+ Yale department and unit websites for 1,200+ editors. The platform deliberately constrains design choices to enforce brand consistency — this is intentional, not a limitation to work around.

## How to use this skill

This skill gives you deep platform context. For most questions, the information in this SKILL.md is sufficient. For deep dives, load the relevant reference file:

| Topic | Reference File |
|---|---|
| All blocks + design options | `references/blocks-reference.md` |
| Block sub-items (accordion items, cards, tiles, etc.) | `references/paragraphs-reference.md` |
| Content type field labels (Page, Post, Event, Resource, Person) | `references/content-types-reference.md` |
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
1. **Top toolbar** (always visible): Content, Structure, Appearance, People, Reports, Admin — site-wide admin. Note: Content → Manage Main Menu is a shortcut to manage navigation directly.
2. **Second toolbar** (content-specific, appears when viewing a node): Manage Settings | Edit Layout and Content | View | Revisions | Translate

### Top Toolbar — Sitewide Settings Categories

The top toolbar contains all site-wide administrative settings, organized into four categories:

- **Content** — Manage all site content: pages, posts, events, resources, people. Also includes "Manage Main Menu" shortcut and access to the Media Library.
- **Settings** — Site configuration: global theme, font family, site name, footer content, social links, Google Tag Manager ID, and other sitewide preferences. This is where the Global Theme "lever" is set.
- **People** — User management: view all users, assign roles (Site Administrator, Editor, Contributor), and manage access. Only Site Administrators can access this section.
- **Reports** — Site health and status: access Editoria11y accessibility reports, recent log messages, and other diagnostic information.

---

## Content Types

YaleSites has five content types:

| Content Type | Purpose |
|---|---|
| **Page** | General content — department pages, about pages, standard site sections |
| **Post** | News/blog articles; appears in Views-powered listings |
| **Event** | Calendar events; feeds into Views; integrates with Localist |
| **Resource** | Documents, reports, publications, and reference materials |
| **Person** | Faculty, staff, and people profiles |

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

### Section Placement Restrictions
The platform uses `layout_builder_restrictions_by_region` to control which block types are allowed in which regions. Restrictions operate at the **block content type level** — meaning separate block content types are required if different display modes need different placement rules. Editors cannot override these restrictions.

**Current restrictions for Views listing blocks** (as of the Views Block Rework epic):

| Display Mode | Full Width | 70% col | 30% sidebar | 50/50 | 33/33/33 |
|---|---|---|---|---|---|
| **Card Grid** | yes | yes | yes | yes | yes |
| **List** | yes | yes | no | no | no |
| **Condensed** | yes | yes | yes | yes | yes |
| **Directory** *(profiles only)* | yes | yes | no | no | no |
| **Calendar** *(events only)* | yes | no | no | no | no |

---

## The Design System — Themes and Constraints

### Global Theme ("lever")
Set at the site level in Sitewide Settings (top toolbar → Settings). Controls the overall color palette for the site — which named colors are available and what they look like. Editors cannot override this per-page.

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
Each block in the Layout Builder exposes a **"Theme"** field — a color swatch picker showing named colors with hex codes (e.g., "Blue Yale #00366b", "Gray 100 #f7f7f7"). Editors select from these named swatches. The available colors depend on the site's Global Theme.

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

## Media Library

The Media Library (accessible via top toolbar → Content → Media, or when inserting images in a block) stores all reusable media assets on the site. There are five media types:

- **Images** — Standard images used in blocks, banners, and content. Supports alt text, focal point cropping, and reuse across multiple pages.
- **Videos** — Embedded video content (typically YouTube or Vimeo). Used in the Video block and Video Banner.
- **Background Videos** — Full-bleed autoplay videos used specifically in banner contexts.
- **Embeds** — Third-party iframe embeds (managed via `ys_embed` module). Used in the Embed block for content like maps, forms, and external tools.
- **Documents** — Uploaded files (PDFs, Word docs, etc.) for download links and the Resource content type.

**Best practice:** Upload images through the Media Library rather than one-off. This allows the image to be reused across pages and updated site-wide from a single location.

---

## Menus & Navigation

YaleSites supports three types of navigation menus:

### Basic Nav
Standard hierarchical navigation. Best for sites with straightforward information architecture and a modest number of top-level sections. Supports dropdown sub-menus.

### Mega Nav
Expanded navigation with rich content in the dropdown panels — supports images, descriptions, and grouped links. Best for large sites with many sections that benefit from visual navigation aids.

### Focus Nav
Simplified navigation designed for focused user journeys (e.g., campaign sites, event sites, single-purpose microsites). Presents fewer navigation options to reduce distraction.

**To add a page to the main menu:** Go to that page's Manage Settings (`/edit`) → right sidebar → Menu settings → enable "Provide a menu link" → select the correct menu and parent item → save.

**Shortcut for managing navigation directly:** Top toolbar → Content → Manage Main Menu. This bypasses individual page settings and lets you manage the entire menu tree in one place — drag to reorder, add custom links, disable items.

**Footer and Utility Menus** are configured in Settings → Menus.

---

## Content Collections (Secondary Navigation)

Content Collections are a secondary navigation system for sites that have sections with many related pages — a User Guide, a report series, a documentation hub. They appear as a persistent contextual nav within a defined section of the site.

**What they do:** Group a set of pages under a shared label and display navigation links between those pages automatically. When a visitor is on any page within the collection, they see the collection nav, making it easy to move between related pages.

**How to create a Content Collection:**
1. Go to top toolbar → Structure → Content Collections
2. Create a new collection with a name and optional description
3. Add pages to the collection
4. On each page that should display the collection nav, configure it via page settings

**Display options:** The collection nav can be configured to appear in the header (below the main nav) or as a sidebar element, depending on the site's layout settings.

**Key distinction:** Content Collections are for grouping and cross-linking related pages — NOT the same as the main menu. A page can be in both the main menu and a Content Collection; they serve different purposes.

---

## Views — How They Work on YaleSites

Views are configured **entirely within the Layout Builder**. Site Administrators do not have access to the standard Drupal "Structure → Views" admin screen. The workflow is:

1. In the Layout Builder, click "+" to add a block
2. Search for and select the View block you want
3. Configure the View's content type, display format, sort, filters, and item count directly in the block form
4. Save the block

**The two View block modules:**
- **ys_views_basic** — for Posts, Events, Pages, and Profiles listings
- **ys_views_content_resources** — for Resources listings only

**Content type labels in the Views block form:** Posts, Events, Pages, Profiles (not "Person"), Resources. These are the exact labels users see — never refer to content types by their Drupal machine names when helping users.

### Views Display Modes

| Content Type | Display Modes |
|---|---|
| **Posts** | Card Grid, List, Condensed |
| **Events** | Card Grid, List, Condensed, Calendar |
| **Pages** | Card Grid, List, Condensed |
| **People** | Card Grid, List, Directory, Condensed |
| **Resources** | (handled by `ys_views_content_resources`) |

See `references/views-reference.md` for the complete list of display formats, sort options, and filter options with their exact labels.

---

## Editorial Workflow

YaleSites uses a content moderation system with three states integrated into the Manage Settings right sidebar.

**Content moderation states:**
- **Draft** — default state when content is created; not publicly visible. Contributors can only save to Draft.
- **Published** — live and visible to site visitors. Editors and Site Administrators can publish.
- **Archived** — removed from public view but preserved in Drupal; content can be restored.

**The Tasks: Draft sidebar** — Editors and Site Administrators can leave notes on content during review using the moderation sidebar, providing a lightweight review workflow.

**Revision history** is available via the "Revisions" tab in the second toolbar. Editors can compare revisions and restore previous versions.

**Workflow by role:**
- Contributor creates/edits → saves as Draft → Editor reviews → publishes or requests changes
- Site Administrator has full control over all states
- Only Editors and Site Administrators can move content to Published or Archived

---

## Taxonomy & Vocabulary

Taxonomy vocabularies categorize content and power Views filters. Managed via `ys_taxonomy_manager`.

**Common vocabularies:**
- **Tags** — general-purpose content tagging; flexible, editor-defined
- **Category** — structured classification for grouping content by type or topic
- **Audience** — defines who content is intended for (e.g., students, faculty, staff, alumni)

**How taxonomy connects to Views:** When a Views block is configured in the Layout Builder, editors can filter results by taxonomy terms — for example, showing only Posts tagged "Research" or Events categorized as "Public Lecture."

**Planning advice:** Before launching a site, agree on a consistent vocabulary structure. Inconsistent tagging makes Views filters unreliable.

---

## Accessibility

YaleSites has **Editoria11y** built in — an accessibility checker developed by Princeton that scans for WCAG violations after each page save.

**How Editoria11y works:** After saving a page, a small indicator appears in the lower corner showing any detected accessibility issues. Clicking it reveals the specific elements and issue type. Editors can mark issues as dismissed if they are intentional or known false positives.

**Site-wide accessibility reports** are available via top toolbar → Reports → Editoria11y.

**Creating Accessible Content — key practices:**
- Provide descriptive alt text for all images; mark decorative images as decorative explicitly
- Use heading hierarchy correctly — do not skip heading levels
- Write descriptive link text — "Read more about the YaleSites platform" not "Click here"
- Avoid using color alone to convey meaning
- Include captions and transcripts for video content
- Use tables only for tabular data, not layout; include proper headers

**Siteimprove** is a related external service for ongoing accessibility and SEO monitoring.

---

## Google Tag Manager

YaleSites supports Google Tag Manager (GTM) for analytics and tracking integrations.

**Setup:** Enter the GTM container ID in Settings (top toolbar → Settings → Google Tag Manager). Once the ID is entered, GTM fires on all pages.

**Relationship to Siteimprove:** Siteimprove is a separate analytics and accessibility platform that operates independently of GTM. Both can be active simultaneously.

---

## Common Misconceptions

**1. "I'll just edit the layout from the Manage Settings page."**
Wrong surface. Manage Settings (`/edit`) controls page metadata, content fields, menus, and publication status. The Layout Builder (`/layout`) controls blocks and visual design.

**2. "I need to add a block every time I want new content."**
Not always. For basic text content, the body/content fields in Manage Settings may be sufficient.

**3. "Why can't I pick Yale Blue in the color picker?"**
The color options shown are defined by the site's Global Theme — they are already Yale-approved colors. If the color isn't shown, the site's theme doesn't include it, and that is intentional.

**4. "Views is just a list block I can drop on the page."**
Views is the most complex feature on the platform. It dynamically queries content based on filters, sorts, and display configurations. See `references/views-reference.md`.

**5. "Any Yale department can just get a YaleSites site."**
Not quite. Sites require OPAC approval. Yale School of Medicine has their own separate platform. Student organizations have a separate pathway.

**6. "I can customize the design beyond what's in the block settings."**
No. The platform is intentionally locked down. Editors cannot add custom CSS or override design tokens.

**7. "The menu section isn't on the Manage Settings page."**
It is — but it's in the **right sidebar**, which can be accidentally collapsed. Look for the small gear/settings icon to reopen it.

**8. "Content Collections are just another type of menu."**
Content Collections and menus serve different purposes. Menus define primary site navigation. Content Collections create contextual secondary navigation linking related pages within a section.

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

Localist is a third-party event management platform. Sites with `ys_localist` enabled get automatic event syncing — events created in Localist are automatically fed into Drupal as Event nodes. Several fields are disabled (read-only) when populated by Localist. The integration is enabled per-site, not globally.

---

## User Roles & Editorial Workflow

YaleSites has three user roles. See `references/user-roles-reference.md` for the full permissions table.

- **Site Administrator** — full control: can assign roles, publish, delete, restore content, and manage all site settings
- **Editor** — can publish, edit, create drafts, restore, and delete content; cannot assign roles
- **Contributor** — can create and edit drafts; **cannot publish** — changes must be approved by an Editor or Administrator

---

## Platform Eligibility & Lifecycle

- **Who qualifies:** Yale departments, units, and affiliated organizations with OPAC approval
- **Who doesn't:** Yale School of Medicine (separate platform); student orgs have separate pathway
- **Go-live process:** Requires OPAC sign-off → Pantheon dev environment → Test → Live
- **Scale:** 300+ active sites, 1,200+ editors

---

## Training & Support Resources

### Training Catalog
Browse all training offerings at: https://yalesites.yale.edu/training-catalog

- **Building with Blocks** — Live Zoom training covering the Layout Builder. Core training for new editors.
- **Auditing and Web Maintenance Webinar** — Establishing a regular audit and maintenance schedule.
- **Conducting a Content Audit Webinar** — Cataloging and analyzing all content on a site.
- **Interpreting and Using Analytics Data Webinar** — Understanding website analytics.
- **Using a Content Matrix Webinar** — Content planning using a matrix tool.
- **Web Writing Best Practices Webinar** — Writing for the web; reaching various audiences.
- **YaleSites Office Hours** — Open Q&A with the YaleSites team.

Sign up for live sessions: https://yalesites.yale.edu/trainings
Office hours: https://yalesites.yale.edu/upcoming-events
Email support: yalesites@yale.edu

---

## User Guide Structure

The User Guide at https://yalesites.yale.edu/explore-resources/user-guide covers all platform features.

### Building Your Site
Content Types, Manage Settings, Edit Layout and Content, Create Powerful Page Sections, Building with Blocks, Sitewide Settings, Secondary Navigation with Content Collections, Working with Images in YaleSites

### Managing Site Content
Managing Site Content, Building Your Menu, Editorial Workflow, Google Tag Manager, Media Library, Using Taxonomy and Vocabulary

### Creating Accessible Content
Creating Accessible Content, Accessibility with Editoria11y

### Standalone Pages
- Term Glossary: https://yalesites.yale.edu/term-glossary
- Go-Live Checklist: https://yalesites.yale.edu/go-live-checklist

---

## Answering Common User Questions

**"How do I add a block to my page?"**
Navigate to your page → "Edit Layout and Content" in the second toolbar → click "+" in the region where you want the block → browse/search for the block type → configure it → Save Layout.

**"How do I change the color of a block?"**
In the Layout Builder, click the pencil icon on the block. Look for the color swatch picker — select the color you want and save.

**"My page isn't showing up in navigation."**
Go to Manage Settings (`/edit`) → right sidebar (click the gear icon if collapsed) → Menu settings → enable "Provide a menu link" → select the correct menu → save.

**"Where can I get training on YaleSites?"**
Start with "Building with Blocks" — sign up at https://yalesites.yale.edu/trainings. Browse all topics at https://yalesites.yale.edu/training-catalog. For one-on-one help, attend Office Hours at https://yalesites.yale.edu/upcoming-events.

**"My content is saved but visitors can't see it."**
Check the publication status. Go to Manage Settings → right sidebar → look at the moderation state. If it says "Draft," change it to "Published" (Editors/Admins) or ask an Editor to publish it (Contributors).

**"How do I set up secondary navigation for a section of my site?"**
Use Content Collections. Go to Structure → Content Collections, create a collection, add the relevant pages, and configure which pages display the collection nav.
