#!/usr/bin/env python3
"""YaleSites router, v0.

Reads the board and the routing rules, promotes feature phase children whose
blockers are finished, and builds a brief of who owes what. Makes no model calls.

Dry run by default: prints the planned writes and the brief. --apply performs the
writes in references/routing.md ("What the router may change") and posts the brief.

  python3 router.py                      # dry run
  python3 router.py --apply              # promote + post the brief
  python3 router.py --apply --no-brief   # promote only
  python3 router.py --brief-file out.md  # also save the brief locally
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ORG = "yalesites-org"
ISSUES_REPO = "YaleSites-Internal"
PROJECT = 6
# Pinned "Router brief" issue in YaleSites-Internal. None = print only.
BRIEF_ISSUE = 1987
WATCH_REPOS = [
    "YaleSites-Internal", "yalesites-project", "atomic",
    "component-library-twig", "tokens", "yalesites-claude-plugins",
]
STALE_WORKING_DAYS = 3
# Slower lanes get a longer clock before they count as stuck; None = never listed.
STALE_BY_TYPE = {"Communications": 20, "Epic": None}
DEFAULT_BY_WORKING_DAYS = 5
ROUTING_MD = Path(__file__).resolve().parents[2] / "ticket" / "references" / "routing.md"
MARKER = "<!-- yalesites:router -->"

TODAY = dt.date.today()


# --- helpers ---------------------------------------------------------------

def gh(*args, input_text=None):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input_text)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}... failed: {r.stderr.strip()}")
    return r.stdout


def graphql(query, **variables):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    data = json.loads(gh(*args))
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"])[:500])
    return data["data"]


def search_all(query_string, fields, include_prs=True):
    """Paginated GraphQL search over issues, and PRs unless include_prs is False."""
    pr = f"... on PullRequest{{{fields}}}" if include_prs else ""
    q = """query($q:String!, $after:String){ search(query:$q, type:ISSUE, first:50, after:$after){
      pageInfo{hasNextPage endCursor} nodes{ __typename ... on Issue{%s} %s } } }""" % (fields, pr)
    out, after = [], None
    while True:
        vars_ = {"q": query_string}
        if after:
            vars_["after"] = after
        d = graphql(q, **vars_)["search"]
        out += [n for n in d["nodes"] if n]
        if not d["pageInfo"]["hasNextPage"]:
            return out
        after = d["pageInfo"]["endCursor"]


def working_days_between(start, end):
    days, d = 0, start
    while d < end:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            days += 1
    return days


def add_working_days(start, n):
    d = start
    while n > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def parse_date(s):
    return dt.date.fromisoformat(s[:10])


def ref(node):
    return f"{node['repository']['nameWithOwner']}#{node['number']}"


def link(node):
    return f"[{ref(node)}]({node['url']})"


def board_status(node):
    for it in (node.get("projectItems") or {}).get("nodes", []):
        if it["project"]["number"] == PROJECT:
            v = it.get("fieldValueByName")
            return v["name"] if v else None
    return None


def labels(node):
    return {l["name"] for l in node["labels"]["nodes"]}


# --- routing rules ---------------------------------------------------------

def load_phases():
    """Parse the phase table in routing.md: key -> {name, owner, gate}."""
    text = ROUTING_MD.read_text()
    phases = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not re.fullmatch(r"`[a-z]+`", cells[1] or ""):
            continue
        owner = re.search(r"`([A-Za-z0-9-]+)`", cells[2])
        gate = re.search(r"`([A-Za-z0-9-]+)`", cells[4])
        phases[cells[1].strip("`")] = {"name": cells[0], "owner": owner.group(1) if owner else None,
                                       "gate": gate.group(1) if gate else None}
    if not phases:
        sys.exit(f"Could not read the phase table from {ROUTING_MD}")
    return phases


AGENT_BLOCK = re.compile(r"<!--\s*yalesites:agent(.*?)-->", re.S)


def agent_field(body, key):
    for block in AGENT_BLOCK.findall(body or ""):
        m = re.search(rf"^\s*{key}:\s*(\S+)", block, re.M)
        if m:
            return m.group(1)
    return None


# --- 1. promotions ---------------------------------------------------------

STATUS_FRAGMENT = "projectItems(first:5){nodes{id project{number} fieldValueByName(name:\"Status\"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}"


def find_promotions(phases):
    fields = f"""number title url state body updatedAt repository{{nameWithOwner}}
      assignees(first:5){{nodes{{login}}}} labels(first:30){{nodes{{name}}}}
      parent{{number title url state repository{{nameWithOwner}}}}
      blockedBy(first:20){{nodes{{number title url state repository{{nameWithOwner}} {STATUS_FRAGMENT}}}}}
      {STATUS_FRAGMENT}"""
    nodes = search_all(f'repo:{ORG}/{ISSUES_REPO} is:issue is:open in:body "phase:"', fields, include_prs=False)
    promos, gated, waiting = [], [], []
    for n in nodes:
        phase = agent_field(n["body"], "phase")
        if not phase:
            continue
        if phase not in phases:
            waiting.append((n, f"unknown phase `{phase}`"))
            continue
        if board_status(n) != "Backlog":
            continue
        blockers = n["blockedBy"]["nodes"]
        if not blockers:
            continue  # nothing to wait on means a person parked it on purpose
        open_blockers = [b for b in blockers if b["state"] != "CLOSED" and board_status(b) != "Done"]
        if open_blockers:
            continue
        if not n["parent"] or n["parent"]["state"] == "CLOSED":
            waiting.append((n, "blockers done, but the parent is closed or missing"))
            continue
        held = labels(n) & {"needs-decision", "follow-up"}
        if held:
            waiting.append((n, f"blockers done, held by an open `{sorted(held)[0]}`"))
            continue
        assignees = [a["login"] for a in n["assignees"]["nodes"]]
        if phases[phase]["gate"]:
            gated.append({"issue": n, "phase": phase, "blockers": blockers, "gate": phases[phase]["gate"],
                          "owner": assignees[0] if assignees else phases[phase]["owner"]})
            continue
        promos.append({
            "issue": n, "phase": phase, "blockers": blockers,
            "assign": None if assignees else phases[phase]["owner"],
            "owner": assignees[0] if assignees else phases[phase]["owner"],
        })
    return promos, gated, waiting


def apply_promotion(p, phases):
    n = p["issue"]
    gh("project", "item-edit", str(PROJECT), "--owner", ORG, "--url", n["url"],
       "--field", "Status", "--value", "To Do")
    if p["assign"]:
        gh("issue", "edit", str(n["number"]), "-R", f"{ORG}/{ISSUES_REPO}", "--add-assignee", p["assign"])
    done = ", ".join(ref(b) for b in p["blockers"])
    body = (f"Moved {ref(n)} ({phases[p['phase']]['name']}) to To Do. "
            f"`{p['owner']}` is up. Finished blockers: {done}.\n\n{MARKER}")
    gh("issue", "comment", str(n["parent"]["number"]), "-R", f"{ORG}/{ISSUES_REPO}", "--body-file", "-",
       input_text=body)
    # read back
    d = graphql("""query($n:Int!){repository(owner:"%s",name:"%s"){issue(number:$n){%s}}}"""
                % (ORG, ISSUES_REPO, STATUS_FRAGMENT), n=n["number"])
    return board_status(d["repository"]["issue"]) == "To Do"


# --- 2. decisions and follow-ups ------------------------------------------

BLOCKS = {
    "needs-decision": (re.compile(r"##\s*Decision needed(.*?)(?=\n##\s|\Z)", re.S), "Decides"),
    "follow-up": (re.compile(r"##\s*Follow-up needed(.*?)(?=\n##\s|\Z)", re.S), "Who"),
}
LEGACY = {"question": "needs-decision"}


def parse_block(text, kind):
    rx, who_key = BLOCKS[kind]
    found = None
    for m in rx.finditer(text or ""):
        found = m.group(1)  # last one wins
    if not found:
        return None
    def field(k):
        m = re.search(rf"\*\*{k}:\*\*\s*(.+?)(?=\s{{2,}}\*\*|\n|$)", found)
        return m.group(1).strip() if m else None
    who = field(who_key) or ""
    who = re.search(r"@?([A-Za-z0-9-]+)", who)
    return {
        "who": who.group(1) if who else None,
        "what": field("Question") if kind == "needs-decision" else field("What"),
        "by": field("Needed by") if kind == "needs-decision" else field("By"),
    }


def find_owed():
    fields = """number title url body repository{nameWithOwner}
      assignees(first:5){nodes{login}} labels(first:30){nodes{name}}
      comments(last:30){nodes{body}}
      timelineItems(itemTypes:LABELED_EVENT, last:30){nodes{... on LabeledEvent{createdAt label{name}}}}"""
    repos = " ".join(f"repo:{ORG}/{r}" for r in WATCH_REPOS)
    owed, seen = [], set()
    for label in ["needs-decision", "follow-up", "question"]:
        for n in search_all(f'{repos} is:open label:"{label}"', fields):
            kind = LEGACY.get(label, label)
            key = (ref(n), kind)
            if key in seen:
                continue
            seen.add(key)
            texts = [n["body"]] + [c["body"] for c in n["comments"]["nodes"]]
            block = None
            for t in texts:
                block = parse_block(t, kind) or block
            labeled = [parse_date(e["createdAt"]) for e in n["timelineItems"]["nodes"]
                       if e and e["label"]["name"] == label]
            since = max(labeled) if labeled else TODAY
            assignees = [a["login"] for a in n["assignees"]["nodes"]]
            who = (block or {}).get("who") or (assignees[0] if assignees else None)
            by = None
            if block and block.get("by"):
                try:
                    by = parse_date(block["by"])
                except ValueError:
                    by = None
            owed.append({
                "node": n, "kind": kind, "legacy": label == "question",
                "who": who, "what": (block or {}).get("what"),
                "has_block": bool(block), "since": since,
                "by": by or add_working_days(since, DEFAULT_BY_WORKING_DAYS),
            })
    return owed


# --- 3. stuck --------------------------------------------------------------

def find_stuck():
    q = """query($after:String){ organization(login:"%s"){ projectV2(number:%d){
      items(first:100, after:$after){ pageInfo{hasNextPage endCursor} nodes{
        fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}
        content{ ... on Issue{ number title url state updatedAt repository{nameWithOwner} issueType{name}
          assignees(first:3){nodes{login}}
          closedByPullRequestsReferences(first:5, includeClosedPrs:false){nodes{number updatedAt}} } } } } } } }""" % (ORG, PROJECT)
    stuck, after = [], None
    while True:
        vars_ = {"after": after} if after else {}
        items = graphql(q, **vars_)["organization"]["projectV2"]["items"]
        for it in items["nodes"]:
            c, s = it.get("content") or {}, (it.get("fieldValueByName") or {}).get("name")
            if s != "In progress" or c.get("state") != "OPEN":
                continue
            prs = c["closedByPullRequestsReferences"]["nodes"]
            last = max([parse_date(c["updatedAt"])] + [parse_date(p["updatedAt"]) for p in prs])
            idle = working_days_between(last, TODAY)
            limit = STALE_BY_TYPE.get((c.get("issueType") or {}).get("name"), STALE_WORKING_DAYS)
            if limit is not None and idle >= limit:
                stuck.append({"node": c, "idle": idle, "has_pr": bool(prs),
                              "who": ", ".join(a["login"] for a in c["assignees"]["nodes"]) or "unassigned"})
        if not items["pageInfo"]["hasNextPage"]:
            return stuck
        after = items["pageInfo"]["endCursor"]


# --- 4. brief --------------------------------------------------------------

def build_brief(promos, gated, applied, waiting, owed, stuck, phases, dry):
    overdue = [o for o in owed if o["by"] < TODAY]
    no_owner = [o for o in owed if not o["who"]]
    head = (f"**TL;DR:** {len(promos)} phase hand-off{'s' if len(promos) != 1 else ''}, {len(gated)} waiting on a go, "
            f"{sum(o['kind'] == 'needs-decision' for o in owed)} open decisions and "
            f"{sum(o['kind'] == 'follow-up' for o in owed)} follow-ups ({len(overdue)} overdue), "
            f"{len(stuck)} stuck.")
    lines = [f"## Router brief, {TODAY:%a %b %-d}" + (" (dry run)" if dry else ""), "", head, ""]

    if promos:
        lines += ["### Handed off", ""]
        for p in promos:
            ok = applied.get(p["issue"]["number"])
            mark = "" if dry else (" (read back OK)" if ok else " (**write did not stick, check by hand**)")
            lines.append(f"- {link(p['issue'])} {p['issue']['title']} → To Do, `{p['owner']}`{mark}")
        lines.append("")

    if gated:
        lines += ["### Waiting on a go", ""]
        for g in sorted(gated, key=lambda g: g["gate"]):
            lines.append(f"- `{g['gate']}`: {link(g['issue'])} {g['issue']['title']} "
                         f"({phases[g['phase']]['name']}, part of {ref(g['issue']['parent'])}). Approve by moving it to To Do")
        lines.append("")

    lines += ["### Owed, by person", ""]
    by_person = {}
    for o in owed:
        by_person.setdefault(o["who"] or "no owner named", []).append(o)
    if not by_person:
        lines += ["Nothing owed. 🎉", ""]
    for who in sorted(by_person, key=lambda w: (w == "no owner named", -sum(o["by"] < TODAY for o in by_person[w]), w)):
        items = sorted(by_person[who], key=lambda o: o["by"])
        late = sum(o["by"] < TODAY for o in items)
        lines.append(f"**`{who}`**: {len(items)} open" + (f", {late} overdue" if late else ""))
        lines.append("")
        lines.append("| | Item | What | By | Open |")
        lines.append("|---|---|---|---|---|")
        for o in items:
            kind = "Decision" if o["kind"] == "needs-decision" else "Follow-up"
            if o["legacy"]:
                kind += " (`question`)"
            what = (o["what"] or o["node"]["title"]).replace("|", "/")[:90]
            if not o["has_block"]:
                what += " _(no block)_"
            by = f"**{o['by']:%b %-d}**" if o["by"] < TODAY else f"{o['by']:%b %-d}"
            days = working_days_between(o["since"], TODAY)
            lines.append(f"| {kind} | {link(o['node'])} | {what} | {by} | {days}d |")
        lines.append("")

    if stuck:
        lines += ["<details>", f"<summary><b>Stuck: In progress with no activity for {STALE_WORKING_DAYS}+ working days, 20+ for Communications ({len(stuck)})</b></summary>", ""]
        for s in sorted(stuck, key=lambda s: -s["idle"]):
            pr = "" if s["has_pr"] else ", no PR"
            lines.append(f"- {link(s['node'])} {s['node']['title']}, `{s['who']}`, {s['idle']}d idle{pr}")
        lines += ["", "</details>", ""]

    if waiting:
        lines += ["<details>", f"<summary><b>Phase children the router did not move ({len(waiting)})</b></summary>", ""]
        for n, why in waiting:
            lines.append(f"- {link(n)} {n['title']}: {why}")
        lines += ["", "</details>", ""]

    lines += ["Routing rules: `yalesites-product` plugin, `skills/ticket/references/routing.md`.", "", MARKER]
    return "\n".join(lines)


# --- main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="perform writes and post the brief")
    ap.add_argument("--no-brief", action="store_true", help="do not post the brief")
    ap.add_argument("--brief-file", help="also write the brief to this path")
    ap.add_argument("--json", action="store_true", help="print machine-readable results instead of the brief; makes no writes")
    a = ap.parse_args()

    phases = load_phases()
    promos, gated, waiting = find_promotions(phases)
    owed = find_owed()
    stuck = find_stuck()

    if a.json:
        item = lambda n: {"ref": ref(n), "url": n["url"], "title": n["title"]}
        print(json.dumps({
            "date": TODAY.isoformat(),
            "handoffs": [{**item(p["issue"]), "phase": p["phase"], "owner": p["owner"],
                          "parent": ref(p["issue"]["parent"])} for p in promos],
            "gated": [{**item(g["issue"]), "number": g["issue"]["number"], "phase": g["phase"], "gate": g["gate"],
                       "owner": g["owner"], "parent": ref(g["issue"]["parent"]),
                       "parent_number": g["issue"]["parent"]["number"],
                       "blockers": [ref(b) for b in g["blockers"]]} for g in gated],
            "owed": [{**item(o["node"]), "kind": o["kind"], "legacy": o["legacy"], "who": o["who"],
                      "what": o["what"], "has_block": o["has_block"], "since": o["since"].isoformat(),
                      "by": o["by"].isoformat(), "overdue": o["by"] < TODAY} for o in owed],
            "stuck": [{**item(s["node"]), "who": s["who"], "idle_working_days": s["idle"], "has_pr": s["has_pr"]}
                      for s in stuck],
            "held": [{**item(n), "reason": why} for n, why in waiting],
        }, indent=2))
        return

    applied = {}
    if a.apply:
        for p in promos:
            try:
                applied[p["issue"]["number"]] = apply_promotion(p, phases)
            except RuntimeError as e:
                applied[p["issue"]["number"]] = False
                print(f"promotion failed for {ref(p['issue'])}: {e}", file=sys.stderr)

    brief = build_brief(promos, gated, applied, waiting, owed, stuck, phases, dry=not a.apply)
    if a.brief_file:
        Path(a.brief_file).write_text(brief)
    print(brief)

    if a.apply and not a.no_brief:
        if BRIEF_ISSUE is None:
            print("\nBRIEF_ISSUE is not set; brief printed only.", file=sys.stderr)
        else:
            gh("issue", "comment", str(BRIEF_ISSUE), "-R", f"{ORG}/{ISSUES_REPO}", "--body-file", "-", input_text=brief)
            print(f"\nPosted to {ORG}/{ISSUES_REPO}#{BRIEF_ISSUE}", file=sys.stderr)

    failed = [n for n, ok in applied.items() if not ok]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
