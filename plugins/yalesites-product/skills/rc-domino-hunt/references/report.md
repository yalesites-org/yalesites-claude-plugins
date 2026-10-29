# The morning report

The report decides whether any of this gets fixed. At Meta, about 70% of findings shown inside the developer's workflow got fixed, and close to 0% of findings sent as a batch list got fixed. So keep it short, ranked, and tied to the PR each finding most likely came from. Everything else stays in the run folder for anyone who wants it.

Write it to `runs/<run>/report.md`. In attended mode, show it in chat too. Follow the `michael-voice` rules: lead with the point, use "we", and no em dashes.

## Template

```markdown
# RC domino hunt: <branch>, <date>

<If stopped early with usage left: **Stopped with <n>% of weekly usage left: <reason>.** This line comes first, as a failure.>
<If a dry run: **Dry run against <branch>. This tests the skill, not the release.**>

**TL;DR:** <n> confirmed, <n> suspicious, from <n> charters on <n> sites. <One sentence on the worst finding.>

## Confirmed

### 1. <What breaks, in plain words>

- **Where:** <RC URL> (live: <live URL>)
- **Likely from:** yalesites-org/yalesites-project#<N> (<how sure, and why>)
- **Blast radius:** <n> live sites use <surface>
- **Repro:** <numbered steps a person can follow>
- **Evidence:** `screenshots/<NN>/<file>` (RC) beside `screenshots/<NN>/<file>` (live). Failed again on re-run.

<at most ~10 confirmed, ranked by confidence × blast radius>

## Suspicious

<one line each: what, where, why not confirmed>

## Coverage

- Charters: <n> run, <n> clean, <n> blocked. Hypotheses still open: <n>.
- Sites used: <list>. Not live clones: <list>.
- Not covered: <the biggest gaps from the debriefs>
- Blocked, waiting on a team decision: <count by reason, e.g. "4 need role users">

## Leftovers

<Every Layout Builder draft or other change a human needs to clear, with its URL. Or "None.">

## Log

Usage at start and end, run start and end time, release branch head SHA.
```

## Ranking

Confidence:

| Level | Meaning |
|---|---|
| High | Failed twice, differs from live, and the cause traces to a PR in the RC |
| Medium | Failed twice and differs from live, but the cause is not traced |
| Low | Goes in Suspicious, not Confirmed |

Order the Confirmed list by confidence, then blast radius. If there are more than 10, keep the rest in `runs/<run>/more-findings.md` and say how many there are.

## Rules

- **Coverage is part of the result.** A night with no findings and low coverage is a gap, not a pass. Say so.
- **No GitHub.** Do not post the report or any finding anywhere. In attended mode, offer the `ticket` skill for each confirmed finding. Never create a ticket without the user's yes.
- **Real-site screenshots stay local**, or go to private repos through `github-screenshots`. Never to a public repo.
- **Update `hypotheses.json`** with each result before writing the report, so the next run starts from the open ones.

## Measuring the routine

Append one line per run to `~/.claude/yalesites/rc-domino-hunt/ledger.md`:

```
| <date> | <branch> | charters | confirmed | suspicious | tickets made | triage minutes (filled in later) |
```

After each release ships, for every hotfix in that release window, add whether the hunt was in a position to catch it (did a charter cover that surface?) and whether it did. The baseline from the lookback is 13 release-caused hotfixes in 12 months, about 3 per feature release (`hotfix-lookback.md`).
