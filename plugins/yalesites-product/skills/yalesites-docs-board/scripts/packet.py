#!/usr/bin/env python3
"""Helpers for docs-board packets.

  python3 packet.py validate <packet-dir>
  python3 packet.py split-md <item-dir> <file.md> [--repo owner/repo --path repo/rel/path]
  python3 packet.py render <packet-dir> <item-id> [--out FILE]
  python3 packet.py status <owner/repo#N> <state> [--packet ID] [--target URL] [--note TEXT] [--result JSON]

`validate` checks a packet before the board opens, so a mistake shows up here
and not as a broken page in front of the reviewer. The rule that matters most:
on an edit, every block on the live page must appear in `ops` exactly once, as
keep, edit, or remove. A block left out of `ops` would vanish from the board
without anyone deciding to drop it.

`split-md` is the internal-docs version of capture.py. It cuts an existing
markdown file into sections at each heading and writes current.json, so a
README edit gets the same keep/edit/add/remove treatment as a page.

`render` prints the approved proposal as one markdown document, top to bottom:
kept and edited blocks as they will read, added blocks in place, removed blocks
left out. For internal docs that output is the file. For a page it is a
read-through of the copy, not something to paste.

`status` records where each ticket stands in
~/.claude/yalesites/docs-board/status.json, which the work dashboard reads.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

ITEM_ID = re.compile(r"^[A-Za-z0-9._-]+$")
TICKET = re.compile(r"^[\w.-]+/[\w.-]+#\d+$")
KINDS = ("edit", "new", "internal")
OPS = ("keep", "edit", "add", "remove")
STATES = ("drafting", "on-board", "changes", "approved", "building", "built", "skipped", "failed")
STATUS_FILE = os.path.expanduser("~/.claude/yalesites/docs-board/status.json")
EM_DASH = "\u2014"



def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def _texts(item):
    """Every reviewer-facing string in an item, with where it came from."""
    yield "summary", item.get("summary") or ""
    yield "build", item.get("build") or ""
    for n, note in enumerate(item.get("notes") or []):
        yield f"notes[{n}]", note
    for n, op in enumerate(item.get("ops") or []):
        for k in ("markdown", "why", "blockWhy"):
            if op.get(k):
                yield f"ops[{n}].{k}", op[k]


def validate(packet_dir):
    errors, warnings = [], []
    path = os.path.join(packet_dir, "packet.json")
    try:
        packet = read_json(path)
    except (OSError, ValueError) as exc:
        return [f"packet.json: {exc}"], []
    if not packet.get("title"):
        errors.append("packet: title is required")
    items = packet.get("items") or []
    if not items:
        errors.append("packet: items is empty")
    seen = set()
    for item in items:
        iid = str(item.get("id", ""))
        where = f"item {iid or '?'}"
        if not ITEM_ID.match(iid):
            errors.append(f"{where}: id must match {ITEM_ID.pattern}")
        if iid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(iid)
        ref = (item.get("ticket") or {}).get("ref", "")
        if not TICKET.match(ref):
            errors.append(f"{where}: ticket.ref must be owner/repo#N, got {ref!r}")
        kind = item.get("kind")
        if kind not in KINDS:
            errors.append(f"{where}: kind must be one of {KINDS}")
            continue
        target = item.get("target") or {}
        if kind == "new" and not target.get("path"):
            errors.append(f"{where}: a new page needs target.path (the proposed URL alias)")
        if kind == "edit" and not target.get("url"):
            errors.append(f"{where}: an edit needs target.url")
        if kind == "internal" and not (target.get("repo") and target.get("file")):
            errors.append(f"{where}: internal docs need target.repo and target.file")

        current = None
        if item.get("current"):
            cpath = os.path.join(packet_dir, item["current"])
            try:
                current = read_json(cpath)
            except (OSError, ValueError) as exc:
                errors.append(f"{where}: current {item['current']}: {exc}")
        if kind == "edit":
            if not current:
                errors.append(f"{where}: an edit needs current (run capture.py)")
            elif not current.get("screenshot"):
                errors.append(f"{where}: current has no screenshot (status {current.get('status')}). "
                              "If the page is gone, make this a new page")
            elif not os.path.exists(os.path.join(packet_dir, os.path.dirname(item["current"]), current["screenshot"])):
                errors.append(f"{where}: screenshot file is missing")
        if kind == "new" and current:
            warnings.append(f"{where}: a new page has a current capture. Did you mean kind=edit?")

        ops = item.get("ops") or []
        if not ops:
            errors.append(f"{where}: ops is empty")
        blocks = {b["id"]: b for b in (current or {}).get("blocks", [])}
        used = {}
        for n, op in enumerate(ops):
            o = op.get("op")
            at = f"{where} ops[{n}]"
            if o not in OPS:
                errors.append(f"{at}: op must be one of {OPS}")
                continue
            if o == "add":
                if not op.get("block"):
                    errors.append(f"{at}: add needs block (the Layout Builder block, or 'Section' for markdown)")
                if not (op.get("markdown") or "").strip():
                    errors.append(f"{at}: add needs markdown")
                if op.get("ref"):
                    errors.append(f"{at}: add must not have a ref. Its place is its position in ops")
                continue
            if kind == "new":
                errors.append(f"{at}: a new page can only add")
                continue
            ref = op.get("ref")
            if ref not in blocks:
                errors.append(f"{at}: ref {ref!r} is not a block in current")
                continue
            used[ref] = used.get(ref, 0) + 1
            if o == "edit":
                new = (op.get("markdown") or "").strip()
                if not new:
                    errors.append(f"{at}: edit needs markdown")
                elif new == blocks[ref].get("markdown", "").strip():
                    errors.append(f"{at}: edit of {ref} does not change anything. Use keep")
                if not op.get("why"):
                    warnings.append(f"{at}: edit has no why")
            if o == "remove" and not op.get("why"):
                errors.append(f"{at}: remove needs a why. Dropping content is a call the reviewer makes")
        if current is not None:
            for bid in blocks:
                if used.get(bid, 0) == 0:
                    errors.append(f"{where}: block {bid} ({blocks[bid].get('type')}) is not in ops. "
                                  "Add it as keep, edit, or remove")
                elif used[bid] > 1:
                    errors.append(f"{where}: block {bid} appears {used[bid]} times in ops")
        if not any(op.get("op") in ("edit", "add", "remove") for op in ops):
            warnings.append(f"{where}: no changes proposed. Should this ticket be skipped?")

        for field, text in _texts(item):
            if EM_DASH in text:
                errors.append(f"{where} {field}: contains an em dash")
            if kind != "internal" and "https://yalesites.yale.edu/" in text and field.startswith("ops"):
                warnings.append(f"{where} {field}: absolute yalesites.yale.edu link. Use a relative path")
        if item.get("draft") and not os.path.exists(os.path.join(packet_dir, item["draft"])):
            errors.append(f"{where}: draft {item['draft']} is missing")
    return errors, warnings


def split_md(text):
    """Cut markdown into sections at headings. Text before the first heading is its own section."""
    sections, buf = [], []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and re.match(r"^#{1,6} ", line) and any(x.strip() for x in buf):
            sections.append("\n".join(buf).strip())
            buf = []
        buf.append(line)
    if any(x.strip() for x in buf):
        sections.append("\n".join(buf).strip())
    return [{"id": f"s{i + 1}", "type": "Section", "markdown": s} for i, s in enumerate(sections)]


def render(packet_dir, item_id):
    pk = read_json(os.path.join(packet_dir, "packet.json"))
    item = next((i for i in pk.get("items", []) if str(i.get("id")) == str(item_id)), None)
    if item is None:
        sys.exit(f"No item {item_id} in {packet_dir}")
    blocks = {}
    if item.get("current"):
        blocks = {b["id"]: b for b in read_json(os.path.join(packet_dir, item["current"])).get("blocks", [])}
    parts = []
    for op in item.get("ops", []):
        if op["op"] == "keep":
            parts.append(blocks[op["ref"]]["markdown"])
        elif op["op"] in ("edit", "add"):
            parts.append(op["markdown"])
    return "\n\n".join(p.strip() for p in parts if p and p.strip()) + "\n"


def set_status(ref, state, packet=None, target=None, note=None, result=None, path=STATUS_FILE):
    if not TICKET.match(ref):
        sys.exit(f"ticket must be owner/repo#N, got {ref!r}")
    if state not in STATES:
        sys.exit(f"state must be one of {STATES}")
    try:
        data = read_json(path)
    except (OSError, ValueError):
        data = {"tickets": {}}
    entry = data.setdefault("tickets", {}).get(ref, {})
    entry.update({"state": state, "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    for k, v in (("packet", packet), ("target", target), ("note", note)):
        if v is not None:
            entry[k] = v
    if result is not None:
        entry["result"] = json.loads(result) if isinstance(result, str) else result
    data["tickets"][ref] = entry
    data["updatedAt"] = entry["updatedAt"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("packet_dir")
    s = sub.add_parser("split-md")
    s.add_argument("item_dir")
    s.add_argument("file")
    s.add_argument("--repo")
    s.add_argument("--path")
    r = sub.add_parser("render")
    r.add_argument("packet_dir")
    r.add_argument("item_id")
    r.add_argument("--out")
    st = sub.add_parser("status")
    st.add_argument("ticket")
    st.add_argument("state")
    st.add_argument("--packet")
    st.add_argument("--target")
    st.add_argument("--note")
    st.add_argument("--result")
    a = ap.parse_args()

    if a.cmd == "validate":
        errors, warnings = validate(a.packet_dir)
        for w in warnings:
            print(f"warning: {w}")
        for e in errors:
            print(f"ERROR: {e}")
        print("OK" if not errors else f"{len(errors)} error(s)")
        sys.exit(1 if errors else 0)
    if a.cmd == "split-md":
        with open(a.file, encoding="utf-8") as f:
            blocks = split_md(f.read())
        os.makedirs(a.item_dir, exist_ok=True)
        out = {"kind": "file", "repo": a.repo, "file": a.path or a.file, "screenshot": None, "blocks": blocks}
        with open(os.path.join(a.item_dir, "current.json"), "w") as f:
            json.dump(out, f, indent=1)
        print(f"{len(blocks)} sections -> {os.path.join(a.item_dir, 'current.json')}")
        return
    if a.cmd == "render":
        text = render(a.packet_dir, a.item_id)
        if a.out:
            with open(a.out, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"wrote {a.out}")
        else:
            sys.stdout.write(text)
        return
    if a.cmd == "status":
        entry = set_status(a.ticket, a.state, a.packet, a.target, a.note, a.result)
        print(json.dumps(entry))


if __name__ == "__main__":
    main()
