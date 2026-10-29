#!/usr/bin/env python3
"""Helpers for docs-board packets.

  python3 packet.py validate <packet-dir>
  python3 packet.py split-md <item-dir> <file.md> [--repo owner/repo --path repo/rel/path]
  python3 packet.py render <packet-dir> <item-id> [--out FILE]
  python3 packet.py status <owner/repo#N> <state> [--packet ID] [--item ID] [--target URL] [--note TEXT] [--result JSON]

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
`built`, `building`, and `published` also lock the ticket's item in its packet.json
(`"locked": true`): the board shows a locked item read-only with a Built badge
and leaves it out of decisions.json, so a later round cannot approve it again.
`failed` takes the lock off and bumps the item's `revision`, so the board
treats it as undecided: the approve that led to the failed build is never
sent again, and a page that half-built needs a fresh approve.

The item is found by its id (`--item`), or by the ticket ref when the packet
has exactly one item for it. `validate` rejects two items with the same
ticket.ref: one ticket touching two pages is two items with the ref suffixed
(`#1818-a`, `#1818-b`), so status and the lock never land on the wrong page.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

ITEM_ID = re.compile(r"^[A-Za-z0-9._-]+$")
# An optional -suffix after the number, for one ticket that touches two
# pages: each page is its own item with its own ref (#1818-a, #1818-b).
TICKET = re.compile(r"^[\w.-]+/[\w.-]+#\d+(-[A-Za-z0-9]+)?$")
KINDS = ("edit", "new", "internal")
OPS = ("keep", "edit", "add", "remove")
STATES = ("drafting", "on-board", "changes", "approved", "building", "built", "published", "skipped", "failed")
STATUS_FILE = os.path.expanduser("~/.claude/yalesites/docs-board/status.json")
PACKETS_DIR = os.path.expanduser("~/.claude/yalesites/docs-board/packets")
LOCKING = {"built": True, "building": True, "published": True, "failed": False}
EM_DASH = "\u2014"



def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    """Write through a temp file, so a reader never sees half a file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


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
    seen, refs = set(), set()
    for item in items:
        iid = str(item.get("id", ""))
        where = f"item {iid or '?'}"
        if not ITEM_ID.match(iid):
            errors.append(f"{where}: id must match {ITEM_ID.pattern}")
        if iid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(iid)
        ticket = item.get("ticket") or {}
        ref = ticket.get("ref", "")
        if not TICKET.match(ref):
            errors.append(f"{where}: ticket.ref must be owner/repo#N, got {ref!r}")
        # Status and the lock are recorded per ref. Two items on one ref would
        # share them, so one page being built would lock, or skip, the other.
        elif ref in refs:
            errors.append(f"{where}: duplicate ticket.ref {ref}. One ticket touching two pages is two items with "
                          f"distinct ids and the ref suffixed ({ref}-a, {ref}-b)")
        refs.add(ref)
        # The board shows both on every card and in the nav, so a packet without
        # them must fail here rather than in front of the reviewer.
        for field in ("title", "url"):
            if not (ticket.get(field) or "").strip():
                errors.append(f"{where}: ticket.{field} is required")
        kind = item.get("kind")
        if kind not in KINDS:
            errors.append(f"{where}: kind must be one of {KINDS}")
            continue
        if "locked" in item and not isinstance(item["locked"], bool):
            errors.append(f"{where}: locked must be true or false. packet.py status sets it; do not write it by hand")
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


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def split_md(text):
    """Cut markdown into sections at headings. Text before the first heading is its own section.

    Every byte of the file lands in exactly one section, blank-line runs and
    the final newline included, so that `render` of all-keep ops gives the file
    back unchanged. A heading inside a fenced code block (``` or ~~~, three or
    more characters, closed only by the same character at the same or greater
    length) does not start a section.
    """
    sections, buf = [], []
    fence = None
    for line in text.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        m = FENCE.match(bare)
        if fence is None:
            if m:
                fence = m.group(1)
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not bare[m.end():].strip():
            fence = None
        if fence is None and not m and re.match(r"^#{1,6} ", bare) and any(x.strip() for x in buf):
            sections.append("".join(buf))
            buf = []
        buf.append(line)
    if buf:
        if sections and not any(x.strip() for x in buf):
            sections[-1] += "".join(buf)
        else:
            sections.append("".join(buf))
    return [{"id": f"s{i + 1}", "type": "Section", "markdown": s} for i, s in enumerate(sections)]


def render(packet_dir, item_id):
    pk = read_json(os.path.join(packet_dir, "packet.json"))
    item = next((i for i in pk.get("items", []) if str(i.get("id")) == str(item_id)), None)
    if item is None:
        sys.exit(f"No item {item_id} in {packet_dir}")
    blocks, is_file = {}, False
    if item.get("current"):
        current = read_json(os.path.join(packet_dir, item["current"]))
        blocks = {b["id"]: b for b in current.get("blocks", [])}
        is_file = current.get("kind") == "file"
    parts = []
    for op in item.get("ops", []):
        if op["op"] == "keep":
            parts.append((blocks[op["ref"]]["markdown"], is_file))
        elif op["op"] in ("edit", "add"):
            parts.append((op["markdown"], False))
    parts = [(p, verbatim) for p, verbatim in parts if p and p.strip()]
    # A kept section of a repo file (split-md) is the file's own bytes, trailing
    # blank lines included, so it goes back verbatim and all-keep ops give the
    # file back unchanged. Page blocks, and edited and added text, get one blank
    # line after them, or just the final newline at the end. When edited or
    # added text follows a kept section that ends without a blank line (the
    # file's last section usually does), the gap is padded to one, or the new
    # paragraph would fuse onto the kept one. Kept followed by kept is left
    # alone: that is the file as it was. The one exception is the end of the
    # file: a kept section carries the blank lines that sat between it and
    # the next heading, and when it ends up last (everything after it was
    # removed) those would leave the file ending in a blank line, which
    # markdownlint and end-of-file-fixer reject. So the output always ends
    # with exactly one newline.
    out = ""
    for n, (p, verbatim) in enumerate(parts):
        if not verbatim:
            out += p.strip("\r\n") + ("\n" if n == len(parts) - 1 else "\n\n")
            continue
        out += p
        authored_next = n + 1 < len(parts) and not parts[n + 1][1]
        if authored_next and not p.endswith("\n\n"):
            out += "\n" if p.endswith("\n") else "\n\n"
    if out.strip():
        out = out.rstrip("\r\n") + "\n"
    return out


