#!/usr/bin/env python3
"""Status file for pr-feedback prep mode.

Prep mode runs unattended and leaves a review board packet for each PR it
prepped. This file is how everything else finds out what is ready: the review
session (SKILL.md Step 1) and anything outside Claude, such as a dashboard.

  python3 prep_status.py [--root DIR] run-start
  python3 prep_status.py [--root DIR] start   --pr REPO#N=SHA [--pr ...] --packet ID
  python3 prep_status.py [--root DIR] ready   --pr REPO#N=SHA [--pr ...] --packet ID
                         --questions N [--driven] [--results pass=8,fail=1]
                         [--cleanup done|failed|none] [--note TEXT]
  python3 prep_status.py [--root DIR] fail    --pr REPO#N=SHA [--pr ...] --reason TEXT
  python3 prep_status.py [--root DIR] get     REPO#N [--head SHA]
  python3 prep_status.py [--root DIR] run-end

The root defaults to ~/.claude/yalesites/pr-review-prep. status.json there looks
like this, keyed by `<repo>#<number>`:

  {"lastRun": "...", "runStartedAt": "...", "prs": {"yalesites-project#1608": {
     "state": "ready", "headSha": "...", "packetId": "ysp-1608",
     "packetDir": ".../packets/ysp-1608", "updatedAt": "...", "questions": 3,
     "driven": true, "results": {"pass": 8, "fail": 1}, "cleanup": "done"}}}

States: running, ready, failed. A `running` entry older than RUNNING_TTL is
reported as failed ("interrupted") by `get`, because a run that died never
writes its own failure. Writes are atomic (temp file, then rename) under a
lock, so a reader never sees half a file.
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


def effective(entry, head=None):
    """The entry as a reader should see it: interrupted runs fail, old heads are stale."""
    entry = dict(entry)
    if entry.get("state") == "running":
        started = parse_time(entry.get("updatedAt"))
        if not started or datetime.now(timezone.utc) - started > RUNNING_TTL:
            entry["state"] = "failed"
            entry["reason"] = "interrupted: the prep run stopped without finishing"
    if head and entry.get("state") == "ready" and not sha_matches(entry.get("headSha"), head):
        entry["state"] = "stale"
    return entry


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
        if name == "ready":
            s.add_argument("--questions", type=int, required=True)
            s.add_argument("--driven", action="store_true")
            s.add_argument("--results", default="")
            s.add_argument("--cleanup", choices=("done", "failed", "none"), default="none")
            s.add_argument("--note", default=None)
        if name == "fail":
            s.add_argument("--reason", required=True)

    g = sub.add_parser("get")
    g.add_argument("key")
    g.add_argument("--head", default=None)

    args = p.parse_args(argv)
    root = os.path.realpath(os.path.expanduser(args.root))

    if args.cmd == "get":
        entry = load(root)["prs"].get(args.key)
        if entry is None:
            print(json.dumps({"state": "none"}))
            return 1
        print(json.dumps(effective(entry, args.head), indent=2, sort_keys=True))
        return 0

    with locked(root):
        data = load(root)
        stamp = now()
        if args.cmd == "run-start":
            data["runStartedAt"] = stamp
        elif args.cmd == "run-end":
            data["lastRun"] = stamp
        else:
            for key, sha in parse_prs(args.pr):
                entry = {"state": {"start": "running", "ready": "ready", "fail": "failed"}[args.cmd],
                         "headSha": sha, "updatedAt": stamp}
                if args.cmd in ("start", "ready"):
                    entry["packetId"] = args.packet
                    entry["packetDir"] = os.path.join(root, "packets", args.packet)
                if args.cmd == "ready":
                    entry.update(questions=args.questions, driven=args.driven,
                                 results=parse_results(args.results), cleanup=args.cleanup)
                    if args.note:
                        entry["note"] = args.note
                if args.cmd == "fail":
                    entry["reason"] = args.reason
                data["prs"][key] = entry
        save(root, data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
