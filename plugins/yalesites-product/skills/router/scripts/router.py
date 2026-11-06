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
NEEDS_PRIORITY_DAYS = 30
ROUTING_MD = Path(__file__).resolve().parents[2] / "ticket" / "references" / "routing.md"
MARKER = "<!-- yalesites:router -->"
GATE_LABEL = "awaiting-go"
BOARD_VIEWS = f"https://github.com/orgs/{ORG}/projects/{PROJECT}/views/"
# The one Monday view on the YaleSites Board, grouped by the Stage field.
MONDAY_VIEW = 28
STAGE_FIELD = "Stage"
# When an item qualifies for more than one stage, the first one listed wins.
STAGE_ORDER = ["Gate", "Decision", "Follow-up", "Stuck", "Intake"]
# The Monday meeting is dev-focused; these Issue Types go to the weekly comms meeting instead.
MONDAY_SKIP_TYPES = {"Communications"}
# Lane floors: candidate tickets listed for a person to approve. The router never assigns them.
LANE_CANDIDATES = 5
CANDIDATE_SKIP_TYPES = {"Epic", "Communications"}
# Issue Types that never count toward a lane floor.
FLOOR_SKIP_TYPES = {"Communications"}
EMBED_TITLE = re.compile(r"^\s*Embed(?: Request)?:", re.I)
CANDIDATE_SKIP_LABELS = {"forming", "needs-decision", "follow-up", "epic"}
PRIORITY_RANK = {"Hotfix": 0, "High": 1, "Medium": 2, "Low": 3}
RISK_RANK = {"Low": 0, "Medium": 1, "High": 2}

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


def search_all(query_string, fields, include_prs=True, issue_fields=""):
    """Paginated GraphQL search over issues, and PRs unless include_prs is False.
    issue_fields are extra fields only issues have (PRs have no issueType)."""
    pr = f"... on PullRequest{{{fields}}}" if include_prs else ""
    q = """query($q:String!, $after:String){ search(query:$q, type:ISSUE, first:50, after:$after){
      pageInfo{hasNextPage endCursor} nodes{ __typename ... on Issue{%s %s} %s } } }""" % (fields, issue_fields, pr)
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


MENTION = re.compile(r"@(?=[A-Za-z0-9-])")


def quiet(text):
    """Break @mentions in text we copy into the brief, so reposting it never pings anyone."""
    return MENTION.sub("@\u200b", text or "")


def board_status(node):
    for it in (node.get("projectItems") or {}).get("nodes", []):
        if it["project"]["number"] == PROJECT:
            v = it.get("fieldValueByName")
            return v["name"] if v else None
    return None


def labels(node):
    return {l["name"] for l in node["labels"]["nodes"]}


# --- routing rules ---------------------------------------------------------

def load_groomers():
    """Handles in the Groomer table of routing.md."""
    text = ROUTING_MD.read_text()
    section = text.split("## Intake", 1)[1].split("\n## ", 1)[0] if "## Intake" in text else ""
    return set(re.findall(r"^\|[^|]+\|\s*`([A-Za-z0-9-]+)`", section, re.M))


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


def load_lanes():
    """Parse the Lane floors table in routing.md: handle -> {name, floor, approver, areas}."""
    text = ROUTING_MD.read_text()
    if "## Lane floors" not in text:
        return {}
    section = text.split("## Lane floors", 1)[1].split("\n## ", 1)[0]
    lanes = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        handle = re.fullmatch(r"`([A-Za-z0-9-]+)`", cells[1])
        floor = re.fullmatch(r"\d+", cells[2])
        approver = re.search(r"`([A-Za-z0-9-]+)`", cells[3])
        if handle and floor:
            areas = re.findall(r"`([^`]+)`", cells[4]) if len(cells) > 4 else []
            lanes[handle.group(1)] = {"name": cells[0], "floor": int(floor.group()),
                                      "approver": approver.group(1) if approver else None,
                                      "areas": [a.lower() for a in areas]}
    return lanes


def load_embed_rule():
    """The New embed providers section of routing.md: (approver handle, Embed Requests epic number)."""
    text = ROUTING_MD.read_text()
    if "## New embed providers" not in text:
        return None, None
    section = text.split("## New embed providers", 1)[1].split("\n## ", 1)[0]
    approver = re.search(r"`([A-Za-z0-9-]+)`", section)
    epic = re.search(r"#(\d+)", section)
    return (approver.group(1) if approver else None), (int(epic.group(1)) if epic else None)


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
        for n in search_all(f'{repos} is:open label:"{label}"', fields, issue_fields="issueType{name}"):
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

