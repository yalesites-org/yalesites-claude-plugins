# YaleSites Claude Plugins

A Claude Code plugin marketplace for the Yale ITS Digital Experiences team.

> **Important:** Review a plugin before installing. The YaleSites core team
> reviews all plugins in `/plugins/`. Plugins can include MCP servers, skills,
> and other executable components. Only install plugins you trust.

## Which plugins do I install?

Pick the row that sounds like you. Each plugin you install adds its skill descriptions to
every Claude session, so install only what you use.

| You are... | Install | You get |
|---|---|---|
| **Reporting bugs and requests** | `yalesites`, `yalesites-ticket` | Well-formed tickets, screenshots on tickets, guided setup |
| **A developer** | `yalesites`, `yalesites-dev` (add `yalesites-security` for dependency audits) | Commits, PRs, issue lookups, Drupal conventions, PHPUnit |
| **A reviewer** | `yalesites`, `yalesites-ticket`, `yalesites-review` | PR review on the multidev or Storybook, reviewer scoping, keeping tickets in sync |
| **On the migration project** | `yalesites`, `yalesites-migration` | Read-only migration assessment of a source site |
| **Testing Beacon** | `yalesites-beacon` (add `yalesites` for platform context) | Question sets, tiered test banks, A/B comparison reviews |

New to Claude Code and the terminal? Install `yalesites-ticket`, then run `/yalesites-ticket:onboard`
and Claude walks you through setup. A plain-language guide is in
[plugins/yalesites-ticket/skills/onboard/README.md](plugins/yalesites-ticket/skills/onboard/README.md).

### Install commands

Register this marketplace once per machine, then install the plugins for your role. For someone
who reports bugs:

```
/plugin marketplace add yalesites-org/yalesites-claude-plugins
/plugin install yalesites@yalesites-claude-plugins
/plugin install yalesites-ticket@yalesites-claude-plugins
```

For other roles, swap in `yalesites-dev`, `yalesites-review`, `yalesites-migration`,
`yalesites-beacon`, or `yalesites-security` as your row says. `/plugin discover` lists everything.
After installing, run `/reload-plugins` or start a new session.

### What each plugin assumes

| Plugin | Skills | Assumes |
|---|---|---|
| [yalesites](plugins/yalesites/) | `yalesites`, `yalesites-portfolio` | Nothing. Core platform knowledge for everyone. |
| [yalesites-ticket](plugins/yalesites-ticket/) | `ticket`, `github-screenshots`, `ux-research`, `onboard` | Nothing. Works better with `yalesites`. |
| [yalesites-review](plugins/yalesites-review/) | `pr-feedback`, `pr-brief`, `reviewer-profile`, `ticket-sync` | `yalesites-ticket` |
| [yalesites-dev](plugins/yalesites-dev/) | `yalesites-pr`, `commit-conventional`, `cross-repo`, `issue-lookup`, `issue-plan`, `pr-description`, `drupal-conventions`, `phpunit-drupal` | Nothing. `yalesites-pr` also runs `ticket-sync` if `yalesites-review` is installed. |
| [yalesites-migration](plugins/yalesites-migration/) | `migration-assessment` | Works better with `yalesites`. |
| [yalesites-beacon](plugins/yalesites-beacon/) | `beacon-question-set`, `beacon-test-bank`, `beacon-comparison-review` | Nothing. |
| [yalesites-security](plugins/yalesites-security/) | `supply-chain-audit` | Nothing. |

### Coming from `yalesites-product`

`yalesites-product` was split up and removed from this marketplace. Uninstall it, then install the
plugins for your role:

```
/plugin uninstall yalesites-product@yalesites-claude-plugins
```

Skill names did not change, but the plugin prefix did. For example, `/yalesites-product:ticket` is
now `/yalesites-ticket:ticket`, and `/yalesites-product:pr-feedback` is now
`/yalesites-review:pr-feedback`. Release prep, the router, backlog hygiene, the RC domino hunt,
feature planning, and the docs and design-pass skills are no longer team plugins.

## Structure

- **`/plugins`** — Core team-maintained plugins, reviewed by
  `@yalesites-org/claude-core-team` before merge
- **`/external_plugins`** — Community plugins (not yet open for submissions)

## Shared writing standards

`/standards` holds the canonical writing rules every skill that posts to GitHub follows:

| File | Governs |
|---|---|
| `github-communication-format.md` | Structure: what is visible, what collapses into `<details>`, what goes in the invisible `<!-- yalesites:agent -->` machine block |
| `github-writing.md` | Words: ASD-STE100 sentence rules, plain-language word swaps, and a visible-layer word budget per surface |
| `check-github-text.py` | Mechanical check of a draft against both |

Claude Code plugins cannot read each other's files, so each consuming plugin carries its
own copy under its host skill's `references/` and `scripts/`. **Those copies are
generated. Do not edit them.** Edit `/standards`, then:

```bash
bash scripts/sync-standards.sh
```

`scripts/validate-plugins.sh` (and therefore CI) fails if any copy has drifted.

## Posting screenshots

`gh` can't upload images to GitHub, so `yalesites-ticket` has a `github-screenshots` skill.
It commits the image to the `screenshots` branch of `yalesites-org/YaleSites-Internal` and prints
an `<img>` tag for the comment.

The image only shows for people with access to YaleSites-Internal (every org member). That makes
it work on YaleSites-Internal tickets, but not in public repos, including this one, so the script
refuses public targets. Details are in `plugins/yalesites-ticket/skills/github-screenshots/SKILL.md`.

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the plugin contract,
versioning convention, and submission process.

## License

See individual plugin directories for license information.
