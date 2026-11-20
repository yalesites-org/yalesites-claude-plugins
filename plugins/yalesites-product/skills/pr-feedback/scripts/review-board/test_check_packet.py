#!/usr/bin/env python3
"""Tests for the ELI5 packet check."""

import contextlib
import io
import json
import os
import tempfile
import unittest

from check_packet import check_packet, main

GOOD_Q = {
    "id": "swatch",
    "gist": "The last color swatch is cut off at the edge of the pop-up. This PR did not cause it. Fix it now or later?",
    "ask": "Ticket the clipping, or fix it in this PR?",
    "brief": ["The last swatch is cut off.", "It shows on dev too."],
    "options": [
        {"value": "followup", "label": "Follow-up ticket", "detail": "Approve as-is and open a design ticket."},
        {"value": "fix", "label": "Fix it here", "detail": "Widens a small bug fix."},
        {"value": "defer", "label": "Decide later", "detail": "Raise it as needs-decision."},
    ],
}
GOOD_UNIT = {"pr": {"ref": "o/r#1"}, "ask": "Stop a warning in the logs.", "change": "Adds a guard."}


def packet(**over):
    return {"units": [GOOD_UNIT], "questions": [{**GOOD_Q, **over}]}


class CheckPacket(unittest.TestCase):
    def test_good_packet_passes(self):
        self.assertEqual(check_packet(packet()), [])

    def test_missing_gist(self):
        self.assertTrue(any("no gist" in p for p in check_packet(packet(gist=""))))

    def test_long_gist(self):
        problems = check_packet(packet(gist="One. Two. Three. Four?"))
        self.assertTrue(any("4 sentences" in p for p in problems))

    def test_code_in_gist(self):
        problems = check_packet(packet(gist="The ys_layouts hook throws in `preprocess`. Guard it?"))
        self.assertTrue(any("snake_case" in p for p in problems))
        self.assertTrue(any("backticks" in p for p in problems))

    def test_ask_must_be_one_short_question(self):
        self.assertTrue(any("not a question" in p for p in check_packet(packet(ask="Keep the padding."))))
        self.assertTrue(any("more than one" in p for p in check_packet(packet(ask="Keep it? Or drop it?"))))

    def test_options_need_detail(self):
        options = [{"value": "a", "label": "A"}, {"value": "b", "label": "B", "detail": "Costs a day."}]
        self.assertTrue(any("no detail" in p for p in check_packet(packet(options=options))))

    def test_unit_lead_in(self):
        p = {"units": [{**GOOD_UNIT, "change": ""}], "questions": [GOOD_Q]}
        self.assertTrue(any("no change" in x for x in check_packet(p)))

    def test_units_with_no_questions_pass(self):
        # A unit whose brief held nothing still gets a lead-in and a ruling row.
        self.assertEqual(check_packet({"units": [GOOD_UNIT], "questions": []}), [])

    def test_empty_packet_fails(self):
        self.assertTrue(any("no questions and no units" in p for p in check_packet({})))

    def test_issue_only_unit_needs_no_change(self):
        unit = {"issue": {"ref": "o/r#2"}, "ask": "Decide what to do with an old ticket."}
        p = {"rulings": False, "units": [unit], "questions": [{**GOOD_Q, "issue": {"ref": "o/r#2"}}]}
        self.assertEqual(check_packet(p), [])

    def test_issue_only_unit_still_needs_ask(self):
        p = {"rulings": False, "units": [{"issue": {"ref": "o/r#2"}}], "questions": [GOOD_Q]}
        self.assertTrue(any("no ask" in x for x in check_packet(p)))

    def test_product_names_are_not_code(self):
        gist = "It breaks on an iPhone and on macOS. The build uses Node.js. Fix it now?"
        self.assertEqual(check_packet(packet(gist=gist)), [])

    def test_abbreviations_do_not_end_sentences(self):
        gist = "Some blocks, e.g. the hero, lose padding. Wide vs. narrow both show it. Fix it now?"
        self.assertEqual(check_packet(packet(gist=gist)), [])

    def test_ask_may_end_in_markdown_or_quotes(self):
        for ask in ("Keep the **new padding?**", 'Keep the label "Read more?"', "Keep it (for now?)"):
            self.assertFalse(any("not a question" in p for p in check_packet(packet(ask=ask))), ask)


class Main(unittest.TestCase):
    def test_bad_json_exits_3(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{not json")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([f.name]), 3)
        finally:
            os.unlink(f.name)

    def test_content_failure_exits_1(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(packet(gist=""), f)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([f.name]), 1)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
