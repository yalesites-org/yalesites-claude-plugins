# Block usage across the live portfolio (2026-10 crawl: 296 sites, 48,285 pages)

**What the columns measure.** Adoption (`% sites`, `Sites`, `Instances`) counts every rendered instance on all 48,285 crawled pages. The position columns, and the "typically preceded by / followed by" lines in the per-block detail, use only built Page-type pages (21,824 pages; event, post, profile and resource detail pages are field-driven and excluded):

- `Median/page`: median instances of the block on the pages where it appears.
- `Avg position`: mean relative index of each instance, 0 = first block on the page, 1 = last.
- `Opens page %` and `Closes page %`: share of the pages containing the block where it is the page's first or last block. The base is pages, not instances.
- Preceded by / followed by counts are per instance: every instance after a page's first block adds one to the count for the block in front of it. So a block can open 100% of its pages and still be "preceded by" something when a page carries it twice (Grand Hero: 57 stacked heroes on 32 pages).

Variants are the rendered design-option attributes, counted over all instances.

`Top sites` names the five sites with the most instances of the block, as `site (count)`, computed from the `block_counts` column of `sites-index.csv` by exact block token (so `image` never picks up `wrapped_image`). Read that line instead of grepping the CSV.

**Two count bases, one crawl.** The adoption table and the per-block instance totals are the 2026-10 snapshot. `block_counts` in `sites-index.csv` (and so the `Top sites` lines) were computed from the raw data after a monthly refresh that re-fetched anthropology and negeobio2024, so summing `block_counts` for a block can land under the table total by under 1% (Text 78,239 vs 78,312; Divider 7,137 vs 7,169 is the widest gap). Cite the table for totals and `block_counts` for per-site ranking.

## Adoption table

| Block | % sites | Sites | Instances | Median/page | Avg position | Opens page % | Closes page % |
|---|---|---|---|---|---|---|---|
| Text | 99.0% | 293 | 78,312 | 1.0 | 0.62 | 33.6 | 84.0 |
| Image | 81.8% | 242 | 7,130 | 1.0 | 0.24 | 49.9 | 5.2 |
| Wrapped Image | 79.1% | 234 | 8,439 | 1.0 | 0.2 | 78.9 | 51.9 |
| Divider | 76.4% | 226 | 7,169 | 1.0 | 0.42 | 10.7 | 4.5 |
| View | 70.3% | 208 | 5,160 | 1.0 | 0.79 | 18.1 | 99.0 |
| Callout | 69.3% | 205 | 2,347 | 1 | 0.21 | 27.3 | 1.0 |
| Button Link | 68.9% | 204 | 5,479 | 1 | 0.4 | 16.5 | 18.9 |
| Grand Hero | 68.2% | 202 | 2,968 | 1.0 | 0.0 | 100.0 | 0.7 |
| Accordion | 67.6% | 200 | 3,414 | 1 | 0.08 | 51.9 | 0.0 |
| Spotlight - Landscape | 57.8% | 171 | 4,873 | 1.0 | 0.35 | 33.6 | 13.5 |
| Custom Cards | 57.8% | 171 | 2,295 | 1 | 0.19 | 43.4 | 6.4 |
| Action Banner | 51.7% | 153 | 1,103 | 1 | 0.02 | 92.6 | 0.9 |
| In-Line Message | 48.0% | 142 | 833 | 1.0 | 0.87 | 3.6 | 69.5 |
| Spotlight - Portrait | 46.3% | 137 | 2,093 | 1.0 | 0.4 | 33.5 | 20.5 |
| Media Grid | 43.6% | 129 | 499 | 1 | 0.24 | 47.3 | 8.7 |
| Quick Links | 40.9% | 121 | 1,317 | 1.0 | 0.1 | 44.2 | 1.3 |
| Gallery | 40.2% | 119 | 1,342 | 1 | 0.09 | 50.3 | 0.0 |
| Quote | 39.5% | 117 | 999 | 1.0 | 0.16 | 46.7 | 0.4 |
| Video | 36.5% | 108 | 1,774 | 1 | 0.28 | 36.6 | 17.8 |
| Image Banner | 36.5% | 108 | 813 | 1 | 0.01 | 95.9 | 0.3 |
| Pre-Built Form | 29.4% | 87 | 125 | 1 | 0.99 | 0.0 | 92.8 |
| Post Feed | 25.3% | 75 | 112 | 1.0 | 0.71 | 28.6 | 100.0 |
| Link Grid | 24.7% | 73 | 780 | 1.0 | 0.16 | 52.8 | 3.8 |
| Tiles | 24.0% | 71 | 324 | 1.0 | 0.87 | 3.5 | 65.4 |
| Quote Callout | 16.6% | 49 | 381 | 1.0 | 0.29 | 21.8 | 6.5 |
| Calendar List | 15.9% | 47 | 66 | 1.0 | 0.88 | 12.1 | 100.0 |
| Embed | 15.5% | 46 | 260 | 1.0 | 0.28 | 29.7 | 21.1 |
| Facts and Figures | 12.8% | 38 | 226 | 1 | 0.14 | 19.8 | 1.9 |
| Tabs | 12.2% | 36 | 172 | 1 | 0.13 | 26.0 | 0.0 |
| Wrapped Text Callout | 10.8% | 32 | 342 | 1.0 | 0.21 | 50.0 | 14.1 |
| Reference Card | 10.5% | 31 | 250 | 1 | 0.26 | 20.8 | 3.4 |
| Directory | 9.5% | 28 | 58 | 1.0 | 0.8 | 19.6 | 100.0 |
| Resource View | 6.4% | 19 | 57 | 1.0 | 0.13 | 53.8 | 11.5 |
| Event Calendar | 6.1% | 18 | 43 | 1.0 | 0.71 | 26.2 | 85.7 |
| Video Banner | 4.1% | 12 | 132 | 1 | 0.02 | 85.8 | 0.0 |
| Related Content | 1.0% | 3 | 26 |  |  |  |  |
| Audio Player | 0.3% | 1 | 1 | 1 | 0.0 | 100.0 | 0.0 |

