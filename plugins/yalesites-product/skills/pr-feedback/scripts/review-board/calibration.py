"""Calibration hooks for the review board: seal our guess, keep the ruling.

Michael's calibration loop (ruled on a board, 2026-11-04) scores how well the
agent predicts his calls, per category, and graduates only low-risk ones. The
guess is the packet's hidden `guess` (held calls) or else the option it marks
recommended; a question with neither has no guess and is not scored. This module does the two board-side jobs; the scoring lives in
~/code/work-dashboard (src/calibration/), which reads what this writes.

seal(folder, packet_id, cal_dir)
    On first open, writes <folder>/seal.json: the time, a hash of packet.json,
    the playbook version, and which questions are blind (our pick hidden until
    he answers: 1 in 4, only in categories still in shadow) or pre-filled
    (categories at rung 1 or higher). A packet changed after its seal is
    re-sealed only while it has no answers yet; after that the dashboard marks
    its rows void.

snapshot(folder, packet_id, cal_dir)
    After a save, copies packet.json, seal.json and answers.json to
    <cal_dir>/boards/<packet_id>/, so a board served from a session scratchpad
    survives /tmp cleanup.

Everything here is local files only and never raises into the server: a
calibration problem must not stop a board from loading or saving.
"""
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

PR_REF = re.compile(r"^[\w.-]+/[\w.-]+#\d+$")
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".claude", "yalesites", "calibration")


def _read_json(path, fallback=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return fallback


def _write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _sha1(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()
    except OSError:
        return None


def recommended(question):
    """The option marked recommended, or None. An unmarked question is a held
    call with no recommendation on purpose, never "the first option"."""
    for o in question.get("options") or []:
        if o.get("recommended"):
            return o
    return None


def hidden_guess(question):
    """A packet's private guess: {"value", "reason"} naming one of its options.

    For held calls with no recommendation, the packet writer still records
    what it thinks Michael will pick. The board never shows it until he has
    answered, so these questions are always blind.
    """
    g = question.get("guess")
    values = {o.get("value") for o in question.get("options") or []}
    if isinstance(g, dict) and g.get("value") in values:
        return g
    return None


def guess_of(question):
    g = hidden_guess(question)
    if g:
        return {"value": g["value"], "visible": False}
    r = recommended(question)
    return {"value": r["value"], "visible": True} if r else None


def _clause_matches(clause, facts):
    for key, want in clause.items():
        if key in ("packet", "dimension"):
            if not re.search(want, facts.get(key) or "", re.I):
                return False
        elif key == "hasPr":
            if bool(PR_REF.match(facts.get("pr") or "")) != want:
                return False
        elif facts.get(key) != want:
            return False
    return True


def classify(facts, cats):
    """Same rules as work-dashboard's src/calibration/categories.js."""
    for c in (cats or {}).get("categories", []):
        if any(_clause_matches(cl, facts) for cl in c.get("match", [])):
            return c["id"]
    return "other"


def excluded(packet_id, cats):
    return any(re.search(p, packet_id or "", re.I) for p in (cats or {}).get("excludePackets", []))


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", str(text or ""))).strip().lower()


def leaks(question, rec):
    """True when the question's own text gives our pick away.

    Many packets restate the recommended option in the brief or the write-up
    ("Close with a short comment..."). Hiding the badge would not make that
    question blind, so it stays visible and is scored as anchored.
    """
    shown = _norm(" ".join([*(question.get("brief") or []), question.get("question") or "", question.get("ask") or ""]))
    if not shown:
        return False
    if re.search(r"\brecommend", shown):
        return True
    detail = _norm(rec.get("detail"))
    for i in range(0, max(1, len(detail) - 40), 20):
        chunk = detail[i:i + 40]
        if len(chunk) >= 40 and chunk in shown:
            return True
    return False


def is_blind(packet_id, question_id, rate):
    digest = hashlib.sha1(f"{packet_id}:{question_id}".encode()).hexdigest()
    return int(digest, 16) % rate == 0


def _playbook_version(cal_dir):
    try:
        with open(os.path.join(cal_dir, "playbook.md")) as f:
            m = re.search(r"^version:\s*(\S+)", f.read(), re.M)
            return m.group(1) if m else None
    except OSError:
        return None


def build_seal(packet, packet_id, cal_dir, packet_sha, now=None):
    cats = _read_json(os.path.join(cal_dir, "categories.json"), {})
    state = _read_json(os.path.join(cal_dir, "state.json"), {})
    rate = int(state.get("blindRate") or 4)
    rungs = state.get("categories") or {}
    blind, prefill = [], []
    if not excluded(packet_id, cats):
        for q in packet.get("questions") or []:
            qid = q.get("id")
            guess = guess_of(q)
            if not qid or not guess:
                continue
            pr = q.get("pr")
            pr = pr.get("ref") if isinstance(pr, dict) else pr
            cat = classify({"source": "board", "packet": packet_id, "dimension": q.get("dimension") or "",
                            "pr": pr or "", "kind": "question"}, cats)
            rung = int((rungs.get(cat) or {}).get("rung") or 0)
            if not guess["visible"]:
                blind.append(qid)  # a hidden guess is blind by nature and never pre-filled
            elif rung >= 1:
                prefill.append(qid)
            elif is_blind(packet_id, qid, rate) and not leaks(q, recommended(q)):
                blind.append(qid)
    return {
        "sealedAt": (now or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z"),
        "packet": packet_id,
        "packetSha": packet_sha,
        "playbook": _playbook_version(cal_dir),
        "blindRate": rate,
        "blind": blind,
        "prefill": prefill,
    }


def seal(folder, packet_id, cal_dir, answers_name="answers.json"):
    try:
        packet_path = os.path.join(folder, "packet.json")
        sha = _sha1(packet_path)
        packet = _read_json(packet_path)
        if not packet or not sha:
            return None
        seal_path = os.path.join(folder, "seal.json")
        current = _read_json(seal_path)
        if current and (current.get("packetSha") == sha or os.path.exists(os.path.join(folder, answers_name))):
            return current
        made = build_seal(packet, packet_id, cal_dir, sha)
        _write_json(seal_path, made)
        return made
    except Exception as err:  # never break the board
        print(f"[calibration] seal failed for {packet_id}: {err}", file=sys.stderr)
        return None


def snapshot(folder, packet_id, cal_dir, answers_name="answers.json"):
    try:
        boards = os.path.join(cal_dir, "boards")
        sha = _sha1(os.path.join(folder, "packet.json")) or "nopacket"
        dest = os.path.join(boards, packet_id)
        if os.path.isdir(dest):
            have = _sha1(os.path.join(dest, "packet.json"))
            if have and have != sha:
                dest = os.path.join(boards, f"{packet_id}-{sha[:8]}")
        os.makedirs(dest, exist_ok=True)
        for name in ("packet.json", "seal.json", answers_name):
            src = os.path.join(folder, name)
            if os.path.isfile(src):
                shutil.copyfile(src, os.path.join(dest, "answers.json" if name == answers_name else name))
        return dest
    except Exception as err:  # never break the board
        print(f"[calibration] snapshot failed for {packet_id}: {err}", file=sys.stderr)
        return None
