#!/usr/bin/env python3
"""Tests for catalog.py, capture.py, and packet.py. Run: python3 test_scripts.py

Nothing here touches the network or a browser. The live paths (fetching the
sitemap, running Playwright) are thin wrappers around the functions tested.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import capture  # noqa: E402
import catalog  # noqa: E402
import packet  # noqa: E402
from packet import read_json  # noqa: E402

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
 <url><loc>http://yalesites.yale.edu/</loc><lastmod>2026-09-28T12:09:24-04:00</lastmod></url>
 <url><loc>http://yalesites.yale.edu/editorial-workflow/</loc></url>
 <url><loc>http://yalesites.yale.edu/upcoming-events/2025-04-08-office-hours</loc></url>
 <url><loc>http://yalesites.yale.edu/a?x=1&amp;y=2</loc></url>
</urlset>"""

INDEX = """<sitemapindex><sitemap><loc>https://yalesites.yale.edu/sitemap.xml?page=2</loc></sitemap></sitemapindex>"""

PAGE = """<html><head><title>Editorial Workflow | YaleSites</title>
<meta name="description" content="Roles &amp; moderation."></head><body>
<nav><h2>Not in main</h2></nav>
<main><h1>Editorial Workflow</h1>
<div class="ys-block-wrapper"><div class="text-field"><h2>Who can <em>publish</em></h2><p>x</p></div></div>
<div class="ys-block-wrapper"><div class="callouts"><h3>Video Demo</h3></div></div>
</main></body></html>"""


class CatalogTest(unittest.TestCase):
    def test_parse_sitemap_normalizes_paths(self):
        entries, children = catalog.parse_sitemap(SITEMAP)
        self.assertEqual([e["path"] for e in entries],
                         ["/", "/editorial-workflow", "/upcoming-events/2025-04-08-office-hours", "/a"])
        self.assertEqual(entries[0]["lastmod"], "2026-09-28T12:09:24-04:00")
        self.assertEqual(children, [])

    def test_parse_sitemap_index_lists_children(self):
        self.assertEqual(catalog.parse_sitemap(INDEX)[1], ["https://yalesites.yale.edu/sitemap.xml?page=2"])

    def test_parse_page_reads_main_only(self):
        p = catalog.parse_page(PAGE)
        self.assertEqual(p["title"], "Editorial Workflow")
        self.assertEqual(p["teaser"], "Roles & moderation.")
        self.assertEqual(p["headings"], ["Who can publish", "Video Demo"])
        self.assertEqual(p["blocks"], 2)

    def test_search_ranks_title_over_teaser_and_drops_stopwords(self):
        cat = {"pages": [
            {"path": "/a", "title": "Something else", "teaser": "office hours mentioned", "headings": []},
            {"path": "/yalesites-office-hours", "title": "YaleSites Office Hours", "teaser": "", "headings": []},
            {"path": "/b", "title": "Unrelated", "teaser": "", "headings": []},
        ]}
        hits = catalog.search(cat, "Docs: Office Hours block user guide page")
        self.assertEqual([p["path"] for _, p in hits], ["/yalesites-office-hours", "/a"])
        self.assertEqual(catalog.search(cat, "the and docs"), [])

    def test_search_matches_word_forms(self):
        cat = {"pages": [{"path": "/finding-and-exporting-content", "title": "Finding and Exporting Content", "teaser": "", "headings": []}]}
        self.assertEqual(len(catalog.search(cat, "People CSV export")), 1)

    def test_inventory_merge_reads_bundled_csv(self):
        inv = catalog.load_inventory()
        self.assertIn("/editorial-workflow", inv)
        self.assertIn("User Guide", inv["/editorial-workflow"]["nav"])


class CaptureTest(unittest.TestCase):
    def test_parse_result_reads_the_result_section(self):
        out = '### Result\n{"status": 200, "blocks": []}\n### Ran Playwright code\n```js\n...\n```'
        self.assertEqual(capture.parse_result(out), {"status": 200, "blocks": []})
        with self.assertRaises(ValueError):
            capture.parse_result("### Error\nTimeoutError")

    def test_targets_accept_paths_and_refuse_other_sites(self):
        self.assertEqual(capture.parse_targets(["1818=/create-powerful-page-sections"]),
                         [("1818", "https://yalesites.yale.edu/create-powerful-page-sections")])
        with self.assertRaises(SystemExit):
            capture.parse_targets(["1770=https://github.com/x/y"])
        with self.assertRaises(SystemExit):
            capture.parse_targets(["../x=/a"])

    def test_build_code_quotes_values_safely(self):
        code = capture.build_code('https://yalesites.yale.edu/a"b', "/tmp/x y.png", 1280, "return 1;")
        self.assertTrue(code.startswith("async page => {\n"))
        self.assertIn('const URL = "https://yalesites.yale.edu/a\\"b";', code)
        self.assertIn("const WIDTH = 1280;", code)

    def test_capture_js_defines_everything_capture_py_passes(self):
        body = open(os.path.join(HERE, "capture.js")).read()
        for name in ("URL", "SHOT", "WIDTH"):
            self.assertIn(name, body)
        self.assertNotIn("const URL", body)


