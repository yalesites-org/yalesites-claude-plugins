# Review board: Step 3b on a screen instead of in a text box

Held calls usually point at something: a screenshot from the driven run, a line in the ticket,
two layouts that should match. A text question in chat makes the reviewer hold all of that in
their head. The review board puts each call on its own page, with the screenshot at full size,
numbered callouts on the exact spot in question, the relevant ticket text with the key line
highlighted, and big option cards. The reviewer can drop their own pins, draw boxes, and comment
on selected ticket text. Every screenshot has an Enlarge button that opens it full screen, at fit
or actual size, and a `compare` block flips between its images in place with the arrow keys, which
is how a 1px against 2px change becomes visible. A `video` block plays a clip from the run, at
normal, half, or quarter speed, and the reviewer can leave a note at any moment in it.

The reviewer runs this several times a day, a handful of PRs each time, so the board is built for
someone arriving cold. Each PR opens with a **lead-in page**: what it is for, what it changes,
where to test it, and the numbered list of decisions coming up. Each question then shows a few
context bullets and one plain question beside the answer cards, which stay in a sticky panel
while the evidence scrolls. A header row of PR chips and a stepper, color-coded per PR, shows
where they are. Picking an answer moves to the next question (number keys pick, arrows move).
The last page shows each PR's ruling, worked out from the answers and open to override, and what
sending will post.

**Finishing the board finishes the review.** Sending it is the reviewer's ruling on every PR in
it. Nothing on the board is asked again in chat, and nothing new is asked after it, so anything
the review needs a person to decide goes on the board as a question.

It is a single local page (`scripts/review-board/index.html`) served by a small Python server
(`scripts/review-board/server.py`) on `127.0.0.1`. Nothing leaves the machine, which matters:
the held calls come from the brief, and the brief stays local.

## When to use it, and when not to

| On the board | Where |
|---|---|
| Step 3b Part 1, the held calls in the reviewer's lane | One question each |
| Step 5 follow-up ticket offers (visreg gaps, docs), and new scope found in Step 2 | One question each, in that PR's group, with a non-blocking option to skip |
| A ticket that drifted from what the PR does (`SKILL.md` Step 9b) | One question: update the ticket, comment on it, or leave it |
| Out-of-lane calls | Named on the PR's lead-in under **Not asked** (`notAsked`). They are not questions |
| Step 3b Part 2, their own read | The last page |
| Step 6, approve or request changes | The last page, one ruling per PR, from the answers (`verdict`) |

Test content needs no question at all: running the skill is consent (`drive-it.md` Step D1).

**Skip the board, and ask in chat with `AskUserQuestion`, when:**
- There is nothing to ask: no in-lane held calls, no follow-up offers (Step 5), and no ticket drift. Say so, then ask for their own read in chat. Follow-up offers or ticket drift on their own still get a board, since each one is a question there.
- `python3` is missing, or the session has no local browser (a cloud or remote session).
- The reviewer has said they prefer chat questions. Respect that for the rest of the session.

## Step R1: Build the packet

One packet per review, or one per batch. The packet folder lives in the session scratchpad:

```
<scratchpad>/review-board/packets/<id>/
  packet.json
  01-fail-editor-overflow-360.png   (copied from the drive-it run folder)
  06-fail-editor-escape-focus.webm
```

**A prepped packet is already built.** When `SKILL.md` Step 1 found one, do not write a packet,
and do not start the server on the shared prep folder. Make this session's packets folder as
usual and put a symlink in it that points at the prepped packet:

```bash
mkdir -p <scratchpad>/review-board/packets
ln -sfn <packetDir> <scratchpad>/review-board/packets/<id>
```

`-sfn` replaces an existing link in place. Without it, `ln` follows an old `packets/<id>` link and
drops the new link inside the old packet folder, exits 0, and the board keeps serving the old
packet. `-n` does not replace a real folder, so a non-link `packets/<id>` left by a packet built
live earlier in the session has to be moved aside first (`mv packets/<id> packets/<id>-live-<time>`).

`<packetDir>` is the versioned folder on the status entry Step 1 read
(`~/.claude/yalesites/pr-review-prep/packets/<id>-<sha7>-<builtAt>`), never a path built from
the id: prep mode builds every run into its own folder and leaves the older ones in place, so
the link is what pins this review to the packet it opened. A rebuild while the board is open
lands in a new folder and does not touch this one.

