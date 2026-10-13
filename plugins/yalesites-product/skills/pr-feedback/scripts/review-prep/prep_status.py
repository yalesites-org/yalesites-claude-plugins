#!/usr/bin/env python3
"""Status file for pr-feedback prep mode.

Prep mode runs unattended and leaves a review board packet for each PR it
prepped. This file is how everything else finds out what is ready: the review
session (SKILL.md Step 1) and anything outside Claude, such as a dashboard.

  python3 prep_status.py [--root DIR] run-start
  python3 prep_status.py [--root DIR] start     --pr REPO#N=SHA [--pr ...] --packet ID
                         --scope DIMS [--force]
  python3 prep_status.py [--root DIR] heartbeat --packet ID
  python3 prep_status.py [--root DIR] ready     --pr REPO#N=SHA [--pr ...] --packet ID
                         --scope DIMS --questions N [--driven] [--results pass=8,fail=1]
                         [--cleanup done|failed|none] [--note TEXT]
  python3 prep_status.py [--root DIR] fail      --pr REPO#N=SHA [--pr ...] --reason TEXT
  python3 prep_status.py [--root DIR] get       REPO#N [--head SHA] [--scope DIMS]
  python3 prep_status.py [--root DIR] run-end

DIMS is the reviewer scope the packet was built for: a comma list of review
dimensions (`functional,product`) or `all` for an unscoped reviewer.

The root defaults to ~/.claude/yalesites/pr-review-prep. status.json there looks
like this, keyed by `<repo>#<number>`:

  {"lastRun": "...", "runStartedAt": "...", "prs": {"yalesites-project#1608": {
     "state": "ready", "headSha": "...", "scope": ["functional", "product"],
     "unit": ["yalesites-project#1608", "component-library-twig#774"],
     "packetId": "ysp-1608", "packetDir": ".../packets/ysp-1608",
     "updatedAt": "...", "questions": 3, "driven": true,
     "results": {"pass": 8, "fail": 1}, "cleanup": "done"}}}

States: running, ready, failed. `get` reports what a reader should act on:
a `running` entry whose updatedAt is older than RUNNING_TTL is reported as
failed ("interrupted"), because a run that died never writes its own failure
(`heartbeat` keeps a live run inside the TTL); and any entry whose head or
scope differs from the `--head` and `--scope` given is reported as `stale`,
with `previousState` saying what it was.

`start` is the claim. It runs under the lock and refuses, with a nonzero exit
and a JSON line saying why, when any PR in the unit is `running` inside the
TTL, when every PR already reads `ready` for these heads and this scope, or
when every PR already `failed` on these heads. `--force` overrides the last two,
never the first. Writes are atomic (temp file, then rename) under a lock, so a
reader never sees half a file.
"""
import argparse
import contextlib
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

