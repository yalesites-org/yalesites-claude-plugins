---
name: yalesites-ux-research
description: "User experience research context for the YaleSites platform. Use when evaluating feature requests, scoping tickets, making product decisions, advising editors or site builders, or assessing whether a proposed change serves the platform's users well. Contains user archetypes, mental models, top needs, and pain points from the YaleSites User Insight Report. Reference the archetypes to reason about who a change affects and how."
---

# YaleSites UX Research Skill

## Critical Context: About This Research

This skill is grounded in the **YaleSites Upgrade User Insight Report (Phase 1.1, September 2021)**, produced by Yale ITS UX and Four Kitchens as pre-discovery research for the platform redesign.

**What this means for how you use it:**

The research was conducted on the **legacy YaleSites platform** — before the current Drupal platform was designed or built. Many of the specific pain points documented (editing raw HTML/CSS, unintuitive Drupal admin, outdated templates, lack of content solutions, inability to customize) were the *direct motivation* for building the new platform. Those issues should be treated as **solved or significantly improved** by the current platform — do not cite them as active problems.

**What remains highly relevant:**
The **user archetypes** describe mental models, role structures, motivations, and emotional needs that are independent of any specific platform. These are still representative of who is using YaleSites today and how they think about the work. Use them freely when reasoning about product decisions, feature requests, and UX tradeoffs.

---

## User Archetypes

Archetypes are organized across three axes: **knowledge level**, **role**, and **approach**. A real user is a combination of one from each axis (e.g., Intermediate + Owner + Mechanic).

---

### Axis 1: Knowledge Level

#### Uninformed
> "I have information I need to get updated on my website, but I struggle to know how to get it done."

Managing a YaleSite is in addition to their primary job. Has limited knowledge of web platforms and Drupal. Gets overwhelmed easily and fears making mistakes. Needs clear guardrails, constrained choices, and proactive guidance — not just documentation that assumes they know what to ask.

**Needs:** Onboarding, help materials, boilerplate starters, direction on all aspects of site management
**Emotional goals:** Not being overwhelmed, comfortable learning, overcoming fear of mistakes

---

#### Intermediate
> "I would like more flexibility to have more creativity in the look and feel than the current templates offer."

Familiar with Drupal and YaleSites basics. Has strong opinions about visual design and what they want the site to look like. Motivated but can get frustrated when they can't realize their vision. Accessibility is on their radar but rarely executed consistently.

**Needs:** Easy creative content solutions, visual design options, integrated accessibility tools, training
**Emotional goals:** Feeling motivated and accomplished; gets frustrated when blocked

---

#### Expert
> "It is a challenge to get the right user permissions for my users to be able to edit their own content according to their skill level and job role."

High technical knowledge in Drupal, HTML, CSS. Often supports multiple sites or departments. Primary job role is directly related to YaleSites. May include vendors and contractors. Up to date on training and accessibility best practices.

**Needs:** Granular user permissions, efficient request workflows, community support model, easy visual design application
**Emotional goals:** Feeling independent, capable, and confident

---

### Axis 2: Role

#### Team Player
> "My role wasn't originally to keep our website updated, but I was the only one who could, so I took on that responsibility."

Willing and eager, but often feels like an imposter. Has accumulated knowledge through necessity rather than training. Motivated to build and create but stressed by the volume of responsibility. Accessibility awareness exists but time constraints prevent execution.

**Needs:** Visual design focus, online help materials, content management tools, user permissions
**Emotional goals:** Confidence in skill sets, working efficiently with less stress

---

#### Owner
> "Content updates come to me from many different channels, and it is up to me to provide direction and resources on how to execute them."

Responsible for one or more YaleSites. Acts as advocate and support layer for less experienced users on their team. Cares deeply about how the site serves its audience — content strategy, UX, and accessibility are priorities. Well-trained in accessibility but struggles with implementation resourcing.

**Needs:** Support for creating and managing a site, user permissions, updated look and feel, content solutions
**Emotional goals:** Working efficiently, confidence in the service, pleased with the final product

---

#### Dabbler
> "I just need to post an article once in a while."

Content author whose involvement is tied to specific moments — an event, a policy update, an academic calendar milestone. Doesn't want to learn the system deeply; just needs to get in, make a change, and get out. Forgets how to do things between sessions. Accessibility awareness is minimal and de-prioritized.

**Needs:** Support, direction, easy-to-follow help materials, low-friction access
**Emotional goals:** Working efficiently with minimal stress, feeling capable without deep training

---

### Axis 3: Approach

#### Easy Going
> "The university chose this platform so that is why I use it."

Follows platform conventions without pushback. Prefers simple, template-driven solutions. Works on smaller, less complex sites. Will comply with accessibility and update requirements without resistance. Needs things to "just work" without extensive configuration.

