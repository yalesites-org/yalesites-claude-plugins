# YaleSites Platform Usage Data (2026)

Supporting data from the **YaleSites UX Report: Understanding Today's YaleSites Users and Their Needs** (Yale ITS Digital Experience, August 7, 2026). Load this when a decision needs the underlying numbers rather than the archetype summary in `SKILL.md`.

Source datasets: Airtable records for all sites created before July 2026, and 3,736 ServiceNow "Website Consultation and Build" tickets.

---

## Site Category Distribution

How the platform is actually used, across 2,210 classified sites.

| Category | Share | Count |
|----------|-------|-------|
| Academic Programs & Resources | 43.5% | 962 |
| Unclassified / Ambiguous | 18.6% | 412 |
| Research Groups | 13.5% | 299 |
| Student Orgs & Clubs | 9.4% | 208 |
| Events & Conferences | 8.1% | 178 |
| Internal Testing & Sandbox | 5.8% | 128 |
| Individual Sites | 1.0% | 23 |

**Notes and limits:**
- Categories were assigned by a locally run LLM (Google Gemma 4 26B via Ollama) using **site titles only**, because the model had no access to site contents. Ambiguous names such as "BluePrint" fell into Unclassified.
- The dataset includes all sites created before July 2026, so some may no longer be active.
- Categories represent **intended purpose**, not current publication status. A site outside Internal Testing & Sandbox is not necessarily publicly live.
- Student Orgs & Clubs at 9.4% is a notable real use case despite Yale guidance directing student organizations toward Yale Connect.

---

## User Affiliation

Based on 3,308 Airtable contact records.

| Affiliation | Share | Count |
|-------------|-------|-------|
| Unidentified / No Affiliation | 42.2% | 1,392 |
| Staff / Employee | 31.4% | 1,038 |
| Students / graduate students / postdocs | 13.5% | 446 |
| Faculty | 11.4% | 376 |
| Affiliate | 1.5% | 50 |

Excluding the unidentified group, **staff and employees are the largest identifiable user group**, meaning the platform is used heavily by non-faculty administrative and professional staff across departments.

The 42.2% unidentified share meaningfully limits demographic interpretation. Improving affiliation records would sharpen future analysis. The "Affiliate" designation is also undefined in the dataset and may include vendors, contractors, or external collaborators.

---

## Affiliation by Site Category

Percentages are within each affiliation row. Because one person can be associated with multiple sites, rows are not mutually exclusive and do not sum to 100%.

| Affiliation | Research Groups | Academic Programs | Individual | Events | Student Orgs | Testing/Sandbox | Unclassified |
|-------------|----------------|-------------------|-----------|--------|--------------|-----------------|--------------|
| Staff / Employee | 8.6% (89) | **76.1% (790)** | 1.4% (14) | 12.8% (133) | 10.4% (108) | 2.9% (30) | 14.0% (145) |
| Faculty | **43.4% (163)** | 39.4% (148) | 2.7% (10) | 4.8% (18) | 9.3% (35) | 0.5% (2) | 11.2% (42) |
| Students / Postdocs | 19.1% (85) | **31.2% (139)** | 0.2% (1) | 9.4% (42) | 28.2% (126) | 0.0% (0) | 10.8% (48) |
| Affiliate | 8.0% (4) | **64.0% (32)** | 0.0% (0) | 10.0% (5) | 16.0% (8) | 0.0% (0) | 6.0% (3) |
| Unidentified | 13.6% (189) | **29.3% (408)** | 1.3% (18) | 8.8% (123) | 16.2% (226) | 0.6% (8) | 9.1% (126) |

**Key observations:**
- **Staff and employees** primarily create and maintain Academic Programs & Resources sites (76.1%), with Events & Conferences as a secondary use case (12.8%). They are the primary operational users responsible for institutional and departmental websites.
- **Faculty** are uniquely associated with Research Group websites (43.4%, their largest category), reflecting research leadership roles in labs, centers, and collaborative projects.
- **Students** show the most diverse usage, spanning academic programs (31.2%), student organizations (28.2%), and research groups (19.1%). This reflects the multiple roles students occupy at the university.

---

## Training Participation

| | Share | Count |
|---|-------|-------|
| Has NOT attended training | 87.6% | 2,898 |
| Has attended training | 12.4% | 410 |

Low participation is understandable given training is not required to become proficient and costs extra time. But interviews surfaced a related constraint: training sessions and Office Hours run roughly once to twice per week, which makes them **poorly suited to time-sensitive problems**. Teams therefore lean on internal resources before consulting ITS support.

---

## ServiceNow Support Ticket Analysis

3,736 tickets, classified into broad categories and subcategories by a locally hosted Gemma 4 (26B) model. Ticket data was extracted with a purpose-built Chrome extension.

### Broad category ranking

| Category | Share | Tickets |
|----------|-------|---------|
| Feature Support & Assistance | 26.9% | 1,004 |
| Bugs & Errors & Alerts | 19.9% | 745 |
| New Site & Go Live Requests | 16.2% | 606 |
| Training & Office Hours | 8.6% | 323 |
| Migration & Archival | 7.5% | 279 |
| Domain Change Requests | 7.1% | 265 |
| Integration & Compatibility Questions | 5.2% | 195 |
| Platform Feedback & Feature Requests | 4.4% | 163 |
| Policy / Process Questions | 1.8% | 68 |
| Other | 1.9% | 71 |
| Email Subscription | 0.5% | 17 |

