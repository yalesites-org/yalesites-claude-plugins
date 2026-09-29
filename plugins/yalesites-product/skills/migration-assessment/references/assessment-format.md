# The shape of the assessment output

The structure every migration assessment this skill produces must follow. Fill
every section; where something could not be determined, say so rather than
omitting it — a missing section reads as "nothing to report."

Lead with constraints and unknowns. An assessment that opens with a tidy summary
gets read as approval.

````markdown
# Migration assessment — <site name> (<url>)

**Assessed:** <date> · **Method:** read-only public probe (`probe_site.py`) + manual page review
**Source platform:** <CMS + major version, with the evidence>

## Read this first

- **Overall complexity:** <low | medium | high>, driven mainly by <volume | structural fit | rebuild burden>
- **Blocking questions:** <decisions that must be made before any work starts, or "none">
- **Hard stops:** <anything with no YaleSites target at all — translations, role-based access, custom form building — or "none">
- **Counted vs estimated:** <state it plainly, e.g. "9 pages counted; ~60-70 events estimated from node-ID bounds">

## Source inventory

| Metric | Value | Counted or estimated |
|---|---|---|
| Source platform | | |
| Total pages | | |
| Content types in use | | |
| Top-level nav items / max depth | | |
| Media items | | |
| Documents (PDF etc.) | | |
| Native forms | | |
| Third-party scripts | | |

Sections: <path prefixes with counts>

## Content type mapping

| Source type | Count | YaleSites target | Field mapping | What is lost |
|---|---|---|---|---|
| | | | | |

**Body content:** <how much long-form HTML there is and what rebuilding it costs.
Always state that YaleSites content types have no body field and that
`basic_html` strips div / iframe / script / style / inline img.>

## Component mapping

| Source page pattern | YaleSites component | Notes |
|---|---|---|
| | | |

## Will not carry over cleanly

| Item | Why | Suggested handling | Decision needed from |
|---|---|---|---|
| | | | |

## Effort and complexity

| Driver | Rating | Basis |
|---|---|---|
| Volume | | |
| Structural fit | | |
| Rebuild burden | | |

**Overall:** <rating>. **Rough effort:** <band>, assuming <the assumption it rests on>.

## Migration mechanism — options, not a decision

| Content bucket | Suggested mechanism | Tradeoff |
|---|---|---|
| | | |

The mechanism decision is the lead developer's, informed by
yalesites-org/YaleSites-Internal#1561. This assessment does not make it.

## Could not determine

- <what, and why — behind a login, no sitemap, host blocked the path>

## Recommended next steps

1. <the decision or check that unblocks the most>
````