## Per-block detail

### Text (`text`) - 99.0% of sites, 78,312 instances
- Variants: component-width: site 87%, content 13%; component-alignment: left 52%, center 48%; component-variation: default 98%, emphasized 2%
- Typically preceded by Text (44715), Divider (2725), Image (1599); followed by Text (44715), View (1712), In-Line Message (613)
- Top sites: ism (5,518), your (5,353), poorvucenter (2,610), ezrastiles (1,922), college (1,514)

### Image (`image`) - 81.8% of sites, 7,130 instances
- Variants: component-width: site 62%, content 38%; component-alignment: left 62%, center 38%
- Typically preceded by Image (2756), Wrapped Image (346), Callout (133); followed by Image (2756), Text (1599), Button Link (418)
- Top sites: your (981), forms-sis (442), chem (293), isps (243), conferencesandevents (236)

### Wrapped Image (`wrapped_image`) - 79.1% of sites, 8,439 instances
- Variants: component-width: site 52%, content 48%; wrapped-image-style: offset 67%, floated 33%; wrapped-image-alignment: left 64%, right 36%
- Typically preceded by Wrapped Image (2807), Callout (201), Accordion (165); followed by Wrapped Image (2807), Text (596), Image (346)
- Top sites: ism (1,007), mcdb (286), isps (272), statistics (232), chem (226)
- Reviewer notes: Wrapped Image works best when text is moderate in length and the image is the thing being discussed. Avoid placing it before lists or very short text, because the wrap leaves gaps or awkward line breaks. Content width keeps line length readable, and the site width option leaves large empty areas on the right at wide screens. Screenshot coverage was partial for some sites (several images would not load).

