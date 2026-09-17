# yalesites-security

Security tooling for YaleSites projects. A home for the team's security-focused
Claude Code skills — currently dependency supply-chain auditing.

## Skills

### supply-chain-audit

Audit a project for **supply-chain attacks** — packages with deliberately injected
malicious code — as distinct from ordinary CVEs. A six-phase audit:

1. Determine scope (detect ecosystems from manifest/lock files).
2. Run native audit tools (`npm audit`, `composer audit`, `pip audit`, `cargo audit`, …).
3. Cross-check the installed inventory against **live** advisory sources scoped to what
   you actually have: the OSV.dev batch API (malicious-package `MAL-` advisories) and
   GitHub's malware advisories (`/advisories?type=malware`). A small bundled seed list of
   marquee incidents (xz-utils, event-stream, …) gives a fast first pass.
4. Scan for compromised CDN / external script references.
5. Flag typosquatting risk.
6. Write a report that keeps supply-chain attacks and regular CVEs clearly separated.

The skill's logic is **general-purpose** — it works on any codebase, not just YaleSites.

## Installation

```
/plugin install yalesites-security@yalesites-claude-plugins
```

## Requirements

- `gh` CLI (authenticated) for GitHub malware advisories
- `curl` for the OSV.dev API (no authentication required)
- The relevant ecosystem tooling for native audits (`npm`, `composer`, `pip`, etc.)

## Writing standard

When an audit report is posted to GitHub, it follows the shared YaleSites GitHub writing
standard, bundled as `skills/supply-chain-audit/references/github-writing.md` and
`github-communication-format.md`: an 80-word TL;DR, findings that need action visible and
ordered by severity, package-by-package evidence in `<details>` blocks, and structured
finding records in a closing `<!-- yalesites:agent -->` block.

```bash
python3 skills/supply-chain-audit/scripts/check-github-text.py report.md --surface report
```

Both reference files and the script are generated from `standards/` at the repo root.
Edit the canonical copies there, then run `bash scripts/sync-standards.sh`.

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
