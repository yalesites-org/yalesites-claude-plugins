---
name: beacon-question-set
description: "Build a quick, content-accuracy-only question set for testing Beacon (or the legacy ai_engine) against one site's published content, exported as an upload-ready .txt plus a QA tracking spreadsheet. Use when the user wants to spot-check whether Beacon answers factual questions correctly, e.g. 'make a question set to test Beacon against college.yale.edu', 'give me 50 questions to run against the tester', 'build a test set from this sitemap' — always when they say something like 'we don't need to test guardrails' or otherwise scope it to content correctness only. For the full tiered bank covering guardrails, safety, injection, and edge cases, use beacon-test-bank instead."
---

# Beacon Content-Accuracy Question Set

## Overview

This is the lightweight of the two question-set skills. It produces a single-purpose
question set for checking whether Beacon (or whatever backend is under test) retrieves
and states real facts from one site correctly — no guardrail, jailbreak, or "does it
know its limits" testing included. If the user wants that broader coverage, or mentions
wanting to test the bot "to its limit," use `beacon-test-bank` instead; don't try to
stretch this skill to cover it.

Default scope: **50-70 questions** unless the user gives a different count.

---

## Workflow

### Step 1: Get the site's structure

Fetch `<site>/sitemap.xml` to see the actual page inventory. Don't guess site structure
from memory — sites reorganize, and a question built against a page that moved or was
retired is worthless.

### Step 2: Sample pages across the site's real sections

Pick a representative spread across the site's actual information architecture (not an
even split by page count — a section with 300 staff profile pages shouldn't get 300
questions). Fetch enough individual pages to pull concrete, checkable facts: numbers,
dates, names, dollar amounts, specific policies. Vague questions ("tell me about
academics") make bad test cases because there's no crisp way to score the answer as
right or wrong. Aim for roughly one question per fetched fact, grouped into clear
categories that mirror the site's own navigation.

**Specific beats general, every time:**
- Bad: "What financial aid does Yale offer?"
- Good: "Below what family income does a student have no expected family contribution?"

A specific factual question has one correct answer you can verify against the source
page, so a chatbot's answer is trivially markable as right, wrong, or hedged.

### Step 3: Draft the questions

For each question, capture:
- **Category** — the site section it belongs to
- **Question text** — phrased the way a real user would ask it
- **Expected answer / key facts** — the specific, verifiable fact(s) from the source page
- **Source URL** — the exact page the fact came from

Keep the question wording itself something you'd be comfortable re-asking verbatim
later. If this set will ever be re-run to compare against a previous run, exact question
text is the join key most Beacon-style testers use to pair runs — see `beacon-comparison-review`
for why that matters. Don't silently reword a question between runs if you want the
history to stay comparable.

### Step 4: Export two files

**1. Plain-text upload file** — one question per line, blank lines ignored, no numbering,
no headers, no category labels inline. This matches the AI Tester's own upload contract
verbatim: *"One question per line. Blank lines are ignored. Use this or upload a file
above — not both."* Don't add anything the tester would send to the bot as part of the
question text.

**2. QA tracking spreadsheet (.xlsx)** — for the human doing the testing, not for upload.
Columns:

| # | Category | Question | Expected Answer / Key Facts | Source Page | Bot Answer Accurate? (Y/N/Partial) | Notes |
|---|----------|----------|------------------------------|--------------|--------------------------------------|-------|

Include a short "Read Me" tab explaining how to use the sheet (ask each question, compare
the answer to the Expected column, mark the tracking column, note specifics). See the
`xlsx` skill for build mechanics — professional font, no hardcoded results where formulas
would apply (this sheet has none), recalc isn't needed since there are no formulas.

If the user asks for the plain-text file only ("just give me the txt", or after already
having the xlsx), ship a fresh `.txt` in that exact format rather than repackaging the
xlsx as a text dump — headers and numbering in a "converted" file will get sent to Beacon
as part of the question text if the user pastes it in as-is.

---

## Rules

- **No guardrail, jailbreak, or adversarial questions.** If the user wants those, point
  them at `beacon-test-bank` — don't quietly fold a few edge cases into a set that was
  scoped as content-only.
- **Every question must be answerable from a page you actually fetched.** Don't invent
  a plausible-sounding fact and assume it's on the site somewhere.
- **Watch for content that a fast summarization pass got wrong.** A tool-generated page
  summary can itself hallucinate a specific number that isn't literally on the page
  (this has happened: a summarized "70+ majors" turned out not to be a real figure once
  checked against what a live retrieval system actually pulled). When a number matters,
  prefer to see it appear as a literal string on the page before trusting it as ground
  truth.
- **Spread categories to match the site**, not evenly by page count. A directory of
  individual staff profile pages is one category with a couple of questions, not a
  quarter of the set.
- **Site content can be internally inconsistent** (two pages giving two different dates
  for the same thing, for example). If you notice this while sourcing a question, either
  pick the more authoritative page and note the discrepancy in your own notes, or skip
  the fact rather than baking an unresolved conflict into the ground truth.

---

## File naming

Save both outputs to the working/scratch directory with a name that identifies the site:
`<site-slug>-beacon-questions.txt` and `<site-slug>-beacon-question-set.xlsx`.
