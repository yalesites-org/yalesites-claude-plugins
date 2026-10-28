#!/usr/bin/env python3
"""Tests for the router's pure helpers and the brief. Run: python3 test_router.py"""
import datetime as dt
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import router  # noqa: E402

# A live mention: @ followed by a handle character, not preceded by a zero-width space.
MENTION = re.compile(r"(?<!​)@[A-Za-z0-9-]")


def node(number, title, repo="yalesites-org/YaleSites-Internal"):
    return {"number": number, "title": title, "url": f"https://github.com/{repo}/issues/{number}",
            "repository": {"nameWithOwner": repo}, "createdAt": "2026-10-20T12:00:00Z",
            "author": {"login": "atiddei"}, "parent": None}


class QuietTest(unittest.TestCase):
    def test_breaks_mentions(self):
        out = router.quiet("ask @miketullo95 and @dblanken-yale")
        self.assertIsNone(MENTION.search(out))
        self.assertEqual(out.replace("​", ""), "ask @miketullo95 and @dblanken-yale")

    def test_leaves_other_at_signs(self):
        self.assertEqual(router.quiet("email me @ noon"), "email me @ noon")

    def test_none_is_empty(self):
        self.assertEqual(router.quiet(None), "")


class ParseBlockTest(unittest.TestCase):
    def test_decision_block(self):
        body = ("## Decision needed\n**Question:** which layout ships first   **Options:** (a) (b)\n"
                "**Decides:** @miketullo95   **Needed by:** 2026-11-03   **Raised by:** Dave")
        b = router.parse_block(body, "needs-decision")
        self.assertEqual(b, {"who": "miketullo95", "what": "which layout ships first", "by": "2026-11-03"})

    def test_follow_up_block_last_one_wins(self):
        body = ("## Follow-up needed\n**Who:** @atiddei   **What:** first\n**By:** 2026-11-01\n"
                "## Follow-up needed\n**Who:** @dblanken-yale   **What:** second\n**By:** 2026-11-04")
        b = router.parse_block(body, "follow-up")
        self.assertEqual((b["who"], b["what"], b["by"]), ("dblanken-yale", "second", "2026-11-04"))

    def test_no_block(self):
        self.assertIsNone(router.parse_block("just a body", "follow-up"))


class WorkingDaysTest(unittest.TestCase):
    def test_skips_weekends(self):
        fri, mon = dt.date(2026, 10, 30), dt.date(2026, 11, 2)
        self.assertEqual(router.working_days_between(fri, mon), 1)
        self.assertEqual(router.add_working_days(fri, 1), mon)


class BriefTest(unittest.TestCase):
    def test_brief_never_mentions_anyone(self):
        loud = "Ping @miketullo95 about this"
        owed = [{"node": node(1, loud), "kind": "follow-up", "legacy": False, "who": "atiddei",
                 "what": "ask @dblanken-yale to confirm", "has_block": True,
                 "since": router.TODAY, "by": router.TODAY},
                {"node": node(2, loud), "kind": "needs-decision", "legacy": True, "who": None,
                 "what": None, "has_block": False, "since": router.TODAY, "by": router.TODAY}]
        stuck = [{"node": node(3, loud), "who": "dblanken-yale", "idle": 4, "has_pr": False}]
        intake = [node(4, loud)]
        features = [{"node": node(5, loud), "milestone": "12-01-26", "done": 1, "total": 3}]
        waiting = [(node(6, loud), "blocker still open")]
        brief = router.build_brief([], [], {}, waiting, owed, stuck, intake, [node(7, loud)], {},
                                   dry=True, features=features)
        self.assertIsNone(MENTION.search(brief), brief)
        self.assertIn("Ping @​miketullo95", brief)


if __name__ == "__main__":
    unittest.main()
