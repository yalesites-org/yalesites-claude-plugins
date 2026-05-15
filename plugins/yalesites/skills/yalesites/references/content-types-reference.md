# YaleSites Content Types Field Reference

Field labels verified from `config/sync/` (develop branch). Fields listed in form display order. Fields common to all content types are listed once in the shared section below.

---

## Fields Shared by All 5 Content Types

These fields appear on every content type's Manage Settings form:

| Field Label | Notes |
|---|---|
| **Title** | Required. The page/content title. |
| **Audience** | Taxonomy (audience vocabulary). Filters content in Views. |
| **Custom Vocab** | Taxonomy (custom_vocab vocabulary). Site-specific custom categorization. |
| **Tags** | Taxonomy (tags vocabulary). General-purpose tagging. |
| **URL alias** | Path alias for the page URL. |
| **URL redirects** | Set up redirects from old URLs to this page. |
| **Metadata** | SEO meta tags (title, description, Open Graph, etc.). In the sidebar. |
| **CAS Login Required** | Boolean. Restrict this page to CAS-authenticated (Yale NetID) users only. |
| **Pin to the beginning of list** | Boolean. Pins content to the top of Views listings. |
| **External Source** | Link field. When set, clicking this content in listings redirects to an external URL instead of this page. Bypasses the Layout Builder. |
| **Simple XML Sitemap** | Controls whether this content appears in the XML sitemap. |

**Teaser fields** (also shared by all — used in card/feed displays):

| Field Label | Notes |
|---|---|
| **Teaser Title** | Overrides the node Title in card and feed displays. |
| **Teaser Text** | Short description for cards. Max 150 characters. |
| **Teaser Media** | Image used in card displays. Falls back to the content's main image if not set. |

---

## Page

General department pages, about pages, and standard site sections.

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | |
| **Category** | No | Taxonomy (page_category vocabulary) |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Tags** | No | *(shared)* |
| **Teaser** fieldset | — | Teaser Title, Teaser Text, Teaser Media |
| **Collection Navigation Display** | **Yes** | Select: "In Content Section" / "In Site Header" — controls where secondary nav appears |
| *(Sidebar)* **CAS Login Required** | No | *(shared)* |
| *(Sidebar)* **Pin to the beginning of list** | No | *(shared)* |
| *(Sidebar)* **External Source** | No | *(shared)* |
| **URL alias** | No | *(shared)* |
| **Metadata** | No | *(shared)* |

**Note:** "Collection Navigation Display" is a required field unique to Page — it determines whether the secondary/collection navigation renders inside the content area or in the site header.

---

## Post

News articles and blog posts. Appears in Views-powered news listings.

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | |
| **Associated Profile** | No | Entity reference to a Profile node — links the post to an author Profile for sorting |
| **Author** | No | Free-text author name string — displayed in post metadata |
| **Publish Date** | **Yes** | Date/time. Defaults to the current date/time. Used for sorting in Views. |
| **Category** | No | Taxonomy (post_category vocabulary) |
| **Tags** | No | *(shared)* |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Teaser** fieldset | — | Teaser Lead-In (short eyebrow text), Teaser Title, Teaser Text, Teaser Media |
| *(Sidebar)* **Show Social Media Sharing Links** | No | Boolean. Default off. Shows social sharing buttons on the post. |
| *(Sidebar)* **Show Read Time** | No | Boolean. Shows estimated read time. |
| *(Sidebar)* **CAS Login Required** | No | *(shared)* |
| *(Sidebar)* **Pin to the beginning of list** | No | *(shared)* |
| *(Sidebar)* **External Source** | No | *(shared)* |
| **URL alias** | No | *(shared)* |
| **Metadata** | No | *(shared)* |

**Post-specific Teaser field:** Posts have an additional "Teaser Lead-In" field — a short eyebrow/label text displayed above the title in card views.

---

## Event

Calendar events. Uses a tabbed form interface. Integrates with the Localist platform.

The event form is organized into **5 tabs** plus persistent sidebar fields.

### Tab 1: Basic Info

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | Event name |
| **Description** | No | Rich text body |
| **Event Website** | No | Link field with title — for Register/RSVP links |
| **Event Experience** | No | Taxonomy (event_type vocab) — e.g. In-Person, Online, Hybrid |
| **Yale Location** | No | Taxonomy (event_place vocab) — Yale building/venue |
| **Room** | No | Free text room/space name |
| **Dates** | No | Smart Date field — supports single and recurring events |
| **Recurring Event** | No | Boolean — marks event as recurring |
| **Stream URL** | No | Link to livestream |
| **Stream embed code** | No | Embed code for inline streaming |

### Tab 2: Teaser

| Field Label | Required | Notes |
|---|---|---|
| **Teaser Title** | No | *(shared)* |
| **Teaser Text** | No | *(shared — max 150 chars)* |
| **Teaser Media** | No | *(shared)* |

### Tab 3: Taxonomies

| Field Label | Required | Notes |
|---|---|---|
| **Tags** | No | *(shared)* |
| **Event Category** | No | Taxonomy (event_category vocab) |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |

### Tab 4: Tickets

| Field Label | Required | Notes |
|---|---|---|
| **Ticket cost** | No | Free text — e.g. "Free", "$25" |
| **Ticket registration URL** | No | Link to ticket/registration page |

### Tab 5: Localist Data

These fields are **populated automatically** by the Localist integration and are disabled (read-only) when set. Editors should not edit them manually.

| Field Label | Notes |
|---|---|
| **Localist ID** | Auto-populated from Localist |
| **Event ID** | External source event ID |
| **Event Source** | Taxonomy (event_sources vocab) |
| **Event status** | Taxonomy (event_status vocab) |
| **Localist event URL** | Link back to the Localist event |
| **Localist event image URL** | Source image URL from Localist |
| **Localist ICS URL** | Calendar subscription link |
| **Localist Register enabled** | Whether registration is enabled in Localist |

