# YaleSites Block Reference

All blocks available in the YaleSites Layout Builder, with their **verified Drupal field labels** sourced directly from the platform's Drupal config YAML files (`field.field.block_content.*.yml`, `web/profiles/custom/yalesites_profile/config/sync/`). These are the exact labels editors see in the "Configure block" form in the Layout Builder.

**All blocks verified:** All field labels and select options in this reference are sourced directly from Drupal config YAML files (`config/sync/`) and `ys_themes.component_overrides.yml`.

**Color picker ("Theme" field):** Most blocks include a "Theme" field — a color swatch picker displaying named colors with hex codes (e.g., "Blue Yale #00366b", "Gray 100 #f7f7f7"). The available colors depend on the site's Global Theme setting. Always refer to colors by their displayed name (e.g., "Blue Yale"), never as "theme one."

**Padding Options field:** Most blocks include a "Padding Options" field with these choices:
- Padding on both top and bottom *(default)*
- No top padding
- No bottom padding
- No padding (removes both top and bottom padding)

---

## Banner Area Blocks

Only one banner block can be placed at a time in the Banner region.

---

### ✅ Grand Hero

The largest, most prominent banner. Full-width with a background image or video and optional overlay content.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title (editors only) |
| **Heading** | Required. 50-character recommended length. |
| **Heading Level** | Select: "H1: This page's title is hidden" / "H2: This page's title is displayed or visually hidden" |
| **Replace heading with image** | Checkbox — swap the text heading for an image |
| **Text** | Rich text body. 90-character recommended length. |
| **Theme** | Color swatch picker (named colors with hex codes) |
| **Overlay Position** | Select: Full / Floating Box / Floating Box Narrow |
| **Media Size** | Select: Tall / Short / Mini |
| **Media** | Image or background video upload |
| **Banner Overlay PNG** | Optional PNG image overlay (appears over the background) |
| **Link** | Primary CTA — URL + link text |
| **Link Two** | Secondary CTA — URL + link text |
| **Padding Options** | See above |

---

### ✅ Action Banner

A prominent banner designed for calls to action. Supports two CTAs and a configurable content layout. Drupal machine name: `cta_banner`.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Image** | Required background image |
| **Action Banner Heading** | Required. Max 50 characters. |
| **Action Banner Content** | Rich text body. Max 90 characters. |
| **Call-to-action** | Primary CTA — URL + link text |
| **Call-to-action Two** | Secondary CTA — URL + link text |
| **Theme** | Color swatch picker — One through Five |
| **Layout** | Select: Bottom / Left / Right — position of text/CTA over the image |
| **Heading Level** | Select: H1 (page title hidden) / H2 (page title shown) |
| **Overlay background image** | Optional additional overlay image |
| **Padding Options** | See above |

---

### ✅ Image Banner

A simpler banner — primarily image-driven with minimal content controls.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Image** | Image or background video |
| **Image Caption** | Rich text caption |
| **Media Size** | Select: Tall / Short |
| **Padding Options** | See above |

---

### ✅ Video Banner

A full-width banner driven by an embedded or background video.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Video** | Video media entity |
| **Video Width** | Select: Contained / Full Width |
| **Padding Options** | See above |

---

## Main Content Area Blocks — Text & Content

---

### ✅ Text

A basic rich-text content block. The body text field is labeled **"Content"** in this block (not "Text").

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Content** | Rich text body field |
| **Text Style Variation** | Select: Default / Emphasized |
| **Padding Options** | See above |

---

### ✅ Accordion

Collapsible content sections. Each accordion item has its own heading and body. Ideal for FAQs.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Accordion Component Title** | Heading displayed above the accordion group |
| **Accordion Item(s)** | Paragraph sub-items — each has its own heading and content |
| **Theme** | Color swatch picker — includes "Default - No Color" option |
| **Padding Options** | See above |

---

### ✅ Inline Message