Then start the server on `<scratchpad>/review-board/packets` (Step R2), exactly as for a packet
built here. The server follows the link, so the board reads the prepped files, and `answers.json`
still lands inside the prepped packet, where Step R4 expects it. Archive a leftover `answers.json`
there first, as below, never delete it: in a prepped packet it is an earlier reviewer's record.
The per-session folder is what keeps Step R2's health check honest: a
server started on the shared folder would answer every session's check with the same `packets`
path. Prep mode builds its packets with this same step (`references/prep-mode.md` Step P4).

Use `<repo-short>-<number>` for the id (`ysp-1598`, `clt-728`), or `batch-<yyyy-mm-dd>` for a
batch. Copy every screenshot and clip the packet names into the folder. Use the `.webm` for clips:
the board plays it in the browser. If an `answers.json` is already there from an earlier pass,
rename it to `answers-<timestamp>.json` first, with the time now in ISO basic form, or the wait
in Step R3 ends at once on stale answers:

```bash
mv <packet-dir>/answers.json "<packet-dir>/answers-$(date -u +%Y%m%dT%H%M%SZ).json"
```

That gives `answers-20261013T161200Z.json`. The archived file is the record of that pass and
stays with the packet (Step R4, and `references/prep-mode.md` Step P4 for a prepped one). Never
delete it.

### packet.json

```json
{
  "title": "1824: Bug: Configure section logs a PHP warning on every open",
  "shortTitle": "Section warning fix",
  "subtitle": "Driven run on pr-1598, site_admin",
  "pr": { "ref": "yalesites-org/yalesites-project#1598", "url": "https://github.com/yalesites-org/yalesites-project/pull/1598" },
  "issue": { "ref": "yalesites-org/YaleSites-Internal#1824", "url": "https://github.com/yalesites-org/YaleSites-Internal/issues/1824" },
  "ownReadPrompt": "Optional. Overrides the default 'What did you notice?' text.",
  "units": [
    {
      "short": "Section warning",
      "issue": { "ref": "yalesites-org/YaleSites-Internal#1824", "url": "https://github.com/yalesites-org/YaleSites-Internal/issues/1824", "title": "Bug: Configure section logs a PHP warning on every open" },
      "ask": "Opening **Configure section** in Layout Builder logs a PHP warning each time. The ticket asks for the warning to stop, with no change to how the dialog looks or works.",
      "pr": { "ref": "yalesites-org/yalesites-project#1598", "url": "https://github.com/yalesites-org/yalesites-project/pull/1598", "title": "fix(ys_layouts): guard the missing theme setting" },
      "change": "Checks for the section theme setting before reading it. One file, no config or UI change.",
      "status": "6 pass, 1 fail, 1 ask",
      "test": { "label": "Multidev pr-1598", "url": "https://pr-1598-yalesites-platform.pantheonsite.io/" },
      "related": [
        { "ref": "yalesites-org/YaleSites-Internal#1790", "url": "https://github.com/yalesites-org/YaleSites-Internal/issues/1790", "note": "Where the swatch clipping was first reported" }
      ],
      "notAsked": ["The null check style on line 42 is a **code** call, for our lead developer."]
    }
  ],
  "questions": [
    {
      "id": "swatch-clipping",
      "title": "Swatch row cuts off",
      "dimension": "design",
      "question": "The last swatch is cut off and a scrollbar shows under the row. This PR did not cause it. How should we handle it?",
      "brief": ["The last swatch is cut off at the modal edge.", "This PR did not cause it; it shows on `dev` too."],
      "ask": "Ticket the clipping, or fix it in this PR?",
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
        { "value": "followup", "label": "Follow-up ticket", "detail": "Approve this fix as-is and open a design ticket.", "recommended": true, "verdict": "approve" },
        { "value": "fix-here", "label": "Fix it in this PR", "detail": "Ask the developer to wrap the swatches.", "verdict": "changes" }
      ]
    }
  ]
}
```

Context blocks, any number per question, shown in order:

