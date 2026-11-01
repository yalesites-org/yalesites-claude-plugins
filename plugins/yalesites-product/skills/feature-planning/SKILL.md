---
name: feature-planning
description: "Run a planning session for a new YaleSites feature before it becomes a ticket: research the idea from every source we can reach (the yalesites-project code and the component library repos, the portfolio crawl, Pantheon, GitHub history, UX research, the docs site, live sites, and external research on other higher ed Drupal platforms, higher ed CMSes, and general CMSes, in that order of weight), then ask the PM the questions that settle the most, ranked by blast radius, with the evidence beside each one. Covers scope, placement, defaults for existing sites, interactions with other features, accessibility, feasibility options, and timeline. Ends in a decision record (decided, deferred, open with an owner) and hands it to the ticket skill to write the feature parent and phase children. Use when the user says 'let's plan a feature', 'planning session for X', 'help me think through X before we ticket it', 'what would it take to add X', 'flesh out this feature idea', or names a forming ticket and wants to decide it out. For writing or grooming a ticket whose decisions are already made, use the ticket skill directly."
---

# YaleSites Feature Planning

A planning session turns a feature idea into decisions. The PM makes the product calls. This
skill does the research first, so every question arrives with the evidence that bears on it, and
asks the questions in the order that settles the most. It ends in a **decision record**, which
the `ticket` skill turns into a feature parent and its phase children.

This skill sits upstream of `ticket`. It does not write tickets itself, and nothing posts to
GitHub without the user seeing the draft first.

## Ground rules

- **Sibling paths go through `realpath`.** Paths like `../ticket/...` and `../pr-feedback/...`
  point at sibling skills in this plugin. If this skill is symlinked (into `~/.claude/skills`
  for testing, say), resolve its folder with `realpath <skill-dir>` first, or those paths miss.
- **The PM decides product calls. Nobody here decides architecture.** Questions about
  implementation approach, data model, refactoring, or system design are not asked as PM
  questions. They are listed on the board under **Not asked** as "for our lead developer"
  (`dblanken-yale`), and they become `needs-decision` items for the lead developer in the ticket. Feasibility
  research names the options and what each would cost; it does not pick one.
- **Research is read-only.** No config changes, no deploys, no content edits, no signing in to
  anything outside our own tools. Pantheon commands are limited to the read list in
  `references/research-sources.md`.
- **Say what you could not check.** A source that was unavailable is reported as skipped, never
  treated as "no impact."
- **Evidence, not verdicts, from outside.** External findings are context under a question.
  They never become the recommendation on their own, and our own portfolio data outweighs them.
- **Writing.** Anything that will land on GitHub follows `../ticket/references/github-writing.md`
  and passes `../ticket/scripts/check-github-text.py`. In chat and on the board, no em dashes,
  "we" not "I", lead with the point.

## Step 0: Take in the idea

Get the idea in a sentence or two. It can come from the user's message, a `forming` intake stub,
an existing ticket (read it with `gh issue view <n> --repo yalesites-org/YaleSites-Internal
--comments`), or a ServiceNow request the user pastes.

Note four things before researching. Ask in chat only for the ones you can't infer, in one
message:

1. **The problem**, in the requester's terms, not the solution they proposed.
2. **Who asked**, and how many (one site owner, a pattern across support tickets, a leadership ask).
3. **Any hard date** (a semester start, an event, a contract).
4. **What it would touch**, as a first guess (a block, a setting, a content type, the editor UI,
   the theme). Research will correct it.

Make a working folder in the scratchpad: `<scratchpad>/feature-planning/<slug>/`. The research
notes, the board packet, and the decision record all go there.

## Step 1: Check which sources are available

