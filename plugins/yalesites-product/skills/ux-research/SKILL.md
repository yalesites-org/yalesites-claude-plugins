---
name: yalesites-ux-research
description: "User experience research context for the YaleSites platform. Use when evaluating feature requests, scoping tickets, making product decisions, advising editors or site builders, or assessing whether a proposed change serves the platform's users well. Contains the six current user archetypes, top pain points, delights, open design recommendations, and platform usage data from the 2026 YaleSites UX Report. Reference the archetypes to reason about who a change affects and how."
---

# YaleSites UX Research Skill

## Critical Context: About This Research

This skill is grounded in the **YaleSites UX Report: Understanding Today's YaleSites Users and Their Needs (August 7, 2026)**, produced by Yale ITS Digital Experience (Jinghan "Kevin" Wu and Michael Tullo). It is the current, authoritative picture of who uses YaleSites and what they struggle with.

**What the 2026 research covered:**

| Method | Scope |
|--------|-------|
| User interviews | 9 sessions, ~30 min, users across seven department/administrative bodies |
| User tests | 8 sessions, ~45 min, new YaleSites users with varying site-building backgrounds |
| Airtable analysis | 5,515 rows of site and user affiliation data (3,308 contact records) |
| ServiceNow analysis | 3,736 "Website Consultation and Build" tickets |

Pain point and delight counts below are reported out of **18 research participants** (cited as P1 through P18).

**Relationship to the 2021 research:** the previous version of this skill was built on the *YaleSites Upgrade User Insight Report (Phase 1.1, September 2021)*, which studied the **legacy** platform before the current Drupal build existed. That report is now a point-in-time snapshot rather than a description of today's users. It is preserved in `references/research-2021-historical.md` for historical context. **Default to the 2026 archetypes and findings.** See "What Changed Since 2021" below, which includes a correction to guidance the older version of this skill got wrong.

Detailed usage data (site categories, affiliations, ServiceNow breakdowns, training participation, methodology) lives in `references/platform-usage-data-2026.md`.

---

## The Six User Archetypes

Archetypes are abstract labels representing collective user behaviors and shared characteristics (Laubheimer, 2022). The 2026 study maps six archetypes on two axes:

- **Y axis, YaleSites experience:** new through experienced
- **X axis, operational scale:** solo through multiple contributors

They group into three bands:

| Band | Archetypes |
|------|-----------|
| **Experienced** | Multi-Site Manager, Part-Time Owner, The Maintainer |
| **Transitioning** | Transitioning Team |
| **New to YaleSites** | New Recruit, Solo Starter |

Unlike the 2021 model, these are **not** combinatorial. A user is one archetype, not one pick from each of three axes.

---

### 1. Multi-Site Manager
> "I oversee the maintenance and creation of multiple sites, and I'm usually the person people comes to when they get stuck."

Experienced user responsible for a portfolio of websites rather than a single site. Work extends past content maintenance into governance, delegation, training, troubleshooting, and consistency across teams and sites. Often serves as their team's internal YaleSites expert: onboarding contributors, answering one-off questions, adapting training materials, establishing repeatable workflows, deciding what can safely be delegated. Because responsibilities scale across many sites and users, **small inefficiencies become significant repeated work**.

**Core needs**
- **Manage and support contributors:** flexible permissions, safe ways for less-experienced users to contribute, delegation that does not create cleanup work
- **Train others efficiently:** shareable documentation, dev environments, examples, just-in-time learning resources
- **Cross-site reuse and consistency:** reusable content, components, sections, and organizational structures across sites

**Pain points**
- Contributors need answers at the moment they hit a task, but documentation is hard to locate or disconnected from the workflow (P13, P16)
- Entire sections cannot be made globally reusable, creating repetitive setup when the same component group is needed in multiple places (P13)
- Permission controls are not granular enough, for example allowing contributors to maintain only their own content (P13)
- Content across separate YaleSites must be manually duplicated because sites cannot share or synchronize content (P9)

**Example persona:** web manager supporting websites for an academic body.

---

### 2. Part-Time Owner
> "I know how to build and run our website, but I have ten other responsibilities competing for my attention"

