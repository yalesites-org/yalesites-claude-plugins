#!/usr/bin/env python3
"""Mechanical style check for YaleSites GitHub artifacts.

Canonical source. Do not edit the synced copies inside plugins/. Edit this file,
then run `bash scripts/sync-standards.sh`.

Checks a draft ticket body, PR description, PR review, release note, or report
against standards/github-writing.md and standards/github-communication-format.md.

The central idea: only the VISIBLE layer is budgeted. Text inside <details>
blocks is exempt from length rules, because a person chose to open it. Text
inside the <!-- yalesites:agent --> block is exempt from prose rules entirely,
because no person ever sees it. Code fences, inline code spans, and HTML
comments are exempt from the whole-document scans, so a draft that quotes the
format spec is never flagged for violating it.

The page-draft surface is the exception to all of that. A draft for a page on
yalesites.yale.edu is not a GitHub artifact: it has no TL;DR, no <details>
layering, and no visible-word budget. It carries its own structure instead, so
it gets its own structural checks (teaser, required sections, site-relative
links) and its prose rules apply to the "## Page copy" section alone, leaving
the config block and handoff notes in normal working English.

Usage:
    python3 check-github-text.py draft.md --surface ticket
    python3 check-github-text.py draft.md --surface pr-review --json
    python3 check-github-text.py draft.md --surface page-draft

Surfaces: ticket, pr-body, pr-review, release-notes, report, page-draft
Exit codes: 0 clean, 1 issues found, 2 bad invocation or unreadable input.
"""

import argparse
import json
import re
import sys

PROC_LIMIT = 20
DESC_LIMIT = 25

# TL;DR word cap, visible-layer word budget.
SURFACES = {
    "ticket": (60, 400),
    "pr-body": (60, 350),
    "pr-review": (60, 250),
    "release-notes": (80, 500),
    "report": (80, 600),
}

# Page drafts budget nothing, so they carry no caps. Kept out of SURFACES so
# the GitHub checks can key off that dict and skip them without a special case.
PAGE_SURFACES = ("page-draft",)
ALL_SURFACES = sorted(tuple(SURFACES) + PAGE_SURFACES)

BANNED = {
    "utilize": "use", "utilizes": "uses", "utilizing": "using",
    "leverage": "use", "leverages": "uses", "leveraging": "using",
    "ensure": "make sure", "ensures": "makes sure", "ensuring": "making sure",
    "in order to": "to", "prior to": "before", "subsequent to": "after",
    "approximately": "about", "additional": "more", "assist": "help",
    "attempt": "try", "commence": "start", "initiate": "start",
    "terminate": "stop", "obtain": "get", "regarding": "about",
    "concerning": "about", "numerous": "many", "facilitate": "help",
    "endeavor": "try", "aforementioned": "this", "in the event that": "if",
    "pursuant to": "under", "herein": "here", "modify": "change",
    "indicate": "show", "sufficient": "enough", "permit": "let",
    "permits": "lets", "require": "need", "requires": "needs",
    "requiring": "needing", "modifies": "changes", "modifying": "changing",
    "indicates": "shows", "indicating": "showing", "via": "with, by",
    "multiple": "many", "robust": "(cut it)",
    "circle back": "follow up", "touch base": "check in",
    "move the needle": "make a difference", "synergy": "(cut it)",
    "value-add": "(cut it)", "seamless": "(cut it)", "holistic": "(cut it)",
    "it is worth noting that": "(cut it, start with the thing)",
    "as discussed above": "(cut it)",
}

IMPERATIVES = (
    "select", "open", "go", "click", "choose", "enter", "type", "add",
    "remove", "clear", "check", "save", "use", "set", "turn", "keep",
    "find", "make", "read", "see", "include", "apply", "change", "confirm",
    "verify", "navigate", "upload", "publish", "run", "install", "update",
)

# Page-draft structure. The teaser runs to the next blank line rather than the
# next newline: a teaser hard-wrapped at a fixed column width has to be rejoined
# before its length means anything, or the 160-character ceiling never fires and
# the stated count is compared against one line of a longer string.
TEASER = re.compile(r"\*\*Teaser text[^*]*\*\*\s*\n+(.+?)(?:\n\s*\n|\Z)", re.S)
STATED_COUNT = re.compile(r"\((\d+)\s*characters?\)")
ABSOLUTE_INTERNAL = re.compile(r"\]\((https?://(?:www\.)?yalesites\.yale\.edu[^)]*)\)")
REQUIRED_SECTIONS = ("## Title", "## Config considerations")
PAGE_COPY = "## Page copy"
PAGE_COPY_STOPS = ("\n## Notes for the editor", "\n## Notes")

