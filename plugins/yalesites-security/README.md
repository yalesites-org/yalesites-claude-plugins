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

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
