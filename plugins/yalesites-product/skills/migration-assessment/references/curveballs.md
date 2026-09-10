# Curveballs, and how they are normally handled

The recurring "will not carry over cleanly" items, each with a suggested
handling. Never list one of these in an assessment without a suggestion, and
never present a suggestion as free when it is not.

## Content and structure

| Source pattern | Why it does not fit | Suggested handling |
|---|---|---|
| A content type with no YaleSites equivalent | Five fixed types, no new ones | Fold into `page` and carry the distinction in `field_category` or `field_tags`. If it has structured fields that matter, say what is lost. Never fold silently. |
| Long body HTML with `<div>` wrappers, inline `<img>`, embedded `<iframe>` | `basic_html` strips all of it | Rebuild as components. This is the single largest cost driver on a page-heavy site. Estimate per page, not in aggregate. `ys_migrate_onha`'s `BodyToLayoutBuilder` shows automation is possible, per-site and with custom code. |
| Deep sub-navigation (3+ levels) | Editors administer items in `main` and two utility menus only | Flatten, or use the book/collection feature on `page` for a nested section. Needs an IA decision before migration, not during. |
| Multiple custom navigation systems | Seven fixed menus | Map onto `main` plus the utility menus; anything left over becomes in-page navigation (Quick Links, Link Grid). |
| One-off bespoke page layouts | Six layouts with per-region allow-lists | Rebuild with the nearest layout. Homepages are almost always the one genuinely custom page — scope it separately from the content pages. |
| Translated content | No language module is installed at all | **Hard stop.** There is no target. Escalate before any other scoping. |
| Comments / forums / discussion | Modules absent | Not migrating. Confirm the site owner is fine losing the archive, or export it separately. |
| A large people directory | `profile` fits, but has no biography field | Structured fields via the shipped Profile CSV importer; every bio is a Layout Builder rebuild. Split the estimate accordingly. |
| Orphan or unfinished content | Invisible to a crawl; often placeholder text | Ask for an authenticated content report. Two Lorem-ipsum orphan pages turned up on the test site. |

## Interactive features

| Source pattern | Why it does not fit | Suggested handling |
|---|---|---|
| Carousel / slider / slideshow | No such component exists, deliberately | Gallery (grid + lightbox), Media Grid, or Tiles. Where the carousel held one image, an Image Banner. Expect this to be contested — it is the most common request. |
| Custom Webform forms | No role can create a webform | Rehost on Microsoft Forms or Qualtrics and use the matching `ys_embed` source. A simple contact form can use the single pre-built `contact` webform. Anything with routing, conditional logic, file upload, or payment needs an owner decision. |
| Externally hosted forms (Maxient, ServiceNow) | Fine — but check the embed allow-list | Qualtrics, Microsoft Forms and 25Live have embed sources. **Maxient and ServiceNow do not** — they stay outbound links, which is what they already are. |
| Gated / login-required content | Access is binary: public or any CAS-authenticated Yale user | `field_login_required`. If the source gated by role, group, or department, there is no equivalent — escalate. `ys_node_access`'s README disclaims it as a security boundary, so genuinely sensitive content does not belong on the platform. |
| Faceted / filtered search | The `view` component offers fixed sort options, not exposed filters | Taxonomy Display and separate view blocks per facet. A true faceted browse is not reproducible. |
| Embedded video from Panopto, Kaltura, Warpwire | media `video` is oEmbed YouTube/Vimeo only | Check the 13 `ys_embed` sources (`jwplayer`, `soundcloud`, `powerbi`, `google_calendar`, `google_maps`, social) — otherwise re-host or link out. |
| Maps | `google_maps` embed only, regex-validated | Google Maps embed, or link out. Mapbox, Leaflet, and ArcGIS have no path. |
| Site-wide custom CSS (CSS Injector and similar) | No custom-CSS surface exists | Nothing carries over. The `ys_themes` dials are the whole styling vocabulary. Show the site owner the dial options early — this is where expectations break. |
| SVG or GIF images | media `image` accepts `png jpg jpeg webp` | Convert. Animated GIFs need a decision (video, or drop the animation). |

## Events

Settle this before scoping anything else, because it changes the whole shape:

| Situation | Handling |
|---|---|
| Live events, actively maintained | Use the `ys_localist` integration rather than migrating nodes. Ongoing sync beats a one-time content move. |
| Historical event archive, no live feed | Native `event` nodes. No bulk importer exists yet (YaleSites-Internal#1231), so this is manual or a custom migration. Ask whether the archive needs to survive at all — often it does not. |
| Events imported from a retired system (Bedework) | Archive material by definition. Check the newest event date before treating it as live content. |
| Recurring events | `field_event_date` is a smartdate field and handles recurrence, but no importer expresses recurrence rules. Assume manual. |

## Migration mechanism options

The decision belongs to the lead developer (YaleSites-Internal#1561). The usual
answer is **a different mechanism per content bucket**, not one for the whole
site.

| Option | Fits | Cost / caveat |
|---|---|---|
| **`ys_migrate` + Migrate module from the source DB** | Large volumes; anything needing repeatable runs; body-to-Layout-Builder conversion | Needs a `d7` (or equivalent) DB connection in `settings.php` — **so it needs source database access, not just the public site**. Per-site custom code: `ys_migrate` carries three site-specific submodules. Precedent exists (`ys_migrate_onha`'s `BodyToLayoutBuilder`). |
| **The shipped CSV importers** | Profiles and Resources, today | Only those two content types ship an importer. Posts (#1230) and Events (#1231) are open and unbuilt. Field data only — never touches Layout Builder. Carries known tech debt (#1653). |
| **Feeds module** | Potentially a generic importer across content types | **Under evaluation, not adopted** (#1561). Not installed. Do not scope against it. |
| **Manual rebuild** | Small page counts; anything where the layout is the content | Honest and often cheapest under a few dozen pages. The test site's nine pages are firmly here. |

State which buckets you would route to which option and why.

## Curveball patterns worth testing the tool against next

The tool has been exercised on one site. These are the shapes most likely to
break it or the assessment method, and where to look for them:

| Pattern | Why it is a good next test | Where to look |
|---|---|---|
| A real Webform site | Forms are the most expensive finding and the detector has only been tested on a site with none | Any departmental site with an application or request form |
| A large people directory | Tests the profile mapping and the "bio is a rebuild" split at volume | A department or centre site with 50+ faculty and staff |
| Deep sub-navigation | Tests the nav extractor beyond `max_depth: 0` and the IA flattening advice | A school or programme site with a section nav on interior pages |
| A genuine carousel | The one test site's carousel drove a single image, so the "this is really a slider" path is untested | A site with a rotating homepage feature |
| Gated content | The gating detector has never fired | A site with CAS-restricted pages |
| A publications / Biblio site | Tests the `resource` mapping and the scholarly metadata fields; `naturalcarboncapture.yale.edu/publications` is already the test corpus for #1561 | `naturalcarboncapture.yale.edu` |
| A Drupal 8/9/10 source with JSON:API open | Every finding so far comes from a D7 site; a modern source should allow an exact inventory instead of a crawl estimate | Any recently built non-YaleSites Yale Drupal site |
| A non-Drupal source (WordPress) | The fingerprint returns `unknown` and every Drupal-specific signal goes silent — worth knowing how badly it degrades | Any Yale WordPress site |

Naming specific sites for the first five needs someone with the portfolio
inventory; the two named above are confirmed from ticket history.
