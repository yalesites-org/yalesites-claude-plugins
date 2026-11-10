#!/usr/bin/env python3
"""The ELI5 check for a review board packet.

The reviewer reads many boards a day, arriving cold each time. Every question has
to work as one to three plain sentences and one straight question, with the detail
folded under it. `references/review-board.md` ("The ELI5 rule") says how to write
that; this script is what makes a packet that ignores it fail before the board opens.

    python3 check_packet.py <packet.json> [...]

Prints one line per problem and exits 1 if there are any. It checks shape and
length, not judgment: a packet can pass and still be unclear, so read it once as
someone who has never seen the PR.
"""

import json
import re
import sys

GIST_SENTENCES = 3
GIST_WORDS = 60
ASK_WORDS = 25
BRIEF_BULLETS = 4
BRIEF_WORDS = 30
UNIT_SENTENCES = 3

# Things a person outside the code would have to look up.
CODE_SHAPES = [
    (re.compile(r"`"), "code in backticks"),
    (re.compile(r"\b[\w./-]+\.(php|twig|yml|yaml|js|ts|scss|css|json|py|md)\b"), "a file name"),
    (re.compile(r"\b[a-z]+_[a-z_]+\b"), "a snake_case name"),
    (re.compile(r"\b[a-z]+[A-Z]\w+\b"), "a camelCase name"),
    (re.compile(r"(?<![\w/])#\d+\b"), "a bare ticket number"),
]


def words(text):
    return len(re.findall(r"\S+", text or ""))


def sentences(text):
    return len([s for s in re.split(r"(?<=[.?!])\s+", (text or "").strip()) if s])


def check_question(q, n):
    where = f"question {n} ({q.get('id') or q.get('title') or 'no id'})"
    out = []
    gist = (q.get("gist") or "").strip()
    ask = (q.get("ask") or "").strip()
    if not gist:
        out.append(f"{where}: no gist. Every question opens with one to three plain sentences.")
    else:
        if sentences(gist) > GIST_SENTENCES:
            out.append(f"{where}: gist is {sentences(gist)} sentences, the limit is {GIST_SENTENCES}.")
        if words(gist) > GIST_WORDS:
            out.append(f"{where}: gist is {words(gist)} words, the limit is {GIST_WORDS}.")
        for pattern, name in CODE_SHAPES:
            hit = pattern.search(gist)
            if hit:
                out.append(f"{where}: gist has {name} ({hit.group(0)!r}). Say what it is in plain words.")
    if not ask:
        out.append(f"{where}: no ask. The sticky panel needs the one question.")
    else:
        if not ask.endswith("?"):
            out.append(f"{where}: ask is not a question.")
        if words(ask) > ASK_WORDS:
            out.append(f"{where}: ask is {words(ask)} words, the limit is {ASK_WORDS}.")
        if ask.count("?") > 1:
            out.append(f"{where}: ask holds more than one question. Split it.")
    brief = q.get("brief") or []
    if len(brief) > BRIEF_BULLETS:
        out.append(f"{where}: brief has {len(brief)} bullets, the limit is {BRIEF_BULLETS}.")
    for b in brief:
        if words(b) > BRIEF_WORDS:
            out.append(f"{where}: a brief bullet is {words(b)} words, the limit is {BRIEF_WORDS}: {b[:60]!r}")
    real = [o for o in q.get("options") or [] if o.get("value") != "defer"]
    if not 2 <= len(real) <= 4:
        out.append(f"{where}: {len(real)} options besides Decide later; give two to four.")
    for o in real:
        if not (o.get("detail") or "").strip():
            out.append(f"{where}: option {o.get('label')!r} has no detail saying what it costs.")
    return out


def check_unit(u, n):
    where = f"unit {n} ({(u.get('pr') or {}).get('ref') or (u.get('issue') or {}).get('ref') or 'no ref'})"
    out = []
    for field in ("ask", "change"):
        text = (u.get(field) or "").strip()
        if not text:
            out.append(f"{where}: no {field} on the lead-in.")
        elif sentences(text) > UNIT_SENTENCES:
            out.append(f"{where}: {field} is {sentences(text)} sentences, the limit is {UNIT_SENTENCES}.")
    return out


def check_packet(packet):
    out = []
    for n, u in enumerate(packet.get("units") or [], 1):
        out += check_unit(u, n)
    questions = packet.get("questions") or []
    if not questions:
        out.append("packet has no questions.")
    for n, q in enumerate(questions, 1):
        out += check_question(q, n)
    return out


def main(argv):
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    bad = 0
    for path in argv:
        with open(path, encoding="utf-8") as f:
            problems = check_packet(json.load(f))
        for p in problems:
            print(f"{path}: {p}")
        bad += len(problems)
    if not bad:
        print("ELI5 check passed.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
