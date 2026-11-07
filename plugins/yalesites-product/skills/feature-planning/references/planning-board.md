# Planning board

The planning board is pr-feedback's review board with two changes: questions are grouped by
**part** of the plan (Scope, Interactions, Feasibility and effort, Timeline) instead of by PR, and
the last page recaps the decisions instead of asking for PR rulings. Everything else works the
same way: a lead-in per part, evidence on the left, sticky answer cards on the right, pins, boxes,
quote comments, compare blocks, and video.

- Board page: `scripts/board/index.html` (this skill)
- Server: `../../pr-feedback/scripts/review-board/server.py`, shared, started with `--board-dir`
- Full reference for context blocks, marks, labels, and writing questions:
  `../../pr-feedback/references/review-board.md`. Everything there applies, except the parts about
  PRs, verdicts, and posting reviews, which this file replaces.

## Step B1: Build the packet

```
<scratchpad>/feature-planning/packets/<slug>/
  packet.json
  onha-facts-band-1440.png
  stanford-editor-doc.png
```

The id is the feature slug (`facts-band-layouts`). Copy every image and clip into the folder. If an
`answers.json` is already there from an earlier round, rename it to
`answers-$(date -u +%Y%m%dT%H%M%SZ).json` first, never delete it.

### packet.json

```json
{
  "title": "Feature plan: Facts and Figures layouts",
  "shortTitle": "Facts band layouts",
  "subtitle": "Research 2026-11-01 | Portfolio crawl 2026-10 | Pantheon skipped: not logged in",
  "ownReadPrompt": "Optional. Overrides the default last-page prompt.",
  "units": [
    {
      "key": "scope",
      "title": "Scope",
      "short": "Scope",
      "ask": "What we are building and who it is for.",
      "change": "Facts and Figures is on **38 of 296** crawled sites (226 instances). Three support tickets in the last year asked for a horizontal layout.",
      "status": "Code, portfolio, GitHub, UX research, two higher ed Drupal platforms",
      "issue": { "ref": "yalesites-org/YaleSites-Internal#NNNN", "url": "https://github.com/yalesites-org/YaleSites-Internal/issues/NNNN", "title": "Facts and Figures horizontal layout" },
      "related": [
        { "ref": "yalesites-org/YaleSites-Internal#MMMM", "url": "https://github.com/yalesites-org/YaleSites-Internal/issues/MMMM", "note": "Earlier ask, closed in 2025 for lack of design time" }
      ],
      "notAsked": [
        "**Settled by research:** no new permission needed. Site admins and site builders already edit the block.",
        "**For our lead developer:** whether the layout is a new view mode or a template variable."
      ]
    }
  ],
  "questions": [
    {
      "id": "placement",
      "part": "scope",
      "title": "Where the layout choice lives",
      "dimension": "scope",
      "brief": [
        "A block option reaches only the instances an editor changes.",
        "A sitewide setting would change all 226 instances on deploy.",
        "Settles: whether the default question below exists at all."
      ],
      "ask": "Make the layout a per-block option, or a sitewide setting?",
      "question": "Optional full write-up, folded under Full write-up.",
      "context": [
        { "type": "image", "label": "Facts and Figures on onha, 1440px", "src": "onha-facts-band-1440.png", "url": "https://onha.yale.edu/", "caption": "The heaviest use in the crawl", "marks": [] }
      ],
      "options": [
        { "value": "block", "label": "Per-block option", "detail": "Recommended: no live site changes until an editor picks it. Adds one field to the block form.", "recommended": true },
        { "value": "sitewide", "label": "Sitewide setting", "detail": "One switch for site admins, but changes every instance on that site at once." },
        { "value": "defer", "label": "Decide later", "detail": "Becomes an open item with you as the owner." }
      ]
    }
  ]
}
```

**Parts (`units`).** One per part of the plan, in the order the questions run. `key` is what a
question's `part` points at. The lead-in fields mean:

