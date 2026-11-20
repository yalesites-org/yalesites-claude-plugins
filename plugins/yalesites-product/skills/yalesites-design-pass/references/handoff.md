# Round 3: handoff spec and Storybook docs page

Both are drafts the reviewer approves on the board. Nothing here posts on its own.

## Handoff spec

Model: the Office Hours handoff on yalesites-org/YaleSites-Internal#1710 (comment of
2026-09-29). It went to a developer's agent and was built with almost no follow-up questions,
because it named where each piece lands and what to check first. Follow the GitHub writing
standard (`ticket/references/github-writing.md` and `github-communication-format.md`) and run
`ticket/scripts/check-github-text.py --surface ticket` on it.

The TL;DR promises the zip in the next comment. Nothing can upload it for us (`gh` and
`github-screenshots` cannot attach a zip), so the reviewer drags it into that comment by hand.
Say so when you hand them the draft.

```markdown
**TL;DR:** The <component> design is done, and the handoff is below. The reference mockups are
in the zip in the next comment. <dev>, this is ready to build in <dev ticket refs>.

**Where each piece lands**
- **<owner/repo#N> (<what>):** <one or two lines of the decision that ticket needs>.

**New and changed components**
<Every new or changed piece, or "None: built entirely from existing components.">
- **New molecule: <Name>** (`02-molecules/<name>`). <Why <existing component> could not do it>. Reusable for <other blocks>.
- **Changed atom: <Name>** (`01-atoms/<name>`). <What changes>. Also used by <components>, so check them in the PR.

**Check these first, and report back in the PR**
1. <the thing most likely to be wrong, e.g. a theme the library has not supported before>
2. <a width or token pairing we did not measure>

<details><summary><b>Component inventory</b></summary>

The <component> is a <molecule | organism> in `<0N-level>/<name>`.

| Level | Component | Status | Storybook |
|---|---|---|---|
| Organism | <Name> | new | n/a |
| Molecule | Card | existing | <link> |
| Atom | Button | changed: icon-only size | <link> |
| Token | <slot> | existing | |
</details>

<details><summary><b>Structure and stack rule</b></summary>
The reference files are mockups, not production code. Rebuild them in component-library-twig
(Twig, SCSS, Storybook) and atomic. <markup structure, container query rule, what stacks when>
</details>

<details><summary><b>States</b></summary>
<every state, each with its colors and contrast ratio>
</details>

<details><summary><b>Theming</b></summary>
<which theme slots it reads; "no new colors" unless a token change is part of the work>
</details>

<details><summary><b>Editor form</b></summary>
<field labels, help text, defaults, validation>
</details>

<!-- yalesites:agent
surface: ticket-comment
kind: design-handoff
ticket: <owner/repo#N>
-->
```

## Storybook docs page

Model: the Event Calendar compact list design's "States and handoff details" page. Most
component-library-twig docs pages today (for example `03-organisms/calendar/calendar.mdx`) are a
canvas, controls and a props table. Those stay; this adds the parts a future maintainer needs
and cannot read off the code. Write it as MDX the developer can drop next to the component's
stories. Use plain prose and tables. Show states with the real stories (`<Canvas of={...} />`),
not with images, so the page stays true as the component changes. Pages attached to a stories
file always use `name="Overview"`, per component-library-twig's
`components/00-introduction/storybook-guide.mdx`.

```mdx
import { Meta, Canvas, Controls } from '@storybook/blocks';
import * as Stories from './<component>.stories';

<Meta of={Stories} name="Overview" />

# <Component>

<One paragraph: what it is and the problem it solves for an editor.>

## Built from
<Its atomic level (molecule or organism), then the atoms and molecules it composes, each linked
to its own docs page. Any piece added for this component says so.>

## When to use it
- Use it for <case>. Use <other component> instead when <case>.

## Anatomy
<Numbered parts, matching a labeled story or diagram.>

## Allowed regions
| Region | Behavior |
|---|---|
| One column | <...> |
| Sidebar (305px at 1440) | <what stacks or hides> |

## States
| State | What changes | Contrast |
|---|---|---|
| Default | | |
| Hover | | |
| Keyboard focus | 2px Medium Blue ring | 5.2:1 |
| Empty | | |

<Canvas of={Stories.<States story>} />

## Accessibility
- Keyboard focus order: <1, 2, 3...>
- Screen reader labels: <e.g. "Wednesday, October 28, 4 events">
- No state depends on color alone: <how each is also shown>
- Motion: <respects prefers-reduced-motion>

## Theming
<Which theme slots it reads, and the themes it was checked in.>

## In Layout Builder
<The block form: each option with one sentence an editor understands, and the defaults.>

## Do and don't
- Do <...>.
- Don't <...>.

## Interactive preview
<Canvas of={Stories.<Default>} />
<Controls of={Stories.<Default>} />

## Properties
<The existing props table, unchanged.>
```

Every number in the States table comes from the signed-off mockups. A contrast ratio that fails
AA is a token pairing problem to fix before handoff, not a note to leave in the docs.

A new atom or molecule in the inventory gets its own short docs page too, in its own folder, so
the next block that reuses it can find it.
