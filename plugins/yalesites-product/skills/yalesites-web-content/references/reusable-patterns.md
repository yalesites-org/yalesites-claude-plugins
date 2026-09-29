# Reusable content patterns on YaleSites

Some content blocks aren't reinvented on every page. They're a house pattern, reused with small variations. Reaching for the existing pattern instead of writing a new version keeps the site consistent and saves the user from having to notice the drift later.

This file is a starting set, verified against real published pages. It should grow: if you notice a pattern repeating across pages that isn't captured here yet, say so, and add it.

## The support callout

Nearly every resource-style page ends with a short block offering help: a link to Office Hours and a link to email the team. It is not always worded identically, but the shape and the two links are constant. This is distinct from the sitewide alert banner and the global footer (see below); it's a mid-page block the author places intentionally, usually near the end.

**Verified real examples:**

From the homepage (`/`):
> ## Need Help or Have Feedback?
> Have a question or want to share feedback? Our team is ready to hear from you. Just reach out anytime.
> [Contact Us](mailto:yalesites@yale.edu)
>
> ## Want to Talk Live?
> Join our office hours to connect directly with the team. Ask questions, get help, or just say hi.
> [Join Office Hours](/trainings#officehours)

From the Getting Started with Siteimprove page (`/explore-resources/working-with-content/getting-started-with-siteimprove`):
> ## Need Help Getting Started?
> The YaleSites team is here to support your digital experience efforts:
> - [Attend Office Hours](/upcoming-events)
> - [Email YaleSites with Questions](mailto:yalesites@yale.edu)
> - [Explore our Resource Library](/explore-resources)

**When drafting a resource or user guide page, offer a version of this** near the end, sized to the page. A short page can use one line; a longer one can use the fuller list-based version. Keep the two anchor links constant:

- Office Hours: `/trainings#officehours` (the `#officehours` anchor is used consistently; don't drop it)
- Email: `mailto:yalesites@yale.edu`

A third link to the Resource Library (`/explore-resources`) appears in some variants and is worth including when the page is deep in a specific topic and a reader might want the broader index.

## The Office Hours alert banner

Every page carries a dismissible alert at the very top:

> ## Talk to a YaleSites expert at Office Hours
> Do you have YaleSites questions and would like to speak to a YaleSites expert? Come to office hours!
> [View upcoming office hours](/trainings#officehours)

This is sitewide chrome, not something an individual page draft controls. Don't try to reproduce it in page copy. Mention it only if a ticket is specifically about changing the sitewide alert itself.

## The footer support block

Every page ends with a "Find Support" / "Related Services Support" block linking to Get Started, the Training Catalog, the Resource Library, Contact YaleSites, and a second column linking to Usability & Accessibility, Siteimprove, Data Safety, and the legacy Drupal 7 sites.

Like the alert banner, this is global footer configuration, not something a page draft supplies. Don't include it in the "Page copy" section of a draft. If a ticket is about changing what the footer itself links to, that's a sitewide settings change, not a content page.

## Video demo embeds

Longer feature pages (Editorial Workflow is a good example) sometimes end with a short screen-recording walkthrough, embedded from Vimeo, under a "## Video Demo" heading. This is optional and tends to appear on pages describing a multi-step workflow rather than a single setting. Flag it as a possible addition in the handoff notes rather than assuming it's required, since producing the video is a separate task from writing the draft.
