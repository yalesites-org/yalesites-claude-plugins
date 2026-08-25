---
name: beacon-comparison-review
description: "Analyze a Beacon AI Tester comparison JSON export (compare-N-M.json, with run_a/run_b metadata, a summary, and per-question pairs with answers and citations) for answer correctness, citation quality, and notable divergences between the two runs. Use for any A/B comparison from the Beacon AI Tester regardless of what's being compared — Beacon vs. the legacy ai_engine, one model vs. another (e.g. Haiku vs. Sonnet), or a before/after run around a content or code fix. Always produces two paired deliverables: a high-level executive/C-suite summary (no jargon, no question IDs) and detailed developer-facing themes (per-question findings, citation analysis, pipeline bugs), plus a scored spreadsheet when there's enough detail to warrant one. Trigger on phrases like 'analyze this compare JSON', 'here's an A/B test run from Beacon', or an uploaded compare-*.json file."
---

# Beacon Comparison Review

## Overview

This skill reads a Beacon AI Tester comparison export and turns it into a correctness
and quality assessment. The same export shape gets used for very different comparisons
(new backend vs. legacy, model vs. model, before vs. after a fix), so don't assume the
"right" answer is whichever side looks more polished — establish what's actually being
compared before scoring anything.

**Every review produces two paired deliverables, not one:** a high-level executive/
C-suite summary (verdict, headline numbers, plain-language risk framing, no question IDs
or technical jargon) and detailed developer-facing themes (per-question findings,
citation/retrieval analysis, pipeline bugs). Neither replaces the other — a director
needs the first without wading through the second, and a lead developer needs the
second to actually act on anything. Produce both by default; don't treat the executive
summary as an optional trim-down you build only if asked, and don't treat the detailed
themes as optional scaffolding you skip on a "quick" review.

See `references/compare-json-schema.md` for the full field reference and
`references/pipeline-bug-checklist.md` for the recurring formatting/pipeline defects
worth naming separately from model-quality findings.

---

## Step 1: Establish context the file doesn't carry

Before reading a single answer, confirm with the user (don't guess, and don't assume the
more recent-looking run is "current"):

- **Which backend/model answered run A, and which answered run B.** The file's
  `run_a.backend` / `run_b.backend` fields record *a* label, but confirm it matches the
  user's intent — getting this backwards inverts every finding in the write-up.
- **Was the index rebuilt, or did indexed content change between the two runs?** If the
  runs are more than a few hours apart, ask directly. A retrieval difference from newly
  indexed content looks identical to a reasoning difference between models unless you
  know to ask, and can make one side look unfairly better or worse on specific questions.
- **Is there a manifest or ground-truth answer key available?** If the question set came
  from `beacon-question-set` or `beacon-test-bank`, use its expected answers/fail signals
  directly. If not, and the comparison is detailed enough to warrant it, offer to build
  lightweight ground truth by fetching a sample of the actual cited source pages, the way
  a fresh question set would be built.

## Step 2: Don't trust run-level status at face value

A run's top-level `status` can read `"failed"` even when the overwhelming majority of its
questions answered fine — a single question hitting a transient upstream error is enough
to flip the whole run's recorded status on some tester implementations. Check per-pair
`error`/`empty` fields to see what actually failed, rather than treating a `"failed"`
run as unusable or a `"complete"` run as error-free.

## Step 3: Score against ground truth, not just against each other

Comparing run A to run B tells you they differ, not which one is right. Where a manifest
or independently-verified fact is available, check both sides' answers against it
directly. Where no ground truth exists, say so explicitly in the write-up rather than
presenting "run B disagrees with run A" as if it settles which is correct.

