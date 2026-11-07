# Decision record

The output of a planning session. Write it to `<scratchpad>/feature-planning/<slug>/decision-record.md`,
show the short form in chat, and hand the file to the `ticket` skill. It follows the GitHub writing
standard (`../../ticket/references/github-writing.md`), since most of it lands in the ticket.

Every decision carries where it came from: the board answer, a chat answer, or "settled by
research" with the evidence. A decision with no source is a guess, and a guess is an open item.

## Template

```markdown
# Feature plan: <name>

**TL;DR:** <one sentence: what we are building, for whom, and when>

Planned <YYYY-MM-DD> by <handle>. Research: research.md in this folder.

## The problem
<Two or three sentences in the requester's terms. Who asked, and how many.>

## Decisions
| # | Decision | Why | Source |
|---|---|---|---|
| 1 | Sitewide setting, not a per-block option | Every site that asked wants it everywhere; a block option would need 140 sites to opt in one block at a time | Board, question 1 |
| 2 | Off by default for existing sites | 140 sites use the block today (2026-10 crawl); a default change would reach all of them on deploy | Board, question 2 |
| 3 | No new permission | Site admins already have the settings page | Settled by research: `user.role.site_admin.yml` |

## Out of scope
- <What the plan explicitly does not promise, and where it would go if we do it later>

## Open items
| Item | Owner | By | Becomes |
|---|---|---|---|
| Config entity or a field on the existing settings form? | `dblanken-yale` | <date> | `needs-decision` on the dev phase |
| Confirm the wording with April | `atiddei` | <date> | `follow-up` on the UX phase |

## Blast radius
- Sites affected on deploy with no action: <n> of <total> (<crawl vintage>)
- Sites that can use it: <n>
- Repos: <list>

## Interaction map
| Area | Status | Note |
|---|---|---|
| Layout Builder vs Manage Settings | Touched | Lives in sitewide settings |
| Themes and palettes | Unknown | Contrast in Theme Four not checked; open item |
(one row per checklist area, from interaction-checklist.md; leave out the not-touched rows)

## What others do
- **Tier 1:** <school, what they built, link, date>
- **Tier 2/3:** <only what shaped a decision>

## Phases
<Phases that apply, with owners, from routing.md. "Small enhancement, single ticket" if so.>

## Timeline
Target: <milestone>. Why: <phases, repo count, hard dates>. Depends on: <anything the lead
developer has to confirm>.

## Risks
- <What could go wrong, and what we would watch for>

## How we'll know it worked
- <The measure from the session>
```

## Short form for chat

Five to eight lines: the TL;DR, the three decisions with the most reach, the open items with
owners, and the target release. Link the file for the rest.
