#!/usr/bin/env python3
"""Tests for the review board server. Run: python3 test_server.py"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import server  # noqa: E402


class ReviewBoardServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.packets = os.path.realpath(cls.tmp.name)
        os.makedirs(os.path.join(cls.packets, "ysp-1"))
        with open(os.path.join(cls.packets, "ysp-1", "packet.json"), "w") as f:
            json.dump({"title": "T", "questions": []}, f)
        with open(os.path.join(cls.packets, "ysp-1", "clip.webm"), "wb") as f:
            f.write(bytes(range(100)))
        with open(os.path.join(cls.tmp.name, "..", "outside.txt"), "w") as f:
            f.write("secret")
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(cls.packets))
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        os.remove(os.path.join(cls.tmp.name, "..", "outside.txt"))
        cls.tmp.cleanup()

    def status(self, path, data=None, headers=None):
        req = urllib.request.Request(self.base + path, data=data, headers=headers or {},
                                     method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req) as res:
                return res.status, res.read()
        except urllib.error.HTTPError as e:
            return e.code, b""

    def ranged(self, path, spec):
        return self.status(path, headers={"Range": spec})

    def test_health_names_the_app_and_packets_dir(self):
        code, body = self.status("/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body), {"app": server.APP, "packets": self.packets})

    def test_serves_board_and_packet(self):
        self.assertEqual(self.status("/?packet=ysp-1")[0], 200)
        code, body = self.status("/packets/ysp-1/packet.json")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["title"], "T")

    def test_only_index_is_served_from_board_dir(self):
        self.assertEqual(self.status("/server.py")[0], 404)
        self.assertEqual(self.status("/test_server.py")[0], 404)

    def test_packet_paths_cannot_escape(self):
        self.assertEqual(self.status("/packets/../outside.txt")[0], 404)
        self.assertEqual(self.status("/packets/%2e%2e/outside.txt")[0], 404)

    def test_clips_serve_byte_ranges_for_seeking(self):
        clip = "/packets/ysp-1/clip.webm"
        self.assertEqual(self.ranged(clip, "bytes=10-19"), (206, bytes(range(10, 20))))
        self.assertEqual(self.ranged(clip, "bytes=95-"), (206, bytes(range(95, 100))))
        self.assertEqual(self.ranged(clip, "bytes=-3"), (206, bytes(range(97, 100))))
        self.assertEqual(self.ranged(clip, "bytes=90-500"), (206, bytes(range(90, 100))))
        self.assertEqual(self.ranged(clip, "bytes=200-")[0], 416)
        self.assertEqual(self.ranged(clip, "bytes=0-1,5-6"), (200, bytes(range(100))))
        self.assertEqual(self.ranged("/packets/../outside.txt", "bytes=0-1")[0], 404)

    def test_post_writes_answers(self):
        code, _ = self.status("/api/answers?packet=ysp-1", json.dumps({"answers": [1]}).encode())
        self.assertEqual(code, 204)
        with open(os.path.join(self.packets, "ysp-1", "answers.json")) as f:
            self.assertEqual(json.load(f), {"answers": [1]})

    def test_post_rejects_bad_ids_and_bad_json(self):
        self.assertEqual(self.status("/api/answers?packet=../x", b"{}")[0], 404)
        self.assertEqual(self.status("/api/answers?packet=missing", b"{}")[0], 404)
        self.assertEqual(self.status("/api/answers?packet=ysp-1", b"not json")[0], 400)


class PortChoiceTest(unittest.TestCase):
    def run_server(self, *args):
        with tempfile.TemporaryDirectory() as packets:
            proc = subprocess.Popen([sys.executable, os.path.join(HERE, "server.py"), "--packets", packets, *args],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                line = proc.stdout.readline()
                if not line:
                    proc.wait(5)
                    return proc.returncode, proc.stderr.read()
                return None, line
            finally:
                proc.kill()
                proc.wait()

    def test_falls_forward_or_exits_when_port_taken(self):
        with socket.socket() as busy:
            busy.bind(("127.0.0.1", 0))
            busy.listen()
            port = busy.getsockname()[1]
            code, out = self.run_server("--port", str(port))
            self.assertIsNone(code)
            self.assertTrue(out.startswith("REVIEW_BOARD_URL http://localhost:"))
            self.assertNotIn(f":{port}\n", out)
            code, err = self.run_server("--port", str(port), "--exact-port")
            self.assertNotEqual(code, 0)
            self.assertIn("No free port", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
