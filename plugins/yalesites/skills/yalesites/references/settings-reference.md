# YaleSites Sitewide Settings Reference

Sitewide settings live on the **Manage Settings page** (`/edit`) for a site — not in the Layout Builder. They control the structural, branding, and global behavioral settings that affect the entire site.

Access path: Navigate to any page on your site → second toolbar → **Manage Settings**

---

## Site Identity & Information

| Setting | Description |
|---|---|
| **Site name** | The official name of the site, displayed in the browser tab and page header |
| **Site slogan** | Optional tagline; appears in specific theme placements |
| **Site email** | Default sender address for system emails |
| **URL alias / path** | The path at which this site or page lives |
| **Front page** | Which node or view is the homepage |

---

## Theme Settings (Global Theme)

The **Global Theme** ("lever") controls the site-wide color palette. This is distinct from the per-block **Component Theme** ("dial").

| Setting | Description |
|---|---|
| **Global Theme selection** | Choose from available theme variants (mapped to Yale brand palettes defined in design tokens) |
| **Header style** | Controls how the site header renders (e.g., global/local header treatment) |
| **Footer style** | Controls footer layout variant |

**How the theme system works:**
1. Design tokens (from the `tokens` repo / Figma) define color variables
2. The Global Theme maps those tokens to specific named colors (e.g., Yale Blue, New Haven Green)
3. When editing a block in Layout Builder, editors see a color swatch picker showing the color name and hex preview
4. Result: the same color slot looks different on a site with a different Global Theme

Editors cannot create custom themes. Theme variants are maintained by the YaleSites platform team.

## Font Settings

In Site Settings, editors can choose the site's font pairing from three Yale-approved combinations:

| Option | Description |
|---|---|
| **YaleNew (old-style numerals) / Mallory** (default) | YaleNew with old-style numerals in the site name and headings; Mallory for body text. The old-style numeral behavior is now explicitly labeled (previously just called "YaleNew / Mallory"). |
| **Mallory / Mallory** | Mallory for both headings and body text |
| **YaleNew (standard numerals) / Mallory** | YaleNew with standard lining numerals throughout — for sites that want a clean, modern number style. Added in v2.22. |

Font size is not configurable — it is controlled by design tokens and cannot be overridden by editors.

---

## Navigation & Menus

### Main Navigation

The primary site navigation that appears in the header.

| Setting | Description |
|---|---|
| **Menu items** | Add/edit/remove top-level and nested menu links |
| **Hierarchy** | Menus support nested items (parent → child) for dropdowns |
| **Menu link titles** | Short labels display in nav; full titles can be set separately |

**To add a page to the menu:** Go to the page's Manage Settings → Menu settings → check "Provide a menu link" → set parent and weight. You can also manage navigation links directly via Content → Manage Main Menu in the top toolbar. Note: the standard Drupal "Structure → Menus" admin path is not accessible to regular YaleSites users — it is a user0-only screen.

### Footer Menu

Separate menu instance for footer links. Managed same as Main Navigation but renders in the footer region.

### Utility Menu

A secondary set of links that appears in the site header (typically for things like "Give", "Directory", or "Intranet").

---

## Header Settings

| Setting | Description |
|---|---|
| **Header layout** | Some themes offer layout variants for the header (e.g., with/without search, utility menu placement) |
| **Logo** | Sites use the Yale University identity or unit-specific lockups. Uploading custom logos must follow Yale brand guidelines and is subject to OPAC review |
| **Search** | Enable/disable the site search bar in the header |

---

## Footer Settings

| Setting | Description |
|---|---|
| **Footer type** | Whether the site uses the global Yale footer or a local/custom footer variant |
| **Footer logo** | Yale identity mark in footer |
| **Footer text / copyright** | Optional copyright or disclaimer text |
| **Footer links** | Managed via Footer Menu (see above) |
| **Social links** | Social media profile URLs (see Social Links section below) |

---

## Social Links

Configure social media icons/links that appear in the footer.

Supported platforms typically include: Facebook, Twitter/X, Instagram, LinkedIn, YouTube, and others. Each entry takes a URL. Empty fields are hidden — only configured platforms display.

---

## Analytics

| Setting | Description |
|---|---|
| **Google Analytics ID** | UA or GA4 measurement ID. YaleSites supports adding the site's own GA property. Yale's central analytics may also be applied platform-wide |
| **Google Tag Manager** | GTM container ID if the site uses a tag manager instead of/in addition to direct GA |
| **Other analytics** | Depending on module configuration, other tracking pixels may be configurable |

