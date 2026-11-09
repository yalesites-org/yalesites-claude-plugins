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
    for name in ("calibration", "isAnswered", "quietGroups", "reveal", "verdicts", "unitOf", "prUrl"):
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

    def test_subject_is_the_title_never_a_bare_ref(self):
        def subject(q, u=None):
            return run({"questions": [q]}, {}, [], f"out = subjectOf(packet.questions[0], {json.dumps(u)});")
        pr = {"ref": "o/r#82", "url": "https://github.com/o/r/pull/82"}
        titled = dict(pr, title="feat: count block positions")
        issue = {"ref": "o/i#5", "title": "Bug: thing breaks"}
        # The unit's PR title wins, then its ticket, then the question's own refs.
        self.assertEqual(subject({"pr": pr}, {"pr": titled})["title"], titled["title"])
        self.assertEqual(subject({"pr": pr}, {"pr": pr, "issue": issue})["title"], issue["title"])
        self.assertEqual(subject({"pr": titled})["title"], titled["title"])
        # A ref with no title is reported as missing, not shown as if it were a title.
        self.assertIsNone(subject({"pr": pr}))

    def test_rulings_are_on_unless_the_packet_turns_them_off(self):
        code = "out = [hasRulings(), noun()];"
        self.assertEqual(run({"questions": []}, {}, [], code), [True, "PR"])
        self.assertEqual(run({"questions": [], "rulings": False}, {}, [], code), [False, "item"])

    def test_unrec_strips_only_the_marker_and_keeps_not_recommended(self):
        cases = ["Merge as is (Recommended)", "Merge as is (our recommendation)", "Recommended: merge as is",
                 "Merge as is (not recommended)", "This is not recommended because it skips tests",
                 "Recommended reading is linked in the brief"]
        got = run({"questions": []}, {}, [], f"out = {json.dumps(cases)}.map(unrec);")
        self.assertEqual(got, ["Merge as is", "Merge as is", "merge as is",
                               "Merge as is (not recommended)", "This is not recommended because it skips tests",
                               "Recommended reading is linked in the brief"])

    def test_reveal_follows_every_pick_on_a_non_blind_question(self):
        # The pick handler redraws the reveal from revealKind after every pick, not only the first blind one.
        code = """
        const rec = { value: 'ship', label: 'Ship it' };
        const a = { choice: null, blindChoice: null, prefilled: false };
        const seen = [];
        for (const v of ['ship', '__other', 'fix', '__other']) { pickAnswer(a, v, false); seen.push(revealKind(a, false, rec)); }
        const pre = { choice: 'ship', blindChoice: null, prefilled: true };
        const before = revealKind(pre, false, rec);
        pickAnswer(pre, 'fix', false);
        const afterSwitch = revealKind(pre, false, rec);
        pickAnswer(pre, 'ship', false);
        out = { seen, before, afterSwitch, back: revealKind(pre, false, rec), prefilled: pre.prefilled, blindChoice: a.blindChoice };
        """
        got = run({"questions": []}, {}, [], code)
        # "Something else" shows the close-or-not chips even when it is not the first pick.
        self.assertEqual(got["seen"], [None, "grade", None, "grade"])
        self.assertIsNone(got["blindChoice"])
        # Switching away from a pre-filled pick drops the note, and coming back does not restore it.
        self.assertEqual(got["before"], "prefilled")
        self.assertIsNone(got["afterSwitch"])
        self.assertIsNone(got["back"])
        self.assertFalse(got["prefilled"])

    def test_reveal_scores_only_the_first_blind_pick(self):
        code = """
        const rec = { value: 'ship', label: 'Ship it' };
        const a = { choice: null, blindChoice: null, prefilled: false };
        const first = pickAnswer(a, 'fix', true), k1 = revealKind(a, true, rec);
        const second = pickAnswer(a, 'ship', true), k2 = revealKind(a, true, rec);
        out = [first, k1, second, k2, a.blindChoice];
        """
        self.assertEqual(run({"questions": []}, {}, [], code), [True, "miss", False, "miss", "fix"])

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

    def test_string_pr_on_a_question_still_groups_by_unit(self):
        # A hand-built batch packet set `pr` to a bare ref. Each question must still find its
        # unit, so no unit reads as quiet and each chip counts its own questions.
        a, b = "yalesites-org/yale-ui-cl#76", "yalesites-org/yalesites-project#1598"
        packet = {"questions": [{"pr": a}, {"pr": a}, {"pr": {"ref": b, "url": "u"}}],
                  "units": [{"pr": {"ref": a}}, {"pr": {"ref": b}}]}
        out = run(packet, {}, [], """
            normalizePrs();
            groups = buildGroups();
            out = { groups: groups.map(g => [g.ref, g.qs]), quiet: quietGroups().length, pr: packet.questions[0].pr };
        """)
        self.assertEqual(out, {"groups": [[a, [0, 1]], [b, [2]]], "quiet": 0,
                               "pr": {"ref": a, "url": "https://github.com/yalesites-org/yale-ui-cl/pull/76"}})

    def test_units_with_no_pr_group_by_issue_and_need_no_ruling(self):
        packet = {"rulings": False,
                  "questions": [{"issue": {"ref": "o/i#5"}}, {"issue": {"ref": "o/i#6"}}, {"issue": {"ref": "o/i#5"}}],
                  "units": [{"issue": {"ref": "o/i#5", "title": "Five"}}, {"issue": {"ref": "o/i#6"}, "short": "Six"}]}
        out = run(packet, {"answers": [answer(None)] * 3}, [], """
            groups = buildGroups();
            out = { groups: groups.map(g => [g.key, g.qs, g.noPr, g.label]), quiet: quietGroups().length };
        """)
        self.assertEqual(out, {"groups": [["o/i#5", [0, 2], True, "Five"], ["o/i#6", [1], True, "Six"]], "quiet": 0})

    def test_pr_units_still_match_by_pr_ref(self):
        packet = {"questions": [{"pr": {"ref": "o/r#2"}}, {"pr": {"ref": "o/c#9"}}],
                  "units": [{"pr": {"ref": "o/r#1"}}, {"pr": {"ref": "o/r#2"}, "extraPrs": ["o/c#9"], "issue": {"ref": "o/i#1"}}]}
        out = run(packet, {}, [], "out = buildGroups().map(g => [g.key, g.qs, g.noPr]);")
        self.assertEqual(out, [["o/r#2", [0, 1], False]])


if __name__ == "__main__":
    unittest.main()
