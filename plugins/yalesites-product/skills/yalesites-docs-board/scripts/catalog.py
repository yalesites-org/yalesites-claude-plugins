#!/usr/bin/env python3
"""Catalog of every page on yalesites.yale.edu, built from the live sitemap.

  python3 catalog.py refresh [--force] [--max-age-hours 24]
  python3 catalog.py search <words...> [--limit 8] [--json]
  python3 catalog.py show <path>
  python3 catalog.py section <name>

`refresh` reads sitemap.xml, fetches each page once (logged out, 8 at a time)
for its title, teaser, and headings, and merges in the nav location and content
cluster from the web-content skill's inventory snapshot. The result is cached at
~/.claude/yalesites/docs-board/catalog.json and reused until it is a day old.

`search` ranks pages against a ticket's words, so "is there already a page for
this" is one command instead of a round of fetches. Title matches weigh most,
then the URL path, then headings and the teaser.
"""
import argparse
import csv
import html
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse

SITE = "https://yalesites.yale.edu"
SITEMAP = SITE + "/sitemap.xml"
CACHE = os.path.expanduser("~/.claude/yalesites/docs-board/catalog.json")
# realpath, so a symlinked install still finds the sibling web-content skill.
HERE = os.path.dirname(os.path.realpath(__file__))
INVENTORY = os.path.join(HERE, "..", "..", "yalesites-web-content", "references", "content-inventory.csv")
UA = "yalesites-docs-board/1.0 (+https://github.com/yalesites-org/yalesites-claude-plugins)"

# Event instances are dated copies of one training. They are real pages, but
# no docs ticket targets them and they drown out search results.
SKIP_PREFIXES = ("/upcoming-events/",)

STOP = set("a an and are as at be by docs doc for from how in into is it of on or page the this to user guide with add update document new yalesites".split())



def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def norm_path(url):
    path = urlparse(url).path or "/"
    if len(path) > 1:
        path = path.rstrip("/")
    return path


def parse_sitemap(xml):
    """Return (locs, child_sitemaps). Handles a urlset and a sitemapindex."""
    children = re.findall(r"<sitemap>\s*<loc>([^<]+)</loc>", xml)
    entries = []
    for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
        loc = re.search(r"<loc>([^<]+)</loc>", block)
        if not loc:
            continue
        mod = re.search(r"<lastmod>([^<]+)</lastmod>", block)
        entries.append({"path": norm_path(html.unescape(loc.group(1).strip())),
                        "lastmod": mod.group(1).strip() if mod else None})
    return entries, [html.unescape(c.strip()) for c in children]


