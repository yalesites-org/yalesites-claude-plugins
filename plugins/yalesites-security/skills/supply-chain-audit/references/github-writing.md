# YaleSites GitHub Writing Standard

Canonical source. Do not edit the synced copies inside `plugins/`. Edit this file, then
run `bash scripts/sync-standards.sh`. CI fails if a synced copy drifts from this one.

Companion file: `github-communication-format.md` governs **structure** (what is visible,
what is collapsed, what is machine-only). This file governs **words**.

## The problem this solves

Tickets and PRs written with agent help have been coming back as too long and too dense.
The cause is not that the analysis is wrong. It is that the analysis is in the reader's
way. A site owner opening a ticket wants one sentence. A PM skimming a review wants the
verdict. Neither wants to scroll past a platform-fit assessment to find it.

So we do not cut the depth. We move it, and we tighten the words that remain.

## Two standards, two jobs

**[ISO 24495-1](https://www.iso.org/standard/78907.html)** (Plain language, 2023) sets the
document-level test. Four questions to ask of any artifact before posting:

| Principle | The question |
|---|---|
| Relevance | Does the reader get what they need? |
| Findability | Can they find it without scrolling or expanding? |
| Comprehensibility | Can they understand it on the first read? |
| Applicability | Can they act on it? |

**[ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/)** sets the
sentence-level rules. It is a controlled-English standard from aerospace maintenance
documentation. Issue 9 (January 2025) has 53 writing rules in 9 sections, about 900
approved words, and about 1,200 unapproved words with suggested replacements.

We use it because the audience overlaps in the way that matters: someone reading under
time pressure, worried about breaking something, who needs to parse a sentence right the
first time.

> **On the specification itself.** ASD-STE100 is free to download and is copyrighted by
> ASD. This file paraphrases the rule categories that change our writing and carries our
> own word-swap table. It does not reproduce the specification text or its dictionary.
> Keep it that way.

## Sentence rules

These are the STE rules that carry weight for GitHub artifacts.

- **Procedural sentences: 20 words maximum.** Acceptance criteria, testing steps, anything
  with an imperative.
- **Descriptive sentences: 25 words maximum.** Descriptions, rationale, release notes.
- **One instruction per sentence.** Two actions means two sentences, even when they always
  happen together.
- **Start a procedural sentence with the verb.** "Open the Layout Builder and add an Image
  block."
- **One topic per paragraph.** Six sentences maximum, fewer for procedures.
- **Active voice.** "The release adds a caption field" beats "a caption field was added."
- **Simple tenses only.** "We changed the label," not "we have changed the label."
- **Keep articles and verbs.** "Select the title field," not "Select title field." Dropped
  words read as terse and ambiguous, not as brief.
- **Noun stacks: three words maximum.** "Announcements cache lifetime setting" is at the
  edge. Write "the cache lifetime for announcements."
- **No semicolons.** Use two sentences.
- **One word, one meaning.** If it is a "block" once, it stays a "block." Do not rotate
  through block, component, element, widget for variety.
- **Write positive instructions.** "Keep this setting on" beats "Do not turn this setting
  off." Reserve negatives for real warnings.

## Word swaps

| Instead of | Use |
|---|---|
| utilize, leverage | use |
| ensure | make sure |
| in order to | to |
| prior to | before |
| subsequent to, following | after |
| approximately | about |
| additional | more |
| assist | help |
| attempt | try |
| commence, initiate | start |
| terminate | stop, end |
| require | need |
| obtain | get |
| via | with, by |
| regarding, concerning | about |
| numerous, multiple | many |
| modify | change |
| indicate | show |
| permit | let |
| sufficient | enough |
| facilitate | help, make easier |
| endeavor | try |
| aforementioned | this, that |
| in the event that | if |

Also cut: circle back, touch base, move the needle, alignment, synergy, value-add, robust,
seamless, holistic, deliverables (unless literally correct).

Two habits specific to agent-written text, both worth deleting on sight:

- **Throat-clearing openers.** "It is worth noting that," "I want to highlight that," "As
  discussed above." Start with the thing.
- **Restating the ask before answering it.** A ticket does not need a paragraph describing
  the request before describing the work.

## Where STE stops

STE was built for procedures, not for argument. A PR review explaining why an approach is
wrong is not a maintenance step, and forcing it into 20-word imperatives makes it worse.

Apply the full rule set to: acceptance criteria, testing steps, TL;DR lines, release notes,
and any numbered list a person works from.

Apply the word swaps, the active voice, the tense rules, and the noun-stack cap everywhere,
including rationale. Relax only the sentence-length caps and the one-instruction rule when
writing an argument, and then only inside a collapsed block.

## Per-surface rules

Budgets are for the **always-visible** layer only. Text inside `<details>` is not counted,
because a person chose to open it. This is the whole point: depth is free once it is out of
the way.

| Surface | TL;DR | Visible budget | Never collapse |
|---|---|---|---|
| Ticket (`ticket`, `ticket-sync`) | 60 words | 400 words | Description, Acceptance Criteria |
| PR body (`yalesites-pr`, `pr-description`) | 60 words | 350 words | H2 link line, Description of work, testing steps, trailing `References` lines |
| PR review (`pr-feedback`) | 60 words | 250 words | The numbered blocking items, one line each |
| Release notes (`release-prep`) | 80 words | 500 words | Featured Feature |
| Report (`beacon-comparison-review`, `supply-chain-audit`) | 80 words | 600 words | Findings that need action, severity-ordered |

Surface-specific notes:

**Tickets.** The reader is often non-technical. No Drupal jargon in the TL;DR or the
Description. Acceptance criteria are procedural, so hold them to 20 words each. One
criterion per bullet. If a bullet needs an "and," it is two criteria.

**PR bodies.** The reader is a developer peer, so normal technical vocabulary is fine. The
word swaps still apply. Do not narrate the diff: the diff is already there. Say what
changed and why, and put the change-by-change walkthrough in a collapsed block.

**PR reviews.** First person singular ("I"), not "we." This overrides any writing-voice
skill's default person. Every blocking item is one line: what to change, which file. The
reasoning goes in a collapsed block. Do not soften a blocking item into a suggestion, and
do not inflate a suggestion into a blocker.

**Release notes and reports.** The widest and least technical audience we write for. Lead
with what changed for the reader, not with what the team did. "Galleries now accept alt
text" beats "we implemented an alt-text field on the gallery paragraph."

## What this does not override

- **No em dashes.** This rule outranks everything else here. Use a comma, a period, a
  colon, parentheses, or restructure the sentence.
- **Voice skills.** If the person running the skill has a personal writing-voice skill,
  apply it on top of these rules. `michael-voice` applies where it exists: "we" for the
  team, not "I," except on PR reviews as noted above.
- **Warmth.** STE constrains sentence construction, not friendliness. A question, an offer
  of help, or a thank-you is still fine. It just gets a short sentence.

## Checking your work

Run the bundled checker before posting:

```bash
python3 scripts/check-github-text.py draft.md --surface ticket
```

Surfaces: `ticket`, `pr-body`, `pr-review`, `release-notes`, `report`.

The checker flags candidates, not verdicts. A 22-word descriptive sentence is fine. A
22-word acceptance criterion is not. It only measures the visible layer, so a long
collapsed block is never a finding.