| `type` | Fields | Use it for |
|---|---|---|
| `image` | `src`, `caption`, `label`, `marks[]`, optional `url` | One screenshot. An `ask` row from drive-it, or a `fail` that needs a ruling |
| `compare` | `label`, `images[]` (each with `src`, `caption`, `marks[]`, optional `url`) | Side by side: multidev against `dev`, two layouts, two roles, two widths |
| `video` | `src`, `caption`, `label`, `moments[]`, optional `poster`, optional `url` | One clip from drive-it ("Clips: when a still is not enough"). Behavior over time: a dialog, focus order, an AJAX rebuild, a flicker |
| `text` | `label`, `body` (light markdown: `###`, `-` lists, `**bold**`, `` `code` ``, links), `highlight[]`, optional `url` | Ticket acceptance criteria, the PR description, the brief's evidence for the call |

**Link every screenshot and clip to the live page it shows.** A block-level `url` puts one
"Open ↗" link on the block; on a `compare` block, give each image its own `url` instead, so each
side opens its own environment (the same story on the published Storybook and on the deploy
preview, the same path on two multidevs). The reviewer uses these to check a finding with their
own eyes before ruling on it, which is the point of a human review. Link the exact story,
docs page, or path, not a home page. For a finding read from code, link the file the site
actually serves (the compiled JS, CSS, or sprite). Leave `url` off only when there is no live
page, such as a simulated deploy, and say so in the caption. A link is only useful if what it
shows still exists, which is one reason Step D5 of `drive-it.md` keeps test content on PR
multidevs.

**Label each side by what differs between them, never "A" and "B".** Any side-by-side, a
two-environment parity run or a single `compare` block, gets labels that say what is being
compared. The reviewer reads one question at a time and should never have to remember which
letter, or which multidev number, means which. Pick the one thing that differs and name it in
a word or two:

| Comparing | Label the sides | Not |
|---|---|---|
| Current code against a PR | `Develop:` / `This PR:`, or the change itself (`Webpack:` / `Vite:`) | `A:` / `B:`, `pr-1612:` / `pr-1413:` |
| Published Storybook against a deploy preview | `Published:` / `Preview:`, or the change itself | `Prod:` / `Netlify:` |
| Two roles | `Editor:` / `Site admin:` | `User 1:` / `User 2:` |
| Two widths | `1440px:` / `360px:` | `Desktop:` / `Small:` |
| Two layouts or themes | `33/67:` / `50/50:`, `Theme One:` / `Theme Four:` | `Left:` / `Right:` |
| Before and after an action | `Before Save:` / `After Save:` | `1:` / `2:` |

Environment IDs, URLs, and commits are what the labels stand for, not the labels themselves.
Put them in a legend in the packet `subtitle`, one entry per label, so the mapping is stated
once at the top of every page:

```
Develop = pr-1612, develop at 41ed37c (Storybook 8, webpack) | Vite = pr-1413, 1435 branch at b556763 (Storybook 10, Vite)
```

Separate legend entries with ` | `, not ` · `: the board header joins the PR ref, the issue
link, and the subtitle with ` · `, so a legend using the same mark reads as more header items.

Use the same labels everywhere in the packet: captions, block labels, mark notes, question
text, and option details. Put the same side on the left in every pair, the baseline first.

### The lead-in: `units`

Each PR opens with a lead-in page, so the reviewer knows what the PR is and what they are about
to decide before the first question. A ref on its own (`component-library-twig#792`) means
nothing to someone arriving cold; the lead-in says, in plain words, what the ticket asked for
and what the PR does, then lists the plain question (`ask`) of every question in its group.
The same facts fold into an "About" line on each question. Write one unit per PR, or per set of
PRs reviewed together. Every packet gets `units`, a single-PR one included.