Responsible for building and maintaining a site, but website management is only a small portion of their role. **They may be highly capable and may have built the site themselves. What distinguishes them is limited time and attention, not limited skill.** They regularly maintain news, profiles, events, or departmental information, but may go weeks or months without touching less-common features. They value workflows that are fast, predictable, and easy to rediscover. Minor friction like resizing an image becomes frustrating when the website is one item on a much longer task list.

**Core needs**
- **Complete updates quickly:** routine publishing in as few steps as possible
- **Efficient everyday content tools:** images, news, profiles, events, and layouts flexible enough to get acceptable results without workarounds
- **Fast access to help:** short videos, screenshots, concise documentation, responsive human support
- **Quickly remember how things work:** infrequent workflows easy to rediscover without full retraining

**Pain points**
- Website maintenance competes with many other job responsibilities, making lengthy or repetitive workflows especially costly (P9)
- Limited image resizing and layout flexibility turns routine updates into design work when available images do not fit the predetermined presentation (P12)
- Responsive layouts behave unexpectedly across screen sizes, requiring checking and troubleshooting they may not have time for (P12)
- Instructions for specific or newer features are hard to locate when they only need a quick reminder (P12)

**Example persona:** departmental staff maintaining the unit website alongside scheduling, student services, and administrative responsibilities.

---

### 3. The Maintainer
> "I'm here to keep our pages, profiles, news, and navigation accurate, not to make decisions about the entire web program."

Staff-level contributor working regularly within an established departmental website. Unlike the New Recruit, they have enough experience to handle most recurring maintenance independently and understand their team's conventions. Unlike the Part-Time Owner or Multi-Site Manager, they typically do **not** own broader strategy, governance, or direction. Work revolves around concrete production tasks: maintaining pages, uploading stories, managing profiles, migrating content, updating menus, working with images, assembling layouts. They need enough flexibility to work efficiently but usually operate within standards set by someone else.

**Core needs**
- **Efficient recurring workflows:** common maintenance should get fast and predictable with experience
- **Find specific answers quickly:** they do not need broad training, they need the exact setting or unusual workflow blocking the task in front of them
- **Reliable content presentation:** images, layouts, navigation, and dynamic content behaving predictably so maintenance does not become visual troubleshooting

**Pain points**
- Images crop, zoom, or lose quality when dimensions do not match platform expectations, requiring trial and error (P14)
- Finding a specific help article is time-consuming when documentation lacks effective search (P15)
- Menu visibility and related navigation settings are unintuitive, making routine publishing confusing (P15)
- Frequently changing content such as faculty profiles or news creates substantial recurring maintenance when updates cannot be automated or reused (P9)

**Example persona:** communications staff member responsible for faculty profiles, stories, and departmental pages.

---

### 4. Transitioning Team
> "Our D7 site already works; The hard part is figuring out what needs to change, and how our old way of working translates into the new YaleSites."

Moving an existing Drupal 7 or non-YaleSites website onto the current platform. They do not start from a blank slate: they bring years of existing pages and content structures, though they may also use the move as a chance to make drastic changes. **They behave much like Solo Starters or New Recruits when interacting with the platform, because the platform itself is unfamiliar.** Their learning challenge is compounded by a strategic one: migration forces decisions about what content should stay, how information should be reorganized, what belongs together on a page, and which legacy patterns should not simply be recreated.

**Core needs**
- **Translate into the new YaleSites:** understand which legacy features have direct equivalents, which work differently, and which need a new approach
- **Plan and restructure content:** guidance on information architecture, editorial strategy, taxonomy, page composition
- **Learn the new platform while migrating:** structured, step-by-step onboarding
- **See successful examples:** case studies showing how components and layouts translate existing content

**Pain points**
- Teams know how content worked in D7 but lack guidance on information architecture and editorial strategy for restructuring it (P10, P11)
- Determining appropriate taxonomy and tagging during migration is difficult when content spans multiple topics or organizational categories (P10, P11)
- Some legacy functionality has no direct equivalent in the current platform (P13, P16)
- Migrating older news, events, and other legacy data can require substantial manual or technical work (P16)

**Example persona:** academic department team moving an established D7 departmental website onto the current YaleSites.

---

### 5. New Recruit
> "I'm new to YaleSites, but my team already has a way of doing things."

New to YaleSites, joining a team where website-management practices, experienced users, or established workflows already exist. They learn the platform in the context of their role rather than inventing a website-management process. Their supervisor or teammates are an important bridge into YaleSites. Through mentorship and department-specific guidance they gradually move from following established procedures toward independently maintaining their portion of the site.

