# Review board: Step 3b on a screen instead of in a text box

Held calls usually point at something: a screenshot from the driven run, a line in the ticket,
two layouts that should match. A text question in chat makes the reviewer hold all of that in
their head. The review board puts each call on its own page, with the screenshot at full size,
numbered callouts on the exact spot in question, the relevant ticket text with the key line
highlighted, and big option cards. The reviewer can drop their own pins, draw boxes, and comment
on selected ticket text. Every screenshot has an Enlarge button that opens it full screen, at fit
or actual size, and a `compare` block flips between its images in place with the arrow keys, which
is how a 1px against 2px change becomes visible. One click sends everything back.

It is a single local page (`scripts/review-board/index.html`) served by a small Python server
(`scripts/review-board/server.py`) on `127.0.0.1`. Nothing leaves the machine, which matters:
the held calls come from the brief, and the brief stays local.

## When to use it, and when not to

| Use the board for | Keep in chat |
|---|---|
| Step 3b Part 1, the held calls in the reviewer's lane | Step D1's ask-once before creating test content |
| Step 3b Part 2, their own read (always the last page) | Step 6, approve or request changes. Always one explicit chat ruling per PR |
| Batch mode Step B4, all units in one packet | Out-of-lane calls. Name them in chat, as Step 3b says. They are not questions |
| | Scope-creep and follow-up ticket offers (Steps 4 and 5) |

**Skip the board, and ask in chat with `AskUserQuestion`, when:**
- There are no in-lane held calls. Say the section is empty, then ask for their own read in chat.
- `python3` is missing, or the session has no local browser (a cloud or remote session).
- The reviewer has said they prefer chat questions. Respect that for the rest of the session.

## Step R1: Build the packet

One packet per review, or one per batch. The packet folder lives in the session scratchpad:

```
<scratchpad>/review-board/packets/<id>/
  packet.json
  01-fail-editor-overflow-360.png   (copied from the drive-it run folder)
```

Use `<repo-short>-<number>` for the id (`ysp-1598`, `clt-728`), or `batch-<yyyy-mm-dd>` for a
batch. Copy every screenshot the packet names into the folder. If an `answers.json` is already
there from an earlier pass, delete it first, or the wait in Step R3 ends at once on stale answers.

### packet.json

```json
{
  "title": "1824: Bug: Configure section logs a PHP warning on every open",
  "subtitle": "Driven run on pr-1598, site_admin",
  "pr": { "ref": "yalesites-org/yalesites-project#1598", "url": "https://github.com/yalesites-org/yalesites-project/pull/1598" },
  "issue": { "ref": "yalesites-org/YaleSites-Internal#1824", "url": "https://github.com/yalesites-org/YaleSites-Internal/issues/1824" },
  "ownReadPrompt": "Optional. Overrides the default 'What did you notice?' text.",
  "questions": [
    {
      "id": "swatch-clipping",
      "title": "Swatch row cuts off",
      "dimension": "design",
      "question": "The last swatch is cut off and a scrollbar shows under the row. This PR did not cause it. How should we handle it?",
      "context": [
        {
          "type": "image",
          "label": "Configure section, Two column (50/50), site_admin",
          "src": "01-pass-site_admin-2col-gray100.png",
          "caption": "Two column, Gray 100 selected",
          "marks": [
            { "x": 94, "y": 52, "w": 6, "h": 38, "note": "The last swatch is clipped at the modal edge." },
            { "x": 40, "y": 20, "note": "A pin, because it has no w or h." }
          ]
        }
      ],
      "options": [
        { "value": "followup", "label": "Follow-up ticket", "detail": "Approve this fix as-is and open a design ticket.", "recommended": true },
        { "value": "fix-here", "label": "Fix it in this PR", "detail": "Ask the developer to wrap the swatches." }
      ]
    }
  ]
}
```

Context blocks, any number per question, shown in order:

| `type` | Fields | Use it for |
|---|---|---|
| `image` | `src`, `caption`, `label`, `marks[]`, optional `url` | One screenshot. An `ask` row from drive-it, or a `fail` that needs a ruling |
| `compare` | `label`, `images[]` (each with `src`, `caption`, `marks[]`) | Side by side: multidev against `dev`, two layouts, two roles, two widths |
| `text` | `label`, `body` (light markdown: `###`, `-` lists, `**bold**`, `` `code` ``, links), `highlight[]`, optional `url` | Ticket acceptance criteria, the PR description, the brief's evidence for the call |

`marks` use percentages of the image (0 to 100), so they stay put at any width. A mark with `w`
and `h` is a box, and one without is a pin. Look at the screenshot before placing marks, and put
each one on the thing its note describes. A pin in the wrong place is worse than no pin.
`highlight` strings must match the `body` text exactly, inline markdown included, or they do not
highlight.

`pr` on a question overrides the packet's `pr`. Batch packets set it on every question, which
tags each page with its PR. Keep a unit's questions next to each other.

### Writing the questions

- **The brief's own words where they are already clear,** as Step 3b says. The board changes how
  the call is shown, not what is asked.
