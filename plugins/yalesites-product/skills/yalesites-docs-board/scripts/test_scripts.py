#!/usr/bin/env python3
"""Tests for catalog.py, capture.py, and packet.py. Run: python3 test_scripts.py

Nothing here touches the network or a browser. The live paths (fetching the
sitemap, running Playwright) are thin wrappers around the functions tested.
"""
import contextlib
import io
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

    def test_stem_keeps_singular_and_plural_together(self):
        for a, b in (("image", "images"), ("course", "courses"), ("embed", "embedded"), ("export", "exporting"),
                     ("install", "installed"), ("tag", "tagged"), ("block", "blocks"), ("address", "addressed"),
                     ("set", "setting"), ("set", "settings"), ("setting", "settings"), ("head", "heading"),
                     ("head", "headings"), ("heading", "headings"), ("export", "exports"),
                     ("create", "creating"), ("create", "created"), ("creating", "created"), ("share", "shared"),
                     ("manage", "managing"), ("image", "imaging"), ("page", "pages"), ("remove", "removed")):
            self.assertEqual(catalog.stem(a), catalog.stem(b), (a, b))
        self.assertEqual(catalog.stem("process"), "process")
        self.assertEqual(catalog.stem("use"), "use")  # three letters keep their e
        self.assertEqual(catalog.stem("need"), "need")
        cat = {"pages": [{"path": "/site-settings", "title": "Site Settings", "teaser": "", "headings": []}]}
        self.assertEqual(len(catalog.search(cat, "Docs: site setting")), 1)
        cat = {"pages": [{"path": "/working-with-images", "title": "Working with Images", "teaser": "", "headings": []}]}
        self.assertEqual(len(catalog.search(cat, "Docs: image block alt text")), 1)

    def test_a_bare_verb_in_the_title_matches_its_ing_form_in_the_ticket(self):
        # "creating" used to stem to "creat" while "create" stayed whole, so
        # this page lost its title and path points and fell below pages that
        # only share "section".
        cat = {"pages": [
            {"path": "/page-sections-overview", "title": "Page Sections Overview", "teaser": "", "headings": []},
            {"path": "/create-powerful-page-sections", "title": "Create Powerful Page Sections", "teaser": "", "headings": []},
            {"path": "/creating-accessible-content", "title": "Creating Accessible Content", "teaser": "", "headings": []},
        ]}
        hits = catalog.search(cat, "Docs: creating sections")
        self.assertEqual(hits[0][1]["path"], "/create-powerful-page-sections")
        self.assertGreaterEqual(hits[0][0], 10)
        cat = {"pages": [{"path": "/manage-settings", "title": "Manage Settings", "teaser": "", "headings": []}]}
        self.assertEqual(len(catalog.search(cat, "Docs: managing a site's settings")), 1)

    def test_stop_words_stay_stopped_in_their_stemmed_forms(self):
        self.assertEqual(catalog.tokens("Docs: pages guides updates users"), [])
        self.assertEqual(catalog.tokens("Docs: create a page"), ["creat"])

    def test_inventory_merge_reads_bundled_csv(self):
        inv = catalog.load_inventory()
        self.assertIn("/editorial-workflow", inv)
        self.assertIn("User Guide", inv["/editorial-workflow"]["nav"])

    def test_refresh_survives_a_child_sitemap_that_does_not_load(self):
        index = (INDEX.replace("</sitemapindex>", "<sitemap><loc>https://yalesites.yale.edu/sitemap.xml?page=3</loc></sitemap></sitemapindex>"))
        calls = []

        def fake_fetch(url, timeout=20):
            calls.append(url)
            if url == catalog.SITEMAP:
                return 200, index
            if url.endswith("page=2"):
                raise OSError("timed out")
            if url.endswith("page=3"):
                return 200, SITEMAP
            return 200, PAGE

        real = catalog.fetch
        catalog.fetch = fake_fetch
        try:
            with tempfile.TemporaryDirectory() as d:
                out = os.path.join(d, "catalog.json")
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    cat = catalog.refresh(force=True, out=out)
                self.assertEqual([p["path"] for p in cat["pages"]], ["/", "/a", "/editorial-workflow"])
                self.assertEqual(read_json(out)["pages"], cat["pages"])
                self.assertIn("1 of 2 child sitemaps did not load", stdout.getvalue())
                self.assertIn("page=2", stderr.getvalue())
        finally:
            catalog.fetch = real
        self.assertIn("https://yalesites.yale.edu/sitemap.xml?page=3", calls)

    def test_refresh_keeps_the_old_catalog_when_most_pages_do_not_load(self):
        # The sitemap loads, then the page fetches fail (rate limit, network
        # blip). Writing that would leave search with empty titles for a day.
        def mostly_failing(url, timeout=20):
            if url == catalog.SITEMAP:
                return 200, SITEMAP
            if url.endswith("/editorial-workflow"):
                return 200, PAGE
            raise OSError("connection reset")

        real = catalog.fetch
        catalog.fetch = mostly_failing
        try:
            with tempfile.TemporaryDirectory() as d:
                out = os.path.join(d, "catalog.json")
                old = {"builtAt": "earlier", "pages": [{"path": "/old", "title": "Old", "teaser": "", "headings": []}]}
                with open(out, "w") as f:
                    json.dump(old, f)
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    cat = catalog.refresh(force=True, out=out)
                self.assertEqual(cat, old)
                self.assertEqual(read_json(out), old)
                self.assertIn("Catalog not written: 1 of 3 pages returned 200", stderr.getvalue())
                self.assertIn("Keeping the old catalog", stderr.getvalue())
                self.assertNotIn("Catalog built", stdout.getvalue())
                # With nothing to keep, refresh stops and writes nothing.
                fresh = os.path.join(d, "fresh", "catalog.json")
                with self.assertRaises(SystemExit) as cm:
                    catalog.refresh(force=True, out=fresh)
                self.assertIn("no earlier catalog", str(cm.exception))
                self.assertFalse(os.path.exists(fresh))
        finally:
            catalog.fetch = real

    def test_one_max_age_for_refresh_and_the_staleness_warning(self):
        ap = catalog.build_parser()
        self.assertEqual(ap.parse_args(["refresh"]).max_age_hours, catalog.MAX_AGE_HOURS)
        self.assertEqual(ap.parse_args(["search", "x"]).max_age_hours, catalog.MAX_AGE_HOURS)
        self.assertEqual(ap.parse_args(["search", "x", "--max-age-hours", "72"]).max_age_hours, 72)
        self.assertEqual(ap.parse_args(["refresh", "--max-age-hours", "72", "--force"]).max_age_hours, 72)
        import inspect
        self.assertEqual(inspect.signature(catalog.refresh).parameters["max_age_hours"].default, catalog.MAX_AGE_HOURS)
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "catalog.json")
            with open(out, "w") as f:
                json.dump({"pages": []}, f)
            os.utime(out, (0, __import__("time").time() - 30 * 3600))
            self.assertAlmostEqual(catalog.catalog_age(out), 30, delta=0.1)
            # 30h is fresh when the caller said 72h, so no fetch happens.
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(catalog.refresh(max_age_hours=72, out=out), {"pages": []})


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

    def test_targets_compare_the_host_not_a_prefix(self):
        self.assertEqual(capture.parse_targets(["1=https://yalesites.yale.edu/x?y=1"])[0][1], "https://yalesites.yale.edu/x?y=1")
        for url in ("https://yalesites.yale.edu.example.com/x", "https://yalesites.yale.edu@evil.example/",
                    "http://yalesites.yale.edu/x", "https://yalesites.yale.edu:8443/x", "yalesites.yale.edu/x"):
            with self.assertRaises(SystemExit, msg=url):
                capture.parse_targets([f"1={url}"])

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

    def test_capture_js_skips_chrome_by_name_not_by_style(self):
        # Collapsed accordion bodies and inactive tab panels are display:none
        # and must still be captured, so md() may not look at computed style.
        body = open(os.path.join(HERE, "capture.js")).read()
        self.assertNotIn("getComputedStyle", body)
        self.assertIn("const CHROME", body)

    def test_item_id_rule_is_shared_with_packet(self):
        self.assertIs(capture.ITEM_ID, packet.ITEM_ID)
        self.assertIs(catalog.read_json, packet.read_json)


