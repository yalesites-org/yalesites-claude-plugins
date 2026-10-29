---
name: rc-domino-hunt
description: "Hunt a YaleSites release candidate for the edge cases and domino effects that PR-level testing never looked at: cross-PR collisions, shared component, token, and contrib-patch changes rippling into blocks nobody tested, new validation landing on old real content, and filter, theme, color, and layout combinations next to the ones a PR tested. Tests read-only on the RC multidevs, which are cloned from real sites, and ends with a short morning report a human triages. Never posts to GitHub. Use when someone asks to hunt, stress, poke at, or look for dominoes or blast radius in the RC, e.g. '/rc-domino-hunt', 'hunt the RC for an hour', 'what could 1666 and 1672 break together', 'check the RC for things PR testing missed', 'mini-hunt this hotfix PR before it ships'. Also the skill the Tuesday-night drain routine calls with --drain during an RC window. Not for reviewing a single PR (that is pr-feedback) or for retesting a ticket's own Release Testing Steps (that is release-prep)."
argument-hint: "[--drain] [--dry-run <release-branch>] [PR numbers] [--site <site>] [--budget <time>] [--hotfix <PR>]"
---

# RC domino hunt

PR testing proves each change works where its developer aimed it. This skill looks everywhere else. It maps what the release candidate (RC) actually touched, works out what each PR's testing steps would **not** have caught, and then explores the RC multidevs, which are copies of real sites, until it finds the dominoes or runs out of budget.

Why it exists: a lookback over Oct 2025 to Oct 2026 found 23 functional hotfixes. 13 were caused by a release, and this method would likely have caught 6 of them and maybe 4 more. The case list is in `references/hotfix-lookback.md`. Read it once per run: it is the best guide to where bugs really come from on this platform.

**Ground rules, in every mode:**

- **Read-only on the RC.** The RC multidevs are the team's shared QA environment. The `yalesites-web-content` skill already says to create nothing there. This skill follows that. The only allowed change is opening a Layout Builder form on an existing page and then discarding it, under the rules in `references/rc-sites.md`.
- **Nothing outbound.** No form submissions, no webform sends, and no writes to Localist, ServiceNow, or CAS.
- **Nothing to GitHub.** No comments, reviews, labels, or issues. Findings go into the morning report. A human triages them, and real bugs go through the `ticket` skill.
- **Screenshots of real sites stay local.** Only use them on private repos, through `github-screenshots`.
- **Evidence or it did not happen.** Every finding needs a screenshot of the RC beside the same view on live, repro steps, and one re-run that fails again (see `references/charters.md`).

## Modes

| Call | What it does |
|---|---|
| `/rc-domino-hunt` | Full hunt on the open RC, attended. Runs phases 1 to 3 and asks before anything that needs a ruling. |
| `/rc-domino-hunt 1666 1672` | Scoped to those PRs and their overlaps. The impact map is still built for the whole RC, since overlaps need it. |
| `--site <site>` | Only that RC site, e.g. `--site ys-registrar-yale-edu`. |
| `--budget 1h` | Stop after that much time, then report. |
| `--hotfix <PR>` | Mini-hunt on a hotfix PR before it ships. Hotfixes skip the RC, and one hotfix has caused the next before (see the lookback). Phases 1 and 2 run for that one PR, and the state folder is `hotfix-<N>/`. Phase 3 runs on the PR's `pr-<N>` multidev under `pr-feedback`'s rules for that environment, not on RC sites. That multidev is a copy of the visreg site, not real content, so it cannot show problems that need real data or scale (like update hooks timing out on big sites). The report says so, and lists the old-data queries a human could run on one RC site. Never in `--drain`. |
| `--dry-run <branch>` | Run against an old release branch whose multidevs still exist (e.g. `v2260`). It tests the skill, not the release: say so at the top of the report. |
| `--drain` | Unattended and open-ended. This is what the Tuesday routine calls. It asks nothing, skips anything that needs a ruling, and keeps going until the stop rules in "Drain mode" below fire. |

