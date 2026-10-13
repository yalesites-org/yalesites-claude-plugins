#!/usr/bin/env python3
"""Status file for pr-feedback prep mode.

Prep mode runs unattended and leaves a review board packet for each PR it
prepped. This file is how everything else finds out what is ready: the review
session (SKILL.md Step 1) and anything outside Claude, such as a dashboard.

  python3 prep_status.py [--root DIR] run-start
  python3 prep_status.py [--root DIR] start     --pr REPO#N=SHA [--pr ...] --packet ID
                         --scope DIMS [--run-dir DIR] [--packet-dir DIR] [--force]
  python3 prep_status.py [--root DIR] heartbeat --packet ID --claim TOKEN
  python3 prep_status.py [--root DIR] ready     --pr REPO#N=SHA [--pr ...] --packet ID
                         --scope DIMS --claim TOKEN --questions N [--driven]
                         [--results pass=8,fail=1] [--cleanup done|failed|none] [--note TEXT]
                         [--packet-dir DIR] [--run-dir DIR]
  python3 prep_status.py [--root DIR] fail      --pr REPO#N=SHA [--pr ...] --claim TOKEN
                         --reason TEXT
  python3 prep_status.py [--root DIR] get       REPO#N [--head SHA] [--scope DIMS]
  python3 prep_status.py [--root DIR] run-end

DIMS is the reviewer scope the packet was built for: a comma list of review
dimensions (`functional,product`) or `all` for an unscoped reviewer.

The root defaults to ~/.claude/yalesites/pr-review-prep. status.json there looks
like this, keyed by `<repo>#<number>`:

  {"lastRun": "...", "runStartedAt": "...", "prs": {"yalesites-project#1608": {
     "state": "ready", "headSha": "...", "scope": ["functional", "product"],
     "unit": ["yalesites-project#1608", "component-library-twig#774"],
     "packetId": "ysp-1608", "packetDir": ".../packets/ysp-1608-abc1234-20261004T130500Z",
     "runDir": "~/.claude/yalesites/pr-feedback/runs/yalesites-project-1608-2026-10-04",
     "claim": "3f9c...", "updatedAt": "...", "questions": 3, "driven": true,
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
never the first. A claim that goes through prints a random `claim` token and
stores it on every entry in the unit, together with `packetDir`, the folder the
packet is built in, and `runDir`, the drive-it run folder when `--run-dir` names
one. `packetDir` is versioned, `packets/<id>-<sha7>-<builtAt>`, from the first
PR's head and the claim time, so a rebuild gets a new folder and nothing is ever
renamed or overwritten: a review session still serving the old folder keeps
working, and an old folder stays as the record of its review. `ready` and `fail`
need the token back: when a stored entry carries a different one, another run has
claimed the unit since (the first run outlived the TTL), and the write is refused
with exit 2 so a finished zombie cannot overwrite the live run's entry. Both
mark every entry that carries the token, not only the PRs named with `--pr`, so a
sibling never stays `running` on its own, and both carry `packetDir` and `runDir`
over from the claim. `heartbeat` only re-stamps entries still inside the TTL and
only under the same token; it exits 1 otherwise, which tells the run it has lost
the claim. Writes are atomic (temp file, then rename) under a lock, so a reader
never sees half a file. A status.json that cannot be parsed is never replaced:
every locked write copies it to `status.json.corrupt-<timestamp>` and refuses
with exit 2, and `get` reports it as `unreadable`, until someone fixes or
removes the file.
"""
import argparse
import contextlib
import fcntl
import json
import os
import secrets
import shutil
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


def iso_basic(stamp):
    """`2026-10-04T13:05:00+00:00` -> `20261004T130500Z`, for folder and file names."""
    return parse_time(stamp).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


class Unreadable(Exception):
    """status.json exists but cannot be read as the status map."""


def load(root):
    path = os.path.join(root, "status.json")
    try:
        with open(path) as f:
            raw = f.read()
    except FileNotFoundError:
        return {"prs": {}}
    except OSError as e:
        raise Unreadable(f"status.json could not be read: {e}")
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise Unreadable(f"status.json is not valid JSON ({e})")
    if not isinstance(data, dict) or not isinstance(data.get("prs", {}), dict):
        raise Unreadable("status.json is not a JSON object with a prs map")
    data.setdefault("prs", {})
    return data


