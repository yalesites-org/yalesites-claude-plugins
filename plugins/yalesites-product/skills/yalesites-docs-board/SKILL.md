---
name: yalesites-docs-board
description: "Take a batch of YaleSites docs tickets from ticket to built draft in one pass: match each ticket against the full yalesites.yale.edu sitemap, screenshot the live page it changes, draft the change, and show every ticket on a local side-by-side board (live page on the left, proposed blocks on the right with additions, edits, and removals highlighted, and a Layout Builder block named for every new piece). The reviewer approves, requests changes, or skips each one, and only approved tickets get built: site pages as unpublished drafts through yalesites-page-build, internal docs (READMEs, repo docs) as a commit on a branch. Use when the user wants to work through several docs tickets at once, e.g. 'draft my docs tickets', 'do the docs for this release', 'run the docs board on 1818, 1870 and 1901', 'batch the Docs: tickets', or when the work dashboard's Draft docs button sends a list of tickets. For one page with no board, use yalesites-web-content and yalesites-page-build directly."
argument-hint: "[tickets, e.g. yalesites-org/YaleSites-Internal#1818 1870 1901, or nothing for every open Docs ticket assigned to you]"
---

# YaleSites Docs Board

Docs tickets pile up and then get written in a batch at a known point in the release. Each one
needs the same four things: find the page it touches, see what is there now, write the change,
and build it. Done one at a time in chat, the reviewer reads a wall of markdown and has to picture
where each paragraph lands on a page they cannot see.

This skill does the batch in one pass and puts every proposed change on a board next to a
screenshot of the live page, block by block. The reviewer rules on each ticket with one click.
Only what they approve gets built.

It writes nothing itself that other skills already cover:

| Piece | Owned by |
|---|---|
| Researching the feature, STE, house style, the freshness audit, the draft's Title / Teaser / Config block | `yalesites-web-content` |
| Building on yalesites.yale.edu in Layout Builder, never publishing, the verify pass | `yalesites-page-build` |
| Intake, the sitemap catalog, the live capture, the board, the routing | **this skill** |

**The promises:**
- Nothing is built before the reviewer approves it on the board, for that revision.
- Nothing is ever published. `yalesites-page-build`'s rules apply in full.
- Internal docs are committed on a branch. Nothing is pushed, and no PR is opened, without a
  separate go-ahead in chat.
- Nothing is posted to a ticket without confirmation.

## Workflow

1. Intake: which tickets
2. Catalog and triage: which page each one touches, or that it needs a new one
3. Capture the live pages
4. Draft each ticket
5. Assemble and validate the packet
6. Open the board and wait
7. Read the decisions, revise, repeat until settled
8. Build what was approved
9. Hand off

Scripts are in `scripts/`. Run them with `python3`, from anywhere. Below, `<skill-dir>` is this
skill's folder and `<dir>` is the packet folder.

---

## Step 1: Intake

**Tickets named in the request** (the dashboard sends them as `owner/repo#N`): use those. A bare
number means `yalesites-org/YaleSites-Internal`.

**Nothing named:** list the open docs tickets assigned to the user. A docs ticket is one the work
dashboard's Docs & web tab would show: a `Docs:`, `Web:`, or `[DOCS]` title prefix, or the
`docs-comms` label (or the older `documentation` and `communications` labels it replaced).

```bash
gh issue list -R yalesites-org/YaleSites-Internal --assignee @me --state open --limit 100 \
  --json number,title,labels,milestone \
  --jq '.[] | select((.title|test("^(Docs:|Web:|\\[DOCS\\])";"i")) or ([.labels[].name]|any(.=="docs-comms" or .=="documentation" or .=="communications")))'
```

Show the list with milestones, soonest first, and ask which to take. Default to the ones in the
next release's milestone. **Keep a batch to eight or fewer.** Every ticket costs real research, and
past eight the board turns into a chore that gets rubber-stamped.

Read each ticket in full (`gh issue view <n> -R <repo> --comments`). Drop any that are not
content work (a Storybook component, a dev-owned README the developer is writing), and say why.

## Step 2: Catalog and triage

Build or reuse the catalog of every page on the site. It is cached for a day:

