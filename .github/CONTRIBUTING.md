# Contributing to yalesites-claude-plugins

## Plugin Contract

A valid plugin must have all three of the following:

**1. `.claude-plugin/plugin.json`** with required fields:

```json
{
  "name": "your-plugin-name",
  "version": "0.1.0",
  "description": "One sentence describing what this plugin does.",
  "author": {
    "name": "Your Name or Team",
    "url": "https://github.com/yalesites-org/yalesites-claude-plugins"
  },
  "keywords": ["yalesites", "relevant-keyword"]
}
```

**2. At least one skill:** `skills/<skill-name>/SKILL.md` with frontmatter:

```markdown
---
name: your-skill-name
description: When Claude should activate this skill (be specific).
---
```

**3. A `README.md`** in the plugin root documenting what it does and how to install it.

Run `bash scripts/validate-plugins.sh` from the repo root before opening a PR.

## Shared Writing Standards

If your plugin has a skill that posts to GitHub (an issue, a PR body, a review, a
release note, a report), it must follow the standards in `/standards` at the repo root.

Add the plugin to the `TARGETS` array in `scripts/sync-standards.sh`, pointing at the
skill directory that hosts the shared files, then run:

```bash
bash scripts/sync-standards.sh
```

Never hand-edit the copies under `plugins/`. They are generated, and CI fails on drift.
To change a rule, edit `/standards/github-writing.md` or
`/standards/github-communication-format.md` and re-sync. A rule change is a `MINOR` bump
for every plugin that carries a copy.

## Versioning

Bump `version` in `plugin.json` with every PR:

| Change | Bump |
|---|---|
| Content fixes, typos, reference updates | `PATCH` — e.g., `0.1.0` to `0.1.1` |
| New skills, new reference files, expanded coverage | `MINOR` — e.g., `0.1.0` to `0.2.0` |
| Breaking changes to skill names or plugin identity | `MAJOR` — e.g., `0.1.0` to `1.0.0` |

## Core Team Plugins (`/plugins/`)

Maintained by `@yalesites-org/claude-core-team`. Open a PR against `main` —
a team member will review. The PR template includes the full checklist.

## Community Plugins (`/external_plugins/`)

Not yet open for external submissions. Watch this repo for updates.
