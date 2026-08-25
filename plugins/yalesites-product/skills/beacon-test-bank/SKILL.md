---
name: beacon-test-bank
description: "Build or extend the full tiered Beacon test bank: a persistent, versioned question set covering content knowledge, whether Beacon knows its limits, guardrails/injection/jailbreak safety, and real-use robustness, backed by a manifest (question ID, tier, expected answer, fail signals) and a single canonical upload file. Use when the user wants to test Beacon 'to its limit', build a comprehensive/tiered question bank, add guardrail or jailbreak test questions, construct custom test PDFs or pages to probe a specific platform bug (chunking, citation links, indexing), or maintain an ongoing test bank across multiple model/backend comparisons. For a quick content-only spot-check with no guardrail testing, use beacon-question-set instead."
---

# Beacon Tiered Test Bank

## Overview

This is the heavyweight of the two question-set skills: a persistent, versioned test
bank meant to be reused across many comparison runs (model swaps, index rebuilds, bug
fixes), not a one-off list. It has more moving parts than `beacon-question-set` on
purpose — a manifest, tiers, and sometimes custom test content — because the questions
themselves aren't self-describing once you're slicing them by category after the fact.

Reach for this skill when the user says something like "test the bot to its limit,"
wants guardrail/jailbreak coverage, wants the set to persist and grow across releases,
or needs to verify a specific platform bug fix (e.g. a chunking or indexing change) with
purpose-built content. If they just want a fast content spot-check for one site with no
safety testing, use `beacon-question-set` instead — don't over-engineer that use case.

See `references/tier-taxonomy.md` for the coverage-bucket/tier structure and the
manifest schema.

---

## Step 0: Ask what kind of coverage is actually wanted

Don't default to building all four buckets. Sometimes the ask is genuinely "test the
guardrails" and nothing else; sometimes it's "we just want extensive content coverage,
no safety testing." If the user's initial prompt already states this clearly, don't
re-ask — proceed with what they said. Otherwise, use `AskUserQuestion` before doing any
research or drafting:

- **Guardrail/safety only** — testing the Beacon technology itself (injection,
  jailbreak, credential/secret requests, scope boundaries). No content-accuracy
  questions.
- **Extensive content coverage only** — factual questions from pages, PDFs, and other
  indexed documents. No guardrail/safety questions. (If this is *all* that's wanted and
  guardrails are explicitly out of scope, `beacon-question-set` may be the better fit —
  point that out rather than building the heavier manifest/tier apparatus for a
  content-only ask.)
- **Full tiered bank** — all four buckets: content knowledge, knows its limits,
  guardrails/safety, and real-use robustness.
- **Something narrower** — e.g. only the "knows its limits" bucket, or only a specific
  platform bug's custom test content. Let the user name it rather than assuming.

This decision changes which buckets get built and whether guardrail questions belong in
the set at all — get it settled before spending research effort.

---

## The one rule that overrides everything else: ship ONE flat file

**Always maintain a single `.txt` upload file for the whole bank, never split it into
subset files** ("core", "tier-3-only", "A/B set", etc.), even though the manifest makes
those subsets easy to imagine as separate uploads.

Why this isn't just tidiness: the tester pairs run A to run B **by exact trimmed
question text**, not by line number or upload order. If one run uploads a 40-question
subset and a later run uploads the full 104-question bank, the 64 questions missing from
the first run come back as `only_b` instead of a real comparison — the signal you
wanted gets buried in noise you created yourself. Two different subset files can never
be cross-compared cleanly, and that constraint is easy to forget weeks later when you're
staring at a confusing run list.

Slicing belongs at **analysis time**, as a filter over the manifest (by tier, by
`core`/`ab` flag, by bucket), never at **file-creation time**. You get every useful
subset for free from one full run, at the cost of a longer run — and file size is
essentially never the constraint (a bank of a hundred-plus questions is a few KB against
typical upload limits).

---

## The manifest

Every question bank needs a companion manifest — a JSON file mapping exact question
text to everything a human or a later analysis pass needs to grade it. Without this, a
comparison export tells you two runs differ but nothing about which one is right.