### Persistent sidebar/bottom fields (outside tabs)

| Field Label | Required | Notes |
|---|---|---|
| **CAS Login Required** | No | *(shared)* |
| **Pin to the beginning of list** | No | *(shared)* |
| **External Source** | No | *(shared)* |
| **URL alias** | No | *(shared)* |
| **Metadata** | No | *(shared)* |

---

## Resource

Documents, reports, publications, and reference materials. Requires a file, video, or image attachment. As of v2.22, the Resource content type includes full publication support for journal articles, working papers, and scholarly content.

The Resource form is organized into tabs:

### Basic Info tab

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | |
| **Description** | No | Rich text body (restricted_html format) |
| **Abstract** | No | Rich text summary of the publication (restricted_html format) |
| **Citation** | No | Formatted citation text (restricted_html; supports `<sub>` and `<sup>` tags for academic formatting) |
| **Journal Publication Name** | No | Name of the journal or publication venue |
| **Journal Publication Issue** | No | Issue, volume, or edition identifier |
| **Affiliated Authors** | No | Entity reference to Profile nodes — links the resource to Yale-affiliated authors. Displays as linked names. (Previously labeled "Authors") |
| **Non-affiliated Authors** | No | Unlimited double field (First Name + Last Name columns) for authors without a Profile node. Displays as plain text. Both author lists are merged and sorted alphabetically on display. |
| **DCN** | No | Custom compound field for structured identifier data: ISBN, ISPS ID, and Ref values |
| **Related Resources** | No | Entity reference to other Resource nodes; renders in a minimal title + date view mode |
| **Resource Media** | **Yes** | Document, video, or image media entity — the primary file or media item |
| **Resource Publication Date** | No | Date/time. Full date required even if only the year will display. |
| **Date Format** | No | Select: **Year** / **Month/Year** / **Month/Day/Year** (default: Month/Day/Year) — controls how the date displays publicly |

### Taxonomies tab

| Field Label | Required | Notes |
|---|---|---|
| **Resource Category** | No | Taxonomy (resource_category vocabulary). Moved from Basic Info tab in v2.22. Accessible to site admins via Manage Taxonomies. |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Affiliation** | No | Taxonomy (affiliation vocabulary) |
| **Discipline** | No | Taxonomy (new Discipline vocabulary, added v2.22) |
| **Academic Years** | No | Taxonomy (new Academic Years vocabulary, added v2.22; pre-populated with year terms) |
| **Areas of Study** | No | Taxonomy (new Areas of Study vocabulary, added v2.22) |
| **Geographic Areas** | No | Taxonomy (new Geographic Areas vocabulary, added v2.22) |
| **Tags** | No | *(shared)* |

### Teaser / Sidebar fields

| Field Label | Required | Notes |
|---|---|---|
| **Teaser** fieldset | — | Teaser Title, Teaser Text, Teaser Media |
| *(Sidebar)* **CAS Login Required** | No | *(shared)* |
| *(Sidebar)* **Pin to the beginning of list** | No | *(shared)* |
| *(Sidebar)* **External Source** | No | *(shared)* |
| **URL alias** | No | *(shared)* |
| **Metadata** | No | *(shared)* |

**Note on authors:** Affiliated Authors (Profile node references) and Non-affiliated Authors (plain-text first/last name) are grouped under an "Authors" section on the form. On the published page, both lists are merged and sorted last-name-first alphabetically. Affiliated authors render as links to their Profile pages; non-affiliated render as plain text.

**Note on Revision Date:** A Revision Date field exists in the database but is intentionally hidden from the editor-facing form.

**New taxonomy vocabularies (v2.22):** Academic Years, Areas of Study, Discipline, Geographic Areas. Editors and site admins can manage terms in these vocabularies via Manage Taxonomies in the top toolbar.

---

## Profile

Faculty, staff, and people profiles. Used in directory and profile Views.

The form has two main fieldsets: **General Information** and **Contact Information**.

### General Information fieldset

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | Full display name |
| **First Name** | No | Used for display; last name drives A-Z sorting in Views |
| **Last Name** | No | Primary sort field for profile directories |
| **Prefix** | No | Honorific — e.g. Dr., Prof. |
| **Pronouns** | No | Free text |
| **Position** | No | Job title or primary role |
| **Subtitle** | No | Secondary title or additional role (supports inline HTML) |
| **Department** | No | Department name (free text) |
| **Affiliation** | No | Taxonomy (affiliation vocabulary) — used as the filter in Views directory listings |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Tags** | No | *(shared)* |

### Contact Information fieldset

| Field Label | Required | Notes |
|---|---|---|
| **Email** | No | Email address |
| **Phone** | No | Phone number (free text) |
| **Address** | No | Long text — supports inline HTML |

### Main form (outside fieldsets)

| Field Label | Required | Notes |
|---|---|---|
| **Profile Image** | No | Image from Media Library — used in directory cards and profile pages |
| **Teaser** fieldset | — | Teaser Title, Teaser Text, Teaser Media |
| *(Sidebar)* **CAS Login Required** | No | *(shared)* |
| *(Sidebar)* **Pin to the beginning of list** | No | *(shared)* |
| *(Sidebar)* **External Source** | No | *(shared)* |
| **URL alias** | No | *(shared)* |
| **Metadata** | No | *(shared)* |

**Note on sorting in directory Views:** The Views sort option "Last Name - A-Z" sorts on `field_last_name`. Editors should always populate Last Name for profiles that will appear in directory listings, even if Title is the display name.