### Divider (`divider`) - 76.4% of sites, 7,169 instances
- Variants: divider-width: 100 82%, 75 13%, 50 5%
- Typically preceded by Divider (3528), Button Link (699), Image (372); followed by Divider (3528), Text (2725), View (101)
- Top sites: your (305), conferencesandevents (295), ezrastiles (284), ehs (283), peabody (258)

### View (`view`) - 70.3% of sites, 5,160 instances
- Variants: component-width: site 93%, content 7%
- Typically preceded by Text (1712), View (1361), Divider (101); followed by View (1361), Calendar List (9), Event Calendar (8)
- Top sites: wlab (338), your (303), ism (293), chem (252), physics (178)
- Reviewer notes: The View is on 70% of sites, so consistency matters. Pick the card, list or profile style that matches the content type, keep item counts to full rows, and make sure every item has a usable image or none do. Check thumbnails: screenshots, flyers and logos look poor when cropped to a landscape card.

### Callout (`callout`) - 69.3% of sites, 2,347 instances
- Variants: component-theme: one 50%, two 23%, five 12%; component-width: site 99%, content 1%; component-alignment: center 99%, left 1%
- Typically preceded by Accordion (401), Custom Cards (296), Grand Hero (279); followed by Text (623), Spotlight - Landscape (434), Callout (264)
- Top sites: poorvucenter (265), your (143), yalesites (101), usability (52), physics (49)
- Reviewer notes: Callout is the platform's workhorse CTA band: 99% of instances use the site-width, centered layout. It works best as a short heading, one sentence, and one or two buttons. Use the two-up variant only for parallel content of similar length, and prefer solid theme colors over image backgrounds unless the overlay is strong. Review that button text makes sense out of context.

### Button Link (`button_link`) - 68.9% of sites, 5,479 instances
- Typically preceded by Button Link (997), Spotlight - Landscape (450), Image (418); followed by Text (1378), Button Link (997), Divider (699)
- Top sites: ets (804), onha (241), registrar (240), ism (235), physics-engineering-biology (211)

### Grand Hero (`grand_hero`) - 68.2% of sites, 2,968 instances
- Variants: grand-hero-overlay-variation: contained 70%, full 21%, contained-narrow 8%; grand-hero-size: reduced 71%, full 24%, mini 5%; component-theme: one 84%, two 6%, five 4%; grand-hero-width: site 99%, full 1%
- Every built page that contains a Grand Hero opens with one; the only block ever found in front of a Grand Hero is another Grand Hero (57 stacked instances on 32 pages). Followed by Quick Links (432), Custom Cards (430), Text (397)
- Top sites: poorvucenter (279), postdocs (170), conferencesandevents (106), onha (101), housing (100)
- Reviewer notes: Grand Hero works best as a short statement, not a content container. The overlay variants (contained panel vs full tint) matter more than size: opaque contained panels survive any image, while full tints and translucent panels often hurt legibility. Video heroes need a pause control, and should carry a real headline. Sites that repeat one configuration across a section look the most polished.

### Accordion (`accordion`) - 67.6% of sites, 3,414 instances
- Variants: component-width: site 94%, content 6%; component-alignment: left 94%, center 6%; component-theme: default 69%, three 13%, one 11%
- Typically preceded by Accordion (1211), Quick Links (296), Grand Hero (287); followed by Accordion (1211), Text (720), Callout (401)
- Top sites: your (277), poorvucenter (198), ism (185), onha (171), up (145)
- Reviewer notes: On 68% of sites. Default width is site-wide; the stronger usages keep to a single theme per page and a heading above each group. Avoid one-item accordions and titles that merely restate the heading. Hide only content that is not needed by most readers.

