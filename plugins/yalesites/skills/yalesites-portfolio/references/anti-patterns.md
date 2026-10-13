# Anti-patterns per block (2026-10 review)

What goes wrong when each block is used badly, from the same screenshot review as exemplars.md. Sites are named so a reviewer can look; treat them as teaching examples, not call-outs. Use this when reviewing a page or advising a site builder; use exemplars.md for models to copy.

## Wrapped Image (`wrapped_image`)

- nextgen: A decorative 'NGN Completed 100%' graphic sits alone with a large empty area to its right, so the wrap has no text to flow around it.
- your: Images are placed inside lists, so list items wrap around the image and break awkwardly (LiveSafe phone mockup, shuttle photo). A generic Y-arrow logo as a filler image on the 'At a Glance' list adds nothing.
- chem: A small group photo is wrapped by a very long letter, producing a long gray text column with the image lost at the top.
- poorvucenter: Long testimonial text wraps under a large portrait so lines run unevenly, and the headings with degrees wrap onto 3 or 4 lines.

## View (`view`)

- your: Events view has no images, a cramped clock icon above wrapped dates, and the card text feels unbalanced; the same layout is repeated across 300 instances with little variation.
- yalesites: Release-notes list mixes low-resolution tiny screenshots, a logo and cropped images as thumbnails, so images are unreadable and inconsistent in size and style.
- chem: Single-item News block shows one huge featured row, and a profile row clips the person image at the top; list-style events with no images feel sparse.
- berkeleydivinity: Image cards mix text-heavy event flyers and a logo-on-white thumbnail; a raw URL in a teaser wraps awkwardly and the Add to Calendar button crowds the pagination.
- haji-akbari: Teasers with mixed content types: a scientific chart thumbnail, inconsistent title weight and an unevenly aligned 3-card row; the same news block is duplicated on several pages.

## Callout (`callout`)

- registrar: Truncated blurb ends mid-sentence ('for students, faculty,'); the walk-in hours callout stacks three address/hour lines as separate paragraphs and leaves a large gap above the button.
- physics: Two-up pair is inconsistent: the Lab Safety half has no blurb so its button sits higher than the EHS half; button labels are long and wrap awkwardly in the first pair.
- berkeleydivinity: Two identical 'Apply Now' button labels in one callout, and bare email addresses used as button text; light-gray bands give little emphasis for a primary admissions action.
- isps: Dark text over a busy, washed-out photo overlay (voting scene) reduces legibility and the long event heading wraps to two lines; the Directions and Contact Us buttons are generic.
- ccs: The same About Us callout is repeated on multiple pages, the heading has odd capitalization ('About US'), and the image overlay is so heavy the photo is just texture.

## Grand Hero (`grand_hero`)

- postdocs: Full-size hero holds three long paragraphs of body copy on a pale translucent panel. It reads as a text page, not a hero, and the photo is washed out.
- goodlifecenter: Heroes are used as narrative text slabs (multi-paragraph story, scripted dialogue) over a heavily darkened image. The image is nearly lost and the copy is hard to scan.
- geospatial: The 'Our History' hero is a flat blue pattern with a title and no photo, and the lab hero buries a large headline over a heavy blue tint. Weak visual payoff for hero space.
- oiea: Interior heroes use a heavy blue wash that makes the photos almost invisible (library, skyline), so the image adds little.
- registrar: The 'Welcome' video hero is full height with a tiny one-word panel; the video does not say anything about what the office does.

## Accordion (`accordion`)

- french: Single-item accordion whose title repeats the heading directly above it (Fall 2026 Undergraduate Courses); adds a click with no benefit.
- physics: Single-item accordions (List of Former Fellows) used as standalone links to content, and a mix of styles on one site.
- admissions: Two-item accordions with vague titles ('Academic potential') and mixed theme variants (dark navy, gray, plain) across pages hurts consistency.
- usability: Accordion with only three items on the homepage under a gray band, and several accent colors for no clear meaning.

## Spotlight - Landscape (`content_spotlight`)

- chem: Featured researcher spotlight on dark gray puts a long paper title and full author list in the body. The image is a busy figure with a portrait pasted over it, and the text becomes a dense wall of names.
- registrar: A low-resolution, blurry screenshot of a web app is used as the image, and there are several stacked bare links with no clear primary action.
- college: The cost estimator spotlight uses a small icon-style graphic with excess whitespace. The copy has a grammar slip ('easy to estimating') and the call-to-action appears cut off or missing.
- poorvucenter: The 'Student Supports' spotlight is a plain list of six bare links that would be better served by a link list or card block.

## Custom Cards (`custom_cards`)