An informational or marketing callout that appears inline within the content flow.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Heading** | Block heading |
| **Content** | Rich text body |
| **Link** | CTA link — URL + link text |
| **Theme** | Color swatch picker |
| **Padding Options** | See above |

---

### ✅ Quote Callout

A styled pull-quote block with optional image and multiple style variants.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Quote** | Rich text — the quote content |
| **Attribution** | Rich text — quote author/source |
| **Image** | Optional portrait image (entity reference) |
| **Theme** | Color swatch picker |
| **Style** | Select: Bar / Quote |
| **Alignment** | Select: Left / Right |
| **Padding Options** | See above |

---

### ✅ Tabs

A tabbed interface where each tab contains independently authored content.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Tabs** | Paragraph sub-items — each tab has its own heading and content |
| **Padding Options** | See above |

*Note: No "Theme" field on Tabs.*

---

### ✅ Callout

A visually distinct callout block — good for highlighting a key message or CTA. Drupal machine name: `callout`.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Callout Item(s)** | Paragraph sub-items — each item contains the callout content |
| **Theme** | Color swatch picker — One through Five |
| **Alignment** | Select: Left / Center |
| **Overlay background image** | Optional background overlay image |
| **Padding Options** | See above |

---

### ✅ Text with Wrapped Image

Inline image alongside running text. Drupal machine name: `wrapped_image`.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Content** | Rich text — the main body text that wraps around the image |
| **Image** | Required image entity |
| **Caption** | Optional image caption. Max 150 characters. |
| **Position** | Select: Image Left / Image Right |
| **Style** | Select: Inline (image within column) / Offset (image shifts outside column) |
| **Padding Options** | See above |

---

### ✅ Text with Wrapped Callout

A styled callout box that floats alongside body text. Drupal machine name: `wrapped_text_callout`.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Callout Content** | Rich text — the content inside the floating callout box |
| **Wrapped Content** | Rich text — the main body text that wraps around the callout |
| **Callout Position** | Select: Left / Right |
| **Theme** | Color swatch picker — One through Five |
| **Padding Options** | See above |

---

## Main Content Area Blocks — Spotlights

---

### ✅ Content Spotlight Portrait

Image and text side by side with a portrait (square or tall) image. Drupal machine name: `content_spotlight_portrait`.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Heading** | Optional. Max 50 characters. |
| **Heading Level** | Select: H1 (page title hidden) / H2 (page title shown) |
| **Image** | Required image entity |
| **Caption** | Optional image caption. Max 90 characters. |
| **Subheading** | Optional. Max 50 characters. |
| **Content** | Required rich text body. Max 650 characters. |
| **Link** | Primary CTA — URL + link text |
| **Secondary Link** | Secondary CTA — URL + link text |
| **Theme** | Color swatch picker — Default - No Color / One through Five |
| **Image Position** | Select: Image Left / Image Right |
| **Image Style** | Select: Inline / Offset |
| **Vertical Alignment** | Select: Top / Middle / Bottom |
| **Padding Options** | See above |

---

### ✅ Content Spotlight Landscape

Like Portrait but with a wide landscape image. Drupal machine name: `content_spotlight`.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Heading** | Optional. Max 80 characters. |
| **Heading Level** | Select: H1 (page title hidden) / H2 (page title shown) |
| **Subheading** | Optional. Max 50 characters. |
| **Content** | Required rich text body. Max 600 characters. |
| **Caption** | Optional image caption. Max 90 characters. |
| **Image** | Required image entity |
| **Call-to-action** | Primary CTA — URL + link text |
| **Call-to-action Two** | Secondary CTA — URL + link text |
| **Theme** | Color swatch picker — Default - No Color / One through Five |
| **Image Position** | Select: Image Left / Image Right |
| **Image Size** | Select: Large / Medium |
| **Image Style** | Select: Inline / Offset |
| **Focus** | Select: Equal Focus / Image Focus |
| **Vertical Alignment** | Select: Top / Middle / Bottom |
| **Padding Options** | See above |

---

