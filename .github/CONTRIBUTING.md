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
for every plugin that carries a copy, so commit it as `feat:`.

## Before you open a skill PR

Run the skill-authoring checklist against your branch first. It lives at
`/standards/skill-authoring-checklist.md` and groups the defects that came back in three
rounds of review on six skill PRs: cross-plugin pointers with no fallback, rules copied into
several files, commands that are not in `allowed-tools` or do not run on macOS, regexes that
match the wrong thing, numbers that disagree with their source, state files with no plan for a
second run, and PR titles that get the wrong version bump.

The fastest way through it is the `skill-review` skill in `yalesites-dev`: it diffs the branch
against `main`, walks every item, runs the commands your skill tells agents to run, and reports
in the shape the reviewer uses. Or go through the file by hand. Either way, also run:

```bash
bash scripts/validate-plugins.sh
```

Fix what the checklist finds before opening the PR. The review will find it otherwise, and a
round of review costs more than the check.

## Versioning

Do not edit `version` in `plugin.json` by hand. [release-please](https://github.com/googleapis/release-please)
sets it from the Conventional Commit messages that land on `main`:

| Change | Commit type | Bump |
|---|---|---|
| Content fixes, typos, reference updates | `fix:` or `docs:` | `PATCH` — e.g., `0.1.0` to `0.1.1` |
| New skills, new reference files, expanded coverage | `feat:` | `MINOR` — e.g., `0.1.0` to `0.2.0` |
| Breaking changes to skill names or plugin identity | `feat!:` or a `BREAKING CHANGE:` footer | `MAJOR` — e.g., `0.1.0` to `1.0.0` |

`chore:`, `ci:`, and `test:` commits do not trigger a release.

Each plugin gets its own version, and a commit bumps only the plugins whose files it
touches. After every merge to `main`, release-please opens or updates one release PR
that holds the pending bumps and changelogs. Several commits or PRs before that release
PR merges still make one bump: the largest one wins. Merging the release PR writes the
new versions and tags each plugin, e.g. `yalesites-dev-v0.7.0`.

PR titles must be Conventional Commits too. CI checks this, because a squash merge uses
the title as the commit message. A rebase merge uses the individual commit messages.

Prefer squash or rebase. With "Create a merge commit", release-please skips any commit
dated before the last release, so a branch that started before the last release gets no
bump. It walks history newest-first and stops at the last release commit, and a merge
commit keeps the branch's original commit dates.

Adding a plugin? Add it to `packages` in `release-please-config.json` and give it a
starting version in `.release-please-manifest.json`.

## Core Team Plugins (`/plugins/`)

Maintained by `@yalesites-org/claude-core-team`. Open a PR against `main` —
a team member will review. The PR template includes the full checklist.

## Community Plugins (`/external_plugins/`)

Not yet open for external submissions. Watch this repo for updates.
