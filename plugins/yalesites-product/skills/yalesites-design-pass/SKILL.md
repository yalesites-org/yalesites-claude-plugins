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
- **Timeline** (yalesites-org/YaleSites-Internal#2033): the acceptance criteria asked for a
  block picker icon, and none of the 15 signed-off mockups had one, so the developer used a
  placeholder. That is why every new block gets its picker icon in round 2.

## Setup: where the design runs (once per person)

The skill works for anyone on the team, with or without Claude Design. Each person's setup lives
in `~/.claude/yalesites/design-pass/config.json`, outside every repo:

```json
{
  "renderer": "claude-design-here | claude-design-other | html",
  "otherAccount": { "label": "Personal Claude", "app": "<path to the app, if any>" },
  "dataRuling": { "date": "YYYY-MM-DD", "scope": "brief.md only" },
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
   scope in `dataRuling`. The scope is always `brief.md only`: the brief is the one file that
   leaves the account.

**Every run, before round 1:**

- `claude-design-other` or `html`, and `checkedAt` is more than 30 days old: ask again whether
  the work account has Claude Design now. If it does, switch to `claude-design-here`. Whatever
  the answer, set `checkedAt` to today and save the config. Nothing else in the skill changes,
  since the rounds, the brief and the boards are the same for every renderer.
- `claude-design-other`: send only `brief.md`. Not the ticket, the parent, screenshots or board
  files. The brief itself never holds real site content, people's names or contact details,
  analytics exports, other tickets, or anything from email or Slack. If it would need any of
  those, leave it out or ask.

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

## Atomic design: build from the library, call out what is new

component-library-twig is organized by atomic design, and every design this skill produces is
too. The levels are its `components/` folders on `develop`:

| Level | CL folder | Examples |
|---|---|---|
| Tokens | `00-tokens` (and the tokens repo) | colors, spacing, type scale, theme slots |
| Atoms | `01-atoms` | controls (buttons), typography, images, forms, lists, divider, date-time |
| Molecules | `02-molecules` | cards, callout, accordion, tabs, office-hours, pager, link-group |
| Organisms | `03-organisms` | calendar, card-collection, galleries, tiles, site-header |

A block can be a molecule (Office Hours, Callout) or an organism (Calendar, Card Collection).
Say which, and why: an organism is made of molecules, a molecule of atoms.

Read the folder listing fresh each time (`gh api repos/yalesites-org/component-library-twig/contents/components/<level>?ref=develop`),
since it changes as the library grows.

**The rule is reuse first.** Every piece of a design is either an existing CL component, an
existing one with a change (a new variant, prop or modifier), or new. New is fine when it is
earned, but it is never silent:

- **Inventory every design.** For each approach and each iteration, list its parts by level,
  each marked **existing** (with a Storybook link), **changed** (what changes, and every other
  component that uses it), or **new**.
- **Call out anything new or changed, loudly.** On the board, in the brief, and in the handoff
  spec, each new or changed piece gets its level, why an existing component could not do the
  job (name the one you considered), and where else it could be reused. A new or changed
  **atom** or **token** carries the biggest blast radius, since everything above it inherits
  it: say so, and size it with `yalesites-portfolio` when it touches a component sites use.
- **Prefer the lowest-impact path.** Composing existing atoms and molecules beats a new
  molecule; a variant of an existing molecule beats a near-duplicate. When two approaches look
  equally good, recommend the one with fewer new pieces.
- **Name the home.** Every new piece gets its CL folder (`01-atoms/<name>`,
  `02-molecules/<name>`, `03-organisms/<name>`), so the developer does not have to decide.

## Before round 1: the gate

Read the ticket, its parent Feature (the `parent:` line in the `yalesites:agent` block), and,
for a Design ticket, the recorded answers on its UX sibling. Stop and ask (one question, in
chat) if any of these is missing. Do not guess them:

1. **Allowed regions.** Which Layout Builder regions the block can go in. The layouts are
   One column (Layout Builder core's `layout_onecol`), and from `ys_layouts`: Two column
   (50/50), Three column (33/33/33), Two column (70/30) and (30/70) with a main and a sidebar
   region, and Banner. Read the parent's `allowed_regions:` machine
   line first (the ticket skill writes it), then the prose. A ticket that says "one-column section"
   (yalesites-org/YaleSites-Internal#2033) has answered it. A parent that lists
   `allowed_regions` as an open decision (yalesites-org/YaleSites-Internal#1957) has not: on a
   UX ticket, make it one of round 1's questions; on a Design ticket, ask before starting.
2. **What the ticket asks to settle.** The open choices in its Acceptance Criteria. These are
   what the approaches must differ on.
3. **The renderer.** Read it from `config.json`. Only when there is no config, run the setup
   questions above first.

## Gather context (read-only)

Build one `brief.md` per ticket, kept with the board packet and carried forward into each
round's packet folder. On `claude-design-other` it is the only thing that leaves the account,
so write it as a brief, not a dump. In round 2, add the
reviewer's notes to the brief rather than sending them separately:

- The ask: the ticket's TL;DR and the open choices, in our words.
- Who it is for: the `ux-research` archetypes the feature touches, with the pain point each one
  has, in a sentence each.
- How the nearest blocks are used today: `yalesites-portfolio` adoption and two exemplar sites,
  so the approaches match how the community actually builds.
- Constraints: allowed regions with their widths (see `references/rounds.md`), themes it must
  hold up in, accessibility floor (WCAG 2.2 AA, 4.5:1 text, no state by color alone, visible
  focus), and the nearest existing components with their atomic level.
- Reuse: build from existing atoms and molecules; any new or changed component must be named
  and justified (see "Atomic design" above).
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
- Its component inventory (see "Atomic design" above), with a one-line cost: "Built from Card
  and Pager; adds 1 new molecule (Filmstrip), changes 1 atom (Button: icon-only size)". The
  cost of new pieces is part of what the reviewer is choosing between.

Board: one question, "Which approach do we take forward?", with each approach as an option and
a `compare` block per approach, our recommendation first, plus "Combine" (notes say how) and
"None of these" (notes say why). Put each approach's inventory line in its option text, so new
atoms, molecules and organisms are visible before the pick. A UX ticket adds one question per open product choice the
approaches do not already settle. Board mechanics are in `references/rounds.md`.

## Round 2: iterate the pick

Take the chosen approach, apply the reviewer's notes and markups, and show it the way a developer
will need it:

- Every allowed region width at desktop, plus phone (360) and tablet (768). Measure on a
  multidev or the published Storybook layout stories when the ticket depends on exact widths.
- Screenshots in at least two global themes plus one dark or colored section theme.
- **A contrast check against every section color.** Editors can put the block on any section
  color, and each section color changes with the site's global theme, so a block that passes
  on white can fail on a colored section nobody mocked up. Measure every text, icon, border and
  focus color in every state against all seven section themes (`default`, `one` to `six`) in
  each of the seven global themes. Screenshots stay a sample; the contrast table covers every
  pairing. How to measure it is in `references/rounds.md`, "Section color contrast".
- Edge cases: empty, one item, the most items allowed, the longest realistic title, a missing
  optional field, past and today states where dates are involved.
- The editor side: the block form in Layout Builder, field labels and help text a New Recruit
  understands.

- The inventory, updated: iterating often turns a "new" piece back into an existing one with a
  variant, or the reverse. Say what moved.
- **The block picker icon, for any ticket that adds a new block.** The tile editors see in
  Layout Builder's "Add a block" picker, drawn to match the existing set: an SVG at 501 by 261
  in the same flat style and palette, plus the picker category it goes in. A change to an
  existing block needs a new icon only when its look changes enough that the old icon misleads.
  Spec and files are in `references/rounds.md`, "Block picker icon".

Board: one question per area that still needs a call, each with the screenshots as a
`compare` block, then one question per new or changed component ("New molecule: Filmstrip.
Keep it new / Use <existing> with a variant / Rethink"), with the existing one it was weighed
against shown next to it. Any pairing that fails the contrast check gets its own question
with the failing section and global theme shown beside a passing one ("Use <token> on this
section / Hide <part> on this section / Rethink"). A new block adds its own **"Block picker icon"** question: the icon
beside two or three existing icons from the same category, with the category named
("Use this icon in Featured Content / Change the icon (notes) / Different category (notes) /
Decide later"). Close with "Sign off / Iterate again / Back to approaches". Sign-off
means every new and changed component, and a new block's picker icon, has been accepted on its
own question, and the contrast table has no open failure.
Iterate as many times as the reviewer asks. Each iteration is a new packet with its own id
(`design-<number>-r2-i2`, then `-i3`), so it opens on a blank board; see `references/rounds.md`.

## Round 3: handoff

After sign-off, write two things (templates in `references/handoff.md`):

1. **Handoff spec**, shaped like the Office Hours one in yalesites-org/YaleSites-Internal#1710:
   where each piece lands (which ticket), the component inventory with every new and changed
   atom, molecule and organism called out and its CL folder named, the structure and stack
   rule, theming with the section color contrast table, the states, the Storybook stories the
   library's testing guide requires, what to check first and report in the PR, plus the
   mockup zip.
   A new block's spec also carries its signed-off **block picker icon**: the image, the SVG
   in the zip, its file path in yalesites-project, and its picker category.
2. **Draft Storybook docs page** for the component: when to use it, anatomy, states with
   contrast, accessibility, regions and widths, theming, block form and help text (with the
   picker category and icon for a new block), do and don't. The developer turns it into
   the component's `.mdx` in component-library-twig. Today most CL docs pages are a canvas,
   controls and a props table; this is the part that keeps the component supportable after
   the people who designed it move on.

Both are **drafts**. Show them to the reviewer on the board. Posting the spec as a ticket comment
happens only when the reviewer says so, with images through `github-screenshots`. Neither
`github-screenshots` nor `gh` can attach a zip, so the reviewer drags the mockup zip into the
next comment by hand; copy it into the round 3 packet folder
(`~/.claude/yalesites/design-pass/packets/design-<number>-r3/`) and tell them its path.
The ticket's acceptance criteria often ask for each answer as a comment; draft those too.

## Rules

- Never posts to GitHub without the reviewer's go-ahead (see round 3), never moves board
  status, never closes a ticket. The router hands the phase off once the reviewer closes it.
- On `claude-design-other`, never sends anything beyond `brief.md`.
- Never ships one approach as "the" design. Round 1 always offers a real choice.
- Region widths are a gate, not a nice-to-have. So is contrast on every section color.
- Never adds a new or changed atom, molecule, organism or token without calling it out by name
  and level, with the existing component it was weighed against.
- A new block never reaches round 3 without a signed-off picker icon. Leaving it to the
  developer means a placeholder ships.
- Write as "we", no em dashes, `owner/repo#N` refs, per `ticket/references/github-writing.md`.

## Orchestrator

Optional. If you run the work dashboard's orchestrator, its `design-pass` lane (in the
dashboard's `lanes.json`) runs round 1 on one ticket at a time: a UX or Design child assigned to
you, whose earlier phase is closed and which has no open board. Its board lands in the
dashboard's "Check the agent's work" bucket. Rounds 2 and 3 run when you answer. When the gate
above fails, the lane writes a needs-you question instead, which lands in "Only you". Without
the dashboard, run the skill by hand; nothing else changes.
