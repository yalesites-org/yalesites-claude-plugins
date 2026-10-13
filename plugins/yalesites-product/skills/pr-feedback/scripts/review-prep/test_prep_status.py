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
NEW = "9999999aaaaaaa"
SCOPE = "functional,product"


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

    def get(self, key, head=None, scope=None):
        args = ["get", key] + (["--head", head] if head else []) + (["--scope", scope] if scope else [])
        code, out = self.run_cmd(*args)
        return code, json.loads(out)

    def start(self, *prs, packet="ysp-1608", scope=SCOPE, force=False):
        args = ["start"]
        for pr in prs:
            args += ["--pr", pr]
        args += ["--packet", packet, "--scope", scope] + (["--force"] if force else [])
        code, out = self.run_cmd(*args)
        return code, json.loads(out)

    def ready(self, *prs, packet="ysp-1608", scope=SCOPE, **extra):
        args = ["ready"]
        for pr in prs:
            args += ["--pr", pr]
        args += ["--packet", packet, "--scope", scope, "--questions", str(extra.get("questions", 0))]
        return self.run_cmd(*args)

    def age(self, key, delta):
        data = self.status()
        then = datetime.now(timezone.utc) - delta
        data["prs"][key]["updatedAt"] = then.isoformat()
        prep_status.save(self.root, data)

    # Recording

    def test_ready_records_every_pr_in_the_unit(self):
        self.run_cmd("ready", "--pr", f"yalesites-project#1608={SHA}",
                     "--pr", "component-library-twig#774=fff0000aaa", "--packet", "ysp-1608",
                     "--scope", SCOPE, "--questions", "3", "--driven", "--results", "pass=8,fail=1",
                     "--cleanup", "done")
        prs = self.status()["prs"]
        self.assertEqual(prs["yalesites-project#1608"]["state"], "ready")
        self.assertEqual(prs["yalesites-project#1608"]["results"], {"pass": 8, "fail": 1})
        self.assertTrue(prs["yalesites-project#1608"]["driven"])
        self.assertEqual(prs["yalesites-project#1608"]["scope"], ["functional", "product"])
        self.assertEqual(prs["yalesites-project#1608"]["unit"],
                         ["yalesites-project#1608", "component-library-twig#774"])
        self.assertEqual(prs["component-library-twig#774"]["packetId"], "ysp-1608")
        self.assertEqual(prs["component-library-twig#774"]["headSha"], "fff0000aaa")
        self.assertEqual(prs["component-library-twig#774"]["unit"], prs["yalesites-project#1608"]["unit"])
        self.assertTrue(prs["yalesites-project#1608"]["packetDir"].endswith(os.path.join("packets", "ysp-1608")))

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

    def test_bad_scope_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.start(f"atomic#524={SHA}", scope="all,code")
        with self.assertRaises(SystemExit):
            self.start(f"atomic#524={SHA}", scope=" , ")

    def test_corrupt_file_is_treated_as_empty(self):
        with open(os.path.join(self.root, "status.json"), "w") as f:
            f.write("{not json")
        self.run_cmd("run-start")
        self.assertIn("runStartedAt", self.status())

    def test_no_temp_files_left_behind(self):
        self.run_cmd("run-start")
        leftovers = [n for n in os.listdir(self.root) if n.startswith(".status-")]
        self.assertEqual(leftovers, [])

    # Reading

    def test_get_unknown_pr_is_none(self):
        code, entry = self.get("tokens#1")
        self.assertEqual(code, 1)
        self.assertEqual(entry["state"], "none")

    def test_get_reports_stale_when_the_head_moved(self):
        self.ready(f"atomic#524={SHA}", packet="atomic-524")
        self.assertEqual(self.get("atomic#524", head=SHA[:7])[1]["state"], "ready")
        entry = self.get("atomic#524", head=NEW)[1]
        self.assertEqual(entry["state"], "stale")
        self.assertEqual(entry["previousState"], "ready")

    def test_failed_and_running_on_an_old_head_read_as_stale(self):
        self.run_cmd("fail", "--pr", f"yalesites-project#1605={SHA}", "--reason", "multidev pr-1605 missing")
        self.assertEqual(self.get("yalesites-project#1605", head=SHA)[1]["state"], "failed")
        entry = self.get("yalesites-project#1605", head=NEW)[1]
        self.assertEqual(entry["state"], "stale")
        self.assertEqual(entry["previousState"], "failed")
        self.assertIn(NEW, entry["reason"])

        self.start(f"atomic#524={SHA}", packet="atomic-524")
        self.assertEqual(self.get("atomic#524", head=SHA)[1]["state"], "running")
        entry = self.get("atomic#524", head=NEW)[1]
        self.assertEqual(entry["state"], "stale")
        self.assertEqual(entry["previousState"], "running")

    def test_running_past_ttl_reads_as_interrupted(self):
        self.start(f"atomic#524={SHA}", packet="atomic-524")
        self.assertEqual(self.get("atomic#524")[1]["state"], "running")
        self.age("atomic#524", prep_status.RUNNING_TTL + timedelta(minutes=1))
        entry = self.get("atomic#524")[1]
        self.assertEqual(entry["state"], "failed")
        self.assertIn("interrupted", entry["reason"])

    def test_scope_mismatch_reads_as_stale(self):
        self.ready(f"atomic#524={SHA}", packet="atomic-524", scope="product,functional")
        self.assertEqual(self.get("atomic#524", head=SHA, scope="functional,product")[1]["state"], "ready")
        self.assertEqual(self.get("atomic#524", head=SHA, scope="Functional, Product")[1]["state"], "ready")
        self.assertEqual(self.get("atomic#524", head=SHA)[1]["state"], "ready")
        entry = self.get("atomic#524", head=SHA, scope="code")[1]
        self.assertEqual(entry["state"], "stale")
        self.assertEqual(entry["previousState"], "ready")
        self.assertIn("code", entry["reason"])
        self.assertEqual(self.get("atomic#524", head=SHA, scope="all")[1]["state"], "stale")

    def test_scope_does_not_touch_a_failed_entry(self):
        self.run_cmd("fail", "--pr", f"atomic#524={SHA}", "--reason", "no multidev")
        self.assertEqual(self.get("atomic#524", head=SHA, scope="code")[1]["state"], "failed")

    # Claiming

    def test_start_claims_the_unit(self):
        code, out = self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        self.assertEqual(code, 0)
        self.assertTrue(out["claimed"])
        self.assertEqual(out["prs"], ["yalesites-project#1608", "component-library-twig#774"])
        prs = self.status()["prs"]
        self.assertEqual(prs["component-library-twig#774"]["state"], "running")
        self.assertEqual(prs["component-library-twig#774"]["scope"], ["functional", "product"])

    def test_start_refuses_while_another_run_has_it(self):
        self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        before = self.status()
        code, out = self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa",
                               packet="other")
        self.assertEqual(code, prep_status.EXIT_REFUSED)
        self.assertFalse(out["claimed"])
        self.assertIn("another prep run", out["reason"])
        self.assertEqual(self.status(), before)
        # --force never overrides a live run.
        self.assertEqual(self.start(f"yalesites-project#1608={SHA}", force=True)[0], prep_status.EXIT_REFUSED)
        # Nor does a sibling-only claim on the same running PR.
        self.assertEqual(self.start("component-library-twig#774=fff0000aaa", packet="clt-774")[0],
                         prep_status.EXIT_REFUSED)

    def test_start_refuses_a_run_still_driving_an_old_head(self):
        self.start(f"yalesites-project#1608={SHA}")
        code, out = self.start(f"yalesites-project#1608={NEW}")
        self.assertEqual(code, prep_status.EXIT_REFUSED)
        self.assertIn("another prep run", out["reason"])

    def test_start_claims_after_the_ttl(self):
        self.start(f"yalesites-project#1608={SHA}")
        self.age("yalesites-project#1608", prep_status.RUNNING_TTL + timedelta(minutes=1))
        code, out = self.start(f"yalesites-project#1608={SHA}")
        self.assertEqual(code, 0)
        self.assertTrue(out["claimed"])

    def test_start_refuses_a_current_packet_unless_forced(self):
        self.ready(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        code, out = self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        self.assertEqual(code, prep_status.EXIT_REFUSED)
        self.assertIn("current", out["reason"])
        self.assertEqual(self.status()["prs"]["yalesites-project#1608"]["state"], "ready")
        # A different scope wants its own packet.
        self.assertEqual(self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa",
                                    scope="code")[0], 0)
        self.ready(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        code, out = self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa",
                               force=True)
        self.assertEqual(code, 0)
        self.assertEqual(self.status()["prs"]["yalesites-project#1608"]["state"], "running")

    def test_start_claims_when_one_sibling_moved(self):
        self.ready(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        code, out = self.start(f"yalesites-project#1608={SHA}", f"component-library-twig#774={NEW}")
        self.assertEqual(code, 0)
        self.assertTrue(out["claimed"])

    def test_start_refuses_a_unit_that_already_failed_on_this_head(self):
        self.run_cmd("fail", "--pr", f"yalesites-project#1605={SHA}", "--reason", "multidev pr-1605 missing")
        code, out = self.start(f"yalesites-project#1605={SHA}", packet="ysp-1605")
        self.assertEqual(code, prep_status.EXIT_REFUSED)
        self.assertIn("multidev pr-1605 missing", out["reason"])
        self.assertEqual(self.start(f"yalesites-project#1605={NEW}", packet="ysp-1605")[0], 0)

    def test_start_claims_when_a_sibling_has_no_entry(self):
        self.ready(f"yalesites-project#1608={SHA}")
        code, _ = self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        self.assertEqual(code, 0)

    # Heartbeat

    def test_heartbeat_keeps_a_slow_run_inside_the_ttl(self):
        self.start(f"yalesites-project#1608={SHA}", "component-library-twig#774=fff0000aaa")
        self.age("yalesites-project#1608", prep_status.RUNNING_TTL - timedelta(minutes=1))
        self.age("component-library-twig#774", prep_status.RUNNING_TTL - timedelta(minutes=1))
        code, out = self.run_cmd("heartbeat", "--packet", "ysp-1608")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["heartbeat"])
        self.age("yalesites-project#1608", timedelta(minutes=5))  # pretend time passed after the stamp
        self.assertEqual(self.get("yalesites-project#1608")[1]["state"], "running")
        self.assertEqual(self.get("component-library-twig#774")[1]["state"], "running")
        self.assertEqual(self.status()["prs"]["yalesites-project#1608"]["headSha"], SHA)

    def test_heartbeat_without_a_running_entry_fails(self):
        self.ready(f"yalesites-project#1608={SHA}")
        code, out = self.run_cmd("heartbeat", "--packet", "ysp-1608")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)["heartbeat"])
        self.assertEqual(self.status()["prs"]["yalesites-project#1608"]["state"], "ready")


if __name__ == "__main__":
    unittest.main()
