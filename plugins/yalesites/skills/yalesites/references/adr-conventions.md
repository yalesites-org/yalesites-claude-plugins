# ADR conventions

Where architecture decision records live, how they are named, and how their PRs look. The `ticket`, `issue-plan`, and `yalesites-pr` skills all point here, so this file is the one place the rule lives.

## Where

ADRs go in `yalesites-org/YaleSites-Internal` under `docs/adr/`. Never in yalesites-project, component-library-twig, atomic, or tokens, even when the decision is about code in one of them. Those repos ship to sites; YaleSites-Internal is where the team's decisions live.

If the same issue also needs code changes, those still go in the product repos as usual, in a separate PR.

## Naming

`docs/adr/{issue-number}-{short-description}.md`, for example `docs/adr/1711-ai-readability.md`. The issue number is the YaleSites-Internal ticket the spike or ADR was scoped under. With no issue, use the branch slug and say so in the PR.

## Recognizing one in a diff

Treat an **added** Markdown file as an ADR when either holds:

- its path contains `adr` or `decision` (`docs/adr-foo.md`, `docs/adr/0002-x.md`, `docs/decisions/0002-search.md`, `ADR-001.md`, `docs/architecture/0001-x.md` with an ADR heading)
- its first heading contains `ADR` or `decision record`

Only added files count. An edit to an ADR that already exists in a product repo is not blocked; note it and leave the move to a follow-up.

## The PR

- Repo `yalesites-org/YaleSites-Internal`, branch `{issue-number}-{short-description}`, base `main` (the repo has no `develop`)
- Title `{issue number}: {issue title}`, the same as a product PR
- Body: a TL;DR line saying what was decided and why, a link to the ADR file on the branch, then `References yalesites-org/YaleSites-Internal#NNN`
- No multidev, Netlify preview, or testing-step links: nothing deploys from this repo
- Link the PR from the issue with a comment once it exists

## Acceptance criterion for spike and ADR tickets

Every ticket whose deliverable is an ADR carries this criterion, so the dev or their agent does not default to the repo the code lives in:

> The ADR lands in `yalesites-org/YaleSites-Internal` under `docs/adr/{issue-number}-{short-description}.md`, not in a product repo.