### Spotlight - Landscape (`content_spotlight`) - 57.8% of sites, 4,873 instances
- Variants: component-focus: equal 96%, image 4%; image-position: image-left 68%, image-right 32%; component-width: site 56%, highlight 44%; component-theme: default 71%, two 11%, one 10%; image-style: inline 58%, equal 33%, offset 7%; content-vertical-align: top 82%, middle 18%, bottom 0%
- Typically preceded by Spotlight - Landscape (2397), Callout (434), Custom Cards (170); followed by Spotlight - Landscape (2397), Text (718), Button Link (450)
- Top sites: wlab (459), college (305), poorvucenter (288), registrar (280), cqdmqd (225)
- Reviewer notes: Spotlight Landscape works best as a single focused story or call-to-action, one block at a time. Pick the theme and image side on purpose rather than leaving the default. It is easy to turn it into a text dump or a link list, which loses the visual impact. Screenshot coverage was partial for some sites (several images would not load), so rankings lean on the instances that could be viewed.

### Custom Cards (`custom_cards`) - 57.8% of sites, 2,295 instances
- Variants: collection-featured: false 100%; component-width: site 100%
- Typically preceded by Custom Cards (444), Grand Hero (430), Action Banner (261); followed by Custom Cards (444), Text (364), Divider (334)
- Top sites: ehs (319), conferencesandevents (167), poorvucenter (152), planetarysolutions (127), your (108)
- Reviewer notes: Custom Cards shine in rows of three or four with images of matching crop and short, parallel copy. Trim descriptions so they do not truncate, and pick row counts that fill the grid. For long lists, consider a different block; the cards become hard to scan beyond about eight.

### Action Banner (`cta_banner`) - 51.7% of sites, 1,103 instances
- Variants: banner-content-layout: bottom 72%, left 18%, right 10%; banner-button-alignment: right 72%, left 28%; banner-button-style-consistency: mixed 100%; component-theme: one 79%, three 8%, two 6%; banner-width: site 100%, full 0%
- Typically preceded by Grand Hero (48), Action Banner (45), Image Banner (30); followed by Custom Cards (261), Quick Links (138), Text (131)
- Top sites: planetarysolutions (144), recreation (71), peabody (61), geospatial (33), your (32)
- Reviewer notes: The banner works best as a single, specific call to action with one sentence of support. Choose a photo with a calm area for the text and always add a button; without one it is just a header image. Check that the image loads and that the title stays to two or three lines. Left and right layouts with a tinted panel read cleaner than bottom bars over busy photos.

### In-Line Message (`inline_message`) - 48.0% of sites, 833 instances
- Variants: component-width: site 100%; inline-message-type: general 100%; component-theme: one 55%, two 22%, three 14%
- Typically preceded by Text (613), In-Line Message (89), Tiles (37); followed by Pre-Built Form (125), View (96), In-Line Message (89)
- Top sites: housing (59), poorvucenter (58), your (56), yalesites (50), blueprint (37)
- Reviewer notes: Every instance uses the 'general' type with an info icon, so differentiation comes only from the theme colour, which is why colour choice matters most. Many sites use the block for informational text that would work as a plain Text block; it is best for short notices with one action. Watch contrast: light-blue and gold backgrounds need dark text, which these sites handle correctly. One instance uses a tree icon, so icon choice exists but is rarely used.

### Spotlight - Portrait (`content_spotlight_portrait`) - 46.3% of sites, 2,093 instances
- Variants: image-position: image-left 87%, image-right 13%; component-width: site 100%; component-theme: default 77%, one 10%, two 8%; image-style: inline 91%, offset 9%; content-vertical-align: middle 86%, top 12%, bottom 2%
- Typically preceded by Spotlight - Portrait (1319), Spotlight - Landscape (135), Wrapped Image (71); followed by Spotlight - Portrait (1319), Text (226), Divider (137)
- Top sites: morse (156), yan-chem (91), ehs (69), chaplain (52), rsl (52)
- Reviewer notes: The portrait variant is a good fit for people features, tributes and program cards, where a tall photo is the point. Always supply a portrait-shaped image. Landscape images get cropped awkwardly. Keep the text short, because the narrow image column makes long copy feel unbalanced. Screenshot coverage was partial for some sites (several images would not load).

