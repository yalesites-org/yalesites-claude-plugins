#!/usr/bin/env python3
"""Screenshot published yalesites.yale.edu pages and map their blocks.

  python3 capture.py --packet <packet-dir> <item-id>=<url-or-path> [...]
                     [--width 1280] [--browser chrome|firefox]

For each item, writes <packet-dir>/<item-id>/current.png (full page) and
current.json (title, teaser, sections, and every Layout Builder block with its
type, padding, markdown, and position as a percentage of the page height).

It runs headless and logged out, in its own Playwright CLI session, so it never
touches the visible browser that yalesites-page-build logs in with. It only
reads public pages. A page that does not return 200 gets a current.json with
the status and no screenshot, so the caller can treat it as a new page.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = ["npx", "-y", "@playwright/cli@0.1.22"]
SESSION = "docs-board-capture"
SITE = "https://yalesites.yale.edu"
ITEM_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def build_code(url, shot, width, body):
    consts = "".join(f"const {k} = {json.dumps(v)};\n" for k, v in
                     (("URL", url), ("SHOT", shot), ("WIDTH", width)))
    return "async page => {\n" + consts + body + "\n}"


def parse_result(output):
    """The CLI prints the function's return value under '### Result'."""
    m = re.search(r"### Result\s*\n(.*?)(?:\n### |\Z)", output, re.S)
    if not m:
        raise ValueError("no '### Result' in playwright-cli output:\n" + output[-2000:])
    return json.loads(m.group(1).strip())


def run(args, cwd, check=True):
    # The CLI writes a .playwright-cli/ log folder wherever it runs, so it runs
    # in the packet folder rather than in the user's repo checkout.
    return subprocess.run(CLI + [f"-s={SESSION}"] + args, capture_output=True, text=True, check=check, cwd=cwd)


def parse_targets(pairs):
    targets = []
    for pair in pairs:
        item, sep, url = pair.partition("=")
        if not sep or not ITEM_ID.match(item):
            sys.exit(f"Expected <item-id>=<url>, got {pair!r}")
        if url.startswith("/"):
            url = SITE + url
        if not url.startswith(SITE):
            sys.exit(f"{url} is not on {SITE}. Internal docs are read from the repo, not captured.")
        targets.append((item, url))
    return targets


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--packet", required=True)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--browser", default=None, help="Same --browser value page-build uses, if Chrome is missing")
    ap.add_argument("targets", nargs="+")
    a = ap.parse_args()

    targets = parse_targets(a.targets)
    packet_dir = os.path.realpath(a.packet)
    os.makedirs(packet_dir, exist_ok=True)
    with open(os.path.join(HERE, "capture.js"), encoding="utf-8") as f:
        body = f.read()
    open_args = ["open", "about:blank"] + (["--browser", a.browser] if a.browser else [])
    opened = run(open_args, packet_dir, check=False)
    if opened.returncode != 0:
        sys.exit("Could not open a browser. See the Browsers table in "
                 "pr-feedback/references/drive-it.md.\n" + opened.stderr[-1500:])
    failures = 0
    try:
        for item, url in targets:
            folder = os.path.join(packet_dir, item)
            os.makedirs(folder, exist_ok=True)
            shot = os.path.join(folder, "current.png")
            if os.path.exists(shot):
                os.remove(shot)
            res = run(["run-code", build_code(url, shot, a.width, body)], packet_dir, check=False)
            try:
                data = parse_result(res.stdout + res.stderr)
            except ValueError as exc:
                failures += 1
                print(f"{item}: FAILED {url}\n{exc}", file=sys.stderr)
                continue
            data["url"] = url
            data["screenshot"] = "current.png" if os.path.exists(shot) else None
            with open(os.path.join(folder, "current.json"), "w") as f:
                json.dump(data, f, indent=1)
            if data["status"] != 200:
                print(f"{item}: {data['status']} {url} (no screenshot; treat as a new page or fix the URL)")
            else:
                print(f"{item}: {len(data['blocks'])} blocks, {data['pageHeight']}px tall, {url}")
    finally:
        run(["close"], packet_dir, check=False)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
