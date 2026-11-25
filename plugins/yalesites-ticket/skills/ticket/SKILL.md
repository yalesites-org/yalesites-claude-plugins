---
name: ticket
description: "Create and groom YaleSites GitHub issues. Use to report a bug or request, file a new issue, fill out a stub ticket, review a ticket for completeness, or prepare issues for a sprint or grooming session. Also scopes epics ('create an epic', 'epic for X', 'break this into an epic', 'this is too big for one ticket') and Feature parents with one sub-issue per phase (UX, Design, Development, QA, Visual regression, Docs) chained by blocked-by dependencies, and gathers an in-flight feature's loose tickets under one parent. Sets the title, description, acceptance criteria, Issue Type, labels, board Status, Priority and Risk, milestone (defaulting to the next feature release), assignee, and the `claude` agent-pickup label. Raises or resolves a `needs-decision` or `follow-up` ('flag this for April to follow up', 'this needs a decision from Michael'). Non-groomers filing a feature request get a short `forming` intake stub instead. Checks the platform knowledge base for overlap with existing features."
---

# YaleSites Ticket Skill

This skill files well-formed GitHub issues in `yalesites-org/YaleSites-Internal` and grooms existing ones. Anyone on the team should be able to read the result, whatever their technical background.

This file holds the short path: who is filing, the intake stub, and a bug report or simple request from start to finish. Heavier flows (features, epics, grooming, decisions) load a reference file only when needed. See "Which file to load" at the end.

## Rules for every ticket

- **Full cross-repo references.** A bare `#1299` always resolves in the current repo, even if the text names another repo. Write `yalesites-org/yalesites-project#1299`. Use the full `owner/repo#number` form for every issue and PR reference.
- **Never use labels for board fields.** Status, Priority, and Risk are board fields. Never apply `status:*`, `priority:*`, or `size:*` labels. Size is retired; don't ask for it.
- **Comments can only be added, never edited.** Post a follow-up comment instead of trying to revise one.
- **The GitHub connector is read-only on `yalesites-project`.** It can create and comment on issues in YaleSites-Internal. To comment on a `yalesites-project` PR, use `gh`, or draft the text and hand it to the user to paste.
- **Plain language first.** Search `yalesites-project`, `component-library-twig`, and `atomic` for context when the work is technical. Technical detail goes in the acceptance criteria, not the description.
- **Only set what was confirmed.** Don't advance a ticket through the workflow as a side effect of filing or grooming it.

---

## Step 0: Who's filing

**Check this first, before any other step.** Grooming means product calls (priority, scope, phases, milestone, who builds it). Those belong to the groomers listed in `references/routing.md` under "Intake." Find out who is running the skill:

```bash
gh api user --jq .login
```

- **A groomer** (`miketullo95` for anything; `dblanken-yale` for dev-only work): use the full flow. For a bug or simple request, that is the quick path below. For anything bigger, see "Which file to load."
- **Anyone else, filing a feature request or enhancement:** write an **intake stub** (below) and stop. Don't ask about phases, Priority, Risk, milestone, assignee, or `claude`. Those aren't their calls, and asking makes filing feel like a test.
- **Anyone else, filing a bug or comms, docs, or training work:** use the quick path below, but skip the Priority question and leave Priority unset. Say in your summary that a groomer will set it.

If the request is unclear about which kind it is, ask the filer one plain question ("Is this something broken, or something new you'd like it to do?"), not a field.

## The intake stub

Ask the filer only what they know, in one `AskUserQuestion` call or from what they've already said:

- What was asked for, in the requester's own words if possible
- Who asked (name and office or site), and where it came from (ServiceNow ticket number, office hours date, email, meeting)
- Why it matters to them, and how many people it affects if they know
- Links or screenshots (use the `github-screenshots` skill for images)

Then run the quick existing-feature check (Step 2 of the quick path). If the feature already exists, tell the filer right away; they may be able to answer the requester today. Put the finding in the stub.

Write it like this:

```markdown
**TL;DR:** [Requester] asked for [one plain sentence]. Filed for grooming.

## The request
[What they asked for, in their words. Why it matters to them.]

## Where it came from
**Requester:** [name, office or site]   **Source:** [ServiceNow INC/RITM number, office hours YYYY-MM-DD, email]
**Filed by:** @[filer]

## Platform fit
[Already exists / extends X / new. One or two lines.]

<!-- yalesites:agent
surface: ticket
kind: intake-stub
source: [servicenow|office-hours|email|meeting|other]
-->
```

Create it with title `Feature Request: <what they want>`, Issue Type `Feature`, label `forming`, board Status `Backlog`, and nothing else (no Priority, Risk, milestone, assignee, or `claude`). Use the create and write commands in Step 6 below. Read back the type, label, and Status. Then tell the filer: "Filed as yalesites-org/YaleSites-Internal#N. Michael will groom it; you'll see it move when he does."