### Media Grid (`media_grid`) - 43.6% of sites, 499 instances
- Variants: component-width: site 62%, content 38%; media-grid-variation: basic 100%
- Typically preceded by Media Grid (145), Wrapped Image (44), Gallery (23); followed by Media Grid (145), Text (113), Image (61)
- Top sites: ezrastiles (154), conferencesandevents (31), meng287 (21), gracehopper (20), yuqc (14)
- Reviewer notes: Media grid works best when the image count fills the row (4 across or a 2x2) and the photos share a similar aspect ratio. With 2 or 3 images the grid leaves empty columns, so consider a different block for small sets. Add a heading for context and avoid watermarked or low-resolution images. Note two Conferences & Events screenshots did not load, so that site was judged on two instances.

### Quick Links (`quick_links`) - 40.9% of sites, 1,317 instances
- Variants: quick-links-variation: promotional 100%; component-width: site 100%; component-theme: one 100%; quick-links-layout: stacked 51%, fluid 49%
- Typically preceded by Grand Hero (432), Action Banner (138), Quick Links (79); followed by Accordion (296), Custom Cards (189), Callout (164)
- Top sites: poorvucenter (102), onha (80), your (73), divinity (62), ism (62)
- Reviewer notes: Only the promotional variation is in use, so every instance is outlined white tiles on theme one (navy). Stacked puts the heading on top and tiles in a row; fluid puts the heading left and tiles in a 3-column grid on the right. In practice Quick Links opens the page or sits directly after the Grand Hero (432 of 1,317 instances follow a hero; average position 0.1; it closes a page 1.3% of the time), handing visitors their main tasks before any prose. It suits a short set of task links, not long lists. Keep labels parallel in length so tiles stay the same height.

### Gallery (`gallery`) - 40.2% of sites, 1,342 instances
- Variants: component-width: site 72%, content 28%; media-grid-variation: interactive 100%; media-grid-modal-state: inactive 100%
- Typically preceded by Gallery (400), Wrapped Image (170), Spotlight - Landscape (55); followed by Text (544), Gallery (400), Image (96)
- Top sites: ezrastiles (326), ism (120), conferencesandevents (77), geospatial (56), peabody (51)
- Reviewer notes: Known limitation: no exemplar guidance for Gallery yet. All 25 gallery screenshots failed to load in the review session (image reads returned no content), so no exemplars or anti-patterns are asserted; the maintainer tracks the re-run. The crawl data still holds: every gallery uses the interactive variation with the modal inactive, and about 72% are site-width.

### Quote (`pull_quote`) - 39.5% of sites, 999 instances
- Variants: component-width: site 72%, content 28%; pull-quote-style: bar-left 55%, quote-left 42%, bar-right 3%; component-theme: one 100%; component-alignment: left 72%, center 28%
- Typically preceded by Quote (223), Accordion (106), Callout (90); followed by Quote (223), Wrapped Image (147), Image (116)
- Top sites: ets (178), ismreview (117), usability (89), onha (66), isps (52)
- Reviewer notes: Quote is a text-only block with bar-left, bar-right, or quote-left styles and a left or center alignment. All instances use theme one, so the visual difference comes from style and width. Always add an attribution, keep it under a paragraph, and do not use the block for body text or lists.

### Video (`video`) - 36.5% of sites, 1,774 instances
- Variants: component-width: site 54%, content 46%; component-alignment: center 56%, left 44%
- Typically preceded by Video (418), Image (136), Wrapped Image (107); followed by Video (418), Text (400), Button Link (215)
- Top sites: ism (278), film (130), berkeleydivinity (107), your (81), cleanenergyconference (78)

