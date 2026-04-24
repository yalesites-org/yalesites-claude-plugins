# YaleSites Content Types Field Reference

Field labels verified from `config/sync/` (develop branch). Fields listed in form display order. Fields common to all content types are listed once in the shared section below.

---

## Fields Shared by All 5 Content Types

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
| **External Source** | Link field. When set, clicking this content in listings redirects to an external URL. |
| **Simple XML Sitemap** | Controls whether this content appears in the XML sitemap. |

**Teaser fields** (shared by all — used in card/feed displays):

| Field Label | Notes |
|---|---|
| **Teaser Title** | Overrides the node Title in card and feed displays. |
| **Teaser Text** | Short description for cards. Max 150 characters. |
| **Teaser Media** | Image used in card displays. Falls back to the content's main image if not set. |

---

## Page

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | |
| **Category** | No | Taxonomy (page_category vocabulary) |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Tags** | No | *(shared)* |
| **Teaser** fieldset | — | Teaser Title, Teaser Text, Teaser Media |
| **Collection Navigation Display** | **Yes** | Select: "In Content Section" / "In Site Header" |
| *(Sidebar)* **CAS Login Required** | No | *(shared)* |
| *(Sidebar)* **Pin to the beginning of list** | No | *(shared)* |
| *(Sidebar)* **External Source** | No | *(shared)* |
| **URL alias** | No | *(shared)* |
| **Metadata** | No | *(shared)* |

---

## Post

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | |
| **Associated Profile** | No | Entity reference to a Person/Profile node |
| **Author** | No | Free-text author name string |
| **Publish Date** | **Yes** | Date/time. Defaults to current date/time. Used for sorting in Views. |
| **Category** | No | Taxonomy (post_category vocabulary) |
| **Tags** | No | *(shared)* |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Teaser** fieldset | — | Teaser Lead-In, Teaser Title, Teaser Text, Teaser Media |
| *(Sidebar)* **Show Social Media Sharing Links** | No | Boolean. Default off. |
| *(Sidebar)* **Show Read Time** | No | Boolean. |
| *(Sidebar)* **CAS Login Required** | No | *(shared)* |
| *(Sidebar)* **Pin to the beginning of list** | No | *(shared)* |
| *(Sidebar)* **External Source** | No | *(shared)* |

---

## Event

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

### Tab 5: Localist Data (read-only when set by Localist)

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

---

## Resource

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | |
| **Description** | No | Rich text body |
| **Resource Category** | No | Taxonomy (resource_category vocabulary) |
| **Audience** | No | *(shared)* |
| **Custom Vocab** | No | *(shared)* |
| **Affiliation** | No | Taxonomy (affiliation vocabulary) |
| **Resource Media** | **Yes** | Document or video media entity — the file itself |
| **Resource Publication Date** | No | Date/time. Full date required even if only the year will display. |
| **Date Format** | No | Select: Year / Month/Year / Month/Day/Year (default) |
| **Tags** | No | *(shared)* |
| **Teaser** fieldset | — | Teaser Title, Teaser Text, Teaser Media |

---

## Person (Profile)

### General Information fieldset

| Field Label | Required | Notes |
|---|---|---|
| **Title** | Yes | Full display name |
| **First Name** | No | Used for display; last name drives A-Z sorting |
| **Last Name** | No | Primary sort field for profile directories |
| **Prefix** | No | Honorific — e.g. Dr., Prof. |
| **Pronouns** | No | Free text |
| **Position** | No | Job title or primary role |
| **Subtitle** | No | Secondary title or additional role |
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

**Note on sorting:** The Views sort option "Last Name - A-Z" sorts on `field_last_name`. Always populate Last Name for profiles that will appear in directory listings.