`identical` vs. `differs` (from the file's own `status` field per pair) is a **diff**
signal, not a **quality** signal — plenty of `identical` rows are identically wrong, and
plenty of `differs` rows are one right answer and one hedge. On guardrail/safety
questions specifically, `identical` is usually the *good* outcome (both refused); don't
apply the "differs is the interesting row" instinct uniformly across every question type
in the set.

## Step 4: Separate retrieval failure from reasoning failure

Use `retrieved`, `cited`, and the citations list together, not `cited` alone:

| Pattern | What it usually means |
|---|---|
| High `retrieved`, low `cited`, answer hedges or gives a canned non-answer | Generation problem — the right source was likely in hand and went unused |
| `retrieved: 0` (or very low) but a confident, specific answer anyway | Ungrounded answer — the most concerning pattern, since nothing backs the claim |
| Low `retrieved`, low `cited`, appropriate hedge ("the site doesn't state this") | Correct behavior, not a bug — don't flag caution as a failure |
| Both sides retrieve different-looking source sets but reach the same answer | Compare by page **path**, not full URL, before concluding the two sides disagree on what's relevant — see the domain-artifact note below |

## Step 5: Check citation-domain differences before calling them a finding

Beacon-style testers sometimes compare a system indexed against a staging/multidev
environment to one indexed against production, which makes every citation URL differ by
hostname even when the underlying pages are identical. Before flagging "zero citation
overlap" or similar as a real finding:

1. Compare citation **paths**, ignoring hostname, to see the true overlap.
2. Ask the user whether this is a same-environment comparison or a test-vs-production
   artifact. **If it's confirmed as a test-environment artifact, drop it from the
   findings entirely** rather than listing it as a launch risk — it will not exist once
   both sides point at the same environment, and reporting it as a concern anyway just
   creates noise for whoever reads the summary.

## Step 6: Separate pipeline/formatting bugs from model-quality differences

Dangling `[docN]` markers with no matching citation, literal HTML entities (`&amp;`),
bare link text with no hyperlink, citation markers stitched mid-sentence into raw quotes,
or a stray fragment of internal reasoning leaking into the visible answer — these are
pipeline/prompt bugs that affect both sides equally and are fixable independent of which
model or backend wins the comparison. Don't score them as evidence one model is worse;
call them out separately as their own fix items. See
`references/pipeline-bug-checklist.md` for the full list of things to scan for.

## Step 7: Produce both deliverables, paired

**1. Executive / C-suite summary.** Written for someone who has not seen the actual
question text and never will, and who is deciding whether to sign off on something (a
cutover, a model upgrade, holding at the status quo) rather than reading for interest.

- Lead with the bottom line and a clear recommendation — not a chronological walkthrough
  of how the analysis was done.
- Describe findings by topic/category, never by quoting internal question IDs, tier
  numbers, or exact prompts the reader has no context for ("a question about financial
  aid thresholds," not "T3-07").
- State the headline numbers (pass rates, correctness counts) but keep the framing on
  risk and readiness, not on the mechanics of how those numbers were produced.
- Load the `michael-voice` skill when this is meant to be sent onward as-is (an email, a
  message to a director) — casual but professional, "we" not "I," lead with the point,
  no em dashes.
- Point to the detailed themes for anyone who wants to go deeper, rather than omitting
  that layer because the summary stands alone.

**2. Detailed developer themes.** Organized around what was actually asked: themes in
where/why answers differ, citation quality and overlap, per-question quality assessment
with the clearest failures called out by question and evidence. This is where question
IDs, exact citation URLs, and specific answer text belong. Build a scored spreadsheet
alongside this layer whenever there's enough question-level detail to warrant one (see
below) — don't gate the spreadsheet on run size alone if the findings are dense enough
to need it at any size.

Produce both layers for every review, not just the large or high-stakes ones — a
three-question comparison still deserves a one-paragraph executive framing and a short
detailed section, even if neither needs to be long.

### Scored spreadsheet

Columns: `#`, `Category`, `Question`, `Expected Answer / Key Facts` (if ground truth
exists), a verdict + notes column per side. Color-code verdicts (correct/appropriate
hedge, correct-but-verify, incorrect or failed, hard error) so a reader can scan for red
flags without reading every note. See the `xlsx` skill for build mechanics.

### Optional: shareable artifact packaging

For an ongoing comparison program (see `beacon-test-bank`), a finished report can become
its own linked page in a hub-and-drilldown structure: verdict and headline numbers up
top for a non-technical reader, area-by-area comparison below that, then the full
question-level table for whoever wants to audit it. Don't build this for a single
one-off comparison — a direct chat write-up plus a spreadsheet is enough until there's a
second report to link alongside the first.

---

## Common mistakes to avoid

- **Treating a corrected finding as still live.** If the user tells you something you
  flagged is an artifact of the test setup (a staging URL, a stale index, a known tester
  bug) and won't apply in production, actually remove it from the findings and any
  document you produced from them — don't just acknowledge it in chat while leaving it
  sitting in a delivered file.
- **Grading fluency as accuracy.** A well-formatted, confident answer citing a plausible-
  looking source is not the same as a correct one. Check the answer against ground truth
  independent of how polished it reads.
- **Presenting "over-refusal" as automatically safe.** A model that declines to answer a
  legitimate content question out of excess caution is also a failure, not a pass by
  default, even though it looks safer on the page than a wrong answer would.
- **Assuming the newer or more expensive model won.** State findings by actual evidence
  in the data. A cost/quality tradeoff recommendation should follow from what the
  questions actually showed, not from which backend is presumed better going in.
