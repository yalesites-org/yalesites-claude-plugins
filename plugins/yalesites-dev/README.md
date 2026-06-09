# yalesites-dev

Day-to-day Git, pull-request, and GitHub-issue workflow skills for YaleSites developers.

## What it does

Bundles the routine development-loop skills the YaleSites team uses against the
four platform repos (`yalesites-project`, `atomic`, `component-library-twig`,
`tokens`) and the `yalesites-org/YaleSites-Internal` issue tracker. The skills are
designed to compose into the normal flow: **find/understand a ticket → plan it →
commit → describe → open the PR(s)**.

| Skill | What it does |
|---|---|
| `create-issue` | File a well-formed bug or feature in YaleSites-Internal from a short description (drafts, then creates with the `forming` label). |
| `issue-lookup` | Read and summarize an existing issue to orient on its context and requirements. |
| `issue-plan` | Explore the codebase and produce a concrete, file-level implementation plan for a ticket. |
| `commit-conventional` | Create Conventional Commits (Angular style) following YaleSites commit specs. |
| `pr-description` | Generate a PR body from the current branch's commits and diff, filling a provided template. |
| `yalesites-pr` | Create the pull request(s) following YaleSites conventions, including cross-repo companion PRs. |
| `cross-repo` | Check status, create matching branches, or clean merged branches across all four repos at once. |

## How they compose

```
create-issue ─┐
issue-lookup ─┼─→ issue-plan ─→ (implement) ─→ commit-conventional ─→ pr-description ─→ yalesites-pr
              cross-repo branch <name>  (set up feature branches up front)
```

`issue-plan` pulls platform context from the `yalesites` plugin (install it from
this marketplace for the richest results).

## Installation

```
/plugin install yalesites-dev@yalesites-claude-plugins
```

## Notes

- **Read-only by default where it matters:** the skills draft and show you content
  (issues, PR bodies) before anything is created on GitHub.
- The four repos and the board (GitHub Projects v2, project 6) are treated as fixed
  YaleSites facts; your GitHub identity is resolved dynamically, so the skills work
  for any team member with repo access.

## Maintainer

Yale ITS Digital Experiences —
[yalesites-org/yalesites-claude-plugins](https://github.com/yalesites-org/yalesites-claude-plugins)

## Version

See `.claude-plugin/plugin.json` for current version.
