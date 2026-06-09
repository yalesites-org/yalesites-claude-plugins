# Known Supply Chain Compromised Packages

This is a curated reference of packages that were confirmed to have malicious code injected — not just CVEs, but actual supply chain attacks where an attacker or rogue maintainer introduced malicious functionality.

## How to use this list

For each entry: check if the package is installed AND whether the installed version matches the compromised range. If both are true, flag it as **HIGH PRIORITY** — this is an actual supply chain compromise, not a theoretical vulnerability.

---

## npm Packages

| Package | Compromised versions | Attack type | Year | Notes |
|---|---|---|---|---|
| `coa` | 2.0.3, 3.0.1 | Account takeover | 2021 | Installs password-stealing malware |
| `rc` | 1.2.9, 1.3.1, 2.3.1, 2.3.2 | Account takeover | 2021 | Same campaign as `coa` |
| `ua-parser-js` | 0.7.29, 0.8.0, 1.0.0 | Account takeover | 2021 | Cryptominer + password stealer |
| `event-stream` | 3.3.6 | Social engineering of maintainer | 2018 | Targeted Bitcoin wallet theft |
| `flatmap-stream` | 0.1.1 | Nested malicious dependency | 2018 | Injected via `event-stream` |
| `eslint-scope` | 3.7.2 | Account takeover | 2018 | Stole npm credentials from CI |
| `node-ipc` | 10.1.1, 10.1.2, 10.1.3 | Rogue maintainer | 2022 | Destructive anti-Russia code (deleted files) |
| `colors` | 1.4.44-liberty-2 | Maintainer protest | 2022 | Infinite loop, broke dependents |
| `faker` | 6.6.6 | Maintainer protest | 2022 | Same maintainer as `colors` |
| `everything` | any | Malicious typosquat | 2023 | Depends on the entire npm registry — causes massive install |
| `@solana/web3.js` | 1.95.6, 1.95.7 | Account takeover | 2024 | Exfiltrated private keys |
| `lottie-player` | 2.0.8 (specific window) | Supply chain via dep | 2024 | DOM-based crypto drainer via compromised dep |

## PyPI Packages (Python)

| Package | Notes | Year |
|---|---|---|
| `ctx` | Malicious version published after PyPI account compromise | 2022 |
| `codecov` (bash uploader) | CI script compromise, not PyPI itself | 2021 |
| `pytorch-nightly` (via pip) | Dependency confusion attack targeting Meta | 2022 |
| `aiocpa` | Infostealer hidden in legitimate-looking crypto library | 2024 |

## RubyGems

| Package | Notes | Year |
|---|---|---|
| `bootstrap-sass` | 3.2.0.3 contained backdoor for remote code execution | 2019 |
| `rest-client` | 1.6.10–1.6.13, 1.7.3 — account takeover, credential stealer | 2019 |

## System / Infrastructure

| Package / Tool | Compromised scope | Attack type | Year | Notes |
|---|---|---|---|---|
| `xz-utils` / `liblzma` | 5.6.0, 5.6.1 | Sophisticated long-term infiltration | 2024 | SSH backdoor on systemd-linked distros |
| SolarWinds Orion | Build pipeline | Nation-state supply chain | 2020 | Not a package manager issue |
| 3CX Desktop App | Build pipeline | Trojanized installer | 2023 | Windows & macOS |

## CDN / External Script Compromises

These are external services that were compromised and should NOT be referenced in any codebase:

| Service | Status | Notes |
|---|---|---|
| `polyfill.io` | **AVOID** — domain sold to malicious operator | Injects crypto drainers; domain sold Feb 2024 |
| `cdn.polyfill.io` | **AVOID** | Same domain |
| `bootcss.com` | **AVOID** | Hosted malicious polyfill.io mirrors |
| `bootcdn.net` | **Monitor** | Same operator as bootcss.com |
| Codecov bash uploader URL | Replaced | Patch was introduced via CI URL, not package |

## Typosquatting — Watch For These Patterns

Supply chain attackers frequently publish packages with names that look like popular ones:
- Adding/removing a hyphen: `lodash` vs `lo-dash`, `node-events` vs `nodeevents`
- Subtle misspellings: `crossenv` (for `cross-env`), `mongose` (for `mongoose`)
- Scoped package spoofing: a public `yalesites-org__component-library-twig` when `@yalesites-org/component-library-twig` is private
- Dependency confusion: publishing a public package with the same name as a private internal one

## Keeping This List Current

This list has a knowledge cutoff. For the most current intelligence:
- **OSV.dev** (osv.dev) — open source vulnerability database, includes supply chain events
- **GitHub Advisory Database** (github.com/advisories) — searchable, includes malicious packages
- **Snyk Vulnerability DB** — commercial but has good coverage
- **Socket.dev** — specializes in supply chain specifically (not just CVEs)
- **npm security advisories** — npmjs.com/advisories
