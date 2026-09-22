# ASD-STE100 for YaleSites pages

[ASD-STE100](https://www.asd-ste100.org/) is a controlled-English standard from aerospace maintenance documentation. YaleSites uses it because the audience overlaps in the way that matters: someone consulting the manual under time pressure, worried about breaking something expensive, who needs to parse a sentence right the first time.

You are not being graded against the full specification. These are the rules that change the writing.

## Sentence and paragraph rules

- **Procedural sentences: 20 words maximum.** Instructions, steps, anything with an imperative.
- **Descriptive sentences: 25 words maximum.** Explanations and overviews.
- **One instruction per sentence.** Two actions means two sentences, even when they always happen together.
- **One topic per paragraph.** Procedural paragraphs stay under six sentences.
- **Start a procedural sentence with the verb.** "Select Save configuration to apply your changes."

## Grammar rules

- **Active voice.** "The platform creates the tag" beats "the tag is created."
- **Simple present tense** for how things behave. Reserve future tense for genuinely future events.
- **Keep articles.** "Select the title" not "Select title." Dropped articles read as terse and ambiguous.
- **Don't drop the verb.** No headline-style fragments in body copy.
- **Noun stacks: three words maximum.** "Announcements cache lifetime setting" is at the edge; rewrite as "the cache lifetime for announcements."
- **One word, one meaning.** If you call it a "section" once, it stays a "section." Don't rotate through section/area/panel/region for variety.
- **Write positive instructions.** "Keep this setting on" beats "Do not turn this setting off." Reserve negatives for real warnings.

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

Also avoid: circle back, touch base, move the needle, alignment, synergy, value-add, deliverables (unless literally correct).

## Software-specific conventions

STE predates web UI, so a few adaptations:

- **"Select"** for clicking a control. Stay consistent rather than alternating with "click," "choose," and "press."
- **"Open"** for navigating to a page.
- **Bold** for exact on-screen labels: Select **Save configuration**.
- **Backticks** for paths and URLs: `/admin/yalesites/dashboard`.
- Skip "please." It adds a word without adding meaning.

## What STE does not override

- **No em dashes.** This rule outranks everything else here. Use a comma, a period, a colon, parentheses, or restructure.
- **"We" for the YaleSites team.** Never "I," unless the user's own writing-voice preferences say otherwise.
- **Warmth is still allowed.** STE constrains sentence construction, not friendliness. "Do you have a question about the Dashboard? Come to Office Hours" is fine and better than a colder equivalent.

## Checking your work

Run `check-github-text.py --surface page-draft`. Sentence-length violations are easy to miss by eye, especially in bullets, where a long parenthetical can push you past 20 words without the line looking long.

The script flags candidates, not verdicts. A 22-word descriptive sentence is fine. A 22-word instruction is not.