def _text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_page(doc):
    """Pull what search needs out of one page's HTML."""
    title = re.search(r"<title>(.*?)</title>", doc, re.S)
    title = _text(title.group(1)) if title else ""
    title = re.sub(r"\s*\|\s*YaleSites\s*$", "", title)
    desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', doc)
    main = doc
    m = re.search(r"<main\b.*?</main>", doc, re.S)
    if m:
        main = m.group(0)
    heads = [_text(h) for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", main, re.S)]
    blocks = len(re.findall(r'class="ys-block-wrapper', main))
    return {
        "title": title,
        "teaser": html.unescape(desc.group(1)).strip() if desc else "",
        "headings": [h for h in heads if h][:30],
        "blocks": blocks,
    }


def load_inventory(path=INVENTORY):
    rows = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                p = (r.get("URL Path") or "").strip()
                if p:
                    rows[norm_path(p)] = {
                        "section": r.get("Section (from URL)") or "",
                        "nav": r.get("Nav Location") or "",
                        "cluster": r.get("Content Cluster (from tags)") or "",
                        "type": r.get("Type") or "",
                    }
    except OSError:
        pass
    return rows


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def refresh(force=False, max_age_hours=24, out=CACHE):
    if not force and os.path.exists(out):
        age = (time.time() - os.path.getmtime(out)) / 3600
        if age < max_age_hours:
            print(f"Catalog is {age:.1f}h old, reusing {out}. Pass --force to rebuild.")
            return read_json(out)
    _, xml = fetch(SITEMAP)
    entries, children = parse_sitemap(xml)
    for child in children:
        entries += parse_sitemap(fetch(child)[1])[0]
    seen, pages = set(), []
    for e in entries:
        if e["path"] in seen or e["path"].startswith(SKIP_PREFIXES):
            continue
        seen.add(e["path"])
        pages.append(e)

    def one(e):
        try:
            status, doc = fetch(SITE + e["path"])
            return {**e, "status": status, **parse_page(doc)}
        except Exception as exc:  # a dead page stays listed, so it can still be matched
            return {**e, "status": getattr(exc, "code", None) or "error", "title": "", "teaser": "", "headings": [], "blocks": 0}

    with ThreadPoolExecutor(max_workers=8) as pool:
        pages = list(pool.map(one, pages))
    inv = load_inventory()
    for p in pages:
        p.update(inv.get(p["path"], {}))
    catalog = {
        "builtAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sitemap": SITEMAP,
        "pages": sorted(pages, key=lambda p: p["path"]),
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(catalog, f, indent=1)
    os.replace(tmp, out)
    failed = sum(1 for p in pages if p["status"] != 200)
    print(f"Catalog built: {len(pages)} pages ({failed} did not load) -> {out}")
    return catalog


def stem(t):
    """Crude, but enough that a ticket saying "export" finds "Exporting Content"."""
    for suffix in ("ing", "ed", "es", "s"):
        if len(t) > len(suffix) + 3 and t.endswith(suffix):
            return t[: -len(suffix)]
    return t


def tokens(s):
    out = (stem(t) for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP)
    return [t for t in out if t not in STOP and len(t) > 1]


def score(page, words):
    if not words:
        return 0
    title = set(tokens(page.get("title", "")))
    path = set(tokens(page.get("path", "")))
    heads = set(tokens(" ".join(page.get("headings", []))))
    teaser = set(tokens(page.get("teaser", "")))
    s = 0.0
    for w in set(words):
        s += 3 * (w in title) + 2 * (w in path) + 1 * (w in heads) + 0.5 * (w in teaser)
    phrase = " ".join(words)
    if len(words) > 1 and phrase in " ".join(tokens(page.get("title", ""))):
        s += 3
    return s


def search(catalog, query, limit=8):
    words = tokens(query)
    ranked = sorted(((score(p, words), p) for p in catalog["pages"]), key=lambda x: -x[0])
    return [(s, p) for s, p in ranked if s > 0][:limit]


def load(path=CACHE):
    if not os.path.exists(path):
        sys.exit("No catalog yet. Run: python3 catalog.py refresh")
    return read_json(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("refresh")
    r.add_argument("--force", action="store_true")
    r.add_argument("--max-age-hours", type=float, default=24)
    s = sub.add_parser("search")
    s.add_argument("words", nargs="+")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--json", action="store_true")
    sh = sub.add_parser("show")
    sh.add_argument("path")
    se = sub.add_parser("section")
    se.add_argument("name", nargs="+")
    a = ap.parse_args()

    if a.cmd == "refresh":
        refresh(a.force, a.max_age_hours)
        return
    cat = load()
    age_h = (time.time() - os.path.getmtime(CACHE)) / 3600
    if age_h > 24:
        print(f"(catalog is {age_h:.0f}h old; run refresh for current titles)", file=sys.stderr)
    if a.cmd == "search":
        hits = search(cat, " ".join(a.words), a.limit)
        if a.json:
            print(json.dumps([{**p, "score": sc} for sc, p in hits], indent=1))
            return
        if not hits:
            print("No match. Treat this as a new page and propose where it goes.")
        for sc, p in hits:
            nav = f"  [{p['nav']}]" if p.get("nav") else ""
            print(f"{sc:5.1f}  {p['path']}  {p['title']}{nav}")
    elif a.cmd == "show":
        want = norm_path(a.path)
        page = next((p for p in cat["pages"] if p["path"] == want), None)
        if not page:
            sys.exit(f"{want} is not in the sitemap")
        print(json.dumps(page, indent=1))
    elif a.cmd == "section":
        # Paths on this site are flat (/editorial-workflow), so siblings come
        # from the inventory's section and nav columns, not from the URL.
        name = " ".join(a.name).lower()
        for p in cat["pages"]:
            where = f"{p.get('section', '')} | {p.get('nav', '')} | {p.get('cluster', '')}"
            if name in where.lower():
                print(f"{p['path']}  {p['title']}  [{where}]")


if __name__ == "__main__":
    main()
