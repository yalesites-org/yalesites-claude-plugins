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
| Views (filters, displays, modules) | `references/views-reference.md` |
| Sitewide settings (Manage Settings page) | `references/settings-reference.md` |

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

### Manage Settings (`/edit` or "Edit" in toolbar)
The **logistical/structural** surface. Accessed via the second toolbar → "Manage Settings." Covers:
- Page title, URL alias, menu placement
- Content authoring fields (body, metadata)
- Publication status (draft/published)
- SEO fields, access restrictions
- Node-level settings specific to the content type

**Key rule:** If it's about *what this page is called, where it lives, or whether it's published*, it's on Manage Settings.

### Layout Builder (`/layout` or "Edit Layout and Content" in toolbar)
The **visual composition** surface. Accessed via second toolbar → "Edit Layout and Content." This is where editors:
- Add, remove, and reorder blocks in the Banner area and Main content area
- Configure each block's visual design options (theme dial, layout, etc.)
- Manage the two-column structure of the page canvas

**Key rule:** If it's about *what's on the page visually and how it looks*, it's in the Layout Builder.

### Two Toolbars
1. **Top toolbar** (always visible): Content, Structure, Appearance, People, Reports, Admin — site-wide admin
2. **Second toolbar** (content-specific, appears when viewing a node): Manage Settings | Edit Layout and Content | View | Revisions | Translate

---

## Content Types

| Content Type | Purpose |
|---|---|
| **Basic Page** | General content; default for departments |
| **Landing Page** | Homepage-style full-width layouts, no sidebar |
| **Post** | News/blog articles; feeds into Views |
| **Event** | Calendar events; feeds into Views; integrates with Localist |
| **Person** | Faculty/staff profiles |
| **Gallery** | Media grid/photo gallery |
| **Book** | Structured multi-page hierarchical content (`ys_book` module) |

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
- Collections: Card Collection, Custom Card Collection, Tiles, Facts & Figures
- Dynamic (Views-powered): Views blocks via `ys_views_basic` and `ys_views_content_resources`

For the full list of each block's design options, read `references/blocks-reference.md`.

---

## The Design System — Themes and Constraints

### Global Theme ("lever")
Set at the site level in Sitewide Settings. Controls the overall color palette for the site. Editors cannot override this per-page.

### Component Theme ("dial")
Per-block color accent selector. Options: **default**, **one**, **two**, **three**, **four**, **five**. Each maps to a color defined by the Global Theme via design tokens from Figma. Most blocks expose a theme dial.

**Critical constraint:** The platform is intentionally prescriptive. Design options are limited to what the component library exposes — editors cannot add custom CSS, override colors arbitrarily, or inject HTML. This is by design to maintain brand consistency across 300+ Yale sites.

### What editors CAN control (per block):
- Theme dial (color accent)
- Layout variants (e.g., image left/right, column count)
- Content/text fields
- Whether optional elements appear (images, links, badges, overlays)

### What editors CANNOT control:
- Font family or size (set by design tokens)
- Custom colors outside the theme palette
- Arbitrary HTML injection into most blocks
- Moving blocks between Banner and Main Content regions

---

## Common Misconceptions

**1. "I'll just edit the layout from the Edit page."**
Wrong surface. `/edit` (Manage Settings) controls page metadata and content fields. `/layout` (Layout Builder) controls blocks and visual design. Many editors spend 10 minutes on the wrong screen.

**2. "I need to add a block every time I want new content."**
Not always. For basic text content on a Basic Page, the body field in Manage Settings may be sufficient. Layout Builder is for structured/designed components.

**3. "The theme color options are a bug — I want the actual Yale Blue."**
The theme dial maps to the site's Global Theme palette, which is intentionally curated to Yale brand standards. The five color slots are pre-defined. This is not a bug.

**4. "Views is just a list block I can drop on the page."**
Views is the most complex feature on the platform. It queries, filters, sorts, and displays content dynamically. It requires understanding content types, taxonomy, and display formats. See `references/views-reference.md`.

**5. "Any Yale department can just get a YaleSites site."**
Not quite. Sites require OPAC approval. Yale School of Medicine (YSM) has their own separate platform and is explicitly excluded. Student organizations have a separate pathway.

**6. "I can customize the design beyond what's in the block settings."**
No. The platform is intentionally locked down. Editors cannot add custom CSS or override design tokens. Site builders can request custom components through the product roadmap process.

---

## Taxonomy

Taxonomy vocabularies are used for categorizing content and powering Views filters. Common vocabularies:
- **Tags** — general-purpose content tagging
- **Category** — structured classification
- **Audience** — who content is for

Taxonomy is managed at Structure → Taxonomy in the admin toolbar. The `ys_taxonomy_manager` custom module handles taxonomy administration.

---

## Menus

YaleSites supports multiple menu types:
- **Main Navigation** — primary site nav, appears in header
- **Footer Menu** — links in site footer
- **Utility Menu** — secondary header links

Menus are managed from Structure → Menus, or configured in Sitewide Settings. Adding a page to a menu is typically done from the Manage Settings page of the content node, not from the menu admin.

---

## Accessibility

YaleSites has **Editoria11y** built in — an accessibility checker developed by Princeton that scans for WCAG violations after each page save. It highlights issues like missing alt text, empty headings, and poor link text directly on the page.

The platform also enforces accessible design patterns at the component level (e.g., proper heading hierarchy, keyboard navigation for tabs and accordions).

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
| `ys_embed` | Third-party iframe embeds |
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

## Platform Eligibility & Lifecycle

- **Who qualifies:** Yale departments, units, and affiliated organizations with OPAC approval
- **Who doesn't:** Yale School of Medicine (separate platform); student orgs have separate pathway
- **Implementation options:** Self-service (editors build it), or assisted implementation with vendor support
- **Go-live process:** Requires OPAC sign-off → Pantheon dev environment → Test → Live
- **Scale:** 300+ active sites, 1,200+ editors as of platform documentation

---

## Answering Common User Questions

**"How do I add a block to my page?"**
1. Navigate to your page and click "Edit Layout and Content" in the second toolbar
2. In the Layout Builder, click the "+" button in the region where you want the block (Banner or Main content area)
3. Browse or search for the block type you want
4. Configure its content and design options in the block configuration panel
5. Click Save Layout when done

**"How do I change the theme/color of a block?"**
In the Layout Builder, click the edit (pencil) icon on the block. Look for the "Component Theme" or "Theme Color" field — select one through five (or default). Save the block.

**"My page isn't showing up in navigation."**
Go to Manage Settings (`/edit`) and check the "Menu settings" section. Add the page to the appropriate menu and set its parent/weight.

**"How do I create a news listing page?"**
Use a Views block from `ys_views_basic` or `ys_views_content_resources`, configured to show Post content type nodes. See `references/views-reference.md` for details.

**"Why can't I change the font or colors freely?"**
YaleSites enforces Yale brand standards through design tokens. The component theme "dial" (one–five) is the only color customization available per block, and it maps to the site's approved Global Theme palette.
