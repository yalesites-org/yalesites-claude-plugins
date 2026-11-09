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


def board_item(number, status="Backlog", priority="Medium", risk=None, assignees=(), milestone=None,
               labels=(), issue_type="Task", sub_issues=0, blocked_by=0, prs=0, created="2026-10-01T00:00:00Z",
               title=None, parent=None):
    c = {**node(number, title or f"Ticket {number}"), "createdAt": created, "issueType": {"name": issue_type},
         "assignees": {"nodes": [{"login": a} for a in assignees]},
         "labels": {"nodes": [{"name": l} for l in labels]},
         "milestone": milestone, "subIssuesSummary": {"total": sub_issues},
         "issueDependenciesSummary": {"blockedBy": blocked_by}, "parent": {"number": parent} if parent else None,
         "closedByPullRequestsReferences": {"nodes": [{"number": 1, "updatedAt": created}] * prs}}
    return {"node": c, "status": status, "priority": priority, "risk": risk}


DEC = {"title": "12-01-26 Feature Release", "dueOn": "2026-12-08T00:00:00Z", "state": "OPEN"}
FEB = {"title": "02-02-27 Feature Release", "dueOn": "2027-02-09T00:00:00Z", "state": "OPEN"}


def nums(lane):
    return [it["node"]["number"] for it, _ in lane["candidates"]]


