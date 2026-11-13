# Question coverage

The ground a feature plan has to cover. Step 5 drafts a question for every row that research did
not already settle, then drops, pulls out, and ranks them. Not every feature needs every row.

Questions are listed roughly in blast-radius order: the earlier rows tend to decide which later
rows exist.

## Scope

| Ground | Example question | Settles |
|---|---|---|
| The problem | "Is the problem that editors can't do X, or that they can but can't find it?" | Feature vs docs and training. An "already exists" finding lands here |
| Who it is for | "Build it for the Multi-Site Manager who asked, or for every editor?" | How much UI it gets, and where it lives |
| Placement | "A per-block option, a page setting, or a sitewide setting?" | Which defaults, roles, and docs questions exist |
| The smallest useful version | "Ship the single-layout version first, or wait for all three?" | Phases, timeline, and what goes in Out of scope |
| Out of scope | "Leave the sibling blocks alone for now?" | What the ticket explicitly does not promise |

## Existing sites

| Ground | Example question | Settles |
|---|---|---|
| Default for existing sites | "Off for the 140 sites that use this block today, or on?" | Whether a deploy changes live sites with no action |
| Existing content | "Leave existing instances as they are, or convert them?" | Whether an update hook is needed |
| Communication | "Do site owners hear about it before it ships, or in the release notes?" | Comms and Docs phases |

## Interactions

One question per **unknown** from the interaction checklist that is a product call. Technical
unknowns go to the lead developer instead. Typical ones:

- "Should the sibling card blocks get the same option?"
- "Should this show in all palettes, or only the ones where it passes contrast?"
- "Should editors see this, or only site admins?"

## Feasibility and effort

Research names the options and their costs. The PM picks between them as a product tradeoff;
the technical approach behind each stays with the lead developer.

| Ground | Example question | Settles |
|---|---|---|
| Build vs adopt | "Adopt the contrib module, with its limits, or build only what we need?" | Effort, and a dependency to maintain |
| Front-end reach | "Accept a design that fits the existing component, or a new variant across three repos?" | Repo count, which drives timeline |
| Parity | "Match the UICL version, or leave UICL for later?" | Scope of the parity work |

## Timeline

| Ground | Example question | Settles |
|---|---|---|
| Target release | "Target the 12-08-26 release, or the one after?" | Milestone |
| Phases | "Does this need UX and Design, or go straight to Development?" | Phase children and their order |
| Hard dates | "Does the semester start make January a must?" | Whether scope shrinks to meet a date |

## Measure

| Ground | Example question | Settles |
|---|---|---|
| Success | "How will we know it worked: support tickets drop, adoption in the next crawl, a named site uses it?" | What we check after release |

## Never asked as PM questions

Implementation approach, data model, plugin vs config entity, refactoring, caching strategy,
performance tradeoffs, test strategy. List each on the lead-in under **Not asked** as "for our lead
developer," and record it as an open item for `dblanken-yale`.
