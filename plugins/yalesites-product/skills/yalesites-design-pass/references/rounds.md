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
  handoff.md               round 3 spec draft
  storybook-docs.mdx       round 3 docs draft
  answers.json             written by the board
```

Name images by what they show, never by letter. Copy the Claude Design export (zip or PNGs from the
config's `exportFolder`) into the folder; never point the board at the export folder directly.

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