DEFAULT_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "yalesites", "pr-review-prep")
RUNNING_TTL = timedelta(minutes=90)
EXIT_REFUSED = 2


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_time(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def sha_matches(a, b):
    """Full and short SHAs both turn up, so compare by a 7+ character prefix."""
    if not a or not b:
        return False
    n = min(len(a), len(b))
    return n >= 7 and a[:n] == b[:n]


def parse_scope(value):
    """`functional,product` -> ["functional", "product"]; `all` -> ["all"]."""
    dims = sorted({part.strip().lower() for part in (value or "").split(",") if part.strip()})
    if not dims:
        raise SystemExit("--scope must be a comma list of dimensions, or all")
    if "all" in dims and len(dims) > 1:
        raise SystemExit("--scope all cannot be combined with other dimensions")
    return dims


@contextlib.contextmanager
def locked(root):
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def load(root):
    try:
        with open(os.path.join(root, "status.json")) as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    data.setdefault("prs", {})
    return data


def save(root, data):
    fd, tmp = tempfile.mkstemp(dir=root, prefix=".status-", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, os.path.join(root, "status.json"))


def parse_prs(values):
    prs = []
    for value in values:
        key, sep, sha = value.partition("=")
        repo, hash_, number = key.partition("#")
        if not (sep and sha and hash_ and repo and number.isdigit()):
            raise SystemExit(f"--pr must look like REPO#N=SHA, got {value!r}")
        prs.append((key, sha))
    return prs


def parse_results(value):
    results = {}
    if not value:
        return results
    for part in value.split(","):
        name, sep, count = part.partition("=")
        if not (sep and count.isdigit()):
            raise SystemExit(f"--results must look like pass=8,fail=1, got {value!r}")
        results[name.strip()] = int(count)
    return results


def effective(entry, head=None, scope=None):
    """The entry as a reader should see it.

    Interrupted runs fail. An entry recorded against another head, or built for
    another reviewer scope, is stale whatever its state was: a failure on an old
    head says nothing about the new one, and a run on an old head is not prepping
    the one under review.
    """
    entry = dict(entry)
    if entry.get("state") == "running":
        stamped = parse_time(entry.get("updatedAt"))
        if not stamped or datetime.now(timezone.utc) - stamped > RUNNING_TTL:
            entry["state"] = "failed"
            entry["reason"] = "interrupted: the prep run stopped without finishing"
    if head and not sha_matches(entry.get("headSha"), head):
        return _stale(entry, f"recorded against {entry.get('headSha')}, the head is now {head}")
    if scope and entry.get("scope") and entry["state"] in ("ready", "running") \
            and parse_scope(",".join(entry["scope"])) != parse_scope(",".join(scope)):
        return _stale(entry, f"prepped for scope {','.join(entry['scope'])}, "
                             f"this review is scoped to {','.join(scope)}")
    return entry


def _stale(entry, why):
    entry["previousState"] = entry["state"]
    entry["state"] = "stale"
    entry["reason"] = why
    return entry


def claim(data, prs, scope, force):
    """Decide whether this run may take the unit. Returns None, or the refusal reason."""
    states = {}
    for key, sha in prs:
        entry = data["prs"].get(key)
        states[key] = effective(entry, sha, scope) if entry else {"state": "none"}
    # A run on an old head reads as stale, but it is still driving the same multidev.
    running = [k for k, e in states.items()
               if e["state"] == "running" or e.get("previousState") == "running"]
    if running:
        return f"another prep run has {', '.join(running)} (running since " \
               f"{states[running[0]].get('updatedAt')}); wait for it or for the TTL to pass"
    if force:
        return None
    if all(e["state"] == "ready" for e in states.values()):
        return "the packet is current for these heads and this scope; pass --force to rebuild it"
    # Only a failure the run wrote itself counts. An interrupted run (a `running` entry past
    # the TTL) reads as failed too, and that is the case the next run should pick up.
    recorded = [data["prs"].get(k, {}).get("state") == "failed" for k in states]
    if all(recorded) and all(e["state"] == "failed" for e in states.values()):
        first = next(iter(states.values()))
        return f"already failed on these heads: {first.get('reason')}; " \
               "it is retried when the head moves, or with --force"
    return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=DEFAULT_ROOT)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("run-start")
    sub.add_parser("run-end")

    for name in ("start", "ready", "fail"):
        s = sub.add_parser(name)
        s.add_argument("--pr", action="append", required=True)
        if name in ("start", "ready"):
            s.add_argument("--packet", required=True)
            s.add_argument("--scope", required=True)
        if name == "start":
            s.add_argument("--force", action="store_true")
        if name == "ready":
            s.add_argument("--questions", type=int, required=True)
            s.add_argument("--driven", action="store_true")
            s.add_argument("--results", default="")
            s.add_argument("--cleanup", choices=("done", "failed", "none"), default="none")
            s.add_argument("--note", default=None)
        if name == "fail":
            s.add_argument("--reason", required=True)

    h = sub.add_parser("heartbeat")
    h.add_argument("--packet", required=True)

    g = sub.add_parser("get")
    g.add_argument("key")
    g.add_argument("--head", default=None)
    g.add_argument("--scope", default=None)

    args = p.parse_args(argv)
    root = os.path.realpath(os.path.expanduser(args.root))

    if args.cmd == "get":
        entry = load(root)["prs"].get(args.key)
        if entry is None:
            print(json.dumps({"state": "none"}))
            return 1
        scope = parse_scope(args.scope) if args.scope else None
        print(json.dumps(effective(entry, args.head, scope), indent=2, sort_keys=True))
        return 0

    with locked(root):
        data = load(root)
        stamp = now()
        if args.cmd == "run-start":
            data["runStartedAt"] = stamp
        elif args.cmd == "run-end":
            data["lastRun"] = stamp
        elif args.cmd == "heartbeat":
            hits = [e for e in data["prs"].values()
                    if e.get("state") == "running" and e.get("packetId") == args.packet]
            for entry in hits:
                entry["updatedAt"] = stamp
            if not hits:
                print(json.dumps({"heartbeat": False, "reason": f"no running entry for packet {args.packet}"}))
                return 1
            print(json.dumps({"heartbeat": True, "packet": args.packet, "updatedAt": stamp}))
        else:
            prs = parse_prs(args.pr)
            unit = [key for key, _ in prs]
            scope = parse_scope(args.scope) if args.cmd in ("start", "ready") else None
            if args.cmd == "start":
                refused = claim(data, prs, scope, args.force)
                if refused:
                    print(json.dumps({"claimed": False, "packet": args.packet, "reason": refused}))
                    return EXIT_REFUSED
            for key, sha in prs:
                entry = {"state": {"start": "running", "ready": "ready", "fail": "failed"}[args.cmd],
                         "headSha": sha, "unit": unit, "updatedAt": stamp}
                if args.cmd in ("start", "ready"):
                    entry["packetId"] = args.packet
                    entry["packetDir"] = os.path.join(root, "packets", args.packet)
                    entry["scope"] = scope
                if args.cmd == "ready":
                    entry.update(questions=args.questions, driven=args.driven,
                                 results=parse_results(args.results), cleanup=args.cleanup)
                    if args.note:
                        entry["note"] = args.note
                if args.cmd == "fail":
                    entry["reason"] = args.reason
                data["prs"][key] = entry
            if args.cmd == "start":
                print(json.dumps({"claimed": True, "packet": args.packet, "prs": unit}))
        save(root, data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