def write_packet(folder, items, blocks=None, screenshot=True, kind=None):
    os.makedirs(os.path.join(folder, "1"), exist_ok=True)
    if blocks is not None:
        with open(os.path.join(folder, "1", "current.json"), "w") as f:
            json.dump({"kind": kind, "status": 200, "screenshot": "current.png" if screenshot else None, "blocks": blocks}, f)
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

    def test_locked_is_accepted_as_a_bool_only(self):
        ops = [{"op": "keep", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}]
        errors, _ = self.check([edit_item(ops, locked=True)])
        self.assertEqual(errors, [])
        errors, _ = self.check([edit_item(ops, locked="yes")])
        self.assertTrue(any("locked must be true or false" in e for e in errors), errors)

    def test_two_items_cannot_share_a_ticket_ref(self):
        ops = [{"op": "keep", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}]
        errors, _ = self.check([edit_item(ops), edit_item(ops, id="1b")])
        self.assertTrue(any("duplicate ticket.ref yalesites-org/YaleSites-Internal#1" in e and "#1-a" in e for e in errors), errors)
        # One ticket touching two pages: two items, refs suffixed.
        errors, _ = self.check([edit_item(ops, id="1-a", ticket={"ref": "yalesites-org/YaleSites-Internal#1-a", "url": "u", "title": "t"}),
                                edit_item(ops, id="1-b", ticket={"ref": "yalesites-org/YaleSites-Internal#1-b", "url": "u", "title": "t"})])
        self.assertEqual(errors, [])
        for bad in ("yalesites-org/YaleSites-Internal#1-", "yalesites-org/YaleSites-Internal#1-a-b", "yalesites-org/YaleSites-Internal#1a"):
            errors, _ = self.check([edit_item(ops, ticket={"ref": bad, "url": "u", "title": "t"})])
            self.assertTrue(any("owner/repo#N" in e for e in errors), (bad, errors))

    def test_ticket_needs_a_title_and_url_for_the_board(self):
        ops = [{"op": "keep", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}]
        errors, _ = self.check([edit_item(ops, ticket={"ref": "yalesites-org/YaleSites-Internal#1"})])
        self.assertTrue(any("ticket.title is required" in e for e in errors), errors)
        self.assertTrue(any("ticket.url is required" in e for e in errors), errors)
        errors, _ = self.check([edit_item(ops, ticket={"ref": "yalesites-org/YaleSites-Internal#1", "title": " ", "url": "u"})])
        self.assertTrue(any("ticket.title is required" in e for e in errors), errors)
        self.assertFalse(any("ticket.url" in e for e in errors), errors)


