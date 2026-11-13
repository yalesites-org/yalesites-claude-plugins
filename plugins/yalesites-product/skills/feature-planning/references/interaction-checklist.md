# Interaction checklist

The places YaleSites features collide. Run every row in Step 2 and mark it **touched**, **not
touched**, or **unknown**, with one line of evidence for touched and unknown. The result is the
interaction map in the decision record.

An unknown is never left as a guess. It becomes a question for the PM if it is a product call, or
an open item for the lead developer if it is a technical one.

| Area | Ask | Why it bites |
|---|---|---|
| **Layout Builder vs Manage Settings** | Does this belong in the block's Layout Builder form, the page's Manage Settings, or sitewide settings? | Editors already confuse the two. A setting in the wrong place adds to the top pain point (confusing terminology) |
| **Block family** | Do sibling blocks share the template or form (cards, collections, banners, heroes)? Should the change reach them too? | Changing one sibling and not the others reads as a bug to editors |
| **Themes and palettes** | Does it look right in every theme and color palette, and in the dark sections? | Each combination is a visual regression case |
| **Component library** | Which of component-library-twig, atomic, tokens, and yale-ui-cl change? | Each repo is its own PR and review, which drives the timeline |
| **Existing sites** | What happens to sites that already use this, on the next deploy, with no action? Is the change opt-in, a new default, or applied by an update hook? | This is the blast radius. A changed default reaches every site in the portfolio count |
| **Content and migration** | Does existing content need to change shape? Does the D7 migration tooling or the starterkit need to know about it? | Content changes need update hooks and are hard to undo |
| **Accessibility** | Does it add interaction, motion, color, or a new heading or landmark? | WCAG 2.1 AA review by `ntay90`, and an AC line |
| **Roles and permissions** | Which roles see it: site admin, site builder, editor? Does it need a new permission? | A setting only admins see may not reach the people who asked for it |
| **Views and listings** | Does it change how content appears in Views, collections, or search results? | Listings are where content shows up away from its page |
| **Search and AI** | Does it change indexed content or what Beacon and the AI features read? | Search quality is a top pain point; Beacon answers can shift |
| **Integrations** | Localist, CAS, analytics, ServiceNow, embeds? | Outside systems have their own owners and timelines |
| **Performance and caching** | Does it add per-page queries, external calls, or cache variation? | Hard to see in review, shows up on big sites |
| **Docs, training, and comms** | Which yalesites.yale.edu pages change? Does it need a release email mention or a training update? | The Docs phase and the comms workstream need lead time |
| **UICL parity** | Does UICL already have this, or will it need a matching change? | Parity gaps pile up quietly |