```bash
python3 <skill-dir>/scripts/catalog.py refresh
python3 <skill-dir>/scripts/catalog.py search <words from the ticket title>
python3 <skill-dir>/scripts/catalog.py show <path>          # title, teaser, headings, nav
python3 <skill-dir>/scripts/catalog.py section "user guide"  # siblings for a new page
```

The catalog is the live sitemap (`https://yalesites.yale.edu/sitemap.xml`) plus each page's
title, teaser, and headings, with the nav location from `yalesites-web-content`'s inventory
merged in. It is current where the inventory is a snapshot, so trust it for "does this page
exist and what is it called."

Sort each ticket into one kind:

| Kind | When |
|---|---|
| `edit` | The ticket names a page, or the feature is already documented on one. Most docs tickets |
| `new` | Nothing on the site covers it. Propose the URL alias, parent, and siblings |
| `internal` | The target is a markdown file in a repo: a module README, `docs/`, a CONTRIBUTING file. Not on yalesites.yale.edu |

Read the top two or three search hits, not only the first. A ticket for "list styles in the
editor guide" may belong on a page whose title never says "list."

**Ask before drafting when triage is a judgment call:** a new page that overlaps an existing
one, an edit that could land on two pages, an internal doc whose repo or path is unclear. Batch
these into one `AskUserQuestion` (up to four questions). A wrong target costs a whole draft.

## Step 3: Capture the live pages

Make the packet folder, then capture every `edit` target in one call:

```bash
DIR=~/.claude/yalesites/docs-board/packets/docs-<yyyy-mm-dd>
mkdir -p "$DIR"
python3 <skill-dir>/scripts/capture.py --packet "$DIR" 1818=/create-powerful-page-sections 1870=/explore-resources/working-with-content/finding-and-exporting-content
```

It runs headless and logged out, in its own Playwright CLI session (`@playwright/cli@0.1.22`,
the version `pr-feedback` and `yalesites-page-build` pin), so it reads only what the public sees and
never touches the browser `yalesites-page-build` logs in with. For each item it writes a full-page
`current.png` at 1280 wide, and `current.json`: every Layout Builder block with its type, section
layout, column, padding, content as markdown, and position on the screenshot. If the browser will
not open, see the Browsers table in `pr-feedback/references/drive-it.md` and pass the same
`--browser` value here.

- **A page that does not return 200** gets no screenshot. The URL is wrong, or the ticket is
  really a new page. Fix it before drafting.
- **Open `current.png` and look at it** before drafting. The block list comes from markup. The
  screenshot is what the reader sees, and it catches a block type the script guessed wrong.
- **The capture is the published revision.** If someone already has a forward draft on that
  page, it is invisible logged out. `yalesites-page-build` checks the Tasks sidebar before building
  and stops if it finds one. Say so in the item's notes if you know of one.

**Internal edits:** read the file from the default branch, not from whatever the local checkout
has, then split it into sections:

```bash
mkdir -p "$DIR/1770"
git -C <checkout> fetch -q origin
git -C <checkout> show origin/<default-branch>:<path> > "$DIR/1770/README.current.md"
python3 <skill-dir>/scripts/packet.py split-md "$DIR/1770" "$DIR/1770/README.current.md" --repo <owner/repo> --path <path>
```

The `mkdir` comes first: `capture.py` makes each item's folder itself, but the `git show` redirect
does not, and `split-md` only creates the folder after it has read the file.

Look for the checkout under `~/code/<repo-name>` first. Ask for its path once if it is not there.

## Step 4: Draft each ticket

For every ticket, follow `yalesites-web-content` Steps 2 to 6 in full: research the feature from
the merged code, match a sibling page, run the Step 3b freshness audit on an edit, write in STE,
and pass `check-github-text.py --surface page-draft`. Save its deliverable as `<dir>/<id>/draft.md`
(a `new` page has no capture, so `mkdir -p "$DIR/<id>"` first). That skill decides what the words
are. This step adds one thing: expressing the draft as **ops** against the captured blocks, so the
board can show it in place.

Read `references/packet-format.md` before writing ops. The rules that carry the weight:

