# GitHub Communication Format

Shared format spec for every skill that posts something a person will read on GitHub:
PR descriptions, PR review comments, new and groomed issues, ticket-sync comments and
edits, and release notes.

## The principle

Two audiences read these artifacts:

- **People** (a PM opening a ticket, a developer skimming a review, a site owner reading
  release notes) skim. They want the one thing they need to know, fast.
- **Agents** (a review agent reading a dev agent's PR, a sync agent comparing a ticket to
  a diff) read deep. They want every detail.

The verbose analysis is worth keeping for the second audience. It just should not be the
first thing the first audience sees. So: **lead with a short TL;DR, keep only the
essentials in the open, and move the depth into collapsible sections.** Nothing is
deleted, only relocated.

## The TL;DR line

Every artifact opens with a TL;DR, always visible, never collapsed.

- One to three sentences. Aim for 60 words or fewer.
- Plain language for the primary human reader. For product artifacts (tickets, review
  comments, release notes) that is a site owner, PM, or content editor: no Drupal jargon.
  For a developer-facing PR body the reader is a developer peer, so normal technical
  language is fine.
- Lead with the outcome, the ask, or the decision, not the background. "Approving. One
  optional note about the empty state." "This adds a caption field to the Image block."
  "Requesting changes: two blocking items, both about role checks."
- Write it last, once the detail is settled.

## What stays visible (never collapse)

- The TL;DR.
- On a **ticket**: the Description and the Acceptance Criteria. These are what developers
  and QA work from.
- On a **request-changes review**: the numbered list of blocking items, one line each.
  The per-item detail collapses, the list itself does not.
- Any checklist a person acts from: functional testing steps, Release Testing Steps.
- On a **PR body**: the H2 issue-link line (`## [NNN: Title](url)`), the "Description of
  work" bullets, and the trailing `References yalesites-org/YaleSites-Internal#NNN` /
  `Closes ...` lines. The team and GitHub both parse these.

## The collapsible blocks

Use GitHub's native `<details>` element. It renders collapsed by default.

```markdown
<details>
<summary><b>Why this approach</b></summary>

The archetype analysis, the platform-fit findings, the rationale, all of it goes here.

</details>
```

Rules:

- **Blank line after `</summary>` and blank line before `</details>`.** Without them
  GitHub will not render the Markdown inside the block.
- The `<summary>` names what is inside: "Why this approach", "File and line references",
  "Platform-fit analysis", "What I checked", "PRs included", "Detailed changes". Never
  just "Details" or "More".
- Group related detail into a small number of blocks, two to five. Do not scatter ten
  one-line blocks down the page.
- One level deep. Do not nest `<details>` inside `<details>`.
- Tables render inside issue and PR bodies but not reliably inside comments. In a comment,
  use a bulleted list instead of a table.

## Per-artifact guide

| Artifact | Visible by default | Collapsed |
|---|---|---|
| **PR review, approving** | TL;DR, plus any optional notes as a short list | Reasoning, file/line references, what was checked, visreg or docs follow-up discussion |
| **PR review, requesting changes** | TL;DR, plus the numbered blocking-items list (one line each) | Per-item detail (file/line, why, how to fix), optional/nice-to-have items, analysis notes |
| **New or groomed ticket** | TL;DR, Description, Acceptance Criteria | Platform-fit check, archetype and UX-research reasoning, implementation context, prior art and links |
| **ticket-sync comment** | TL;DR: what changed or what is now accurate, one or two lines | The before/after reasoning, the PR or decision trail, cross-references |
| **ticket-sync edit** | The reconciled section itself, clean | If a "why did this change" note is worth keeping, a short collapsed block or a separate companion comment, not inline clutter |
| **Release notes comment** | TL;DR (release theme plus headline counts), Featured Feature section | New Features & Enhancements, Bug Fixes, PRs Included |
| **Release Testing Steps (appended to an issue)** | The steps themselves, plus a one-line summary above them | Nothing usually. The steps are the payload, keep them open |
| **PR description body** | H2 link line, TL;DR, Description of work bullets, Functional testing steps, trailing reference lines | Granular change-by-change notes, technical rationale, cross-repo detail, as a "Detailed changes" block |

## Voice

This file is about structure only. Follow the calling skill's voice guidance for the
words themselves: `michael-voice` where it applies (no em dashes, "we" not "I"),
`pr-feedback`'s override to first-person singular for review comments, and each skill's
own tone notes.
