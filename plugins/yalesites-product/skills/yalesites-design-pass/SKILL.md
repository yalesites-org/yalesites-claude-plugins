---
name: yalesites-design-pass
description: "Run an agentic first design pass on a YaleSites UX or Design phase ticket (a `<Feature>: UX` or `<Feature>: Design` child in yalesites-org/YaleSites-Internal), so the reviewer reviews and signs off on drafts instead of starting from a blank page. Three rounds, each on a local review board: round 1 shows three or four genuinely different approaches; round 2 iterates the one picked, at desktop and phone and at every Layout Builder region width the block is allowed in, across themes and edge cases; round 3 writes the developer handoff spec and a draft Storybook docs page for the component. Mockups come from Claude Design using the YaleSites Design System, or from HTML mockups built on the published component library CSS and tokens. Use when the user says 'do a first design pass on 2013', 'draft designs for the gallery carousel', 'start the UX for X', 'give me design options for this ticket', 'iterate on approach B', 'write the design handoff', or when the work dashboard's design-pass lane picks a ticket. A human always signs off; this skill never posts to GitHub on its own."
argument-hint: "[ticket, e.g. yalesites-org/YaleSites-Internal#2013] [round: approaches | iterate | handoff]"
---

# YaleSites Design Pass

UX and design tickets are the work that most needs a person's judgment, so they are the last
thing we want an agent to decide. They are also the work that most often starts from a blank
page. This skill closes that gap: it does the first pass and the legwork, and puts every choice
in front of the reviewer on a board. The reviewer picks, iterates, and signs off. Nothing ships on the
agent's say-so.

The shape comes from work that went well:

