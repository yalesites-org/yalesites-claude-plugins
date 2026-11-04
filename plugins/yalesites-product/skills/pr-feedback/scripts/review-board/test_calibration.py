#!/usr/bin/env python3
"""Tests for the review board's calibration hooks. Run: python3 test_calibration.py"""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calibration  # noqa: E402
import server  # noqa: E402
from test_verdicts import NODE, run  # noqa: E402

CATS = {
    "excludePackets": ["^demo$"],
    "categories": [
        {"id": "pr-verdict", "tier": "gated", "match": [{"kind": "verdict"}]},
        {"id": "board-hygiene", "tier": 0, "match": [{"packet": "^mikes-work"}]},
        {"id": "pr-product", "tier": 2, "match": [{"hasPr": True}]},
        {"id": "design-calls", "tier": 2, "match": [{"source": "board"}]},
    ],
}


def q(qid, *values, rec=None, pr=None):
    return {"id": qid, "pr": pr, "options": [
        {"value": v, "label": v.title(), **({"recommended": True} if v == rec else {})} for v in values]}


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


class Classify(unittest.TestCase):
    def test_same_rules_as_the_dashboard(self):
        self.assertEqual(calibration.classify({"source": "board", "packet": "mikes-work-cleanup"}, CATS), "board-hygiene")
        self.assertEqual(calibration.classify({"source": "board", "packet": "b", "pr": "yalesites-org/atomic#555"}, CATS), "pr-product")
        self.assertEqual(calibration.classify({"source": "board", "packet": "b", "pr": "Layout"}, CATS), "design-calls")
        self.assertEqual(calibration.classify({"kind": "verdict"}, CATS), "pr-verdict")

    def test_guess_is_the_hidden_guess_else_the_marked_option(self):
        self.assertEqual(calibration.guess_of(q("a", "x", "y", rec="y")), {"value": "y", "visible": True})
        self.assertIsNone(calibration.guess_of(q("a", "x", "y")))  # held call, no recommendation
        held = {**q("a", "x", "y"), "guess": {"value": "y", "reason": "r"}}
        self.assertEqual(calibration.guess_of(held), {"value": "y", "visible": False})
        self.assertIsNone(calibration.guess_of({**q("a", "x"), "guess": {"value": "nope"}}))

    def test_hidden_guesses_are_always_blind(self):
        tmp = tempfile.mkdtemp()
        try:
            packet = {"questions": [{**q(f"h{i}", "x", "y"), "guess": {"value": "x"}} for i in range(5)] + [q("none", "x", "y")]}
            s = calibration.build_seal(packet, "batch-2", tmp, "sha")
            self.assertEqual(s["blind"], [f"h{i}" for i in range(5)])
        finally:
            shutil.rmtree(tmp)


class Seal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cal = os.path.join(self.tmp, "cal")
        self.folder = os.path.join(self.tmp, "packets", "batch-1")
        write(os.path.join(self.cal, "categories.json"), CATS)
        qs = [q(f"q{i}", "a", "b", rec="a", pr="yalesites-org/atomic#1") for i in range(40)]
        write(os.path.join(self.folder, "packet.json"), {"questions": qs})

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_about_one_in_four_blind_in_shadow(self):
        s = calibration.seal(self.folder, "batch-1", self.cal)
        self.assertTrue(4 <= len(s["blind"]) <= 18, s["blind"])
        self.assertEqual(s["prefill"], [])
        self.assertTrue(os.path.isfile(os.path.join(self.folder, "seal.json")))

    def test_rung_one_prefills_and_never_blinds(self):
        write(os.path.join(self.cal, "state.json"), {"blindRate": 4, "categories": {"pr-product": {"rung": 1}}})
        s = calibration.seal(self.folder, "batch-1", self.cal)
        self.assertEqual(s["blind"], [])
        self.assertEqual(len(s["prefill"]), 40)

    def test_seal_is_kept_once_answered_even_if_packet_changes(self):
        first = calibration.seal(self.folder, "batch-1", self.cal)
        write(os.path.join(self.folder, "answers.json"), {"answers": []})
        write(os.path.join(self.folder, "packet.json"), {"questions": [q("new", "a")]})
        self.assertEqual(calibration.seal(self.folder, "batch-1", self.cal)["packetSha"], first["packetSha"])

    def test_unanswered_packet_is_resealed_after_a_change(self):
        first = calibration.seal(self.folder, "batch-1", self.cal)
        write(os.path.join(self.folder, "packet.json"), {"questions": [q("new", "a")]})
        self.assertNotEqual(calibration.seal(self.folder, "batch-1", self.cal)["packetSha"], first["packetSha"])

    def test_demo_packets_get_nothing(self):
        demo = os.path.join(self.tmp, "packets", "demo")
        shutil.copytree(self.folder, demo)
        s = calibration.seal(demo, "demo", self.cal)
        self.assertEqual((s["blind"], s["prefill"]), ([], []))