def write_packet(folder, items, blocks=None, screenshot=True):
    os.makedirs(os.path.join(folder, "1"), exist_ok=True)
    if blocks is not None:
        with open(os.path.join(folder, "1", "current.json"), "w") as f:
            json.dump({"status": 200, "screenshot": "current.png" if screenshot else None, "blocks": blocks}, f)
        if screenshot:
            open(os.path.join(folder, "1", "current.png"), "wb").close()
    with open(os.path.join(folder, "packet.json"), "w") as f:
        json.dump({"title": "T", "items": items}, f)


def edit_item(ops, **kw):
    return {"id": "1", "ticket": {"ref": "yalesites-org/YaleSites-Internal#1", "url": "u", "title": "t"},
            "kind": "edit", "target": {"url": "https://yalesites.yale.edu/x"}, "current": "1/current.json",
            "ops": ops, **kw}


BLOCKS = [{"id": "b1", "type": "Text", "markdown": "One"}, {"id": "b2", "type": "Text", "markdown": "Two"}]


class PacketValidateTest(unittest.TestCase):
    def check(self, items, blocks=BLOCKS, screenshot=True):
        with tempfile.TemporaryDirectory() as d:
            write_packet(d, items, blocks, screenshot)
            return packet.validate(d)

    def test_a_good_edit_passes(self):
        errors, _ = self.check([edit_item([
            {"op": "keep", "ref": "b1"},
            {"op": "add", "block": "Callout", "markdown": "New"},
            {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}])])
        self.assertEqual(errors, [])

    def test_every_live_block_must_be_accounted_for(self):
        errors, _ = self.check([edit_item([{"op": "keep", "ref": "b1"}])])
        self.assertTrue(any("b2" in e and "not in ops" in e for e in errors), errors)
        errors, _ = self.check([edit_item([{"op": "keep", "ref": "b1"}, {"op": "keep", "ref": "b1"}, {"op": "keep", "ref": "b2"}])])
        self.assertTrue(any("appears 2 times" in e for e in errors), errors)

    def test_remove_needs_a_reason_and_edit_must_change_something(self):
        errors, _ = self.check([edit_item([{"op": "remove", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two"}])])
        self.assertTrue(any("remove needs a why" in e for e in errors), errors)
        self.assertTrue(any("does not change anything" in e for e in errors), errors)

    def test_em_dashes_and_missing_screenshot_are_errors(self):
        errors, _ = self.check([edit_item([{"op": "keep", "ref": "b1"},
                                           {"op": "edit", "ref": "b2", "markdown": "Two \u2014 changed", "why": "w"}])],
                               screenshot=False)
        self.assertTrue(any("em dash" in e for e in errors), errors)
        self.assertTrue(any("no screenshot" in e for e in errors), errors)

    def test_new_pages_only_add_and_need_a_path(self):
        item = {"id": "1", "ticket": {"ref": "yalesites-org/YaleSites-Internal#1", "title": "t"}, "kind": "new",
                "target": {}, "ops": [{"op": "keep", "ref": "b1"}]}
        errors, _ = self.check([item], blocks=None)
        self.assertTrue(any("target.path" in e for e in errors), errors)
        self.assertTrue(any("can only add" in e for e in errors), errors)

    def test_bad_ticket_refs_and_kinds(self):
        errors, _ = self.check([edit_item([{"op": "keep", "ref": "b1"}, {"op": "keep", "ref": "b2"}],
                                          ticket={"ref": "#1818", "title": "t"}, kind="page")])
        self.assertTrue(any("owner/repo#N" in e for e in errors), errors)
        self.assertTrue(any("kind must be" in e for e in errors), errors)


class RenderTest(unittest.TestCase):
    def test_render_follows_ops_order_and_drops_removed(self):
        with tempfile.TemporaryDirectory() as d:
            write_packet(d, [edit_item([
                {"op": "add", "block": "Text", "markdown": "Zero"},
                {"op": "keep", "ref": "b1"},
                {"op": "remove", "ref": "b2", "why": "w"},
                {"op": "add", "block": "Callout", "markdown": "Three"}])], BLOCKS)
            self.assertEqual(packet.render(d, "1"), "Zero\n\nOne\n\nThree\n")


class SplitAndStatusTest(unittest.TestCase):
    def test_split_md_cuts_at_headings_but_not_inside_code(self):
        text = "Intro line\n\n# Title\nBody\n```\n# not a heading\n```\n## Next\nMore\n"
        secs = packet.split_md(text)
        self.assertEqual([s["id"] for s in secs], ["s1", "s2", "s3"])
        self.assertEqual(secs[0]["markdown"], "Intro line")
        self.assertIn("# not a heading", secs[1]["markdown"])
        self.assertTrue(secs[2]["markdown"].startswith("## Next"))

    def test_status_merges_per_ticket(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "status.json")
            packet.set_status("yalesites-org/YaleSites-Internal#1818", "on-board", packet="p1", path=path)
            packet.set_status("yalesites-org/YaleSites-Internal#1818", "built", result='{"nid": 5}', path=path)
            data = read_json(path)
            entry = data["tickets"]["yalesites-org/YaleSites-Internal#1818"]
            self.assertEqual((entry["state"], entry["packet"], entry["result"]), ("built", "p1", {"nid": 5}))
            with self.assertRaises(SystemExit):
                packet.set_status("1818", "built", path=path)
            with self.assertRaises(SystemExit):
                packet.set_status("yalesites-org/YaleSites-Internal#1818", "published", path=path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
