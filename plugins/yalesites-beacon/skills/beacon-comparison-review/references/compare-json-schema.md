# Beacon AI Tester comparison JSON — field reference

Top-level shape of a `compare-N-M.json` export:

```json
{
  "run_a": { "id": 1, "created": 1787582755, "source_filename": "typed-questions.txt", "status": "failed", "backend": "beacon" },
  "run_b": { "id": 2, "created": 1787582755, "source_filename": "typed-questions.txt", "status": "complete", "backend": "legacy" },
  "summary": { "total_compared": 67, "differ": 67, "identical": 0, "only_a": 0, "only_b": 0 },
  "pairs": [ /* one entry per question */ ]
}
```

## `run_a` / `run_b`

Metadata for each run: `id`, `created` (Unix timestamp), `source_filename`, `status`,
and `backend` (a label for which assistant/model answered). **`status` can read
`"failed"` even when only one question in a long run hit a transient upstream error** —
don't treat a `"failed"` run as uninterpretable; check the individual pairs.

## `summary`

Counts across the whole comparison: `total_compared`, `differ`, `identical`, `only_a`
(question only present in run A), `only_b` (question only present in run B). `only_a`/
`only_b` usually mean the two uploads didn't contain the exact same question text —
see `beacon-test-bank`'s single-file rule for why that happens.

## `pairs[]`

One entry per question:

- **`question`** — the question text, identical on both sides (this is the pairing key).
- **`status`** — `identical`, `differs`, `only_a`, or `only_b`. A diff signal, not a
  quality signal — see the main skill file for how this reads differently on guardrail
  questions.
- **`a` / `b`** — that question's result on each side, or `null` when not asked in that
  run. Each side has:
  - `answer` — the answer text. May contain inline `[docN]` markers, which are the
    assistant's own references to its retrieved sources — treat them as citation
    references, not prose, and don't use a marker's number as an index into `citations`
    (the numbering schemes don't necessarily match).
  - `citations` — one entry per retrieved source: `number`, `title`, `url`, `excerpt`
    (first ~300 characters only — don't assume you have the full page from this), `cited`
    (bool: whether the answer actually referenced this source; `false` is normal
    retrieval behavior, not a fault by itself).
  - `len` — answer length in characters.
  - `cited` — count of sources the answer referenced.
  - `retrieved` — count of sources retrieved for the question.
  - `empty` — bool.
  - `error` — non-empty only when that side failed to answer (check this per-question
    rather than trusting the run-level `status`).
- **`len_delta`** — run B's answer length minus run A's; `0` when the question was only
  asked in one run.
- **`citation_overlap`** — `{both, only_a, only_b}`, each a list of `{url, title}`,
  partitioning the two sides' sources **by full URL**. If the two runs point at different
  hostnames (a staging multidev vs. production, for example), this will read as near-zero
  overlap even when the underlying pages are the same — always cross-check by URL *path*
  before treating a low overlap number as a real content-divergence finding, and confirm
  with the user whether it's a same-environment comparison before reporting it either way.

## Things this file does NOT tell you

- Which backend/model the user *intended* for each run (only a label).
- Whether the index or indexed content changed between the two runs.
- Whether a manifest/ground-truth answer exists for grading correctness — that has to
  come from the question set itself (see `beacon-question-set` / `beacon-test-bank`) or
  be built fresh by checking the actual source pages.

Always ask for the first two rather than inferring them from filenames or timestamps.