- **Office Hours** (yalesites-org/YaleSites-Internal#1710): several approaches first, one
  picked, iterated, then a handoff spec and an HTML mockup zip the developer built from in
  yalesites-org/YaleSites-Internal#1542, #1704, #1705 and #1707. The one thing that bit late
  was width: the 305px sidebar overflowed. That is why region widths are a hard gate here.
- **Event Calendar, compact list** (in Claude Design, not yet approved): its "States and
  handoff details" page listed every state with its contrast ratio, the keyboard focus order,
  screen reader labels, and the block form choices. That page is a Storybook docs page in all
  but format, which is why round 3 drafts one.

## Setup: where the design runs (once per person)

The skill works for anyone on the team, with or without Claude Design. Each person's setup lives
in `~/.claude/yalesites/design-pass/config.json`, outside every repo:

```json
{
  "renderer": "claude-design-here | claude-design-other | html",
  "otherAccount": { "label": "Personal Claude", "app": "<path to the app, if any>" },
  "dataRuling": { "date": "YYYY-MM-DD", "scope": "brief, ticket, parent, public links, placeholder content" },
  "exportFolder": "~/Downloads",
  "checkedAt": "YYYY-MM-DD"
}
```

**No config yet:** ask once, in one `AskUserQuestion` call, then write the file.

1. **Does the Claude account you are using for this work have Claude Design?** Yes, No, Not sure.
   Yes sets `claude-design-here`, the simplest case: nothing leaves the account.
2. **Only if No or Not sure: do you have Claude Design on another account?** If not, set `html`.
   If yes, say plainly that running the pass there sends the ticket's design brief outside
   Yale's enterprise agreement, that whether that is allowed is the user's call (and possibly
   their manager's), not ours, and offer `html` as the option that keeps everything in. Set
   `claude-design-other` only on an explicit yes, and record their ruling with its date and
   scope in `dataRuling`.

**Every run, before round 1:**

- `claude-design-other` or `html`, and `checkedAt` is more than 30 days old: ask again whether
  the work account has Claude Design now. If it does, switch to `claude-design-here`. Nothing
  else in the skill changes, since the rounds, the brief and the boards are the same for every
  renderer.
- `claude-design-other`: send only what `dataRuling.scope` covers. Never real site content,
  people's names or contact details, analytics exports, other tickets, or anything from email
  or Slack. If the brief would need any of those, leave it out or ask.

| Renderer | How it runs |
|---|---|
| `claude-design-here` | The design runs in Claude Design in the same account with the YaleSites Design System attached; the export (zip or PNGs) lands in `exportFolder`, and we build the board from it |
| `claude-design-other` | Same, in the other account: we write the brief and open the other app if `otherAccount.app` is set; the user starts the design there |
| `html` | Static HTML that loads the published component library CSS and tokens, rendered at each width by headless Chromium. Also the fallback for a quick variant or a side-by-side check in any setup |

Claude Code does not drive Claude Design yet, so the hand-over is manual in both Claude Design
setups: we write the brief and open what we can, the user runs the design, and we pick up the
export. Do not click through another app's interface on the user's behalf unless they ask in
that session.

## The design system artifact

On either Claude Design setup, the account needs the **YaleSites Design System** artifact
attached, or Claude Design invents its own Yale.

- **Check it is there.** Ask the user if it is not in their config's account yet. To create it,
  use a design system export (a folder with `IMPORT.md` and `project/`), which explains how to
  recreate the artifact in another account. The export is not in this repo, because it bundles
  licensed Yale fonts (Yale New, Mallory); ask the YaleSites product team for the current one.
  The 2026-10-14 export holds about 38 components, 430 tokens, all 25 themes (7 global, 6 basic,
  5 component, 7 CTA), 97 icons, a page template and a Site UI Kit, built from
  component-library-twig `develop` and tokens `main`.
- **Check it is current.** Compare its readme's Coverage list and the newest components in
  `component-library-twig` (`git log --since` on `components/`). If the CL has gained components
  or token changes since the export, tell the user what is missing and offer to refresh it
  first. A stale system makes every approach look slightly off-brand.
- On `html`, the published Storybook CSS and the tokens repo are the design system; nothing to
  set up.
- The ticket's own component is usually not in the system yet (it is new). Say which existing
  components are the nearest starting point (Media Grid for a carousel, Calendar for an event
  view), so the approaches build from them instead of from scratch.

## Before round 1: the gate

Read the ticket, its parent Feature (the `parent:` line in the `yalesites:agent` block), and,
for a Design ticket, the recorded answers on its UX sibling. Stop and ask (one question, in
chat) if any of these is missing. Do not guess them:

1. **Allowed regions.** Which Layout Builder regions the block can go in. The layouts are
   One column, Two column (50/50), Three column (33/33/33), Two column (70/30) and (30/70),
   each with a main and a sidebar region, and Banner. Read the parent's `allowed_regions:` machine
   line first (the ticket skill writes it), then the prose. A ticket that says "one-column section"
   (yalesites-org/YaleSites-Internal#2033) has answered it. A parent that lists
   `allowed_regions` as an open decision (yalesites-org/YaleSites-Internal#1957) has not: on a
   UX ticket, make it one of round 1's questions; on a Design ticket, ask before starting.
2. **What the ticket asks to settle.** The open choices in its Acceptance Criteria. These are
   what the approaches must differ on.
3. **The renderer.** Claude Design or HTML mockups. Default to Claude Design.

## Gather context (read-only)

Build one `brief.md` per ticket, kept with the board packet. On `claude-design-other` it is also exactly
what leaves the account, so write it as a brief, not a dump:

- The ask: the ticket's TL;DR and the open choices, in our words.
- Who it is for: the `ux-research` archetypes the feature touches, with the pain point each one
  has, in a sentence each.
- How the nearest blocks are used today: `yalesites-portfolio` adoption and two exemplar sites,
  so the approaches match how the community actually builds.
- Constraints: allowed regions with their widths (see `references/rounds.md`), themes it must
  hold up in, accessibility floor (WCAG 2.2 AA, 4.5:1 text, no state by color alone, visible
  focus), and the nearest existing components.
- Links: the published Storybook stories for the nearest components, and the CL and tokens
  repos. All public.
- Placeholder content: invent realistic Yale-flavored placeholder titles and dates. Never copy
  content from a real site.

## Round 1: approaches

Three or four approaches that are **genuinely different**, each a different answer to the
ticket's open choices (thumbnails versus dots versus a count; a peek of the next image or
not). Not color swaps, not the same layout at two sizes. Each approach gets:

- A name a person can say out loud ("Filmstrip", "Quiet dots"), never "A" or "B".
- One desktop mockup (1440) and one phone mockup (360) in the widest region it is allowed in.
- Two or three lines: what it is good at, who it serves (an archetype), and its main risk.

Board: one question, "Which approach do we take forward?", with each approach as an option and
a `compare` block per approach, our recommendation first, plus "Combine" (notes say how) and
"None of these" (notes say why). A UX ticket adds one question per open product choice the
approaches do not already settle. Board mechanics are in `references/rounds.md`.

## Round 2: iterate the pick

Take the chosen approach, apply the reviewer's notes and markups, and show it the way a developer
will need it:

- Every allowed region width at desktop, plus phone (360) and tablet (768). Measure on a
  multidev or the published Storybook layout stories when the ticket depends on exact widths.
- At least two global themes plus one dark or colored section theme.
- Edge cases: empty, one item, the most items allowed, the longest realistic title, a missing
  optional field, past and today states where dates are involved.
- The editor side: the block form in Layout Builder, field labels and help text a New Recruit
  understands.

Board: one question per area that still needs a call, each with the screenshots as a
`compare` block, and a closing question "Sign off / Iterate again / Back to approaches".
Iterate as many times as the reviewer asks; archive each round's `answers.json` before the next.

## Round 3: handoff

After sign-off, write two things (templates in `references/handoff.md`):

1. **Handoff spec**, shaped like the Office Hours one in yalesites-org/YaleSites-Internal#1710:
   where each piece lands (which ticket), the structure and stack rule, theming, the states,
   what to check first and report in the PR, plus the mockup zip.
2. **Draft Storybook docs page** for the component: when to use it, anatomy, states with
   contrast, accessibility, regions and widths, theming, block form and help text, do and
   don't. The developer turns it into the component's `.mdx` in component-library-twig. Today
   most CL docs pages are a canvas, controls and a props table; this is the part that keeps the
   component supportable after the people who designed it move on.

Both are **drafts**. Show them to the reviewer on the board. Posting the spec as a ticket comment, and
attaching the zip, happens only when the reviewer says so, through `github-screenshots` for images.
The ticket's acceptance criteria often ask for each answer as a comment; draft those too.

## Rules

- Never posts to GitHub, never moves board status, never closes a ticket. The router hands the
  phase off once the reviewer closes it.
- On `claude-design-other`, never sends anything beyond the brief and what `dataRuling.scope` covers.
- Never ships one approach as "the" design. Round 1 always offers a real choice.
- Region widths are a gate, not a nice-to-have.
- Write as "we", no em dashes, `owner/repo#N` refs, per `ticket/references/github-writing.md`.

## Orchestrator

Optional. If you run the work dashboard's orchestrator, its `design-pass` lane (in the
dashboard's `lanes.json`) runs round 1 on one ticket at a time: a UX or Design child assigned to
you, whose earlier phase is closed and which has no open board. Its board lands in the
dashboard's "Check the agent's work" bucket. Rounds 2 and 3 run when you answer. When the gate
above fails, the lane writes a needs-you question instead, which lands in "Only you". Without
the dashboard, run the skill by hand; nothing else changes.
