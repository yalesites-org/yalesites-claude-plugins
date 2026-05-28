# YaleSites Block Reference

All blocks available in the YaleSites Layout Builder, with their design options sourced from `*-props.yml` files in the `component-library-twig` repository. These are the authoritative design options — they drive both Storybook controls and Drupal block configuration.

**Component Theme (dial)** appears on most blocks. Options are always: `default`, `one`, `two`, `three`, `four`, `five` — mapping to the site's Global Theme palette via design tokens.

---

## Banner Area Blocks

Only one banner block can be placed at a time in the Banner region.

---

### Grand Hero

The largest, most prominent banner. Full-width with a background image or color and optional overlay content.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Required |
| `snippet` | HTML | — | Supporting body text |
| `linkContent` | string | — | Primary CTA label |
| `linkContentTwo` | string | — | Secondary CTA label |
| `bgColor` | select | `one` `two` `three` `four` `five` | Background color |
| `overlayVariation` | select | `contained` `contained-narrow` `full` | How text/content is positioned over image |
| `size` | select | `reduced` `full` `mini` | Height of the hero |
| `withVideo` | boolean | true/false | Show a background video instead of image |

---

### Action Banner

A prominent banner designed for calls to action. Supports two buttons with layout controls.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Required |
| `snippet` | HTML | — | Supporting body text |
| `linkContent` | string | — | Primary link/CTA label |
| `linkContentTwo` | string | — | Secondary link/CTA label |
| `bgColor` | select | `one` `two` `three` `four` `five` | Background color |
| `overlayBackgroundImage` | boolean | true/false | Whether a background image has a color overlay |
| `linkStyle` | select | `cta` `text-link` `none` | Button style |
| `contentLayout` | select | `bottom` `left` `right` | Position of text/CTA content over the image |
| `buttonAlignment` | select | `left` `center` `right` | How buttons are aligned |
| `buttonStyleConsistency` | select | `mixed` `both_primary` `both_secondary` | Whether both buttons share the same style |

---

### Image Banner

A simpler banner — primarily image-driven with minimal content controls.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `bgColor` | select | `one` `two` `three` `four` `five` | Background color (for fallback / overlay) |
| `size` | select | `tall` `short` | Banner height |
| `withVideo` | boolean | true/false | Show a video instead of image |
| `imageCaption` | string | — | Caption text below or over the image |

---

### Video Banner

A full-width banner driven by an embedded or background video.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `width` | select | `max` `full` | Container width of the video |

---

## Main Content Area Blocks — Text & Content

---

### Accordion

Collapsible content sections. Each accordion item has its own heading and body. Ideal for FAQs.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Required — group heading above the accordion |
| `content` | string | — | Required — content per item |
| `accordionHeading` | string | — | Optional secondary group heading |
| `themeColor` | select | `default` `one` `two` `three` `four` `five` | Accent color for the accordion bars |
| `accordionItems` | array | — | Each item has its own heading + content |

---

### Callout

A visually distinct text block — good for highlighting a key message or quote-style content.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Callout headline |
| `text` | string | — | Body text |
| `linkText` | string | — | CTA label |
| `linkType` | select | `cta` `link` | Button vs. text link style |
| `backgroundColor` | select | `one` `two` `three` `four` `five` | Background fill color |
| `calloutAlignment` | select | `left` `center` | Text alignment |
| `overlayBackgroundImage` | boolean | true/false | Apply a color overlay on a background image |

---

### Inline Message

An informational or marketing callout block — can appear within the content flow.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `type` | select | `general` `marketing` | Affects visual treatment |
| `heading` | string | — | Block heading |
| `content` | HTML | — | Body content |
| `themeColor` | select | `one` `two` `three` `four` `five` | Accent color |
| `linkContent` | string | — | CTA label |
| `linkUrl` | string | — | CTA destination URL |

---

### Quote Callout

A styled pull-quote block. Three visual styles plus optional image.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `quote` | HTML | — | Required — the quote text |
| `attribution` | string | — | Quote author/source |
| `style` | select | `default` `bar` `quote` `image` | Visual treatment: default (no decoration), bar (accent bar), quote (large quote marks), image (with portrait) |
| `alignment` | select | `left` `right` | Quote text alignment |
| `withImage` | boolean | true/false | Only applies when `style` = `image` |

---

### Tabs

A tabbed interface where each tab contains independently authored content.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `tabsTheme` | select | `one` `two` `three` `four` `five` | Color accent for the tab bar (no `default` option — one through five only) |

Each tab panel's content is authored separately in the CMS. The number of tabs is determined by how many tab items are added.

---

### Text with Wrapped Image (Wrapped Image)