- poorvucenter: The Summer Programs grid has 20 cards of imageless text with descriptions cut off mid-word ('al', 'appr', 'fr'), uneven card heights and many two-line arrow titles; it reads as a directory, not cards.
- your: Several rows have no images and uneven body copy; a card title wraps so the external arrow sits alone on its own line ('Share your thoughts. ↗').
- planetarysolutions: Event cards have wildly different title lengths (up to five lines) and only three cards fill a four-column row, leaving an empty gap; report cards are mixed in style.
- climateweek: Panelist cards leave one or two cards in a four-column row, with inconsistent headshot crops and no way for the grid to feel balanced.

## Action Banner (`cta_banner`)

- climateandhealth: Banner image failed to load, leaving a broken-image alt text in the top corner and a large empty navy area; the title is five lines long and crowds the button.
- planetarysolutions: Banners on the impact, programs and action-area pages have a title and sentence but no button at all, so they act as decorative headers rather than calls to action.
- french: The 'For Undergraduate Students' banner has a title only with no description or button, and the L'Amuse-Bouche banner places text over busy magazine covers, hurting legibility.
- geospatial: The Welcome banner uses a dense satellite image with only a newsletter button and no description; the same Earth Observation Lab banner is repeated on multiple pages.

## In-Line Message (`inline_message`)

- postdocs: Messages are used as generic link teasers ('Click here for more information' with a 'Salaries & Taxes' link) and the same salary message is repeated on several pages; the link text is vague and the message adds no information.
- physics: The lab-safety message renders its title as a huge heading that dwarfs the info icon and the link, which breaks the visual hierarchy; the 'Internal Pages' message is a link wrapped in a full-width navy bar.
- your: Used as a standard page footer (feedback/contact) and for a pasted legal blurb; the Clery Act text runs together ('Clery Act-A federal statute') and a long-running contact block does not need alert styling.
- yalesites: The grey 'Note' message mostly repeats its own link text ('Learn why at nngroup.com' twice), and the Drupal 7 archiving message mixes bold and regular text across four short paragraphs, which is heavy for a notice.
- admissions: The non-degree message has no title and is a four-line paragraph in a navy bar, making it look like body copy rather than a notice.

## Spotlight - Portrait (`content_spotlight_portrait`)

- yalesites: Demo pages use placeholder content (furniture store link lists with a tower photo) so the block is a link list rather than a spotlight, and the Ask AI button overlaps the image.
- ling: The identical Director of Graduate Studies spotlight is repeated across pages and the subhead, role and heading overlap ('Director of Graduate Studies' / name / 'Associate Professor & DGS'). It sits tight against the top edge with no padding.
- mcdb: The graduate handbook spotlight uses a plant stock photo and long body text with two links, which dilutes the call-to-action.

## Media Grid (`media_grid`)

- fortnerlab: Small, low-resolution phone snapshots in a thin single row with no heading or captions; looks like a filler strip and the crop is tight.
- fgli: Only two or three small images in a four-column row leaves a large empty right side, and the low-resolution snapshots feel unbalanced.
- campyalearts: Same thin single row of tiny images on the homepage; a lion statue pair appears on an events page that looks unrelated to the content.
- conferencesandevents: A two-photo row with a visible photographer watermark and an unfilled right half looks unfinished.
- silliman: Rows of 2 to 3 images float left with blank space on the right and no heading; the layout looks unbalanced.

## Quick Links (`quick_links`)

- divinity: Typos in the block ('Request Infomation', 'and and aid') plus contact details mixed into the intro area reduce polish and trust.
- ipch: All-caps one-word tiles (NEWS, EVENTS, CONTACT US, SUPPORT) under a slogan heading read as a generic menu with no context, and the same block repeats across pages.
- physics: Inconsistent labels ('Tutoring-Explore the Poorvu Center for teaching & Learning', 'Physics & Philosophy (B.A. or B.S.)') produce ragged multi-line tiles.
- divinity: Seven tile 'Social Media' grid mixes abbreviations (YMI, YBS, CCE) that outsiders will not understand.
- onha: Tile text 'Questions? Email yalepathways@yale.edu!' is an email address inside a button, which wraps awkwardly and is not a standard link.

## Quote (`pull_quote`)

- ismreview: Used to render long body excerpts and a list of scripture verses; several have no real attribution (a bare article text or newspaper name), so it works as a blockquote not a pull quote.
- beingwell: Large empty gap between a two-line quote and the attribution, and the right-aligned bar instance leaves the rest of the row empty.
- westcampus: Fragment quotes with no attribution (Either our measurements were wrong...) or a gap before the attribution; reads like stray text.
- your: Quote mark style with mid-quote punctuation errors (said Chavis inside the quote) and a missing closing mark; attribution reads 'Nuterangelo said'.
- yalesites: Demo page uses placeholder famous quotes (Lennon, Jobs) that show the styles but are not a model of real content.