# Screenshot markers are instructions to the editor, not page copy. They are
# dropped before the markdown is stripped, because stripping deletes the very
# asterisks that identify them.
SCREENSHOT_MARKER = re.compile(r"^\*?\[SCREENSHOT\b|^\*Alt text\b", re.I)

AGENT_BLOCK = re.compile(r"<!--\s*yalesites:agent\b.*?-->", re.S)
DETAILS_BLOCK = re.compile(r"<details\b.*?</details>", re.S | re.I)
ANY_COMMENT = re.compile(r"<!--.*?-->", re.S)

# Regions the author cannot rewrite without changing what they mean. A command,
# a code sample, or a quoted <details> is markup the draft talks about, not
# markup the draft uses, so no check may read it as the real thing.
CODE = (
    re.compile(r"```.*?```", re.S),
    re.compile(r"~~~.*?~~~", re.S),
    re.compile(r"`[^`\n]+`"),
)
EXEMPT = CODE + (ANY_COMMENT,)


def line_of(text, index):
    return text[:index].count("\n") + 1


def blank_out(text, patterns):
    """Overwrite every match with spaces, keeping offsets and line breaks."""
    out = list(text)
    for pattern in patterns:
        for m in pattern.finditer(text):
            for i in range(m.start(), m.end()):
                if out[i] != "\n":
                    out[i] = " "
    return "".join(out)


def mask_code(text):
    return blank_out(text, CODE)


def mask_exempt(text):
    return blank_out(text, EXEMPT)


def split_layers(text):
    """Return (visible, collapsed, agent_block_or_None, agent_start).

    Blocks are located in a code-masked copy, so a draft that quotes a
    <details> block or a yalesites:agent block never has the quotation
    mistaken for a real layer. Offsets survive the mask, so the content
    itself is still sliced out of the original text.
    """
    masked = mask_code(text)

    agent = None
    agent_start = None
    m = AGENT_BLOCK.search(masked)
    if m:
        agent = text[m.start():m.end()]
        agent_start = m.start()
        text = text[: m.start()] + text[m.end():]
        masked = masked[: m.start()] + masked[m.end():]

    spans = [(b.start(), b.end()) for b in DETAILS_BLOCK.finditer(masked)]
    collapsed = "\n".join(text[s:e] for s, e in spans)

    parts = []
    last = 0
    for s, e in spans:
        parts.append(text[last:s])
        parts.append(" ")
        last = e
    parts.append(text[last:])
    visible = ANY_COMMENT.sub(" ", "".join(parts))

    return visible, collapsed, agent, agent_start


def strip_markdown(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`#>]", "", text)
    return text


LIST_ITEM = re.compile(r"^([-*+]\s+|\d+[.)]\s+)")


def prose_lines(section, drop=None):
    """Yield prose units with hard wraps undone.

    A sentence broken over several lines has to be rejoined before it can be
    measured, or the sentence caps never fire on anything drafted at a fixed
    column width. A blank line, a heading, a table row, or a new list marker
    starts a new unit; anything else continues the one in progress.

    `drop` is an optional predicate run on each raw line. A line it matches is
    discarded and ends the unit in progress. Callers that need to recognise a
    line by its markdown must pass the section unstripped and use this, since
    stripping removes the markers they would match on.
    """
    out = []
    current = []
    in_code = False

    def flush():
        if current:
            out.append(" ".join(current))
            current.clear()

    for raw in section.split("\n"):
        line = raw.strip()
        if line.startswith("```") or line.startswith("~~~"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        if not line or line.startswith("#") or line.startswith("|") or set(line) <= set("-*= "):
            flush()
            continue
        if drop is not None and drop(line):
            flush()
            continue
        if LIST_ITEM.match(line):
            flush()
            line = LIST_ITEM.sub("", line)
        current.append(line)
    flush()
    return out


def sentences(line):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if s.strip()]


def is_procedural(sentence):
    first = re.sub(r"^\W+", "", sentence).split()
    return bool(first) and first[0].lower() in IMPERATIVES


def page_copy_section(text):
    """The "## Page copy" section, or the whole draft if there is no heading.

    Everything outside it (the config block, handoff notes) is working English
    for one reader and is not held to the page's prose rules.
    """
    if PAGE_COPY not in text:
        return text
    section = text.split(PAGE_COPY, 1)[1]
    for stop in PAGE_COPY_STOPS:
        if stop in section:
            return section.split(stop, 1)[0]
    return section


