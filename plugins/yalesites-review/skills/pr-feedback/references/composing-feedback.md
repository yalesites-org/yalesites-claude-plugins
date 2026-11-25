# Composing the feedback and offering follow-ups (Steps 4 and 5 detail)

Read this from `SKILL.md` Step 4, before writing the review body.

## Step 4: Turn the user's answers into actionable feedback

Once the user responds, your job is translation: turn their (possibly short, possibly informal) input into feedback a developer can act on without a follow-up round trip.

**Scope the composed feedback to the reviewer's dimensions from Step 0.** The brief carries
findings across every dimension, and the temptation is to pour all of them into the review body
because they are sitting right there. Don't. A design reviewer's review must not carry code-level
file-and-line notes they never made: the developer reads the whole body as that person's review,
and follows up with them on notes they cannot defend.

So: the reviewer's own observations and the brief findings inside their dimensions go in the body.
Findings outside their dimensions stay out of it, having already been named in Step 3b. The
mechanical ones among them already went to the developer from the automated pass, so they are not
lost by being left here.

If that empties the body completely, say so. An approval with no feedback is a normal outcome and
Step 6 already handles a feedback-free approval.

**On the unscoped path, no filtering. Everything the user's answers support goes in.**

For every point that does go in:

- **Name the file and line(s)** from the brief's acceptance-criteria coverage map, or from the diff if Step 2 had to read it (`path/to/file.php:42` style, or the closest anchor if exact lines shifted).
- **Say what to change**, not just what's wrong. "This should check the user's role before rendering" beats "this seems off."
- **Say why**, tying back to the issue or a concrete risk (a11y, broken state, security, mismatched spec), one line is enough.
- **Separate blocking from optional.** If the user's feedback includes both must-fix items and nice-to-haves, label them so the developer doesn't have to guess what's gating merge. There is no third bucket. Anything the reviewer expects to see changed before merge is blocking, however small (a wording fix, a doc line, a rename). "Optional" means the developer can skip it and merge without anyone following up. Never write "edits before merge (non-blocking)": it is a contradiction, and Step 6 turns it into the wrong review event.

Keep the tone direct and collegial, matching a ticket-tone memory such as [[feedback_ticket_tone]] if the person running the skill has one, no "PM-approved," no "do not push back," no ownership stamps. State the feedback and let it speak for itself.

**New scope found mid-review doesn't automatically become a new ticket.** If reviewing the diff surfaces functionality worth adding beyond what the linked issue asked for, don't default to grooming it into a separate backlog ticket, ask the user first: as a question on the board, in that PR's group, when Step 2 found it (`review-board.md`), or in chat on the fallback. They may want it folded into the existing ticket instead (edited in after the PR merges) with the new functionality just drafted as a PR comment for the developer to see now.

**Voice: use one if available.** If `config.md`'s `voice_skill` names a skill and it is installed, apply it. Otherwise, if a personal writing-voice skill exists for whoever is running this, apply that: the comment goes out under that person's name. Neither is required. If none exists, default to a plain, direct, dev-facing tone: specific, unadorned, no forced friendliness.

**Exception, stay singular ("I"), not "we."** This overrides any writing-voice skill's default person, even if that skill normally speaks as "we" (some personal voice skills do). PR feedback is one reviewer's read on the code, not an org-wide statement, so write it in first person singular: "I think this should check the role first," not "we think." Apply this to every comment this skill posts, clarifying questions, the review body, and any follow-up ticket offers from Step 5.

### How this reads on GitHub

The review body is read by a person first. Compose it per `github-communication-format.md` and write it per `github-writing.md` (both in this folder):

- **Open with a TL;DR line**, the outcome in one or two sentences. "Approving. One optional note about the empty state." / "Requesting changes: two blocking items, both about role gating."
- **Keep visible:** the TL;DR, and on a request-changes review the numbered list of blocking items (one line each, what to change, which file).
- **Collapse into `<details>` blocks with named summaries:** the per-item detail (file/line references, why it matters, how to fix), the optional/nice-to-have items, "what I checked" notes, and the visreg-coverage and documentation follow-up discussion from Step 5. Group them, two to four blocks, not one per point.
- **Close with a `<!-- yalesites:agent -->` block** holding the acceptance-criteria coverage map from the brief, what this pass checked, and the file/line index. That payload is what the next agent would otherwise re-derive from the diff, and no person needs to read it. Never put the approve/request-changes call or a blocking item in there: if it changes what someone does, it stays visible.
- The same TL;DR-first shape applies to the Step 3 clarifying-question comment if it goes to GitHub rather than staying in chat.

**On the words.** `github-writing.md` caps a review's visible layer at 250 words, the tightest of any surface, because a reviewer's verdict is the whole point and everything else is support. It also carries the one exception that matters here: a review is argument, not procedure, so the 20-word sentence cap and the one-instruction rule are relaxed for rationale, and only inside a collapsed block. The word swaps, active voice, and the no-em-dash rule still apply everywhere.

Check the draft body before posting:

```bash
python3 <skill-dir>/scripts/check-github-text.py review.md --surface pr-review
```

## Step 5: Offer the follow-up tickets the brief already found

The audit's brief has a **Follow-ups worth a ticket** section. It covers both checks that used
to happen here, so this step is now offering them, not finding them.

**Both are non-blocking.** Neither affects the approve or request-changes call in Step 6. Say
that explicitly when raising them, so an offer to open a ticket does not read as a condition
on this PR.

**On the board, these offers are questions, built with the rest of the packet.** Each gets an
`approve`-verdict "Ticket it" option and a "Skip" option in its PR's group; the docs offer's
options name where the doc lives. Act on the answers after the board is sent, without asking
again. The wording below is for the chat fallback.

**A. Visreg coverage gaps.** The brief flags a brand-new block, or a new variant, field, or
option on an existing block, that the shared visreg content set will not represent. The
consequence is worth stating when you raise it: the next PR to touch this area will have no
reference page either, so the gap compounds. Offer a follow-up ticket as a heads-up, not an
`AskUserQuestion`. If they want it, **invoke the `ticket` skill** (in the `yalesites-ticket` plugin) to create it, assigned to
whoever is running this, with acceptance criteria naming the specific block and the page it
belongs on under `/blocks-for-visreg` or `/content-types`.

**B. Documentation.** The brief flags a documentation item in the ticket's acceptance criteria
that the PR does not include, or user-facing behavior changing with no doc change anywhere.
Offer a follow-up ticket. If they want it, **invoke the `ticket` skill** to create it, with:

- **Assignee:** whoever is running this skill (the reviewer login from `config.md`), not the PR's developer.
- **Title prefix:** `Docs:`, per the `ticket` skill's conventions.
- **Where it lives:** ask which applies. External and editor-facing is yalesites.yale.edu.
  Internal is Teams, or GitHub (the org-wide internal knowledge repo, or a repo-specific
  README or docs folder).

**Every follow-up ticket goes through the `ticket` skill, never a hand-written `gh issue create`.**
Copying its body format is not enough. The skill is what sets Status, Priority, Risk, and Issue
Type on the board and reads them back. A ticket written by hand lands with the right labels and
an empty board, which is how `YaleSites-Internal#1870` shipped without Priority or Size on
2026-10-05.

If the brief's follow-ups section is empty, skip this step without comment. Do not go hunting
for follow-up work the audit did not surface.