### Image Banner (`image_banner`) - 36.5% of sites, 813 instances
- Variants: image-banner-overlay-variation: full 100%; image-banner-size: short 71%, tall 28%, mini 1%; component-theme: one 100%; image-banner-width: site 98%, full 2%
- Typically preceded by Grand Hero (31), Image Banner (31); followed by Text (121), Accordion (88), Spotlight - Landscape (76)
- Top sites: college (126), up (66), bands (28), your (26), hospitality (23)
- Reviewer notes: Image Banner has no text overlay, so the image is the only signal. It is best for interior pages where the title appears below it. Source images should be at least banner width and sharp; low-resolution uploads are the most common fault. Check mobile and tall variants, since subjects get cropped.

### Pre-Built Form (`webform`) - 29.4% of sites, 125 instances
- Variants: drupal-selector: webform-submission-contact-block-content-26-add-form 36%, webform-submission-contact-block-content-85-add-form 14%, webform-submission-contact-block-content-130-add-form 3%
- Typically preceded by In-Line Message (125); followed by View (6), Event Calendar (3)
- Top sites: plc (5), berkeleydivinity (4), recreation (4), tdps (4), urbanstudies (4)
- Reviewer notes: All 24 screenshots show the same fixed contact form (Your Name, Your Email, Subject, Message, Submit, plus a reCAPTCHA notice), so usages differ only in button and footer-notice colour. Inputs are narrow (about 400px) and left-aligned with a large empty area to the right, which looks unfinished in full-width sections. No usage stands out; the screenshots are cropped to the form so surrounding context could not be judged, and no exemplars are recommended.

### Post Feed (`post_list`) - 25.3% of sites, 112 instances
- Typically preceded by Text (43), Action Banner (11), View (8); followed by nothing (closes the page)
- Top sites: microbialsciences (6), yjil (5), biodiversitycredits (3), gleeclub (3), oiea (3)
- Reviewer notes: Post Feed output is mostly text lists, so quality comes from metadata and discipline: add images where they exist, write real teasers, and remove test or placeholder posts before publishing. Pick a filter only if readers will use it. Event feeds benefit from clear action buttons.

### Link Grid (`link_grid`) - 24.7% of sites, 780 instances
- Variants: component-theme: one 67%, two 17%, three 7%; component-width: site 99%, content 1%; line-treatment: default 79%, no_lines 7%, all_strong_lines 7%
- Typically preceded by Link Grid (288), Grand Hero (91), Action Banner (45); followed by Link Grid (288), Callout (94), Text (85)
- Top sites: your (240), college (46), admissions (36), hospitality (34), divinity (22)
- Reviewer notes: Link Grid is a text-only list of links in columns and the screenshots are tight crops, so judge them on structure rather than imagery. Line treatment options (default, no lines, strong, light) only change the accent and divider rules. Pick a column count that balances items, and add a heading since the block does not require one. It is best for indexes and resource lists, not one or two links.

### Tiles (`tiles`) - 24.0% of sites, 324 instances
- Variants: component-width: site 100%; component-tile-style: heading 100%; component-alignment: left 60%, center 40%; component-vertical-alignment: bottom 51%, top 49%; component-grid-count: three 47%, two 32%, four 20%; component-tiles-have-images: false 100%; component-tiles-have-animation: false 85%, true 15%
- Typically preceded by Text (229), Tiles (60), Divider (8); followed by Tiles (60), View (53), In-Line Message (37)
- Top sites: poorvucenter (50), marshbotanicalgarden (14), regulatedresearchdata (14), blueprint (12), chem (12)
- Reviewer notes: Tiles in these samples are overwhelmingly used as large link cards or button-like navigation, which works best with short headings and a one-line caption. Colour themes carry no inherent meaning, so vary them only when the items are genuinely distinct. Some sites (Marsh Botanical Garden) show background imagery on tiles even though the portfolio stats list tiles-have-images as false, so the stats may undercount or the screenshot may reflect a different config. Avoid putting long paragraphs inside tiles; they grow uneven and hard to scan.