**Needs:** Updated look and feel, templates and ready-made solutions, help materials, content management
**Emotional goals:** Working efficiently, feeling independent and capable

---

#### The Inspired
> "I saw a feature on a website that I loved and I wanted it for my site but due to lack of resources we couldn't easily add it."

Builds by idea or example. Gets excited by what's possible but frustrated when the platform or budget can't deliver it. Often doesn't have the technical skill set to build what they envision. Wants accessibility built in — not as an extra step.

**Needs:** Help materials, updated visual design, content strategy support, accessibility baked into components
**Emotional goals:** Motivated and creative; frustrated easily when blocked

---

#### Mechanic
> "A lot of my work is cleaning up past technical debt, using CSS injector to customize, and spinning up new sites for our department."

Knowledgeable but not at Expert level. Responsible for maintaining multiple sites, fixing errors from other users, and building solutions under constraint. Well-versed in accessibility — incorporates it into daily work. Values efficiency and reliability above all.

**Needs:** User permissions, accessibility tools, easy visual design, online help, content management
**Emotional goals:** Working efficiently, independence, confidence

---

## Priority Archetype Combinations

When making product decisions, prioritize for these combinations:

| Priority | Combination | Why |
|----------|-------------|-----|
| **Primary — most likely user** | Intermediate + Owner + Mechanic | Represents the core active YaleSites user base — skilled enough to have strong opinions, responsible enough to own outcomes |
| **Secondary — needs most support** | Uninformed + Team Player + The Inspired | Highest user needs, most at risk of making mistakes or giving up; improvements here have outsized impact on the community |

---

## Top User Needs (From Research)

These were the five most-cited user needs across interviews, surveys, and shadowing sessions. Use these to assess whether a proposed feature or change aligns with what users actually need.

1. **Accessibility audit tool** — Cited by 72% of interviewed users. Users want accessibility integrated into the platform, not a separate external process.
2. **Updated look and feel** — Cited by 61% of interviewed users. Users wanted a modern Yale visual identity that was easy to apply. *This has been addressed by the current platform's design system.*
3. **User permissions and access** — Cited by 55% of interviewed users. Users need role-based permissions that match actual skill levels and responsibilities.
4. **Support and help materials** — Cited by 55% of interviewed users. Users want to be self-sufficient; they need robust, findable resources so they don't have to ask for help.
5. **Managing content** — Cited by 50% of interviewed users. Content management — particularly events, images, and structured content — needs to be low-friction.

---

## How to Apply This in Product Decisions

### When evaluating a feature request:
- **Which archetype(s) does this serve?** Name them. A feature that serves the Dabbler and Uninformed will need simpler UX and better defaults than one that serves the Expert.
- **Does it serve the priority combinations?** Changes that help the Intermediate + Owner + Mechanic and/or the Uninformed + Team Player + The Inspired should be weighted higher.
- **Does it align with the top user needs?** Accessibility tooling, permissions, support, and content management have been validated as high-value areas.

### When writing or grooming a ticket:
- Use archetype language in the description when it's relevant: "This change particularly affects the Dabbler archetype, who needs to complete this task infrequently and without deep platform knowledge."
- Use the acceptance criteria to call out archetype-specific UX considerations: "The interface should be clear enough for an Uninformed user to complete without training."
- If a feature has accessibility implications, flag the WCAG 2.1 AA requirement — all archetype segments identified accessibility tooling as a need, and the Mechanic and Expert incorporate it into daily work.

### When making a platform direction decision:
- Changes that increase complexity without benefiting the Uninformed or Dabbler archetype should be scrutinized — the platform's deliberate design constraints exist to serve these users.
- Changes that remove constraints to serve the Expert or Mechanic may be valid but should be weighed against the risk of overwhelming the Uninformed and Dabbler.

---

## Filter & Search Interaction Patterns

When evaluating a request to change filter/search UI — e.g., removing an "Apply" button in favor of real-time/auto-submit filtering:

- Real-time filtering (no separate Apply action) is generally fine on desktop — NN/g and Baymard research both support it in that context.
- Mobile is the explicit exception in that same research: slower connections and the higher cost of an accidental refresh mean batch filtering with an explicit Apply button holds up better there. Don't assume a desktop-validated pattern carries over to mobile.
- Any change here also has an accessibility floor — see `views-reference.md`'s WCAG 3.2.2 note on auto-submit filters.

---

## What NOT to Use This Research For

Do not cite the following as current pain points — they were addressed in the platform redesign:

- Editing raw HTML or CSS to accomplish basic layout tasks
- Unintuitive Drupal admin interface and confusing vocabulary
- Lack of content solutions / template limitations
- Outdated visual design
- Manual work caused by lack of components
- Difficulty applying Yale visual identity

These were the *motivation* for building the current platform, not active problems on it. If a user is experiencing something in this category today, it's likely a specific gap or bug rather than a systemic issue.