def set_aside(root, stamp):
    """Copy a corrupt status.json next to itself, once, and return the copy's path.

    The original stays where it is, so nothing a run wrote before the file broke
    is lost, and a second refused write does not make a second copy of the same
    bytes.
    """
    src = os.path.join(root, "status.json")
    try:
        with open(src, "rb") as f:
            bad = f.read()
    except OSError:
        return None
    for name in sorted(os.listdir(root)):
        if name.startswith("status.json.corrupt-"):
            with open(os.path.join(root, name), "rb") as f:
                if f.read() == bad:
                    return os.path.join(root, name)
    dest = os.path.join(root, f"status.json.corrupt-{iso_basic(stamp)}")
    n = 1
    while os.path.exists(dest):
        dest = os.path.join(root, f"status.json.corrupt-{iso_basic(stamp)}-{n}")
        n += 1
    shutil.copyfile(src, dest)
    return dest


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
    if scope and entry.get("scope") and entry["state"] in ("ready", "running", "failed") \
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


def packet_dir(root, packet, prs, stamp):
    """The versioned folder a packet is built in: packets/<id>-<sha7>-<builtAt>."""
    return os.path.join(root, "packets", f"{packet}-{prs[0][1][:7]}-{iso_basic(stamp)}")


def under_claim(data, prs, token):
    """The PRs given plus every stored entry that carries the same token.

    `start` stamps one token on the whole unit, so the token is the unit: a
    `ready` or `fail` that names only some of the PRs still settles all of them,
    and no sibling is left `running` until the TTL. Siblings not named keep the
    head they were claimed at.
    """
    prs = list(prs)
    if not token:
        return prs
    passed = {key for key, _ in prs}
    order = next((e.get("unit") or [] for e in data["prs"].values() if e.get("claim") == token), [])
    extras = [key for key, e in data["prs"].items() if e.get("claim") == token and key not in passed]
    extras.sort(key=lambda key: (order.index(key) if key in order else len(order), key))
    return prs + [(key, data["prs"][key].get("headSha")) for key in extras]


def carried(data, prs):
    """`packetDir`, `runDir` and `scope` as the claim recorded them, for ready and fail to keep."""
    fields = {}
    for key, _ in prs:
        stored = data["prs"].get(key) or {}
        for field in ("packetDir", "runDir", "scope"):
            if stored.get(field) and field not in fields:
                fields[field] = stored[field]
    return fields