**Core needs**
- **Structured onboarding:** learn the team's established workflows, conventions, recurring responsibilities
- **Become productive quickly:** learn the parts of YaleSites relevant to their assigned work without mastering the whole platform
- **Trusted support network:** easy access to supervisors, experienced teammates, internal training materials, YaleSites resources

**Pain points**
- Unfamiliar YaleSites terminology makes even straightforward tasks initially confusing
- They depend heavily on coworkers when platform guidance is not available in context
- Documentation is hard to navigate when searching for a very specific task
- Hidden settings and unintuitive workflows make instructions harder to remember independently
- Their success depends on the quality and consistency of their team's existing documentation and onboarding

**Example persona:** new communications coordinator learning an established departmental website workflow from experienced teammates.

---

### 6. Solo Starter
> "I need to build this website and need to figure out YaleSites my own."

New to YaleSites with little access to experienced YaleSites users nearby. They typically arrive with a specific goal such as creating a lab, department, program, or event website, and must independently determine how the platform works. Some have experience with other website builders, others are completely new to site building. **Without an established departmental workflow to follow, they build their own mental model through exploration, documentation, and trial and error.**

**Core needs**
- **Clear starting point:** where to begin, how YaleSites is organized, the basic steps to launch a site
- **Discoverable self-service guidance:** trustworthy documentation, tutorials, examples, and answers found without relying on a teammate
- **Get to a functional site quickly:** essential site-building tasks before advanced functionality

**Pain points**
- YaleSites terminology such as blocks, sections, Views, and content types does not match their existing mental model
- Important settings and configuration options are difficult to discover
- Lack of direct manipulation, preview, or familiar site-builder interactions makes the platform feel unintuitive
- Help resources are difficult to search or discover at the moment they are needed
- Without an experienced teammate, trial and error becomes the primary troubleshooting method

**Example persona:** graduate student independently building a lab website without an experienced YaleSites colleague.

---

## Top User Pain Points

Ordered by how many of the 18 participants raised each one. Use these to weigh whether a proposed change addresses something users actually hit.

| Pain point | Count | Most affected archetypes |
|-----------|-------|--------------------------|
| **Confusing terminology** (Block vs. Section, Teaser fields, padding, footer, alt text, tags/categories, Admin Label vs. Heading; users cannot predict what a control does from its label) | 12/18 (67%) | Solo Starter, New Recruit |
| **Misleading Google search results** (missing docs, weak Help Center search, outdated Google results, misleading AI summaries, hard-to-find visual references) | 11/18 (61%) | Solo Starter, New Recruit, Transitioning Team |
| **Poor UI discoverability** (users know *what* to change but not *where*; site name, Add Content, editing, utility navigation, menu settings live in scattered places) | 10/18 (56%) | Solo Starter, New Recruit |
| **Counter-intuitive Drupal operation logic** (page creation, attaching pages to navigation, internal linking, menu visibility, page-level vs. system-level links) | 8/18 (44%) | Solo Starter, New Recruit |
| **Editing interaction does not match expectations** (users expect visible content to be directly editable; they click text, look for an Edit icon, confuse View and Edit modes, want immediate preview) | 8/18 (44%) | Solo Starter, New Recruit |
| **Rigid layout/content composition** (moving large blocks, moving items across sections, reordering layouts, image/text combinations, independent padding control, responsive layouts) | 8/18 (44%) | The Maintainer |
| **Taxonomy, search, filtering, and structured data do not scale** (tags/categories confusing, Views overloaded, limited filtering, shallow site search, no sortable tables, complex directory/job-board cases) | 7/18 (39%) | The Maintainer, Part-Time Owner |
| **Power users feel constrained by loss of flexibility** (missing legacy functionality, custom Views/content types, plugins or integrations, specialized layouts, richer permissions) | 6/18 (33%) | Multi-Site Manager, Transitioning Team |
| **Image and media handling requires too much trial and error** (dimensions, scaling, cropping, responsive behavior, recommended sizes, media placement) | 5/18 (28%) | Part-Time Owner, The Maintainer |
| **Lack of accessible expert support** (office hours hard to attend; some want strategic/editorial guidance rather than purely technical support) | 4/18 (22%) | Transitioning Team |
| **Migration, export, and long-term preservation** (labor-intensive legacy content moves, limited bulk migration/export, archival preservation for long-lived academic content) | 2/18 (11%) | Transitioning Team, Multi-Site Manager |