### Quote Callout (`quote_callout`) - 16.6% of sites, 381 instances
- Variants: component-width: content 100%; quote-callout-style: image 75%, bar 13%, quote 12%; component-theme: one 50%, four 24%, two 12%; component-alignment: center 100%; quote-callout-quote-alignment: left 85%, right 15%
- Typically preceded by Quote Callout (124), Callout (83), Accordion (37); followed by Quote Callout (124), Spotlight - Landscape (62), Text (52)
- Top sites: poorvucenter (57), campyalearts (36), chaplain (27), divinity (24), zcafe (22)
- Reviewer notes: Quote Callout is a full-width band with optional image, so use it for testimonials with a face. Without an image, the Quote block is the lighter choice. Keep attribution tidy and make sure an image-style instance actually has an image; blank halves look broken.

### Calendar List (`event_list`) - 15.9% of sites, 66 instances
- Typically preceded by Text (44), View (9), Action Banner (2); followed by nothing (closes the page)
- Top sites: gleeclub (6), yso (6), bands (3), yaledancelab (3), ypa (3)
- Reviewer notes: Calendar List renders through the same list/card structure as Post Feed. Post Feed output is mostly text lists, so quality comes from metadata and discipline: add images where they exist, write real teasers, and remove test or placeholder posts before publishing. Pick a filter only if readers will use it. Event feeds benefit from clear action buttons. (Entries re-filed from the Post Feed review after the feed classifier was corrected.)

### Embed (`embed`) - 15.5% of sites, 260 instances
- Variants: embed-type: audio 60%, form 20%, map 9%
- Typically preceded by Embed (114), Image (17), Spotlight - Portrait (11); followed by Embed (114), Text (51), Divider (23)
- Top sites: whc (79), admissions (51), chaplain (15), your (11), silliman (7)
- Reviewer notes: Embeds depend on third-party content, so empty calendars, offline streams and blank Power BI frames can render poorly, and the block gives no fallback. Several screenshots may show frames before they finished loading. Page builders should check the embed in a logged-out browser and provide surrounding text for context and accessibility. Narrow containers truncate audio titles, so use a wider width.

### Facts and Figures (`facts`) - 12.8% of sites, 226 instances
- Variants: component-width: site 100%; component-grid-count: three 51%, four 38%, two 11%; facts-and-figures-style: basic 100%; facts-and-figures-has-icon: false 100%; component-alignment: left 60%, center 40%; component-theme: one 39%, two 36%, four 15%
- Typically preceded by Grand Hero (100), Action Banner (49), Facts and Figures (14); followed by Custom Cards (57), Quick Links (34), Accordion (22)
- Top sites: onha (33), planetarysolutions (19), admissions (17), yalesites (14), poorvucenter (13)
- Reviewer notes: Facts and Figures works best as a short summary band of three or four numbers with a heading and intro; the style is basic only across the portfolio, so the variety comes from theme, grid count and alignment. Icons appear in many captures even though the has-icon setting reads false, so check icon settings when copying. Avoid using it for taglines, thank-you notes or more than eight items. Keep numbers genuinely quantitative and current.

### Tabs (`tabs`) - 12.2% of sites, 172 instances
- Variants: overflow: none 100%; component-theme: one 100%
- Typically preceded by Accordion (42), Grand Hero (26), Tabs (22); followed by Text (38), Callout (28), Tabs (22)
- Top sites: french (21), enterprisemonitoring (20), your (16), rgvolunteers (13), poorvucenter (9)
- Reviewer notes: Only one theme and no overflow option is in use anywhere, so differences come from content. Tabs work best for a few short parallel panels; long labels or many tabs trigger the scroll arrow and hide content. Consider an accordion for long or numerous sections, especially on mobile.

