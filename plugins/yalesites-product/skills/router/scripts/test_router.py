#!/usr/bin/env python3
"""Tests for the router's pure helpers and the brief. Run: python3 test_router.py"""
import datetime as dt
import os
import re
import sys
import json
import subprocess
import unittest
from unittest import mock

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


class BlockerRefsTest(unittest.TestCase):
    def test_blocker_line_forms(self):
        body = ("> **Blocked by** yalesites-org/YaleSites-Internal#1161, the Views rework.\n"
                "Do not start this until #1561 reaches a recommendation.\n"
                "Depends on https://github.com/yalesites-org/YaleSites-Internal/issues/1593 landing.")
        self.assertEqual(router.blocker_refs(body), {1161, 1561, 1593})

    def test_ignores_lines_without_blocker_wording(self):
        body = "Related: #1754, #1099.\nFixed in #1827 last month."
        self.assertEqual(router.blocker_refs(body), set())

    def test_ignores_other_repos_and_agent_block(self):
        body = ("Blocked by yalesites-org/component-library-twig#728.\n"
                "<!-- yalesites:agent\nblocked by #999\n-->")
        self.assertEqual(router.blocker_refs(body), set())


class FindUnblockedTest(unittest.TestCase):
    """A blocker ref that is a PR or doesn't exist must be skipped, not fail the run."""

    def test_skips_pr_and_missing_refs(self):
        candidate = {"number": 1900, "title": "Waiting", "url": "u", "state": "OPEN",
                     "lastEditedAt": None, "createdAt": "2026-10-01T00:00:00Z",
                     "body": "Blocked by #1991, #1161 and #99999.", "repository": {}, "issueType": None}
        # What gh api graphql prints (with exit 1) when one alias is NOT_FOUND.
        payload = {"data": {"repository": {
            "i1161": {"__typename": "Issue", "number": 1161, "state": "CLOSED",
                      "closedAt": "2026-10-29T12:00:00Z", "stateReason": "COMPLETED"},
            "i1991": {"__typename": "PullRequest"},
            "i99999": None}},
            "errors": [{"type": "NOT_FOUND", "path": ["repository", "i99999"], "message": "Could not resolve"}]}
        done = subprocess.CompletedProcess([], 1, stdout=json.dumps(payload), stderr="gh: Could not resolve")
        with mock.patch.object(router, "search_all", return_value=[candidate]), \
                mock.patch.object(router.subprocess, "run", return_value=done) as run:
            out = router.find_unblocked()
        self.assertIn("issueOrPullRequest(number:1991)", run.call_args[0][0][-1])
        self.assertEqual([b["number"] for b in out[0]["blockers"]], [1161])

    def test_other_graphql_errors_still_raise(self):
        payload = {"data": None, "errors": [{"type": "FORBIDDEN", "message": "no"}]}
        done = subprocess.CompletedProcess([], 1, stdout=json.dumps(payload), stderr="gh: no")
        with mock.patch.object(router.subprocess, "run", return_value=done):
            with self.assertRaises(RuntimeError):
                router.graphql("query{x}", _tolerate={"NOT_FOUND"})


class BriefTest(unittest.TestCase):
    def test_unblocked_section(self):
        u = [{"node": node(1842, "Card size"), "blockers": [
            {"number": 1161, "closedAt": "2026-10-29T12:00:00Z", "stateReason": "COMPLETED"},
            {"number": 1681, "closedAt": "2026-09-24T12:00:00Z", "stateReason": "NOT_PLANNED"}]}]
        brief = router.build_brief([], [], {}, [], [], [], [], [], {}, dry=True, unblocked=u)
        self.assertIn("1 may be unblocked.", brief)
        self.assertIn("#1161 closed Oct 29, #1681 closed Sep 24 as not planned", brief)
        self.assertNotIn("May be unblocked", router.build_brief([], [], {}, [], [], [], [], [], {}, dry=True))

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

    def test_monday_counts_skip_communications(self):
        def typed(number, kind):
            return {**node(number, f"Item {number}"), "issueType": {"name": kind}}
        comms, dev = typed(10, "Communications"), typed(11, "Task")
        stuck = [{"node": comms, "who": "rachel-is-at-yale", "idle": 30, "has_pr": False},
                 {"node": dev, "who": "dblanken-yale", "idle": 4, "has_pr": False}]
        owed = [{"node": typed(12, "Communications"), "kind": "needs-decision", "legacy": False, "who": "miketullo95",
                 "what": "comms call", "has_block": True, "since": router.TODAY, "by": router.TODAY}]
        intake = [typed(13, "Communications"), typed(14, "Feature")]
        saved = router.TODAY
        router.TODAY = dt.date(2026, 11, 2)  # a Monday
        try:
            brief = router.build_brief([], [], {}, [], owed, stuck, intake, [], {}, dry=True, features=[])
        finally:
            router.TODAY = saved
        self.assertIn("**Decisions & follow-ups**: 0 decisions", brief)
        self.assertIn("**Stuck**: 1 stuck", brief)
        self.assertIn("**Intake**: 1 to groom", brief)
        # The daily sections still list the comms items.
        self.assertIn("Item 10", brief)
        self.assertIn("Item 13", brief)
        self.assertIn("comms call", brief)


if __name__ == "__main__":
    unittest.main()