def check_page_draft(text, masked, add):
    """Structural checks for a yalesites.yale.edu page draft."""
    for m in ABSOLUTE_INTERNAL.finditer(masked):
        path_only = re.sub(r"^https?://(?:www\.)?yalesites\.yale\.edu", "", m.group(1)) or "/"
        add("absolute_internal_link", line_of(text, m.start()),
            f"Use the site-relative path instead: {path_only}")

    teaser = TEASER.search(masked)
    if not teaser:
        add("teaser_missing", 0,
            "No '**Teaser text (N characters):**' block found. Every page draft needs one.")
    else:
        line = line_of(text, teaser.start())
        body = re.sub(r"\s+", " ", text[teaser.start(1):teaser.end(1)]).strip()
        n = len(body)
        if n > 160:
            add("teaser_too_long", line,
                f"Teaser is {n} characters. Target ~150, ceiling 160.")
        stated = STATED_COUNT.search(teaser.group(0))
        if stated and int(stated.group(1)) != n:
            add("teaser_count_wrong", line,
                f"Draft says {stated.group(1)} characters, actual is {n}.")

    for heading in REQUIRED_SECTIONS:
        if heading not in masked:
            add("section_missing", 0, f"Draft is missing a '{heading}' section.")

    # Prose rules, page copy only. prose_lines runs on the unstripped section so
    # the screenshot markers are still recognisable; each unit is stripped after.
    section = mask_exempt(page_copy_section(text))
    units = [strip_markdown(u) for u in
             prose_lines(section, drop=SCREENSHOT_MARKER.search)]

    for unit in units:
        for s in sentences(unit):
            n = len(s.split())
            proc = is_procedural(s)
            limit = PROC_LIMIT if proc else DESC_LIMIT
            if n > limit:
                add("long_sentence", 0,
                    f"{n} words ({'procedural' if proc else 'descriptive'}, limit {limit}): {s[:90]}")

    low = " ".join(units).lower()
    for word, better in BANNED.items():
        for _ in re.finditer(r"\b" + re.escape(word) + r"\b", low):
            add("banned_word", 0, f'"{word}" -> "{better}"')