class LaneFloorTest(unittest.TestCase):
    LAURA = {"name": "Laura", "floor": 2, "approver": "miketullo95", "areas": ["csv", "dashboard"]}
    DAVE = {"name": "Dave", "floor": 5, "approver": "miketullo95", "areas": []}
    LANES = {"laura-johnson": LAURA, "dblanken-yale": DAVE}

    def dave_full(self):
        return [board_item(100 + i, "To Do", assignees=["dblanken-yale"]) for i in range(5)]

    def test_routing_md_has_the_lanes(self):
        lanes = router.load_lanes()
        self.assertEqual(lanes["laura-johnson"]["floor"], 2)
        self.assertEqual(lanes["laura-johnson"]["approver"], "miketullo95")
        self.assertIn("csv", lanes["laura-johnson"]["areas"])
        self.assertEqual(lanes["dblanken-yale"]["floor"], 5)
        self.assertEqual(lanes["dblanken-yale"]["areas"], [])

    def test_routing_md_has_the_embed_rule(self):
        self.assertEqual(router.load_embed_rule(), ("miketullo95", 1373))

    def test_counts_only_dev_to_do(self):
        items = [board_item(1, "To Do", assignees=["laura-johnson"]),
                 board_item(2, "In progress", assignees=["laura-johnson"]),
                 board_item(3, "In review", assignees=["laura-johnson"]),
                 board_item(4, "To Do", assignees=["laura-johnson"], issue_type="Communications")]
        under, _ = router.lane_report(items + self.dave_full(), self.LANES)
        self.assertEqual([(l["handle"], l["to_do"]) for l in under], [("laura-johnson", 1)])

    def test_nothing_when_every_lane_is_full(self):
        items = [board_item(i, "To Do", assignees=["laura-johnson", "dblanken-yale"]) for i in range(5)]
        items.append(board_item(99))
        self.assertEqual(router.lane_report(items, self.LANES), ([], []))

    def test_candidate_filters(self):
        skip = [board_item(20, assignees=["atiddei"]), board_item(21, priority=None),
                board_item(22, status="In progress"), board_item(23, labels=["forming"]),
                board_item(24, labels=["needs-decision"]), board_item(25, issue_type="Epic"),
                board_item(26, issue_type="Communications"), board_item(27, sub_issues=3),
                board_item(28, blocked_by=1), board_item(29, prs=1)]
        keep = [board_item(30), board_item(31, status="To Do")]
        under, _ = router.lane_report(skip + keep, {"dblanken-yale": self.DAVE})
        self.assertEqual(sorted(nums(under[0])), [30, 31])

    def test_pickup_order_for_a_lane_without_areas(self):
        items = [board_item(40, priority="High"),  # no milestone sorts last
                 board_item(41, priority="Low", milestone=DEC),
                 board_item(42, priority="High", milestone=FEB),
                 board_item(43, priority="High", milestone=DEC, risk="High"),
                 board_item(44, priority="High", milestone=DEC, risk="Low"),
                 board_item(45, priority="Hotfix")]
        under, _ = router.lane_report(items, {"dblanken-yale": self.DAVE})
        self.assertEqual(nums(under[0]), [45, 44, 43, 41, 42])

    def test_laura_gets_bugs_then_her_areas_then_low(self):
        items = [board_item(50, priority="High", milestone=DEC),
                 board_item(51, priority="Low", milestone=FEB),
                 board_item(52, priority="Medium", milestone=FEB, title="Feature Request: Events CSV export"),
                 board_item(53, priority="Low", milestone=FEB, issue_type="Bug"),
                 board_item(54, priority="High", milestone=DEC, issue_type="Bug")]
        under, _ = router.lane_report(items + self.dave_full(), self.LANES)
        laura = under[0]
        self.assertEqual(nums(laura), [54, 53, 52, 51, 50])
        self.assertEqual([why for _, why in laura["candidates"]], ["Bug", "Bug", "Area: csv", "Low priority", ""])

    def test_embeds_need_an_approval(self):
        items = [board_item(60, title="Embed: Google My Maps"), board_item(61, title="Embed Request: Loom"),
                 board_item(62, title="Canva support", parent=1373), board_item(63, title="Embed: Panopto"),
                 board_item(64)]
        under, held = router.lane_report(items, {"dblanken-yale": self.DAVE}, 1373, approved_embeds={63})
        self.assertEqual(sorted(nums(under[0])), [63, 64])
        self.assertEqual(sorted(it["node"]["number"] for it in held), [60, 61, 62])

    def test_embed_bugs_are_not_held(self):
        bug = board_item(65, title="Embed: Vimeo player cropped on mobile", issue_type="Bug")
        self.assertFalse(router.is_embed(bug["node"], 1373))
        under, held = router.lane_report([bug], {"dblanken-yale": self.DAVE}, 1373, approved_embeds=set())
        self.assertEqual(held, [])
        self.assertEqual(nums(under[0]), [65])

    def test_hotfix_embeds_are_still_held(self):
        hot = board_item(66, priority="Hotfix", title="Hotfix: Embed: Panopto")
        hot_req = board_item(67, priority="Hotfix", title="hotfix:Embed Request: Loom")
        self.assertTrue(router.is_embed(hot["node"], 1373))
        self.assertTrue(router.is_embed(hot_req["node"], 1373))
        self.assertFalse(router.is_embed(board_item(68, title="Hotfix: Bug: Embed height")["node"], 1373))
        under, held = router.lane_report([hot, hot_req, board_item(69)], {"dblanken-yale": self.DAVE}, 1373,
                                         approved_embeds=set())
        self.assertEqual(nums(under[0]), [69])
        self.assertEqual(sorted(it["node"]["number"] for it in held), [66, 67])

    def test_areas_match_whole_words(self):
        areas = ["import", "manage content", "csv"]
        self.assertEqual(router.fit(board_item(70, title="Important: fix menu z-index"), areas), (4, ""))
        self.assertEqual(router.fit(board_item(71, title="Re-import people from CSV"), areas), (2, "Area: import"))
        self.assertEqual(router.fit(board_item(72, title="Bulk imports for events"), areas), (2, "Area: import"))
        self.assertEqual(router.fit(board_item(73, title="Manage  Content filters"), areas),
                         (2, "Area: manage content"))
        self.assertEqual(router.fit(board_item(74, title="Managed contentious pages"), areas), (4, ""))
        self.assertEqual(router.fit(board_item(75, title="CSVs (export)"), areas), (2, "Area: csv"))
        self.assertTrue(router.area_hit("c++", "Add C++ snippet support"))
        self.assertFalse(router.area_hit("c++", "Add C snippet support"))

    def test_brief_lists_short_lane_and_candidates(self):
        lane = {"handle": "laura-johnson", **self.LAURA, "to_do": 1,
                "candidates": [(board_item(70, milestone=DEC), "Bug")]}
        brief = router.build_brief([], [], {}, [], [], [], [], [], {}, dry=True, lanes_under=[lane],
                                   embeds_held=[board_item(71, title="Embed: Loom")])
        self.assertIn("### Lane floors", brief)
        self.assertIn("**`laura-johnson` (Laura)**: 1 in To Do, floor 2. Needs 1 more", brief)
        self.assertIn("bugs, then their areas, then Low priority", brief)
        self.assertIn("| Bug |", brief)
        self.assertIn("12-01-26 Feature Release", brief)
        self.assertIn("Left out 1 embed ticket with no approval", brief)
        self.assertIn("1 lane under its floor", brief)
        self.assertIsNone(MENTION.search(brief), brief)

    def test_brief_has_no_lane_section_when_full(self):
        saved = router.TODAY
        router.TODAY = dt.date(2026, 11, 6)  # a Friday, so no Monday agenda
        try:
            brief = router.build_brief([], [], {}, [], [], [], [], [], {}, dry=True)
        finally:
            router.TODAY = saved
        self.assertNotIn("Lane floors", brief)

if __name__ == "__main__":
    unittest.main()
