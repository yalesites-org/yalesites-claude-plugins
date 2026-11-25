# Held calls, open decisions, and the reviewer's own read (Step 3b detail)

Read this from `SKILL.md` Step 3b. The board mechanics are in `review-board.md`; this file holds
what goes on it: how held calls are sorted against the reviewer's dimensions, how open calls get
put on the record, and Part 2.

## Step 3b: Get the user's calls and their own feedback

Two parts, and neither is optional.

**Ask them on the review board, not in a chat text box.** Read `review-board.md` and
follow it. The board is a local page that shows each held call with its screenshot at full size (or its clip),
numbered callouts on the exact spot, the ticket or PR text with the key line highlighted, and big
option cards. The reviewer can pin, box, and comment on what they see, and one click sends it all
back. Both parts below go on it, Part 2 as the last page. `AskUserQuestion` is the fallback for
the cases that reference lists (no in-lane calls, no local browser, or a reviewer who prefers
chat). The sorting rules below decide what goes on the board, and they do not change.
When Step 1 found a current prepped board, the packet is already built: serve it from this
session's own packets folder through a symlink (`review-board.md` Step R1) instead of building a
new one. When the reviewer already answered that packet in a dashboard (Step R1, "Answered
already"), those answers stand in for the board: do not open it, but the rest of this step still
applies, including the open-decision check and the `defer` handling under "Open calls go on the
record". Its `prep.json` carries every held call tagged by dimension, so the out-of-lane calls to
name below come from there.

**Part 1, the held calls.** Put the brief's **Your calls** items to the user. They
are already scoped to real product decisions (copy, defaults, role gating, scope) because the
audit was forbidden to decide them, so put them to the user in the brief's own words where they
are already clear. Every `ask` screenshot from the driven run goes in as that call's context.

**Sort them against the reviewer's dimensions from Step 0 first.** Every held call belongs to one
of the five dimensions, usually obviously: a copy or defaults question is `product`, a keyboard
path is `a11y`, a spacing question is `design`, an implementation-approach question is `code`.

| The call is | What to do |
|---|---|
| In the reviewer's dimensions | Ask it, as you would have anyway |
| Not in their dimensions | **Name it, do not ask it.** One line: what the call is, which dimension it belongs to, and who owns it if the role map names someone |
| Unclear which dimension | Ask it. Scoping is a filter on questions that clearly are not theirs, not a reason to lose one |
| Anything in the profile's **Always ask me about** | Ask it, even if the brief never held it and even if it sits outside their dimensions. That section is a floor the reviewer set for themselves |

**Out-of-lane calls are stated, never dropped.** The brief raised them for a reason, and this
review is where they would otherwise disappear. Listing them also tells the reviewer what the
posted review will *not* cover, which is what makes a scoped approval honest:

```
Two calls are outside your lane, so I have left them:
- The `--variant` default on line 88 is a code call. That one is for our lead developer.
- The 12px gap under the heading is a design call, April's.
Neither gates your functional approval. Want me to raise them as decisions for whoever owns them?
```

On the board, they go in the PR's unit as `notAsked` and show on its lead-in, with no chat
message and no offer. On the chat fallback, offer to raise each one as a `needs-decision` on the PR (see "Open calls go on the record" below), with **Decides** set to the owner the role map names for that dimension. When no one in `reviewer-roles.md` owns the dimension, ask the reviewer who should decide. Skip it if the reviewer says no.

**On the unscoped path from Step 0, none of this applies.** Every held call goes to the user, as
it does today.

If the brief's Your calls section is empty, say so plainly rather than inventing questions.
An empty section means the audit found nothing that needed a human ruling, which is a real
and common outcome. Say it is empty even when the reviewer is scoped, so an empty brief and a
fully-out-of-lane brief do not look the same from the outside.

### Open calls go on the record

Anything this review leaves open must end up on GitHub with a name and a date, not only in this chat. That is what puts it in the owner's queue: any tooling that tracks who owes what (a router brief or a work dashboard, where the team runs one) reads these labels. The labels, block formats, and resolution lines are defined by the `ticket` skill in the `yalesites-ticket` plugin, in its `routing.md` reference ("Waiting on a person"). Use them exactly, since that tooling parses them.

**Before asking anything, check what's already open.** Read the PR and its linked issue for an open `needs-decision` or `follow-up` (labels plus the latest `## Decision needed` / `## Follow-up needed` block):

```bash
gh pr view NUMBER --repo yalesites-org/REPO --json labels,body,comments \
  --jq '{labels: [.labels[].name], blocks: [(.body, .comments[].body) | select(test("## (Decision|Follow-up) needed"))]}'
```

Put any open decision that names the reviewer to them first, ahead of the brief's calls. If they answer it, post the resolution line from the `ticket` skill's `routing.md` (`## Decision: (b), decided by <name> on 2026-11-03. Reason: ...`) as part of Step 9, and remove the label in Step 8.

**Raise a block when a call stays open:**

| What happened | What to raise | Who |
|---|---|---|
| A held call is out of the reviewer's lane, and they said yes to raising it | `needs-decision` on the PR | Decides: the dimension's owner from the role map |
| The reviewer can't call it yet ("let me think," "I want to see the real site," "check with a teammate") | `needs-decision` if it's a choice, `follow-up` if someone owes an action | The reviewer, or whoever they name |
| The review requests changes that hinge on an unanswered product question | `needs-decision`, and say in the review body that the changes wait on it | The decider |

Default **Needed by** to 5 working days out unless the reviewer gives a date. Post each block as its own PR comment in Step 9, before the review itself, and add the label in Step 8. Then tell the reviewer what you raised, in one line each.

**Never raise one silently.** Each block is a public ask of a named person, so confirm the list with the reviewer before posting, the same way the review body is confirmed.

**Part 2, their own read.** Always ask what they noticed, separately from your questions. They
may have tested the multidev before starting this session, or carry context from a meeting the
diff cannot show. Ask even when your own analysis turned up nothing: their input is a
first-class input to this review, not a fallback for when you are stuck. Pins, boxes, and
comments they leave on the board count as part of their own read.
