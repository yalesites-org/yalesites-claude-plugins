# Reviewer roles, dimensions, and pass labels

Read this from `SKILL.md` Step 0. It answers three things: what a review dimension is, which
`pass ___ review` label each dimension maps to in each repo, and which dimensions a given
GitHub login owns when that person has no personal reviewer profile.

**This file is the fallback, not the primary source.** The primary source is the reviewer's own
profile at `~/.claude/yalesites/pr-feedback/reviewer-profile.md`, written by the
`reviewer-profile` skill. A person's profile always wins over their row here, because they wrote
it and this table was written about them. This file exists for two cases: a teammate who has not
built a profile yet, and a teammate on a new machine whose profile has not travelled with them.

---

## The five review dimensions

| Dimension | What it covers | What it does not |
|---|---|---|
| `code` | Implementation quality, structure, naming, error handling, test coverage, security, whether the approach will hold up | Whether the thing was worth building |
| `functional` | Does the built thing do what the ticket asked, in the running environment, for the roles that matter | Whether the code behind it is any good |
| `design` | Visual fidelity to the design, spacing, typography, responsive behavior, component consistency, interaction feel | Drupal-side plumbing |
| `a11y` | Keyboard paths, screen reader output, semantics and landmarks, contrast, focus management, reduced motion | Visual polish that carries no accessibility consequence |
| `product` | Was this the right ask, is the copy right, are the defaults right, is the scope right, who should be able to do it | Any of the above four |

A dimension is a claim about **what someone actually checked**. That is the whole point of
scoping: a review should not stamp a label asserting a check nobody performed.

## Dimension to label, per repo

Confirmed against all four repos' label sets on 2026-09-21. **Never send a label a repo does not
define.** Step 8's `PUT` creates it silently rather than erroring, which litters a new label onto
the repo.

| Dimension | Label | `yalesites-project` | `component-library-twig` | `atomic` | `tokens` |
|---|---|---|---|---|---|
| `code` | `pass code review` | yes | yes | yes | yes |
| `functional` | `pass functional review` | yes | yes | yes | yes |
| `design` | `pass design review` | **no** | yes | **no** | **no** |
| `a11y` | `pass a11y review` | yes | yes | **no** | **no** |
| `product` | none | n/a | n/a | n/a | n/a |

`product` has no label of its own anywhere. A product-only call is recorded in the review body,
not on a label. In practice `product` travels with `functional`, because the person weighing
whether the ask was right is usually the same person clicking through the running thing.

**When a reviewer's dimensions yield no label for this repo**, a design reviewer on a
`yalesites-project` PR for instance, apply no pass label, say plainly which dimension they own and that
the repo defines no label for it, and ask before adding `ready to merge`. Do not fall back to
`pass functional review` to have something to apply. That fallback is the bug this whole feature
exists to fix.

## Login to dimensions

Resolve the login with `gh api user --jq .login`.

| GitHub login | Person | Role | Owns | Entitled to apply |
|---|---|---|---|---|
| `miketullo95` | Mike Tullo | Product Manager | `functional`, `product` | `pass functional review` |

### Adding someone to this table

**Confirm the handle with the person. Do not infer it.** Not from org membership, not from
commit history, not from a name that looks close enough. A wrong row is worse than a missing
one: a missing row gives that person today's full ungated review, while a wrong row silently
withholds feedback they were the right person to give, and stamps a label for a dimension they
never checked.

Ask them two things and write down their answers, not your reading of their job title:

1. Which of the five dimensions above are yours to rule on?
2. Which are explicitly not yours, that you would want left for someone else?

Roles we know exist on the team and have **not** confirmed handles for yet, so they are
deliberately absent from the table above rather than guessed at:

- UX / design reviewer: would own `design`, likely `a11y`
- Platform developers: would own `code`, likely `functional`
- Accessibility reviewer: would own `a11y`

Until a row exists, those reviewers get the ungated path, which is correct behavior and not a
failure. There is no hurry to fill the table in.

### Who keeps this current

Whoever maintains the `yalesites-product` plugin. This table and the dimension-to-label matrix
above are the two parts of this feature that go stale as the team changes, so they live in one
file on purpose. Re-confirm the label matrix against the repos if a repo's label set changes:

```bash
for r in yalesites-project component-library-twig atomic tokens; do
  echo "=== $r ==="
  gh label list --repo yalesites-org/$r --limit 200 --json name -q '.[].name' \
    | grep -Ei 'pass|ready to'
done
```