- **On an edit, every captured block appears in `ops` exactly once:** keep, edit, or remove. Ops
  run top to bottom, and an `add` sits where it will appear on the page.
- **Edit inside the existing blocks wherever you can.** Start from the block's `markdown` in
  `current.json` and change only what needs changing. The diff stays small enough to read, and
  the build becomes an exact replace in a block that already exists, the safest change
  `yalesites-page-build` makes.
- **Every `add` names its Layout Builder block, and why.** Use the labels from the `yalesites`
  skill's `references/blocks-reference.md`. When the block is anything but Text, fill `blockWhy`
  with the reason a different block would be wrong, and `settings` with the form values that matter.
  Follow `yalesites-page-build/references/layout-conventions.md`: a page ends on a non-text block,
  and adjacent blocks need padding.
- **A restructure is a call for the reviewer, not a silent edit.** The freshness audit's
  structural findings (removing a section, merging groups) become `remove` and `add` ops with a
  `why`, so the reviewer rules on them on the board. That is the "surface it, do not silently
  restructure" step from `yalesites-web-content`, in a form they can click.
- **Contradictions with the ticket go in `summary` and `notes`**, plainly. The board is where the
  reviewer sees them.

**Three or more tickets: draft in parallel.** Start one subagent per ticket. Give each the
ticket ref, its kind and target, the paths to `current.json` and `current.png`, the paths to this
file, `references/packet-format.md`, and `yalesites-web-content/SKILL.md`, and ask it to write
`draft.md` and `ops.json` (the item's `ops`, `summary`, `build`, and `notes`) into the ticket's
folder. Each subagent researches its own feature, so this saves the most time. Read every result
yourself before assembling it. A subagent's draft gets the same scrutiny as your own.

## Step 5: Assemble and validate

Write `<dir>/packet.json` (format in `references/packet-format.md`), then:

```bash
python3 <skill-dir>/scripts/packet.py validate "$DIR"
```

Fix every error. Read the warnings and fix them or know why not. Then record each ticket:

```bash
python3 <skill-dir>/scripts/packet.py status yalesites-org/YaleSites-Internal#1818 on-board --packet docs-<yyyy-mm-dd> --target <url-or-path>
```

The work dashboard reads that status file to show where each docs ticket stands.

## Step 6: Open the board and wait

The board is `scripts/board/index.html`. It is served by `pr-feedback`'s review board server,
started with this board's folder, route, output file, and app name, so the two boards share one
server (and one set of fixes) and still run side by side on different ports. The server is in the
sibling skill, so resolve the path through `realpath` first, the same way `catalog.py` finds
`yalesites-web-content`, and a symlinked install still works:

```bash
SERVER="$(realpath <skill-dir>)/../pr-feedback/scripts/review-board/server.py"
```

**Pick the port.** Start at 8775. `curl -s http://localhost:<port>/api/health`:

| Result | Meaning |
|---|---|
| Connection refused | Free. Use it |
| `{"app": "docs-board", "packets": "<this packets folder>"}` | Already running for these packets. Reuse it |
| Anything else | Taken. Try the next port up |

**In the Claude desktop app, with the Browser pane tools:** add this to `configurations` in the
project's `.claude/launch.json` (create the file with `"version": "0.0.1"` if there is none, and
note that you did):

```json
{
  "name": "docs-board",
  "runtimeExecutable": "python3",
  "runtimeArgs": ["<resolved server path>", "--packets", "<home>/.claude/yalesites/docs-board/packets", "--board-dir", "<skill-dir>/scripts/board", "--route", "/api/decisions", "--out", "decisions.json", "--app", "docs-board", "--port", "<port>", "--exact-port"],
  "port": <port>
}
```

Start it with `preview_start`, go to `http://localhost:<port>/?packet=<id>` with `preview_eval`,
and take one screenshot to confirm it loaded the packet rather than "Couldn't load packet." The
board needs about 1400px of width for the two panes side by side. If the pane is narrower, say
the reviewer can open the same URL in their own browser.

