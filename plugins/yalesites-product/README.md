# yalesites-product

Product team workflows for the YaleSites platform for Claude Code.

## What it does

Gives Claude the context and workflows needed to assist the YaleSites product
team with:

- **Release prep** — drafting release notes, feature documentation, release
  emails, QA testing steps, and knowledge base sync
- **Ticket creation & grooming** — creating new GitHub issues and grooming
  existing ones with correct format, acceptance criteria, priority, size,
  type, and labels
- **PR feedback** — reviewing a pull request against its linked issue and
  posting approve/request-changes feedback directly to GitHub, one PR at a
  time or several in one batched pass, scoped to the review dimensions the
  person running it actually rules on
- **Reviewer profile**, a short interview that records what one person
  reviews, so PR feedback asks them the calls that are theirs and labels only
  the checks they performed
- **Ticket sync** — checking whether a ticket still matches how the work
  actually turned out as it moves through review and grooming, and catching
  it up with a comment or an edit
- **Web content** — drafting and revising pages for yalesites.yale.edu
  (user guides, resource pages, release documentation), researched from the
  merged code and written in ASD-STE100 Simplified Technical English, with the
  Layout Builder blocks and config decisions handed over alongside the copy
- **UX research** — the six current user archetypes, top pain points, delights,
  and platform usage data from the 2026 YaleSites UX Report for informing
  product decisions
- **Beacon test question sets** — building a quick content-accuracy question set
  for one site, or a full tiered test bank covering guardrails, safety, and
  edge cases
- **Beacon comparison analysis** — reading an AI Tester A/B comparison export
  (Beacon vs. legacy, model vs. model, or before/after a fix) for answer
  correctness, citation quality, and a stakeholder-ready summary

## Installation

```
/plugin install yalesites-product@yalesites-claude-plugins
```

This plugin works best alongside `yalesites`, which provides deep platform
knowledge that the workflow skills reference:

```
/plugin install yalesites@yalesites-claude-plugins
/plugin install yalesites-product@yalesites-claude-plugins
```

## Skills

| Skill | Trigger |
|---|---|
| `release-prep` | Preparing a YaleSites release, and reconciling the board after it ships |
| `ticket` | Creating a new GitHub issue or grooming an existing one (invoke directly with `/ticket`) |
| `pr-feedback` | Reviewing, approving, or requesting changes on a YaleSites pull request, or on several at once (batch mode) |
| `reviewer-profile` | Setting up or changing how `pr-feedback` is scoped to you (invoke directly with `/reviewer-profile`) |
| `ticket-sync` | Checking whether a ticket still matches the work — invoked mid-flow by `pr-feedback` and `ticket`, or directly with `/ticket-sync` |
| `ux-research` | Product decisions and feature evaluation |
| `yalesites-web-content` | Writing or revising a page that will live on yalesites.yale.edu |
| `beacon-question-set` | A quick content-accuracy question set for testing Beacon against one site |
| `beacon-test-bank` | A full tiered test bank with guardrails, safety, and edge-case coverage |
| `beacon-comparison-review` | Analyzing a Beacon AI Tester A/B comparison JSON export |

## Writing standard

Every skill here that posts to GitHub follows the shared YaleSites GitHub writing
standard, bundled as `skills/ticket/references/github-writing.md` (words) and
`github-communication-format.md` (structure). Tickets, sync comments, PR reviews, and
release notes all lead with a short TL;DR, hold the visible layer to a word budget, push
the depth into named `<details>` blocks, and close with an invisible
`<!-- yalesites:agent -->` block for agent-to-agent payload.

The sentence rules come from ASD-STE100 Simplified Technical English; the
document-level test comes from ISO 24495-1 plain language. Verify a draft before posting:

```bash
python3 skills/ticket/scripts/check-github-text.py draft.md --surface ticket
```

Surfaces: `ticket`, `pr-body`, `pr-review`, `release-notes`, `report`. Both reference
files and the script are generated from `standards/` at the repo root. Edit the canonical
copies there, then run `bash scripts/sync-standards.sh`.

## Reviewer role scoping

`pr-feedback` tailors what it asks, what it writes, and which `pass ___ review` label it applies
to the person running it. It resolves that in three steps: the reviewer's own profile at
`~/.claude/yalesites/pr-feedback/reviewer-profile.md`, then a shared map keyed by GitHub login at
`skills/pr-feedback/references/reviewer-roles.md`, then an ungated fallback that behaves exactly
as the skill did before scoping existed.

Two things need ongoing maintenance, both in `reviewer-roles.md`:

- **The login-to-dimensions map.** Add a row when someone new starts reviewing. Confirm the handle
  with that person rather than inferring it from org membership or commit history. A wrong row
  silently withholds feedback they were the right person to give.
- **The dimension-to-label matrix.** Re-verify it if a repo's label set changes. The file carries
  the command.

Maintained by whoever maintains this plugin. A person with no profile and no row is a normal,
supported state, not a misconfiguration.

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
