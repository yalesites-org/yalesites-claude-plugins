# Docs board packet format

One packet per batch. It lives in a folder that outlasts the session, because the build step and
the work dashboard both read it later:

```
~/.claude/yalesites/docs-board/packets/<packet-id>/
  packet.json
  decisions.json          written by the board when the reviewer sends
  1818/
    current.json          capture.py (page) or packet.py split-md (repo file)
    current.png           capture.py, edits only
    draft.md              yalesites-web-content deliverable for this ticket
  1901/
    draft.md              a new page has no capture
```

Use `docs-<yyyy-mm-dd>` for the packet id, with `-2`, `-3` for a second batch the same day. Use
the ticket number for each item id.

**One ticket, two pages.** A ticket that touches two pages is two items, one per page, with the
ids and the refs suffixed: id `1818-a` with ref `yalesites-org/YaleSites-Internal#1818-a`, and
`1818-b` with `#1818-b`. `packet.py validate` rejects two items with the same `ticket.ref`,
because status and the build lock are recorded per ref: one page being built would lock, or
skip, the other. Each suffixed ref gets its own entry in the status file.

## packet.json

```json
{
  "id": "docs-2026-10-12",
  "title": "Docs for the 12-01-26 release",
  "subtitle": "4 tickets · drafted 2026-10-12",
  "items": [ ... ]
}
```

### An item

| Field | Required | What it is |
|---|---|---|
| `id` | yes | The ticket number. Letters, digits, `.`, `_`, `-` only |
| `ticket` | yes | `{ "ref": "yalesites-org/YaleSites-Internal#1818", "url": "...", "title": "Docs: ..." }`. Always the full `owner/repo#N` form, unique within the packet (suffix it, `#1818-a`, when one ticket is two items) |
| `kind` | yes | `edit` (a page that exists), `new` (a page that does not), or `internal` (a markdown file in a repo) |
| `target` | yes | Where it goes. See below |
| `summary` | yes | One or two sentences: what changes and why. The reviewer reads this first |
| `current` | edit, and internal edits | Path to `current.json`, relative to the packet folder |
| `ops` | yes | The proposed page or file, top to bottom. See below |
| `build` | no | Markdown. For a page: the Title, Teaser, and Config considerations sections of `draft.md`. For internal: branch and commit plan |
| `notes` | no | Strings. Screenshots still owed, scope left out on purpose, follow-ups |
| `draft` | no | Path to `draft.md`. The board links it |
| `revision` | no | Starts at 1. Bump it on every revision so the board resets that item's decision. `packet.py status <ref> failed` bumps it too, so a half-built page needs a fresh approve |
| `previousFeedback` | revisions | One line restating what the reviewer asked for last round. Shown as a banner |
| `locked` | set by `packet.py status` | `true` once the ticket is `building` or `built`. The board shows the item read-only with a Built badge, counts it as settled, and leaves it out of `decisions.json`. `failed` clears it and bumps `revision`. Do not write it by hand |

`target` by kind:

| Kind | Fields |
|---|---|
| `edit` | `url` (full URL of the live page), `label` (its title) |
| `new` | `path` (proposed URL alias), `label` (page title), `parent` (where it sits in the nav, in words), `menu` (the menu link, or "None"), `siblings` (`[{ title, path }]`, pages it will sit beside), `overlap` (`[{ title, path, why }]`, close matches the reviewer should know about) |
| `internal` | `repo` (`owner/repo`), `file` (path in the repo), `branch` (the branch it will be written on), optional `url` (GitHub link to the file on the default branch) |

### Ops

`ops` is the proposed page in order, top to bottom. Each op is one block:

| `op` | Fields | Meaning |
|---|---|---|
| `keep` | `ref` | The block stays as it is |
| `edit` | `ref`, `markdown`, `why` | The block stays, with new content. `markdown` is the whole block as it will read, not just the changed part. The board diffs it against the capture |
| `add` | `block`, `markdown`, optional `settings`, `why`, `blockWhy` | A new block, placed where it sits in the list. No `ref` |
| `remove` | `ref`, `why` | The block goes. `why` is required: dropping content is the reviewer's call |

`ref` is a block id from `current.json` (`b1`, `b2` for a page, `s1`, `s2` for a repo file).
**On an edit, every block in `current.json` appears in `ops` exactly once**, as keep, edit, or
remove. `packet.py validate` enforces it, because a block left out of `ops` would vanish from the
board without anyone deciding to drop it.

