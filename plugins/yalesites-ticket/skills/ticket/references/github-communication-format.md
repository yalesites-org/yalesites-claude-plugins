# GitHub Communication Format

Canonical source. Do not edit the synced copies inside `plugins/`. Edit this file, then run
`bash scripts/sync-standards.sh`. CI fails if a synced copy drifts from this one.

Companion file: this file governs **structure**. `github-writing.md` governs **words**
(sentence length, plain-language rules, word swaps, per-surface budgets). Read both.

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

That gives every artifact three layers:

| Layer | Mechanism | Who reads it |
|---|---|---|
| **Visible** | Plain Markdown at the top | Everyone. Budgeted, see `github-writing.md` |
| **Collapsed** | `<details>` blocks | A person who wants the depth, and any agent |
| **Machine-only** | An HTML comment block | Agents. Invisible in rendered GitHub |

Each layer has a different test. Visible text has to be worth a person's attention.
Collapsed text has to be worth expanding. Machine-only text has to be worth parsing, and
nothing else.

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

## The machine-only block

Some payload exists purely so the next agent does not have to re-derive it: which
acceptance criterion maps to which file, which PRs a release note covers, what a review
pass already checked. A person never needs it. Putting it in a `<details>` block still
costs them a summary line to ignore.

That payload goes in an HTML comment. GitHub does not render it, so it is invisible on the
page, but it stays in the raw body that `gh api` and the GitHub MCP tools return.

```markdown
<!-- yalesites:agent
surface: pr-review
issue: yalesites-org/YaleSites-Internal#1471
pr: yalesites-org/yalesites-project#1288
ac_coverage:
  - criterion: "Editors can set alt text on each gallery item"
    status: met
    evidence: web/modules/custom/ys_gallery/src/Form/GalleryItemForm.php:88
  - criterion: "Alt text is required before save"
    status: not_met
    evidence: no validation found
checked: [diff, acceptance_criteria, visreg_coverage]
-->
```

Rules, and these are firm:

- **One block per artifact, at the very bottom.** After everything else, including the
  trailing `References` lines.
- **Open with `yalesites:agent`** on its own line so an agent can find it without guessing.
- **YAML inside.** Keys are lowercase snake_case. Keep it flat where you can.
- **Nothing a person needs may live only here.** If it changes what someone should do, it
  belongs in the visible layer or a `<details>` block. The machine block is an index, never
  a source of truth. A human reviewer cannot audit what they cannot see, and an agent will
  sometimes be wrong.
- **No reasoning.** Rationale a person might want to check goes in `<details>`. This block
  holds references, states, and mappings.
- **No secrets.** No tokens, credentials, internal hostnames, or anything that would not
  survive the repository going public.
- **Never edit another agent's block** in place. Post your own artifact, or add a comment
  with its own block.

If there is nothing worth parsing, leave the block out. An empty one is noise.

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

What goes in the machine block, by artifact:

| Artifact | Machine-only payload |
|---|---|
| **PR review** | Acceptance-criteria coverage map, what the pass checked, file/line index |
| **New or groomed ticket** | Related issue and PR refs, epic/child links, platform-fit verdict as a flag |
| **ticket-sync comment or edit** | What was compared, the PR or decision that triggered it |
| **Release notes** | The PR list as structured refs, the milestone, the featured-feature issue |
| **PR description** | Linked issue refs, cross-repo companion branches |
| **Report** | Findings as structured records (id, severity, location) |


## Voice

This file is about structure. For the words themselves, follow `github-writing.md` in this
same directory: sentence-length caps, active voice, the word-swap table, and the visible
budget for each surface. On top of that, apply the calling skill's voice guidance:
`michael-voice` where it applies (no em dashes, "we" not "I"), `pr-feedback`'s override to
first-person singular for review comments, and each skill's own tone notes.
