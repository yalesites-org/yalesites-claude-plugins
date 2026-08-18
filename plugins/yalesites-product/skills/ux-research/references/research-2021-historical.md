# YaleSites UX Research, 2021 (Historical)

**This is archived research. Do not use it as the current picture of YaleSites users.** For current archetypes and findings, use `SKILL.md`, which is grounded in the 2026 UX Report.

Source: **YaleSites Upgrade User Insight Report (Phase 1.1, September 2021)**, produced by Yale ITS UX and Four Kitchens as pre-discovery research for the platform redesign.

---

## Why This Is Kept

The 2021 research studied the **legacy** YaleSites platform, before the current Drupal build was designed. It is a point-in-time record of what the platform's users looked like and what motivated the rebuild. It is useful for:

- Understanding **why** the current platform was built the way it was, and which constraints were deliberate
- Tracing how a long-standing pain point has or has not changed over five years
- Historical context when someone references the older archetype vocabulary (Uninformed, Dabbler, Mechanic, and so on) in an old ticket or document

It is **not** useful for describing who uses YaleSites today. Use the six 2026 archetypes for that.

---

## Important: One Piece of This Research Aged Badly

The prior version of this skill concluded that "unintuitive Drupal admin interface and confusing vocabulary" had been **solved** by the platform rebuild, and instructed readers not to cite it.

**The 2026 research contradicts that conclusion.** Confusing terminology is the most-cited pain point in 2026 (67% of participants), with poor UI discoverability at 56% and counter-intuitive Drupal operation logic at 44%. The rebuild improved many things, but naming and discoverability were not among them.

If you encounter that older guidance anywhere else in the plugin or in team documents, it is out of date.

---

## The 2021 Archetype Model

Archetypes were organized across three axes: **knowledge level**, **role**, and **approach**. A real user was described as a combination of one from each axis, for example Intermediate + Owner + Mechanic.

The 2026 model replaced this with six standalone archetypes on two axes (YaleSites experience and operational scale). The composite approach is no longer used.

### Axis 1: Knowledge Level

**Uninformed**
> "I have information I need to get updated on my website, but I struggle to know how to get it done."

Managing a YaleSite is in addition to their primary job. Limited knowledge of web platforms and Drupal. Gets overwhelmed easily and fears making mistakes. Needs clear guardrails, constrained choices, and proactive guidance, not documentation that assumes they know what to ask.

*Needs:* onboarding, help materials, boilerplate starters, direction across all aspects of site management
*Emotional goals:* not being overwhelmed, comfortable learning, overcoming fear of mistakes

**Intermediate**
> "I would like more flexibility to have more creativity in the look and feel than the current templates offer."

Familiar with Drupal and YaleSites basics. Strong opinions about visual design. Motivated but frustrated when they cannot realize their vision. Accessibility is on their radar but rarely executed consistently.

*Needs:* easy creative content solutions, visual design options, integrated accessibility tools, training
*Emotional goals:* feeling motivated and accomplished, frustrated when blocked

**Expert**
> "It is a challenge to get the right user permissions for my users to be able to edit their own content according to their skill level and job role."

High technical knowledge in Drupal, HTML, CSS. Often supports multiple sites or departments. Primary job role directly related to YaleSites. May include vendors and contractors. Up to date on training and accessibility best practices.

*Needs:* granular user permissions, efficient request workflows, community support model, easy visual design application
*Emotional goals:* feeling independent, capable, confident

### Axis 2: Role

**Team Player**
> "My role wasn't originally to keep our website updated, but I was the only one who could, so I took on that responsibility."

Willing and eager but often feels like an imposter. Accumulated knowledge through necessity rather than training. Motivated to build but stressed by the volume of responsibility. Accessibility awareness exists but time constraints prevent execution.

*Needs:* visual design focus, online help materials, content management tools, user permissions
*Emotional goals:* confidence in skill sets, working efficiently with less stress

**Owner**
> "Content updates come to me from many different channels, and it is up to me to provide direction and resources on how to execute them."

Responsible for one or more YaleSites. Acts as advocate and support layer for less experienced users on their team. Cares deeply about how the site serves its audience. Well-trained in accessibility but struggles with implementation resourcing.

*Needs:* support for creating and managing a site, user permissions, updated look and feel, content solutions
*Emotional goals:* working efficiently, confidence in the service, pleased with the final product

