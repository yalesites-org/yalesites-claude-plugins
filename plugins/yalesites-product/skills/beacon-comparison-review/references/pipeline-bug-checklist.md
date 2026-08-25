# Pipeline/formatting bugs to scan for

These recur across model and backend comparisons because they're artifacts of the
retrieval-augmented-generation pipeline itself (prompt construction, citation
extraction, index conversion), not of any particular model's reasoning. When found,
report them as their own fix items rather than folding them into "model A is better than
model B" — they typically affect both sides, or would affect whichever side hits the
same code path.

- **Dangling citation markers.** The answer references `[doc4]` or `[doc5]` but only 3
  citations came back in the `citations` array. Suggests the generation prompt is being
  shown more documents than the citation-building step records, so those markers point
  at nothing clickable in the rendered answer.
- **HTML entity leaks.** Literal `&amp;`, `&quot;`, etc. rendering in the visible answer
  text instead of being decoded.
- **Bare link text with no hyperlink.** A phrase like "check out this resource: Video
  Block or Video Banner Block" or "👉 Site Request Forms" where a real link was clearly
  intended but never rendered as one.
- **Citation-marker-before-quote stitching.** Answers that read like a search-result
  dump — `[doc2] The platform is designed so that [doc2] "every component..."` — with the
  marker placed before each quoted fragment repeatedly, rather than paraphrased prose
  with the marker placed naturally at the end of a sentence.
- **Internal reasoning leaking into the visible answer.** A fragment like "...upgraded
  modules to keep the platform current with Drupal `[doc1... wait, correcting]`..."
  appearing in user-facing text. Usually a one-off rather than systemic, but worth
  flagging even from a single occurrence since it's the kind of thing that looks
  unprofessional on a public-facing assistant.
- **Indexed content carrying stripped-attribute text.** Image `alt` text or an embed's
  `title` attribute showing up as citable/answerable content when it should have been
  excluded from indexing (or, conversely, a heading that legitimately renders as visible
  page text getting mistaken for a leak — check the actual page markup before concluding
  either way).
- **Canned/generic failure responses despite sources retrieved.** A boilerplate line like
  "The requested information is not available in the retrieved data" when `retrieved` is
  non-trivial (5+) and the fact is verifiably on one of those pages. This is a generation
  problem, not a data gap — the answer-generation step gave up rather than the retrieval
  step failing to find anything.

None of these require a manifest or ground truth to catch — they're visible directly in
the answer text and the citations array. Scan for them on every comparison, even a quick
one.