def lost_claim(data, keys, token):
    """The PR whose stored entry belongs to another claim, or None.

    Only `start` hands out tokens, so a stored token that differs from the one
    given means another run claimed the unit after this one did, whether that
    run is still `running` or has already written `ready` or `failed`. An entry
    without a token (none, or written before claims existed) is open to anyone.
    """
    for key in keys:
        stored = data["prs"].get(key, {}).get("claim")
        if stored and stored != token:
            return key
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
        if name in ("start", "ready"):
            s.add_argument("--packet-dir", default=None,
                           help="where the packet is built; start computes a versioned one when absent")
            s.add_argument("--run-dir", default=None, help="the drive-it run folder")
        if name == "start":
            s.add_argument("--force", action="store_true")
        else:
            s.add_argument("--claim", default=None, help="the token `start` printed")
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
    h.add_argument("--claim", required=True, help="the token `start` printed")

    g = sub.add_parser("get")
    g.add_argument("key")
    g.add_argument("--head", default=None)
    g.add_argument("--scope", default=None)

    args = p.parse_args(argv)
    root = os.path.realpath(os.path.expanduser(args.root))

    if args.cmd == "get":
        try:
            entry = load(root)["prs"].get(args.key)
        except Unreadable as e:
            print(json.dumps({"state": "unreadable", "reason": str(e)}))
            return EXIT_REFUSED
        if entry is None:
            print(json.dumps({"state": "none"}))
            return 1
        scope = parse_scope(args.scope) if args.scope else None
        print(json.dumps(effective(entry, args.head, scope), indent=2, sort_keys=True))
        return 0

    with locked(root):
        stamp = now()
        try:
            data = load(root)
        except Unreadable as e:
            copy = set_aside(root, stamp)
            print(json.dumps({"written": False, "reason":
                              f"{e}; nothing was written. A copy of the file is at {copy}. "
                              "Fix or remove status.json before the next write"}))
            return EXIT_REFUSED
        if args.cmd == "run-start":
            data["runStartedAt"] = stamp
        elif args.cmd == "run-end":
            data["lastRun"] = stamp
        elif args.cmd == "heartbeat":
            hits = [e for e in data["prs"].values()
                    if e.get("state") == "running" and e.get("packetId") == args.packet]
            # An entry past the TTL already reads as interrupted, and another run may have
            # taken the multidev on that reading. Stamping it back to life would put two
            # runs on the same multidev, so a stale run is told it lost the claim instead.
            live = [e for e in hits if effective(e)["state"] == "running"
                    and e.get("claim") == args.claim]
            if not live:
                if not hits:
                    reason = f"no running entry for packet {args.packet}"
                elif any(e.get("claim") != args.claim for e in hits):
                    reason = f"packet {args.packet} was claimed by another run; stop driving"
                else:
                    reason = f"the claim on packet {args.packet} expired at " \
                             f"{hits[0].get('updatedAt')} plus {RUNNING_TTL}; stop driving"
                print(json.dumps({"heartbeat": False, "reason": reason}))
                return 1
            for entry in live:
                entry["updatedAt"] = stamp
            print(json.dumps({"heartbeat": True, "packet": args.packet, "updatedAt": stamp}))
        else:
            prs = parse_prs(args.pr)
            scope = parse_scope(args.scope) if args.cmd in ("start", "ready") else None
            folders = {}
            if args.cmd == "start":
                refused = claim(data, prs, scope, args.force)
                if refused:
                    print(json.dumps({"claimed": False, "packet": args.packet, "reason": refused}))
                    return EXIT_REFUSED
                token = secrets.token_hex(8)
                folders["packetDir"] = args.packet_dir or packet_dir(root, args.packet, prs, stamp)
                if args.run_dir:
                    folders["runDir"] = args.run_dir
            else:
                token = args.claim
                taken = lost_claim(data, [key for key, _ in prs], token)
                if taken:
                    holder = data["prs"][taken]
                    print(json.dumps({"recorded": False, "prs": [key for key, _ in prs], "reason":
                                      f"{taken} was claimed by another run (packet {holder.get('packetId')}, "
                                      f"now {holder.get('state')} since {holder.get('updatedAt')}); "
                                      f"this run's claim is lost, so its result is not recorded"}))
                    return EXIT_REFUSED
                prs = under_claim(data, prs, token)
                # A claim is only good inside the TTL. Past it, a live review may already
                # have read the entry as failed, cleaned up, and started its own drive, so a
                # late ready or fail must not turn the entry back over to this run.
                expired = [key for key, _ in prs
                           if (data["prs"].get(key) or {}).get("state") == "running"
                           and effective(data["prs"][key])["state"] != "running"]
                if expired:
                    print(json.dumps({"recorded": False, "prs": [key for key, _ in prs], "reason":
                                      f"the claim on {', '.join(expired)} expired (no heartbeat inside "
                                      f"{int(RUNNING_TTL.total_seconds() // 60)} minutes); this run's result "
                                      f"is not recorded, and its multidev content needs D5 cleanup"}))
                    return EXIT_REFUSED
                folders = carried(data, prs)
                claimed_scope = folders.pop("scope", None)
                if args.cmd == "fail":
                    scope = claimed_scope
                if args.cmd == "ready":
                    if args.packet_dir:
                        folders["packetDir"] = args.packet_dir
                    if args.run_dir:
                        folders["runDir"] = args.run_dir
                    if not folders.get("packetDir"):
                        raise SystemExit("ready needs the packet folder: claim the unit with start first, "
                                         "or pass --packet-dir")
            unit = [key for key, _ in prs]
            for key, sha in prs:
                entry = {"state": {"start": "running", "ready": "ready", "fail": "failed"}[args.cmd],
                         "headSha": sha, "unit": unit, "updatedAt": stamp, **folders}
                if token:
                    entry["claim"] = token
                if args.cmd in ("start", "ready"):
                    entry["packetId"] = args.packet
                    entry["scope"] = scope
                elif scope:
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
                print(json.dumps({"claimed": True, "packet": args.packet, "prs": unit, "claim": token, **folders}))
            else:
                print(json.dumps({"recorded": True, "prs": unit}))
        save(root, data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
