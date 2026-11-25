# yalesites-review

The human half of YaleSites PR review. Claude walks you through what to test and where, runs it on
the multidev or Storybook with screenshots, settles the product and UX calls with you, and posts
the review with the right labels.

## Who it's for

Reviewers. This plugin assumes `yalesites-ticket` is installed too, for screenshots on tickets and
the ticket skill's routing and board references.

## Installation

```
/plugin install yalesites@yalesites-claude-plugins
/plugin install yalesites-ticket@yalesites-claude-plugins
/plugin install yalesites-review@yalesites-claude-plugins
```

## Skills

| Skill | Use it for |
|---|---|
| `pr-feedback` | Reviewing, approving, or requesting changes on a YaleSites PR, or on several at once |
| `pr-brief` | Writing a local pre-review brief for a PR. Read-only: it never posts, comments, or labels. `pr-feedback` runs it when no brief exists |
| `reviewer-profile` | Setting up what you review, so `pr-feedback` asks you only your calls (`/reviewer-profile`) |
| `ticket-sync` | Checking whether a ticket still matches the work. Also run by `pr-feedback`, `ticket`, and `yalesites-pr` |

## Pre-review briefs

`pr-feedback` starts from a brief file with fixed sections, described in
`skills/pr-feedback/references/brief-format.md`. It looks for one in this order:

1. A current brief already on disk.
2. A brief from the skill named in `brief_skill` in your config, if you set one.
3. The generic `pr-brief` skill.

## Your config

Per-person settings live in `~/.claude/yalesites/pr-feedback/config.json`. The file is optional and
every key has a default. Your reviewer login defaults to the account `gh` is logged in as. The keys
are listed in `skills/pr-feedback/references/config.md`.

## Reviewer role scoping

`pr-feedback` tailors what it asks and which `pass ___ review` label it applies to the person
running it. It checks your own profile at `~/.claude/yalesites/pr-feedback/reviewer-profile.md`,
then the team map keyed by GitHub login in `skills/pr-feedback/references/reviewer-roles.md`, then
an ungated fallback. Having no profile and no row is a normal, supported state.

Keep `reviewer-roles.md` current: add a row when someone new starts reviewing (confirm the login
with them), and re-check the dimension-to-label matrix if a repo's label set changes.

## Writing standard

Reviews follow the shared writing standard bundled under `skills/pr-feedback/references/`,
generated from `standards/` at the repo root by `bash scripts/sync-standards.sh`.

## Maintainer

Yale ITS Digital Experiences,
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)
