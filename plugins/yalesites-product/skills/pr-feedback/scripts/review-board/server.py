#!/usr/bin/env python3
"""Review board for pr-feedback Step 3b.

Serves the board UI from this folder and review packets from --packets, and
saves the reviewer's answers next to the packet they belong to.

  python3 server.py --packets <dir> [--port 8765]

A packet is <dir>/<id>/packet.json plus the images and clips it names. The board lives at
http://localhost:<port>/?packet=<id>. Submitting writes <dir>/<id>/answers.json.

If the port is taken, the next free one (up to 20 higher) is used, unless
--exact-port is set, in which case it exits instead. The chosen URL is printed
as a single line starting with REVIEW_BOARD_URL.
"""
import argparse
import json
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

BOARD_DIR = os.path.dirname(os.path.abspath(__file__))
APP = "pr-feedback-review-board"
PACKET_ID = re.compile(r"^[A-Za-z0-9._-]+$")
RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")


def make_handler(packets_dir):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=BOARD_DIR, **kwargs)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def translate_path(self, path):
            url_path = unquote(urlparse(path).path)
            if url_path.startswith("/packets/"):
                rel = url_path[len("/packets/"):]
                full = os.path.realpath(os.path.join(packets_dir, rel))
                if full == packets_dir or full.startswith(packets_dir + os.sep):
                    return full
                return os.path.join(packets_dir, "__denied__")
            if url_path in ("/", "/index.html"):
                return os.path.join(BOARD_DIR, "index.html")
            return os.path.join(BOARD_DIR, "__not_found__")

        def do_GET(self):
            if urlparse(self.path).path == "/api/health":
                body = json.dumps({"app": APP, "packets": packets_dir}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.headers.get("Range") and self.send_range():
                return
            super().do_GET()

        def send_range(self):
            # Browsers need byte ranges to seek in a video. Single ranges only.
            m = RANGE.match(self.headers["Range"].strip())
            path = self.translate_path(self.path)
            if not m or not os.path.isfile(path):
                return False
            size = os.path.getsize(path)
            start, end = m.group(1), m.group(2)
            if start == "":
                start, end = max(0, size - int(end)), size - 1
            else:
                start, end = int(start), min(int(end), size - 1) if end else size - 1
            if start >= size or start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return True
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(64 * 1024, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            return True

        def do_POST(self):
            url = urlparse(self.path)
            packet = parse_qs(url.query).get("packet", [""])[0]
            if url.path != "/api/answers" or not PACKET_ID.match(packet):
                self.send_error(404)
                return
            folder = os.path.join(packets_dir, packet)
            if not os.path.isdir(folder):
                self.send_error(404, "Unknown packet")
                return
            length = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(length))
            except ValueError:
                self.send_error(400, "Invalid JSON")
                return
            tmp = os.path.join(folder, "answers.json.tmp")
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, os.path.join(folder, "answers.json"))
            self.send_response(204)
            self.end_headers()

        def log_message(self, fmt, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packets", required=True, help="Folder that holds packet folders")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--exact-port", action="store_true", help="Exit if --port is taken")
    args = parser.parse_args()
    packets_dir = os.path.realpath(args.packets)
    os.makedirs(packets_dir, exist_ok=True)
    handler = make_handler(packets_dir)
    last = args.port if args.exact_port else args.port + 20
    for port in range(args.port, last + 1):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            continue
    else:
        sys.exit(f"No free port between {args.port} and {last}")
    print(f"REVIEW_BOARD_URL http://localhost:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
