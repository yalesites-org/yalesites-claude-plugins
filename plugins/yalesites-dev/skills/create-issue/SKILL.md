---
name: create-issue
description: Creates a new GitHub issue in yalesites-org/YaleSites-Internal using the correct template (bug report or feature request). Use this skill whenever the user wants to file a ticket, report a bug, request a feature, write up an issue, or document a problem or idea for the YaleSites project — even if they don't say "create issue" explicitly. Invoke with an optional description: /create-issue [description of the bug or feature].
argument-hint: "[description of what you want to report]"
---

# Create YaleSites GitHub Issue

Your job is to gather just enough information to create a well-formed issue in `yalesites-org/YaleSites-Internal`, then show the user a draft for approval before posting.

## Step 1: Get the description

If `$ARGUMENTS` contains a description, use it. If `$ARGUMENTS` is empty or just whitespace, ask the user one question: "What do you want to report?"

## Step 2: Determine the issue type

From the description, infer whether this is a **bug report** or a **feature request**.

**Bug signals:** something is broken, not working, throwing an error, behaving unexpectedly, regressed, crashing, displaying incorrectly, or not matching expected behavior.

**Feature signals:** asking for something new, an enhancement, a change to existing behavior by design, a "would be nice if", adding support for something, or improving something that works but could be better.

If you're confident, proceed without asking. If genuinely ambiguous (e.g., "the editor experience feels off"), ask once: "Is this a bug report or a feature request?"

## Step 3: Gather any remaining info

Ask only what you still need after reading the description:

- **Affected site or URL** (bugs especially — ask "What site or URL were you on when you saw this? Leave blank if not applicable."). Skip this question if the description already names a URL, or if it's clearly a general/platform-wide issue.
- **Title** — generate a concise, specific title from the description (e.g., "Banner component breaks on mobile when image is missing alt text"). Only ask for a title if the description is too vague to produce a confident one.

Do not ask about priority, assignees, related PRs, or anything else — those are handled during grooming.

Ask all outstanding questions at once, not one at a time.

## Step 4: Fill in the template

Use the appropriate template below. Fill in every section thoughtfully based on what the user told you. Do not leave placeholder text like "..." — if information wasn't provided, use your best judgment or write "N/A".

---

### Bug report template

```
**Describe the bug**
{clear description of what the bug is}

**To Reproduce**
Steps to reproduce the behavior:
{numbered steps based on what the user described; infer reasonable steps if not given explicitly}

**Expected behavior**
{what should have happened instead}

**Screenshots or Screen Recording**
{note any screenshots/recordings the user mentioned, or "N/A if not applicable"}
```

Labels: `forming`

---

### Feature request template

```
**Description**
{clear description of what is wanted and why}

**Screenshot or Screen Recording**
{any mockup, inspiration, or example the user mentioned; or "N/A"}

---
**Ticket Forming**
If you are creating this ticket, anything below here is meant for ticket forming. You do not have to fill this section in.

**Acceptance Criteria**
{draft 3–5 specific, testable acceptance criteria based on the description}
- [ ] {criterion}
- [ ] {criterion}
- [ ] {criterion}

**Tasks Needed To Complete This Work**
If an item on the list is not needed, it should be crossed off but not removed.
- [ ] UX Research - April/Mike
- [ ] Design - Em/April
- [ ] Accessibility - Nick
- [ ] Development - Dave
- [ ] Documentation Change - TBD
```

Labels: `forming`

For the acceptance criteria, think about: what does "done" look like? What would a developer need to verify? What edge cases matter? Make them specific and concrete, not vague.

For the tasks list, leave all items unchecked — grooming will determine what's actually needed.

---

## Step 5: Show the draft

Present the full issue to the user before posting:

```
**Title:** {title}
**Type:** Bug report / Feature request
**Label:** forming

---
{body}
```

Then ask: "Does this look right? I'll create it as-is, or let me know what to change."

## Step 6: Create the issue

Once the user approves (or approves with edits applied), run:

```bash
gh issue create \
  --repo yalesites-org/YaleSites-Internal \
  --title "{title}" \
  --body "{body}" \
  --label "forming"
```

After creating, share the issue URL so the user can open it directly.
