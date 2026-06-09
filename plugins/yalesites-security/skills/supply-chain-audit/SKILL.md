---
name: supply-chain-audit
description: >
  Audit a project or system for supply chain attacks — packages with malicious code intentionally
  injected, not just regular CVEs. Use this skill whenever the user asks about supply chain
  security, whether their dependencies are safe or compromised, if a recent attack affects them,
  or asks to audit packages/dependencies for malicious code. Also use when the user mentions
  specific known attacks (polyfill.io, xz-utils, event-stream, etc.) and wants to know if they're
  affected. Triggers on: "supply chain", "compromised package", "malicious dependency",
  "are my packages safe", "dependency audit", "check my packages", "were we affected by X attack".
argument-hint: "[project-path (default: current directory)]"
---

# Supply Chain Audit Skill

Supply chain attacks are fundamentally different from ordinary security vulnerabilities. An attacker
intentionally injects malicious code into a package — through account takeover, social engineering
a maintainer, or publishing a typosquatting lookalike. The installed package appears legitimate
but actively harms users: stealing credentials, exfiltrating data, destroying files, or installing
cryptominers. Regular CVEs are bugs; supply chain attacks are sabotage.

This skill walks through a systematic audit covering: the current project's dependencies, globally
installed tools, external CDN/script references, and a cross-check against **live** supply-chain
advisory sources (OSV.dev and GitHub's malware advisories), scoped to what is actually installed.

---

## Phase 1: Determine scope

First, establish what to scan.

**Check for a project directory:**
Look for package manager manifest files in the current working directory (and one level up if
needed). Presence of these files determines which ecosystems to scan:

| File | Ecosystem | Audit command |
|---|---|---|
| `package.json` | Node.js / npm | `npm audit --json` |
| `yarn.lock` (with `package.json`) | Yarn | `yarn audit --json` |
| `pnpm-lock.yaml` | pnpm | `pnpm audit --json` |
| `composer.json` | PHP / Composer | `composer audit` |
| `requirements.txt` or `Pipfile` or `pyproject.toml` | Python | `pip audit` or `safety check` |
| `Cargo.toml` | Rust | `cargo audit` |
| `Gemfile` | Ruby | `bundle audit check` |
| `go.mod` | Go | `govulncheck ./...` |

**If no project manifests are found** (or the user explicitly asks for a global scan), check:
- `npm list -g --depth=0 --json` — globally installed Node packages
- `pip list` / `pip3 list` — globally installed Python packages
- `brew list --versions` — Homebrew packages (macOS)
- `gem list` — globally installed Ruby gems
- `cargo install --list` — globally installed Rust binaries
- Check system xz/liblzma version if on Linux: `xz --version`

Announce what you found before proceeding: "Found package.json and composer.json — scanning
Node.js and PHP dependencies."

---

## Phase 2: Run the audit tools

Run all applicable audit commands. These tools check against live advisory databases and catch
known CVEs and some supply chain events.

Important notes on interpreting results:
- Most findings from `npm audit` are **regular CVEs in devDependencies** — they affect your build
  tooling, not production users. Note this distinction clearly in your report.
- A "critical" npm finding in a devDependency (e.g., a Storybook tool) is far less urgent than a
  "moderate" finding in a package that ships to end users.
- `composer audit` may show "ignored" advisories — review what's being ignored and why.

Run all applicable tools in parallel where possible to save time.

---

## Phase 3: Cross-check against live supply-chain advisories

Supply-chain attacks surface constantly, so this check queries **live advisory sources at scan
time**, scoped to the ecosystems and exact package versions found in Phase 1. The bundled
`references/known-compromised.md` is only a fast-path **seed** of marquee incidents (xz-utils,
event-stream, …) — the live sources below are authoritative. Skim the seed first to catch the
famous cases quickly, then run the live queries for everything current.

### 3a. Build the installed-package inventory

Lockfiles are the source of truth for exact installed versions. For each detected ecosystem:
- npm: `npm ls --all --json` (or parse `package-lock.json`)
- Composer: parse `composer.lock` — `jq '.packages[] | {name, version}'`
- Python: `pip freeze`, or parse `poetry.lock` / `Pipfile.lock`
- Cargo: parse `Cargo.lock`; Go: `go list -m all`; Ruby: parse `Gemfile.lock`

### 3b. Query OSV.dev (all ecosystems, no auth)

OSV aggregates malicious-package advisories (IDs prefixed `MAL-`) alongside regular CVEs, so it is
the broadest live source. Batch-query the inventory:

1. Build `queries.json`:
   `{"queries":[{"package":{"name":"<name>","ecosystem":"npm"},"version":"<version>"}, ...]}`
   OSV ecosystem names: `npm`, `PyPI`, `Packagist`, `crates.io`, `Go`, `RubyGems`.
2. `curl -sS -X POST -d @queries.json https://api.osv.dev/v1/querybatch`
3. For any package with results, pull details with `curl -sS https://api.osv.dev/v1/vulns/<ID>`.
   **Supply-chain hits** = advisory IDs starting with `MAL-`, or advisories whose details mark them
   as malware. Regular CVEs belong in the normal-vulnerability section of the report, not the
   supply-chain section — keep the distinction sharp.

### 3c. Cross-check GitHub's malware advisories (scoped)

GitHub classifies deliberately-malicious packages separately from CVEs (`type=malware`). For each
detected ecosystem:

```bash
gh api "/advisories?type=malware&ecosystem=<ecosystem>&per_page=100" --paginate \
  --jq '.[] | {ghsa: .ghsa_id, summary: .summary, pkgs: [.vulnerabilities[].package.name]}'
```

GitHub ecosystem names: `npm`, `pip`, `composer`, `rust`, `go`, `rubygems`, `maven`, `nuget`.
Cross-reference the returned package names against your inventory — any match is a **HIGH PRIORITY
supply-chain hit**; confirm the installed version falls within the advisory's affected range.

### 3d. Confirm exact installed versions for any hit

- npm: `cat node_modules/<pkg>/package.json | grep '"version"'`
- Composer: `composer show <pkg>`; pip: `pip show <pkg>`

A match on name **and** affected version = confirmed hit. Name matches but the installed version is
outside the affected range = note as "present, version not affected" (so the user sees why you
checked).

---

## Phase 4: Check for CDN and external script references

Scan the codebase for references to known-compromised external services. These are dangerous even
if your package dependencies are clean — a compromised CDN injects malicious scripts into every
page that loads from it.

Search for these patterns in `.html`, `.twig`, `.php`, `.js`, `.ts`, `.vue`, `.jsx`, `.tsx` files:

```
grep -r "polyfill.io\|cdn.polyfill.io\|polyfill\.com\|bootcss\.com\|bootcdn\.net" .
```

Also look for any `<script src="...">` or dynamically constructed script URLs that pull from
third-party domains you don't control. Note the files and line numbers if found.

---

## Phase 5: Check for typosquatting risk

This is harder to automate, but worth flagging. Look at the direct dependencies listed in
`package.json` / `composer.json` / etc. and check:
- Are any package names unexpectedly similar to popular packages? (e.g., `lodahs`, `expres`)
- Are there unscoped packages that should be scoped? (e.g., `yalesites-component-library` when
  the real package is `@yalesites-org/component-library-twig`)
- Are there packages you don't recognize in direct dependencies?

Flag any that look suspicious for the user to verify.

---

## Phase 6: Write the report

Read `references/report-template.md` for the full report structure. Lead with the most urgent findings. Keep the report honest about supply chain attacks vs regular CVEs — conflating them dilutes urgency. If everything is clean, say so clearly.

---

## Important context to communicate

If the user seems unfamiliar with the distinction, briefly explain: supply chain attacks are when
someone deliberately puts malicious code into a package that gets distributed to everyone who
installs it. It's different from a regular security bug — it's intentional sabotage. The `xz-utils`
attack (2024) is a good real-world example: a contributor spent two years gaining trust before
hiding a backdoor in a widely-used compression library.

Attackers move fast and the bundled seed list can't update in real time — that's why Phase 3
queries OSV.dev and GitHub's malware advisories live. For anything ambiguous, socket.dev is a good
additional source to recommend to the user.