A new page has no `current`, so its ops are all `add`.

**Block considerations.** `block` is the Layout Builder block, by the label editors see (`Text`,
`Callout`, `Inline Message`, `Accordion`, `Quick Links`, `View`, `Divider`). Take the label from
the `yalesites` skill's `references/blocks-reference.md` when it is installed. For a repo file,
use `Section`.

- `settings` is shown as chips: `{ "Padding": "No padding", "Style": "Emphasized" }`. Use the
  form's own labels.
- `blockWhy` says why this block and not plain Text. Fill it whenever the block is not Text.
  "A short message with no link is what Inline Message is for. Callout would ask for a button."
- An add that goes into a specific section or column says so in `place`:
  `"place": "new Two column (30/70) section, right column"`.

**Moving a block** has no op of its own. Write it as a `remove` with `why: "Moved below
b7"` and an `add` with `why: "Moved from above b3"`, and say so in `notes`, so the build uses the
Move recipe instead of deleting and recreating the block.

### Markdown

The board renders a light markdown: `##`/`###` headings, paragraphs, `-` and `1.` lists, tables
with a `|---|` row, `>` quotes, fenced code, `**bold**`, `*italic*`, `` `code` ``, and links.
Write internal links as site-relative paths (`/editorial-workflow`). The board links them to the
live site. Mark screenshots the way `yalesites-web-content` does:

```markdown
*[SCREENSHOT: the Office Hours block on a published page]*
*Alt text: An Office Hours block with hours for Monday to Friday.*
```

`capture.py` writes each block's current content in the same markdown, so an `edit` should start
from the block's `markdown` in `current.json` and change only what needs changing. A rewrite of
the whole block from scratch shows as a wall of red and green, and hides the real change.

## current.json

From `capture.py`, for a page:

```json
{
  "status": 200, "url": "https://yalesites.yale.edu/create-powerful-page-sections",
  "title": "Create Powerful Page Sections", "teaser": "Sections are the foundation...",
  "pageHeight": 7232, "width": 1280, "screenshot": "current.png",
  "sections": [{ "index": 3, "layout": "fifty-fifty", "theme": "two", "top": 13.8, "height": 19.29 }],
  "blocks": [
    { "id": "b2", "type": "Text", "cls": "text-field", "section": 3, "region": "primary",
      "padding": "no-padding", "top": 14.68, "height": 8.4, "left": 10.2, "width": 38.5,
      "markdown": "## Available Section Types\n\n..." }
  ]
}
```

Positions are percentages of the full page, so the board can outline each block on the
screenshot at any width. `type` is inferred from the block's markup class; a class the script
does not know shows as `Unknown (<class>)`. Check it against the screenshot.

From `packet.py split-md`, for a repo file: `{ "kind": "file", "repo", "file", "screenshot": null,
"blocks": [{ "id": "s1", "type": "Section", "markdown": "..." }] }`, one block per heading.

## decisions.json

Written by the board on Send. One entry per item:

```json
{
  "packet": "docs-2026-10-12",
  "submittedAt": "2026-10-12T18:59:48.545Z",
  "decisions": [
    {
      "id": "1901", "ticket": "yalesites-org/YaleSites-Internal#1901", "kind": "new", "revision": 1,
      "decision": "changes",
      "notes": "Shorter intro",
      "comments": [
        { "type": "quote", "on": { "index": 0, "op": "add", "num": 1, "ref": null, "block": "Text" },
          "quote": "Use the Office Hours block", "note": "Lead with who uses this block" },
        { "type": "pin", "on": "live page screenshot", "x": 50, "y": 20.4,
          "nearBlock": "b2", "nearType": "Text", "note": "This heading is out of date too" }
      ]
    }
  ]
}
```

- `decision` is `approve`, `changes`, or `skip`. A `changes` decision always has notes or at
  least one comment.
- A `locked` item has no entry at all. It was built on an earlier round, and the board does not
  send it again.
- A `quote` comment names the op by its position in `ops` (`index`) and by the number the board
  showed (`num`). A `pin` names the live block it landed on (`nearBlock`). Describe both in
  words when you play the decisions back, because the reviewer never saw the ids.
- `revision` is the revision the reviewer decided on. If it does not match the item's current
  `revision`, the decision is for an older draft. Ignore it and ask.