See `references/tier-taxonomy.md` for the full schema. Minimum required fields per
question: `id`, `tier`, `bucket`, `question` (exact text, byte-for-byte what's in the
upload file), `expected_answer`, `fail_signals`, `in_tester` (false for anything that
can't run through a single-turn tester).

**Question IDs** use a `T<tier>-<number>` scheme (e.g. `T7-02`, `T12-05`) so a question
can be referenced precisely in conversation without pasting its full text.

---

## Coverage buckets

Organize questions into four buckets (tiers nest inside these — see the reference file
for a worked example from an actual bank):

1. **Does it know our content** — straightforward factual retrieval, the same spirit as
   `beacon-question-set` but folded into the larger bank with IDs and manifest entries.
2. **Does it know its limits** — questions whose correct answer is "I don't know" or a
   redirect, because the fact genuinely isn't in the indexed content. Answering
   confidently here is the failure, not answering vaguely.
3. **Is it safe** — guardrails, prompt injection, jailbreak attempts, requests for
   credentials/secrets, requests to leak system instructions. See "Reading guardrail
   results" below before scoring these.
4. **Does it hold up in real use** — multi-part questions, ambiguous phrasing, questions
   that require picking the right row out of two similar options, deeply nested content,
   off-topic redirects, and anything probing a specific known platform bug.

---

## Reading guardrail results (don't apply the default heuristic here)

For ordinary content questions, `differs` between two runs is the interesting row and
`identical` is uninteresting. **This inverts on guardrail/safety questions**: two
identical refusals is the desired outcome, and a model that suddenly answers what the
other one declined is the finding worth flagging. Don't let a "differs = interesting"
scan skip past guardrail rows just because they show up as `identical`, and don't treat
an `identical` refusal as a boring row to skip.

Also distinguish *where* a refusal happened. A hard 400/error from the backend on an
overt jailbreak prompt (an upstream content filter rejecting the request before the
model ever saw it) is a different mechanism than the model itself declining in-band with
a clean redirect. Both can be defensible, but they're not the same behavior, and an
export recording the run as "failed" because of the former shouldn't be misread as the
model failing to hold the line.

---

## Multi-turn questions can't run through the tester

The tester sends one line at a time with no conversation state. Any question that
depends on a follow-up turn (a clarifying question, a "no, the other one" correction)
cannot be evaluated this way. Tag these `in_tester: false` in the manifest, leave them
out of the `.txt` upload entirely, and flag them for the user to run by hand in the live
chat widget instead.

---

## Sourcing PDF/document content (when content coverage is in scope)

If the requested coverage includes documents and not just web pages, don't assume a
sitemap crawl surfaces them. A sitemap generally only lists the site's own pages — PDFs
linked *from* those pages usually aren't enumerated there, and even when you do find a
PDF's URL by crawling links, finding the link tells you nothing about whether that
specific file is actually indexed for AI/Beacon retrieval in Drupal. A PDF can be linked
on a page and still be entirely outside the search index.

Work through this in order:

1. **Look for obviously-linked PDFs** while sampling pages for content questions, but
   treat anything found as a lead, not a confirmed indexed source.
2. **If you don't find any, or can't confirm indexing status, ask the user directly:**
   do they have specific PDFs they know are indexed in Drupal for AI analysis? Get the
   exact links or files from them rather than guessing from what a page happens to
   link to.
3. **If they don't have any real ones on hand, ask whether they want dummy/synthetic
   test PDFs drafted instead.** This is sometimes genuinely needed — testing whether
   Beacon can find and cite document content at all, or verifying chunking/retrieval
   behavior specific to PDFs, requires content that provably isn't available anywhere
   else on the site (see the decoy-fact guidance below). But it's not always needed —
   if the ask is pure page-content coverage, skip this step entirely rather than
   manufacturing document-testing scope nobody asked for.

Don't silently skip document coverage just because a sitemap crawl came up empty, and
don't silently invent test PDFs either — both are a reason to ask, not to guess.

---

## Building custom test content for a specific platform bug

Some tiers exist to verify a specific code or content-pipeline fix (e.g., an
HTML-to-Markdown chunking change, a citation-link precedence question, an indexing
behavior). The site's real content usually can't test this precisely, so build dedicated
content instead:

- **Use real structure, not pasted text.** If testing how CKEditor tables, headings, or
  links survive into a chunk, build them as real CKEditor elements — a heading block, a
  real table, a real Linkit-inserted internal link. Pasted plain text or a hand-written
  anchor tag in source view can skip the exact code path you're trying to exercise.
- **Pick decoy facts/links with exactly one explanation if they leak.** If checking
  whether an answer cites the right page versus reaching into an in-body link, point that
  in-body link at content with zero legitimate connection to the question being asked —
  a generic unrelated demo page, not a real page that could plausibly be cited for other
  reasons. If it shows up in the answer, there's only one explanation, not three you now
  have to rule out.
- **Put the interesting content in the structurally awkward spot on purpose.** If testing
  retrieval depth, put the fact in the last section of the page/document, since retrieval
  and chunking both tend to get thin toward the end.
- **Confirm the "before" state actually predates the fix.** If this is a before/after
  test for a code change, verify the target environment is genuinely running pre-fix code
  before calling a run the baseline — ask a control question whose answer is known to
  differ once the fix lands, and check it before starting the real run.
- **Confirm every intended document actually indexed.** Ask something with an answer
  that exists in exactly one uploaded document and nowhere else, and check that both
  models retrieve it before trusting a "no answer" result as meaningful for that
  document's tier.

---

## Before starting any comparison run

Ask the user (the export doesn't record this):
- **Which backend/model answered which run** — the file records `backend` per run, but
  not the user's intent, and getting run A and run B backwards inverts every finding.
- **Was the index rebuilt, or did the content/documents change between runs?** A
  retrieval difference caused by new content indexed between runs looks identical to a
  reasoning difference between models unless you know to ask.

---

## Packaging as a shareable artifact (optional)

For an ongoing program meant for a mixed audience (a lead developer who wants question-
level detail, a director who wants a one-screen verdict), consider a two-layer artifact
structure rather than a single flat page:

- **A hub page** — what the testing program is for, the coverage buckets at a glance,
  and links to finished comparison reports. Keep it to about a screen and a half; a
  non-technical reader should never need to learn the word "tier" to understand it.
- **A question-bank page**, linked from the hub, for whoever wants to see every question.
- **One page per finished comparison run**, also linked from the hub, each following the
  pattern in `beacon-comparison-review`: verdict and headline numbers up top, then
  detail below.

Don't build this scaffolding for a single one-off comparison — it earns its keep once
there's a second and third run to link alongside the first.
