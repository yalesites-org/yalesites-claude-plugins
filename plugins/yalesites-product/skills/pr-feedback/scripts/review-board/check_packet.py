#!/usr/bin/env python3
"""The ELI5 check for a review board packet.

The reviewer reads many boards a day, arriving cold each time. Every question has
to work as one to three plain sentences and one straight question, with the detail
folded under it. `references/review-board.md` ("The ELI5 rule") says how to write
that; this script is what makes a packet that ignores it fail before the board opens.

    python3 check_packet.py <packet.json> [...]

Prints one line per problem and exits 1 if there are any. Exits 2 when run with no
arguments and 3 when a file cannot be read or is not valid JSON, so a broken packet
is not mistaken for one that only needs its wording fixed. It checks shape and
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

# Product names that look like code to the patterns above but are plain words to a reader.
PRODUCT_NAMES = re.compile(
    r"\b(?:iPhone|iPad|iPadOS|iOS|iMac|iCloud|iTunes|iMessage|macOS|watchOS|tvOS|visionOS"
    r"|eBay|eCommerce|eLearning|YouTube|LinkedIn|GitHub|PayPal|WordPress|JavaScript|TypeScript"
    r"|Node\.js|Next\.js|Nuxt\.js|Vue\.js|React\.js)\b"
)

# Abbreviations whose full stop does not end a sentence.
ABBREVIATIONS = re.compile(r"\b(?:e\.g|i\.e|vs|cf)\.", re.IGNORECASE)

# Closing marks an ask may end on after its question mark: markdown emphasis, quotes, brackets.
TRAILING_MARKS = "*_`\"')]\u201d\u2019 "


def words(text):
    return len(re.findall(r"\S+", text or ""))


def sentences(text):
    text = ABBREVIATIONS.sub(lambda m: m.group(0)[:-1], (text or "").strip())
    return len([s for s in re.split(r"(?<=[.?!])\s+", text) if s])


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
        plain = PRODUCT_NAMES.sub("", gist)
        for pattern, name in CODE_SHAPES:
            hit = pattern.search(plain)
            if hit:
                out.append(f"{where}: gist has {name} ({hit.group(0)!r}). Say what it is in plain words.")
    if not ask:
        out.append(f"{where}: no ask. The sticky panel needs the one question.")
    else:
        if not ask.rstrip(TRAILING_MARKS).endswith("?"):
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
    # A unit with no PR (a backlog or planning board) has no change to describe.
    fields = ("ask", "change") if u.get("pr") else ("ask",)
    for field in fields:
        text = (u.get(field) or "").strip()
        if not text:
            out.append(f"{where}: no {field} on the lead-in.")
        elif sentences(text) > UNIT_SENTENCES:
            out.append(f"{where}: {field} is {sentences(text)} sentences, the limit is {UNIT_SENTENCES}.")
    return out


def check_packet(packet):
    out = []
    units = packet.get("units") or []
    for n, u in enumerate(units, 1):
        out += check_unit(u, n)
    questions = packet.get("questions") or []
    # Zero questions is valid when there are units: a unit whose brief held nothing
    # still gets a lead-in and a ruling row (prep-mode.md, batch-mode.md).
    if not questions and not units:
        out.append("packet has no questions and no units.")
    for n, q in enumerate(questions, 1):
        out += check_question(q, n)
    return out


def main(argv):
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    bad = 0
    for path in argv:
        try:
            with open(path, encoding="utf-8") as f:
                packet = json.load(f)
        except (OSError, ValueError) as e:
            print(f"{path}: cannot read the packet: {e}", file=sys.stderr)
            return 3
        problems = check_packet(packet)
        for p in problems:
            print(f"{path}: {p}")
        bad += len(problems)
    if not bad:
        print("ELI5 check passed.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
