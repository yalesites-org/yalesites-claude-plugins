# YaleSites Paragraph Sub-Items Reference

Paragraph sub-items are the editable rows within certain blocks — accordion items inside an Accordion block, cards inside a Custom Cards block, etc. All field labels verified from `config/sync/` on the `develop` branch.

---

## accordion_item — Accordion Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Accordion Item Heading** | Yes | The clickable toggle header. Max ~80 characters recommended. |
| **Accordion Item Content** | Yes | The panel body — accepts a nested `text` paragraph type. |

---

## tab — Tabs Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Tab Heading** | Yes | The tab label shown in the tab bar. Max ~40 characters recommended. |
| **Tab Content** | No | The panel body — accepts a nested `text` paragraph type. |

---

## callout_item — Callout Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Callout Item Heading** | Yes | Max ~80 characters recommended. |
| **Callout Content** | No | Rich text body. Max 150 characters enforced. |
| **Link** | Yes | CTA link — URL + link text (link text required). |

---

## custom_card — Custom Cards Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Image** | No | Optional card image (from Media Library). |
| **Custom Card Heading** | Yes | Max ~80 characters recommended. |
| **Custom Card Content** | No | Rich text body. Max 175 characters enforced. |
| **Link** | Yes | Card link — URL only (no separate link text field; the heading becomes the link). |

---

## tile — Tiles Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Tile Heading** | No | Max ~80 characters recommended. |
| **Content** | No | Descriptive text. Max ~120 characters recommended. |
| **Image** | No | Optional tile image. |
| **Link** | No | Optional tile link — URL + optional link text. |
| **Theme** | Yes | Color swatch picker — One through Five (default: One). |

---

## facts_item — Facts & Figures Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Icon** | No | Select from a list of icons (see below). Default: None. |
| **Facts and Figures Item Heading** | Yes | The stat value itself, e.g. "42%" or "500+". Max ~80 characters. |
| **Content** | No | Descriptive label below the stat. Max ~120 characters recommended. |

**Available icons:** Atom, Bee, Bolt, Book, Calendar, Car Building, Chart Line, City, Cloud with Rain, Code, Dollar Sign, Droplet, Envelope, Flask, Frowning Face, Gears, Globe, Graduation Cap, Hand Holding Dollar, House Chimney, Industry Windows, Leaf, Lightbulb, Location Dot, Mountain with Sun, Pencil, People, Piggy Bank, Recycle, Rocket Launch, Smiling Face, Sun, Teacher, Temperature Sun, Tree, University, User, Wave Pulse.

---

## gallery_item — Gallery Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Image** | Yes | The gallery image (from Media Library). |
| **Gallery Item Heading** | No | Heading shown in the lightbox modal. Max ~80 characters. |
| **Gallery Image Caption** | No | Caption shown in the lightbox modal. Max ~200 characters. |

---

## link_list — Link Grid Block

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Link list heading** | No | Optional heading above this cluster of links. |
| **Links** | No | Multiple links — URL + optional link text. |

---

## cta_link — CTA Link (used across various blocks)

| Drupal Field Label | Required | Notes |
|---|---|---|
| **Link** | Yes | URL + required link text. |

**Where it's actually used.** Despite the generic name, `cta_link` is referenced by only two block bundles through the `field_heading_links` field: **View** (`block_content.view`) and **Events Calendar** (`block_content.event_calendar`). Other blocks that collect links do so through their own fields (`link_list` on Link Grid, the per-item `Link` fields on Callout/Custom Cards/Tiles), not through `cta_link`.

**Why the authoring form looks the way it does.** `field_heading_links` is an `entity_reference_revisions` field labelled **Links**, capped at 3 values, with exactly one allowed target bundle (`cta_link`) — and `cta_link` itself holds exactly one field. So it's a paragraph entity wrapping a single link. That's why the General tab of the View block form shows a full paragraphs widget (the "Links" table header, drag handles, collapsed summaries, Duplicate, and a delete-confirm modal) just to collect up to three links.

Paragraphs earns that complexity when a field allows multiple types or nesting. Neither applies here. If a request comes in to clean up this form, the relevant fact is that the storage is shared: `field_heading_links` config is per-bundle, so a change can technically be scoped to just the View block, but that leaves Events Calendar handling links differently from its sibling. Treat "which bundles does this change cover" as a scoping question to settle before the work is estimated, not a detail to leave to the implementer.

---

## Known Issues

**Quick Node Clone + Paragraph Items module interaction:** Cloning a node with the Quick Node Clone module can lock the *original* node's paragraph-backed sub-item blocks (Accordion, Gallery, Link Grid, and similar components built on paragraph sub-items) instead of locking the clone — the opposite of the expected behavior. If an editor reports a block that's suddenly stuck or uneditable shortly after cloning a page, check whether this is the cause.