Inline image floated or offset alongside running text — good for editorial content.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `caption` | HTML | — | Image caption |
| `imageAlignment` | select | `left` `right` | Which side the image floats to |
| `imageStyle` | select | `floated` `offset` | `floated` = text wraps around image; `offset` = image shifts outside the content column |

---

### Text with Wrapped Callout (Wrapped Callout)

Similar to Wrapped Image but replaces the image with a styled callout box that wraps alongside body text.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `calloutAlignment` | select | `left` `right` | Which side the callout box appears on |
| `calloutContent` | HTML | — | The main body text (the wrapping text) |
| `calloutText` | HTML | — | The content inside the callout box |
| `themeColor` | select | `default` `one` `two` `three` `four` `five` | Callout box accent color |

---

## Main Content Area Blocks — Spotlights

Spotlight blocks feature a single piece of content prominently — often a person, story, or featured item — with an image and text side-by-side.

---

### Content Spotlight Portrait

Image and text side-by-side with a portrait (square or tall) image orientation.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `componentTheme` | select | `default` `one` `two` `three` `four` `five` | Background/accent color |
| `position` | select | `image-left` `image-right` | Which side the image appears on |
| `contentVerticalAlignment` | select | `top` `middle` `bottom` | Vertical alignment of text relative to image |
| `imageStyle` | select | `inline` `offset` | `inline` = image sits within container; `offset` = image bleeds outside |
| `overline` | string | — | Small label text above the heading |
| `heading` | string | — | Required — main headline |
| `subheading` | string | — | Optional sub-headline |
| `text` | string | — | Body text |
| `linkContent` | string | — | Primary link label |
| `linkTwoContent` | string | — | Secondary link label |
| `caption` | string | — | Image caption |

---

### Content Spotlight Landscape

Like Portrait but with a landscape (wide) image orientation. Also called "Text with Image" in the component library.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `componentTheme` | select | `default` `one` `two` `three` `four` `five` | Background/accent color |
| `width` | select | `site` `highlight` | Container width — `highlight` is narrower/inset |
| `position` | select | `image-left` `image-right` | Which side the image appears on |
| `contentVerticalAlignment` | select | `top` `middle` `bottom` | Vertical alignment of text |
| `imageStyle` | select | `inline` `offset` | Image bleed behavior |
| `focus` | select | `image` `equal` | Whether the image or text takes visual emphasis |
| `overline` | string | — | Small label text above heading |
| `heading` | string | — | Required — main headline |
| `subheading` | string | — | Optional sub-headline |
| `text` | string | — | Body text |
| `linkContent` | string | — | Primary link label |
| `linkTwoContent` | string | — | Secondary link label |
| `caption` | string | — | Image caption |

**Difference from Portrait:** Landscape uses wider images and has the additional `focus` and `width` options. Portrait is better for headshots and people-focused content; Landscape for editorial/story content.

---

## Main Content Area Blocks — Media

---

### Video

An embedded video block (YouTube, Vimeo, or other supported platforms via oEmbed).

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Optional title above the video |
| `text` | string | — | Optional caption/description below |
| `placement` | select | `left` `center` | Video alignment within its container |

---

### Embed

An iframe embed block for third-party tools — forms, maps, calendars, audio players.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `width` | select | `max` `site` `highlight` `content` | Container width from fullest to narrowest |
| `type` | select | `form` `audio` `map` `calendar` | Type of embed; affects height and styling behavior |
| `loading` | select | `lazy` `eager` | iframe loading strategy |

**Common use cases:** Qualtrics forms, Google Maps, Spotify embeds, Yale Events calendar iframes.

---

### Gallery (Media Grid)

An interactive image grid that opens images in a lightbox/modal when clicked. No design options exposed via props — gallery appearance is driven entirely by the images added and the automatic grid layout.

**Notes:** Powered by the `media-grid` organism in the component library. Supports image captions and titles in the modal view. Built with full keyboard accessibility and focus management.

---

## Main Content Area Blocks — Navigation

---

### Link Grid

A grid of links — useful for "quick access" navigation sections or topic indexes.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `themeColor` | select | `one` `two` `three` `four` `five` | Accent color for the grid |
| `lineTreatment` | select | `default` `all_strong_lines` `all_light_lines` `no_lines` | Whether divider lines appear between links and how strong they are |

---

### Quick Links

A compact, scannable list of links — often used in sidebars or as a "related links" section.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Section heading above the links |
| `description` | string | — | Optional descriptor below the heading |
| `withImage` | boolean | true/false | Show a thumbnail image next to each link |

---

## Main Content Area Blocks — Collections

Collection blocks display multiple items in a structured layout. They are most powerful when combined with Views for dynamic content.

---