def sync_gate_labels(gated):
    """Keep GATE_LABEL on exactly the gated children waiting on a go. Returns (added, removed)."""
    want = {g["issue"]["number"] for g in gated}
    have = {n["number"] for n in search_all(f'repo:{ORG}/{ISSUES_REPO} is:issue is:open label:"{GATE_LABEL}"',
                                            "number", include_prs=False)}
    for n in want - have:
        gh("issue", "edit", str(n), "-R", f"{ORG}/{ISSUES_REPO}", "--add-label", GATE_LABEL)
    for n in have - want:
        gh("issue", "edit", str(n), "-R", f"{ORG}/{ISSUES_REPO}", "--remove-label", GATE_LABEL)
    return sorted(want - have), sorted(have - want)


def desired_stages(gated, owed, stuck, intake, no_priority):
    """url -> Stage option, highest STAGE_ORDER entry wins."""
    want = {}
    def put(url, stage):
        if url not in want or STAGE_ORDER.index(stage) < STAGE_ORDER.index(want[url]):
            want[url] = stage
    for g in gated:
        put(g["issue"]["url"], "Gate")
    for o in owed:
        put(o["node"]["url"], "Decision" if o["kind"] == "needs-decision" else "Follow-up")
    for x in stuck:
        put(x["node"]["url"], "Stuck")
    for n in list(intake) + list(no_priority):
        put(n["url"], "Intake")
    return want


def sync_stages(want, board):
    """Set or clear Stage on board items so it matches want. Returns (set, cleared) counts."""
    d = graphql("""query{ organization(login:"%s"){ projectV2(number:%d){ id
      field(name:"%s"){ ... on ProjectV2SingleSelectField{ id options{ id name } } } } } }""" % (ORG, PROJECT, STAGE_FIELD))
    proj = d["organization"]["projectV2"]
    field = proj["field"]
    if not field:
        raise RuntimeError(f"no {STAGE_FIELD} field on project {PROJECT}")
    opts = {o["name"]: o["id"] for o in field["options"]}
    n_set = n_clear = 0
    for url, item in board.items():
        target = want.get(url)
        if target == item["stage"]:
            continue
        base = ["project", "item-edit", "--id", item["id"], "--project-id", proj["id"], "--field-id", field["id"]]
        if target:
            gh(*base, "--single-select-option-id", opts[target]); n_set += 1
        elif item["stage"] in opts:
            gh(*base, "--clear"); n_clear += 1
    return n_set, n_clear


def find_features():
    """Open Feature parents with sub-issues, and how many children are Done or closed."""
    fields = f"""number title url repository{{nameWithOwner}} milestone{{title dueOn}}
      subIssues(first:50){{nodes{{state {STATUS_FRAGMENT}}}}}"""
    out = []
    for n in search_all(f'repo:{ORG}/{ISSUES_REPO} is:issue is:open type:Feature', fields, include_prs=False):
        kids = n["subIssues"]["nodes"]
        if not kids:
            continue
        done = sum(k["state"] == "CLOSED" or board_status(k) == "Done" for k in kids)
        out.append({"node": n, "done": done, "total": len(kids),
                    "milestone": (n.get("milestone") or {}).get("title") or "No milestone",
                    "due": (n.get("milestone") or {}).get("dueOn") or "9999"})
    return sorted(out, key=lambda f: (f["due"], f["done"] / f["total"]))


def find_intake():
    fields = """number title url createdAt repository{nameWithOwner} author{login} issueType{name}"""
    nodes = search_all(f'repo:{ORG}/{ISSUES_REPO} is:issue is:open label:forming', fields, include_prs=False)
    return sorted(nodes, key=lambda n: n["createdAt"], reverse=True)