### ✅ Reference Card

Dynamically pulls content from an existing node and displays it as a styled card.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Reference source** | Entity reference — select a node (event, page, post, profile, resource) |
| **Show teaser lead-in** | Checkbox — show the content's teaser/lead-in text |
| **Style** | Select: Featured / Non-featured |
| **Padding Options** | See above |

---

## Main Content Area Blocks — Media

---

### ✅ Video

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Video Component Title** | Optional heading above the video |
| **Video Description** | Rich text description/caption |
| **Video** | Video media entity (via Media Library) |
| **Alignment** | Select: Left / Center |
| **Padding Options** | See above |

---

### ⚠️ Embed

An iframe embed block for third-party tools — forms, maps, calendars, audio players. Editors add embed content through the **Media Library** first (paste in embed code or URL), then the Embed block references that media entity.

**Important:** Yale no longer supports Qualtrics embeds. Do not recommend it.

---

### ✅ Gallery (Media Grid)

An interactive image grid that opens images in a lightbox/modal when clicked.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Gallery Component Title** | Heading above the gallery grid |
| **Images** | Paragraph sub-items — each is an image with caption |
| **Padding Options** | See above |

---

## Main Content Area Blocks — Navigation

---

### ✅ Link Grid

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Link Grid Component Title** | Heading above the grid |
| **Link Lists** | Paragraph sub-items — each is a list of links |
| **Line Treatment** | Select: Default / All Strong Lines / All Light Lines / No Lines |
| **Theme** | Color swatch picker |
| **Padding Options** | See above |

---

### ✅ Quick Links

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Quick Links Component Title** | Heading above the links |
| **Quick Link Content** | Rich text description |
| **Links** | Multiple link fields (URL + link text) |
| **Image** | Optional image entity reference |
| **Padding Options** | See above |

---

### ✅ Button Link

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Button Link** | Link field — URL + link text |
| **Button Alignment** | Select: Left / Center / Right |
| **Button Style** | Select: Both Filled / Both Outline / Filled+Outline / Outline+Filled |
| **Padding Options** | See above |

---

## Main Content Area Blocks — Collections

---

### ✅ Facts & Figures

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Facts and Figures Block Title** | Heading above the collection |
| **Content** | Rich text body/description |
| **Image** | Optional image |
| **Facts and Figures Items** | Paragraph sub-items — each has a number and label |
| **Theme** | Color swatch picker |
| **Alignment** | Select: Left / Center |
| **Columns** | Select: Two / Three / Four — grid column count |
| **Padding Options** | See above |

---

### ✅ Custom Cards

The platform's custom card collection block. Drupal machine name: `custom_cards`. **Note:** There is no separate "Card Collection" block type — this is the only card block.

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Custom Cards Component Title** | Optional heading above the cards. Max 50 characters. |
| **Cards** | Paragraph sub-items — each card is a `custom_card` paragraph |
| **Padding Options** | See above |

---

### ✅ Tiles

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Tiles** | Paragraph sub-items — each tile is a `tile` paragraph |
| **Columns** | Select: Two / Three / Four — grid column count |
| **Alignment** | Select: Left / Center / Right |
| **Content Position** | Select: Top / Bottom — position of text relative to tile image |
| **Enable Animation** | Checkbox — enables entrance animation |
| **Padding Options** | See above |

---

## Dynamic Views Blocks

Views blocks are configured entirely in the Layout Builder. See `references/views-reference.md` for the full configuration guide.

---

### ✅ Event Calendar

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **Event Calendar Title** | Heading above the calendar |
| **Links** | CTA links (paragraph sub-items) |
| **Basic params** | Custom field — stores event calendar filter configuration |

---

### ✅ Resource View

| Drupal Field Label | Notes |
|---|---|
| **Administrative label** | Internal block title |
| **View Heading** | Heading above the resource listing |
| **View Resource Params** | Custom field — stores JSON-encoded filter configuration for the View |
| **Padding Options** | See above |
