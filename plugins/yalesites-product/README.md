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
- **UX research** — user archetypes, mental models, and pain points from the
  YaleSites User Insight Report for informing product decisions
- **Backlog hygiene** — a read-only audit of the backlog that reports tickets
  missing acceptance criteria, board fields, or a type, and hands findings off
  to the `ticket` skill for grooming

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
| `ux-research` | Product decisions and feature evaluation |
| `backlog-hygiene` | Auditing the backlog for tickets that need grooming (read-only) |

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