**Anywhere else on a Mac:** run the server in the background (`run_in_background`) with the same
arguments, read the port from its `REVIEW_BOARD_URL` line (it moves to the next free port if
yours was taken between the check and the start), and `open "http://localhost:<port>/?packet=<id>"`.

```bash
python3 "$SERVER" --packets ~/.claude/yalesites/docs-board/packets --board-dir <skill-dir>/scripts/board \
  --route /api/decisions --out decisions.json --app docs-board --port <port>
```

The server accepts a Send only from the board itself (a `localhost` origin on its own port, as
JSON), so a page open in another tab cannot write `decisions.json`.

Tell the reviewer in one or two lines: the board is open, how many tickets it holds, and that the
numbers on the screenshot match the cards on the right. Then arm one wait with the `Monitor`
tool. It ends the moment they press Send:

```
Monitor({
  command: 'until [ -f "<dir>/decisions.json" ]; do sleep 1; done; echo "decisions.json written"',
  description: "docs board decisions for <packet-id>",
  timeout_ms: 1800000
})
```

That `until` loop belongs in `Monitor`, never in Bash, foreground or `run_in_background`: a
sleep-based wait in Bash is blocked, and the Monitor tool is the one made for waiting on a
file. Its single event wakes the session. Read `<dir>/decisions.json` then. If the monitor
expires before the reviewer is done, arm it again. Do not poll in a loop and do not ask "are you
done?" If the reviewer gives their decisions in chat instead, use those and `TaskStop` the monitor.

**No local browser** (a cloud or remote session) or **no `python3`**: skip the board. Post each
ticket's summary and `draft.md` in chat and ask for a decision on each.

## Step 7: Read the decisions, revise, repeat

**Play every decision back in chat first**, one line per ticket, describing comments in words
("on the new Inline Message: shorter"), so a misclick gets caught before anything is built.

| Decision | Do |
|---|---|
| `approve` | Status `approved`. It goes to Step 8 |
| `skip` | Status `skipped`. Leave the ticket alone |
| `changes` | Revise the item from the notes and comments. Re-run `yalesites-web-content`'s checker on the new copy. Bump `revision`, set `previousFeedback` to one line restating what they asked for, validate, and set status `on-board` again |

**A ticket built on an earlier round does not come back.** `packet.py status <ref> built` (and
`building`) sets `locked` on that item in `packet.json`. The board shows a locked item read-only
with a Built badge, counts it as settled, and leaves it out of `decisions.json`, so the stale
`approve` from the round that built it is never sent again. The status file stays as the
backstop: on every round after the first, check `status.json` before acting on an `approve`. If
a ticket at `built` or `building` still arrives with a decision (a packet edited by hand, a lock
that did not get written), say so in the playback and leave it out of Step 8. Only `approved`
and `on-board` tickets go on to be built.

When anything was revised: delete `decisions.json`, tell the reviewer to reload the board (approved
tickets keep their decision, revised ones start fresh with the banner), and arm the same `Monitor`
wait as in Step 6 again. Delete the file first, or the new wait ends at once on the old decisions.
Repeat until nothing is left at `changes`.

If the reviewer wants the approved tickets built while others are still in revision, build them
now. Otherwise build after the board settles, so the CAS login in Step 8 covers the whole batch.

## Step 8: Build what was approved

Build each approved ticket once. Set `building` as each one starts: that locks the item in
`packet.json`, so the board stops offering it and a round that arrives mid-build cannot pick it
up. `built` keeps the lock. The lock finds the packet through the `--packet` recorded in Step 5,
so pass `--packet` again if that status entry was never written, and the item by its ticket ref
(pass `--item <id>` if the ref alone does not name one item). Before starting any of them,
still read `~/.claude/yalesites/docs-board/status.json` and drop every ticket already at `built`
or `building`: building it again would put a second draft on the page or a second commit on the
branch, and the lock only guards the board, not a decision taken in chat.

### Site pages (`edit` and `new`)

Hand each approved ticket to `yalesites-page-build`, one at a time, in one logged-in browser for
the whole batch. Its preflight, CAS login, Create New Draft flow, save, and verify pass all apply
unchanged. The item is the build plan: `draft.md` for title, teaser, and config, and the ops for
the layout.

