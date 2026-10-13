#!/usr/bin/env python3
"""Tests for the review board server. Run: python3 test_server.py

The same server backs yalesites-docs-board's board (its --board-dir, --route,
--out, and --app flags), so the docs-board cases live here too.
"""
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

# The docs board lives in the sibling skill. realpath, so a symlinked install
# still resolves it, the same way catalog.py finds yalesites-web-content.
DOCS_BOARD_DIR = os.path.realpath(os.path.join(HERE, "..", "..", "..", "yalesites-docs-board", "scripts", "board"))
JSON = {"Content-Type": "application/json"}


class ServerTestBase(unittest.TestCase):
    handler_kwargs = {}

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.packets = os.path.realpath(cls.tmp.name)
        os.makedirs(os.path.join(cls.packets, "ysp-1"))
        with open(os.path.join(cls.packets, "ysp-1", "packet.json"), "w") as f:
            json.dump({"title": "T", "questions": [], "items": []}, f)
        with open(os.path.join(cls.packets, "ysp-1", "clip.webm"), "wb") as f:
            f.write(bytes(range(100)))
        with open(os.path.join(cls.tmp.name, "..", "outside.txt"), "w") as f:
            f.write("secret")
        # A prepped packet lives outside the packets folder, in a versioned folder named by
        # prep_status.py, and is reached through a symlink named for the packet id.
        cls.prepped = tempfile.TemporaryDirectory()
        cls.prepped_packet = os.path.join(os.path.realpath(cls.prepped.name), "ysp-2-abc1234-20261004T130500Z")
        os.makedirs(cls.prepped_packet)
        with open(os.path.join(cls.prepped_packet, "packet.json"), "w") as f:
            json.dump({"title": "Prepped", "questions": []}, f)
        with open(os.path.join(cls.prepped_packet, "01-fail.png"), "wb") as f:
            f.write(b"png")
        os.symlink(cls.prepped_packet, os.path.join(cls.packets, "ysp-2"))
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(cls.packets, **cls.handler_kwargs))
        cls.port = cls.httpd.server_address[1]
        cls.base = f"http://127.0.0.1:{cls.port}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        os.remove(os.path.join(cls.tmp.name, "..", "outside.txt"))
        cls.tmp.cleanup()
        cls.prepped.cleanup()

    def status(self, path, data=None, headers=None):
        req = urllib.request.Request(self.base + path, data=data, headers=headers or {},
                                     method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req) as res:
                return res.status, res.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def post(self, path, data, **extra):
        return self.status(path, data, {**JSON, **extra})

    def ranged(self, path, spec):
        return self.status(path, headers={"Range": spec})


class ReviewBoardServerTest(ServerTestBase):
    def test_health_names_the_app_and_packets_dir(self):
        code, body = self.status("/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body), {"app": server.APP, "packets": self.packets})

    def test_serves_board_and_packet(self):
        code, body = self.status("/?packet=ysp-1")
        self.assertEqual(code, 200)
        self.assertIn(b"<title>Review board</title>", body)
        code, body = self.status("/packets/ysp-1/packet.json")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["title"], "T")

    def test_only_index_is_served_from_board_dir(self):
        self.assertEqual(self.status("/server.py")[0], 404)
        self.assertEqual(self.status("/test_server.py")[0], 404)

    def test_packet_paths_cannot_escape(self):
        self.assertEqual(self.status("/packets/../outside.txt")[0], 404)
        self.assertEqual(self.status("/packets/%2e%2e/outside.txt")[0], 404)
        self.assertEqual(self.status("/packets/ysp-1/../ysp-2/packet.json")[0], 404)
        self.assertEqual(self.status("/packets/ysp-2/../outside.txt")[0], 404)

    def test_symlinked_packet_is_served_and_answered_in_place(self):
        code, body = self.status("/packets/ysp-2/packet.json")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["title"], "Prepped")
        self.assertEqual(self.status("/packets/ysp-2/01-fail.png"), (200, b"png"))
        code, _ = self.post("/api/answers?packet=ysp-2", json.dumps({"answers": [2]}).encode())
        self.assertEqual(code, 204)
        with open(os.path.join(self.prepped_packet, "answers.json")) as f:
            self.assertEqual(json.load(f), {"answers": [2]})

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
        code, _ = self.post("/api/answers?packet=ysp-1", json.dumps({"answers": [1]}).encode())
        self.assertEqual(code, 204)
        with open(os.path.join(self.packets, "ysp-1", "answers.json")) as f:
            self.assertEqual(json.load(f), {"answers": [1]})

    def test_post_rejects_bad_ids_bad_json_and_other_routes(self):
        self.assertEqual(self.post("/api/answers?packet=../x", b"{}")[0], 404)
        self.assertEqual(self.post("/api/answers?packet=missing", b"{}")[0], 404)
        self.assertEqual(self.post("/api/answers?packet=ysp-1", b"not json")[0], 400)
        self.assertEqual(self.post("/api/decisions?packet=ysp-1", b"{}")[0], 404)

    def test_post_from_the_board_itself_is_accepted(self):
        for origin in (f"http://localhost:{self.port}", f"http://127.0.0.1:{self.port}"):
            code, _ = self.post("/api/answers?packet=ysp-1", b'{"ok": 1}', Origin=origin, Host=f"localhost:{self.port}")
            self.assertEqual(code, 204, origin)

    def test_post_from_another_site_is_refused(self):
        body = b'{"answers": [{"id": "x", "choice": "approve"}]}'
        before = os.path.getmtime(os.path.join(self.packets, "ysp-1", "answers.json")) if os.path.exists(
            os.path.join(self.packets, "ysp-1", "answers.json")) else None
        for headers in (
            {"Origin": "https://evil.example"},
            {"Origin": f"http://localhost:{self.port + 1}"},
            {"Origin": "null"},
            {"Host": "evil.example"},
            {"Host": f"localhost:{self.port + 1}"},
        ):
            code, res = self.post("/api/answers?packet=ysp-1", body, **headers)
            self.assertEqual(code, 403, headers)
            self.assertIn("error", json.loads(res))
        if before is not None:
            self.assertEqual(os.path.getmtime(os.path.join(self.packets, "ysp-1", "answers.json")), before)

    def test_post_without_json_content_type_is_refused(self):
        for ctype in ("text/plain", "application/x-www-form-urlencoded", "multipart/form-data"):
            code, res = self.status("/api/answers?packet=ysp-1", b"{}", {"Content-Type": ctype})
            self.assertEqual(code, 403, ctype)
            self.assertIn("application/json", json.loads(res)["error"])
        self.assertEqual(self.status("/api/answers?packet=ysp-1", b"{}", {"Content-Type": "application/json; charset=utf-8"})[0], 204)


