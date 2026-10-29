# Phase 2: test plan gap analysis

This is mutation testing applied to our testing steps, not to our code. For each PR, ask: "if this change broke in a way its developer did not expect, would the steps we tested it with have caught it?" Every "no" is a hypothesis for Phase 3.

It borrows from Meta's mutation-guided test generation (arxiv.org/abs/2501.12862). Engineers accepted most of its tests because each one targeted one concrete, specific fault. Generic "might break" guesses were noise. The same holds here.

## 1. Find what each PR was tested with

There is no PR template, so look in this order and use everything you find:

1. The PR body, `### Functional testing steps:` (the yalesites-dev convention).
2. Other headings in the PR body: "To check on the multidev", "Testing", "How to test", "QA".
3. The linked issue's `## Release Testing Steps` section (written by `release-prep`).
4. A pr-feedback run folder for the PR, if there is one (`~/.claude/yalesites/pr-feedback/runs/<repo>-<N>-*/results.md`). It lists what was actually driven and passed.
5. Unchecked boxes in any of the above. An unchecked step is a step nobody ran. The calendar filter hotfix (yalesites-org/YaleSites-Internal#1053) was an unchecked step on its feature PR.

If a PR has no testing steps anywhere, every behavior change in its diff counts as untested.

## 2. Write the gaps as concrete claims

Read the diff hunk by hunk. For each behavior it changes, write what a plausible unexpected break would look like, then check it against the steps. Keep the gap only if the steps would miss it.

Every gap needs all four parts:

| Part | Example |
|---|---|
| **Change** | yalesites-org/yalesites-project#1666 adds a small size to the wrapped image block |
| **Untested condition** | wrapped image inside a 33/33/33 section, theme 3, at 768px |
| **Oracle**: what you would see if broken | the image overflows its column, or text wraps under it instead of beside it |
| **Why the steps miss it** | the testing steps only place the block in a one-column section at desktop width |

Drop a gap if:

- it has no observable oracle ("might cause issues");
- the change cannot affect it (an equivalent mutant: for example, a renamed private variable);
- or it duplicates another gap.

Mark each remaining gap with the surfaces from the impact map it touches.

## 3. What to look for, from real hotfixes

These are the gap types that caused real hotfixes. Check every PR for each one:

| Gap type | What the steps usually skip | Real example |
|---|---|---|
| **Neighboring setting combinations** | The PR tested one filter, option, or layout. The bug lived in the next one over. | Calendar filters and navigation: yalesites-org/YaleSites-Internal#1053, yalesites-org/YaleSites-Internal#1136, yalesites-org/YaleSites-Internal#1847 |
| **Old content** | Steps create a new block. Existing blocks, saved before the new field or validation existed, were never opened. | yalesites-org/YaleSites-Internal#1052 |
| **Empty and missing states** | Steps fill every field. The bug shows when a field is empty or a list has no items. | Apply button on a calendar with no filters: yalesites-org/YaleSites-Internal#1136 |
| **Color and theme** | Steps check one theme or the default section color. | Link Grid heading white-on-white: yalesites-org/YaleSites-Internal#1734 |
| **Role** | Steps run as an admin. | Media library Access denied for non-admins: yalesites-org/YaleSites-Internal#1791 |
| **Data shape** | Steps use simple test data. Real data has many roles per user, multi-day events, long URLs. | Dashboard listing editors once per role: yalesites-org/YaleSites-Internal#1732 |
| **Logs** | Steps look at the page. The bug is only a PHP warning in the log. | yalesites-org/YaleSites-Internal#1824 |
| **Scale** | Steps use a small site. Update hooks time out on big ones. | yalesites-org/yalesites-project#1168 |

## 4. Standing hypotheses

Add these on every RC, whether or not a PR points at them. Mark them `standing` in `hypotheses.json`:

1. **Events calendar.** Every filter type (include, exclude, parent term, none) × month navigation × Apply × list and grid view, on RC sites with real Localist events. This is our most-hotfixed surface.
2. **New validation or required fields on old data.** For every new required field, new validation, or changed default in the RC, find existing entities that would fail it (see "Old-data queries" in `charters.md`).
3. **Section color contrast.** Every block the RC touched, on every section color, checked with axe for contrast.
4. **Log diff.** New warnings or errors on each RC site compared with live (see `charters.md`).
5. **Reusable vs. inline.** Every block type the RC touched, placed both ways (yalesites-org/YaleSites-Internal#1381).

## 5. Overlaps and wide triggers

- Every overlap from the impact map becomes a hypothesis: "PRs A and B both touch X. Check X where both changes apply at once." Name the condition where both apply.
- Every wide trigger becomes a pairwise charter (see "Generators" in `charters.md`) rather than one hypothesis per block.
- Every `untraced` entry becomes a judgment hypothesis: say what the file could reach, and where to look.

## 6. Rank

Score each hypothesis from 1 to 3 on each of these, then multiply:

| Factor | 1 | 2 | 3 |
|---|---|---|---|
| **Blast radius** (sites using the surface, from the impact map) | under 20 | 20 to 100 | over 100, or a wide trigger |
| **Overlap** | one PR | one PR plus contrib | two or more PRs |
| **Severity if real** | cosmetic | broken for some editors or pages | data loss, 5xx, security, or broken for all editors |

Standing hypotheses start at a minimum score of 9. Ties go to the hypothesis matching a gap type from the table above that has caused the most hotfixes.

## Output shape

Each entry in `hypotheses.json`:

```json
{
  "id": "h014",
  "kind": "gap | overlap | wide | untraced | standing | generated",
  "prs": ["yalesites-project#1666"],
  "surfaces": ["block:wrapped_image"],
  "claim": "Small wrapped image in a 33/33/33 section on theme 3 at 768px overflows its column",
  "oracle": "image box wider than its column, or body text below the image instead of beside it",
  "why_missed": "PR steps place it only in a one-column section at desktop width",
  "score": 18,
  "status": "open",
  "sites": ["ys-your-yale-edu", "ys-registrar-yale-edu"],
  "charter": null,
  "result": null
}
```