**Note:** Adding unauthorized tracking scripts outside of these settings is not possible for editors (no custom JS injection). All analytics must go through these fields.

---

## Accessibility Settings

| Setting | Description |
|---|---|
| **Editoria11y** | Built-in accessibility checker (by Princeton). Runs after page saves; highlights issues for content editors. Configured platform-wide; individual site settings may expose suppress/ignore controls for specific rules |
| **Skip navigation** | Configured at the theme level; skip links are part of the base templates |

---

## Access & Permissions

| Setting | Description |
|---|---|
| **Site visibility** | Whether the site is publicly accessible or restricted (password protected / Yale login required). Configured via `ys_node_access` module |
| **CAS authentication** | Login via Yale NetID using CAS. Enabled platform-wide. Login path: append `/cas` to any site URL |
| **User roles** | Standard Drupal roles (Administrator, Editor, Content Author) plus any custom roles. Managed at People in the top admin toolbar |

### Default User Roles

| Role | Capabilities |
|---|---|
| **Administrator** | Full site access; manage settings, users, structure, modules |
| **Site Builder** | Configure layouts, content types, Views; no module management |
| **Editor** | Create and edit content, manage menus; cannot change site settings |
| **Content Author** | Create content in specific sections; more restricted than Editor |

Roles are assigned per-user in the People admin.

---

## Content Settings

| Setting | Description |
|---|---|
| **Default front page** | Path to the node or view used as the homepage |
| **403/404 pages** | Custom pages for access denied / not found errors |
| **Comment settings** | YaleSites disables comments by default on all content types |
| **Revision settings** | Content revisions are enabled; node edit history is retained |

---

## URL & Path Settings

| Setting | Description |
|---|---|
| **URL aliases** | Friendly paths for nodes (e.g., `/about` instead of `/node/42`). Configured per-node in Manage Settings |
| **Pathauto patterns** | Automatic URL generation based on content type and title (e.g., `/news/[node:title]`). Configured platform-wide |
| **Redirect management** | 301/302 redirects managed via the Redirect module; accessible to Admins and Site Builders |

---

## Alert Banner (`ys_alert`)

A sitewide alert bar that appears at the top of every page — used for urgent announcements.

| Setting | Description |
|---|---|
| **Alert text** | The message displayed in the alert bar |
| **Alert type** | Severity level (informational, warning, urgent) which affects color treatment |
| **Dismissible** | Whether visitors can close/dismiss the alert |
| **Active / Inactive** | Toggle to show or hide the alert without deleting the content |

---

## CAS / Authentication Settings

Yale CAS (Central Authentication Service) integration is handled by the `ys_core` and related modules.

- **Login URL:** Append `/cas` to the site URL (e.g., `https://mysite.yale.edu/cas`)
- **NetID required:** All editor/admin access requires a valid Yale NetID
- **External collaborators:** Cannot use CAS; require a Yale guest account or alternative access method
- **Auto-assign roles:** CAS login can auto-assign roles based on NetID attributes (configurable by platform admins)

---

## AI Integration (`ys_ai` — Ask Beacon)

The `ys_ai` module integrates with Yale's Ask Beacon AI assistant.

| Setting | Description |
|---|---|
| **Enable Ask Beacon** | Toggle the AI chatbot on/off for the site |
| **Placement** | Typically a floating button/widget; placement configured in module settings |

This is a platform-managed integration — sites can opt in but cannot customize the underlying AI model or responses.

---

## ServiceNow Integration (`ys_servicenow`)

Connects site forms or contact mechanisms to Yale's ServiceNow instance.

| Setting | Description |
|---|---|
| **ServiceNow endpoint** | API endpoint configuration (managed by platform admins) |
| **Form mapping** | Which site forms route to which ServiceNow queues |

This is typically configured during site setup, not by editors day-to-day.

---

## Localist Integration (`ys_localist`)

Syncs events from Yale's Localist events platform into Drupal Event nodes.

| Setting | Description |
|---|---|
| **Localist endpoint** | The Localist calendar API URL to pull events from |
| **Sync frequency** | How often the module pulls updates from Localist |
| **Group/filter** | Which Localist groups or calendars to import |

Synced events become standard Drupal Event nodes and can be used in Views like any other content.

---

## Starterkit (`ys_starterkit`)

Used during site provisioning to scaffold a new site with default content, menus, layouts, and configuration. Not used after initial site setup.