class RenderTest(unittest.TestCase):
    def test_render_follows_ops_order_and_drops_removed(self):
        with tempfile.TemporaryDirectory() as d:
            write_packet(d, [edit_item([
                {"op": "add", "block": "Text", "markdown": "Zero"},
                {"op": "keep", "ref": "b1"},
                {"op": "remove", "ref": "b2", "why": "w"},
                {"op": "add", "block": "Callout", "markdown": "Three"}])], BLOCKS)
            self.assertEqual(packet.render(d, "1"), "Zero\n\nOne\n\nThree\n")


README = (
    "\n\nIntro line\n\n\n# Title\nBody\n\n```bash\n# not a heading\n```\n\n~~~\n# nor this one\n```\n# still fenced\n~~~\n"
    "\n````md\n```\n# fenced by four backticks\n```\n````\n   ~~~~ python\n# four tildes\n~~~\n# not closed by three\n~~~~\n"
    "## Next\n\n\nMore\n\n\n"
)


class SplitAndStatusTest(unittest.TestCase):
    def test_split_md_cuts_at_headings_but_not_inside_fences(self):
        secs = packet.split_md(README)
        self.assertEqual([s["id"] for s in secs], ["s1", "s2", "s3"])
        self.assertEqual(secs[0]["markdown"], "\n\nIntro line\n\n\n")
        self.assertTrue(secs[1]["markdown"].startswith("# Title\n"))
        for fenced in ("# not a heading", "# nor this one", "# still fenced", "# fenced by four backticks", "# four tildes", "# not closed by three"):
            self.assertIn(fenced, secs[1]["markdown"], fenced)
        self.assertEqual(secs[2]["markdown"], "## Next\n\n\nMore\n\n\n")

    def test_split_md_keeps_an_unclosed_fence_open_and_a_file_without_a_final_newline(self):
        self.assertEqual(len(packet.split_md("# A\n```\n# B\n")), 1)
        secs = packet.split_md("# A\ntext\n# B\nmore")
        self.assertEqual([s["markdown"] for s in secs], ["# A\ntext\n", "# B\nmore"])
        self.assertEqual(packet.split_md("   \n\n"), [{"id": "s1", "type": "Section", "markdown": "   \n\n"}])

    def test_split_then_render_gives_the_file_back_byte_for_byte(self):
        # Except at the very end: the output always ends with exactly one
        # newline, so a file that ended with extra blank lines (or none)
        # comes back with one.
        for text in (README, "# A\ntext\n# B\nmore", "no headings at all\n\n\n", "# only\n",
                     "# Title\n\nIntro.\n\n## Usage\n\nRun it.\n"):
            secs = packet.split_md(text)
            self.assertEqual("".join(s["markdown"] for s in secs), text)
            with tempfile.TemporaryDirectory() as d:
                item = {"id": "1", "ticket": {"ref": "yalesites-org/x#1", "url": "u", "title": "t"}, "kind": "internal",
                        "target": {"repo": "yalesites-org/x", "file": "README.md"}, "current": "1/current.json",
                        "ops": [{"op": "keep", "ref": s["id"]} for s in secs]}
                write_packet(d, [item], secs, screenshot=False, kind="file")
                self.assertEqual(packet.render(d, "1"), text.rstrip("\n") + "\n")

    def test_render_ends_with_one_newline_when_the_last_section_is_removed(self):
        secs = packet.split_md("# A\ntext\n\n# B\nmore\n")
        self.assertEqual(secs[0]["markdown"], "# A\ntext\n\n")
        with tempfile.TemporaryDirectory() as d:
            item = {"id": "1", "ticket": {"ref": "yalesites-org/x#1", "url": "u", "title": "t"}, "kind": "internal",
                    "target": {"repo": "yalesites-org/x", "file": "README.md"}, "current": "1/current.json",
                    "ops": [{"op": "keep", "ref": "s1"}, {"op": "remove", "ref": "s2", "why": "w"}]}
            write_packet(d, [item], secs, screenshot=False, kind="file")
            self.assertEqual(packet.render(d, "1"), "# A\ntext\n")

    def test_render_separates_edited_and_added_text_with_one_blank_line(self):
        secs = packet.split_md("# A\ntext\n\n# B\nmore\n")
        with tempfile.TemporaryDirectory() as d:
            item = {"id": "1", "ticket": {"ref": "yalesites-org/x#1", "url": "u", "title": "t"}, "kind": "internal",
                    "target": {"repo": "yalesites-org/x", "file": "README.md"}, "current": "1/current.json",
                    "ops": [{"op": "edit", "ref": "s1", "markdown": "# A\nnew text", "why": "w"},
                            {"op": "add", "block": "Section", "markdown": "# A2\nbetween\n"},
                            {"op": "keep", "ref": "s2"},
                            {"op": "add", "block": "Section", "markdown": "# C\nlast"}]}
            write_packet(d, [item], secs, screenshot=False, kind="file")
            self.assertEqual(packet.render(d, "1"), "# A\nnew text\n\n# A2\nbetween\n\n# B\nmore\n\n# C\nlast\n")

    def test_render_pads_a_kept_section_before_added_text(self):
        # The file's last section ends on a single newline. An add after it
        # must start its own paragraph, not fuse onto "Run it."
        readme = "# Title\n\nIntro.\n\n## Usage\n\nRun it.\n"
        secs = packet.split_md(readme)
        self.assertEqual([s["id"] for s in secs], ["s1", "s2"])
        with tempfile.TemporaryDirectory() as d:
            item = {"id": "1", "ticket": {"ref": "yalesites-org/x#1", "url": "u", "title": "t"}, "kind": "internal",
                    "target": {"repo": "yalesites-org/x", "file": "README.md"}, "current": "1/current.json",
                    "ops": [{"op": "keep", "ref": "s1"}, {"op": "keep", "ref": "s2"},
                            {"op": "add", "block": "Section", "markdown": "More text here."}]}
            write_packet(d, [item], secs, screenshot=False, kind="file")
            self.assertEqual(packet.render(d, "1"), readme + "\nMore text here.\n")
        # A kept section with no final newline at all gets a full blank line.
        secs = packet.split_md("# A\ntext")
        with tempfile.TemporaryDirectory() as d:
            item = {"id": "1", "ticket": {"ref": "yalesites-org/x#1", "url": "u", "title": "t"}, "kind": "internal",
                    "target": {"repo": "yalesites-org/x", "file": "README.md"}, "current": "1/current.json",
                    "ops": [{"op": "keep", "ref": "s1"}, {"op": "add", "block": "Section", "markdown": "# B\nmore"}]}
            write_packet(d, [item], secs, screenshot=False, kind="file")
            self.assertEqual(packet.render(d, "1"), "# A\ntext\n\n# B\nmore\n")

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

    def test_status_refuses_to_replace_a_corrupt_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "status.json")
            packet.set_status("yalesites-org/YaleSites-Internal#1", "built", path=path)
            with open(path, "w") as f:
                f.write('{"tickets": {"yalesites-org/YaleSites-Internal#1": {"state": "built"')  # half-written
            with open(path) as f:
                before = f.read()
            with self.assertRaises(SystemExit) as cm:
                packet.set_status("yalesites-org/YaleSites-Internal#2", "building", path=path)
            self.assertIn("not valid JSON", str(cm.exception))
            with open(path) as f:
                self.assertEqual(f.read(), before)
            # A missing file is still the first run.
            fresh = os.path.join(d, "fresh", "status.json")
            with contextlib.redirect_stderr(io.StringIO()):
                packet.set_status("yalesites-org/YaleSites-Internal#2", "building", path=fresh, packets_dir=d)
            self.assertEqual(read_json(fresh)["tickets"]["yalesites-org/YaleSites-Internal#2"]["state"], "building")

    def test_built_and_building_lock_the_item_in_its_packet(self):
        ref = "yalesites-org/YaleSites-Internal#1"
        with tempfile.TemporaryDirectory() as d:
            packets = os.path.join(d, "packets")
            folder = os.path.join(packets, "docs-2026-10-13")
            ops = [{"op": "keep", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}]
            write_packet(folder, [edit_item(ops), edit_item(ops, id="2", ticket={"ref": "yalesites-org/YaleSites-Internal#2", "url": "u", "title": "t"})], BLOCKS)
            path = os.path.join(d, "status.json")
            kw = {"path": path, "packets_dir": packets}
            packet.set_status(ref, "on-board", packet="docs-2026-10-13", **kw)
            self.assertNotIn("locked", read_json(os.path.join(folder, "packet.json"))["items"][0])
            # building locks, and finds the packet from the earlier entry.
            with contextlib.redirect_stderr(io.StringIO()):
                packet.set_status(ref, "building", **kw)
            items = read_json(os.path.join(folder, "packet.json"))["items"]
            self.assertIs(items[0].get("locked"), True)
            self.assertNotIn("locked", items[1])
            self.assertEqual(packet.validate(folder)[0], [])
            # failed unlocks and bumps the revision, so the board forgets the
            # approve that led to the half-built page. built locks again.
            packet.set_status(ref, "failed", note="CAS timed out", **kw)
            item = read_json(os.path.join(folder, "packet.json"))["items"][0]
            self.assertNotIn("locked", item)
            self.assertEqual(item["revision"], 2)
            self.assertEqual(read_json(os.path.join(folder, "packet.json"))["items"][1].get("revision"), None)
            packet.set_status(ref, "built", result='{"nid": 5}', **kw)
            item = read_json(os.path.join(folder, "packet.json"))["items"][0]
            self.assertIs(item["locked"], True)
            self.assertEqual(item["revision"], 2)
            # The status entry remembers which item it acted on.
            self.assertEqual(read_json(path)["tickets"][ref]["item"], "1")
            # No packet known: the status is still recorded, with a note.
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                entry = packet.set_status("yalesites-org/YaleSites-Internal#9", "built", **kw)
            self.assertEqual(entry["state"], "built")
            self.assertIn("not locked", err.getvalue())


