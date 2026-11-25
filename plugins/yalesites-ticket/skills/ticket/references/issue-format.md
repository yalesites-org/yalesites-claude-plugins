# Issue format

Load this when writing or grooming any ticket beyond a plain bug report: features, enhancements, docs and comms tickets, epic and phase children, and any groom of an existing ticket. The quick bug path in `SKILL.md` carries a short version. This file is the full version and wins if they disagree.

Every issue needs a clear title, a TL;DR line, then these six fields, in this order: Description, Acceptance Criteria, Priority, Risk, Type, Labels.

---

## How this reads on GitHub

An issue is opened and skimmed by people across the team, most of them non-technical. Compose the body per two files in `references/`: `github-communication-format.md` for the structure, and `github-writing.md` for the words. Read both before drafting.

`github-writing.md` is where the plain-language rules live: 20-word acceptance criteria, 25-word descriptive sentences, active voice, the word-swap table, and a 400-word budget on the visible layer of a ticket. The short version is that depth is free once it is collapsed, and the visible layer has to earn every word.

- **First line of the body is a TL;DR:** one or two plain-language sentences saying what the work is and why it matters. No Drupal jargon. This is the part everyone actually reads.
- **Keep visible:** the TL;DR, the Description, and the full Acceptance Criteria. Developers and QA work straight from the Acceptance Criteria, so it never gets collapsed.
- **Collapse into a named `<details>` block** (for example `<summary><b>Background and analysis</b></summary>`): the platform fit write-up, the archetype and UX-research reasoning from Step 1b of `references/platform-fit.md`, implementation context pulled from the repos, and links to prior art. The *conclusions* that change the work still surface in the Description and Acceptance Criteria; the supporting analysis sits in the collapsed block.
- One exception stays visible: an "already exists" or "conflicts with platform direction" flag from the platform fit check goes as a short note directly under the TL;DR, not inside the collapsed block, because it gates whether the ticket should be scoped at all.
- **Close with a `<!-- yalesites:agent -->` block** carrying the refs the next agent would otherwise re-derive: related issue and PR numbers, the epic or child links, and the platform-fit verdict as a flag. It is invisible on the rendered page. See the machine-only block section of `github-communication-format.md` for the rules, including what must never go in it.

**Check the draft before posting:**

```bash
python3 scripts/check-github-text.py draft.md --surface ticket
```

It flags em dashes, over-length criteria, banned words, a missing or bloated TL;DR, `<details>` blocks that will not render, and anything unsafe in the machine block. Findings are candidates, not verdicts: fix what is real, and say so if you are overriding one.

**Screenshots:** when a screenshot belongs on a YaleSites-Internal ticket or comment (a punch list, a bug repro, an image the user pasted into chat), use the `github-screenshots` skill (in this plugin) instead of asking the user to drag it in. It prints an `<img>` tag to put in the body. It refuses public repos, where the image would show as broken.

---

## Title

The title is what shows up in board views, search results, and notification emails. It needs to tell someone what the work is without opening the issue. Write (or rewrite) the title so it names the specific thing being built, fixed, or requested, not a vague category. "Fix embed bug" tells nobody anything; "RC: Embed block: missing title attribute on Bluesky, Instagram, and event map embeds" tells the reader exactly what's broken and where.

When grooming an existing stub ticket, check the title along with the other fields. A placeholder or overly generic title ("Bug in Layout Builder", "Update embeds") should be rewritten to reflect what the description actually says once it's filled in. If rewriting a title would change what the issue appears to be about (e.g., the original title implies a different bug than what's described), flag that for the user rather than silently reinterpreting.

**Common title prefixes.** The backlog uses a set of recurring prefixes that make similar tickets easy to spot and filter on. Apply one if it fits; don't force one onto a ticket that doesn't match any of these patterns. A plain, descriptive title is better than a mismatched prefix.

