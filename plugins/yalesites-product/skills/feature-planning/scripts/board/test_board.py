#!/usr/bin/env python3
"""Tests for the planning board's saved-answer logic in index.html, run under Node.

Step B1 reuses the feature slug as the packet id for every round, so the board must not
bring one round's picks back into the next. The functions under test sit between
`// test:begin <name>` and `// test:end` markers in index.html; each test loads those blocks
into a Node vm and reads the result back as JSON.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
NODE = shutil.which("node")


def blocks():
    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
        src = f.read()
    found = dict(re.findall(r"// test:begin (\w+)\n(.*?)// test:end", src, re.S))
    for name in ("storageKey", "restoreState", "isAnswered"):
        assert name in found, f"index.html lost its test:{name} block"
    return "\n".join(found.values())


HARNESS = r"""
const vm = require('vm');
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const ctx = { input, out: null };
vm.createContext(ctx);
vm.runInContext(input.code + '\n' + input.run, ctx);
process.stdout.write(JSON.stringify(ctx.out));
"""


def run(code, **data):
    payload = json.dumps({"code": blocks(), "run": code, **data})
    res = subprocess.run([NODE, "-e", HARNESS], input=payload, capture_output=True, text=True)
    if res.returncode:
        raise AssertionError(res.stderr)
    return json.loads(res.stdout)


def question(qid, *values, title=None):
    return {"id": qid, "title": title or qid, "ask": f"Pick for {qid}?",
            "options": [{"value": v, "label": v.title()} for v in values]}


ROUND_ONE = {"questions": [question("placement", "block", "sitewide"),
                           question("default", "stacked", "row")]}
# Same slug and question count, different questions: the case from the PR review.
ROUND_TWO = {"round": 2, "questions": [question("mobile", "stack", "scroll"),
                                       question("limit", "four", "six")]}


def key(packet, packet_id="facts-band-layouts"):
    return run("out = storageKey(input.id, input.packet);", id=packet_id, packet=packet)


def answers(*choices):
    return {"answers": [{"choice": c, "other": "", "notes": "", "markups": []} for c in choices],
            "ownRead": "round one read"}


def restore_and_check(saved, packet):
    """Restore saved state into packet, then report the state and which questions pass Send."""
    return run("""
        const packet = input.packet;
        const state = restoreState(input.saved, packet);
        out = { state, answered: packet.questions.map((_, i) => !!isAnswered(i)) };
    """, saved=saved, packet=packet)


@unittest.skipUnless(NODE, "node is not installed")
class StorageKeyTest(unittest.TestCase):
    def test_same_packet_keeps_its_key(self):
        self.assertEqual(key(ROUND_ONE), key(json.loads(json.dumps(ROUND_ONE))))
        self.assertTrue(key(ROUND_ONE).startswith("planning-board:facts-band-layouts:"))

    def test_round_two_with_same_slug_and_count_gets_a_new_key(self):
        self.assertNotEqual(key(ROUND_ONE), key(ROUND_TWO))

    def test_round_number_alone_changes_the_key(self):
        self.assertNotEqual(key(ROUND_ONE), key({**ROUND_ONE, "round": 2}))

    def test_changed_option_changes_the_key(self):
        edited = {"questions": [question("placement", "block", "global"), ROUND_ONE["questions"][1]]}
        self.assertNotEqual(key(ROUND_ONE), key(edited))


@unittest.skipUnless(NODE, "node is not installed")
class RestoreTest(unittest.TestCase):
    def test_reload_of_same_round_keeps_answers(self):
        out = restore_and_check(answers("block", "row"), ROUND_ONE)
        self.assertEqual([a["choice"] for a in out["state"]["answers"]], ["block", "row"])
        self.assertEqual(out["answered"], [True, True])

    def test_round_one_picks_do_not_pass_send_on_round_two(self):
        # Even if a stale entry reached round two, its picks match no option there.
        out = restore_and_check(answers("block", "row"), ROUND_TWO)
        self.assertEqual([a["choice"] for a in out["state"]["answers"]], [None, None])
        self.assertEqual(out["answered"], [False, False])

    def test_other_answer_survives_and_needs_text(self):
        saved = answers("__other", "__other")
        saved["answers"][0]["other"] = "A toggle on the section"
        out = restore_and_check(saved, ROUND_ONE)
        self.assertEqual(out["answered"], [True, False])

    def test_count_mismatch_starts_blank(self):
        out = restore_and_check(answers("block"), ROUND_ONE)
        self.assertEqual([a["choice"] for a in out["state"]["answers"]], [None, None])
        self.assertEqual(out["state"]["ownRead"], "")


if __name__ == "__main__":
    unittest.main()