class StatusByItemTest(unittest.TestCase):
    def test_status_locks_by_item_id_when_a_ref_names_two_items(self):
        # A packet that skipped validate: two items on one ref. The lock must
        # not land on the first match.
        ref = "yalesites-org/YaleSites-Internal#1"
        with tempfile.TemporaryDirectory() as d:
            packets = os.path.join(d, "packets")
            folder = os.path.join(packets, "docs-2026-10-13")
            ops = [{"op": "keep", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}]
            write_packet(folder, [edit_item(ops, id="1-a"), edit_item(ops, id="1-b")], BLOCKS)
            self.assertTrue(any("duplicate ticket.ref" in e for e in packet.validate(folder)[0]))
            path = os.path.join(d, "status.json")
            kw = {"path": path, "packets_dir": packets}
            with self.assertRaises(SystemExit) as cm:
                packet.set_status(ref, "building", packet="docs-2026-10-13", **kw)
            self.assertIn("Pass --item", str(cm.exception))
            self.assertIn("1-a, 1-b", str(cm.exception))
            # The status itself was recorded before the lock stopped.
            self.assertEqual(read_json(path)["tickets"][ref]["state"], "building")
            items = read_json(os.path.join(folder, "packet.json"))["items"]
            self.assertFalse(any("locked" in i for i in items))
            packet.set_status(ref, "building", packet="docs-2026-10-13", item="1-b", **kw)
            items = read_json(os.path.join(folder, "packet.json"))["items"]
            self.assertNotIn("locked", items[0])
            self.assertIs(items[1].get("locked"), True)
            # Later calls without --item reuse the remembered item.
            packet.set_status(ref, "failed", note="x", **kw)
            items = read_json(os.path.join(folder, "packet.json"))["items"]
            self.assertNotIn("locked", items[1])
            self.assertEqual(items[1]["revision"], 2)
            self.assertNotIn("revision", items[0])
            # An --item that is not in the packet: recorded, not locked, with a note.
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                packet.set_status(ref, "built", item="9", **kw)
            self.assertIn("not locked", err.getvalue())
            self.assertFalse(any("locked" in i for i in read_json(os.path.join(folder, "packet.json"))["items"]))

    def test_suffixed_refs_each_get_their_own_status_and_lock(self):
        with tempfile.TemporaryDirectory() as d:
            packets = os.path.join(d, "packets")
            folder = os.path.join(packets, "docs-2026-10-13")
            ops = [{"op": "keep", "ref": "b1"}, {"op": "edit", "ref": "b2", "markdown": "Two, changed", "why": "w"}]
            write_packet(folder, [edit_item(ops, id="1-a", ticket={"ref": "yalesites-org/YaleSites-Internal#1-a", "url": "u", "title": "t"}),
                                  edit_item(ops, id="1-b", ticket={"ref": "yalesites-org/YaleSites-Internal#1-b", "url": "u", "title": "t"})], BLOCKS)
            self.assertEqual(packet.validate(folder)[0], [])
            path = os.path.join(d, "status.json")
            kw = {"path": path, "packets_dir": packets}
            packet.set_status("yalesites-org/YaleSites-Internal#1-b", "built", packet="docs-2026-10-13", **kw)
            items = read_json(os.path.join(folder, "packet.json"))["items"]
            self.assertNotIn("locked", items[0])
            self.assertIs(items[1].get("locked"), True)
            self.assertEqual(sorted(read_json(path)["tickets"]), ["yalesites-org/YaleSites-Internal#1-b"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
