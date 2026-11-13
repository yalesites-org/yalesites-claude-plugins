# Rounds: widths, files, and board mechanics

## Region widths

One column is Layout Builder core's `layout_onecol`. The rest come from `ys_layouts` in
yalesites-project (`ys_layouts.layouts.yml` on `develop`), which also defines Page Meta, a page
header layout and not a block region. The widths below are content widths at a 1440px viewport. Only the two marked "measured" were
measured (on pr-1477 for Office Hours, yalesites-org/YaleSites-Internal#1710); measure the rest
on a multidev or the published Storybook layout stories before a ticket depends on them, and
update this table.

| Region | Layout | Width at 1440 | Notes |
|---|---|---|---|
| One column | One column | full content width | The widest. Every block's default |
| Half | Two column (50/50) | about half | |
| Third | Three column (33/33/33) | 411px, measured | Time ranges and short labels start wrapping |
| Main | Two column (70/30) and (30/70) | about 70% | |
| Sidebar | Two column (70/30) and (30/70) | 305px, measured | The hard one. Office Hours overflowed here |
| Banner | Banner | full bleed | Only for banner-type blocks |
| Any, phone | any layout at 360px | about 298px | Columns stack; check the sidebar case's content again here |

Show every region the block is allowed in, never only the widest. If a block is allowed in the
sidebar, the sidebar mockup is the one that matters most. Prefer container queries over viewport
breakpoints in the spec, since the same block sits in regions of different widths on one page
(the Office Hours stack rule: rows stack under 340px of block width).

## Files

One folder per board packet in a durable folder, not the session scratchpad, since rounds 2 and 3
often run in a later session. It mirrors docs-board's `~/.claude/yalesites/docs-board/packets`.
Every round, and every "Iterate again" within a round, gets its own packet id, and the folder is
named for it:

```
~/.claude/yalesites/design-pass/packets/
  design-<number>-r1/        round 1
  design-<number>-r2/        round 2, first pass
  design-<number>-r2-i2/     round 2 after one "Iterate again" (then -i3, -i4, ...)
  design-<number>-r3/        round 3
```

A fresh id is what gives each round a blank board. The board saves the reviewer's picks in the
browser under `review-board:<packet id>` and restores them on load whenever the saved answer count
matches the packet's question count, and nothing clears them. A reused id would open the next
round with the last round's picks already made. Never rebuild an earlier round's folder for a new
round; make the next id.

Each folder holds what its round shows, plus the brief carried forward:

```
design-<number>-r<round>[-i<n>]/
  brief.md                 what goes to Claude Design; on claude-design-other, the only file that leaves.
                           Copy it from the previous folder and add this round's notes
  packet.json              the board
  r1-<approach>-1440.png   round 1, one desktop and one phone per approach
  r1-<approach>-360.png
  r2-<region>-<theme>.png  round 2
  <block>.svg              round 2, new blocks only: the block picker icon, named as it will be
                           in yalesites-project (e.g. timeline.svg); carried into r3 and the zip
  r2-picker-<category>.png round 2: the icon beside its category neighbors
  contrast.json            round 2: every section x global theme pairing, carried into r3
  handoff.md               round 3 spec draft
  storybook-docs.mdx       round 3 docs draft
  answers.json             written by the board
```

Name images by what they show, never by letter. Copy the Claude Design export (zip or PNGs from the
config's `exportFolder`) into the folder; never point the board at the export folder directly.

## Section color contrast

Section themes are the background colors editors pick per Layout Builder section. The
component library (`components/_storybook/theme-constants.js` on `develop`) lists seven:
`default` and `one` to `six`. A section theme is a slot, not a color: its real color comes from
the site's global theme (seven of them, from the tokens repo), and the mapping lives in
`03-organisms/layout/layout/_yds-layout.scss`. So the check is 7 section themes by 7 global
themes, 49 backgrounds, per state. Read both lists fresh; they grow.

**How to measure:**

- Render the round 2 HTML mockup once per pairing: wrap it in
  `data-global-theme="<global>"` and a section with `data-section-theme="<section>"`, the way
  the library's own stories do, on the published component library CSS. On a Claude Design
  setup, rebuild just the block's colored parts this way for the check; never read contrast
  off an exported PNG.
- In headless Chromium, read the computed foreground and background colors of every text,
  icon, border, divider and focus ring, at rest, on hover and on keyboard focus.
- Thresholds (WCAG 2.2 AA): 4.5:1 for text, 3:1 for large text (24px, or 18.66px bold), icons,
  borders that carry meaning and focus rings. A part that sits on its own fill (a card on a
  colored section) is measured against that fill, and the fill against the section for 3:1
  when its edge is what shows the part is there.

**Output:** `contrast.json` (every pairing, part, state and ratio) and a summary table on the
board: one row per section theme, one column per global theme, the lowest ratio in each cell,
failures marked in words as well as color. Each failure becomes a round 2 question (see
SKILL.md). A failure is fixed with an existing token pairing first; a token change is a
changed token in the inventory, called out like any other.

## Block picker icon

Every ticket that adds a new block gets its picker icon in round 2 (a product ruling of 2026-11-12,
after the Timeline block, yalesites-org/YaleSites-Internal#2033, shipped its handoff without
one). The icon is the tile editors see in Layout Builder's "Add a block" picker, from the
`layout_builder_browser` contrib module.

**How the existing set is made** (yalesites-project `develop`; the whole set was redrawn and
signed off in yalesites-org/YaleSites-Internal#1963 and
yalesites-org/YaleSites-Internal#1903, so match it, not older icons):

- **Folder:** `web/profiles/custom/yalesites_profile/modules/custom/ys_core/images/preview-icons/`,
  one SVG per block, named for the block in kebab case (`facts-and-figures.svg`,
  `office-hours.svg`).
- **Format:** SVG, `width="501" height="261" viewBox="0 0 501 261"`, with
  `role="img" aria-label="<file name>"`. Flat shapes only (`rect`, `circle`, `polygon`, `line`),
  no text, no gradients, no embedded images, no fonts.
- **Palette:** white `#ffffff` background, a light gray `#d9d9d9` band or panel, Yale Blue
  `#00356b` for the one thing that makes the block what it is, and grays for placeholder text:
  `#5e5e5e` for headings, `#757575` for body lines, `#bababa` for secondary shapes. Facts and
  Figures is a good model: two blue pictograms, each over a dark gray bar (the figure) and a
  lighter one (the label).
- **Wiring:** a config file per block,
  `config/sync/layout_builder_browser.layout_builder_browser_block.<id>.yml`, with
  `block_id: 'inline_block:<block type>'`, `category`, `label`, `image_path` (the SVG's path
  from `/profiles/...`), `image_alt` and `weight`. A block without its own icon falls back to
  `fallback-general.jpg`, which is the placeholder we are avoiding.
- **Categories** (the picker's tabs, `layout_builder_browser_blockcat.*.yml`): Text & Content
  (`text_and_content`), Featured Content (`featured_content`), Dynamic Content
  (`dynamic_content`), Media (`media`), Calls to Action (`calls_to_action`), Basic (`basic`),
  and the Views tabs (Post, People, Page and Resource Views). Read the folder fresh, since
  categories change.

**What round 2 makes:**

1. Draw the icon as hand-written SVG to the spec above, from the signed-off design's most
   recognizable feature (the Timeline's dated markers on a line, say), not a shrunken mockup.
   Write it ourselves on every renderer, so it matches the flat set exactly.
2. Pick the category: the one the nearest existing block sits in, unless the ticket says
   otherwise. Name the nearest block as the reason.
3. Render `r2-picker-<category>.png`: the new icon beside two or three icons from the same
   category (read from `develop`), at the same size with their labels under them, so the
   reviewer judges it as an editor will see it.
4. Ask it on the board as its own question (see SKILL.md, round 2). On "Change the icon",
   redraw it in the next iteration with the rest.

## The board

Use the pr-feedback review board: `plugins/yalesites-product/skills/pr-feedback/scripts/review-board/`.
Packet format is in `pr-feedback/references/review-board.md`. Start the server as a background
task and open the board for the reviewer at `http://localhost:8797/?packet=<packet id>`, the
current round's id (`design-<number>-r2-i2`, say). One server serves every round:

```bash
python3 <plugin>/skills/pr-feedback/scripts/review-board/server.py --packets ~/.claude/yalesites/design-pass/packets --port 8797
```

A design packet is not a PR review, so:

- Give it one `units` entry with `pr: { "ref": "Design pass", "title": "<Feature>: <phase>" }`
  and `issue` set to the ticket. The board needs a `pr` on the unit to draw its lead-in page.
- Use `compare` blocks with sides labeled by approach name or by what differs
  (`Sidebar 305px:` / `One column:`, `Global One:` / `Global Four:`), never "A" and "B".
- Give every option `"verdict": "comment"`, "Decide later" included. The board wants a ruling
  per unit and stops Send without one; `comment` is the one that claims nothing. Its last page
  still uses PR wording ("Posts your open decision as a comment"); ignore it, since Send only
  writes `answers.json` and nothing posts.
- Put the recommendation first, with `recommended: true`, and end every question with
  "Decide later".
- Never reuse a packet id across rounds or iterations (see "Files" above). Each round's
  `answers.json` stays in its own folder; never delete one, since together they are the design
  record. Archive an `answers.json` with a timestamp only when the same packet is rebuilt
  within a round (a fix to a typo, say), as `answers-<timestamp>.json`.

The reviewer's answers on the board are the ruling. Do not re-ask them in chat.