class Leaks(unittest.TestCase):
    def test_brief_that_restates_our_pick_is_not_blind(self):
        rec = {"value": "close", "label": "Close as done", "detail": "Close with a short comment recording what the meeting decided."}
        self.assertTrue(calibration.leaks({"brief": ["Packet done. Close with a short comment recording what the meeting decided."]}, rec))
        self.assertTrue(calibration.leaks({"question": "We recommend closing it."}, rec))
        self.assertFalse(calibration.leaks({"brief": ["The packet shipped before the meeting."]}, rec))


class Snapshot(unittest.TestCase):
    def test_copies_and_keeps_different_packets_apart(self):
        tmp = tempfile.mkdtemp()
        try:
            cal, folder = os.path.join(tmp, "cal"), os.path.join(tmp, "p", "demo")
            write(os.path.join(folder, "packet.json"), {"questions": [1]})
            write(os.path.join(folder, "answers.json"), {"answers": []})
            first = calibration.snapshot(folder, "demo", cal)
            self.assertTrue(os.path.isfile(os.path.join(first, "answers.json")))
            write(os.path.join(folder, "packet.json"), {"questions": [2]})
            second = calibration.snapshot(folder, "demo", cal)
            self.assertNotEqual(first, second)
        finally:
            shutil.rmtree(tmp)


class ServerHooks(unittest.TestCase):
    def test_open_seals_and_save_snapshots(self):
        tmp = tempfile.mkdtemp()
        try:
            packets, cal = os.path.join(tmp, "packets"), os.path.join(tmp, "cal")
            write(os.path.join(packets, "ysp-9", "packet.json"), {"questions": [q("a", "x", "y")]})
            httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(packets, cal_dir=cal))
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            port = httpd.server_address[1]
            urllib.request.urlopen(f"http://localhost:{port}/packets/ysp-9/packet.json").read()
            self.assertTrue(os.path.isfile(os.path.join(packets, "ysp-9", "seal.json")))
            req = urllib.request.Request(f"http://localhost:{port}/api/answers?packet=ysp-9", method="POST",
                                         data=b'{"answers": []}', headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req).read()
            for name in ("packet.json", "seal.json", "answers.json"):
                self.assertTrue(os.path.isfile(os.path.join(cal, "boards", "ysp-9", name)), name)
            httpd.shutdown()
            httpd.server_close()
        finally:
            shutil.rmtree(tmp)

    def test_off_by_default_in_make_handler(self):
        tmp = tempfile.mkdtemp()
        try:
            write(os.path.join(tmp, "x", "packet.json"), {"questions": [q("a", "x")]})
            httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(tmp))
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            urllib.request.urlopen(f"http://localhost:{httpd.server_address[1]}/packets/x/packet.json").read()
            self.assertFalse(os.path.exists(os.path.join(tmp, "x", "seal.json")))
            httpd.shutdown()
            httpd.server_close()
        finally:
            shutil.rmtree(tmp)


@unittest.skipUnless(NODE, "node not installed")
class BoardJs(unittest.TestCase):
    def test_blind_needs_a_guess_and_shuffle_is_stable(self):
        packet = {"questions": [q("a", "x", "y", "z", rec="x"), {"id": "b", "options": [{"value": "x"}]},
                                {"id": "c", "options": [{"value": "x"}, {"value": "y"}], "guess": {"value": "y"}}]}
        out = run(packet, {"answers": []}, [], """
          seal = { blind: ['a', 'b'], prefill: [] };
          const s1 = stableShuffle(packet.questions[0].options, 'p:a').map(o => o.value);
          const s2 = stableShuffle(packet.questions[0].options, 'p:a').map(o => o.value);
          out = { a: isBlind(packet.questions[0]), b: isBlind(packet.questions[1]), c: isBlind(packet.questions[2]),
                  same: s1.join() === s2.join(), n: s1.length, rec: recOf(packet.questions[0]).value,
                  hidden: recOf(packet.questions[2]).value, none: recOf(packet.questions[1]) };
        """)
        self.assertEqual(out, {"a": True, "b": False, "c": True, "same": True, "n": 3, "rec": "x", "hidden": "y", "none": None})


if __name__ == "__main__":
    unittest.main()
