# The shape of yalesites.yale.edu

There is no crawl tool here. `WebFetch` loads one page at a time. Don't describe the site's contents as if you'd surveyed all of it; you've only seen what you fetched.

What makes this manageable: YaleSites renders its full top-level navigation in the markup of every single page. Fetching any one published page, even one unrelated to your task, gives you the current primary nav for free. Use that instead of guessing at section names, and re-fetch periodically since this list will drift.

## Verified top-level sections (checked August 2026)

| Section | URL | What lives here |
|---|---|---|
| **Platform** | `/continuous-improvement` | YaleSites Advantage, Release Notes, Product Roadmap, Current Issues & Fixes. Platform-direction and release material. |
| **Community** | `/community` | Building YaleSites Together, Development, Common Requests, Working with a Vendor. How the YaleSites community and contribution model works. |
| **Resource Library** | `/explore-resources` | Learn the Basics, Working With Content, User Guide, Tips and Tricks. The largest section, and where most editor-facing documentation lives. |
| **Trainings** | `/trainings` | Scheduled trainings and Office Hours signup. `#officehours` is a real in-page anchor, used constantly as a link target across the site. |
| **Get Started** | `/get-started-with-yalesites` | Onboarding for a brand-new site. |
| **Support** | `/support` | General support entry point. |

## Inside Resource Library: the User Guide

The User Guide (`/explore-resources/user-guide`) has its own left-hand nav, distinct from the top-level one, built with a mechanism called Content Collections (see `/secondary-navigation-with-content-collections`). As of August 2026 it has these sections and children:

- **Building Your Site** — Content Types, Manage Settings, Edit Layout and Content, Create Powerful Page Sections, Building with Blocks, Sitewide Settings, Secondary Navigation with Content Collections, Working with Images in YaleSites
- **Managing Site Content** — Building Your Menu, Editorial Workflow, Google Tag Manager, Media Library, Using Taxonomy and Vocabulary
- **Creating Accessible Content** — Accessibility with Editoria11y
- **Term Glossary**
- **Go-Live Checklist**

Don't treat this list as permanent. Verify it by fetching `/explore-resources/user-guide` or any of its children before relying on it for nav placement, since the whole point of this reference is to save a fetch, not to replace one when accuracy actually matters.

## Checking for overlap before creating a new page

Before drafting a brand new page, fetch the hub page for the section it would live under and skim the existing children. Two failure modes to avoid:

- **Missing an existing page that already covers this**, and drafting a duplicate.
- **Missing a close-but-not-quite match**, where the right move is editing the existing page rather than adding a new one.

If you find something close, surface it and ask which way to go rather than deciding alone. This is exactly the kind of call worth checking rather than guessing, per the skill's main workflow.

## Other domains referenced from YaleSites content

Content on yalesites.yale.edu regularly links out to a small set of other Yale domains. Know these so you don't mistake them for YaleSites pages or apply the relative-link rule to them by mistake:

- `usability.yale.edu` — Usability & Web Accessibility, including Siteimprove documentation
- `cybersecurity.yale.edu` — Yale data classification guidance
- `legacy.yalesites.yale.edu` — the old Drupal 7 platform
- `privacy.yale.edu` — Yale's privacy statement

These stay absolute. Only links to yalesites.yale.edu itself should be relative.