| Prefix | When to use |
|--------|-------------|
| `Hotfix:` | A ticket set to **Hotfix** priority. Unlike the others, this one stacks in front of the type prefix rather than replacing it, so a hotfix bug reads `Hotfix: Bug: <what's broken>`. See the stacking note below the table. |
| `RC:` | A bug found during release-candidate testing, before the release ships. Use when the prompt says something like "make an RC ticket" or references RC/QA testing. (Occasionally numbered, `RC2:`, `RC3:`, for issues found in a later regression pass on the same release.) |
| `Epic:` | The parent ticket for a multi-ticket initiative. See `references/epic.md`. |
| `Feature:` | A feature parent with phase children. See `references/feature.md`. |
| `Bug:` | A defect found outside of RC testing (reported by an editor, caught in normal use, etc.). |
| `Embed:` | New or changed support for a specific embeddable content type (calendars, maps, social posts). |
| `Embed Request:` | An intake ticket for a new embed type someone has asked for but that isn't scoped/dev-ready yet. |
| `Feature Request:` | A new-functionality ask, typically as raised by a stakeholder, before it's fully scoped. |
| `UX Research:` / `UX Discovery:` / `UX Evaluation:` | Research-workstream tickets: study prep, participant outreach, interview scheduling, evaluating an existing flow. |
| `Design:` | A visual/design deliverable with no dev work implied (mockups, icon sets, etc.). |
| `Web:` | Work on the yalesites.yale.edu marketing/content site itself, not the platform. |
| `Docs:` | A documentation-only ticket. |
| `Migration Tool:` | Work on content migration tooling (CSV import/export, etc.). |
| `Community Spotlight:` | A specific Community Spotlight content ticket. |
| `YS-Email:` | YaleSites training or release email tickets. |

**New embed providers need Michael's approval.** Any `Embed:` or `Embed Request:` ticket, or child of the Embed Requests epic (yalesites-org/YaleSites-Internal#1373), gets a `needs-decision` for `miketullo95` asking whether to add the provider, unless the ticket's Issue Type is Bug (a bug on an embed that already ships) or the ticket already has his `## Decision: approved` comment. Until it does, don't assign it or tag it `claude`, even if the user asks: say why and offer to raise the decision instead. The rule and the approval format are in `references/routing.md` ("New embed providers").

**`Hotfix:` stacks; the rest don't.** Every other prefix in the table is one-per-ticket. `Hotfix:` is the exception: it goes in front of whatever prefix the ticket already earned, so you get `Hotfix: Bug: ...` or `Hotfix: View: ...`. This matters because Priority is a Projects v2 field, which means it doesn't appear in search results, notification emails, or most board views. The title prefix is the only place the urgency is visible to someone skimming. Whenever Priority comes back as Hotfix, prepend it. Reference examples: yalesites-org/YaleSites-Internal#1729, yalesites-org/YaleSites-Internal#1730, yalesites-org/YaleSites-Internal#1732, yalesites-org/YaleSites-Internal#1381.

**Epic child tickets** follow a related but distinct pattern: they're prefixed with a short form of their epic's name rather than one of the prefixes above, so they group together visually in the backlog (e.g., `Views Block Rework: Authoring Form UX/UI Audit`, `Publications: Teaser Display`, `Wave 3: Interactive molecules`). When scoping child tickets for a new epic, pick one short, consistent name and apply it to every child ticket. See `references/epic.md`. Feature phase children use `<Feature name>: <Phase>`; see `references/feature.md`.

---

## TL;DR (first line of the body)

One or two sentences, plain language, leading with what the work is and why it matters. Write it last, once the Description and Acceptance Criteria are settled. Example: *"Editors can't set alt text on gallery images, so galleries fail accessibility review. This adds an alt-text field to each gallery item."* Keep it above the Description; it is the only part guaranteed to be read.

## 1. Description

Briefly describe the feature, bug, or improvement in plain language. Avoid developer jargon. Focus on **what it is** and **why it matters** to the user or platform. Anyone on the team, regardless of technical background, should be able to read this and understand the work.

Search the code repos for implementation context when you need it, but always write the description in plain English first. Technical details belong in the acceptance criteria, not the description.

---

## 2. Acceptance Criteria

A single bulleted list of everything required to close the issue. Cover all relevant angles:

- Developer tasks and technical requirements
- UX considerations (field labels, design option names, UI behavior). Where Step 1b of the platform fit check identified an affected archetype, write the expectation as a testable criterion rather than a general aspiration. "A New Recruit can complete this without asking a teammate" is checkable; "should be intuitive" isn't.
- Accessibility: flag anything that needs WCAG 2.1 AA validation for the accessibility engineer
- Documentation: note if any existing docs need updating or new docs need to be created
- Spikes and ADRs: when the deliverable is an ADR (architecture decision record), add the criterion that it lands in `yalesites-org/YaleSites-Internal` under `docs/adr/{issue-number}-{short-description}.md`, not in a product repo. This applies to a standalone spike ticket as much as to the first child of an epic, so the dev or their agent does not default to the repo the code lives in. The full convention is in the `yalesites` skill's `references/adr-conventions.md` (core `yalesites` plugin), if it is installed.