**The pattern that matters most:** the five most-cited pain points all name **Solo Starter and New Recruit** as most affected. First-run comprehension, naming, and discoverability are where the platform loses people, not advanced capability.

---

## What Users Delight In

Protect these when weighing changes. They are the platform's current strengths.

| Delight | Count |
|---------|-------|
| **Good learning resources and support** (video tutorials, office hours, direct technical assistance) | 9/18 (50%) |
| **D10 is substantially easier and faster than prior versions** (major improvement over D7; easy onboarding, manageable routine content, rapid site creation; the newer Views GUI praised specifically) | 6/18 (33%) |
| **Dynamic content, taxonomy, and integrations can be highly effective** (Localist, Views, audience-specific feeds, tags, taxonomy reduce manual maintenance when configured successfully) | 4/18 (22%) |
| **Getting inspired from other sites** (seeing components and layouts on real Yale websites makes features easier to understand than documentation alone) | 4/18 (22%) |
| **Good release and email communication** (release and platform update emails help users stay aware of new functionality and serve as a reference to return to) | 3/18 (17%) |
| **Appreciate brand-compliant design** (animations, video, palettes, polished finished-site appearance) | 3/18 (17%) |

---

## Open Design Recommendations

Five recommendations from the 2026 report, drawn mainly from usability testing with first-time users. Full observed-issue and expected-effect detail is in `references/platform-usage-data-2026.md`.

1. **Retire or archive the legacy YaleSites website.** Google results and AI summaries surface legacy D7 resources alongside current D10 guidance, sending users down obsolete paths. *Addresses: misleading Google search results.*
2. **Add menu editing shortcuts.** Users enter "Edit Layout and Content" expecting to change every visible element, but site name and primary navigation are managed through separate site-level tools. Add contextual shortcuts from the editing screen to Site Settings and Manage Menus. *Addresses: editing interaction mismatch, poor UI discoverability.*
3. **Differentiate banner and content level block sections.** The banner and content "Choose a block" pickers look identical, so users think the wrong picker opened or the system malfunctioned. Give each distinct titles, accent colors, and section labels. *Addresses: counter-intuitive Drupal logic, editing interaction mismatch, confusing terminology.*
4. **Distinguish the system interface from page content.** System text such as "Edit layout for Homepage" is styled like a page title, making its role ambiguous. Give admin UI its own visual language and add an editing-mode indicator. *Addresses: editing interaction mismatch, poor UI discoverability.*
5. **Enable auto-scrolling when dragging blocks.** Dragging a block toward the viewport edge does not scroll the page, so long moves require repeated drop-and-reposition. *Addresses: rigid layout/content composition.*

---

## How to Apply This in Product Decisions

### When evaluating a feature request
- **Name the archetype(s) it serves.** A change serving the Solo Starter or New Recruit needs clearer naming and better first-run defaults than one serving the Multi-Site Manager.
- **Check it against the pain point table.** A request mapping to a high-count pain point (terminology, discoverability, findable documentation) carries more evidence than one that does not appear at all.
- **Watch for the Part-Time Owner trap.** This archetype is time-poor, not skill-poor. Do not resolve their problems by simplifying away capability. Resolve them by reducing steps and making infrequent workflows easy to rediscover.
- **Weigh cross-site scale for the Multi-Site Manager.** A small per-site inefficiency multiplies across a portfolio. Reuse, delegation, and permission granularity are worth more to them than any single-site polish.

### When writing or grooming a ticket
- Use archetype language where relevant: "This primarily affects the Solo Starter, who has no experienced teammate to ask and will rely on search and trial and error."
- Put archetype-specific UX expectations in acceptance criteria: "Labels should be understandable to a New Recruit who has not been trained on YaleSites terminology."
- Flag WCAG 2.1 AA where a change has accessibility implications. Accessibility did not surface as a top-cited pain point in 2026, but that is an absence of signal, not evidence it stopped mattering. It remains a platform requirement.

