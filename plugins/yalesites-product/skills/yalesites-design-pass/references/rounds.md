# Rounds: widths, files, and board mechanics

## Region widths

The layouts come from `ys_layouts` in yalesites-project (`*.layouts.yml` on `develop`). The
widths below are content widths at a 1440px viewport. Only the two marked "measured" were
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

One folder per ticket in the session scratchpad, served by the review board:

```
<scratchpad>/design-pass/packets/design-<number>/
  brief.md                 what goes to Claude Design (and nothing more)
  packet.json              the board
  r1-<approach>-1440.png   round 1, one desktop and one phone per approach
  r1-<approach>-360.png
  r2-<region>-<theme>.png  round 2
  handoff.md               round 3 spec draft
  storybook-docs.mdx       round 3 docs draft
  answers.json             written by the board
```

Name images by what they show, never by letter. Copy the Claude Design export (zip or PNGs from the
config's `exportFolder`) into the folder; never point the board at the export folder directly.

## The board

Use the pr-feedback review board: `plugins/yalesites-product/skills/pr-feedback/scripts/review-board/`.
Packet format is in `pr-feedback/references/review-board.md`. Start the server as a background
task and open the board for the reviewer:

```bash
python3 <plugin>/skills/pr-feedback/scripts/review-board/server.py --packets <scratchpad>/design-pass/packets --port 8797
```

A design packet is not a PR review, so:

- Give it one `units` entry with `pr: { "ref": "Design pass", "title": "<Feature>: <phase>" }`
  and `issue` set to the ticket. The board needs a `pr` on the unit to draw its lead-in page.
- Use `compare` blocks with sides labeled by approach name or by what differs
  (`Sidebar 305px:` / `One column:`, `Global One:` / `Global Four:`), never "A" and "B".
- Put the recommendation first, with `recommended: true`, and end every question with
  "Decide later".
- Before each new round, archive the previous `answers.json` as
  `answers-<round>-<timestamp>.json`. Never delete one; together they are the design record.

The reviewer's answers on the board are the ruling. Do not re-ask them in chat.