### Wrapped Text Callout (`wrapped_text_callout`) - 10.8% of sites, 342 instances
- Variants: component-width: content 71%, site 29%; wrapped-callout-alignment: left 71%, right 29%; component-theme: three 61%, one 22%, two 14%
- Typically preceded by Wrapped Text Callout (31), Accordion (14), Callout (11); followed by Wrapped Text Callout (31), Image (23), Wrapped Image (17)
- Top sites: your (215), ismreview (17), poorvucenter (15), wwn (12), hospitality (10)
- Reviewer notes: Best for a single short, supporting point beside body text. Keep it brief; long content makes the box dominate and narrows the main column. Check where adjacent headings and lists land, since wrapped text can break lists oddly. Use a full-width Callout block instead for standalone messages. Demo content on yalesites.yale.edu shows intended usage but not a live-site model.

### Reference Card (`reference_card`) - 10.5% of sites, 250 instances
- Variants: collection-featured: true 62%, false 38%; collection-type: single 100%; component-width: site 100%; collection-source: page 50%, post 40%, resource 6%
- Typically preceded by Reference Card (101), Grand Hero (44), Custom Cards (32); followed by Reference Card (101), Callout (52), Text (18)
- Top sites: peabody (37), csoc (21), poorvucenter (21), ypsa (20), commencement (15)
- Reviewer notes: Reference Card is a featured-item block: the image drives the layout, so use a landscape photo with a focal point near the centre. Portrait or very tall images stretch the card and strand the text. Check descriptions for truncation. The overlapping panel needs a photo with enough room on the right.

### Directory (`directory`) - 9.5% of sites, 58 instances
- Typically preceded by Text (40), View (3), Spotlight - Landscape (2); followed by nothing (closes the page)
- Top sites: episonic (4), urbanstudies (3), bands (2), beingwell (2), biomechanics (2)
- Reviewer notes: The Directory block depends entirely on profile data quality. Fix photo crop and background consistency, fill in title and email for everyone, and keep bio text short. Use filters and pagination only for larger rosters, and avoid showing a Directory with one or two people.

### Resource View (`resource_view`) - 6.4% of sites, 57 instances
- Variants: component-width: site 100%
- Typically preceded by Custom Cards (8), Grand Hero (5), Link Grid (5); followed by Text (11), Callout (10), Accordion (7)
- Top sites: admissions (10), usability (8), tinsleyworkshop (5), ccs (4), isps (4)
- Reviewer notes: Resource View works best as a browseable library with consistent thumbnails, a type label and a date. Filters and search matter more as the list grows. Avoid it for one or two items, and make sure every item has a thumbnail or none do. Thumbnails of document pages are weak; use designed cover images.

### Event Calendar (`event_calendar`) - 6.1% of sites, 43 instances
- Variants: component-width: site 98%, content 2%
- Typically preceded by Text (16), View (8), Pre-Built Form (3); followed by View (5), Calendar List (1)
- Top sites: geospatial (4), isps (4), timothydwight (4), yalesites (4), onha (3)
- Reviewer notes: The calendar suits sites with steady event volume; sparse calendars look empty and a list may serve better. Event title quality matters most because cells are narrow. Consider filters when many categories exist, and keep multi-day or recurring items under control.

### Video Banner (`video_banner`) - 4.1% of sites, 132 instances
- Variants: component-width: max 100%; full-width-component:  100%
- Typically preceded by Image Banner (12), Grand Hero (6), Video Banner (2); followed by Text (102), Callout (4), Quick Links (4)
- Top sites: whc (101), divinity (9), carbon-elti (4), cultivatingconversation (4), ezrastiles (4)
- Reviewer notes: The block is a full-width embed, so it is huge on the page and the poster frame matters more than anything else. There is no overlay text, so editors cannot add a headline; put context in the page title or nearby text. Archive lectures and event recordings are better as a standard video block than as a banner. Add captions and avoid autoplay surprises.

### Related Content (`related_content`) - 1.0% of sites, 26 instances
- Variants: component-width: site 100%
- Top sites: isps (19), yalesites (4), ets (3)

### Audio Player (`audio`) - 0.3% of sites, 1 instances
- Variants: component-width: site 100%; component-alignment: left 100%
- Typically preceded by nothing (opens the page); followed by Text (1)
- Top sites: yalesites (1)