### When making a platform direction decision
- Naming and discoverability changes have the broadest reach. The top three pain points are all comprehension problems rather than capability gaps.
- Changes that add capability for the Multi-Site Manager or Transitioning Team can be valid, but check they do not add terminology or interface surface that costs the Solo Starter and New Recruit.
- Documentation and findability are product surface, not a support afterthought. Weak Help Center search and stale legacy content ranking in Google are cited as often as interface defects.

---

## Filter & Search Interaction Patterns

When evaluating a request to change filter/search UI, for example removing an "Apply" button in favor of real-time/auto-submit filtering:

- Real-time filtering (no separate Apply action) is generally fine on desktop. NN/g and Baymard research both support it in that context.
- Mobile is the explicit exception in that same research. Slower connections and the higher cost of an accidental refresh mean batch filtering with an explicit Apply button holds up better there. Do not assume a desktop-validated pattern carries over to mobile.
- Any change here also has an accessibility floor. See `views-reference.md`'s WCAG 3.2.2 note on auto-submit filters.

### Segmented controls (two-option toggles) in authoring forms

A recurring pattern in the block authoring forms is a binary operator choice, for example Any vs. All for "match content tagged with." A few things hold consistently here:

- **Text labels, not icons.** A two-segment control works for this only when each segment carries a word. Icons cannot communicate a logical operator, so an icon-only treatment pushes the Solo Starter and New Recruit into guessing. If earlier guidance said "avoid the button treatment," that concern was about icons carrying the meaning, not about segmented controls as such.
- **Keep it a radio group underneath.** Style `#type => 'radios'` with CSS rather than rebuilding the control out of `<button>` elements. Buttons submit the form, and switching away from radios loses arrow-key navigation and the free "radio group, 1 of 2" screen reader announcement.
- **Prefer always-visible-but-disabled over conditionally-appearing.** A control that only renders once a sibling field has content is three states to QA and shifts the layout while someone is typing. Showing it in a disabled state is steadier. The tradeoff: disabled styling still needs to stay at or above 3:1 contrast. Disabled controls are technically exempt from contrast requirements, but leaning on that exemption defeats the reason you showed the control in the first place.
- **Watch the vertical footprint.** These forms are tabbed and dense. An operator that reads as one line (`[Any|All]` followed by short help text on the same line) instead of a stacked title/radios/description block frees enough room to keep later settings in view. Dropping a redundant standalone `#title` is usually safe as long as the group is still labelled for screen readers.

---

## What Changed Since 2021

### Correction: confusing terminology and admin UI are NOT solved

The previous version of this skill instructed the reader **not** to cite "unintuitive Drupal admin interface and confusing vocabulary" as a current pain point, on the grounds that the platform rebuild addressed it. **The 2026 data contradicts this.** Confusing terminology is now the single most-cited pain point (67%), followed by poor UI discoverability (56%) and counter-intuitive Drupal operation logic (44%). Treat these as live, high-priority problems.

### Genuinely addressed since 2021

The 2026 delights confirm these 2021 complaints were resolved. Do not cite them as active problems:

- Outdated visual design, and difficulty applying Yale visual identity (2026 delight: brand-compliant design)
- General platform speed and usability versus prior versions (2026 delight: D10 substantially easier and faster than D7)
- Editing raw HTML or CSS to accomplish basic layout tasks

### Partially addressed, still live in a narrower form

- **Template and content-solution limitations** now show up as rigid layout/content composition (44%) and structured data that does not scale (39%), concentrated in The Maintainer rather than across all users.
- **Manual work from missing components** now shows up as cross-site content duplication and recurring profile/news maintenance, concentrated in the Multi-Site Manager.
- **User permissions** remains live, as granularity limits for the Multi-Site Manager.

### How the archetype model itself changed

| 2021 model | 2026 model |
|-----------|-----------|
| Three axes (knowledge, role, approach), combined into a composite user | Six standalone archetypes on two axes (experience, operational scale) |
| Framed the high-support user as low-knowledge ("Uninformed") | Reframes them as the **Part-Time Owner**: capable, but time-constrained |
| No migration-specific archetype | Adds **Transitioning Team** for D7 and non-YaleSites migrations |
| No distinction by support network | Splits new users into **New Recruit** (has experienced teammates) and **Solo Starter** (does not), which drives different needs |

The single biggest reframe: **isolation and available time now predict user need better than technical skill does.**