### Subcategory breakdowns

**Feature Support & Assistance (1,004)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Users, Roles & Permissions | 35.6% | 357 |
| Content & Media Management | 26.3% | 264 |
| Feature How-To & Configuration | 11.2% | 112 |
| Page Layout & Navigation | 9.7% | 97 |
| Components & Modules | 9.4% | 94 |
| Site Administration Requests | 6.9% | 69 |
| General or Unspecified | 1.1% | 11 |

Users, Roles & Permissions being the single largest support subcategory corroborates the Multi-Site Manager's permission-granularity pain point.

**Bugs & Errors & Alerts (745)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Feature or Component Malfunction | 40.0% | 298 |
| Login & Access Errors | 15.8% | 118 |
| Visual & Styling Defects | 13.6% | 101 |
| Navigation & Link Failures | 12.8% | 95 |
| Performance & Availability | 8.9% | 66 |
| System, Security & Monitoring Alerts | 8.5% | 63 |
| General or Unspecified | 0.5% | 4 |

**New Site & Go Live Requests (606)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Launch Readiness & Go-Live | 34.5% | 209 |
| New Site Provisioning | 23.6% | 143 |
| Pre-Launch Planning | 21.9% | 133 |
| Sandbox Provisioning | 19.6% | 119 |
| General or Unspecified | 0.3% | 2 |

**Training & Office Hours (323)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| External Tool Training | 61.0% | 197 |
| Office Hours & Consultation | 21.1% | 68 |
| YaleSites Training | 9.9% | 32 |
| Meeting & General Inquiry | 8.0% | 26 |

**Migration & Archival (279)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Migration Discovery & Planning | 39.4% | 110 |
| Site Decommissioning & Archival | 35.5% | 99 |
| Content & Site Migration | 14.3% | 40 |
| Site Rebuild & Redesign | 10.8% | 30 |

**Domain Change Requests (265)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Redirects, DNS & Certificates | 57.7% | 153 |
| New or Custom Domain | 27.2% | 72 |
| Domain or URL Change | 15.1% | 40 |

**Integration & Compatibility Questions (195)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Third-Party Service Integration | 71.8% | 140 |
| Embeds & Cross-Platform Compatibility | 21.0% | 41 |
| API & Data Connectivity | 7.2% | 14 |

**Platform Feedback & Feature Requests (163)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| New Feature Request | 55.2% | 90 |
| Existing Feature Enhancement | 43.6% | 71 |
| Platform & Design Feedback | 1.2% | 2 |

**Policy / Process Questions (68)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Eligibility & Acceptable Use | 35.3% | 24 |
| Service Process & Requirements | 29.4% | 20 |
| Governance, Ownership & Responsibilities | 23.5% | 16 |
| Accessibility, Privacy & Compliance | 11.8% | 8 |

**Email Subscription (17)**

| Subcategory | Share | Count |
|-------------|-------|-------|
| Subscribe to Email | 64.7% | 11 |
| Email Preference Change | 17.6% | 3 |
| Unsubscribe from Email | 17.6% | 3 |

---

## Design Recommendations in Full

The five recommendations below come mainly from usability testing with first-time users, so they concentrate on the **Solo Starter**, **New Recruit**, and **Transitioning Team** archetypes.

### 1. Retire or archive the legacy YaleSites website

- **Observed issue:** participants frequently used Google to find YaleSites documentation. Search results and AI-generated summaries surfaced legacy YaleSites D7 resources alongside current D10 guidance, directing users to obsolete navigation paths and features. This increased the likelihood users would attempt outdated workflows before finding correct documentation.
- **Recommended action:** retire, archive, or reduce the search visibility of the legacy YaleSites website so search engines prioritize current D10 documentation.
- **Expected effect:** users reach accurate instructions first, reducing false starts and documentation confusion.
- **Pain points addressed:** misleading Google search results.

### 2. Reduce confusion by adding menu editing shortcuts

- **Observed issue:** participants entered "Edit Layout and Content" expecting to modify every visible page element, but the site name and primary navigation are managed through separate site-level tools. The mismatch led users to believe they were in the wrong place or that the functionality was unavailable.
- **Recommended action:** add clear shortcut buttons or contextual links within Edit Layout and Content:
  - Edit Site Name button leads to Site Settings
  - Edit Navigation Menu button leads to Content, then Manage Menus

  When a user clicks the site title or navigation menu while in editing mode, interpret that as editing intent: highlight the relevant shortcut or offer a direct link to the appropriate interface instead of navigating away.
- **Expected effect:** contextual entry points bridge related editing tasks without requiring users to understand YaleSites' administrative structure, reducing navigation friction while preserving the existing separation of functions.
- **Pain points addressed:** editing interaction does not match expectations; poor UI discoverability.

### 3. Differentiate banner and content level block sections

