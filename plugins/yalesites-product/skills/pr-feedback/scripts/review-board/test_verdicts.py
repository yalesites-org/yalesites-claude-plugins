#!/usr/bin/env python3
"""Tests for the board's ruling logic in index.html, run under Node.

Send posts reviews with no check in chat, so the ruling the board infers has to be
right on its own. The functions under test sit between `// test:begin <name>` and
`// test:end` markers in index.html; each test loads those blocks into a Node vm
with a small packet and state, and reads the result back as JSON.
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
    for name in ("isAnswered", "quietGroups", "verdicts"):
        assert name in found, f"index.html lost its test:{name} block"
    return "\n".join(found.values())


HARNESS = r"""
const vm = require('vm');
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const ctx = { packet: input.packet, state: input.state, groups: input.groups, PR_COLORS: ['#000'], out: null };
ctx.groupOf = qi => ctx.groups.find(g => g.qs.includes(qi));
vm.createContext(ctx);
vm.runInContext(input.code + '\n' + input.run, ctx);
process.stdout.write(JSON.stringify(ctx.out));
"""


def run(packet, state, groups, code):
    payload = json.dumps({"packet": packet, "state": state, "groups": groups,
                          "code": blocks(), "run": code})
    res = subprocess.run([NODE, "-e", HARNESS], input=payload, capture_output=True, text=True)
    if res.returncode:
        raise AssertionError(res.stderr)
    return json.loads(res.stdout)


def answer(choice, other=""):
    return {"choice": choice, "other": other, "notes": "", "markups": []}


def question(*options):
    return {"options": [dict(value=v, label=l, **({"verdict": d} if d else {})) for v, l, d in options]}


GROUP = {"key": "o/r#1", "ref": "o/r#1", "qs": [0, 1]}


def verdict(questions, answers, verdicts=None):
    state = {"answers": answers, "verdicts": verdicts or {}}
    return run({"questions": questions}, state, [GROUP], "out = verdictFor(groups[0]);")


@unittest.skipUnless(NODE, "node is not installed")
class VerdictTest(unittest.TestCase):
    def test_option_verdicts_rank_changes_over_comment_over_approve(self):
        qs = [question(("ok", "Ship it", "approve"), ("hold", "Ask April", "comment")),
              question(("fix", "Fix it", "changes"), ("ok", "Leave it", "approve"))]
        self.assertEqual(verdict(qs, [answer("ok"), answer("ok")])["verdict"], "approve")
        self.assertEqual(verdict(qs, [answer("hold"), answer("ok")])["verdict"], "comment")
        v = verdict(qs, [answer("hold"), answer("fix")])
        self.assertEqual((v["verdict"], v["because"]), ("changes", [2]))

    def test_option_without_verdict_is_not_guessed(self):
        # Labels the old regex got wrong both ways.
        for label in ("Request a fix", "Needs work before merge", "Ship it; nothing must change",
                      "Follow-up ticket, not in this PR"):
            qs = [question(("x", label, None)), question(("ok", "Ship it", "approve"))]
            v = verdict(qs, [answer("x"), answer("ok")])
            self.assertIsNone(v["verdict"], label)
            self.assertEqual(v["unread"], [1])

    def test_changes_still_wins_over_an_unread_option(self):
        qs = [question(("x", "Widen the gutter", None)), question(("fix", "Fix it", "changes"))]
        self.assertEqual(verdict(qs, [answer("x"), answer("fix")])["verdict"], "changes")

    def test_reviewer_rules_a_pr_the_board_cannot_read(self):
        qs = [question(("x", "Widen the gutter", None)), question(("ok", "Ship it", "approve"))]
        v = verdict(qs, [answer("x"), answer("ok")], {"o/r#1": "changes"})
        self.assertEqual((v["verdict"], v["overridden"]), ("changes", True))

    def test_something_else_is_a_comment(self):
        qs = [question(("ok", "Ship it", "approve")), question(("ok", "Ship it", "approve"))]
        v = verdict(qs, [answer("__other", "rename the field before merge"), answer("ok")])
        self.assertEqual(v["verdict"], "comment")

    def test_changing_an_answer_drops_the_override(self):
        qs = [question(("ok", "Ship it", "approve"), ("fix", "Fix it", "changes")),
              question(("ok", "Ship it", "approve"))]
        state = {"answers": [answer("ok"), answer("ok")], "verdicts": {"o/r#1": "comment"}}
        out = run({"questions": qs}, state, [GROUP], """
            const before = verdictFor(groups[0]).verdict;
            clearOverride(0);
            state.answers[0].choice = 'fix';
            out = { before, after: verdictFor(groups[0]).verdict, kept: state.verdicts };
        """)
        self.assertEqual(out, {"before": "comment", "after": "changes", "kept": {}})

    def test_quiet_units_get_a_group_with_no_questions(self):
        packet = {"questions": [{}], "units": [{"pr": {"ref": "o/r#1"}}, {"pr": {"ref": "o/r#2"}, "short": "Two"}]}
        out = run(packet, {"answers": [answer(None)]}, [GROUP], """
            const q = quietGroups();
            out = { quiet: q.map(g => [g.ref, g.qs.length, g.quiet, g.label]), verdict: verdictFor(q[0]).verdict };
        """)
        self.assertEqual(out, {"quiet": [["o/r#2", 0, True, "Two"]], "verdict": None})


if __name__ == "__main__":
    unittest.main()