def find_stuck(groomers=frozenset()):
    q = """query($after:String){ organization(login:"%s"){ projectV2(number:%d){
      items(first:100, after:$after){ pageInfo{hasNextPage endCursor} nodes{ id
        fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}
        stage: fieldValueByName(name:"%s"){... on ProjectV2ItemFieldSingleSelectValue{name}}
        priority: fieldValueByName(name:"Priority"){... on ProjectV2ItemFieldSingleSelectValue{name}}
        risk: fieldValueByName(name:"Risk"){... on ProjectV2ItemFieldSingleSelectValue{name}}
        content{ ... on Issue{ number title url state createdAt updatedAt repository{nameWithOwner} issueType{name}
          author{login} labels(first:20){nodes{name}}
          assignees(first:3){nodes{login}} milestone{title dueOn state} parent{number}
          subIssuesSummary{total} issueDependenciesSummary{blockedBy}
          closedByPullRequestsReferences(first:5, includeClosedPrs:false){nodes{number updatedAt}} } } } } } } }""" % (ORG, PROJECT, STAGE_FIELD)
    stuck, no_priority, board, open_items, after = [], [], {}, [], None
    cutoff = TODAY - dt.timedelta(days=NEEDS_PRIORITY_DAYS)
    while True:
        vars_ = {"after": after} if after else {}
        items = graphql(q, **vars_)["organization"]["projectV2"]["items"]
        for it in items["nodes"]:
            c, s = it.get("content") or {}, (it.get("fieldValueByName") or {}).get("name")
            if c.get("url"):
                board[c["url"]] = {"id": it["id"], "stage": (it.get("stage") or {}).get("name"), "state": c.get("state")}
            if c.get("state") == "OPEN":
                open_items.append({"node": c, "status": s, "priority": (it.get("priority") or {}).get("name"),
                                   "risk": (it.get("risk") or {}).get("name")})
            if (c.get("state") == "OPEN" and s != "Done" and not it.get("priority")
                    and c["repository"]["nameWithOwner"] == f"{ORG}/{ISSUES_REPO}"
                    and (c.get("author") or {}).get("login") not in groomers
                    and "forming" not in {l["name"] for l in c["labels"]["nodes"]}
                    and parse_date(c["createdAt"]) >= cutoff):
                no_priority.append(c)
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
            return stuck, no_priority, board, open_items
        after = items["pageInfo"]["endCursor"]


# --- 4. lane floors -------------------------------------------------------

def is_candidate(it):
    """An open, groomed, unassigned ticket nobody is blocked on, ready for a person to hand out."""
    c = it["node"]
    return (it["status"] in ("Backlog", "To Do") and bool(it["priority"])
            and not c["assignees"]["nodes"]
            and c["repository"]["nameWithOwner"] == f"{ORG}/{ISSUES_REPO}"
            and (c.get("issueType") or {}).get("name") not in CANDIDATE_SKIP_TYPES
            and not labels(c) & CANDIDATE_SKIP_LABELS
            and not (c.get("subIssuesSummary") or {}).get("total")
            and not (c.get("issueDependenciesSummary") or {}).get("blockedBy")
            and not c["closedByPullRequestsReferences"]["nodes"])


def is_embed(c, epic):
    """A new embed provider: titled Embed: or Embed Request:, or a child of the Embed Requests epic.

    Bugs are not held: a Bug on an embed that already ships needs no provider approval.
    """
    if (c.get("issueType") or {}).get("name") == "Bug":
        return False
    return bool(EMBED_TITLE.match(c["title"])) or (epic is not None and (c.get("parent") or {}).get("number") == epic)


def embed_approvals(numbers, approver):
    """Issue numbers among these whose body or comments hold the approver's `## Decision: approved`."""
    if not numbers or not approver:
        return set()
    rx = re.compile(r"##\s*Decision:\s*approved", re.I)
    parts = " ".join(f"i{n}: issue(number:{n}){{number author{{login}} body comments(last:50){{nodes{{author{{login}} body}}}}}}"
                     for n in numbers)
    d = graphql('query{ repository(owner:"%s", name:"%s"){ %s } }' % (ORG, ISSUES_REPO, parts))["repository"]
    ok = set()
    for i in d.values():
        posts = [(i.get("author") or {}, i["body"])] + [(c.get("author") or {}, c["body"]) for c in i["comments"]["nodes"]]
        if any(a.get("login") == approver and rx.search(b or "") for a, b in posts):
            ok.add(i["number"])
    return ok


def open_milestone(c):
    m = c.get("milestone")
    return m if m and m.get("state") == "OPEN" else None


def candidate_key(it):
    m = open_milestone(it["node"])
    return (it["priority"] != "Hotfix", m is None, (m or {}).get("dueOn") or "9999",
            PRIORITY_RANK.get(it["priority"], 9), RISK_RANK.get(it["risk"], 1), it["node"]["createdAt"])


