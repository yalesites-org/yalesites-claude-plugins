#!/usr/bin/env python3
"""Unit tests for post-screenshot.py's pure helpers.

Network-free by design: nothing here calls `gh`.

    python3 test_post_screenshot.py

CI runs this via `scripts/run-skill-tests.sh`, which also asserts the tests were
actually collected.
"""

import datetime
import importlib.util
import os
import unittest

# The script has a hyphen in its name (matching check-github-text.py), so it
# can't be imported with a plain `import` statement. Load it by path instead.
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("post_screenshot", os.path.join(_HERE, "post-screenshot.py"))
p = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p)


class ParseTicketTest(unittest.TestCase):
    def test_full_reference(self):
        self.assertEqual(p.parse_ticket("yalesites-org/YaleSites-Internal#1785"), ("yalesites-org", "YaleSites-Internal", 1785))

    def test_repo_only_defaults_to_org(self):
        self.assertEqual(p.parse_ticket("YaleSites-Internal#1785"), ("yalesites-org", "YaleSites-Internal", 1785))

    def test_bare_number_is_rejected(self):
        with self.assertRaises(p.InputError):
            p.parse_ticket("#1785")

    def test_url_is_rejected(self):
        with self.assertRaises(p.InputError):
            p.parse_ticket("https://github.com/yalesites-org/YaleSites-Internal/issues/1785")

    def test_zero_is_rejected(self):
        with self.assertRaises(p.InputError):
            p.parse_ticket("YaleSites-Internal#0")


class SlugifyTest(unittest.TestCase):
    def test_punctuation_and_case(self):
        self.assertEqual(p.slugify("Results & filters tab: BLANK!"), "results-filters-tab-blank")

    def test_length_cap_does_not_end_on_hyphen(self):
        slug = p.slugify("a" * 59 + " bcd")
        self.assertLessEqual(len(slug), p.SLUG_MAX)
        self.assertFalse(slug.endswith("-"))

    def test_nothing_usable(self):
        with self.assertRaises(p.InputError):
            p.slugify("!!!")


class CheckFileTest(unittest.TestCase):
    def test_allowed_types(self):
        for name in ("a.png", "a.PNG", "a.webp", "a.gif", "a.jpg"):
            self.assertEqual(p.check_file(name, 1000), os.path.splitext(name)[1].lower())

    def test_jpeg_normalised(self):
        self.assertEqual(p.check_file("a.jpeg", 1000), ".jpg")

    def test_unsupported_type(self):
        for name in ("a.mov", "a.pdf", "noext"):
            with self.assertRaises(p.InputError):
                p.check_file(name, 1000)

    def test_size_limit(self):
        self.assertEqual(p.check_file("a.png", p.MAX_BYTES), ".png")
        with self.assertRaises(p.InputError):
            p.check_file("a.png", p.MAX_BYTES + 1)

    def test_empty_file(self):
        with self.assertRaises(p.InputError):
            p.check_file("a.png", 0)


class PathTest(unittest.TestCase):
    def test_layout(self):
        self.assertEqual(
            p.build_path("YaleSites-Internal", 1785, datetime.date(2026, 10, 2), "item5", ".webp"),
            "YaleSites-Internal/1785/2026-10-02-item5.webp",
        )

    def test_free_path_untouched(self):
        self.assertEqual(p.next_free_path("r/1/x.png", lambda _: False), "r/1/x.png")

    def test_clash_gets_suffix_never_overwrites(self):
        taken = {"r/1/x.png", "r/1/x-2.png"}
        self.assertEqual(p.next_free_path("r/1/x.png", taken.__contains__), "r/1/x-3.png")


class LinkTest(unittest.TestCase):
    SHA = "0586b39c43a47c3caef7708a254b8674efde09c5"

    def test_url_is_github_raw_pinned_to_commit(self):
        url = p.image_url(self.SHA, "YaleSites-Internal/1785/x.webp")
        self.assertEqual(url, f"https://github.com/yalesites-org/YaleSites-Internal/raw/{self.SHA}/YaleSites-Internal/1785/x.webp")
        self.assertNotIn("raw.githubusercontent.com", url)
        self.assertNotIn("/main/", url)
        self.assertNotIn(f"/{p.DEST_BRANCH}/", url)

    def test_img_tag_escapes_alt(self):
        tag = p.img_tag("https://x/y.png", 'Results & "filters"')
        self.assertIn('alt="Results &amp; &quot;filters&quot;"', tag)
        self.assertIn('width="600"', tag)

    def test_img_tag_without_width(self):
        self.assertNotIn("width=", p.img_tag("https://x/y.png", "a", None))


class MainInputTest(unittest.TestCase):
    """Input errors are caught before any gh call, so these stay network-free."""

    def test_bad_ticket_exits_2(self):
        self.assertEqual(p.main(["x.png", "--ticket", "#1", "--alt", "a"]), 2)

    def test_missing_file_exits_2(self):
        self.assertEqual(p.main(["/nonexistent/x.png", "--ticket", "YaleSites-Internal#1", "--alt", "a"]), 2)

    def test_blank_alt_exits_2(self):
        self.assertEqual(p.main(["x.png", "--ticket", "YaleSites-Internal#1", "--alt", "  "]), 2)


if __name__ == "__main__":
    unittest.main()
