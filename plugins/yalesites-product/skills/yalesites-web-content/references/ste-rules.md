# ASD-STE100 for YaleSites pages

Page copy follows the same Simplified Technical English rules as every other YaleSites artifact. Those rules live in one place: the shared YaleSites writing standard, which this plugin ships at `../../ticket/references/github-writing.md`. Read its "Sentence rules" and "Word swaps" sections before drafting. The checker enforces that word-swap table, so it is the only copy.

This file holds only what is different about a page on yalesites.yale.edu.

## The full rule set applies to all page copy

The shared standard relaxes the sentence-length caps and the one-instruction rule for arguments inside a collapsed `<details>` block. A page has no collapsed layer, and nearly everything on it is something a reader acts on. So everything under `## Page copy` gets the full rule set, with no relaxation:

- **Procedural sentences: 20 words maximum.** Instructions, steps, anything with an imperative.
- **Descriptive sentences: 25 words maximum.** Explanations and overviews.
- **Procedural paragraphs stay under six sentences.**

The per-surface budgets, TL;DR rules, and `<details>` layering in the shared standard are GitHub rules. They do not apply to pages.

## Tense

Use the simple present tense for how things behave: "The Dashboard shows your unpublished pages." Reserve future tense for genuinely future events, such as a feature that ships in a later release.

## Software-specific conventions

STE predates web UI, so a few adaptations:

- **"Select"** for clicking a control. Stay consistent rather than alternating with "click," "choose," and "press."
- **"Open"** for navigating to a page.
- **Bold** for exact on-screen labels: Select **Save configuration**.
- **Backticks** for paths and URLs: `/admin/yalesites/dashboard`.
- Skip "please." It adds a word without adding meaning.

## Voice and warmth

The shared standard's "What this does not override" section applies here too: no em dashes, a personal writing-voice skill on top of STE where one is installed, and warmth still allowed. Two page-specific notes:

- **Without a voice skill, default to "we"** for the YaleSites team, never "I." The PR-review exception in the shared standard does not apply to pages.
- **Warmth fits support moments best.** "Do you have a question about the Dashboard? Come to Office Hours" is fine, and better than a colder equivalent.

## Checking your work

Run `check-github-text.py --surface page-draft`, as described in Step 5 of the skill. Sentence-length violations are easy to miss by eye, especially in bullets, where a long parenthetical can push you past 20 words without the line looking long.

The script flags candidates, not verdicts. A 22-word descriptive sentence is fine. A 22-word instruction is not.