def check(path, surface):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as err:
        print(f"cannot read {path}: {err}", file=sys.stderr)
        sys.exit(2)
    issues = []

    def add(kind, line, detail):
        issues.append({"kind": kind, "line": line, "detail": detail})

    # --- Whole-document structural checks -------------------------------
    # Every whole-document scan runs on the masked copy, so a draft that quotes
    # the format spec is never flagged for violating it.
    masked = mask_exempt(text)

    for m in re.finditer("—", masked):
        add("em_dash", line_of(text, m.start()),
            "Em dash found. Rewrite with a comma, period, colon, or parentheses.")

    # A page draft shares the em-dash rule and nothing below it.
    if surface in PAGE_SURFACES:
        check_page_draft(text, masked, add)
        return issues

    tldr_cap, visible_cap = SURFACES[surface]

    for m in re.finditer(r"<details\b", masked, re.I):
        rest = masked[m.end():]
        close = rest.lower().find("</details>")
        nested = rest.lower().find("<details")
        if nested != -1 and (close == -1 or nested < close):
            add("nested_details", line_of(text, m.start()),
                "Nested <details>. Flatten to one level.")

    for m in re.finditer(r"</summary>(?!\s*\n\s*\n)", masked, re.I):
        add("details_blank_line", line_of(text, m.start()),
            "Needs a blank line after </summary> or GitHub will not render the Markdown.")

    for m in re.finditer(r"(?<!\n\n)\s*</details>", masked, re.I):
        if not re.search(r"\n\s*\n\s*</details>", masked[max(0, m.start() - 4): m.end()]):
            add("details_blank_line", line_of(text, m.start()),
                "Needs a blank line before </details> or GitHub will not render the Markdown.")

    for m in re.finditer(r"<summary>\s*(?:<b>)?\s*(details|more|info|notes)\s*(?:</b>)?\s*</summary>",
                         masked, re.I):
        add("vague_summary", line_of(text, m.start()),
            f'"{m.group(1)}" does not say what is inside. Name the content.')

    visible, collapsed, agent, agent_start = split_layers(text)

    # --- Machine-only block ---------------------------------------------
    if agent is not None:
        tail = mask_exempt(text)[agent_start + len(agent):].strip()
        if tail:
            add("agent_block_position", line_of(text, agent_start),
                "The yalesites:agent block must be last in the body.")
        body = re.sub(r"^\s*yalesites:agent\b", "", agent[4:-3])
        if not body.strip():
            add("agent_block_empty", line_of(text, agent_start),
                "Empty yalesites:agent block. Leave it out instead.")
        for key in re.findall(r"^\s*([A-Za-z_][\w-]*):", body, re.M):
            if key != key.lower() or "-" in key:
                add("agent_block_key", 0,
                    f'Key "{key}" should be lowercase snake_case.')
        for hit in re.finditer(r"(?i)\b(token|secret|password|api[_-]?key|bearer)\b", body):
            add("agent_block_secret", 0,
                f'"{hit.group(1)}" in the machine block. Secrets never go here.')

    if len(AGENT_BLOCK.findall(masked)) > 1:
        add("agent_block_duplicate", 0,
            "More than one yalesites:agent block. Keep exactly one, at the bottom.")

    # --- TL;DR ----------------------------------------------------------
    tldr = re.search(r"\*\*TL;DR:?\*\*:?\s*(.+?)(?:\n\s*\n|\Z)", visible, re.S | re.I)
    if not tldr:
        add("tldr_missing", 0,
            "No '**TL;DR:**' line found. Every artifact opens with one, always visible.")
    else:
        words = len(strip_markdown(tldr.group(1)).split())
        if words > tldr_cap:
            add("tldr_too_long", line_of(visible, tldr.start()),
                f"TL;DR is {words} words. Cap for {surface} is {tldr_cap}.")

    # --- Visible budget --------------------------------------------------
    clean_visible = strip_markdown(visible)
    visible_words = len(clean_visible.split())
    if visible_words > visible_cap:
        over = visible_words - visible_cap
        add("visible_too_long", 0,
            f"Visible layer is {visible_words} words, {over} over the {visible_cap} "
            f"budget for {surface}. Move depth into a <details> block.")

    if not collapsed and visible_words > visible_cap:
        add("no_collapsed_layer", 0,
            "Over budget with no <details> block at all. The depth has nowhere to go yet.")

    # --- Prose rules, visible layer only ---------------------------------
    for line in prose_lines(clean_visible):
        for s in sentences(line):
            n = len(s.split())
            proc = is_procedural(s)
            limit = PROC_LIMIT if proc else DESC_LIMIT
            if n > limit:
                add("long_sentence", 0,
                    f"{n} words ({'procedural' if proc else 'descriptive'}, limit {limit}): {s[:90]}")

    # --- Word swaps, visible and collapsed (not the machine block) -------
    low = re.sub(r"\s+", " ", clean_visible + " " + strip_markdown(collapsed)).lower()
    for word, better in BANNED.items():
        for _ in re.finditer(r"\b" + re.escape(word) + r"\b", low):
            add("banned_word", 0, f'"{word}" -> "{better}"')

    return issues


ORDER = [
    "em_dash", "section_missing", "teaser_missing", "teaser_too_long",
    "teaser_count_wrong", "absolute_internal_link",
    "tldr_missing", "tldr_too_long", "visible_too_long",
    "no_collapsed_layer", "details_blank_line", "nested_details",
    "vague_summary", "agent_block_position", "agent_block_duplicate",
    "agent_block_empty", "agent_block_key", "agent_block_secret",
    "long_sentence", "banned_word",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--surface", required=True, choices=ALL_SURFACES)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    issues = check(args.path, args.surface)

    if args.json:
        print(json.dumps(issues, indent=2))
        return 1 if issues else 0

    if not issues:
        print(f"Clean. No issues found ({args.surface}).")
        return 0

    by_kind = {}
    for it in issues:
        by_kind.setdefault(it["kind"], []).append(it)

    print(f"{len(issues)} issue(s) found in {args.path} ({args.surface})\n")
    for kind in ORDER:
        if kind not in by_kind:
            continue
        print(f"[{kind}] {len(by_kind[kind])}")
        for it in by_kind[kind]:
            loc = f"line {it['line']}: " if it["line"] else ""
            print(f"  - {loc}{it['detail']}")
        print()

    print("Long sentences and banned words are candidates, not verdicts.")
    if args.surface in PAGE_SURFACES:
        print("A 22-word descriptive sentence can be fine. A 22-word instruction is not.")
        print("Only the '## Page copy' section is held to the prose rules.")
    else:
        print("A 22-word descriptive sentence can be fine. A 22-word acceptance criterion is not.")
        print("Only the visible layer is budgeted. Collapsed depth is free.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