| Field | What goes in it |
|---|---|
| `short` | Two to four words for the header chip and the lead-in (`LB resize edge`, `Audio transcript`). The chip shows it next to the short ref |
| `issue` | `ref`, `url`, and `title` of the ticket the PR closes. Leave it off if there is none, and say so in `change` |
| `ask` | One to three sentences: what the ticket asks for and why, in the reviewer's terms. Not the acceptance criteria list (a `text` block carries that), the point of the ticket |
| `pr` | `ref`, `url`, and `title`. This is how a question finds its unit, so it must match the question's `pr.ref` (or the packet's `pr.ref`) exactly |
| `extraPrs` | Optional. Refs of the other PRs in the same unit (`yalesites-org/atomic#545`). A question tagged with one of them joins this unit's group |
| `change` | One to three sentences: what the PR actually does, and anything it leaves out that the ticket or an earlier PR promised |
| `status` | Optional. The drive-it result in one line (`8 pass, 2 fail, 1 ask`), or why there was no run |
| `test` | Optional. `label` and `url` of where to check it: the multidev, the Storybook deploy preview |
| `related` | Optional. `ref`, `url`, `note` for each ticket or PR a question mentions that the reviewer would otherwise have to look up: a closed earlier attempt, a parent epic, a follow-up |
| `notAsked` | Optional. One line per out-of-lane call (`SKILL.md` Step 3b): what it is, its dimension, who owns it. Shown on the lead-in, never asked |

Take `ask` and `change` from the brief, rewritten for someone who has not read it. `ask`, `change`,
and `status` take the same light markdown as a `text` block. Keep each to one or two sentences:
the lead-in is read in seconds. `shortTitle` on the packet is the header title; leave it off and
the board uses `title`.

`marks` use percentages of the image (0 to 100), so they stay put at any width. A mark with `w`
and `h` is a box, and one without is a pin. Look at the screenshot before placing marks, and put
each one on the thing its note describes. A pin in the wrong place is worse than no pin.
`highlight` strings must match the `body` text exactly, inline markdown included, or they do not
highlight.

`moments` are a clip's callouts: `{ "t": 4.5, "note": "The dialog opens, but focus stays on the
page behind it." }`, with `t` in seconds. Each shows as a timestamp the reviewer clicks to jump
there. Take `t` from the clip's frame strip, never from a clock kept while recording: each CLI
call takes a second or two to start, so clock times drift. A moment at the wrong time is worse
than none, the same as a misplaced pin.

```json
{
  "type": "video",
  "label": "Configure block dialog, editor, 1280px",
  "src": "06-fail-editor-escape-focus.webm",
  "caption": "Open the dialog, then press Escape",
  "moments": [
    { "t": 3.5, "note": "The dialog opens." },
    { "t": 7, "note": "After Escape, focus lands on the page body, not on Add block." }
  ]
}
```

`pr` on a question overrides the packet's `pr`. On a batch packet it tags each page with its PR
and picks that PR's unit for the lead-in. Set `pr` on every question, carry one unit per PR,
and keep a unit's questions next to each other: the board groups them in packet order.

### Writing the questions

