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
- **UX research** — the six current user archetypes, top pain points, delights,
  and platform usage data from the 2026 YaleSites UX Report for informing
  product decisions

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

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
