# Hotfix lookback, Oct 2025 to Oct 2026

Where real release bugs came from, and which part of this skill would catch each one. Use it to calibrate Phase 2 and to measure the routine. Extend it after each release.

**Counts:** 17 patch releases (v2.17.1 to v2.31.1). About 17 of the fixes in them were security, composer, or CI changes, which are out of scope. That leaves 23 functional bug hotfixes. 13 of them were caused by a release. Of those 13, the hunt would likely catch 6, maybe 4, and unlikely 3.

## Caused by a release

| Bug | Ticket and fix | Caused by | What would catch it | Verdict |
|---|---|---|---|---|
| Action Banner CTAs misaligned | yalesites-org/YaleSites-Internal#1051, yalesites-org/component-library-twig#600 | yalesites-org/yalesites-project#1113, yalesites-org/yalesites-project#1068 | Impact map (shared button and padding code), pairwise theme × block | Likely |
| Existing blocks demand new padding and button values on save | yalesites-org/YaleSites-Internal#1052, yalesites-org/yalesites-project#1163 | yalesites-org/yalesites-project#1068, yalesites-org/yalesites-project#1113 | Old-data queries plus Layout Builder discard. The PR steps only tested new blocks. | Maybe |
| Update hooks time out on sites with many blocks | yalesites-org/yalesites-project#1168 | yalesites-org/yalesites-project#1163, itself a hotfix | `drush deploy` on real clones, but the hotfix skipped the RC. `--hotfix` mode exists for this. | Unlikely |
| Calendar include and exclude filters do nothing | yalesites-org/YaleSites-Internal#1053, yalesites-org/yalesites-project#1165 | yalesites-org/yalesites-project#1031 | Gap analysis: the filter step on the PR was left unchecked | Likely |
| AI chatbot markdown mangled | yalesites-org/yalesites-project#1173 | yalesites-org/yalesites-project#1095 | Real content (ys-chat-finance is an RC site). No chatbot generator. | Maybe |
| Apply button on calendars with no filters | yalesites-org/YaleSites-Internal#1136, yalesites-org/yalesites-project#1228 | yalesites-org/yalesites-project#1186 | Gap analysis (no "no filters" step), standing calendar hypothesis | Likely |
| Multi-day all-day events have no date separator | yalesites-org/YaleSites-Internal#1374, yalesites-org/component-library-twig#666 | CLT date-time work for yalesites-org/YaleSites-Internal#1222 (medium confidence) | Date boundary generator on real Localist events | Likely |
| Dashboard lists each editor once per role | yalesites-org/YaleSites-Internal#1732, yalesites-org/yalesites-project#1564 | yalesites-org/yalesites-project#1288 | Real user data on clones, read as user 1 | Likely |
| Link Grid heading white-on-white | yalesites-org/YaleSites-Internal#1734, yalesites-org/component-library-twig#738 | yalesites-org/component-library-twig#714 | Section color contrast standing check, pairwise | Likely |
| gsa.yale.edu forms cannot send | yalesites-org/YaleSites-Internal#1735, yalesites-org/yalesites-project#1571 | the yalesites-org/YaleSites-Internal#1669 validation change | Fleet config scan only. gsa is not an RC site. | Unlikely |
| Media library Apply filters gives Access denied in Layout Builder | yalesites-org/YaleSites-Internal#1791, yalesites-org/yalesites-project#1586 | yalesites-org/yalesites-project#1017 (gin_lb 2.0) plus yalesites-org/yalesites-project#1300 (core patch revision) | Vendor diff plus overlap, but only fails for real roles. Blocked until role users are allowed. | Maybe |
| PHP warning on every Configure Section | yalesites-org/YaleSites-Internal#1824 | yalesites-org/yalesites-project#1174 | Log diff | Unlikely before, likely now |
| Calendar month navigation and Apply drop the parent-term filter | yalesites-org/YaleSites-Internal#1847, yalesites-org/yalesites-project#1605 | yalesites-org/yalesites-project#1031, left uncovered by yalesites-org/yalesites-project#1186 | Standing calendar hypothesis, needs a calendar with a parent term | Maybe |

## Not caused by a release, but worth knowing

- **Content-specific:** a long URL in Teaser Text breaks card grids (yalesites-org/YaleSites-Internal#1729), and an EXIF-rotated photo blows out a card in Safari (yalesites-org/YaleSites-Internal#1730). Content extremes and WebKit generators.
- **Already there before a release:** recurring-event overflow around month ends (yalesites-org/YaleSites-Internal#1379), and reusable Grand Hero failing validation (yalesites-org/YaleSites-Internal#1381). Date boundary and reusable-vs-inline generators.
- **External:** Campus Groups fatal from a floating migrate_plus (yalesites-org/YaleSites-Internal#1394), Twig 3.30 500s (yalesites-org/YaleSites-Internal#1805), gin_lb accordion white screen (yalesites-org/YaleSites-Internal#1950), and CAS username case from externalauth (yalesites-org/YaleSites-Internal#1775). Vendor diff and log diff.

## Patterns

1. **The events calendar is our most-hotfixed surface.** Three hotfixes trace back to one feature PR and its follow-ups. Each was a filter or navigation combination the steps skipped.
2. **New validation landing on old data** (yalesites-org/YaleSites-Internal#1052, yalesites-org/YaleSites-Internal#1735).
3. **Section color and contrast** (yalesites-org/YaleSites-Internal#1734, yalesites-org/YaleSites-Internal#1051).
4. **Contrib and patch bumps in Layout Builder and Views AJAX** (yalesites-org/YaleSites-Internal#1791, yalesites-org/YaleSites-Internal#1950, yalesites-org/YaleSites-Internal#1394). No `composer.lock` means the repo diff cannot see them.
5. **Silent failures** that show only in logs or cron (yalesites-org/YaleSites-Internal#1824, yalesites-org/YaleSites-Internal#1394).
6. **Hotfixes skip the RC**, and one hotfix caused the next.
