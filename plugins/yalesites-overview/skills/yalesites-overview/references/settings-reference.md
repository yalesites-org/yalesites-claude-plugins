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

**How the theme system works:**
1. Design tokens (from the `tokens` repo / Figma) define color variables
2. The Global Theme maps those tokens to specific named colors (e.g., Yale Blue, New Haven Green)
3. When editing a block in Layout Builder, editors see a color swatch picker showing the color name and hex preview
4. Result: the same color slot looks different on a site with a different Global Theme

Editors cannot create custom themes. Theme variants are maintained by the YaleSites platform team.

## Font Settings

| Option | Heading Font | Body Font |
|---|---|---|
| **YaleNew / Mallory** (default) | YaleNew | Mallory |
| **Mallory / Mallory** | Mallory | Mallory |
| **YaleNew (old numbers) / Mallory** | YaleNew (oldstyle numerals variant) | Mallory *(coming in next release)* |

Font size is not configurable — it is controlled by design tokens and cannot be overridden by editors.

---

## Navigation & Menus

**To add a page to the menu:** Go to the page's Manage Settings → Menu settings → check "Provide a menu link" → set parent and weight. Do NOT add pages to menus from the menu admin (Structure → Menus) unless managing links to external URLs.

- **Main Navigation** — primary site navigation in the header
- **Footer Menu** — separate menu instance for footer links
- **Utility Menu** — secondary set of links in the site header (e.g., "Give", "Directory")

---

## Analytics

| Setting | Description |
|---|---|
| **Google Analytics ID** | UA or GA4 measurement ID |
| **Google Tag Manager** | GTM container ID |

**Note:** Adding unauthorized tracking scripts outside of these settings is not possible for editors (no custom JS injection). All analytics must go through these fields.

---

## Alert Banner (`ys_alert`)

A sitewide alert bar that appears at the top of every page.

| Setting | Description |
|---|---|
| **Alert text** | The message displayed in the alert bar |
| **Alert type** | Severity level (informational, warning, urgent) |
| **Dismissible** | Whether visitors can close/dismiss the alert |
| **Active / Inactive** | Toggle to show or hide the alert without deleting the content |

---

## Access & Permissions

| Setting | Description |
|---|---|
| **Site visibility** | Whether the site is publicly accessible or restricted |
| **CAS authentication** | Login via Yale NetID using CAS. Login path: append `/cas` to any site URL |
| **User roles** | Managed at People in the top admin toolbar |

---

## CAS / Authentication

- **Login URL:** Append `/cas` to the site URL (e.g., `https://mysite.yale.edu/cas`)
- **NetID required:** All editor/admin access requires a valid Yale NetID
- **External collaborators:** Cannot use CAS; require a Yale guest account or alternative access method

---

## Localist Integration (`ys_localist`)

| Setting | Description |
|---|---|
| **Localist endpoint** | The Localist calendar API URL to pull events from |
| **Sync frequency** | How often the module pulls updates from Localist |
| **Group/filter** | Which Localist groups or calendars to import |

Synced events become standard Drupal Event nodes and can be used in Views like any other content.

---

## AI Integration (`ys_ai` — Ask Beacon)

| Setting | Description |
|---|---|
| **Enable Ask Beacon** | Toggle the AI chatbot on/off for the site |
| **Placement** | Typically a floating button/widget |

This is a platform-managed integration — sites can opt in but cannot customize the underlying AI model or responses.