**Dabbler**
> "I just need to post an article once in a while."

Content author whose involvement is tied to specific moments, such as an event or a policy update. Does not want to learn the system deeply. Forgets how to do things between sessions. Accessibility awareness minimal.

*Needs:* support, direction, easy-to-follow help materials, low-friction access
*Emotional goals:* working efficiently with minimal stress, feeling capable without deep training

### Axis 3: Approach

**Easy Going**
> "The university chose this platform so that is why I use it."

Follows platform conventions without pushback. Prefers simple, template-driven solutions. Works on smaller sites. Complies with accessibility and update requirements. Needs things to "just work."

*Needs:* updated look and feel, templates and ready-made solutions, help materials, content management
*Emotional goals:* working efficiently, feeling independent and capable

**The Inspired**
> "I saw a feature on a website that I loved and I wanted it for my site but due to lack of resources we couldn't easily add it."

Builds by idea or example. Excited by what is possible, frustrated when the platform or budget cannot deliver it. Often lacks the technical skill to build what they envision. Wants accessibility built in rather than added as an extra step.

*Needs:* help materials, updated visual design, content strategy support, accessibility baked into components
*Emotional goals:* motivated and creative, frustrated easily when blocked

**Mechanic**
> "A lot of my work is cleaning up past technical debt, using CSS injector to customize, and spinning up new sites for our department."

Knowledgeable but not at Expert level. Maintains multiple sites, fixes errors from other users, builds under constraint. Well-versed in accessibility. Values efficiency and reliability above all.

*Needs:* user permissions, accessibility tools, easy visual design, online help, content management
*Emotional goals:* working efficiently, independence, confidence

### 2021 Priority Combinations

| Priority | Combination | Rationale given |
|----------|-------------|-----------------|
| Primary, most likely user | Intermediate + Owner + Mechanic | Core active user base, skilled enough to have strong opinions, responsible enough to own outcomes |
| Secondary, needs most support | Uninformed + Team Player + The Inspired | Highest needs, most at risk of mistakes or giving up |

---

## 2021 Top User Needs

The five most-cited needs across 2021 interviews, surveys, and shadowing sessions, with current status noted.

| Rank | Need | 2021 citation rate | Status as of 2026 |
|------|------|-------------------|-------------------|
| 1 | Accessibility audit tool | 72% | Did not surface as a top-cited pain point in 2026. Absence of signal, not proof of resolution. WCAG 2.1 AA remains a platform requirement. |
| 2 | Updated look and feel | 61% | **Addressed.** Brand-compliant design appears as a 2026 delight. |
| 3 | User permissions and access | 55% | **Still live.** Appears as permission granularity limits for the Multi-Site Manager, and Users/Roles/Permissions is the largest ServiceNow support subcategory (35.6% of Feature Support tickets). |
| 4 | Support and help materials | 55% | **Mixed.** Learning resources are the top 2026 delight (50%), but findability is a top pain point: misleading Google results (61%) and weak documentation search. |
| 5 | Managing content | 50% | **Partially addressed.** Now narrower: rigid layout composition (44%) and structured data that does not scale (39%), concentrated in The Maintainer. |

---

## How 2021 Archetypes Map onto 2026

Approximate, for translating older documents. The mapping is loose because the models are structured differently.

| 2021 concept | Closest 2026 archetype | Caveat |
|--------------|----------------------|--------|
| Expert + Mechanic | Multi-Site Manager | 2026 emphasizes portfolio scale and delegation over raw technical depth |
| Owner | Part-Time Owner | **Significant reframe.** 2021 treated the struggling site owner as low-knowledge; 2026 finds they are often highly capable and constrained by time |
| Team Player | The Maintainer or New Recruit | 2026 splits these by whether the user has an established team workflow to follow |
| Uninformed + Dabbler | Part-Time Owner or New Recruit | 2026 explicitly rejects "uninformed" as the framing; infrequency and isolation, not ignorance, drive the need |
| The Inspired | Partially Solo Starter | 2026 has no direct equivalent; inspiration appears instead as a delight, "getting inspired from other sites" |
| No equivalent | Transitioning Team | D7 migration work was not a distinct archetype in 2021 |

**The headline shift:** 2021 modeled user need primarily as a function of **technical skill**. The 2026 research finds that **available time and access to an experienced colleague** predict user need better than skill does.