Before researching, check each source in `references/research-sources.md` and list the result in
one short chat message ("Using: code, portfolio, GitHub, UX research, docs site, browser, web.
Skipped: Pantheon, Terminus is not logged in."). If a skipped source matters for this feature,
say why and what the user can do (`terminus auth:login`), then carry on without waiting.

## Step 2: Internal research

Work through every source in `references/research-sources.md`, in the order there. For each one,
the file says what to look for and the exact read-only commands. Spend effort in proportion to
the feature: a new option on one block needs less than a new content type.

Then run the interaction pass in `references/interaction-checklist.md`. It is a fixed list of the
places features collide on YaleSites (Layout Builder against Manage Settings, themes and palettes,
the component library repos, existing sites' config, accessibility, Views, search, roles, docs).
Mark each one: touched, not touched, or unknown. "Unknown" is a question for the board or for the
lead developer.

Write the findings to `research.md` in the working folder, one section per source, each finding
with its link and date. This is the evidence the board cites, and it goes in the ticket's
collapsed Background and analysis block later.

## Step 3: External research

Search outward in this order. The tier is how much weight a finding gets:

| Tier | Where | Why it counts |
|---|---|---|
| 0 | **Drupal itself**: drupal.org issue queues, contrib modules, Drupal CMS (Starshot) | Answers "does a module already do this?" and "is core about to change this?", which bear on feasibility and timeline |
| 1 | **Higher ed Drupal platforms**: managed multisite Drupal for departments (e.g. Stanford Sites, Harvard's OpenScholar; find others) | Same platform shape, same editors. Some publish code on GitHub |
| 2 | **Other higher ed CMSes**: Cascade, Modern Campus (Omni CMS), Terminalfour, university WordPress multisite | Same users and editor problems, different stack |
| 3 | **General CMSes**: WordPress block editor, Squarespace, Webflow, Contentful, Sanity | Editor experience and content modeling ideas |

For each tier, look for: whether they built this, how editors use it (public docs, demos,
changelogs), what they chose to leave out, and any public sign it went badly. Stop a tier when it
has given two or three solid findings, or when it clearly has nothing.

Rules for external findings:

- **Public sources only.** Never sign in, never fill a form, never accept a cookie banner beyond
  declining non-essential ones.
- **Verify it is current.** Schools move platforms. Check that a platform still runs what you are
  citing before citing it, and say when you could not tell.
- **Date and link every finding**, and tag its tier in `research.md`.
- **Weigh it.** Tier 3 is a source of ideas. Our portfolio data and our editors' pain points
  outweigh any external pattern.

## Step 3b: Capture the visual evidence

Most feature questions are easier to answer from a picture than a description, and a new block
has no live YaleSites instance to show. So capture pictures on purpose, following
`references/visual-evidence.md`:

1. **Inspiration from the external research.** For each strong tier 0 to 3 finding, a screenshot
   of the real thing: the other school's version on a live page, the WordPress or Webflow
   pattern, their editor docs when public. Labeled with source, tier, and date, and linked.
2. **Our closest current option.** What editors use today to work around the gap, on a heavy-use
   site from the portfolio. This is the "what they do now" side of every comparison.
3. **Component library starting points.** The Storybook story for any existing component the
   feature could build on or extend.
4. **The affected area today,** for a change to something that exists: the block or setting on
   its heaviest-use sites, at the widths where layout matters.

Any question about layout, direction, or appearance gets a side-by-side `compare` block of its
options, never a text description of them. If no picture exists for an option, say so in the
option's `detail` rather than describing it as if there were one.

These images are for the user's decision on the local board only. They never go into tickets,
docs, or anything published; the ticket links to the sources instead.

## Step 4: Share the research brief

Before asking anything, post a short brief in chat, five to eight lines: what the feature would
touch, the blast radius in numbers (sites, block instances, roles), the strongest internal
finding, the strongest external finding, and anything that already settles a question. Link
`research.md`. This is where the user catches a wrong first guess before it shapes the questions.

If the research shows the feature **already exists** or **conflicts with platform direction**
(the classifications in `../ticket/SKILL.md`, "Platform Fit Check"), lead with that. The session
may end here, and that is a good outcome.

## Step 5: Build the question set

Draft every question the plan needs, using the coverage list in
`references/question-coverage.md` so nothing standard is missed. Then shape the set:

1. **Drop what research already answered.** List those on the lead-in as settled, with the
   evidence, so the user can still object.
2. **Pull out architecture questions.** They go under **Not asked**, for the lead developer.
3. **Rank by blast radius.** Ask first the questions whose answer removes or changes other
   questions, and the ones that change how many sites are affected. "Per-block option or
   sitewide setting?" comes before "What should the default be?", because its answer decides
   which default question even exists. Each question says what it settles in its brief.
4. **Group into parts:** usually Scope, Interactions, Feasibility and effort, Timeline. A part
   with no questions left is dropped.
5. **Give every question two to four concrete options, our recommendation first,** each with the
   cost of choosing it, plus "Decide later" (it becomes an open item with an owner). Recommend
   only where the evidence supports it, and put that evidence in the option's `detail`.
6. **Put the evidence beside it.** The screenshots from Step 3b, the adoption number, the other
   school's editor doc, the relevant code or ticket text with the key line highlighted. A
   question about how something should look shows its options side by side. The user should be
   able to answer from the page without opening another tab.

## Step 6: Ask

- **Three or fewer quick questions:** ask in chat with `AskUserQuestion`.
- **Four or more, or any that need a screenshot or a side-by-side:** use the planning board,
  following `references/planning-board.md`. Serve it locally, open it, and wait for Send. The
  answers on the board are the ruling. Do not re-ask them in chat.

**One follow-up round, at most.** Answers often open a few new questions (choosing "sitewide
setting" raises "on or off for existing sites?"). Ask those in chat if there are three or fewer,
otherwise on a second, smaller board. If a third round looks needed, the idea is not ready to
ticket: say so, record what is decided, and leave the rest open.

## Step 7: Write the decision record

Write `decision-record.md` in the working folder, using `references/decision-record.md`. It holds:
what we are building and for whom, each decision with its reason and evidence, what is out of
scope, open items with an owner and a date, the interaction map, the phases that apply, the
timeline recommendation, and the risks. Show it to the user in chat, short form, and link the file.

**Timeline.** Read the live milestones the way `../ticket/SKILL.md` ("Milestone") does, with the
same two traps (past due dates, releases already in RC). Recommend a target release from the
phases that apply, how many repos the work spans, and any hard date from Step 0. It is a
recommendation for the PM, not an estimate on the developers' behalf: if the timeline depends on
dev effort, say so and make it an open item for the lead developer.

## Step 8: Hand off to the ticket skill

Ask whether to write the ticket now. On yes, invoke the `ticket` skill (`yalesites-product:ticket`)
with the decision record, and tell it which fields are already decided so it does not ask again:
the phases, milestone, priority, risk, and owners the session settled. The ticket skill writes the
feature parent and phase children (or a single ticket for a small enhancement), puts the research
summary in the collapsed Background and analysis block, and raises each open item as a
`needs-decision` or `follow-up` block. It shows the drafts before posting, as it always does.

If an existing ticket started the session, the ticket skill grooms that ticket instead of making a
new one.

## Cleanup

Stop the board server you started and undo any `.claude/launch.json` entry, as in
`references/planning-board.md`. Leave the working folder: `research.md` and the decision record
are the record of the session.
