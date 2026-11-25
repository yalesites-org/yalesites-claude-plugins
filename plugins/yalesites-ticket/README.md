# yalesites-ticket

Report YaleSites bugs and requests as well-formed GitHub issues, and groom tickets, features, and
epics. This plugin works on its own. It works better with the core `yalesites` plugin, which the
`ticket` skill uses to check whether an idea already exists on the platform.

## Who it's for

Anyone who reports bugs or asks for features. Reviewers install it too, because `yalesites-review`
assumes it is present.

## New to this? Start here

If you have never used a terminal, type each line into Claude Code and press Return:

```
/plugin marketplace add yalesites-org/yalesites-claude-plugins
/plugin install yalesites-ticket@yalesites-claude-plugins
/yalesites-ticket:onboard
```

Claude checks your Mac or Windows computer, installs what is missing, and tells you the few steps
only you can do. It is safe to run again any time. The step-by-step guide is in
[skills/onboard/README.md](skills/onboard/README.md). It does not set up a developer machine.

## Installation

```
/plugin install yalesites@yalesites-claude-plugins
/plugin install yalesites-ticket@yalesites-claude-plugins
```

## Skills

| Skill | Use it for |
|---|---|
| `ticket` | Reporting a bug or request, grooming an existing ticket, or scoping a feature or epic (invoke directly with `/ticket`) |
| `github-screenshots` | Putting a screenshot on a YaleSites-Internal ticket or comment, since `gh` can't upload images |
| `ux-research` | The six user archetypes, top pain points, and usage data from the 2026 YaleSites UX Report |
| `onboard` | Setting up a Mac or Windows computer so the ticket skill works (`/yalesites-ticket:onboard`) |

## Writing standard

Tickets follow the shared YaleSites GitHub writing standard, bundled as
`skills/ticket/references/github-writing.md` (words) and `github-communication-format.md`
(structure). Check a draft before posting:

```bash
python3 skills/ticket/scripts/check-github-text.py draft.md --surface ticket
```

These files are generated from `standards/` at the repo root. Edit the canonical copies there,
then run `bash scripts/sync-standards.sh`.

## Maintainer

Yale ITS Digital Experiences,
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)