## Image Banner (`image_banner`)

- divinity: Images are visibly low-resolution and soft, and tall portrait-style shots (graduates, a classroom) are cropped awkwardly at tall size.
- climateandhealth: The same flood photo is reused across pages, and the group photo is pixelated and cropped through people's faces and bodies.
- your: Heavy saturated blue duotone makes the images dark and muddy; three different pages feel generic and nearly interchangeable.
- peabody: Research report banners are casual phone snapshots (sunset, hillside) with no clear link to the report, and one has a thin visible border line.

## Pre-Built Form (`webform`)

- plc: Light-blue Submit button with dark text and the form is otherwise identical to every other site; no intro text or heading is visible in the screenshot, so nothing sets expectations.
- berkeleydivinity: Form appears on a podcast page and an 'update your contact information' page, where a generic 4-field contact form does not match the task of updating contact details.
- recreation: A generic contact form is used for locker rentals, a transactional need that a generic Subject/Message form handles poorly.

## Post Feed (`post_list`)

- yjil: A second instance is titled Test and shows only the first item with an image while the rest have none, which looks unfinished.
- silliman: News feed is a long text-only stack of titles and dates with no teasers or images; the events list shows a template placeholder (Revitalize past events).
- urbanstudies: Featured Events surfaces a leftover Test post and a placeholder event (Revitalize past events); filter label says Post Category on an events block.
- cadmy: News list is all headline and date with large empty space on the right and no images or teasers, so it feels bare and gets repetitive.
- microbialsciences: Text-only news list with inconsistent teasers (some items have summaries, most do not), making the rhythm uneven.

## Link Grid (`link_grid`)

- your: Grids with only two links and no heading ('Careers Overview', 'Applicant Resources') are used as a navigation list with no context.
- hospitality: Single-column 'Learn more' lists with a small gray label work as a sidebar but offer no visual advantage over a plain link list; one capture has no heading at all.
- french: A grid holding a single link under 'Table of Contents' is better as plain text or a button.
- registrar: Yale College guide list lacks the accent line, so adjacent grids on the same site look inconsistent; 16 long titles also strain a two-column layout.
- divinity: A grid of 12 faculty areas has no heading and a vertical gold line repeated per column, which looks cluttered.

## Tiles (`tiles`)

- registrar: Four tiles in four different theme colours (light blue, grey, navy, navy) with no meaning behind the colour, and mixed link icons in one row; reads as decoration.
- poorvucenter: Emoji icons in the heading (calendar, envelope, laptop, phone) look unpolished and are inconsistent with the platform's visual language; emoji can also be noisy for screen readers.
- chem: Dark grey tiles (placement page) and an orphaned last row with one tile of four; plain heading-only tiles are used as a nav list with no context, and the grey colour feels heavy and drab.
- marshbotanicalgarden: Background photos are darkened so heavily by the overlay that images are barely visible, and repeated filler text ('Click for more information') adds nothing; Desert House tile has a long paragraph that crowds the card.
- quantuminstitute: Name tiles (13 people) and long headings like '2017 - Tobias Kippenberg - Ecole Polytechnique Federale de Lausanne' overflow into very tall, uneven tiles; a table or list would suit this content better.

## Quote Callout (`quote_callout`)

- campyalearts: Block is used as a staff bio card (College, Major, Loves) rather than a quote; one instance has an empty 'Loves:' line and no image, leaving a large blank area on the left.
- civicthought: Bar style used for descriptive body paragraphs with no attribution on several instances, so they do not read as quotes; the long paragraph is hard to scan.
- planetarysolutions: The same presidential quote appears twice, and the image-style instance carries a promotional paragraph (media kit request) with a photo, not a quote.
- portal-redcap: Attribution lines run together (name, MD Gladys Phillips Crofoot Professor ...) with missing punctuation and a very long title that wraps.
- poorvucenter: Quotes with no photo and generic attribution (Student) on a plain band give little reason to use this block over a simple quote.

## Embed (`embed`)

- geospatial: Equipment rental Google Calendar in month view is entirely empty, which looks broken and tells visitors nothing.
- silliman: Recording Studio calendar embed is empty, with no explanation for visitors.
- ism: Livestream embed shows an 'OFFLINE' slate pointing to another site, and a form embed renders blank in the capture.
- chaplain: Power BI embeds show blank frames with 'Page 1 of 6' style pagination chrome, so the first impression is empty.
- gonzalezlab: Narrow SoundCloud embed truncates the title to 'In Conversa...'.

