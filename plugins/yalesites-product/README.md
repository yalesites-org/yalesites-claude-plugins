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
  time or several in one batched pass
- **Ticket sync** — checking whether a ticket still matches how the work
  actually turned out as it moves through review and grooming, and catching
  it up with a comment or an edit
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
| `release-prep` | Preparing a YaleSites release |
| `ticket` | Creating a new GitHub issue or grooming an existing one (invoke directly with `/ticket`) |
| `pr-feedback` | Reviewing, approving, or requesting changes on a YaleSites pull request, or on several at once (batch mode) |
| `ticket-sync` | Checking whether a ticket still matches the work — invoked mid-flow by `pr-feedback` and `ticket`, or directly with `/ticket-sync` |
| `ux-research` | Product decisions and feature evaluation |
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

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
