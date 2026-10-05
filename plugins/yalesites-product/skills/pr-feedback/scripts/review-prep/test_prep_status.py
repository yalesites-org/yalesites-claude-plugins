#!/usr/bin/env python3
"""Tests for the prep mode status file. Run: python3 test_prep_status.py"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_status  # noqa: E402

SHA = "abc1234def5678"


class PrepStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = prep_status.main(["--root", self.root, *args])
        return code, out.getvalue()

    def status(self):
        with open(os.path.join(self.root, "status.json")) as f:
            return json.load(f)

    def get(self, key, head=None):
        args = ["get", key] + (["--head", head] if head else [])
        code, out = self.run_cmd(*args)
        return code, json.loads(out)

    def test_ready_records_every_pr_in_the_unit(self):
        self.run_cmd("ready", "--pr", f"yalesites-project#1608={SHA}",
                     "--pr", "component-library-twig#774=fff0000aaa", "--packet", "ysp-1608",
                     "--questions", "3", "--driven", "--results", "pass=8,fail=1", "--cleanup", "done")
        prs = self.status()["prs"]
        self.assertEqual(prs["yalesites-project#1608"]["state"], "ready")
        self.assertEqual(prs["yalesites-project#1608"]["results"], {"pass": 8, "fail": 1})
        self.assertTrue(prs["yalesites-project#1608"]["driven"])
        self.assertEqual(prs["component-library-twig#774"]["packetId"], "ysp-1608")
        self.assertEqual(prs["component-library-twig#774"]["headSha"], "fff0000aaa")
        self.assertTrue(prs["yalesites-project#1608"]["packetDir"].endswith(os.path.join("packets", "ysp-1608")))

    def test_get_reports_stale_when_the_head_moved(self):
        self.run_cmd("ready", "--pr", f"atomic#524={SHA}", "--packet", "atomic-524", "--questions", "0")
        self.assertEqual(self.get("atomic#524", head=SHA[:7])[1]["state"], "ready")
        self.assertEqual(self.get("atomic#524", head="9999999")[1]["state"], "stale")

    def test_get_unknown_pr_is_none(self):
        code, entry = self.get("tokens#1")
        self.assertEqual(code, 1)
        self.assertEqual(entry["state"], "none")

    def test_running_past_ttl_reads_as_interrupted(self):
        self.run_cmd("start", "--pr", f"atomic#524={SHA}", "--packet", "atomic-524")
        self.assertEqual(self.get("atomic#524")[1]["state"], "running")
        data = self.status()
        old = datetime.now(timezone.utc) - prep_status.RUNNING_TTL - timedelta(minutes=1)
        data["prs"]["atomic#524"]["updatedAt"] = old.isoformat()
        prep_status.save(self.root, data)
        entry = self.get("atomic#524")[1]
        self.assertEqual(entry["state"], "failed")
        self.assertIn("interrupted", entry["reason"])

    def test_fail_records_the_reason(self):
        self.run_cmd("fail", "--pr", f"yalesites-project#1605={SHA}", "--reason", "multidev pr-1605 missing")
        entry = self.status()["prs"]["yalesites-project#1605"]
        self.assertEqual(entry["state"], "failed")
        self.assertEqual(entry["reason"], "multidev pr-1605 missing")

    def test_run_markers(self):
        self.run_cmd("run-start")
        self.run_cmd("run-end")
        data = self.status()
        self.assertIn("runStartedAt", data)
        self.assertIn("lastRun", data)

    def test_bad_pr_argument_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_cmd("fail", "--pr", "yalesites-project-1605", "--reason", "x")

    def test_corrupt_file_is_treated_as_empty(self):
        with open(os.path.join(self.root, "status.json"), "w") as f:
            f.write("{not json")
        self.run_cmd("run-start")
        self.assertIn("runStartedAt", self.status())

    def test_no_temp_files_left_behind(self):
        self.run_cmd("run-start")
        leftovers = [n for n in os.listdir(self.root) if n.startswith(".status-")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