def find_item(packet_id, ref, item_id=None, packets_dir=PACKETS_DIR):
    """The packet and the item `status` acts on: by item id when given, else the one item with that ticket ref.

    Returns (path, packet, item). Any of them is None when there is no such
    packet or item. Two items with the same ref (a packet that skipped
    validate) stop here, because locking the first match would lock the
    wrong page half the time.
    """
    if not packet_id or not ITEM_ID.match(str(packet_id)):
        return None, None, None
    path = os.path.join(packets_dir, packet_id, "packet.json")
    try:
        pk = read_json(path)
    except FileNotFoundError:
        return path, None, None
    except ValueError as exc:
        sys.exit(f"status recorded, but {path} is not valid JSON, so the item was not touched: {exc}")
    items = pk.get("items", [])
    if item_id is not None:
        return path, pk, next((i for i in items if str(i.get("id")) == str(item_id)), None)
    hits = [i for i in items if (i.get("ticket") or {}).get("ref") == ref]
    if len(hits) > 1:
        sys.exit(f"status recorded, but {len(hits)} items in {path} carry {ref}. Pass --item <id> to say which one "
                 f"(ids: {', '.join(str(i.get('id')) for i in hits)})")
    return path, pk, hits[0] if hits else None


def lock_item(packet_id, ref, locked, packets_dir=PACKETS_DIR, item_id=None):
    """Set or clear `locked` on one packet item. Returns the item, or None if there is no such packet or item.

    Clearing the lock (a failed build) also bumps the item's `revision`, so the
    board drops the approve it had for the old revision and asks again.
    """
    path, pk, item = find_item(packet_id, ref, item_id, packets_dir)
    if item is None:
        return None
    if locked:
        item["locked"] = True
    else:
        item.pop("locked", None)
        item["revision"] = int(item.get("revision") or 1) + 1
    write_json(path, pk)
    return item


def set_status(ref, state, packet=None, target=None, note=None, result=None, path=STATUS_FILE, packets_dir=PACKETS_DIR, item=None):
    if not TICKET.match(ref):
        sys.exit(f"ticket must be owner/repo#N, got {ref!r}")
    if state not in STATES:
        sys.exit(f"state must be one of {STATES}")
    # A missing file is the first run. Anything else that fails to read is a
    # file someone half-wrote or hand-edited, and replacing it would drop
    # every other ticket's state, built entries included.
    try:
        data = read_json(path)
    except FileNotFoundError:
        data = {"tickets": {}}
    except ValueError as exc:
        sys.exit(f"{path} is not valid JSON: {exc}. Fix or remove it; nothing was written")
    entry = data.setdefault("tickets", {}).get(ref, {})
    # An item id only means something inside its packet. A new --packet drops
    # the remembered one, or the next lock would look for packet A's item in
    # packet B, find nothing, and leave the ticket open to a second build.
    if packet is not None and packet != entry.get("packet"):
        entry.pop("item", None)
    entry.update({"state": state, "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    for k, v in (("packet", packet), ("item", item), ("target", target), ("note", note)):
        if v is not None:
            entry[k] = v
    if result is not None:
        entry["result"] = json.loads(result) if isinstance(result, str) else result
    data["tickets"][ref] = entry
    data["updatedAt"] = entry["updatedAt"]
    write_json(path, data)
    # built, building, and published lock the item in its packet, so the board stops
    # offering it and decisions.json stops carrying a stale approve. failed
    # unlocks it and bumps its revision, so it can go back on the board for
    # a fresh approve. The item is the one named by --item (remembered in the
    # entry), else the one item on this ref. Whichever way it was found, the
    # entry records it, every time, so it always names the item last acted on.
    if state in LOCKING:
        found = lock_item(entry.get("packet"), ref, LOCKING[state], packets_dir, item_id=entry.get("item"))
        if found is None and LOCKING[state]:
            print(f"note: no packet item found for {ref} (packet {entry.get('packet')!r}, item {entry.get('item')!r}), "
                  "so it is not locked on the board", file=sys.stderr)
        elif found is not None and entry.get("item") != str(found.get("id")):
            entry["item"] = str(found.get("id"))
            data["tickets"][ref] = entry
            write_json(path, data)
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
    st.add_argument("--item", help="packet item id, when the ref alone does not name one item")
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
        entry = set_status(a.ticket, a.state, a.packet, a.target, a.note, a.result, item=a.item)
        print(json.dumps(entry))


if __name__ == "__main__":
    main()