class DocsBoardServerTest(ServerTestBase):
    """The same server, started the way yalesites-docs-board starts it."""
    handler_kwargs = {"board_dir": DOCS_BOARD_DIR, "route": "/api/decisions", "out": "decisions.json", "app": "docs-board"}

    def test_health_names_the_docs_board(self):
        code, body = self.status("/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body), {"app": "docs-board", "packets": self.packets})

    def test_serves_the_docs_board_index_and_nothing_else_from_its_folder(self):
        code, body = self.status("/?packet=ysp-1")
        self.assertEqual(code, 200)
        self.assertIn(b"<title>Docs board</title>", body)
        self.assertEqual(self.status("/index.html")[0], 200)
        self.assertEqual(self.status("/server.py")[0], 404)
        self.assertEqual(self.status("/packets/../outside.txt")[0], 404)

    def test_post_writes_decisions_on_its_own_route_only(self):
        code, _ = self.post("/api/decisions?packet=ysp-1", json.dumps({"decisions": [1]}).encode())
        self.assertEqual(code, 204)
        with open(os.path.join(self.packets, "ysp-1", "decisions.json")) as f:
            self.assertEqual(json.load(f), {"decisions": [1]})
        self.assertFalse(os.path.exists(os.path.join(self.packets, "ysp-1", "answers.json")))
        self.assertEqual(self.post("/api/answers?packet=ysp-1", b"{}")[0], 404)
        self.assertEqual(self.post("/api/decisions?packet=../x", b"{}")[0], 404)
        self.assertEqual(self.post("/api/decisions?packet=missing", b"{}")[0], 404)
        self.assertEqual(self.post("/api/decisions?packet=ysp-1", b"not json")[0], 400)

    def test_cross_site_post_is_refused_here_too(self):
        code, _ = self.post("/api/decisions?packet=ysp-1", b"{}", Origin="https://evil.example")
        self.assertEqual(code, 403)
        code, _ = self.status("/api/decisions?packet=ysp-1", b"{}", {"Content-Type": "text/plain"})
        self.assertEqual(code, 403)

    def test_post_cannot_write_outside_a_packet_folder(self):
        # `..` and `.` match PACKET_ID, so they must be refused by the folder resolution itself.
        parent = os.path.dirname(self.packets)
        self.assertEqual(self.status("/api/answers?packet=..", json.dumps({"answers": []}).encode())[0], 404)
        self.assertFalse(os.path.exists(os.path.join(parent, "answers.json")))
        self.assertFalse(os.path.exists(os.path.join(parent, "answers.json.tmp")))
        self.assertEqual(self.status("/api/answers?packet=.", json.dumps({"answers": []}).encode())[0], 404)
        self.assertFalse(os.path.exists(os.path.join(self.packets, "answers.json")))
        self.assertFalse(os.path.exists(os.path.join(self.packets, "answers.json.tmp")))
        self.assertEqual(self.status("/api/answers?packet=...", b"{}")[0], 404)
        self.assertEqual(self.status("/api/answers?packet=%2e%2e", b"{}")[0], 404)


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

    def test_docs_board_flags_start_the_same_server(self):
        code, out = self.run_server("--port", "0", "--board-dir", DOCS_BOARD_DIR, "--route", "/api/decisions",
                                    "--out", "decisions.json", "--app", "docs-board")
        self.assertIsNone(code)
        self.assertTrue(out.startswith("REVIEW_BOARD_URL http://localhost:"), out)
        # --port 0 lets the OS pick, and the line has to carry the port it picked.
        port = int(out.strip().rsplit(":", 1)[1])
        self.assertGreater(port, 0, out)

    def test_refuses_a_board_dir_without_an_index(self):
        with tempfile.TemporaryDirectory() as empty:
            code, err = self.run_server("--board-dir", empty)
            self.assertNotEqual(code, 0)
            self.assertIn("No index.html", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