def fit(it, areas):
    """(group, why) for a lane with Areas: Hotfix, bugs, the person's areas, Low priority, the rest."""
    c = it["node"]
    if it["priority"] == "Hotfix":
        return 0, "Hotfix"
    if (c.get("issueType") or {}).get("name") == "Bug" or c["title"].lower().startswith("bug:"):
        return 1, "Bug"
    title = c["title"].lower()
    hit = next((a for a in areas if a in title), None)
    if hit:
        return 2, f"Area: {hit}"
    if it["priority"] == "Low":
        return 3, "Low priority"
    return 4, ""


def lane_report(items, lanes, embed_epic=None, approved_embeds=frozenset()):
    """Lanes under their To Do floor, each with up to LANE_CANDIDATES (item, why) pairs, plus the
    embed tickets left out for want of an approval."""
    to_do = {h: 0 for h in lanes}
    for it in items:
        if it["status"] == "To Do" and (it["node"].get("issueType") or {}).get("name") not in FLOOR_SKIP_TYPES:
            for a in it["node"]["assignees"]["nodes"]:
                if a["login"] in to_do:
                    to_do[a["login"]] += 1
    under = [{"handle": h, **lanes[h], "to_do": to_do[h]} for h in lanes if to_do[h] < lanes[h]["floor"]]
    if not under:
        return [], []
    pool, held = [], []
    for it in items:
        if not is_candidate(it):
            continue
        if is_embed(it["node"], embed_epic) and it["node"]["number"] not in approved_embeds:
            held.append(it)
        else:
            pool.append(it)
    pool.sort(key=candidate_key)
    for lane in under:
        if lane["areas"]:
            ranked = sorted(((it, fit(it, lane["areas"])) for it in pool), key=lambda p: p[1][0])
            lane["candidates"] = [(it, why) for it, (_, why) in ranked[:LANE_CANDIDATES]]
        else:
            lane["candidates"] = [(it, "") for it in pool[:LANE_CANDIDATES]]
    return under, sorted(held, key=candidate_key)


# --- 5. brief --------------------------------------------------------------

def lanes_phrase(n):
    return f"{n} lane under its floor" if n == 1 else f"{n} lanes under their floor"