## Facts and Figures (`facts`)

- ets: Convening page has a Facts band with only a one-line thank-you sentence and no visible stats, leaving an empty navy strip.
- ets: Putting the whole phrase ('625 Internships Offered') in the number field makes the stats read as headings with no hierarchy between figure and label.
- divinity: Grey background on the 'Education for a Purpose' band gives weak contrast, and the block is used for qualitative taglines rather than facts.
- poorvucenter: Busy photo background with long, jargon-heavy labels (e.g. team names in each caption) makes the numbers harder to scan.
- your: Mixing 3-up and shifted spacing with no heading on benefits band; also stat '8,565 Years of service' is stranger without explanation of what the number aggregates.

## Tabs (`tabs`)

- your: Very long, dense benefit tables inside tabs (nearly 3000px tall), making the panel hard to scan and mobile-unfriendly; also tabs repeated across near-duplicate pages.
- registrar: Tab bars overflow with an arrow and clipped labels (e.g. 'Benefits for Departments and Fac...'), hiding options; a Guide tab just points to the other tabs.
- french: Tabs hold a few short paragraphs of text where plain headings would do; the profile tabs are fine but the policy content hides advising guidance.
- poorvucenter: Five tabs of platform descriptions that are partly hidden, so comparing platforms requires clicking each.

## Wrapped Text Callout (`wrapped_text_callout`)

- hospitality: Full-width callouts used as the only styling for ordinary paragraphs in a process explanation; no text wraps around them, so they are just boxed paragraphs with oversized padding.
- complit: Callout holds a long bio paragraph (very tall box) that squeezes the main text into a narrow column, and a callout that merely repeats the post title.
- ismreview: Callouts on left with long sentences become tall boxes that outweigh the main text; placement above the fold crowds the heading.
- your: Callout is a single short sentence beside a numbered list so the list text wraps awkwardly under the box; one instance is a full-width one-liner with a loud red border.

## Reference Card (`reference_card`)

- csoc: Tall posters and book covers stretch the card to over 900px, leaving huge empty navy space beside small text; the poster text is unreadable at that size and duplicates the card's content.
- ypsa: Grant card descriptions are cut off mid-word ('research' becomes 'researc'), and the stock manuscript photo is generic.
- ling: The 'Language is Everywhere' card uses a thin waveform graphic that leaves a large empty navy field; image does not fit the card's frame.
- yalesites: The release card uses a blurred, tiny dashboard screenshot as the image, and the title-only illustration cards leave large empty areas.

## Directory (`directory`)

- urbanstudies: One person (Anh Nguyen) has no photo or details, leaving a gap in the grid; mixed black-and-white and color photos look inconsistent.
- bands: A long bio line overflows and breaks mid-word (Educato / r), and the blocks have no heading or filter.
- episonic: Only two people shown in a four-column grid leaves a large empty area; casual vacation-style photo mixed with a formal headshot.
- campushealth: Photo styles and framing vary widely and some cards have contact details while others do not, so rows look uneven.
- beingwell: Only two cards fill a quarter of the width; the heavy HR affiliation label repeated on every card adds little.

## Resource View (`resource_view`)

- ccs: Book series listing mixes items with and without cover images, leaving empty gaps and a very long page with no pagination or filter.
- admissions: Several instances render as a lone title and rule (e.g. The Muykens Letter, no summary or link affordance), so the block does not read as a resource list.
- tinsleyworkshop: A single map image in a 3-column grid slot leaves most of the row empty; an image block would serve better.
- usability: Text-only list rows with no description; the same trainings repeat across 'Related' and 'Other' lists, and the grid view has uneven row heights.
- successlab: Thumbnails are screenshots of PDFs with tiny unreadable text and inconsistent crops.

## Event Calendar (`event_calendar`)

- urbanstudies: Homepage calendar shows a 'Revitalize past events' multi-day event on every day, burying any real events and looking broken.
- chaplain: Asterisks in titles and repeated multi-day entries for holy days clutter the grid, and a calendar fits poorly for observances.
- yalesites: Mostly empty months, with only one or two events, make the large grid feel hollow.
- timothydwight: Recurring weekly items and odd times (10:23PM) fill the grid with noise and suggest data entry problems.

## Video Banner (`video_banner`)

- whc: Lecture recordings show a slide or a distant podium as the poster, so the banner is dull and unreadable; 100 instances use the same flat full-width treatment.
- carbon-elti: A Zoom webinar recording with black pillarbox bars; the poster is a dense slide and the player is repeated on several pages.
- ezrastiles: Two nearly identical ceremony recordings appear on the same page, one showing the back of graduates' heads.
- wff: The same video is used twice on one page with a mid-interview frame that has no context.