---

## Quick path: a bug report or simple request

Use this for a bug (including an RC bug), comms, docs, or training work, or a small enhancement: one developer, one Acceptance Criteria list, no UX or design work, docs that fit as one AC line. It finishes without loading a reference file. If it turns out to be bigger, stop and switch to the right flow in "Which file to load."

### Step 1: Gather the facts

From what the user said, or in one `AskUserQuestion` call for what's missing:

- **What happens, and what should happen.** For a bug: the site and page URL, the steps that show it, and what the user expected.
- **Who reported it and where.** ServiceNow number, office hours, RC testing, email.
- **Screenshots.** Use the `github-screenshots` skill (in this plugin). It prints an `<img>` tag for the body and refuses public repos.

### Step 2: Quick existing-feature check

Check that the request isn't already handled. If the core `yalesites` skill is installed, check its blocks, content types, settings, and views references. For a bug, check that the behavior isn't by design. If it already exists or works as intended, say so right away and add a short visible note under the TL;DR ("Note: this functionality may already exist via [X]. Recommend confirming before scoping.").

If the `yalesites` skill isn't installed, say so and don't guess. Groomers filing a feature, an enhancement, or an editor-facing bug run the full check in `references/platform-fit.md` (who it affects, how much it's used).

### Step 3: Title

Name the specific thing that is broken or wanted, not a category. "Fix embed bug" says nothing. "RC: Embed block: missing title attribute on Bluesky, Instagram, and event map embeds" says what and where.

Common prefixes: `Bug:` (found in normal use), `RC:` (found in release-candidate testing), `Docs:`, `Web:` (the yalesites.yale.edu site itself), `YS-Email:`, `Design:`. Use one only if it fits. `Hotfix:` is the one that stacks: a Hotfix-priority bug reads `Hotfix: Bug: <what's broken>`. The full prefix table is in `references/issue-format.md`.

**Embed tickets.** A new embed provider (`Embed:` or `Embed Request:`, not a Bug on an embed that already ships) needs Michael's approval first. Load `references/decisions.md`.

### Step 4: Body

```markdown
**TL;DR:** [One or two plain sentences: what is wrong or wanted, and why it matters.]

## Description
[Plain language. What happens, where, and what should happen instead. Who it affects.]

## Acceptance Criteria
- [One testable outcome per line. Start with a verb. 20 words or fewer.]
- [Accessibility: anything needing WCAG 2.1 AA validation.]
- [Docs: any existing doc that needs an update.]

<details>
<summary><b>Background and analysis</b></summary>

[Repro detail, implementation context from the repos, links to prior art.]

</details>

<!-- yalesites:agent
surface: ticket
related: [yalesites-org/yalesites-project#NNNN]
-->
```

Writing rules: no em dashes. Active voice. Descriptive sentences 25 words or fewer, acceptance criteria 20 or fewer. Keep the visible part (TL;DR, Description, Acceptance Criteria) under about 400 words. Leave a blank line after `</summary>` and before `</details>`. Nothing a person needs may live only in the machine block, and no secrets go in it. Write the TL;DR last.

Check the draft before posting:

```bash
python3 scripts/check-github-text.py draft.md --surface ticket
```

Findings are candidates, not verdicts. Fix what is real, and say so if you override one. If a finding isn't clear from these rules, load `references/github-writing.md` and `references/github-communication-format.md`.

### Step 5: Fields

Ask for anything the user hasn't answered, in `AskUserQuestion`. It allows at most **4 questions per call** and **4 options per question**, so batch board fields (Status, Priority, Risk, Milestone) in one call and Assignee plus `claude` in a second. Offer the likeliest options; **Other** covers the rest. Never guess a field silently.

- **Status**, exact text: `Backlog`, `To Do`, `Blocked`, `In progress`, `In review`, `Done`. A new bug is usually `Backlog` or `To Do`.
- **Priority:** `Hotfix` (breaks core functionality or accessibility; ships on its own), `High` (blocks key workflows), `Medium` (moderate pain), `Low` (nice to have). Priority is order, not timing. Skip it for a non-groomer.
- **Risk:** `Low` (bounded, easy rollback), `Medium` (shared components, config, update hooks, editor-facing UI), `High` (new data, auth, migrations, irreversible, cross-repo). If unsure, pick the higher one.
- **Milestone:** recommend the next dated release still ahead of today (title `MM-DD-YY ... Release`). A due date of today or earlier isn't upcoming, and new feature work doesn't go into a release already in RC. A `Hotfix` ticket gets the open `MM-DD-YY Hotfix` milestone. List them with:
  ```bash
  gh api repos/yalesites-org/YaleSites-Internal/milestones --paginate -q '.[] | "\(.number)\t\(.title)\tdue=\(.due_on)"'
  ```
- **Assignee:** offer three likely handles plus "leave it unassigned for now." Usual owners: `dblanken-yale` (development), `vinmassaro` (CI, deploy, Drupal and PHP upgrades), `ntay90` (accessibility), `atiddei` (UX), `alyssadechiaro` (events and Localist), `chrissuquie` and `rachel-is-at-yale` (ServiceNow intake and comms; keep them on tickets they filed), `miketullo95` (PM).
- **`claude` label:** ask before adding it. It hands the ticket to the dev team's Claude agent. Only on a fully groomed ticket with a milestone and nothing waiting on a decision.

**Type** (native Issue Type, not a label): `Bug`, `Task`, `Feature`, `Communications` (includes docs for yalesites.yale.edu), `AI` (Beacon), or `Vendor/Supported Builds`.

**Labels:** at most one workstream (`design-system`, `platform`, `ai`, `devops`, `docs-comms`, `migration`) plus any flags that fit (`accessibility`, `tech-debt`, `feedback`, `non-testable`). Never a type label.

The full rules behind each field are in `references/fields.md` (fields), and `references/issue-format.md` (Type, Labels, Priority, Risk).

### Step 6: Create, write the fields, read back

```bash
gh issue create --repo yalesites-org/YaleSites-Internal --title "<title>" --body-file draft.md \
  --milestone "<milestone title>" --assignee <handle> --label <label>
gh api -X PATCH repos/yalesites-org/YaleSites-Internal/issues/<n> -f type=Bug
scripts/set-board-fields.sh <n> Status="To Do" Priority=Medium Risk=Low
```

`set-board-fields.sh` adds the issue to the YaleSites Board and sets every board field in one write. Don't use `gh project item-edit --url` instead. Then read everything back in one query:

```bash
gh api graphql -f query='query($n:Int!){repository(owner:"yalesites-org",name:"YaleSites-Internal"){issue(number:$n){issueType{name} milestone{title} labels(first:20){nodes{name}} assignees(first:5){nodes{login}} projectItems(first:5){nodes{project{number} fieldValues(first:20){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2FieldCommon{name}}}}}}}}}}' -F n=<n>
```

A command with no error is not proof. Fix anything missing and name it.

**If `gh` fails or lacks the `project` scope,** don't loop or troubleshoot. Create the issue however works, then give the user the exact board values to set by hand (`Status: Backlog, Priority: Medium, Risk: Low`) with the link. The durable fix is `gh auth refresh -h github.com -s project,repo,read:org,workflow,gist`, or the `onboard` skill in this plugin.

### Step 7: Report back

Give the full `owner/repo#number` link and the fields as read back. Say what you left unset and why.

---

## Which file to load

Load only the files the flow needs. All paths are relative to this skill.

| Flow | Load |
|---|---|
| Filling in or confirming any field in depth: full Status table, milestone kinds and Hotfix milestones, the assignee table and routing habits, the `claude` bar, writing fields, Issue Type ids | `references/fields.md` |
| Full issue format: GitHub layout rules, the full title prefix table, Acceptance Criteria rules (ADRs, debates, visreg pages, docs tickets), and the Priority, Risk, Type, and Labels tables | `references/issue-format.md` |
| Platform fit check for a feature, enhancement, UX change, or any epic or phase child: what exists, who it affects, how much it's used, scope classification | `references/platform-fit.md` |
| A new Feature: parent plus phase children, allowed regions, blocked-by wiring, or gathering an in-flight feature under a parent | `references/feature.md`, then `references/routing.md` for the phase table |
| An epic: clarifying questions, spike first, the epic template, anti-patterns, epic quality bar | `references/epic.md` |
| Grooming an existing or `forming` ticket, a completeness review, drift on a ticket with history, a backlog sweep, and the full Quality Bar | `references/grooming.md` |
| Raising or resolving `needs-decision` or `follow-up`, or a new embed provider's approval | `references/decisions.md`, then "Waiting on a person" in `references/routing.md` |
| Phase owners, gates, groomers, the agent pickup order, lane floors, embed approval rules | `references/routing.md` |
| Reading board fields, the `project` scope, who sets which Status when, why there is no label fallback | `references/board-status.md` |
| Writing rules in full, and the GitHub body layout rules | `references/github-writing.md`, `references/github-communication-format.md` |

A groomer setting all fields on a feature, enhancement, or groomed ticket reads `references/fields.md` and `references/issue-format.md`, and runs `references/platform-fit.md` first. Every groomed ticket ends with the Quality Bar in `references/grooming.md`.