| Field | Shows as | Put in it |
|---|---|---|
| `title` | The lead-in heading | The part name |
| `short` | The header chip | One or two words |
| `ask` | What we are deciding | One sentence |
| `change` | What research found | The two or three findings that matter for this part, with numbers |
| `status` | Sources | The sources this part draws on, and any that were skipped |
| `issue` | Ticket link | The ticket that started the session, if there is one. Put it on the first part only |
| `related` | Related | Earlier tickets, PRs, and ADRs a question mentions |
| `notAsked` | Not asked | Questions research settled (with the evidence) and architecture questions for the lead developer |

Only list a part that has questions. When every question in a part was settled or is for the
lead developer, put its `notAsked` items on the closest part that still has questions. If a
questionless part slips into `units` anyway, the board shows its Not asked items on the last page
and leaves it out of the part count.

**Questions.** Write them as pr-feedback's "Writing the questions" says, with these differences:

- `part` instead of `pr`. Keep a part's questions next to each other.
- No `verdict` on options.
- Every question ends with the **Decide later** option shown above. It becomes an open item with
  the user as owner.
- The third `brief` bullet says what the answer settles ("Settles: ..."), so the ranking is visible.
- `dimension` is the part's area: `scope`, `existing-sites`, `interactions`, `feasibility`,
  `timeline`, `measure`, `ux`, `a11y`.
- External findings go in as context blocks with the tier and date in the `label`
  ("Tier 1: Stanford Sites editor doc, checked 2026-11-01"), and an `url` to the source. Use the
  screenshots from Step 3b; `references/visual-evidence.md` says how visual options map to
  `compare` blocks.

## Step B2: Serve and open it

Pick a port starting at 8785, checking with `curl -s http://localhost:<port>/api/health`:
connection refused means free; `{"app": "feature-planning-board", "packets": "<this session's
packets folder>"}` means this session's board is already up, so reuse it; anything else means
taken, so try the next port.

```bash
SERVER="$(realpath <skill-dir>)/../pr-feedback/scripts/review-board/server.py"
python3 "$SERVER" --packets <scratchpad>/feature-planning/packets \
  --board-dir <skill-dir>/scripts/board --app feature-planning-board --port <port>
```

Run it in the background. It prints `REVIEW_BOARD_URL http://localhost:<port>`; read the port
from that line, then `open "http://localhost:<port>/?packet=<slug>"`.

**In the Claude desktop app with the Browser pane,** add a `feature-planning-board` entry to the
project's `.claude/launch.json` instead (same arguments, plus `--exact-port`), start it with
`preview_start`, and navigate with `preview_eval`. Note whether you created the file or only added
an entry, so cleanup undoes exactly that.

Confirm the board loaded the packet and not "Couldn't load packet". Then tell the user, in one
line, that the board is open and how many questions it holds.

## Step B3: Wait, then read the answers

Arm one `Monitor` on the answers file, as pr-feedback's Step R3 does:

```
Monitor({
  command: 'until [ -f "<packet-dir>/answers.json" ]; do sleep 1; done; echo "answers.json written"',
  description: "planning board answers for <slug>",
  timeout_ms: 1800000
})
```

If it expires, arm it again. Don't poll and don't ask "are you done?". If the user answers in chat
instead, use those and stop the monitor.

`answers.json` holds `answers[]` (each with `id`, `part`, `choice`, `choiceLabel`, `notes`,
`markups`) and `ownRead`. `choice: "other"` is the user's own answer, in `choiceLabel`. `notes`,
`markups`, and `ownRead` are first-class input to the decision record, often the most useful part.
The answers are the ruling: don't ask them again in chat.

## Step B4: Clean up

Stop the server you started (`TaskStop`, or `preview_stop` in the desktop app). Undo the
`.claude/launch.json` change, and never commit it. Leave the packet folder with the session's
other files.