| Op | page-build action |
|---|---|
| `keep` | Nothing |
| `edit` | The exact-replace recipe on that block. Replace only the changed passages, never the whole block |
| `add` | The add-inline-block recipe with the named block and `settings`, then the Move recipe to put it in place |
| `remove` | Layout Builder's Remove block form, at `/layout_builder/remove/block/overrides/node.<nid>/<section>/<region>/<uuid>` |
| remove + add marked as a move | The Move recipe |

**Map capture ids to Layout Builder UUIDs by order and content, never by order alone.** `b3` is
the third block on the public page. On `/node/<nid>/layout`, read `[data-layout-block-uuid]` in
order, and confirm each target block's text matches the capture's `markdown` before changing it.
If they do not match (the page changed since the capture, or a forward draft exists), stop and
recapture instead of guessing.

Record each result:

```bash
python3 <skill-dir>/scripts/packet.py status <ref> built --result '{"nid": 559, "url": "https://yalesites.yale.edu/node/559/latest"}'
```

Use `building` while it runs, and `failed` with `--note` if it does not finish. `failed` takes
the lock off and bumps the item's `revision`, so the board treats it as undecided: the approve
that started the build is never sent again, and the ticket needs a fresh approve before it is
built again. That is on purpose. A page that half-built (draft created, some ops applied) is
not the page the reviewer approved, so before it goes back on the board, recapture it if a
draft was saved, and add what got applied and what did not to the item's `notes`.

### Internal docs

1. Render the approved file: `python3 <skill-dir>/scripts/packet.py render "$DIR" <id> --out <tmp>`.
   That output is exactly what the board showed, so nothing is retyped.
2. In the local checkout, start `target.branch` from `origin/<default-branch>`. If the checkout has
   uncommitted work or sits on another branch, use a `git worktree` instead of switching. Never
   stash or overwrite someone's work in progress.
3. Write the file and commit it with the `commit-conventional` skill (`docs(<scope>): ...`,
   referencing the ticket in full `owner/repo#N` form).
4. Stop there. Report the branch and commit, and ask before pushing or opening a PR. On a yes,
   use `yalesites-dev:yalesites-pr` if it is installed.
5. Status `built` with `--result '{"branch": "...", "commit": "..."}'`.

## Step 9: Hand off

Report in one table: ticket, decision, and result (the draft URL and node, or the branch and
commit). Under it, what is left: screenshots owed, release-day publishing, a PR waiting on a
go-ahead, follow-ups the freshness audit found.

Then offer, without doing it: a short comment on each built ticket with the draft link (through
`ticket-sync` if the ticket's scope moved). Post only on a yes.

Clean up: stop the board server if you started it (`preview_stop`, or `TaskStop` on the background
task), `TaskStop` a `Monitor` wait that is still armed, and undo the `.claude/launch.json` change. Leave the packet folder. It is the record of what
was proposed and approved, and the dashboard reads its status.

## Status file

`~/.claude/yalesites/docs-board/status.json`, keyed by ticket ref. Write it only through
`packet.py status`. States: `drafting`, `on-board`, `changes`, `approved`, `building`, `built`,
`skipped`, `failed`. The work dashboard joins it onto its Docs & web tab, the same way it joins
`pr-feedback`'s prep status onto the review queue. `building` and `built` also set `locked` on
the ticket's item in its packet (see Step 7), and `failed` clears it and bumps the item's
`revision` (see Step 8). One ticket touching two pages is two items with the ref suffixed
(`#1818-a`, `#1818-b`), each with its own status entry. If the file is not valid
JSON, `packet.py status` stops and says so rather than replacing it: fix or remove the file by
hand, because replacing it would drop every other ticket's state.

## Related skills

- `yalesites-web-content`: writes every draft this skill puts on the board
- `yalesites-page-build`: builds the approved site pages
- `pr-feedback`: the review board this board is modeled on, the server that serves both boards
  (`scripts/review-board/server.py`, tests included), and the shared Playwright browser setup in
  `references/drive-it.md`
- `ticket-sync`: when a draft shows that the ticket's scope moved
- `release-prep`: publishes the staged drafts on release day
