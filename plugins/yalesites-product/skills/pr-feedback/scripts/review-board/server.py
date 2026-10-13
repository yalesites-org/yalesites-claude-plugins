#!/usr/bin/env python3
"""Review board for pr-feedback Step 3b, and the server behind yalesites-docs-board.

Serves a board UI from --board-dir and packets from --packets, and saves what
the reviewer sends next to the packet it belongs to.

  python3 server.py --packets <dir> [--port 8765]
  python3 server.py --packets <dir> --board-dir <dir-with-index.html> \
      --route /api/decisions --out decisions.json --app docs-board [--port 8775]

A packet is <dir>/<id>/packet.json plus the files it names. The board lives at
http://localhost:<port>/?packet=<id>. A POST to --route (default /api/answers)
writes <dir>/<id>/<--out> (default answers.json). The defaults are pr-feedback's
review board. yalesites-docs-board starts this same server with its own
--board-dir, --route, --out, and --app, so one copy serves both.

A POST is accepted only from the board itself: the Host (and the Origin, when a
browser sends one) must be localhost or 127.0.0.1 on this port, and the body
must be sent as application/json. A page on another site cannot write the file.

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
ROUTE = "/api/answers"
OUT = "answers.json"
PACKET_ID = re.compile(r"^[A-Za-z0-9._-]+$")
RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")
LOCAL_HOSTS = ("localhost", "127.0.0.1")


def make_handler(packets_dir, board_dir=BOARD_DIR, route=ROUTE, out=OUT, app=APP):
    board_dir = os.path.realpath(board_dir)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=board_dir, **kwargs)

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
                return os.path.join(board_dir, "index.html")
            return os.path.join(board_dir, "__not_found__")

        def send_json(self, status, payload):
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if urlparse(self.path).path == "/api/health":
                self.send_json(200, {"app": app, "packets": packets_dir})
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

        def same_origin(self):
            """True when the request comes from this board, not from another site.

            A cross-site form post or no-cors fetch carries the other site's
            Origin (or none, with a foreign Host), so checking both against
            this server's own address shuts it out.
            """
            port = self.server.server_address[1]
            allowed = {f"{host}:{port}" for host in LOCAL_HOSTS}
            if self.headers.get("Host", "") not in allowed:
                return False
            origin = self.headers.get("Origin")
            if origin is None:
                return True
            parsed = urlparse(origin)
            return parsed.scheme == "http" and parsed.netloc in allowed

        def do_POST(self):
            url = urlparse(self.path)
            packet = parse_qs(url.query).get("packet", [""])[0]
            if url.path != route or not PACKET_ID.match(packet):
                self.send_error(404)
                return
            if not self.same_origin():
                self.send_json(403, {"error": "POST must come from this board on localhost"})
                return
            ctype = self.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if ctype != "application/json":
                self.send_json(403, {"error": "Content-Type must be application/json"})
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
            tmp = os.path.join(folder, out + ".tmp")
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, os.path.join(folder, out))
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
    parser.add_argument("--board-dir", default=BOARD_DIR, help="Folder holding the index.html to serve")
    parser.add_argument("--route", default=ROUTE, help="POST path the board sends to")
    parser.add_argument("--out", default=OUT, help="File written next to the packet on POST")
    parser.add_argument("--app", default=APP, help="Name reported by /api/health")
    args = parser.parse_args()
    packets_dir = os.path.realpath(args.packets)
    os.makedirs(packets_dir, exist_ok=True)
    if not os.path.isfile(os.path.join(args.board_dir, "index.html")):
        sys.exit(f"No index.html in {args.board_dir}")
    handler = make_handler(packets_dir, args.board_dir, args.route, args.out, args.app)
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
