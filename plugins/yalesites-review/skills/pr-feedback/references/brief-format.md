# The pre-review brief: file contract

`pr-feedback` depends on a brief file, not on any one skill. Any producer that writes a file in
this format, at one of these paths, works. Today there are two producers:

- **`pr-brief`**, in this plugin. Small and generic. It never posts, comments, or changes labels.
- **An override skill**, named by `brief_skill` in `config.md`. For example, a scheduled audit
  that also comments and hands PRs back to the developer. Optional.

## Where the file lives

```
<brief_dir>/<repo>-<number>.md
```

- `<repo>` is the short repo name: `yalesites-project`, `component-library-twig`, `atomic`,
  `tokens`, or `yale-ui-cl`.
- `<brief_dir>` comes from `config.md`. Default: `~/.claude/yalesites/pr-feedback/briefs`.
- Consumers also read the legacy folder `~/.claude/yalesites/pr-prereview/briefs`, where
  scheduled audits have always written. When both folders hold a brief for the same PR, use the
  one whose SHA matches the head. If both match, or neither does, use the newer **Written** time.
- One file per PR. **Overwrite, never append.** A brief describes one SHA.
- Create the folder if it is missing.

**The brief is local and stays local.** It holds product calls a producer may not publish. No
part of "Your calls" or "Not checked here" goes onto GitHub word for word.

## Is it current?

Read the **Brief written against SHA** line and compare it to the PR's `headRefOid`:

| Compare | State | What `pr-feedback` does |
|---|---|---|
| `headRefOid` starts with the brief's SHA | current | Use it. Skip the diff read |
| It does not | stale | Use it for context, then read only the newer commits |
| No file, or no SHA line | absent | Get a new one (`SKILL.md` Step 1, lookup order) |

Write the SHA as at least 7 characters, so a prefix match is safe.

## Required layout

A header list, then these sections, as `##` headings, in this order. Write `None.` under a
section with nothing in it, instead of dropping the heading. The one exception is **Parity map**,
which only `yale-ui-cl` briefs carry.

```markdown
# {repo}#{number}: {title}

- **Ticket:** YaleSites-Internal#{NNNN}, {issue title} (yale-ui-cl#{NNNN} for a UICL PR)
- **Dev:** @{assignee}
- **Siblings:** {repo#number for the same ticket, or "none"}
- **Brief written against SHA:** {short sha}
- **Written:** {ISO timestamp}
- **Written by:** {producer skill name}
- **Audit outcome:** {producer's own words, e.g. "clean" or "handed to dev (2 findings)"; pr-brief writes "local brief only, nothing posted"}
- **CI:** {actual check states}

## What this changes
## Acceptance criteria coverage
## Parity map
## Regression surface
## Where to test
## Draft test plan
## Your calls
## Already answered, no action needed
## Follow-ups worth a ticket
## Not checked here
```

**Written by** is new. Older briefs lack it, and that is fine.

## What each section must hold

| Section | Contents | Who reads it in `pr-feedback` |
|---|---|---|
| What this changes | Two or three plain sentences: what the code does, from the diff, not the PR body | Step 3 |
| Acceptance criteria coverage | One bullet per AC item, tagged **Covered here:** `file:line`, **Covered in a sibling:** `repo#number`, or **Not covered anywhere:** | Step 2 spot-checks every "Not covered anywhere" |
| Parity map | `yale-ui-cl` only. One row per difference from YaleSites: component, difference, kind (parity gap, deliberate simplification, more options than YaleSites, UICL-only addition), evidence, planned ticket | Step 3, `drive-it.md` |
| Regression surface | One line per shared thing the diff touches, every other consumer found by grep, and where to see each. "None found" plus what was searched when the change is local | Step 3, row 1 of `beyond-ac-checks.md` |
| Where to test | The resolved environment URL, probed, per `preview-environments.md`. Say what it cannot show | Step 3 |
| Draft test plan | Numbered steps: what to do, where, expected result. Each marked AC, regression, or checklist row N. Name any step that needs a role other than platform admin | Step 3 |
| Your calls | Every product or UX call the producer would not decide, each as an answerable question with one line of context | Step 3b |
| Already answered, no action needed | `question`: answer, and what was checked | Step 2 |
| Follow-ups worth a ticket | `Visreg gap:` and `Docs:` items | Step 5 |
| Not checked here | What was deliberately left alone, and what could not be verified, with why | Step 3b, Step 10 |

## Rules for any producer

- Describe what was found. Do not write as the reviewer in the first person.
- Every call held back for a human goes under **Your calls**, as a question.
- Keep "Not covered anywhere" honest. An unaddressed AC item belongs there even when unsure; say
  it is unsure.
- The test plan is a draft. Never copy it to a ticket as Release Testing Steps.
- No em dashes.

## How an override skill is called

`pr-feedback` invokes it as `/<brief_skill> <repo>#<number> --dry-run`. In that mode the
override must write the brief in this format and post nothing to GitHub. If it is not installed,
`pr-feedback` says so in one line and falls back to `pr-brief`.
