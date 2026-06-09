# Supply Chain Audit Report Template

Use this structure in Phase 6. Lead with the most urgent findings.

```
## Supply Chain Audit Report
**Scanned:** [list what was scanned]
**Date:** [today's date]

### CRITICAL — Active Supply Chain Compromise
[Only if a known-compromised version is installed]
- Package: X  Version: Y  Issue: Z  Action: [upgrade to version / remove]

### PHP / Composer Findings
[Group by ecosystem]
- Unpatched advisories being ignored: ...
- Packages needing updates: ...

### JavaScript / npm Findings
**Production dependencies:** ...
**Dev/build tooling (lower priority):** ...

### CDN/External Script Findings
[Any polyfill.io or similar references found]

### Globally Installed Tools
[Any issues with global installs]

### No Issues Found
[List the ecosystems/packages checked that came back clean]

### Recommended Next Steps
1. [Most urgent action] — command to fix it
2. [Second action] — command
...

### Staying Current
Supply chain attacks happen continuously. For ongoing monitoring, consider:
- socket.dev — specializes in supply chain detection (free tier available)
- OSV.dev — search any package for known supply chain events
- GitHub's Dependabot — automated PRs for dependency updates
```
