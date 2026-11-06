#!/usr/bin/env python3
"""Find open tickets whose body talks about another ticket that has since closed.

Flags a line when it names a YaleSites-Internal ticket that closed after the open
ticket's body was last edited, and the same line uses dependency or time wording
("blocked by," "until," "once," "today," "currently"). These are candidates only:
about half are history or related-ticket lists that need nothing. Read each line
and keep the ones a reader would act on.

Two bulk GraphQL calls (open bodies, closed dates). No per-issue requests.

  python3 stale_refs.py            # markdown table of candidates
  python3 stale_refs.py --json     # machine-readable
"""

import argparse
import json
import re
import subprocess
import sys

REPO = "yalesites-org/YaleSites-Internal"
OWNER, NAME = REPO.split("/")

REF = re.compile(r"(?:(?<![\w/])|yalesites-org/YaleSites-Internal)#(\d{2,5})\b", re.I)
CUE = re.compile(
    r"\b(blocked|blocks|depends on|waiting|wait for|until|once|after|pending|"
    r"will|releases|lands?|ships?|today|currently|still|not yet|for now|"
    r"temporar\w*|workaround|in progress|is open)\b",
    re.I,
)
BLOCKER = re.compile(r"\b(blocked|depends on|waiting on|wait for|until|do not start)\b", re.I)


def gql(states, fields):
    query = (
        "query($endCursor:String){repository(owner:\"%s\",name:\"%s\"){"
        "issues(first:100,states:%s,after:$endCursor){pageInfo{hasNextPage endCursor}"
        "nodes{%s}}}}" % (OWNER, NAME, states, fields)
    )
    out = subprocess.run(
        ["gh", "api", "graphql", "--paginate", "-f", f"query={query}",
         "--jq", ".data.repository.issues.nodes[]"],
        check=True, capture_output=True, text=True,
    ).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def line_at(body, start, end):
    s = body.rfind("\n", 0, start) + 1
    e = body.find("\n", end)
    return body[s:len(body) if e < 0 else e].strip()


def scan():
    closed = {d["number"]: d for d in gql("CLOSED", "number closedAt stateReason")}
    hits = []
    for d in gql("OPEN", "number title url createdAt lastEditedAt body"):
        edited = d["lastEditedAt"] or d["createdAt"]
        body = re.sub(r"<!--.*?-->", "", d["body"] or "", flags=re.S)
        refs = {}
        for m in REF.finditer(body):
            n = int(m.group(1))
            c = closed.get(n)
            if not c or n == d["number"] or c["closedAt"] <= edited:
                continue
            line = line_at(body, m.start(), m.end())
            if CUE.search(line) and n not in refs:
                refs[n] = {
                    "ref": n,
                    "closed": c["closedAt"][:10],
                    "reason": c["stateReason"],
                    "blocker": bool(BLOCKER.search(line)),
                    "line": line[:240],
                }
        if refs:
            hits.append({
                "number": d["number"], "title": d["title"], "url": d["url"],
                "edited": edited[:10], "refs": list(refs.values()),
            })
    hits.sort(key=lambda h: (not any(r["blocker"] for r in h["refs"]), -h["number"]))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    hits = scan()
    if args.json:
        json.dump(hits, sys.stdout, indent=1)
        return
    print(f"{len(hits)} candidate(s)\n")
    print("| Ticket | Names | Closed | Line |")
    print("|---|---|---|---|")
    for h in hits:
        for r in h["refs"]:
            reason = "not planned" if r["reason"] == "NOT_PLANNED" else "done"
            line = r["line"].replace("|", "\\|")
            print(f"| [#{h['number']}]({h['url']}) | #{r['ref']} | {r['closed']} ({reason}) | {line} |")


if __name__ == "__main__":
    main()