## Workflow

1. Find the RC and its sites, then preflight (`references/rc-sites.md`)
2. Phase 1: build or refresh the impact map (`references/impact-map.md`)
3. Phase 2: test plan gap analysis, then rank the hypotheses (`references/gap-analysis.md`)
4. Phase 3: run charters, one subagent each, plus the standing checks (`references/charters.md`)
5. Write the morning report (`references/report.md`)

Phases 1 and 2 run once per RC and are saved. Later runs reuse them, and only refresh when the release branch has moved (compare the head SHA saved in `impact-map.json`) or when new PRs were merged into it.

## State

Everything for one RC lives in one folder, so a fresh session can pick up where the last one stopped:

```
~/.claude/yalesites/rc-domino-hunt/<release-branch>/
  release.json          release PR, head SHA, site list with clone sources, URLs
  impact-map.json       Phase 1
  vendor-diff.json      Phase 1, contrib and patch changes
  hypotheses.json       Phase 2, one entry per hypothesis with status
  runs/<YYYY-MM-DD-HHMM>/
    charters/<NN>-<slug>.md     the charter and its debrief
    screenshots/
    report.md
    leftovers.md        anything a human has to clear
```

A hypothesis status is `open`, `running`, `confirmed`, `suspicious`, `clean`, or `blocked` (with the reason). Write the status after every charter, not at the end. If a session dies, the next one continues from `hypotheses.json`. Each `running` entry also records `started` (ISO time). At the start of every run, set any `running` entry older than 2 hours back to `open`: its session died.

## Step 1: Find the RC and preflight

Follow `references/rc-sites.md`. In short:

- The open release PR is the one into `master` whose head is a `v<NNNN>` branch. Its head branch is the release branch, and the RC multidevs are named after it.
- The site list comes from the `RELEASE_SITES` repo variable. Read each entry's clone source from it. 23 entries clone `live`, but some clone `dev` or another multidev, and `yalesites-platform` is a fresh install. Record which is which in `release.json`, and flag non-live sites in the report.
- Confirm the multidevs exist with Terminus. Do not wait for the "Environments ready for review" comment: it only posts when a repo flag is reset, and that flag has been left stuck before.
- Preflight Terminus, the browser, and that the RC multidev runs the release branch's code, before anything else.

If there is no open release PR and no `--dry-run`, say so and stop. In `--drain`, exit quietly, so the routine's fallback drain list runs.

## Step 2: Impact map

Mechanical, not judgment. See `references/impact-map.md`. The output is a list of **changed surfaces**: blocks, templates, content types, settings, update hooks, and contrib modules. Each surface has the PRs that touched it, how it was reached (the trace), and how many live sites use it. Pairs of PRs that touch the same surface are **overlaps**. Changes to global tokens, theme-wide CSS, or shared Twig includes are **wide triggers**, which mark every block as touched.

## Step 3: Test plan gap analysis

See `references/gap-analysis.md`. For each PR, read its diff next to its testing steps and write down what a plausible unexpected breakage would look like that those steps would not catch. Every gap must be a concrete claim with a named oracle (what you would see if it is broken). Drop vague ones.

Add the standing hypotheses that every RC gets (calendar filter and navigation combinations, new validation on old data, contrast on every section color). Then rank everything by blast radius × overlap × severity.

## Step 4: Charters

See `references/charters.md`. Each hypothesis becomes a charter: "Explore *surface* on *sites* to find *what*", with a budget. Run each charter in its own subagent (Agent tool), passing the charter file path and the paths to `references/rc-sites.md` and `references/charters.md`. Run at most **two at a time**: the RC multidevs are small Pantheon containers shared with the team, and Playwright sessions must not collide. Name sessions `-s=c<NN>`.

Also run the standing checks once per site per run: log diff, old-data queries, and accessibility on changed surfaces. Every charter that looks at a page checks it on a phone too, in mobile WebKit (`references/charters.md`, "Phones").

