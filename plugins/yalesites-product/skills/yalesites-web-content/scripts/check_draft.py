#!/usr/bin/env python3
"""Mechanical style check for YaleSites page drafts.

Checks the things that are easy to miss by eye: em dashes, over-length
sentences, absolute internal URLs, non-STE vocabulary, and teaser length.

Only the "## Page copy" section is checked for prose rules, so the config
block and handoff notes can use normal working English. If the draft has no
"## Page copy" heading, the whole file is checked.

Usage:
    python3 check_draft.py path/to/draft.md
    python3 check_draft.py path/to/draft.md --json
"""

import argparse
import json
import re
import sys

PROC_LIMIT = 20   # procedural sentences
DESC_LIMIT = 25   # descriptive sentences

BANNED = {
    "utilize": "use", "utilizes": "uses", "utilizing": "using",
    "leverage": "use", "leverages": "uses", "leveraging": "using",
    "ensure": "make sure", "ensures": "makes sure", "ensuring": "making sure",
    "in order to": "to", "prior to": "before", "subsequent to": "after",
    "approximately": "about", "additional": "more", "assist": "help",
    "attempt": "try", "commence": "start", "initiate": "start",
    "terminate": "stop", "obtain": "get", "regarding": "about",
    "concerning": "about", "numerous": "many", "facilitate": "help",
    "endeavor": "try", "pursuant to": "under", "herein": "here",
    "circle back": "follow up", "touch base": "check in",
    "move the needle": "make a difference", "synergy": "(cut it)",
    "value-add": "(cut it)", "please": "(usually cut it)",
}

# Imperative openers that mark a sentence as procedural.
IMPERATIVES = (
    "select", "open", "go", "click", "choose", "enter", "type", "add",
    "remove", "clear", "check", "save", "use", "set", "turn", "keep",
    "find", "make", "read", "see", "come", "include", "apply", "change",
)


def strip_markdown(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`#>]", "", text)
    return text


def prose_lines(section):
    """Body prose only: skip headings, screenshot markers, code, tables."""
    out = []
    in_code = False
    for raw in section.split("\n"):
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        if line.startswith("#") or line.startswith("|"):
            continue
        if line.startswith("*[") or line.startswith("*Alt text"):
            continue
        if set(line) <= set("-*= "):
            continue
        out.append(re.sub(r"^[-*+]\s+|^\d+\.\s+", "", line))
    return out


def sentences(line):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if s.strip()]


def is_procedural(sentence):
    first = re.sub(r"^\W+", "", sentence).split()
    return bool(first) and first[0].lower() in IMPERATIVES


def check(path):
    text = open(path, encoding="utf-8").read()
    issues = []

    for m in re.finditer(r"—", text):
        line_no = text[: m.start()].count("\n") + 1
        issues.append({"kind": "em_dash", "line": line_no,
                       "detail": "Em dash found. Rewrite with a comma, period, colon, or parentheses."})

    for m in re.finditer(r"\]\((https?://(?:www\.)?yalesites\.yale\.edu[^)]*)\)", text):
        line_no = text[: m.start()].count("\n") + 1
        path_only = re.sub(r"^https?://(?:www\.)?yalesites\.yale\.edu", "", m.group(1)) or "/"
        issues.append({"kind": "absolute_internal_link", "line": line_no,
                       "detail": f"Use the site-relative path instead: {path_only}"})

    teaser = re.search(r"\*\*Teaser text[^*]*\*\*\s*\n+([^\n]+)", text)
    if teaser:
        body = teaser.group(1).strip()
        n = len(body)
        if n > 160:
            issues.append({"kind": "teaser_too_long", "line": text[: teaser.start()].count("\n") + 1,
                           "detail": f"Teaser is {n} characters. Target ~150, ceiling 160."})
        stated = re.search(r"\((\d+)\s*characters?\)", teaser.group(0))
        if stated and int(stated.group(1)) != n:
            issues.append({"kind": "teaser_count_wrong", "line": text[: teaser.start()].count("\n") + 1,
                           "detail": f"Draft says {stated.group(1)} characters, actual is {n}."})
    else:
        issues.append({"kind": "teaser_missing", "line": 0,
                       "detail": "No '**Teaser text (N characters):**' block found. Every page draft needs one."})

    for heading in ("## Title", "## Config considerations"):
        if heading not in text:
            issues.append({"kind": "section_missing", "line": 0,
                           "detail": f"Draft is missing a '{heading}' section."})

    if "## Page copy" in text:
        section = text.split("## Page copy", 1)[1]
        for stop in ("\n## Notes for the editor", "\n## Notes"):
            if stop in section:
                section = section.split(stop, 1)[0]
                break
        offset = text.split("## Page copy", 1)[0].count("\n") + 1
    else:
        section, offset = text, 0

    clean = strip_markdown(section)
    for i, line in enumerate(prose_lines(clean)):
        for s in sentences(line):
            words = len(s.split())
            proc = is_procedural(s)
            limit = PROC_LIMIT if proc else DESC_LIMIT
            if words > limit:
                issues.append({
                    "kind": "long_sentence",
                    "line": offset,
                    "detail": f"{words} words ({'procedural' if proc else 'descriptive'}, limit {limit}): {s[:90]}",
                })

    low = clean.lower()
    for word, better in BANNED.items():
        for m in re.finditer(r"\b" + re.escape(word) + r"\b", low):
            issues.append({"kind": "banned_word", "line": offset,
                           "detail": f'"{word}" -> "{better}"'})

    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    issues = check(args.path)

    if args.json:
        print(json.dumps(issues, indent=2))
        return 1 if issues else 0

    if not issues:
        print("Clean. No issues found.")
        return 0

    order = ["em_dash", "section_missing", "teaser_missing", "teaser_too_long",
             "teaser_count_wrong", "absolute_internal_link", "long_sentence", "banned_word"]
    by_kind = {}
    for it in issues:
        by_kind.setdefault(it["kind"], []).append(it)

    print(f"{len(issues)} issue(s) found in {args.path}\n")
    for kind in order:
        if kind not in by_kind:
            continue
        print(f"[{kind}] {len(by_kind[kind])}")
        for it in by_kind[kind]:
            loc = f"line {it['line']}: " if it["line"] else ""
            print(f"  - {loc}{it['detail']}")
        print()

    print("Long sentences and banned words are candidates, not verdicts.")
    print("A 22-word descriptive sentence can be fine; a 22-word instruction is not.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