- **Context first, then one plain question.** `brief` is two to four short bullets, one fact
  each: what was built, what was measured, what is already settled elsewhere. No PR ref and
  ticket number preamble, since the lead-in and the tag carry those. `ask` is the decision
  itself in one sentence a person can answer without rereading the bullets ("Keep the 12px
  padding, or let the strip overlap a narrower gutter?"). The sticky panel shows `ask` beside
  the options, so it is the thing the reviewer reads hardest. `question` stays as the full
  write-up, folded under "Full write-up"; a question with no `brief` shows it in full instead.
- **`title` is a short label, not the question,** for the stepper tooltip and the recap. Leave
  the PR out of it.
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
- **Every option carries a `verdict`:** `approve` if the PR can merge with that answer, `changes`
  if it means the developer has to change something before merge (Step 6's rule: even one small
  edit), `comment` if it leaves the PR waiting on someone (decide later, ask April, hold for a
  site owner). The last page combines them per PR: any `changes` wins, then any `comment`, else
  approve. An option without `verdict` is not guessed from its wording: unless another answer
  for that PR is `changes`, the PR gets no inferred ruling and the reviewer has to pick one on
  the last page before Send works. "Something else" counts as `comment`.

## Step R2: Start the server and open the board

**Pick the port.** Start at 8765. `curl -s http://localhost:<port>/api/health` tells you what is
there:

| Result | Meaning |
|---|---|
| Connection refused | Free. Use it |
| `{"app": "pr-feedback-review-board", "packets": "<this session's packets folder>"}` | This session's board is already running. Reuse it and skip starting one |
| Anything else (another session's board, another app) | Taken. Try the next port up |

The `packets` path in the health check is only proof of ownership because it is this session's
scratchpad folder, which no other session serves. A match on a shared folder, such as the prep
packets folder, is not proof the server belongs to this session, which is why Step R1 never
serves that folder directly.

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
holds, and that sending it posts the reviews. The out-of-lane calls are on each PR's lead-in,
so there is no need to list them here.

## Step R3: Wait for the answers, then read them back

Arm one wait with the `Monitor` tool. It ends the moment they press Send:

```
Monitor({
  command: 'until [ -f "<packet-dir>/answers.json" ]; do sleep 1; done; echo "answers.json written"',
  description: "review board answers for <packet-id>",
  timeout_ms: 1800000
})
```

That `until` loop belongs in `Monitor`, never in Bash, foreground or `run_in_background`: a
sleep-based wait in Bash is blocked, and `Monitor` is the tool made for waiting on a file. Its
single event wakes the session; read `<packet-dir>/answers.json` then. If it expires before the
reviewer is done, arm it again. Do not poll in a loop and do not ask "are you done?" If the
reviewer types their answers in chat instead, use those and `TaskStop` the monitor.

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
        { "on": "PR description", "file": null, "type": "quote", "quote": "are unchanged", "note": "Are they, though?" },
        { "on": "Open the dialog, then press Escape", "file": "06-fail-editor-escape-focus.webm",
          "type": "moment", "t": 7.5, "note": "Focus should go back to Add block" }
      ]
    }
  ],
  "verdicts": [
    { "pr": "yalesites-org/yalesites-project#1598", "verdict": "approve", "inferred": true, "because": [] }
  ],
  "ownRead": "Looks fine on my laptop."
}
```

- **`choice: "other"`** means they wrote their own answer, and it is in `choiceLabel`. That is
  their ruling. Ask a follow-up in chat only if it is unclear.
- **`markups`** are the reviewer's own observations, so they are first-class input for Step 4,
  like `ownRead`. A box or pin names the screenshot `file` and where on it. Describe it in words
  in the feedback ("the white swatch, left of the selected one"), because the developer never
  sees the coordinates. A `moment` names the clip `file` and `t`, the second they paused on.
  Describe it the same way ("right after Escape, about 7 seconds in"). A screenshot or clip
  with markups is one worth suggesting they drag into the review comment, since `gh` cannot
  upload images or video. For a clip, suggest the MP4.
- **`verdicts`** holds one entry per PR group: `{ "pr": "<ref>", "verdict": "approve" | "changes"
  | "comment", "inferred": true, "because": [5] }`. `inferred: false` means the reviewer picked
  it on the last page, either changing the inferred one or ruling where the board had none.
  Changing any answer for a PR drops a ruling picked that way, so it always reflects the final
  answers. That is the Step 6 ruling for that PR. Do not ask for it again. A unit in
  `units` with no questions gets an entry too, always with `inferred: false`, because the board
  makes the reviewer pick it rather than guessing.
- **Do not wait for a playback confirmation.** The board's last page already showed every ruling
  and what sending would post, so go straight on to Step 4 and post. List the rulings in Step 10's
  report instead, so the transcript still has them.

If they press "Edit and resend" later, `answers.json` is overwritten. Re-arm the wait only when
they say they changed something.

## Step R4: Clean up

When the review is posted, or abandoned:

- Stop the server you started: `preview_stop` in the desktop app, or `TaskStop` on the background
  task elsewhere. Leave a reused one running.
- Undo the `.claude/launch.json` change: remove the `pr-review-board` entry, or the whole file if
  you created it. Never commit it.
- Leave the packet folder. Like the drive-it screenshots and clips, it is the evidence for the
  review. A prepped packet stays where prep mode put it, and its `answers.json` stays with it,
  along with any `answers-<timestamp>.json` an earlier pass left behind (Step R1): the next
  review on the same packet archives, never deletes. When the developer pushes and prep rebuilds
  the packet, the new build goes into its own versioned folder and this one stays exactly as it
  is (`references/prep-mode.md` Step P4); nothing is renamed. The symlink in this session's
  packets folder holds nothing and goes with the scratchpad.