When the ranked list is used up, the generators in `references/charters.md` make new charters. In attended mode, stop and ask whether to keep going. In `--drain`, keep going.

## Step 5: Report

See `references/report.md`. Keep it short: at most about 10 findings, ranked by confidence × blast radius. A long list gets ignored. Put everything else in the run folder.

In attended mode, show the report and offer the next steps:

- turn a confirmed finding into a ticket with the `ticket` skill, linked to the PR it most likely came from, with screenshots through `github-screenshots`;
- run another round;
- or stop.

Never create the ticket without the user's yes.

## Drain mode

The Tuesday routine calls `/rc-domino-hunt --drain` the night before the weekly usage reset. The point is to spend the rest of the week's usage on useful work, so:

- **Do not stop because the ranked list ran out.** Generators always have more.
- **Stop when** usage is at about 99% of the weekly limit, or 20 minutes before the reset, whichever comes first. Read both from the session usage tool (`get_usage`) at the start and after every charter. The reset time moves with daylight saving, so never hard-code it.
- **A second wake-up at about 3:30 AM** resumes from `hypotheses.json` if usage is still under about 97%. This is a second scheduled task, not something the first run schedules (see "The routine" below).
- **Ask nothing.** A charter that needs a ruling (a role user, creating content, a fleet-wide scan) is marked `blocked` with the reason, and the next charter starts.
- **No Lando.** Everything runs against Pantheon. Never start a local site on a drain night.
- **Keep the session small.** Charters run in subagents, state lives in files, and nothing reports progress between charters.
- **Write the report even if the run fails.** If the run stopped with more than 3% of the weekly usage left, the report's first line says so, as a failure, with the reason.

## The routine

Two scheduled tasks, both created **disabled** and turned on by hand when an RC window opens:

| Task | When | Prompt |
|---|---|---|
| `rc-domino-hunt-tuesday` | Tuesday about 9 PM ET | `/rc-domino-hunt --drain` |
| `rc-domino-hunt-resume` | Wednesday about 3:30 AM ET | `/rc-domino-hunt --drain`, only if usage is under about 97% and the reset has not passed |

`create_scheduled_task` has no enabled flag, so create each task and then set `enabled: false` with `update_scheduled_task`. Set `notifyOnCompletion: false`, since it defaults to true. Scheduled tasks only run while the desktop app is open. Unattended runs cannot read production with drush, so the skill already avoids that in `--drain`. Any other permission prompt blocks the charter and gets reported.

## Pending team decisions

These are open questions to Vincent. Until he answers, the defaults here apply. Each one lists the setting to change once he does.

| Question | Default until answered | Where it changes |
|---|---|---|
| Can we create `qa-<role>` users on RC sites, and remove them after? | No. Logged out plus user 1 for read-only setup only. Permission hypotheses are marked `blocked: needs role users`. | `references/rc-sites.md`, "Logins" |
| Can the hunt create `[domino-hunt]` content on RC sites? | No. Read-only, plus Layout Builder discard. | `references/rc-sites.md`, "What the hunt may change" |
| Can a read-only config scan run across all ~299 sites? | Attended mode only, with the user's yes each time. Never in `--drain`. | `references/charters.md`, "Fleet config scan" |
| RC cleanup and the `RELEASE_SITES_DEPLOYED` flag | Do not rely on the "Environments ready" comment. | `references/rc-sites.md`, "Find the RC" |

## Related skills

- `pr-feedback`: `references/drive-it.md` has the Playwright CLI setup, screenshot discipline, and role rules this skill adapts for RC sites. Use it, not this skill, to review one PR.
- `yalesites-portfolio`: block adoption numbers and per-page block data, used for blast radius and for picking which RC sites to test on.
- `release-prep`: owns each ticket's Release Testing Steps. This skill reads them as one source of what was already tested.
- `ticket` and `github-screenshots`: turn a triaged finding into a ticket.
- `yalesites-web-content`: the source of the "create nothing on the RC" rule and the Layout Builder discard rule.