- **Observed issue:** participants encountered two visually similar "Choose a block" interfaces, one for the site banner and one for page content. Because both share the same title and treatment, some users thought the system had opened the wrong picker or malfunctioned.
- **Recommended action:** make the editing context immediately recognizable through distinct labels and visual treatments.
  - Use specific titles such as "Choose a Banner Block" and "Choose a Content Block"
  - Use different accent colors, icons, or section labels for each context
  - Visually separate the banner region from the page-content region and clarify that each uses a different block library
- **Expected effect:** a stronger distinction helps users build a clearer mental model of banner-level versus content-level customization and reduces uncertainty when switching between them.
- **Pain points addressed:** counter-intuitive Drupal operation logic; editing interaction does not match expectations; confusing terminology.

### 4. Distinguish the system interface from page content

- **Observed issue:** participants occasionally mistook system-interface text for editable page content. For example, "Edit layout for Homepage" uses typography and placement similar to a page title, making its role ambiguous.
- **Recommended action:** adopt a distinct visual language for administrative interface elements so they cannot be confused with user-generated content.
  - Place system headings in a dedicated toolbar or interface panel
  - Use different typography, color, or background treatment for system messages
  - Add an editing-mode indicator such as "Editing: Homepage," styled as part of the administrative interface rather than the page canvas
- **Expected effect:** users identify their editing context at a glance and more confidently distinguish system guidance from content they control.
- **Pain points addressed:** editing interaction does not match expectations; poor UI discoverability.

### 5. Enable auto-scrolling when dragging blocks

- **Observed issue:** when users drag a block toward the top or bottom of the viewport, the page does not scroll automatically. Moving a block over a long distance therefore requires repeated dropping and repositioning.
- **Recommended action:** enable directional auto-scrolling while a block is being dragged, with scroll speed responding predictably as the pointer approaches the viewport edge.
- **Expected effect:** users reorder blocks over longer distances in one continuous interaction, reducing repetitive work.
- **Pain points addressed:** rigid layout/content composition.

---

## Methodology

### User interviews

Participants were drawn from the Airtable Contacts table. A stratified sample of roughly 100 candidates was selected based on the distribution of user affiliations and invited in batches of 15.

Initial response was low, roughly 1 to 2 signups per 30 invitations (under 6.7%). The invitation email was shortened and a second selection round added two criteria: the candidate had agreed to be contacted by email, and had previously attended YaleSites Office Hours or training (on the reasoning that prior ITS contact predicts willingness to participate). This identified 243 additional candidates, of whom 44 were invited.

Approximately 70 invitations were extended in total, producing **9 completed interviews (12.9% response rate)**. This excludes one participant who registered but did not attend. Interviews ran about 30 minutes, were conducted by Kevin and Mike, and followed a semi-structured format: a predefined guide with interviewers free to reorder questions and follow up based on responses.

### User tests

Planned and conducted by Kevin. Participants were recruited from the **2026 Yale ITS Summer Internship Program** because the interns closely resemble the Solo Starter and New Recruit archetypes, with no prior YaleSites experience.

**Sampling limitation to keep in mind:** recruitment was convenience sampling from an ITS internship program, so many participants had technical backgrounds including computer science or web development experience. **The sample likely overrepresents technically proficient users.** Response rate was near 100%.

Each test ran up to 45 minutes using scenario-based task design. Participants imagined they had joined the Computational Physics Lab (a hypothetical Yale research lab) as undergraduate research assistants responsible for maintaining the lab's YaleSites website. Lab websites were chosen because they are one of the most common site types maintained by student users.

Tasks:
- Logging into YaleSites
- Editing the site title
- Recreating a homepage banner
- Reordering content blocks
- Creating a new page
- Adding the page to the site's navigation menu
- Adding and configuring a profile listing block

Participants were asked to think aloud, told there were no right or wrong answers, and encouraged to search existing documentation before receiving moderator guidance. Sessions were screen recorded with consent.

### Data analysis

- **Site analysis:** Airtable site records exported as CSV, classified by site name into seven predefined categories using a locally hosted Ollama model.
- **Affiliation analysis:** counts aggregated per standardized affiliation group, then linked to site-category classifications. For each affiliation group, the analysis calculated the percentage associated with at least one site in each category. Because a person can be associated with multiple sites, category percentages are **not mutually exclusive**.
- **ServiceNow analysis:** 3,736 tickets classified against a predefined taxonomy of broad categories and subcategories, one of each per ticket, then aggregated into frequencies.

All model processing was run locally through Ollama. **No data was transmitted to or processed by a cloud-based AI service.**

---

## Reading These Numbers Responsibly

- Interview and test findings come from a small qualitative sample (18 participants). Counts and percentages describe **that group**, not the full user population. Treat them as signal strength, not incidence rates.
- The user-test sample skews technical. If technically proficient first-time users still hit a usability problem, that is a strong signal, since less technical users would likely fare worse.
- Site categories and ServiceNow classifications were LLM-assigned from limited input (titles, ticket fields), so individual rows may be wrong even where aggregate distributions are informative.
- 42.2% of contact records have no identified affiliation, which caps how far demographic conclusions can be pushed.