def build_brief(promos, gated, applied, waiting, owed, stuck, intake, no_priority, phases, dry, features=None,
                lanes_under=(), embeds_held=()):
    overdue = [o for o in owed if o["by"] < TODAY]
    no_owner = [o for o in owed if not o["who"]]
    head = (f"**TL;DR:** {len(promos)} phase hand-off{'s' if len(promos) != 1 else ''}, {len(gated)} waiting on a go, "
            f"{sum(o['kind'] == 'needs-decision' for o in owed)} open decisions and "
            f"{sum(o['kind'] == 'follow-up' for o in owed)} follow-ups ({len(overdue)} overdue), "
            f"{len(intake) + len(no_priority)} in intake, {len(stuck)} stuck"
            + (f", {lanes_phrase(len(lanes_under))}." if lanes_under else "."))
    lines = [f"## Router brief, {TODAY:%a %b %-d}" + (" (dry run)" if dry else ""), "", head, ""]

    if TODAY.weekday() == 0:
        # Counts for the dev meeting only. Comms items stay in the rest of the brief.
        dev = lambda n: (n.get("issueType") or {}).get("name") not in MONDAY_SKIP_TYPES
        d_owed = [o for o in owed if dev(o["node"])]
        d_stuck = [x for x in stuck if dev(x["node"])]
        d_intake, d_no_pri = [n for n in intake if dev(n)], [n for n in no_priority if dev(n)]
        decisions = sum(o["kind"] == "needs-decision" for o in d_owed)
        late_follow = sum(o["kind"] == "follow-up" and o["by"] < TODAY for o in d_owed)
        pl = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
        counts = {"Decisions & follow-ups": f"{pl(decisions, 'decision')}, {pl(late_follow, 'overdue follow-up')}",
                  "Stuck": f"{len(d_stuck)} stuck",
                  "Intake": f"{len(d_intake)} to groom, {len(d_no_pri)} need a priority",
                  "Features": f"{len(features or [])} in flight, release-planning weeks only",
                  "Gates": f"{len(gated)} waiting on a go",
                  "Lane floors": lanes_phrase(len(lanes_under))}
        empty = (decisions == 0 and late_follow == 0 and not d_stuck and not d_intake and not d_no_pri and not gated
                 and not lanes_under)
        lines += ["### Monday agenda", "",
                  "Nothing needs the room this week. Skip the meeting." if empty else
                  "30 minutes, top to bottom. Skip any empty section. "
                  "Communications items are left out; they go to the weekly comms meeting.", ""]
        where = {"Decisions & follow-ups": f"[Monday view]({BOARD_VIEWS}{MONDAY_VIEW})",
                 "Stuck": f"[Monday view]({BOARD_VIEWS}{MONDAY_VIEW})", "Intake": f"[Monday view]({BOARD_VIEWS}{MONDAY_VIEW})",
                 "Features": "below", "Gates": f"[Monday view]({BOARD_VIEWS}{MONDAY_VIEW})", "Lane floors": "below"}
        for i, name in enumerate(["Decisions & follow-ups", "Stuck", "Intake", "Features", "Gates", "Lane floors"], 1):
            lines.append(f"{i}. **{name}**: {counts[name]} ({where[name]})")
        lines.append("")

    if promos:
        lines += ["### Handed off", ""]
        for p in promos:
            ok = applied.get(p["issue"]["number"])
            mark = "" if dry else (" (read back OK)" if ok else " (**write did not stick, check by hand**)")
            lines.append(f"- {link(p['issue'])} {quiet(p['issue']['title'])} → To Do, `{p['owner']}`{mark}")
        lines.append("")

    if gated:
        lines += ["### Waiting on a go", ""]
        for g in sorted(gated, key=lambda g: g["gate"]):
            lines.append(f"- `{g['gate']}`: {link(g['issue'])} {quiet(g['issue']['title'])} "
                         f"({phases[g['phase']]['name']}, part of {ref(g['issue']['parent'])}). Approve by moving it to To Do")
        lines.append("")

    if lanes_under:
        lines += ["### Lane floors", "",
                  "Check fit first, then top up a lane by assigning a candidate and moving it to To Do. "
                  "The router never assigns these.", ""]
        for l in lanes_under:
            short = l["floor"] - l["to_do"]
            lines += [f"**`{l['handle']}` ({l['name']})**: {l['to_do']} in To Do, floor {l['floor']}. "
                      f"Needs {short} more, `{l['approver'] or 'a groomer'}` approves.", ""]
            if not l["candidates"]:
                lines += ["No candidates: nothing groomed and unassigned is ready. Groom something for this lane.", ""]
                continue
            order = "bugs, then their areas, then Low priority" if l["areas"] else "pickup order"
            lines += [f"Candidates, {order}:", "",
                      "| Ticket | Why | Priority | Milestone | Risk | Status |", "|---|---|---|---|---|---|"]
            for it, why in l["candidates"]:
                c, m = it["node"], open_milestone(it["node"])
                lines.append(f"| {link(c)} {quiet(c['title']).replace('|', '/')} | {why or '-'} | {it['priority']} | "
                             f"{m['title'] if m else 'none'} | {it['risk'] or 'not set'} | {it['status']} |")
            lines.append("")
        if embeds_held:
            refs = ", ".join(link(it["node"]) for it in embeds_held)
            lines += [f"Left out {len(embeds_held)} embed ticket{'s' if len(embeds_held) != 1 else ''} with no approval "
                      f"comment: {refs}.", ""]

    if intake or no_priority:
        lines += ["### Intake", "",
                  f"{len(intake)} `forming` ticket{'s' if len(intake) != 1 else ''} waiting to be groomed"
                  + (f", {len(no_priority)} new ticket{'s' if len(no_priority) != 1 else ''} with no priority." if no_priority else "."), ""]
        lines += ["<details>", "<summary><b>Intake list</b></summary>", ""]
        for n in intake:
            who = (n.get("author") or {}).get("login", "?")
            lines.append(f"- {link(n)} {quiet(n['title'])}, filed by `{who}` {parse_date(n['createdAt']):%b %-d}")
        for n in no_priority:
            who = (n.get("author") or {}).get("login", "?")
            lines.append(f"- {link(n)} {quiet(n['title'])}, filed by `{who}`: needs a priority")
        lines += ["", "</details>", ""]

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
            what = quiet(o["what"] or o["node"]["title"]).replace("|", "/")[:90]
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
            lines.append(f"- {link(s['node'])} {quiet(s['node']['title'])}, `{s['who']}`, {s['idle']}d idle{pr}")
        lines += ["", "</details>", ""]

    if features:
        lines += ["<details>", f"<summary><b>Features in flight ({len(features)})</b></summary>", "",
                  "| Feature | Milestone | Done |", "|---|---|---|"]
        for f in features:
            lines.append(f"| {link(f['node'])} {quiet(f['node']['title']).replace('|', '/')} | {f['milestone']} | "
                         f"{f['done']} of {f['total']} |")
        lines += ["", "</details>", ""]

    if waiting:
        lines += ["<details>", f"<summary><b>Phase children the router did not move ({len(waiting)})</b></summary>", ""]
        for n, why in waiting:
            lines.append(f"- {link(n)} {quiet(n['title'])}: {why}")
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
    intake = find_intake()
    stuck, no_priority, board, open_items = find_stuck(load_groomers())
    lanes = load_lanes()
    embed_approver, embed_epic = load_embed_rule()
    lanes_under, embeds_held = lane_report(open_items, lanes, embed_epic)
    if lanes_under:
        maybe = [it["node"]["number"] for it in open_items if is_candidate(it) and is_embed(it["node"], embed_epic)]
        lanes_under, embeds_held = lane_report(open_items, lanes, embed_epic, embed_approvals(maybe, embed_approver))

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
            "intake": [{**item(n), "number": n["number"], "author": (n.get("author") or {}).get("login"),
                        "created": n["createdAt"][:10]} for n in intake],
            "needs_priority": [{**item(n), "number": n["number"], "author": (n.get("author") or {}).get("login"),
                                "created": n["createdAt"][:10]} for n in no_priority],
            "lanes_under_floor": [{"handle": l["handle"], "name": l["name"], "floor": l["floor"],
                                   "to_do": l["to_do"], "approver": l["approver"],
                                   "candidates": [{**item(it["node"]), "number": it["node"]["number"], "why": why,
                                                   "priority": it["priority"], "risk": it["risk"], "status": it["status"],
                                                   "milestone": (open_milestone(it["node"]) or {}).get("title")}
                                                  for it, why in l["candidates"]]} for l in lanes_under],
            "embeds_held": [{**item(it["node"]), "number": it["node"]["number"]} for it in embeds_held],
        }, indent=2))
        return

    applied, post_failed = {}, False
    if a.apply:
        try:
            added, removed = sync_gate_labels(gated)
            if added or removed:
                print(f"{GATE_LABEL}: added {added}, removed {removed}", file=sys.stderr)
        except RuntimeError as e:
            print(f"{GATE_LABEL} sync failed: {e}", file=sys.stderr)
        try:
            n_set, n_clear = sync_stages(desired_stages(gated, owed, stuck, intake, no_priority), board)
            if n_set or n_clear:
                print(f"{STAGE_FIELD}: set {n_set}, cleared {n_clear}", file=sys.stderr)
        except RuntimeError as e:
            print(f"{STAGE_FIELD} sync failed: {e}", file=sys.stderr)
        for p in promos:
            try:
                applied[p["issue"]["number"]] = apply_promotion(p, phases)
            except RuntimeError as e:
                applied[p["issue"]["number"]] = False
                print(f"promotion failed for {ref(p['issue'])}: {e}", file=sys.stderr)

    features = find_features() if TODAY.weekday() == 0 else None
    brief = build_brief(promos, gated, applied, waiting, owed, stuck, intake, no_priority, phases,
                        dry=not a.apply, features=features, lanes_under=lanes_under, embeds_held=embeds_held)
    if a.brief_file:
        Path(a.brief_file).write_text(brief)
    print(brief)

    if a.apply and not a.no_brief:
        if BRIEF_ISSUE is None:
            print("\nBRIEF_ISSUE is not set; brief printed only.", file=sys.stderr)
        else:
            try:
                gh("issue", "comment", str(BRIEF_ISSUE), "-R", f"{ORG}/{ISSUES_REPO}", "--body-file", "-", input_text=brief)
                print(f"\nPosted to {ORG}/{ISSUES_REPO}#{BRIEF_ISSUE}", file=sys.stderr)
            except RuntimeError as e:
                print(f"\nPosting the brief failed: {e}", file=sys.stderr)
                post_failed = True

    failed = [n for n, ok in applied.items() if not ok]
    sys.exit(1 if failed or post_failed else 0)


if __name__ == "__main__":
    main()