If an existing ticket has an unresolved internal debate (e.g., a past comment thread arguing both sides of a design question), don't resolve it unilaterally while grooming. Preserve it as an explicit open acceptance-criteria item so it gets a real decision rather than getting silently closed over. Also raise it as a `needs-decision` with its block (see `references/decisions.md`), so it shows up in the decider's queue instead of waiting for someone to reread the ticket.

**Visreg site page tickets** (anything that adds or changes pages on the visreg site, `/blocks-for-visreg`) can't be worked until the feature they cover is live. Put the ticket in the **next** release milestone after the feature's, set its Status to `Blocked`, and add a line saying which release it waits for. When it is a phase child, use the `visreg-site` phase (see `references/feature.md`). Storybook visreg stories are different: they are code that ships with the feature, so they take the feature's milestone like any other ticket.

**Documentation tickets for features that haven't shipped yet:** these can still be marked `To Do` so the doc can be drafted and staged in parallel with development. Mark the ticket as blocked by the feature ticket, and add an explicit acceptance criterion not to publish until the feature ships. Under a feature parent the Docs phase child is the exception: it starts in `Backlog` and waits for its gatekeeper's go once Development finishes (see the Gate column in `references/routing.md`, and `references/feature.md`).

---

## 3. Priority

Choose one based on user and platform impact. Priority says what goes first, not when: the milestone says when. Agents pick up work in Priority order within a milestone (see "Priority and the agent pickup order" in `references/routing.md`), so don't raise a ticket's Priority to pull it into a release. Give it the right milestone instead.

| Priority | When to use |
|----------|-------------|
| **Hotfix** | Critical issue breaking core functionality or accessibility. Jumps ahead of every milestone and ships on its own. Also prepend the `Hotfix:` title prefix (see "Title" above). |
| **High** | Significantly impacts user experience or blocks key workflows. First in its milestone. |
| **Medium** | Improves platform usability or addresses moderate user pain points. |
| **Low** | Nice-to-have enhancement with minimal user impact. Last in its milestone. |

---

## 4. Risk

How much could go wrong, and how hard it is to undo. Risk sets how carefully the work is built and reviewed, and breaks ties in the agent pickup order. It replaced Size on 2026-10-28; don't estimate effort.

| Risk | Means | What it triggers |
|------|-------|------------------|
| **Low** | Bounded, existing patterns, easy rollback | The normal gate and pre-review, one quick human look |
| **Medium** | Shared components, config, update hooks, editor-facing UI | A plan comment before building, functional and design review |
| **High** | New data, auth, migrations, irreversible, or cross-repo | A spike or ADR first, Dave on code, Michael on product, visual regression, Vincent on deploy |

If unsure between two levels, pick the higher one.

---

## 5. Type

Set as the native Issue Type (see "Setting the native Issue Type" in `references/fields.md`). Choose one:

| Type | When to use |
|------|------------|
| **AI** | Work related to the Beacon AI chatbot |
| **Bug** | An unexpected problem or behavior |
| **Communications** | Work that falls under the Communications workstream. Includes documentation written for the public yalesites.yale.edu site (user guide pages, resource pages, release documentation), even when the title carries the `Docs:` prefix. A `Docs:` prefix does not imply Task. |
| **Feature** | A request, idea, or new functionality |
| **Task** | A specific piece of work |
| **Vendor/Supported Builds** | Websites being built by vendors or supported by the YaleSites team |
| **Epic** | The parent of a multi-ticket initiative only. See `references/epic.md` |

---

## 6. Labels

Labels describe the work, not its type: the native Issue Type covers that, so never add a type label (`bug`, `feature`, `task`, `epic`, `communications`). Apply:

- **At most one workstream:** `design-system` (components, Storybook, themes, tokens), `platform` (Drupal features, views, embeds, forms, config), `ai` (Beacon and AI features), `devops`, `docs-comms` (docs, release notes, comms), or `migration`.
- **Any flags that fit:** `accessibility`, `tech-debt`, `feedback`, `non-testable`.

The old area labels (`component-library`, `color-system`, `views-blocks`, `embeds`, and the rest) and requester tags (`opac`) were retired on 2026-10-28. Don't recreate them. Never apply `status:*`, `priority:*`, or `size:*` labels either (see `references/fields.md`).

`claude` is a workflow label, not a descriptive one. It only goes on when the user has explicitly confirmed it and the ticket clears the bar in "Claude pickup" in `references/fields.md`. Never add it as part of a routine "apply all relevant labels" sweep.