### Card Collection

The primary multi-card layout block. Displays a set of cards with configurable layout style.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Section heading above the cards |
| `collectionType` | select | `grid` `list` `condensed` | `grid` = card grid; `list` = horizontal list rows; `condensed` = compact text-only list |
| `featured` | boolean | true/false | First card is larger/featured |
| `withOverlay` | boolean | true/false | Show a "Pinned" badge on featured content |
| `withImages` | boolean | true/false | Whether card images are displayed |

---

### Custom Card Collection

Similar to Card Collection but uses the Global Theme lever (site-level theme) rather than the per-component dial.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `globalTheme` | — | — | Pulls from site Global Theme lever, not a per-block selection |
| `customCardCollectionHeading` | string | — | Section heading |
| `featured` | boolean | true/false | First card featured/larger |
| `withImage` | boolean | true/false | Whether images are shown on cards |

---

### Reference Card

The card component used within card collections and Views-powered listings. Exposed as a configurable block pattern.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `heading` | string | — | Required — card title |
| `snippet` | string | — | Descriptive text below heading |
| `collectionType` | select | `grid` `list` `condensed` `single` | Layout context (also `single` for standalone use) |
| `featured` | boolean | true/false | Featured layout style |
| `withImage` | boolean | true/false | Display an image |
| `showEyebrow` | boolean | true/false | Show eyebrow label above heading |
| `eyebrow` | string | — | Eyebrow text (visible when `showEyebrow` is true) |
| `showCategories` | boolean | true/false | Show category/affiliation tags |
| `showTags` | boolean | true/false | Show taxonomy tags |

---

### Tiles

A structured grid of items — typically used for feature lists, service offerings, or icon-based navigation.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `presentationStyle` | select | `heading` `icon` `text-only` | Whether tiles show a heading, an icon, or text only |
| `alignment` | select | `left` `center` `right` | Text/content alignment within tiles |
| `verticalAlignment` | select | `top` `bottom` | Vertical content alignment |
| `columnCount` | select | `two` `three` `four` | Number of columns in the grid |
| `image` | boolean | true/false | Whether tiles have a background image |
| `withAnimation` | boolean | true/false | Enable entrance animation on scroll |

---

### Facts & Figures

A structured block for displaying statistics, numbers, or key data points.

**Design options:**
| Option | Type | Values | Notes |
|---|---|---|---|
| `themeColor` | select | `one` `two` `three` `four` `five` | Accent color |
| `factsAndFiguresGroupHeading` | string | — | Section heading |
| `factsAndFiguresGroupContent` | string | — | Supporting text |
| `factsAndFiguresGroupLink` | string | — | CTA link |
| `image` | boolean | true/false | Background image behind the facts |
| `presentationStyle` | select | `basic` `icon-only` | `basic` = with a decorative line; `icon-only` = icon without line |
| `fontStyle` | select | `normal` `numeric-oldstyle` | `numeric-oldstyle` uses oldstyle figures for a more refined typographic feel |
| `columnCount` | select | `two` `three` `four` | Number of fact columns |
| `alignment` | select | `left` `center` | Content alignment |
| `iconName` | select | (from icon registry) | Icon shown per fact item |

---

## Views-Powered Blocks

Views blocks are dynamic — they query the CMS database and display matching content automatically. They are placed in the Layout Builder like any other block, but their content updates as nodes are created/updated.

Two modules handle Views:

**`ys_views_basic`** — Simple listings. Good for: recent posts, upcoming events, featured people.

**`ys_views_content_resources`** — Advanced content resource listings with more filter/sort/display options.

The design options for Views blocks are configured in Drupal Views administration (Structure → Views), not in the Layout Builder block config panel. Each View exposes a display plugin (page, block, attachment) with its own path, format, and exposed filters.

See `references/views-reference.md` for detailed Views configuration guidance.

---

## Block Selection Guide

| User Goal | Recommended Block |
|---|---|
| Big homepage hero with CTA button | Grand Hero or Action Banner |
| Simple image at top of page | Image Banner |
| FAQ section | Accordion |
| Highlight a quote | Quote Callout |
| Feature a person or story with image | Content Spotlight Portrait or Landscape |
| Side-by-side image + text (editorial) | Content Spotlight Landscape |
| Image floating in text | Wrapped Image |
| List of links / quick nav | Quick Links or Link Grid |
| Stats and data points | Facts & Figures |
| Features/services in a grid | Tiles |
| News/event card listing | Card Collection + Views |
| Photo gallery | Gallery |
| Embed a form or map | Embed |
| Tabbed content sections | Tabs |
| Pull a quote with styling | Quote Callout |
| Video (YouTube/Vimeo) | Video |