- **Answerable from the page.** If the reviewer needs to open another tab to decide, put the
  thing they would look at into a context block instead.
- **Two to four options, each with a `detail` naming its cost.** "Widens a small bug fix" is the
  part that makes the choice real. The board always adds a "Something else" option with a free
  text box, so do not add an "Other" option yourself.
- **`recommended` only with a reason the reviewer can see.** Put the reason in `detail`. These
  are held calls, which the audit was forbidden to decide, so most questions have no
  recommendation, and that is fine.
- **`dimension`** is the Step 0 dimension the call belongs to (`product`, `design`, `a11y`,
  `functional`, `code`).

## Step R2: Start the server and open the board

**Pick the port.** Start at 8765. `curl -s http://localhost:<port>/api/health` tells you what is
there:

| Result | Meaning |
|---|---|
| Connection refused | Free. Use it |
| `{"app": "pr-feedback-review-board", "packets": "<this session's packets folder>"}` | This session's board is already running. Reuse it and skip starting one |
| Anything else (another session's board, another app) | Taken. Try the next port up |

**In the Claude desktop app, with the Browser pane tools,** let the pane run the server. Add this
to `configurations` in the project's `.claude/launch.json` (create the file with
`"version": "0.0.1"` if there is none):

```json
{
  "name": "pr-review-board",
  "runtimeExecutable": "python3",
  "runtimeArgs": ["<skill-dir>/scripts/review-board/server.py", "--packets", "<scratchpad>/review-board/packets", "--port", "<port>", "--exact-port"],
  "port": <port>
}
```

Start it with `preview_start`, then go to the packet with `preview_eval`
(`location.href = "http://localhost:<port>/?packet=<id>"`). `--exact-port` matters here: the pane
opens the port in the config, so the server must fail loudly rather than move to another one. A
URL-only entry, which attaches to a server already running, is not available on every install,
so do not rely on it.

`.claude/launch.json` is not gitignored in the YaleSites repos. Note whether you created the file
or only added an entry, because Step R4 undoes exactly that.

**Anywhere else on a Mac,** start the server in the background (Bash `run_in_background`) and
open it in the default browser:

```bash
python3 <skill-dir>/scripts/review-board/server.py --packets <scratchpad>/review-board/packets --port <port>
```

It prints `REVIEW_BOARD_URL http://localhost:<port>`, and moves to the next free port if that
one was taken between the check and the start, so read the port from that line. Then
`open "http://localhost:<port>/?packet=<id>"`.

Take one `preview_screenshot` (or, outside the app, a quick `curl` of the packet URL) to confirm
the board loaded the packet, and not the "Couldn't load packet" header.

Then tell the reviewer in chat, in one or two lines: the board is open, how many questions it
holds, and that they can still answer in chat instead. List the out-of-lane calls in the same
message, per Step 3b.

## Step R3: Wait for the answers, then read them back

Arm one background wait. It ends the moment they press Send:

```bash
until [ -f <packet-dir>/answers.json ]; do sleep 1; done; cat <packet-dir>/answers.json
```

Do not poll in a loop and do not ask "are you done?" The wait wakes the session. If the reviewer
types their answers in chat instead, use those and leave the wait to expire.

`answers.json` looks like this:

```json
{
  "packet": "ysp-1598",
  "answers": [
    {
      "id": "swatch-clipping",
      "pr": "yalesites-org/yalesites-project#1598",
      "dimension": "design",
      "choice": "followup",
      "choiceLabel": "Follow-up ticket",
      "notes": "Check event pages too",
      "markups": [
        { "on": "Two column, Gray 100 selected", "file": "01-pass-site_admin-2col-gray100.png",
          "type": "box", "x": 10, "y": 30, "w": 20, "h": 40, "note": "The white swatch blends into the modal" },
        { "on": "PR description", "file": null, "type": "quote", "quote": "are unchanged", "note": "Are they, though?" }
      ]
    }
  ],
  "ownRead": "Looks fine on my laptop."
}
```

- **`choice: "other"`** means they wrote their own answer, and it is in `choiceLabel`. That is
  their ruling. Ask a follow-up in chat only if it is unclear.
- **`markups`** are the reviewer's own observations, so they are first-class input for Step 4,
  like `ownRead`. A box or pin names the screenshot `file` and where on it. Describe it in words
  in the feedback ("the white swatch, left of the selected one"), because the developer never
  sees the coordinates. A screenshot with markups is one worth suggesting they drag into the
  review comment, since `gh` cannot upload images.
- **Play the rulings back in chat before Step 4,** one line per question, so the decisions are in
  the transcript and the reviewer can correct a misclick before anything is drafted.

If they press "Edit and resend" later, `answers.json` is overwritten. Re-arm the wait only when
they say they changed something.

## Step R4: Clean up

When the review is posted, or abandoned:

- Stop the server you started: `preview_stop` in the desktop app, or `TaskStop` on the background
  task elsewhere. Leave a reused one running.
- Undo the `.claude/launch.json` change: remove the `pr-review-board` entry, or the whole file if
  you created it. Never commit it.
- Leave the packet folder. Like the drive-it screenshots, it is the evidence for the review.
